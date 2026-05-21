"""Tests for display terminology normalization."""

from src.terminology import normalize_display_text


def test_stroidi_typo():
    assert normalize_display_text("получава строиди с химио", "bg") == "получава кортикостероиди с химио"


def test_steroidi_to_corticosteroidi():
    assert normalize_display_text("при стероиди захарта е висока", "bg") == "при кортикостероиди захарта е висока"


def test_already_corticosteroidi_unchanged():
    text = "кортикостероиди повишават апетита"
    assert normalize_display_text(text, "bg") == text


def test_anabolic_steroids_unchanged():
    text = "анаболни стероиди не са тема тук"
    assert normalize_display_text(text, "bg") == text


def test_en_steroids_to_corticosteroids():
    assert normalize_display_text("on steroids appetite rises", "en") == "on corticosteroids appetite rises"


def test_bg_typo_fused_words():
    assert normalize_display_text("деня на терапиятаи продължава", "bg") == "деня на терапията и продължава"
    assert normalize_display_text("започни с бистритечности", "bg") == "започни с бистри течности"
    assert normalize_display_text("не променяй drastично диетата", "bg") == "не променяй драстично диетата"


def test_bg_semicolon_spacing():
    assert normalize_display_text("ори,з;Бистри течности", "bg") == "ори,з; Бистри течности"


def test_en_fused_word_spacing():
    text = "CALORIES_FIRST,focus on weightloss forbreakfast andhoney amountsfrequently"
    out = normalize_display_text(text, "en")
    assert "focus on" in out
    assert "CALORIES_FIRST," in out
    assert "weight loss" in out
    assert "for breakfast" in out
    assert "and honey" in out
    assert "amounts frequently" in out


def test_flatten_food_items():
    from src.terminology import flatten_food_items

    items = flatten_food_items(["супа; хляб", "drastично мазно"], "bg")
    assert items == ["супа", "хляб", "драстично мазно"]
