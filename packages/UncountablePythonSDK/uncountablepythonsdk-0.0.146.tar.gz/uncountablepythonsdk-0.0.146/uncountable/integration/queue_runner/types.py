from asyncio import Queue, Task

from uncountable.types import queued_job_t

ListenQueue = Queue[queued_job_t.QueuedJob]
ResultQueue = Queue[queued_job_t.QueuedJobResult]
ResultTask = Task[queued_job_t.QueuedJobResult]

RESTART_EXIT_CODE = 147
