"""
Automation Error Detector
Public API
"""

# Cache
from automation_error_detector.infrastructure.cache.json_cache_repository import (
    JsonCacheCallback,
)
from automation_error_detector.infrastructure.cache.json_phrase_cache import (
    JsonPhraseCache,
)
from automation_error_detector.infrastructure.cache.redis_cache_repository import (
    RedisCacheCallback,
)
from automation_error_detector.infrastructure.cache.redis_phrase_cache import (
    RedisPhraseCacheCallback,
)

# AI
from automation_error_detector.infrastructure.ai.openai_client import (
    OpenAIClient,
)

# Use cases
from automation_error_detector.application.use_cases.detect_error_use_case import (
    DetectErrorUseCase,
)
from automation_error_detector.application.use_cases.detect_screen_use_case import (
    DetectScreenUseCase,
)


from automation_error_detector.domain.services.cache_callback import CacheSaveCallback
from automation_error_detector.config.app_config import AppConfig

__all__ = [
    "JsonCacheCallback",
    "OpenAIClient",
    "DetectErrorUseCase",
    "CacheSaveCallback",
    "AppConfig",
    "DetectScreenUseCase",
    "JsonPhraseCache",
    "RedisCacheCallback",
    "RedisPhraseCacheCallback",
]
