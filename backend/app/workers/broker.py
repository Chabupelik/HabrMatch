import os
from typing import Any
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

RABBITMQ_URL: str = os.getenv("RABBITMQ_URL") or "amqp://guest:guest@rabbitmq:5672/"
REDIS_URL: str = os.getenv("REDIS_URL") or "redis://redis:6379/0"

result_backend: RedisAsyncResultBackend[Any] = RedisAsyncResultBackend(
    redis_url=REDIS_URL
)

broker = AioPikaBroker(
    url=RABBITMQ_URL,
    result_backend=result_backend,
)