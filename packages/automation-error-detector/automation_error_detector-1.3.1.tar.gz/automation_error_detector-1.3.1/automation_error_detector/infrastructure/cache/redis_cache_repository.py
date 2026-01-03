import json
from typing import Optional, Dict, Any, TYPE_CHECKING

from automation_error_detector.domain.services.cache_callback import CacheSaveCallback

if TYPE_CHECKING:
    import redis
    import redis.asyncio as aioredis


class RedisCacheCallback(CacheSaveCallback):
    """
    Redis-based cache callback for automation error detector.

    Stores cache data using signature as Redis key.
    """

    def __init__(
        self,
        redis_client: "redis.Redis | None" = None,
        async_redis_client: "aioredis.Redis | None" = None,
        key_prefix: str = "automation_error_cache",
        ttl_seconds: Optional[int] = None,
    ):
        if redis_client is None and async_redis_client is None:
            raise RuntimeError(
                "RedisCacheCallback requires redis support. "
                "Install with: pip install automation-error-detector[redis]"
            )

        self.redis = redis_client
        self.async_redis = async_redis_client
        self.key_prefix = key_prefix
        self.ttl_seconds = ttl_seconds

    # =========================
    # INTERNAL
    # =========================
    def _key(self, signature: str) -> str:
        return f"{self.key_prefix}:{signature}"

    # =========================
    # SYNC
    # =========================
    def load(self, signature: str) -> Optional[Dict[str, Any]]:
        if not self.redis:
            return None

        value = self.redis.get(self._key(signature))
        if not value:
            return None

        return json.loads(value)

    def save(self, signature: str, data: Dict[str, Any]) -> None:
        if not self.redis:
            return

        key = self._key(signature)
        payload = json.dumps(data)

        self.redis.set(key, payload)

        if self.ttl_seconds:
            self.redis.expire(key, self.ttl_seconds)

    # =========================
    # ASYNC
    # =========================
    async def aload(self, signature: str) -> Optional[Dict[str, Any]]:
        if not self.async_redis:
            return None

        value = await self.async_redis.get(self._key(signature))
        if not value:
            return None

        return json.loads(value)

    async def asave(self, signature: str, data: Dict[str, Any]) -> None:
        if not self.async_redis:
            return

        key = self._key(signature)
        payload = json.dumps(data)

        await self.async_redis.set(key, payload)

        if self.ttl_seconds:
            await self.async_redis.expire(key, self.ttl_seconds)
