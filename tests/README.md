# Tests

Fast unit tests — no API keys, no embedding model download (unless noted).

## Run

```bash
pip install -r requirements-dev.txt
pytest tests/ -q
```

## Coverage

| File | What it checks |
|------|----------------|
| `test_patient_context.py` | `derive_priority`, `derive_phase_hint`, `to_prompt_block` (BG/EN) |
| `test_terminology.py` | BG/EN display fixes, `flatten_food_items` |
| `test_i18n.py` | Locale detection, markdown section titles |
| `test_keyword_retrieval.py` | Keyword tier filter (temp chunks file) |
| `test_retrieval_mode.py` | `RETRIEVAL=auto\|vector\|keyword` resolution |
| `test_retrieval_documents.py` | Chunk ↔ LangChain `Document` roundtrip |
| `test_parallel_retrieve.py` | Dual-tier runs both searches (mock) |
| `test_llm_parse.py` | JSON parsing from fences / prefill (no Anthropic) |
| `test_vector_store_config.py` | `VECTOR_STORE` env |
| `test_download_sources.py` | PDF manifest entries |

Integration / manual: `python scripts/eval_smoke.py` (needs `ANTHROPIC_API_KEY`).
