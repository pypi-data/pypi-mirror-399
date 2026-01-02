import json
from typing import Any, Dict, Optional

import redis

from .base import MemoryStore


class RedisMemoryStore(MemoryStore):
    """
    Redis-backed memory store.

    Used for:
    - Fast session memory
    - Short-lived agent context
    """

    def __init__(self, redis_client: redis.Redis):
        self._redis = redis_client

    def write(self, key: str, value: Dict[str, Any]) -> None:
        self._redis.set(key, json.dumps(value))

    def read(self, key: str) -> Optional[Dict[str, Any]]:
        raw = self._redis.get(key)
        return json.loads(raw) if raw else None

    def delete(self, key: str) -> None:
        self._redis.delete(key)
