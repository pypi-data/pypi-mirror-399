import argparse
import json
from typing import assert_never

from dateutil import tz
from opentelemetry.trace import get_current_span
from tabulate import tabulate

from uncountable.core.environment import get_local_admin_server_port
from uncountable.integration.queue_runner.command_server.command_client import (
    send_job_cancellation_message,
    send_job_queue_message,
    send_list_queued_jobs_message,
    send_retry_job_message,
)
from uncountable.integration.queue_runner.command_server.types import (
    CommandCancelJobStatus,
)
from uncountable.integration.telemetry import Logger
from uncountable.types import queued_job_t


def register_enqueue_job_parser(
    sub_parser_manager: argparse._SubParsersAction,
    parents: list[argparse.ArgumentParser],
) -> None:
    run_parser = sub_parser_manager.add_parser(
        "run",
        parents=parents,
        help="Process a job with a given host and job ID",
        description="Process a job with a given host and job ID",
    )
    run_parser.add_argument("job_id", type=str, help="The ID of the job to process")
    run_parser.add_argument(
        "--payload", type=str, help="JSON payload for webhook invocation context"
    )

    def _handle_enqueue_job(args: argparse.Namespace) -> None:
        invocation_context: queued_job_t.InvocationContext

        if args.payload is not None:
            try:
                webhook_payload = json.loads(args.payload)
                invocation_context = queued_job_t.InvocationContextWebhook(
                    webhook_payload=webhook_payload
                )
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON payload: {e}")
        else:
            invocation_context = queued_job_t.InvocationContextManual()

        send_job_queue_message(
            job_ref_name=args.job_id,
            payload=queued_job_t.QueuedJobPayload(
                invocation_context=invocation_context
            ),
            host=args.host,
            port=get_local_admin_server_port(),
        )

    run_parser.set_defaults(func=_handle_enqueue_job)


def register_cancel_queued_job_parser(
    sub_parser_manager: argparse._SubParsersAction,
    parents: list[argparse.ArgumentParser],
) -> None:
    cancel_parser = sub_parser_manager.add_parser(
        "cancel",
        parents=parents,
        help="Cancel a queued job with a given host and queued job UUID",
        description="Cancel a job with a given host and queued job UUID",
    )
    cancel_parser.add_argument(
        "uuid", type=str, help="The UUID of the queued job to cancel"
    )

    def _handle_cancel_queued_job(args: argparse.Namespace) -> None:
        resp = send_job_cancellation_message(
            queued_job_uuid=args.uuid,
            host=args.host,
            port=get_local_admin_server_port(),
        )

        match resp:
            case CommandCancelJobStatus.CANCELLED_WITH_RESTART:
                print(
                    "Job successfully cancelled. The integration server will restart."
                )
            case CommandCancelJobStatus.NO_JOB_FOUND:
                print("Job not found.")
            case CommandCancelJobStatus.JOB_ALREADY_COMPLETED:
                print("Job already completed.")
            case _:
                assert_never(resp)

    cancel_parser.set_defaults(func=_handle_cancel_queued_job)


def register_list_queued_jobs(
    sub_parser_manager: argparse._SubParsersAction,
    parents: list[argparse.ArgumentParser],
) -> None:
    list_queued_jobs_parser = sub_parser_manager.add_parser(
        "list-queued-jobs",
        parents=parents,
        help="List all jobs queued on the integration server",
        description="List all jobs queued on the integration server",
    )

    list_queued_jobs_parser.add_argument(
        "--status",
        type=str,
        default=None,
        help="Status of the retrieved jobs",
    )

    list_queued_jobs_parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Number of jobs to skip. Should be non-negative.",
    )
    list_queued_jobs_parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="A number between 1 and 100 specifying the number of jobs to return in the result set.",
    )

    def _handle_list_queued_jobs(args: argparse.Namespace) -> None:
        queued_jobs = send_list_queued_jobs_message(
            status=args.status,
            offset=args.offset,
            limit=args.limit,
            host=args.host,
            port=get_local_admin_server_port(),
        )

        headers = ["UUID", "Job Ref Name", "Attempts", "Status", "Submitted At"]
        rows = [
            [
                job.uuid,
                job.job_ref_name,
                job.num_attempts,
                job.status,
                job.submitted_at.ToDatetime(tz.UTC).astimezone(tz.tzlocal()),
            ]
            for job in queued_jobs
        ]
        print(tabulate(rows, headers=headers, tablefmt="grid"))

    list_queued_jobs_parser.set_defaults(func=_handle_list_queued_jobs)


def register_retry_job_parser(
    sub_parser_manager: argparse._SubParsersAction,
    parents: list[argparse.ArgumentParser],
) -> None:
    retry_failed_jobs_parser = sub_parser_manager.add_parser(
        "retry-job",
        parents=parents,
        help="Retry failed job on the integration server",
        description="Retry failed job on the integration server",
    )

    retry_failed_jobs_parser.add_argument(
        "job_uuid", type=str, help="The uuid of the job to retry"
    )

    def _handle_retry_job(args: argparse.Namespace) -> None:
        send_retry_job_message(
            job_uuid=args.job_uuid,
            host=args.host,
            port=get_local_admin_server_port(),
        )

    retry_failed_jobs_parser.set_defaults(func=_handle_retry_job)


def main() -> None:
    logger = Logger(get_current_span())

    main_parser = argparse.ArgumentParser(
        description="Execute a given integrations server command."
    )

    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument(
        "--host", type=str, default="localhost", nargs="?", help="The host to run on"
    )

    subparser_action = main_parser.add_subparsers(
        dest="command",
        required=True,
        help="The command to execute (e.g., 'run')",
    )

    register_enqueue_job_parser(subparser_action, parents=[base_parser])
    register_retry_job_parser(subparser_action, parents=[base_parser])
    register_list_queued_jobs(subparser_action, parents=[base_parser])
    register_cancel_queued_job_parser(subparser_action, parents=[base_parser])

    args = main_parser.parse_args()
    with logger.push_scope(args.command):
        args.func(args)


main()
