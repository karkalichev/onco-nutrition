# Source code layout

```
src/
├── cli.py              # python -m src.cli ingest | ask
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
│   └── store.py        # keyword search by tier (MVP)
└── prompts/
    └── nutrition.py    # system prompt + context builder
```

## Commands

```bash
pip install -r requirements.txt

# 1. Build knowledge base
python -m src.cli ingest

# 2. Ask (needs ANTHROPIC_API_KEY in .env)
python -m src.cli ask "Какво да ям при гадене след химио?" \
  --symptoms nausea --cycle-day 2 --weight-trend losing

python -m src.cli ask "What should I eat when nauseous?" --lang en \
  --symptoms nausea --cycle-day 2 --weight-trend losing

python -m src.cli ask "Мога ли сладко?" --corticosteroids --glucose high_recently \
  --comorbidity diabetes

# 3. Eval smoke (priority checks + optional LLM runs)
python scripts/eval_smoke.py --dry-run
python scripts/eval_smoke.py   # saves markdown to data/eval/runs/

# 4. Mobile / tablet demo (Streamlit — same Wi‑Fi as laptop)
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


## Data flow

`docs/references/` + `data/raw/user-queries/` → **ingest** → `data/processed/chunks.jsonl` → **retrieve** → **PatientContext** → **LLM** → 4-section markdown response.

See [../docs/concept.md](../docs/concept.md) and [../docs/architecture.md](../docs/architecture.md).