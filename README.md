# Onco Nutrition Assistant

AI assistant for **nutrition during cancer treatment** — with a clear split between clinical guidelines and patient-reported experience, in **Bulgarian and English**.

> General nutrition information, not medical advice. Discuss any diet changes with your oncologist or dietitian.

## What it does

Every answer has **four sections**:

1. **Recommended from clinical guidelines** (ACS, ESPEN, onco.bg, …)
2. **What other patients share** (forums — with disclaimer)
3. **What the app suggests** (synthesis using symptoms and context)
4. **Footer** — reminder to consult the care team

Patient context (cycle day, symptoms, corticosteroids, weight, blood sugar) drives priority: `CALORIES_FIRST` | `BALANCED` | `BLOOD_SUGAR_AWARE`.

## Pipeline

```mermaid
flowchart TB
  subgraph sources["Sources (docs/references)"]
    S1["Tier 1: clinical<br/>PDFs, onco.bg, CancerInfo"]
    S2["Tier 2: peer<br/>forums, user-queries"]
  end

  subgraph offline["Offline (CLI)"]
    ING["ingest<br/>tag tier + chunk"]
    CHUNKS[("chunks.jsonl")]
    IDX["index<br/>embed 384-dim"]
    VS{{"VECTOR_STORE"}}
    CHROMA[("Chroma<br/>data/processed/chroma")]
    PG[("PostgreSQL<br/>pgvector table")]
  end

  subgraph runtime["Runtime (ask / Streamlit)"]
    Q["User question"]
    PC["PatientContext<br/>symptoms, cycle_day, glucose…"]
    PR["derive_priority()"]
    RS["ChunkStore<br/>RETRIEVAL auto|vector|keyword"]
    RC["retrieve clinical k=5"]
    RP["retrieve peer k=3"]
    LLM["Anthropic Claude<br/>structured JSON"]
    OUT["4 sections:<br/>clinical · peer · app · disclaimer"]
  end

  S1 --> ING
  S2 --> ING
  ING --> CHUNKS
  CHUNKS --> IDX
  IDX --> VS
  VS -->|chroma| CHROMA
  VS -->|pgvector| PG

  Q --> RS
  PC --> PR
  PR --> LLM
  CHUNKS -.->|keyword fallback| RS
  CHROMA -.-> RS
  PG -.-> RS
  RS --> RC
  RS --> RP
  RC --> LLM
  RP --> LLM
  LLM --> OUT
```

| Step | Command | Output |
|------|---------|--------|
| Ingest | `python -m src.cli ingest` | `data/processed/chunks.jsonl` |
| Index | `python -m src.cli index` | Chroma dir **or** `onco_chunk_embeddings` in Postgres |
| Ask | `python -m src.cli ask "…"` | Markdown (CLI) or Streamlit UI |

Details: [docs/architecture.md](docs/architecture.md) · ADR [002 — RAG](docs/decisions/002-rag-approach.md)

## Quick start

### 1. Environment

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # set ANTHROPIC_API_KEY
```

### 2. Knowledge base

```bash
python -m src.cli ingest
```

Reads `docs/references/` (PDFs + web pages) and writes `data/processed/chunks.jsonl`.

### 3. Vector index (recommended for demo)

Same embeddings for both backends: `paraphrase-multilingual-MiniLM-L12-v2` (384-dim; first `index` downloads ~400MB model). Without a vector index, `ask` falls back to keyword search.

Pick one vector store via `VECTOR_STORE` in `.env` (default **`chroma`**).

**A — Chroma (local, no database)**

```bash
# VECTOR_STORE=chroma   # default
python -m src.cli index
# or: python -m src.cli ingest --index
```

Persists under `data/processed/chroma/`.

**B — PostgreSQL + pgvector**

```bash
docker compose up -d
# .env:
#   VECTOR_STORE=pgvector
#   DATABASE_URL=postgresql://onco:onco@localhost:5432/onco_nutrition
python -m src.cli ingest   # if needed
python -m src.cli index      # creates extension + table + embeddings
```

Schema (`onco_chunk_embeddings`) is created automatically on `index` — no separate migration file.

**Troubleshooting `index` (NumPy / PyTorch errors):** use Python 3.12 and reinstall pinned deps:

```bash
pip install -r requirements.txt --upgrade
# Intel Mac (x86_64): PyPI only has torch 2.2.x — requirements.txt pins numpy<2 + transformers<5
```

If you see `numpy 2.x` + `torch 2.2` warnings, run explicitly:

```bash
pip install "numpy>=1.26.4,<2" "torch==2.2.2" "transformers>=4.41,<5" "sentence-transformers>=3.3,<4"
```

### 4. Ask from the terminal

```bash
python -m src.cli ask "What should I eat when nauseous after chemo?" \
  --symptoms nausea --cycle-day 2 --weight-trend losing --lang en

python -m src.cli ask "What should I eat when nauseous after chemo?" \
  --symptoms nausea --cycle-day 2 --weight-trend losing --lang bg
```

### Example questions

| Topic | Example (EN) |
|-------|----------------|
| Symptom | `What should I eat when nauseous after chemo?` |
| Weekly menu | `Plan a 7-day menu for my chemo cycle — day 4 after infusion, still nauseous.` |
| Daily menu | `What should I eat today? Light meals, cycle day 2, no appetite.` |
| Food substitute | `You suggested banana but banana makes me nauseous — what can I eat instead?` |
| Local / seasonal | `Suggest soft fruits for nausea this season — I'm in Sofia, Bulgaria.` |

With location flags:

```bash
python -m src.cli ask "Suggest a weekly menu with local seasonal produce." \
  --cycle-day 4 --symptoms nausea --country BG --city Sofia --lang en
```

> **Location (Phase 2+):** `country` and `city` steer toward seasonal local produce. A curated produce calendar per region is not in the MVP yet — the model uses general knowledge; patients should verify market availability.

## Phone / tablet demo (Streamlit)

**Same as before** — laptop and phone on one **Wi‑Fi**, port **8081**. The UI did not change; retrieval is vector if you ran `index` (sidebar shows Chroma or `PostgreSQL/pgvector`).

**Before first demo:**

1. `ingest` (and ideally `index` for better answers)
2. `ANTHROPIC_API_KEY` in `.env`

```bash
source venv/bin/activate
./scripts/run_demo_mobile.sh
```

The script runs `streamlit run demo_app.py` on `0.0.0.0:8081` and prints your LAN URL. On the phone open e.g. `http://192.168.x.x:8081` (also shown in the app **sidebar**).

Alternative without the script:

```bash
streamlit run demo_app.py --server.address 0.0.0.0 --server.port 8081
```

## Project layout

```
onco-nutrition/
├── demo_app.py              # Streamlit UI (port 8081)
├── docker-compose.yml       # Postgres + pgvector (optional; for VECTOR_STORE=pgvector)
├── src/                     # Python package — see src/README.md
├── scripts/
│   ├── run_demo_mobile.sh
│   └── eval_smoke.py
├── docs/
│   ├── concept.md           # Product concept (BG)
│   ├── architecture.md
│   ├── decisions/           # ADRs (LLM, RAG, two-tier)
│   └── references/          # Sources (clinical + peer)
├── data/
│   ├── processed/           # chunks.jsonl + chroma/ (generated; Chroma backend only)
│   ├── eval/                # test scenarios
│   └── raw/user-queries/    # patient interviews
└── tests/
```

## CLI flags

| Flag | Description |
|------|-------------|
| `--lang auto\|bg\|en` | Response language |
| `--symptoms` | `nausea`, `no_appetite`, `diarrhea`, … |
| `--cycle-day` | Day of cycle (1 = chemo day) |
| `--corticosteroids` | On corticosteroids today |
| `--weight-trend` | `stable` / `losing` / `gaining` |
| `--glucose` | `normal` / `high_recently` |
| `--comorbidity` | e.g. `diabetes` |
| `--country` | e.g. `BG` — seasonal / local produce hint |
| `--city` | e.g. `Sofia` |
| `-v` / `--verbose` | Timing breakdown on stderr (load, retrieve, LLM) |

## Configuration

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-5   # optional; avoid claude-sonnet-4-20250514 (404)
RETRIEVAL=auto                      # auto | vector | keyword
VECTOR_STORE=chroma                 # chroma | pgvector
# DATABASE_URL=postgresql://onco:onco@localhost:5432/onco_nutrition
```

| `RETRIEVAL` | Behavior |
|-------------|----------|
| `auto` (default) | Vector if index exists (Chroma dir or pgvector table), else keyword |
| `vector` | Semantic search (requires `python -m src.cli index`) |
| `keyword` | Token overlap only |

| `VECTOR_STORE` | Behavior |
|----------------|----------|
| `chroma` (default) | Local persisted Chroma under `data/processed/chroma/` |
| `pgvector` | Embeddings in PostgreSQL (`docker compose up -d`) |

## Documentation

| Document | Content |
|----------|---------|
| [docs/concept.md](docs/concept.md) | Two-tier model, menu, patient context |
| [docs/architecture.md](docs/architecture.md) | Pipeline, RAG, i18n |
| [docs/decisions/001-llm-provider.md](docs/decisions/001-llm-provider.md) | Anthropic (Claude) |
| [docs/decisions/002-rag-approach.md](docs/decisions/002-rag-approach.md) | LangChain + Chroma or pgvector + multilingual embeddings |
| [docs/decisions/003-two-tier-knowledge.md](docs/decisions/003-two-tier-knowledge.md) | Clinical vs peer |
| [src/README.md](src/README.md) | Code layout and commands |

## Eval

```bash
python scripts/eval_smoke.py --dry-run   # priority logic only
python scripts/eval_smoke.py             # full run → data/eval/runs/
```

## MVP status

- [x] Dual-tier RAG (clinical + peer)
- [x] Vector RAG (Chroma or PostgreSQL pgvector + multilingual embeddings) with keyword fallback
- [x] Anthropic + structured JSON responses
- [x] BG + EN
- [x] PatientContext in CLI and Streamlit
- [ ] Weekly menu + daily override (Phase 2 — example questions work in Q&A mode now)
- [ ] Seasonal produce data per country/region (beyond LLM general knowledge)

## Data / sources

References under `docs/references/` are for educational use. Archived sources are not edited — terminology normalization applies only to app output (`src/terminology.py`).
