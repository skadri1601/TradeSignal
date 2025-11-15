import os
import json
import redis
from typing import Any, Optional, List, Union


class RedisCache:
    def __init__(self):
        self._enabled = True
        self.redis: Optional[redis.Redis] = None
        try:
            self.redis = redis.Redis(
                host=os.getenv("REDIS_HOST", "redis"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                db=int(os.getenv("REDIS_DB", "0")),
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            # Test connection
            self.redis.ping()
        except Exception:
            # If redis is not available, gracefully disable cache
            self._enabled = False
            self.redis = None

    def enabled(self) -> bool:
        return self._enabled and self.redis is not None

    def get(self, key: str) -> Optional[dict]:
        if not self.enabled() or self.redis is None:
            return None
        try:
            value = self.redis.get(key)
            if value is not None:
                return json.loads(value)  # type: ignore
            return None
        except Exception:
            return None

    def set(self, key: str, value: dict, ttl: int = 10) -> None:
        if not self.enabled() or self.redis is None:
            return
        try:
            self.redis.setex(key, ttl, json.dumps(value))
        except Exception:
            return

    def mget(self, keys: List[str]) -> List[Optional[dict]]:
        if not self.enabled() or self.redis is None:
            return [None] * len(keys)
        try:
            values = self.redis.mget(keys)  # type: ignore
            result: List[Optional[dict]] = []
            for v in values:  # type: ignore
                if v is not None:
                    result.append(json.loads(v))  # type: ignore
                else:
                    result.append(None)
            return result
        except Exception:
            return [None] * len(keys)

    def delete(self, key: str) -> None:
        if not self.enabled() or self.redis is None:
            return
        try:
            self.redis.delete(key)
        except Exception:
            return

    def exists(self, key: str) -> bool:
        if not self.enabled() or self.redis is None:
            return False
        try:
            result = self.redis.exists(key)  # type: ignore
            return result > 0  # type: ignore
        except Exception:
            return False


# Singleton instance for the app to reuse
_cache = None


def get_cache() -> RedisCache:
    global _cache
    if _cache is None:
        _cache = RedisCache()
    return _cache
