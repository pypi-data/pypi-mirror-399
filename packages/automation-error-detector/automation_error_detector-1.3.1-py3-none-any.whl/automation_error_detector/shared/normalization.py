import re

from automation_error_detector.domain.services.phrase_cache_service import (
    PhraseCacheService,
)
from .text_dispatcher import is_vietnamese
from .vi_text_processor import extract_keywords_vi

STOPWORDS = {"the", "is", "and", "or", "to", "of", "a", "for", "on", "in"}
AUTH_PHRASES = [
    "log in",
    "login",
    "sign in",
    "sign up",
    "create account",
    "password",
    "email",
    "phone",
]

# =========================
# BLOCK SIGNALS (permission)
# =========================
BLOCK_PHRASES = [
    "not available",
    "cannot view",
    "content blocked",
    "restricted",
    "not allowed",
    "access denied",
    "unavailable",
]
HTTP_ERROR_PHRASES = [
    "uri too long",
    "request too long",
    "request rejected",
    "cannot accept the request",
    "server will not accept",
    "http error",
    "request failed",
    "bad request",
]


def normalize_phrase(p: str) -> str:
    p = p.lower().strip()
    p = re.sub(r"[^a-z0-9 ]", " ", p)
    p = re.sub(r"\s+", " ", p)
    return p


def is_valid_phrase(p: str) -> bool:
    if len(p) < 5:
        return False
    if len(p.split()) < 2:
        return False
    if p in {"error", "issue", "problem", "unknown"}:
        return False
    return True


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_dynamic_phrases(
    phrase_cache: PhraseCacheService,
    purpose: str,
) -> list[str]:
    """
    Combine static phrases with learned phrases for a given PURPOSE.
    """
    return (
        AUTH_PHRASES
        + BLOCK_PHRASES
        + HTTP_ERROR_PHRASES
        + list(phrase_cache.load(purpose))
    )


async def aget_dynamic_phrases(
    phrase_cache: PhraseCacheService,
    purpose: str,
) -> list[str]:
    return (
        AUTH_PHRASES
        + BLOCK_PHRASES
        + HTTP_ERROR_PHRASES
        + list(await phrase_cache.aload(purpose))
    )


def extract_keywords_en(
    text: str, purpose: str, phrase_cache: PhraseCacheService
) -> list[str]:
    text = normalize(text)

    keywords: set[str] = set()

    # =========================
    # AUTH SIGNALS (login)
    # =========================

    # 1️⃣ Match PHRASES (highest priority)
    for phrase in get_dynamic_phrases(phrase_cache, purpose):
        if phrase in text:
            keywords.add(phrase)

    # 2️⃣ Limited single-word fallback
    words = text.split()
    for w in words:
        if w in {"login", "password", "signin"}:
            keywords.add("login")
        elif w in {"blocked", "restricted", "denied"}:
            keywords.add("restricted")

    # 3️⃣ Safety fallback (ensure >= 2 keywords)
    if len(keywords) < 2:
        keywords.add("generic")
        keywords.add("screen")

    return sorted(keywords)


def extract_keywords(
    text: str, purpose: str, phrase_cache: PhraseCacheService
) -> list[str]:
    if is_vietnamese(text):
        return extract_keywords_vi(text, purpose, phrase_cache)
    return extract_keywords_en(text, purpose, phrase_cache)
