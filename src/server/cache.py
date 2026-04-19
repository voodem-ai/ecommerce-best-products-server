"""Redis caching layer for product search results."""

import json
from typing import Any

import redis.asyncio as redis
import structlog

from server.config import settings

log = structlog.get_logger()

_pool: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    """Return a shared async Redis connection (lazy-init)."""
    global _pool
    if _pool is None:
        _pool = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
        )
        log.info("redis_connected", host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    return _pool


async def close_redis() -> None:
    """Shutdown the Redis connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        log.info("redis_disconnected")


async def cache_get(key: str) -> Any | None:
    """Retrieve a cached value by key, returning parsed JSON or None."""
    r = await get_redis()
    try:
        raw = await r.get(key)
        if raw:
            log.debug("cache_hit", key=key)
            return json.loads(raw)
    except redis.ConnectionError:
        log.warning("cache_unavailable_read", key=key)
    return None


async def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    """Store a JSON-serialisable value in the cache."""
    r = await get_redis()
    ttl = ttl or settings.REDIS_TTL
    try:
        await r.setex(key, ttl, json.dumps(value))
        log.debug("cache_set", key=key, ttl=ttl)
    except redis.ConnectionError:
        log.warning("cache_unavailable_write", key=key)
