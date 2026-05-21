"""Locale support: BG + EN UI strings, disclaimers, language detection."""

from typing import Literal

Locale = Literal["bg", "en"]
SUPPORTED_LOCALES: frozenset[str] = frozenset({"bg", "en"})


def detect_language(text: str) -> Locale:
    sample = text[:500]
    if not sample.strip():
        return "bg"
    cyrillic = sum(1 for c in sample if "\u0400" <= c <= "\u04FF")
    return "bg" if cyrillic > len(sample) * 0.15 else "en"


def resolve_locale(query: str, lang: str | None) -> Locale:
    if lang and lang != "auto" and lang in SUPPORTED_LOCALES:
        return lang  # type: ignore[return-value]
    return detect_language(query)


UI: dict[Locale, dict[str, str]] = {
    "bg": {
        "clinical_heading": "Препоръчано от медицински насоки",
        "foods_to_eat": "Яжте",
        "foods_to_avoid": "Избягвайте",
        "sources": "Източници",
        "peer_heading": "Това споделят други пациенти",
        "peer_disclaimer": "Личен опит — не е медицински съвет.",
        "app_heading": "Приложението предлага",
        "hydration": "Хидратация",
        "symptoms_prefix": "Симптоми",
        "empty_clinical_context": "(няма релевантни откъси)",
        "empty_peer_context": "(няма релевантни откъси)",
    },
    "en": {
        "clinical_heading": "Recommended from clinical guidelines",
        "foods_to_eat": "Eat",
        "foods_to_avoid": "Avoid",
        "sources": "Sources",
        "peer_heading": "What other patients share",
        "peer_disclaimer": "Personal experience — not medical advice.",
        "app_heading": "What the app suggests",
        "hydration": "Hydration",
        "symptoms_prefix": "Symptoms",
        "empty_clinical_context": "(no relevant excerpts)",
        "empty_peer_context": "(no relevant excerpts)",
    },
}


DEFAULT_DISCLAIMER: dict[Locale, str] = {
    "bg": (
        "Това е обща хранителна информация, не медицински съвет. "
        "Съгласувайте промени в храненето с онколог или диетолог."
    ),
    "en": (
        "This is general nutrition information, not medical advice. "
        "Discuss any diet changes with your oncologist or dietitian."
    ),
}


def ui(locale: Locale, key: str) -> str:
    return UI[locale][key]
