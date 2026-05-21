# Architecture

## Overview

AI nutrition assistant for oncology patients with a **two-tier knowledge model**: clinical guidelines (authoritative) and peer patient insights (anecdotal, clearly labeled).

See [concept.md](concept.md) for product rationale.

## Stack

- **Backend:** Python
- **LLM:** Anthropic API (Claude)
- **RAG:** LangChain + Chroma + `paraphrase-multilingual-MiniLM-L12-v2` — **dual-tier retrieval** (metadata filter `tier`; keyword fallback)
- **Data:** Tier 1 PDFs/guidelines + Tier 2 forum/interview text

## Knowledge tiers

```
Tier 1 (clinical)          Tier 2 (peer)
─────────────────          ─────────────
sources/*.pdf              forums/**/*.md
web/onco-bg, cancerinfo    web/anticancer-bratan
                           data/raw/user-queries/
        │                          │
        └──────────┬───────────────┘
                   ▼
         [Ingest + tag: tier]
                   ▼
    ┌──────────────┴──────────────┐
    │  clinical index  │  peer index  │
    └──────────────┬──────────────┘
                   ▼
              [Retrieval]
         clinical first (k=5)
         peer if relevant (k=3)
                   ▼
              [LLM + structured prompt]
                   ▼
         [Response with labeled sections]
```

## Response flow

```
[Patient context] ──→ treatment, cycle_day, diagnosis, labs (self-report)
        +
[User question + symptoms today]
        ↓
[Derive phase + nutrition priority]  ← CALORIES_FIRST | BALANCED | BLOOD_SUGAR_AWARE
        ↓
[Retrieve clinical chunks] ──→ [CLINICAL_CONTEXT]
        ↓
[Retrieve peer chunks]     ──→ [PEER_CONTEXT]  (optional)
        ↓
[LLM generates structured JSON/markdown:]
  1. clinical_recommendations  (+ sources)
  2. peer_insights             (+ disclaimer, optional)
  3. app_suggestion            (synthesis; respects priority)
  4. disclaimer_footer
        ↓
[Render to user / weekly menu day slot]
```

Patient context schema: [concept.md — Patient context](concept.md#patient-context--какво-трябва-да-следим)

**Implemented:** `PatientContext` in [src/models.py](../src/models.py) — CLI flags (`--cycle-day`, `--symptoms`, `--corticosteroids`, …) → `[PATIENT_CONTEXT]` in prompt → `derive_priority()` / `derive_phase_hint()`.

**Display terminology:** archived sources keep original wording; all user-facing LLM output passes through `src/terminology.py` (locale-aware, e.g. BG „строиди“ → „кортикостероиди“, EN vague „steroids“ → „corticosteroids“).

**Locales:** BG + EN (`src/i18n.py`). CLI `--lang auto|bg|en`; auto-detects from the question. Prompts, UI labels, disclaimers, and retrieval language preference follow the resolved locale.

## Structured output schema (target)

```json
{
  "clinical": {
    "summary": "...",
    "foods_to_eat": ["..."],
    "foods_to_avoid": ["..."],
    "sources": [{"title": "ACS BG", "ref": "..."}]
  },
  "peer": {
    "summary": "...",
    "examples": ["..."],
    "confidence_note": "Личен опит — не е медицински съвет"
  },
  "app_suggestion": {
    "meals": ["..."],
    "hydration": "..."
  },
  "disclaimer": "Съгласувайте с онколог или диетолог."
}
```

## Conflict handling

If peer contradicts clinical → clinical wins in `app_suggestion`; peer shown with explicit conflict note. See [concept.md](concept.md#правила-при-конфликт).

## Decisions

- [001 — LLM provider](decisions/001-llm-provider.md)
- [002 — RAG approach](decisions/002-rag-approach.md)
- [003 — Two-tier knowledge](decisions/003-two-tier-knowledge.md)

## Directory map

| Path | Tier | Purpose |
|------|------|---------|
| `docs/references/sources/` | clinical | PDF guidelines |
| `docs/references/web/` | clinical* | Official patient education pages |
| `docs/references/forums/` | peer | Archived forum threads |
| `data/raw/user-queries/` | peer | Real user phrases from interviews |

\* `web/anticancer-bratan-dieta.md` is Tier 2 (experiential NGO tips)

## Application code

```
src/
├── cli.py           # ingest | ask
├── config.py        # paths, tier mapping
├── models.py        # Chunk, PatientContext, NutritionResponse
├── llm.py           # Anthropic JSON completion
├── assistant.py     # orchestration
├── i18n.py          # BG + EN UI strings, locale detection
├── ingest/          # docs/references → chunks.jsonl
├── retrieval/       # vector (Chroma) + keyword fallback, dual-tier
├── prompts/         # dual-tier system prompt
└── terminology.py   # normalize display text (sources unchanged)
```

See [src/README.md](../src/README.md).
