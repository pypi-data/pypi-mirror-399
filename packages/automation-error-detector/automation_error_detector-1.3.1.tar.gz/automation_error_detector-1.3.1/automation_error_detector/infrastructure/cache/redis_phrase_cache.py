from typing import TYPE_CHECKING, Iterable, Set, Optional

if TYPE_CHECKING:
    import redis
    import redis.asyncio as aioredis

from automation_error_detector.domain.services.phrase_cache_service import (
    PhraseCacheService,
)


class RedisPhraseCacheCallback(PhraseCacheService):
    """
    Redis-based Phrase Cache (sync + async).

    Phrase cache is grouped by PURPOSE only (e.g. ERROR, SCREEN).

    Redis keys are stored as SET:
        {key_prefix}:{purpose} -> Set[str]

    Example:
        phrase_cache:ERROR
        phrase_cache:SCREEN
    """

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
        :param ttl_seconds: Optional TTL (seconds) for phrase sets
        """
        if redis_client is None and async_redis_client is None:
            raise RuntimeError(
                "RedisPhraseCache requires a redis client.\n"
                "Install optional dependency:\n"
                "  pip install automation-error-detector[redis]"
            )

        self.redis = redis_client
        self.async_redis = async_redis_client
        self.key_prefix = key_prefix
        self.ttl_seconds = ttl_seconds

    # =========================
    # INTERNAL
    # =========================
    def _key(self, purpose: str) -> str:
        return f"{self.key_prefix}:{purpose}"

    # =========================
    # SYNC
    # =========================
    def load(self, purpose: str) -> Set[str]:
        if not self.redis:
            raise RuntimeError("Sync redis client not provided")

        key = self._key(purpose)
        phrases = self.redis.smembers(key)

        return {p.decode("utf-8") if isinstance(p, bytes) else p for p in phrases}

    def save(self, purpose: str, phrases: Iterable[str]) -> None:
        if not self.redis:
            raise RuntimeError("Sync redis client not provided")

        phrases = {p for p in phrases if p}
        if not phrases:
            return

        key = self._key(purpose)
        self.redis.sadd(key, *phrases)

        if self.ttl_seconds:
            self.redis.expire(key, self.ttl_seconds)

    # =========================
    # ASYNC
    # =========================
    async def aload(self, purpose: str) -> Set[str]:
        if not self.async_redis:
            raise RuntimeError("Async redis client not provided")

        key = self._key(purpose)
        phrases = await self.async_redis.smembers(key)

        return {p.decode("utf-8") if isinstance(p, bytes) else p for p in phrases}

    async def asave(self, purpose: str, phrases: Iterable[str]) -> None:
        if not self.async_redis:
            raise RuntimeError("Async redis client not provided")

        phrases = {p for p in phrases if p}
        if not phrases:
            return

        key = self._key(purpose)
        await self.async_redis.sadd(key, *phrases)

        if self.ttl_seconds:
            await self.async_redis.expire(key, self.ttl_seconds)
