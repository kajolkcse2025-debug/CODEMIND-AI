import time

import pytest

from app.core.redis import InMemoryStore, RedisStore
from tests.conftest import TEST_REDIS_URL


def test_in_memory_store_get_set_delete() -> None:
    store = InMemoryStore()
    assert store.get("k") is None
    store.set("k", "v")
    assert store.get("k") == "v"
    store.delete("k")
    assert store.get("k") is None


def test_in_memory_incr_counts_and_expires() -> None:
    store = InMemoryStore()
    assert [store.incr("n", ttl_seconds=60) for _ in range(3)] == [1, 2, 3]
    store.set("short", "x", ttl_seconds=0)
    time.sleep(0.01)
    assert store.get("short") is None


@pytest.mark.redis
def test_redis_store_round_trip() -> None:
    store = RedisStore(TEST_REDIS_URL)
    assert store.ping() is True
    store.delete("test:k")
    assert store.get("test:k") is None
    store.set("test:k", "v", ttl_seconds=30)
    assert store.get("test:k") == "v"
    store.delete("test:counter")
    assert [store.incr("test:counter", ttl_seconds=30) for _ in range(3)] == [1, 2, 3]
    store.delete("test:k")
    store.delete("test:counter")
