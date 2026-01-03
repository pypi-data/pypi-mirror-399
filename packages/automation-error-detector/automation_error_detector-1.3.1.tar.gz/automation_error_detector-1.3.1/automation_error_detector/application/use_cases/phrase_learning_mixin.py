from automation_error_detector.domain.services.phrase_cache_service import (
    PhraseCacheService,
)
from automation_error_detector.shared.normalization import (
    is_valid_phrase,
    normalize_phrase,
)


class PhraseLearningMixin:
    phrase_cache: PhraseCacheService
    phrase_purpose: str  # ERROR / SCREEN

    def _learn_phrases(self, keywords: list[str]) -> None:
        phrases = []
        for kw in keywords:
            p = normalize_phrase(kw)
            if is_valid_phrase(p):
                phrases.append(p)

        if phrases:
            try:
                self.phrase_cache.save(self.phrase_purpose, phrases)
            except Exception:
                pass

    async def _alearn_phrases(self, keywords: list[str]) -> None:
        phrases = []
        for kw in keywords:
            p = normalize_phrase(kw)
            if is_valid_phrase(p):
                phrases.append(p)

        if phrases:
            try:
                await self.phrase_cache.asave(self.phrase_purpose, phrases)
            except Exception:
                pass
