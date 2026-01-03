from typing import Iterable, Set

from automation_error_detector.domain.services.phrase_cache_service import (
    PhraseCacheService,
)


class InMemoryPhraseCache(PhraseCacheService):
    def __init__(self):
        self._store: dict[str, Set[str]] = {
            "auth": set(),
            "block": set(),
            "http_error": set(),
        }

    # =========================
    # SYNC
    # =========================
    def load(self, bucket: str) -> Set[str]:
        return self._store.get(bucket, set())

    def save(self, bucket: str, phrases: Iterable[str]) -> None:
        if not phrases:
            return
        self._store.setdefault(bucket, set()).update(phrases)

    # =========================
    # ASYNC
    # =========================
    async def aload(self, bucket: str) -> Set[str]:
        # In-memory nên async chỉ là wrapper
        return self.load(bucket)

    async def asave(self, bucket: str, phrases: Iterable[str]) -> None:
        # In-memory nên async chỉ là wrapper
        self.save(bucket, phrases)
