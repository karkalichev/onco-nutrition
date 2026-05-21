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


_JSON_RETRY_SUFFIX = (
    "\n\n[SYSTEM NOTE] Your previous reply was empty or not valid JSON. "
    "Respond with ONLY one JSON object matching the schema. No markdown fences, no commentary."
)


_TRUNCATED_SUFFIX = (
    "\n\n[SYSTEM NOTE] Previous JSON was cut off (token limit). "
    "Reply with ONLY valid JSON. Keep each string brief (1-2 sentences max)."
)


def complete_json(system: str, user: str) -> dict:
    """Call Anthropic and parse JSON response."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is required. Set it in .env")
    model = resolve_anthropic_model()
    last_raw = ""
    user_msg = user
    for attempt in range(2):
        try:
            last_raw, stop_reason = _call_anthropic(system, user_msg, model)
        except Exception as exc:
            if _is_model_not_found(exc):
                raise RuntimeError(
                    f"Anthropic model not found: {model!r}. "
                    f"Set ANTHROPIC_MODEL={DEFAULT_ANTHROPIC_MODEL!r} in .env "
                    f"(or claude-opus-4-5). Remove invalid values like "
                    f"'claude-sonnet-4-20250514'."
                ) from exc
            raise
        if not last_raw.strip():
            user_msg = user + _JSON_RETRY_SUFFIX
            continue
        try:
            return _parse_json(last_raw)
        except json.JSONDecodeError:
            if attempt == 0:
                user_msg = user + (
                    _TRUNCATED_SUFFIX if stop_reason == "max_tokens" else _JSON_RETRY_SUFFIX
                )
                continue
            raise _json_parse_error(last_raw, model, stop_reason)
    raise RuntimeError(
        f"Empty response from Anthropic model {model!r}. "
        "Retry the request or check API status."
    )


def _is_model_not_found(exc: BaseException) -> bool:
    name = type(exc).__name__
    if name == "NotFoundError":
        return True
    msg = str(exc).lower()
    return "not_found" in msg and "model" in msg


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json fences even when the closing ``` is missing (truncated response)."""
    t = text.strip()
    if not t.startswith("```"):
        return t
    t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.IGNORECASE)
    if "```" in t:
        t = t[: t.rfind("```")].strip()
    return t.strip()


def _parse_json(text: str) -> dict:
    text = _strip_markdown_fences(text.strip())
    candidates: list[str] = []

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


def _json_parse_error(
    raw: str, model: str, stop_reason: str | None = None
) -> json.JSONDecodeError:
    preview = raw.strip().replace("\n", " ")[:240]
    hint = (
        "Response may be truncated — set ANTHROPIC_MAX_TOKENS=4096 in .env and retry."
        if stop_reason == "max_tokens"
        else "Check ANTHROPIC_MODEL or retry."
    )
    msg = f"Model returned non-JSON (model={model!r}). Preview: {preview!r} … {hint}"
    return json.JSONDecodeError(msg, raw, 0)


def _extract_message_text(response: object) -> str:
    """Concatenate all text blocks from the API response."""
    parts: list[str] = []
    for block in getattr(response, "content", []) or []:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return "\n".join(parts).strip()


def _call_anthropic(system: str, user: str, model: str) -> tuple[str, str | None]:
    import anthropic

    client = anthropic.Anthropic()
    # Assistant prefill steers raw JSON (no ```json fences).
    messages: list[dict[str, str]] = [
        {"role": "user", "content": user},
        {"role": "assistant", "content": "{"},
    ]
    response = client.messages.create(
        model=model,
        max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096")),
        system=system,
        messages=messages,
    )
    stop_reason = getattr(response, "stop_reason", None)
    body = _extract_message_text(response)
    return "{" + body, stop_reason
