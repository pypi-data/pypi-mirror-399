from typing import TYPE_CHECKING, Iterable, Set, Optional

if TYPE_CHECKING:
    import redis
    import redis.asyncio as aioredis

from automation_error_detector.domain.services.phrase_cache_service import (
    PhraseCacheService,
)


class RedisPhraseCacheService(PhraseCacheService):
    def __init__(
        self,
        redis_client: "redis.Redis | None" = None,
        async_redis_client: "aioredis.Redis | None" = None,
        key_prefix: str = "phrase_cache",
        ttl_seconds: Optional[int] = None,
    ):
        """
        :param redis_client: redis.Redis (sync)
        :param async_redis_client: redis.asyncio.Redis (async)
        :param key_prefix: Redis key prefix
        :param ttl_seconds: Optional TTL for phrase buckets
        """
        if redis_client is None and async_redis_client is None:
            raise RuntimeError(
                "RedisPhraseCacheService requires redis. "
                "Install with: pip install automation-error-detector[redis]"
            )

        self.redis = redis_client
        self.async_redis = async_redis_client
        self.key_prefix = key_prefix
        self.ttl_seconds = ttl_seconds

    # =========================
    # INTERNAL
    # =========================
    def _key(self, bucket: str) -> str:
        return f"{self.key_prefix}:{bucket}"

    # =========================
    # SYNC
    # =========================
    def load(self, bucket: str) -> Set[str]:
        key = self._key(bucket)
        phrases = self.redis.smembers(key)
        return {p.decode("utf-8") if isinstance(p, bytes) else p for p in phrases}

    def save(self, bucket: str, phrases: Iterable[str]) -> None:
        phrases = list(phrases)
        if not phrases:
            return

        key = self._key(bucket)
        self.redis.sadd(key, *phrases)

        if self.ttl_seconds:
            self.redis.expire(key, self.ttl_seconds)

    # =========================
    # ASYNC
    # =========================
    async def aload(self, bucket: str) -> Set[str]:
        if not self.async_redis:
            raise RuntimeError("Async redis client not provided")

        key = self._key(bucket)
        phrases = await self.async_redis.smembers(key)
        return {p.decode("utf-8") if isinstance(p, bytes) else p for p in phrases}

    async def asave(self, bucket: str, phrases: Iterable[str]) -> None:
        if not self.async_redis:
            raise RuntimeError("Async redis client not provided")

        phrases = list(phrases)
        if not phrases:
            return

        key = self._key(bucket)
        await self.async_redis.sadd(key, *phrases)

        if self.ttl_seconds:
            await self.async_redis.expire(key, self.ttl_seconds)
