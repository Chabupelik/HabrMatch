import os

from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
REDIS_URL = os.getenv("REDIS_URL")

result_backend = RedisAsyncResultBackend(redis_url=REDIS_URL)

broker = AioPikaBroker(
    url=RABBITMQ_URL,
    result_backend=result_backend,
)
