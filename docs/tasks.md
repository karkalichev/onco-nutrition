# Summary
Работя върху onco-nutrition — AI асистент за диетично хранене при онко болни.

**Ключова концепция:** два слоя — (1) официална мед. документация, (2) peer съвети от пациенти — с ясни етикети и disclaimer.

Stack: Python, Anthropic API, dual-tier RAG pipeline + PatientContext (priority: CALORIES_FIRST | BALANCED | BLOOD_SUGAR_AWARE).

**Код:** `python -m src.cli ingest` · `python -m src.cli ask "..."` — виж `src/README.md`

**Eval:** `python scripts/eval_smoke.py --dry-run` · `data/eval/cases.yaml` (10 сценария)

**Следва:** user queries в `data/raw/user-queries/` (re-ingest) · Phase 2 седмично меню UI · сезонен календар · LangSmith (optional)

**Готово:** vector RAG (Chroma или pgvector), dual-tier, eval smoke (`data/eval/cases.yaml`)

Виж `docs/concept.md` за продуктовата концепция.
