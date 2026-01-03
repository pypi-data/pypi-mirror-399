from abc import ABC, abstractmethod
from typing import Iterable, Set


class PhraseCacheService(ABC):
    """
    Phrase cache grouped by PURPOSE (e.g. ERROR, SCREEN).
    """

    # =========================
    # SYNC
    # =========================
    @abstractmethod
    def load(self, purpose: str) -> Set[str]:
        raise NotImplementedError

    @abstractmethod
    def save(self, purpose: str, phrases: Iterable[str]) -> None:
        raise NotImplementedError

    # =========================
    # ASYNC
    # =========================
    @abstractmethod
    async def aload(self, purpose: str) -> Set[str]:
        raise NotImplementedError

    @abstractmethod
    async def asave(self, purpose: str, phrases: Iterable[str]) -> None:
        raise NotImplementedError
