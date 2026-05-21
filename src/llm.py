import json
import os
import re

from dotenv import load_dotenv

from src.config import ANTHROPIC_MODEL_ALIASES, DEFAULT_ANTHROPIC_MODEL

load_dotenv()


def resolve_anthropic_model() -> str:
    """Return model ID from env, with aliases for deprecated names."""
    raw = os.getenv("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL).strip()
    return ANTHROPIC_MODEL_ALIASES.get(raw, raw)


def complete_json(system: str, user: str) -> dict:
    """Call Anthropic and parse JSON response."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is required. Set it in .env")
    model = resolve_anthropic_model()
    try:
        raw = _call_anthropic(system, user, model)
    except Exception as exc:
        if _is_model_not_found(exc):
            raise RuntimeError(
                f"Anthropic model not found: {model!r}. "
                f"Set ANTHROPIC_MODEL={DEFAULT_ANTHROPIC_MODEL!r} in .env "
                f"(or claude-opus-4-5). Remove invalid values like "
                f"'claude-sonnet-4-20250514'."
            ) from exc
        raise
    try:
        return _parse_json(raw)
    except json.JSONDecodeError as exc:
        raise json.JSONDecodeError(
            f"{exc.msg} (check ANTHROPIC_MODEL; use {DEFAULT_ANTHROPIC_MODEL} if unsure)",
            exc.doc,
            exc.pos,
        ) from exc


def _is_model_not_found(exc: BaseException) -> bool:
    name = type(exc).__name__
    if name == "NotFoundError":
        return True
    msg = str(exc).lower()
    return "not_found" in msg and "model" in msg


def _parse_json(text: str) -> dict:
    text = text.strip()
    candidates: list[str] = []

    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fence:
        candidates.append(fence.group(1))

    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start : end + 1])

    candidates.append(text)

    last_error: json.JSONDecodeError | None = None
    for candidate in candidates:
        for payload in (candidate, _repair_json(candidate)):
            try:
                return json.loads(payload)
            except json.JSONDecodeError as exc:
                last_error = exc
                continue

    if last_error:
        raise last_error
    raise json.JSONDecodeError("No JSON object found in model response", text, 0)


def _repair_json(text: str) -> str:
    """Best-effort fixes for common LLM JSON mistakes."""
    text = text.replace("\u201c", '"').replace("\u201d", '"').replace("\u2018", "'").replace("\u2019", "'")
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return text


def _call_anthropic(system: str, user: str, model: str) -> str:
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "2000")),
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text
