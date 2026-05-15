"""Redis-based rate limiter for Agentity Registry."""

import os
from datetime import datetime, timezone
from typing import Optional

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_redis: Optional = None


async def get_redis():
    global _redis
    if _redis is None:
        import redis.asyncio as aioredis
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


async def check_rate_limit(did: str, max_requests: int = 100, window_seconds: int = 60) -> tuple[bool, int]:
    """Retourne (autorisé, remaining)."""
    try:
        r = await get_redis()
        key = f"ratelimit:{did}"
        current = await r.incr(key)
        if current == 1:
            await r.expire(key, window_seconds)
        ttl = await r.ttl(key)
        return (current <= max_requests, max(0, max_requests - current))
    except Exception:
        return (True, max_requests)
