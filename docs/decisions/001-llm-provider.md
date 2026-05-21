# 001 — LLM Provider

**Date:** 2026-05-19  
**Status:** Accepted (2026-05-21)

## Context

Choice between OpenAI and Anthropic as the primary LLM provider. We have a paid Anthropic budget.

## Decision

**Anthropic** — sole provider for MVP.

- Default model: `claude-sonnet-4-5` (override with `ANTHROPIC_MODEL`)
- Auth: `ANTHROPIC_API_KEY` in `.env`
- Implementation: `src/llm.py`

## Consequences

- One API key and one SDK (`anthropic`) — simpler code and configuration
- OpenAI is not used; the `openai` package was removed from dependencies
- For a stronger model when needed: `ANTHROPIC_MODEL=claude-opus-4-5` (more expensive)

## Configuration

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-5   # optional
ANTHROPIC_MAX_TOKENS=2000         # optional
```

## When to reconsider

Stay on **one Anthropic provider** until Phase 2. Before adding a second vendor, try **two models within Anthropic** (Sonnet vs Opus) — cheaper and consistent tone/terminology.

Revisit this decision only if:

| Trigger | Action |
|---------|--------|
| **Repeated outages** at Anthropic | Optional fallback provider (unavailability only, not main flow) |
| **Eval on BG/EN questions** shows systematic medical-language errors another model fixes | A/B test with a second provider; migrate only with clear benefit |
| **Budget or latency** blocks scale | Cheaper model / shorter context first; second vendor only if insufficient |
| **Regulatory / geographic** requirement | Provider that meets data residency or compliance |

**Not worth** a second provider for: load balancing, “just in case” without metrics, or parallel answers from two models (complicates QA and two-tier UX).

Success criterion before change: fixed eval set (~20–30 real BG/EN questions) + review of terminology and disclaimers.
