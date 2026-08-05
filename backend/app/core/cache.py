import time
from typing import Any, Optional, Dict

class MemoryCache:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        item = self._cache.get(key)
        if not item:
            return None
        if item["expires_at"] and time.time() > item["expires_at"]:
            del self._cache[key]
            return None
        return item["value"]

    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        expires_at = time.time() + ttl_seconds if ttl_seconds > 0 else None
        self._cache[key] = {
            "value": value,
            "expires_at": expires_at
        }

    def delete(self, key: str):
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        self._cache.clear()

cache = MemoryCache()
