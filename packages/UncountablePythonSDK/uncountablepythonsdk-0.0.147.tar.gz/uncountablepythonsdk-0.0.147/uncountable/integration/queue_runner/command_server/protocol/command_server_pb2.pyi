# ruff: noqa
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class CancelJobStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CANCELLED_WITH_RESTART: _ClassVar[CancelJobStatus]
    NO_JOB_FOUND: _ClassVar[CancelJobStatus]
    JOB_ALREADY_COMPLETED: _ClassVar[CancelJobStatus]

CANCELLED_WITH_RESTART: CancelJobStatus
NO_JOB_FOUND: CancelJobStatus
JOB_ALREADY_COMPLETED: CancelJobStatus

class EnqueueJobRequest(_message.Message):
    __slots__ = ("job_ref_name", "serialized_payload")
    JOB_REF_NAME_FIELD_NUMBER: _ClassVar[int]
    SERIALIZED_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    job_ref_name: str
    serialized_payload: str
    def __init__(
        self,
        job_ref_name: _Optional[str] = ...,
        serialized_payload: _Optional[str] = ...,
    ) -> None: ...

class EnqueueJobResult(_message.Message):
    __slots__ = ("successfully_queued", "queued_job_uuid")
    SUCCESSFULLY_QUEUED_FIELD_NUMBER: _ClassVar[int]
    QUEUED_JOB_UUID_FIELD_NUMBER: _ClassVar[int]
    successfully_queued: bool
    queued_job_uuid: str
    def __init__(
        self, successfully_queued: bool = ..., queued_job_uuid: _Optional[str] = ...
    ) -> None: ...

class RetryJobRequest(_message.Message):
    __slots__ = ("uuid",)
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class RetryJobResult(_message.Message):
    __slots__ = ("successfully_queued", "queued_job_uuid")
    SUCCESSFULLY_QUEUED_FIELD_NUMBER: _ClassVar[int]
    QUEUED_JOB_UUID_FIELD_NUMBER: _ClassVar[int]
    successfully_queued: bool
    queued_job_uuid: str
    def __init__(
        self, successfully_queued: bool = ..., queued_job_uuid: _Optional[str] = ...
    ) -> None: ...

class VaccuumQueuedJobsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class VaccuumQueuedJobsResult(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CheckHealthRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CheckHealthResult(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ListQueuedJobsRequest(_message.Message):
    __slots__ = ("offset", "limit", "status")
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    offset: int
    limit: int
    status: str
    def __init__(
        self,
        offset: _Optional[int] = ...,
        limit: _Optional[int] = ...,
        status: _Optional[str] = ...,
    ) -> None: ...

class ListQueuedJobsResult(_message.Message):
    __slots__ = ("queued_jobs",)
    class ListQueuedJobsResultItem(_message.Message):
        __slots__ = ("uuid", "job_ref_name", "num_attempts", "submitted_at", "status")
        UUID_FIELD_NUMBER: _ClassVar[int]
        JOB_REF_NAME_FIELD_NUMBER: _ClassVar[int]
        NUM_ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
        SUBMITTED_AT_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        uuid: str
        job_ref_name: str
        num_attempts: int
        submitted_at: _timestamp_pb2.Timestamp
        status: str
        def __init__(
            self,
            uuid: _Optional[str] = ...,
            job_ref_name: _Optional[str] = ...,
            num_attempts: _Optional[int] = ...,
            submitted_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
            status: _Optional[str] = ...,
        ) -> None: ...

    QUEUED_JOBS_FIELD_NUMBER: _ClassVar[int]
    queued_jobs: _containers.RepeatedCompositeFieldContainer[
        ListQueuedJobsResult.ListQueuedJobsResultItem
    ]
    def __init__(
        self,
        queued_jobs: _Optional[
            _Iterable[_Union[ListQueuedJobsResult.ListQueuedJobsResultItem, _Mapping]]
        ] = ...,
    ) -> None: ...

class CancelJobRequest(_message.Message):
    __slots__ = ("job_uuid",)
    JOB_UUID_FIELD_NUMBER: _ClassVar[int]
    job_uuid: str
    def __init__(self, job_uuid: _Optional[str] = ...) -> None: ...

class CancelJobResult(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: CancelJobStatus
    def __init__(
        self, status: _Optional[_Union[CancelJobStatus, str]] = ...
    ) -> None: ...
