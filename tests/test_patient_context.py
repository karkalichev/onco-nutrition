"""Tests for PatientContext derivation and prompt block."""

from src.models import PatientContext


def test_derive_priority_calories_first():
    ctx = PatientContext(
        cycle_day=2,
        symptoms_today=["nausea"],
        weight_trend="losing",
    )
    assert ctx.derive_priority() == "CALORIES_FIRST"
    assert ctx.derive_phase_hint() == "post_chemo_early"


def test_derive_priority_blood_sugar():
    ctx = PatientContext(
        on_corticosteroids_today=True,
        glucose="high_recently",
        comorbidities=["diabetes"],
    )
    assert ctx.derive_priority() == "BLOOD_SUGAR_AWARE"


def test_derive_priority_balanced():
    ctx = PatientContext(cycle_day=14, weight_trend="stable")
    assert ctx.derive_priority() == "BALANCED"
    assert ctx.derive_phase_hint() == "recovery"


def test_has_context_false_when_empty():
    assert PatientContext().has_context() is False


def test_has_context_true_with_symptoms():
    assert PatientContext(symptoms_today=["nausea"]).has_context() is True


def test_to_prompt_block_includes_priority_bg():
    ctx = PatientContext(cycle_day=2, symptoms_today=["nausea"], weight_trend="losing")
    block = ctx.to_prompt_block("bg")
    assert "[PATIENT_CONTEXT]" in block
    assert "nutrition_priority: CALORIES_FIRST" in block
    assert "симптоми_днес: nausea" in block


def test_to_prompt_block_includes_priority_en():
    ctx = PatientContext(on_corticosteroids_today=True)
    block = ctx.to_prompt_block("en")
    assert "nutrition_priority: BLOOD_SUGAR_AWARE" in block
    assert "on_corticosteroids_today: yes" in block


def test_derive_priority_diarrhea_symptom():
    ctx = PatientContext(symptoms_today=["diarrhea"], cycle_day=3)
    assert ctx.derive_priority() == "CALORIES_FIRST"


def test_to_prompt_block_includes_location():
    ctx = PatientContext(country="BG", city="Sofia")
    block = ctx.to_prompt_block("en")
    assert "country: BG" in block
    assert "city: Sofia" in block


def test_to_prompt_block_empty_bg():
    block = PatientContext().to_prompt_block("bg")
    assert "няма подаден" in block
