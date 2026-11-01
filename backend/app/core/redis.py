
from functools import lru_cache

import redis

from app.core.config import settings


@lru_cache
def get_redis_client() -> redis.Redis:
    """
    Create and cache a Redis client.
    """

    return redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        health_check_interval=30,
    )


def check_redis_connection() -> bool:
    """
    Verify Redis connectivity.
    """

    try:
        return bool(get_redis_client().ping())

    except redis.RedisError:
        return False
