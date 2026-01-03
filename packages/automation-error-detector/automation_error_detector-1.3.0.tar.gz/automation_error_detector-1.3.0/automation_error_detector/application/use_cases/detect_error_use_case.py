from automation_error_detector.domain.services.ai_service import AIService
from automation_error_detector.domain.services.phrase_cache_service import (
    PhraseCacheService,
)
from automation_error_detector.domain.value_objects.screen_text import ScreenText
from automation_error_detector.domain.value_objects.keywords import Keywords
from automation_error_detector.domain.services.signature_service import SignatureService
from automation_error_detector.shared.normalization import (
    extract_keywords,
    is_valid_phrase,
    normalize_phrase,
)
from automation_error_detector.application.dto.error_result_dto import ErrorResultDTO
from automation_error_detector.domain.services.cache_callback import CacheSaveCallback


class DetectErrorUseCase:
    def __init__(
        self,
        cache_callback: CacheSaveCallback,
        ai_client: AIService,
        phrase_cache: PhraseCacheService,
    ):
        self.cache_callback = cache_callback
        self.ai_client = ai_client
        self.phrase_cache = phrase_cache

    # =========================
    # SYNC
    # =========================
    def execute(self, raw_text: str) -> ErrorResultDTO:
        screen_text = ScreenText(raw_text)

        keywords = Keywords(extract_keywords(screen_text.raw_text))
        signature = SignatureService.generate(
            keywords=keywords,
            purpose="ERROR",
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
        # 🔥 CALLBACK SAVE
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

        keywords = Keywords(extract_keywords(screen_text.raw_text))
        signature = SignatureService.generate(
            keywords=keywords,
            purpose="ERROR",
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

        # 🔥 CALLBACK SAVE
        await self.cache_callback.asave(signature, ai_result)

        return ErrorResultDTO(
            ai_result["error_code"],
            ai_result["short_description"],
            ai_result["keywords"],
            ai_result["suggested_action"],
            source="AI",
        )

    def _learn_phrases_from_ai(self, ai_result: dict):
        error_code = ai_result.get("error_code", "")
        keywords = ai_result.get("keywords", [])

        if error_code.startswith("HTTP"):
            bucket = "http_error"
        elif error_code.startswith("AUTH"):
            bucket = "auth"
        elif error_code.startswith("BLOCK"):
            bucket = "block"
        else:
            return  # ❌ không học UNKNOWN

        phrases = []
        for kw in keywords:
            p = normalize_phrase(kw)
            if is_valid_phrase(p):
                phrases.append(p)

        self.phrase_cache.save(bucket, phrases)
