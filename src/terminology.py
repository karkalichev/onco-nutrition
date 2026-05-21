"""Normalize user-facing text: correct medical terms, fix common misspellings.

Archived source documents (forums, PDFs) are never modified — only app output.
BG-specific rules apply only when locale is ``bg``.
"""

import re
from typing import Iterable

from src.i18n import Locale

# Known misspellings and vague terms → preferred display term (Bulgarian)
_BG_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("строиди", "кортикостероиди"),
    ("Строиди", "Кортикостероиди"),
    ("СТРОИДИ", "КОРТИКОСТЕРОИДИ"),
    ("строид", "кортикостероид"),
    ("Строид", "Кортикостероид"),
    ("терапиятаи", "терапията и"),
    ("бистритечности", "бистри течности"),
    ("drastично", "драстично"),
    ("Drastично", "Драстично"),
)

_BG_STEROID_WORD = re.compile(
    r"(?<![\w-])(?<!кортико)(?<!анаболни )(?<!non-)(стероиди|стероид)(?![\w-])",
    re.IGNORECASE,
)

# Missing space after semicolon in lists
_SEMICOLON_NO_SPACE = re.compile(r";([а-яА-Я])")

# Fused "та" + "и" at word end (e.g. терапията + и)
_FUSED_TA_I = re.compile(r"([а-я]{2,})таи\b")

_EN_STEROID_WORD = re.compile(
    r"(?<![\w-])(?<!cortico)(?<!anabolic )(?<!non-)(steroids?)(?![\w-])",
    re.IGNORECASE,
)

# LLM sometimes fuses words in English output
_EN_FUSED_WORDS: tuple[tuple[str, str], ...] = (
    (",focus", ", focus"),
    ("weightloss", "weight loss"),
    ("forbreakfast", "for breakfast"),
    ("andhoney", "and honey"),
    ("amountsfrequently", "amounts frequently"),
    ("CALORIES_FIRST,", "CALORIES_FIRST, "),
)


def _normalize_bg(text: str) -> str:
    for wrong, right in _BG_REPLACEMENTS:
        text = text.replace(wrong, right)

    text = _SEMICOLON_NO_SPACE.sub(r"; \1", text)
    text = _FUSED_TA_I.sub(r"\1та и", text)

    def _replace(match: re.Match[str]) -> str:
        word = match.group(1)
        if word.lower().endswith("и"):
            return "кортикостероиди" if word[0].islower() else "Кортикостероиди"
        return "кортикостероид" if word[0].islower() else "Кортикостероид"

    return _BG_STEROID_WORD.sub(_replace, text)


def _normalize_en(text: str) -> str:
    for wrong, right in _EN_FUSED_WORDS:
        text = text.replace(wrong, right)

    def _replace(match: re.Match[str]) -> str:
        word = match.group(1)
        if word.lower().endswith("s"):
            return "corticosteroids" if word[0].islower() else "Corticosteroids"
        return "corticosteroid" if word[0].islower() else "Corticosteroid"

    return _EN_STEROID_WORD.sub(_replace, text)


def normalize_display_text(text: str, locale: Locale = "bg") -> str:
    if not text:
        return text
    if locale == "en":
        return _normalize_en(text)
    return _normalize_bg(text)


def flatten_food_items(items: Iterable[str], locale: Locale = "bg") -> list[str]:
    """Split semicolon-joined LLM items and normalize each line."""
    out: list[str] = []
    for item in items:
        for part in re.split(r"\s*;\s*", item):
            part = part.strip()
            if part:
                out.append(normalize_display_text(part, locale))
    return out


def normalize_strings(items: Iterable[str], locale: Locale = "bg") -> list[str]:
    return [normalize_display_text(s, locale) for s in items]


def normalize_optional(text: str | None, locale: Locale = "bg") -> str | None:
    return normalize_display_text(text, locale) if text else text
