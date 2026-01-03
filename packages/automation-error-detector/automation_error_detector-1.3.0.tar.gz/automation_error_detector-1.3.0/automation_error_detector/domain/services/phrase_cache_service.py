# domain/services/phrase_cache_service.py
from abc import ABC, abstractmethod
from typing import Iterable, Set


class PhraseCacheService(ABC):
    """
    Phrase cache service for self-learning keyword/phrase detection.

    This cache stores normalized phrases learned from AI results,
    grouped by semantic bucket (e.g. auth, block, http_error).
    """

    # =========================
    # SYNC
    # =========================
    @abstractmethod
    def load(self, bucket: str) -> Set[str]:
        """
        Load cached phrases by bucket.

        :param bucket: Phrase category (e.g. auth, block, http_error)
        :return: Set of normalized phrases
        """
        raise NotImplementedError

    @abstractmethod
    def save(self, bucket: str, phrases: Iterable[str]) -> None:
        """
        Persist phrases into cache.

        :param bucket: Phrase category
        :param phrases: Iterable of normalized phrases
        """
        raise NotImplementedError

    # =========================
    # ASYNC
    # =========================
    @abstractmethod
    async def aload(self, bucket: str) -> Set[str]:
        """
        Async version of load_phrases().
        """
        raise NotImplementedError

    @abstractmethod
    async def asave_(self, bucket: str, phrases: Iterable[str]) -> None:
        """
        Async version of save_phrases().
        """
        raise NotImplementedError
