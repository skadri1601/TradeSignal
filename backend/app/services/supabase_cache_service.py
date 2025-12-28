"""
Supabase Cache Service

Generic caching service using Supabase PostgreSQL instead of Redis.
Replaces Redis-based caching for on-demand data fetching with TTL support.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class SupabaseCacheService:
    """
    Generic Supabase-based caching service (replaces Redis).
    
    Uses Supabase PostgreSQL table for caching with TTL support.
    """

    def __init__(self):
        """Initialize Supabase cache service."""
        self.enabled = False
        self.client = None
        
        # Check if Supabase is configured
        if hasattr(settings, 'supabase_url') and hasattr(settings, 'supabase_service_role_key'):
            if settings.supabase_url and settings.supabase_service_role_key:
                try:
                    from supabase import create_client, Client
                    self.client = create_client(
                        settings.supabase_url,
                        settings.supabase_service_role_key
                    )
                    self.enabled = True
                    logger.info("Supabase cache service initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize Supabase cache: {e}")
                    self.enabled = False
            else:
                logger.warning("Supabase URL or service role key not configured. Cache disabled.")
        else:
            logger.warning("Supabase settings not found. Cache disabled.")

    async def get(self, cache_key: str) -> Optional[Any]:
        """
        Get cached data if not expired.
        
        Args:
            cache_key: Unique cache key
            
        Returns:
            Cached data if found and not expired, None otherwise
        """
        if not self.enabled or not self.client:
            return None

        try:
            now = datetime.now(timezone.utc).isoformat()
            
            # Query for non-expired cache entry
            response = self.client.table("api_cache") \
                .select("data") \
                .eq("cache_key", cache_key) \
                .gt("expires_at", now) \
                .limit(1) \
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0].get("data")
            
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {cache_key}: {e}")
            return None

    async def set(
        self, 
        cache_key: str, 
        data: Any, 
        ttl_minutes: int = 15, 
        cache_type: str = "general"
    ) -> bool:
        """
        Store data in cache with TTL.
        
        Args:
            cache_key: Unique cache key
            data: Data to cache (will be stored as JSONB)
            ttl_minutes: Time to live in minutes (default: 15)
            cache_type: Type of cache (e.g., 'news', 'sec', 'research')
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(minutes=ttl_minutes)
            
            # Upsert cache entry (update if exists, insert if not)
            self.client.table("api_cache").upsert({
                "cache_key": cache_key,
                "data": data,
                "fetched_at": now.isoformat(),
                "expires_at": expires_at.isoformat(),
                "cache_type": cache_type
            }, on_conflict="cache_key").execute()
            
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {cache_key}: {e}")
            return False

    async def delete(self, cache_key: str) -> bool:
        """
        Delete cached data.
        
        Args:
            cache_key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            self.client.table("api_cache") \
                .delete() \
                .eq("cache_key", cache_key) \
                .execute()
            
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {cache_key}: {e}")
            return False

    async def clear_expired(self) -> int:
        """
        Clean up expired cache entries.
        
        Returns:
            Number of entries deleted
        """
        if not self.enabled or not self.client:
            return 0

        try:
            now = datetime.now(timezone.utc).isoformat()
            
            # Delete expired entries
            response = self.client.table("api_cache") \
                .delete() \
                .lt("expires_at", now) \
                .execute()
            
            # Count deleted (response structure may vary)
            deleted_count = len(response.data) if hasattr(response, 'data') else 0
            logger.info(f"Cleared {deleted_count} expired cache entries")
            
            return deleted_count
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
            return 0

    async def get_or_set(
        self,
        cache_key: str,
        fetch_func,
        ttl_minutes: int = 15,
        cache_type: str = "general"
    ) -> Any:
        """
        Get value from cache or fetch and cache it.
        
        Args:
            cache_key: Unique cache key
            fetch_func: Async function to fetch data if cache miss
            ttl_minutes: Time to live in minutes
            cache_type: Type of cache
            
        Returns:
            Cached or freshly fetched data
        """
        # Try to get from cache
        cached = await self.get(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit for key: {cache_key}")
            return cached

        # Cache miss - fetch data
        logger.debug(f"Cache miss for key: {cache_key}, fetching...")
        value = await fetch_func()

        # Cache it
        await self.set(cache_key, value, ttl_minutes=ttl_minutes, cache_type=cache_type)

        return value


# Singleton instance
supabase_cache_service = SupabaseCacheService()
