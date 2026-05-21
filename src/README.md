# Source code layout

```
src/
├── cli.py              # python -m src.cli ingest | index | ask
├── config.py           # paths, tier dirs, constants
├── models.py           # Tier, Chunk, PatientContext, NutritionResponse
├── llm.py              # Anthropic JSON completion
├── assistant.py        # retrieve + generate answer
├── i18n.py             # BG + EN UI strings
├── terminology.py      # display text normalization
├── ingest/
│   ├── registry.py     # path → tier: clinical | peer
│   ├── readers.py      # .md + .pdf text extraction
│   ├── chunker.py      # split into chunks with metadata
│   └── pipeline.py     # writes data/processed/chunks.jsonl
├── retrieval/
│   ├── store.py        # ChunkStore: vector or keyword by tier
│   ├── backend.py      # Chroma vs pgvector selection
│   ├── vector.py       # LangChain + Chroma + tier filter
│   ├── pgvector.py     # PostgreSQL + pgvector + tier filter
│   ├── keyword.py      # token overlap fallback
│   ├── index_build.py  # ingest → Chroma or pgvector
│   ├── documents.py    # Chunk ↔ LangChain Document
│   └── embeddings.py   # HuggingFace multilingual model
└── prompts/
    └── nutrition.py    # system prompt + context builder
```

## Commands

```bash
pip install -r requirements.txt

# 1. Build knowledge base
python -m src.cli download-sources   # PDFs from links (local only)
python -m src.cli ingest

# 2. Vector index (Chroma default, or pgvector — see root README)
python -m src.cli index
# or: python -m src.cli ingest --index
# pgvector: docker compose up -d && VECTOR_STORE=pgvector in .env

# 3. Ask (needs ANTHROPIC_API_KEY in .env)
python -m src.cli ask "What should I eat when nauseous after chemo?" \
  --symptoms nausea --cycle-day 2 --weight-trend losing --lang en

python -m src.cli ask "What should I eat today?" --symptoms nausea --cycle-day 2 --lang en --verbose
# timing on stderr: load store, retrieve, LLM

python -m src.cli ask "What should I eat when nauseous after chemo?" \
  --symptoms nausea --cycle-day 2 --weight-trend losing --lang bg

python -m src.cli ask "Can I eat sweets today?" --corticosteroids --glucose high_recently \
  --comorbidity diabetes --lang en

# 4. Eval smoke (priority checks + optional LLM runs)
python scripts/eval_smoke.py --dry-run
python scripts/eval_smoke.py   # saves markdown to data/eval/runs/

# 5. Mobile / tablet demo (Streamlit — same Wi‑Fi as laptop)
./scripts/run_demo_mobile.sh
# or: streamlit run demo_app.py --server.address 0.0.0.0
# On phone: http://<laptop-ip>:8081  (URL also shown in app sidebar)
```

### Patient context flags


| Flag                     | Example                         |
| ------------------------ | ------------------------------- |
| `--symptoms`             | `nausea no_appetite diarrhea`   |
| `--cycle-day`            | `2` (day after chemo)           |
| `--corticosteroids`      | flag for dexamethasone days     |
| `--weight-trend`         | `stable` / `losing` / `gaining` |
| `--glucose`              | `normal` / `high_recently`      |
| `--treatment`            | `chemotherapy`                  |
| `--comorbidity`          | `diabetes`                      |
| `--dietary-restrictions` | `lactose_free`                  |
| `--country`              | `BG`                            |
| `--city`             | `Sofia`                         |

Example questions (weekly menu, substitutes, seasonal): see root [README.md](../README.md#example-questions).

## Data flow

`docs/references/` + `data/raw/user-queries/` → **ingest** → `chunks.jsonl` → **index** → `chroma/` or PostgreSQL → **retrieve** (clinical k=5, peer k=3) → **PatientContext** → **LLM** → 4-section markdown response.

Set `RETRIEVAL=auto|vector|keyword` and `VECTOR_STORE=chroma|pgvector` in `.env` (defaults: `auto`, `chroma`).

See [../docs/concept.md](../docs/concept.md) and [../docs/architecture.md](../docs/architecture.md).