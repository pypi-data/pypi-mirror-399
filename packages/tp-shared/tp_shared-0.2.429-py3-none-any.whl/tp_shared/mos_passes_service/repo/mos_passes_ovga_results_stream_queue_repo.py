from redis.asyncio import Redis
from tp_helper.base_queues.base_stream_queue_repo import BaseStreamQueueRepo

from tp_shared.mos_passes_service.schemas.mos_passes_ovga_result_message import (
    MosPassesOvgaResultStreamMessage,
)
from tp_shared.types.source_system import SourceSystem


class MosPassesOvgaTasksResultsStreamQueueRepo(BaseStreamQueueRepo):
    QUEUE_NAME = "mos:passes:service:ovga:results:stream"

    def __init__(self, redis_client: Redis, source_system: SourceSystem | None = None):
        queue_name = self.QUEUE_NAME
        if source_system is not None:
            queue_name += f":{source_system}"
        super().__init__(
            redis_client=redis_client,
            queue_name=queue_name,
            schema=MosPassesOvgaResultStreamMessage,
        )
