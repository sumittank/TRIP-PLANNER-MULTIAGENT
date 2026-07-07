"""Simple in-memory TTL cache."""

import time
from typing import Any


class TTLCache:
    def __init__(self, ttl_seconds: int = 300):
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if not entry:
            return None
        expires_at, value = entry
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.time() + self._ttl, value)

    def clear(self) -> None:
        self._store.clear()


search_cache = TTLCache()
