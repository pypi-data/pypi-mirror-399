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
from automation_error_detector.application.dto.error_result_dto import ErrorResultDTO
from automation_error_detector.domain.services.cache_callback import CacheSaveCallback


class DetectErrorUseCase(PhraseLearningMixin):
    PURPOSE = "ERROR"
    phrase_purpose = "ERROR"

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
    def execute(self, raw_text: str) -> ErrorResultDTO:
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
            return ErrorResultDTO(
                cached["error_code"],
                cached["short_description"],
                cached["keywords"],
                cached["suggested_action"],
                source="CACHE",
            )

        ai_result = self.ai_client.analyze(screen_text.raw_text)

        self._learn_phrases_from_ai(ai_result)

        self.cache_callback.save(signature, ai_result)

        return ErrorResultDTO(
            ai_result["error_code"],
            ai_result["short_description"],
            ai_result["keywords"],
            ai_result["suggested_action"],
            source="AI",
        )

    # =========================
    # ASYNC
    # =========================
    async def aexecute(self, raw_text: str) -> ErrorResultDTO:
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
            return ErrorResultDTO(
                cached["error_code"],
                cached["short_description"],
                cached["keywords"],
                cached["suggested_action"],
                source="CACHE",
            )

        ai_result = await self.ai_client.aanalyze(screen_text.raw_text)

        await self._alearn_phrases_from_ai(ai_result)

        await self.cache_callback.asave(signature, ai_result)

        return ErrorResultDTO(
            ai_result["error_code"],
            ai_result["short_description"],
            ai_result["keywords"],
            ai_result["suggested_action"],
            source="AI",
        )

    # =========================
    # PHRASE LEARNING
    # =========================
    def _map_error_bucket(self, error_code: str) -> str | None:
        if error_code.startswith("HTTP"):
            return "http_error"
        if error_code.startswith("AUTH"):
            return "auth"
        if error_code.startswith("BLOCK"):
            return "block"
        return None

    def _learn_phrases_from_ai(self, ai_result: dict) -> None:
        self._learn_phrases(ai_result.get("keywords", []))

    async def _alearn_phrases_from_ai(self, ai_result: dict) -> None:
        await self._alearn_phrases(ai_result.get("keywords", []))
