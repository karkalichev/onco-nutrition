"""Tests for locale detection and UI strings."""

from src.i18n import detect_language, resolve_locale, ui
from src.models import NutritionResponse


def test_detect_bulgarian():
    assert detect_language("Какво да ям при гадене?") == "bg"


def test_detect_english():
    assert detect_language("What should I eat when nauseous?") == "en"


def test_resolve_auto():
    assert resolve_locale("What to eat?", "auto") == "en"
    assert resolve_locale("Какво да ям?", "auto") == "bg"


def test_resolve_force():
    assert resolve_locale("What to eat?", "bg") == "bg"
    assert resolve_locale("Какво да ям?", "en") == "en"


def test_render_markdown_english():
    response = NutritionResponse(
        clinical_summary="Eat small meals.",
        clinical_foods_to_eat=["toast"],
        clinical_foods_to_avoid=["greasy food"],
        clinical_sources=[],
        peer_summary=None,
        peer_examples=[],
        app_meals=["Plain rice"],
        app_hydration="Water between meals",
        locale="en",
    )
    md = response.render_markdown()
    assert "Recommended from clinical guidelines" in md
    assert "What the app suggests" in md
    assert "Discuss any diet changes" in md
