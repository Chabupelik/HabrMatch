from typing import Any

from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from app.core.config import settings

result_backend: RedisAsyncResultBackend[Any] = RedisAsyncResultBackend(
    redis_url=settings.redis_uri
)

broker = AioPikaBroker(url=settings.rabbitmq_uri).with_result_backend(result_backend)
