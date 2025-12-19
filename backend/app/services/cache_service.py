"""
Cache service for managing Redis caching with TTL and invalidation.
"""

import logging
import json
from typing import Any, Optional, Dict
from datetime import timedelta
import redis.asyncio as aioredis
from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Service for managing application caching."""

    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self._connection_pool = None

    async def connect(self):
        """Connect to Redis."""
        if not settings.redis_url:
            logger.warning("Redis URL not configured. Caching disabled.")
            return

        try:
            self.redis_client = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self.redis_client:
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        ttl_delta: Optional[timedelta] = None,
    ) -> bool:
        """Set a value in cache with optional TTL."""
        if not self.redis_client:
            return False

        try:
            serialized = json.dumps(value)
            
            if ttl_delta:
                ttl_seconds = int(ttl_delta.total_seconds())
            elif ttl:
                ttl_seconds = ttl
            else:
                ttl_seconds = None

            if ttl_seconds:
                await self.redis_client.setex(key, ttl_seconds, serialized)
            else:
                await self.redis_client.set(key, serialized)
            
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if not self.redis_client:
            return False

        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        if not self.redis_client:
            return 0

        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await self.redis_client.delete(*keys)
            
            return len(keys)
        except Exception as e:
            logger.error(f"Error deleting cache pattern {pattern}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        if not self.redis_client:
            return False

        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a numeric value in cache."""
        if not self.redis_client:
            return None

        try:
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Error incrementing cache key {key}: {e}")
            return None

    async def get_or_set(
        self,
        key: str,
        fetch_func,
        ttl: Optional[int] = None,
        ttl_delta: Optional[timedelta] = None,
    ) -> Any:
        """Get value from cache or fetch and cache it."""
        # Try to get from cache
        cached = await self.get(key)
        if cached is not None:
            return cached

        # Fetch value
        value = await fetch_func()

        # Cache it
        await self.set(key, value, ttl=ttl, ttl_delta=ttl_delta)

        return value

    async def invalidate_company_cache(self, ticker: str):
        """Invalidate all cache entries for a company."""
        patterns = [
            f"company:{ticker}:*",
            f"trades:{ticker}:*",
            f"ivt:{ticker}:*",
            f"risk:{ticker}:*",
            f"ts_score:{ticker}:*",
            f"management:{ticker}:*",
            f"competitive:{ticker}:*",
            f"competitive_strength:{ticker}:*",  # Explicit pattern for competitive strength
            f"management_score:{ticker}:*",  # Explicit pattern for management score
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = await self.delete_pattern(pattern)
            total_deleted += deleted
        
        logger.info(f"Invalidated {total_deleted} cache entries for {ticker}")
        return total_deleted


# Global cache service instance
cache_service = CacheService()

