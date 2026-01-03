import json
import os
import asyncio
from typing import Iterable, Set, Dict

from automation_error_detector.domain.services.phrase_cache_service import (
    PhraseCacheService,
)
from automation_error_detector.config import AppConfig


class JsonPhraseCache(PhraseCacheService):
    """
    {
      "ERROR": ["uri too long"],
      "SCREEN": ["login"]
    }
    """

    def __init__(self, file_path: str | None = None):
        self.file_path = file_path or AppConfig.phrase_cache_file

        if not os.path.exists(self.file_path):
            self._save_all({})

    # =========================
    # INTERNAL
    # =========================
    def _load_all(self) -> Dict[str, Set[str]]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return {k: set(v) for k, v in raw.items()}

    def _save_all(self, data: Dict[str, Set[str]]) -> None:
        serializable = {k: sorted(v) for k, v in data.items()}
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)

    # =========================
    # SYNC
    # =========================
    def load(self, purpose: str) -> Set[str]:
        return self._load_all().get(purpose, set())

    def save(self, purpose: str, phrases: Iterable[str]) -> None:
        phrases = set(phrases)
        if not phrases:
            return

        data = self._load_all()
        data.setdefault(purpose, set()).update(phrases)
        self._save_all(data)

    # =========================
    # ASYNC
    # =========================
    async def aload(self, purpose: str) -> Set[str]:
        return await asyncio.to_thread(self.load, purpose)

    async def asave(self, purpose: str, phrases: Iterable[str]) -> None:
        await asyncio.to_thread(self.save, purpose, phrases)
