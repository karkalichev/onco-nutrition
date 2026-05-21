# Summary
Работя върху onco-nutrition — AI асистент за диетично хранене при онко болни.

**Ключова концепция:** два слоя — (1) официална мед. документация, (2) peer съвети от пациенти — с ясни етикети и disclaimer.

Stack: Python, Anthropic API, dual-tier RAG pipeline + PatientContext (priority: CALORIES_FIRST | BALANCED | BLOOD_SUGAR_AWARE).

**Код:** `python -m src.cli ingest` · `python -m src.cli ask "..."` — виж `src/README.md`

**Eval:** `python scripts/eval_smoke.py --dry-run` · `data/eval/cases.yaml` (10 сценария)

**Следва (когато има повече данни):** user queries в `data/raw/user-queries/` · embeddings RAG · Phase 2 седмично меню

Виж `docs/concept.md` за продуктовата концепция.
