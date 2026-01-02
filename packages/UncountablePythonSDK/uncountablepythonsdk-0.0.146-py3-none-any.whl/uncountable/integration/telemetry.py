import functools
import json
import os
import resource
import threading
import time
import traceback
import types
import typing
from contextlib import contextmanager
from enum import StrEnum
from typing import Generator, assert_never, cast

import psutil
from opentelemetry import _logs, trace
from opentelemetry.context import get_current
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import Logger as OTELLogger
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LogRecord,
)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
from opentelemetry.sdk.resources import Attributes, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
)
from opentelemetry.trace import Span, Tracer

from uncountable.core.environment import (
    get_otel_enabled,
    get_server_env,
    get_version,
)
from uncountable.types import base_t, job_definition_t


def _cast_attributes(attributes: dict[str, base_t.JsonValue]) -> Attributes:
    return cast(Attributes, attributes)


def one_line_formatter(record: LogRecord) -> str:
    json_data = record.to_json()
    return json.dumps(json.loads(json_data), separators=(",", ":")) + "\n"


@functools.cache
def get_otel_resource() -> Resource:
    attributes: dict[str, base_t.JsonValue] = {
        "service.name": "integration-server",
        "sdk.version": get_version(),
    }
    unc_version = os.environ.get("UNC_VERSION")
    if unc_version is not None:
        attributes["service.version"] = unc_version
    unc_env = get_server_env()
    if unc_env is not None:
        attributes["deployment.environment"] = unc_env
    resource = Resource.create(attributes=_cast_attributes(attributes))
    return resource


@functools.cache
def get_otel_tracer() -> Tracer:
    provider = TracerProvider(resource=get_otel_resource())
    if get_otel_enabled():
        provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    return provider.get_tracer("integration.telemetry")


@functools.cache
def get_otel_logger() -> OTELLogger:
    provider = LoggerProvider(resource=get_otel_resource())
    provider.add_log_record_processor(
        BatchLogRecordProcessor(ConsoleLogExporter(formatter=one_line_formatter))
    )
    if get_otel_enabled():
        provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
    _logs.set_logger_provider(provider)
    return provider.get_logger("integration.telemetry")


class LogSeverity(StrEnum):
    INFO = "Info"
    WARN = "Warn"
    ERROR = "Error"


def _get_severity_number(severity: LogSeverity) -> _logs.SeverityNumber:
    """Map LogSeverity to OpenTelemetry SeverityNumber for Datadog."""
    match severity:
        case LogSeverity.INFO:
            return _logs.SeverityNumber.INFO
        case LogSeverity.WARN:
            return _logs.SeverityNumber.WARN
        case LogSeverity.ERROR:
            return _logs.SeverityNumber.ERROR
        case _:
            assert_never(severity)


class Logger:
    current_span: Span

    def __init__(self, base_span: Span) -> None:
        self.current_span = base_span

    @property
    def current_span_id(self) -> int:
        return self.current_span.get_span_context().span_id

    @property
    def current_trace_id(self) -> int | None:
        return self.current_span.get_span_context().trace_id

    def _patch_attributes(
        self,
        attributes: Attributes | None,
        *,
        message: str | None = None,
        severity: LogSeverity | None = None,
    ) -> Attributes:
        patched_attributes = {**(attributes if attributes is not None else {})}
        if message is not None:
            patched_attributes["message"] = message
        elif "body" in patched_attributes:
            patched_attributes["message"] = patched_attributes["body"]

        if severity is not None:
            patched_attributes["status"] = severity.lower()
        elif "severity_text" in patched_attributes and isinstance(
            patched_attributes["severity_text"], str
        ):
            patched_attributes["status"] = patched_attributes["severity_text"].lower()

        return patched_attributes

    def _emit_log(
        self, message: str, *, severity: LogSeverity, attributes: Attributes | None
    ) -> None:
        otel_logger = get_otel_logger()
        log_record = LogRecord(
            body=message,
            severity_text=severity,
            timestamp=time.time_ns(),
            attributes=self._patch_attributes(
                message=message, severity=severity, attributes=attributes
            ),
            context=get_current(),
            severity_number=_get_severity_number(severity),
            resource=get_otel_resource(),
        )
        otel_logger.emit(log_record)

    def log_info(self, message: str, *, attributes: Attributes | None = None) -> None:
        self._emit_log(
            message=message, severity=LogSeverity.INFO, attributes=attributes
        )

    def log_warning(
        self, message: str, *, attributes: Attributes | None = None
    ) -> None:
        self._emit_log(
            message=message, severity=LogSeverity.WARN, attributes=attributes
        )

    def log_error(self, message: str, *, attributes: Attributes | None = None) -> None:
        self._emit_log(
            message=message, severity=LogSeverity.ERROR, attributes=attributes
        )

    def log_exception(
        self,
        exception: BaseException,
        *,
        message: str | None = None,
        attributes: Attributes | None = None,
        severity: LogSeverity = LogSeverity.ERROR,
    ) -> None:
        traceback_str = "".join(traceback.format_exception(exception))
        patched_attributes = self._patch_attributes(
            message=message, severity=severity, attributes=attributes
        )
        self.current_span.record_exception(
            exception=exception, attributes=patched_attributes
        )
        log_message = f"error: {message}\nexception: {exception}{traceback_str}"
        self._emit_log(
            message=log_message, severity=severity, attributes=patched_attributes
        )

    @contextmanager
    def push_scope(
        self, scope_name: str, *, attributes: Attributes | None = None
    ) -> Generator[typing.Self, None, None]:
        with get_otel_tracer().start_as_current_span(
            scope_name, attributes=self._patch_attributes(attributes)
        ):
            yield self


class PerJobResourceTracker:
    def __init__(self, logger: "JobLogger", sample_interval: float = 0.5) -> None:
        self.logger = logger
        self.sample_interval = sample_interval
        self._process = psutil.Process(os.getpid())
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

        self.max_rss: int = 0
        self.start_cpu_times: psutil._common.pcputimes | None = None
        self.end_cpu_times: psutil._common.pcputimes | None = None
        self.start_wall_time: float | None = None
        self.end_wall_time: float | None = None

    def start(self) -> None:
        self.start_cpu_times = self._process.cpu_times()
        self.start_wall_time = time.monotonic()

        def _monitor() -> None:
            try:
                while not self._stop_event.is_set():
                    rss = self._process.memory_info().rss
                    self.max_rss = max(self.max_rss, rss)
                    time.sleep(self.sample_interval)
            except Exception:
                self._stop_event.set()

        self._thread = threading.Thread(target=_monitor, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()
        self.end_cpu_times = self._process.cpu_times()
        self.end_wall_time = time.monotonic()

    def __enter__(self) -> typing.Self:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        self.stop()
        stats = dict(self.summary())
        if isinstance(exc_value, MemoryError):
            limit, _ = resource.getrlimit(resource.RLIMIT_AS)
            self.logger.log_exception(
                exc_value,
                message=(
                    f"Job '{self.logger.job_definition.name}' (ID={self.logger.job_definition.id}) "
                    f"exceeded memory limit ({limit / (1024**3):.2f} GB)."
                ),
            )
            return
        self.logger.log_info("Job resource usage summary", attributes=stats)
        return

    def summary(self) -> Attributes:
        assert self.start_cpu_times is not None
        assert self.end_cpu_times is not None
        assert self.start_wall_time is not None
        assert self.end_wall_time is not None

        cpu_user = self.end_cpu_times.user - self.start_cpu_times.user
        cpu_sys = self.end_cpu_times.system - self.start_cpu_times.system
        cpu_total = cpu_user + cpu_sys
        elapsed = self.end_wall_time - self.start_wall_time
        return {
            "cpu_user_s": round(cpu_user, 3),
            "cpu_system_s": round(cpu_sys, 3),
            "cpu_total_s": round(cpu_total, 3),
            "wall_time_s": round(elapsed, 3),
            "peak_rss_mb": round(self.max_rss / (1024 * 1024), 2),
        }


class JobLogger(Logger):
    def __init__(
        self,
        *,
        base_span: Span,
        profile_metadata: job_definition_t.ProfileMetadata,
        job_definition: job_definition_t.JobDefinition,
        queued_job_uuid: str,
    ) -> None:
        self.profile_metadata = profile_metadata
        self.job_definition = job_definition
        self.queued_job_uuid = queued_job_uuid
        super().__init__(base_span)

    def _patch_attributes(
        self,
        attributes: Attributes | None,
        *,
        message: str | None = None,
        severity: LogSeverity | None = None,
    ) -> Attributes:
        patched_attributes: dict[str, base_t.JsonValue] = {
            **super()._patch_attributes(
                attributes=attributes, message=message, severity=severity
            )
        }
        patched_attributes["profile.name"] = self.profile_metadata.name
        patched_attributes["profile.base_url"] = self.profile_metadata.base_url
        patched_attributes["job.name"] = self.job_definition.name
        patched_attributes["job.id"] = self.job_definition.id
        patched_attributes["job.definition_type"] = self.job_definition.type
        patched_attributes["job.queued_job_uuid"] = self.queued_job_uuid
        match self.job_definition:
            case job_definition_t.CronJobDefinition():
                patched_attributes["job.definition.cron_spec"] = (
                    self.job_definition.cron_spec
                )
            case job_definition_t.HttpJobDefinitionBase():
                pass
            case _:
                assert_never(self.job_definition)
        patched_attributes["job.definition.executor.type"] = (
            self.job_definition.executor.type
        )
        match self.job_definition.executor:
            case job_definition_t.JobExecutorScript():
                patched_attributes["job.definition.executor.import_path"] = (
                    self.job_definition.executor.import_path
                )
            case job_definition_t.JobExecutorGenericUpload():
                patched_attributes["job.definition.executor.data_source.type"] = (
                    self.job_definition.executor.data_source.type
                )
            case _:
                assert_never(self.job_definition.executor)
        return _cast_attributes(patched_attributes)

    def resource_tracking(self) -> PerJobResourceTracker:
        return PerJobResourceTracker(self)


@contextmanager
def push_scope_optional(
    logger: Logger | None, scope_name: str, *, attributes: Attributes | None = None
) -> Generator[None, None, None]:
    if logger is None:
        yield
    else:
        with logger.push_scope(scope_name, attributes=attributes):
            yield
