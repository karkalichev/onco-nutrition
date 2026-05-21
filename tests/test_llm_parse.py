"""LLM JSON parsing helpers (no Anthropic API)."""

import json

import pytest

from src.llm import _parse_json, _strip_markdown_fences


def test_strip_markdown_fences_without_closing_backticks():
    raw = '```json\n{"clinical": {"summary": "ok"}, "peer": null}\n'
    assert _strip_markdown_fences(raw).startswith('{"clinical"')


def test_parse_json_from_markdown_fence():
    raw = """```json
{
  "clinical": {"summary": "Eat small meals.", "foods_to_eat": [], "foods_to_avoid": [], "sources": []},
  "peer": {"summary": null, "examples": []},
  "app_suggestion": {"meals": [], "hydration": "water"},
  "disclaimer": "Ask your doctor."
}
```"""
    data = _parse_json(raw)
    assert data["clinical"]["summary"] == "Eat small meals."
    assert data["peer"]["summary"] is None


def test_parse_json_assistant_prefill_body():
    raw = (
        '{"clinical": {"summary": "x", "foods_to_eat": [], "foods_to_avoid": [], '
        '"sources": []}, "peer": {"summary": null, "examples": []}, '
        '"app_suggestion": {"meals": [], "hydration": "y"}, "disclaimer": "z"}'
    )
    data = _parse_json(raw)
    assert data["app_suggestion"]["hydration"] == "y"


def test_parse_json_invalid_raises():
    with pytest.raises(json.JSONDecodeError):
        _parse_json("not json at all")
