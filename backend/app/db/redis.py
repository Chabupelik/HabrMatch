from collections.abc import AsyncGenerator

from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings

redis_pool = ConnectionPool.from_url(
    settings.redis_uri,
    decode_responses=True,
)


def get_redis_client() -> Redis:
    return Redis(connection_pool=redis_pool)


async def get_redis() -> AsyncGenerator[Redis, None]:
    client = get_redis_client()
    try:
        yield client
    finally:
        await client.aclose()
