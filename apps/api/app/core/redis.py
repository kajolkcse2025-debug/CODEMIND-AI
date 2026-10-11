"""Redis behind a small interface.

Phase 1 only establishes the seam. Later phases build rate limiting, AI quotas, caching
and locks on top of ``KeyValueStore`` without depending on the redis-py API directly.
"""

import time
from functools import lru_cache
from typing import Any, Protocol

import redis

from app.config import get_settings


class KeyValueStore(Protocol):
    def ping(self) -> bool: ...

    def get(self, key: str) -> str | None: ...

    def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None: ...

    def incr(self, key: str, ttl_seconds: int | None = None) -> int:
        """Atomically increment; the TTL is applied only when the key is first created."""
        ...

    def delete(self, key: str) -> None: ...


class RedisStore:
    def __init__(self, url: str) -> None:
        self._client: Any = redis.Redis.from_url(
            url, decode_responses=True, socket_connect_timeout=2, socket_timeout=2
        )

    def ping(self) -> bool:
        return bool(self._client.ping())

    def get(self, key: str) -> str | None:
        value = self._client.get(key)
        return value if isinstance(value, str) else None

    def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        self._client.set(key, value, ex=ttl_seconds)

    def incr(self, key: str, ttl_seconds: int | None = None) -> int:
        pipe = self._client.pipeline()
        pipe.incr(key)
        if ttl_seconds is not None:
            pipe.expire(key, ttl_seconds, nx=True)
        result = pipe.execute()
        return int(result[0])

    def delete(self, key: str) -> None:
        self._client.delete(key)


class InMemoryStore:
    """Process-local store for unit tests. Never used as a production fallback."""

    def __init__(self) -> None:
        self._data: dict[str, tuple[str, float | None]] = {}

    def _alive(self, key: str) -> bool:
        item = self._data.get(key)
        if item is None:
            return False
        if item[1] is not None and item[1] <= time.monotonic():
            del self._data[key]
            return False
        return True

    def ping(self) -> bool:
        return True

    def get(self, key: str) -> str | None:
        return self._data[key][0] if self._alive(key) else None

    def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        expires = time.monotonic() + ttl_seconds if ttl_seconds is not None else None
        self._data[key] = (value, expires)

    def incr(self, key: str, ttl_seconds: int | None = None) -> int:
        if self._alive(key):
            value, expires = self._data[key]
            new_value = int(value) + 1
            self._data[key] = (str(new_value), expires)
            return new_value
        self.set(key, "1", ttl_seconds)
        return 1

    def delete(self, key: str) -> None:
        self._data.pop(key, None)


@lru_cache
def get_store() -> KeyValueStore:
    return RedisStore(get_settings().redis_url)
