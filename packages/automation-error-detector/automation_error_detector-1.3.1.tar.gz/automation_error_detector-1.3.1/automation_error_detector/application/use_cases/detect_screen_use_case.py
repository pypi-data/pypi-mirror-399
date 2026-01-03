from automation_error_detector.application.dto.screen_result_dto import ScreenResultDTO
from automation_error_detector.application.use_cases.phrase_learning_mixin import (
    PhraseLearningMixin,
)
from automation_error_detector.domain.services.ai_service import AIService
from automation_error_detector.domain.services.phrase_cache_service import (
    PhraseCacheService,
)

from automation_error_detector.domain.value_objects.screen_text import ScreenText
from automation_error_detector.domain.value_objects.keywords import Keywords
from automation_error_detector.domain.services.signature_service import SignatureService
from automation_error_detector.shared.normalization import extract_keywords
from automation_error_detector.domain.services.cache_callback import CacheSaveCallback


class DetectScreenUseCase(PhraseLearningMixin):
    PURPOSE = "SCREEN"
    phrase_purpose = "SCREEN"

    def __init__(
        self,
        cache_callback: CacheSaveCallback,
        phrase_cache: PhraseCacheService,
        ai_client: AIService,
    ):
        self.cache_callback = cache_callback
        self.phrase_cache = phrase_cache
        self.ai_client = ai_client

    # =========================
    # SYNC
    # =========================
    def execute(self, raw_text: str) -> ScreenResultDTO:
        screen_text = ScreenText(raw_text)

        keywords = Keywords(
            extract_keywords(
                screen_text.raw_text,
                self.phrase_purpose,
                self.phrase_cache,
            )
        )

        signature = SignatureService.generate(
            keywords=keywords,
            purpose=self.PURPOSE,
        )

        cached = self.cache_callback.load(signature)
        if cached:
            return ScreenResultDTO(
                screen_type=cached["screen_type"],
                confidence=cached["confidence"],
                keywords=cached["keywords"],
                reason=cached["reason"],
                source="CACHE",
            )

        ai_result = self.ai_client.detect_screen(screen_text.raw_text)

        self._learn_phrases_from_ai(ai_result)

        self.cache_callback.save(signature, ai_result)

        return ScreenResultDTO(
            screen_type=ai_result["screen_type"],
            confidence=ai_result["confidence"],
            keywords=ai_result["keywords"],
            reason=ai_result["reason"],
            source="AI",
        )

    # =========================
    # ASYNC
    # =========================
    async def aexecute(self, raw_text: str) -> ScreenResultDTO:
        screen_text = ScreenText(raw_text)

        keywords = Keywords(
            extract_keywords(
                screen_text.raw_text,
                self.phrase_purpose,
                self.phrase_cache,
            )
        )

        signature = SignatureService.generate(
            keywords=keywords,
            purpose=self.PURPOSE,
        )

        cached = await self.cache_callback.aload(signature)
        if cached:
            return ScreenResultDTO(
                screen_type=cached["screen_type"],
                confidence=cached["confidence"],
                keywords=cached["keywords"],
                reason=cached["reason"],
                source="CACHE",
            )

        ai_result = await self.ai_client.adetect_screen(screen_text.raw_text)

        await self._alearn_phrases_from_ai(ai_result)

        await self.cache_callback.asave(signature, ai_result)

        return ScreenResultDTO(
            screen_type=ai_result["screen_type"],
            confidence=ai_result["confidence"],
            keywords=ai_result["keywords"],
            reason=ai_result["reason"],
            source="AI",
        )

    # =========================
    # PHRASE LEARNING
    # =========================
    def _map_screen_bucket(self, screen_type: str) -> str | None:
        if screen_type == "permission_screen":
            return "permission"
        if screen_type == "login_screen":
            return "auth"
        return None

    def _learn_phrases_from_ai(self, ai_result: dict) -> None:
        self._learn_phrases(ai_result.get("keywords", []))

    async def _alearn_phrases_from_ai(self, ai_result: dict) -> None:
        await self._alearn_phrases(ai_result.get("keywords", []))
