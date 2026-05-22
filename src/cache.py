"""Redis cache and session management"""

import redis.asyncio as redis
from typing import Any, Optional
import json
import logging

from src.config import settings

logger = logging.getLogger(__name__)

redis_client: Optional[redis.Redis] = None


async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = await redis.from_url(
            settings.redis_url,
            encoding="utf8",
            decode_responses=True,
        )
        # Test connection
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


async def get_redis() -> redis.Redis:
    """Get Redis client"""
    if not redis_client:
        await init_redis()
    return redis_client


async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        client = await get_redis()
        value = await client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    except Exception as e:
        logger.error(f"Cache get error for key {key}: {e}")
        return None


async def cache_set(
    key: str,
    value: Any,
    ttl: Optional[int] = None,
) -> bool:
    """Set value in cache"""
    try:
        client = await get_redis()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        ttl = ttl or settings.redis_cache_ttl
        await client.setex(key, ttl, value)
        return True
    except Exception as e:
        logger.error(f"Cache set error for key {key}: {e}")
        return False


async def cache_delete(key: str) -> bool:
    """Delete value from cache"""
    try:
        client = await get_redis()
        await client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Cache delete error for key {key}: {e}")
        return False


async def cache_clear_pattern(pattern: str) -> int:
    """Clear all keys matching pattern"""
    try:
        client = await get_redis()
        keys = await client.keys(pattern)
        if keys:
            return await client.delete(*keys)
        return 0
    except Exception as e:
        logger.error(f"Cache clear pattern error for {pattern}: {e}")
        return 0


async def session_set(
    session_id: str,
    data: dict,
    ttl: Optional[int] = None,
) -> bool:
    """Store session data"""
    ttl = ttl or settings.redis_session_ttl
    return await cache_set(f"session:{session_id}", data, ttl)


async def session_get(session_id: str) -> Optional[dict]:
    """Retrieve session data"""
    return await cache_get(f"session:{session_id}")


async def session_delete(session_id: str) -> bool:
    """Delete session"""
    return await cache_delete(f"session:{session_id}")


async def rate_limit_check(
    key: str,
    limit: int,
    window: int = 60,
) -> tuple[bool, int]:
    """
    Check rate limit using sliding window counter
    
    Returns:
        (allowed: bool, remaining: int)
    """
    try:
        client = await get_redis()
        current = await client.incr(f"rate_limit:{key}")
        
        if current == 1:
            await client.expire(f"rate_limit:{key}", window)
        
        remaining = max(0, limit - current)
        allowed = current <= limit
        
        return allowed, remaining
    except Exception as e:
        logger.error(f"Rate limit check error for key {key}: {e}")
        return True, limit  # Allow on error


async def rate_limit_reset(key: str) -> bool:
    """Reset rate limit counter"""
    return await cache_delete(f"rate_limit:{key}")
