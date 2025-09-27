from typing import Optional
from redis.asyncio import Redis
from app.core.config import settings

_redis: Optional[Redis] = None


async def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            ssl=bool(settings.REDIS_SSL),
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
        )
        await _redis.ping()
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None
