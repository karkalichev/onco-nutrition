# Summary

Working on **onco-nutrition** — an AI assistant for nutrition during cancer treatment.

**Core concept:** two layers — (1) official medical documentation, (2) peer advice from patients — with clear labels and disclaimers.

**Stack:** Python, Anthropic API, dual-tier RAG pipeline + PatientContext (priority: `CALORIES_FIRST` | `BALANCED` | `BLOOD_SUGAR_AWARE`).

**Code:** `python -m src.cli ingest` · `python -m src.cli ask "..."` — see `src/README.md`

**Eval:** `python scripts/eval_smoke.py --dry-run` · `data/eval/cases.yaml` (10 scenarios)

**Next:** user queries in `data/raw/user-queries/` (re-ingest) · Phase 2 weekly menu UI · seasonal produce calendar · LangSmith (optional)

**Done:** vector RAG (Chroma or pgvector), dual-tier, eval smoke (`data/eval/cases.yaml`)

See `docs/concept.md` for the product concept.
