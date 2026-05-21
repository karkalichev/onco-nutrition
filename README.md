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

### 3. Ask from the terminal

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

### 4. Phone / tablet demo (Streamlit)

Laptop and phone on the **same Wi‑Fi**:

```bash
./scripts/run_demo_mobile.sh
```

On your phone, open the URL from the terminal or sidebar, e.g. `http://192.168.x.x:8081`.

## Project layout

```
onco-nutrition/
├── demo_app.py              # Streamlit UI (port 8081)
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
│   ├── processed/           # chunks.jsonl (generated)
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

## Configuration

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-5   # optional; avoid claude-sonnet-4-20250514 (404)
```

## Documentation

| Document | Content |
|----------|---------|
| [docs/concept.md](docs/concept.md) | Two-tier model, menu, patient context |
| [docs/architecture.md](docs/architecture.md) | Pipeline, RAG, i18n |
| [docs/decisions/001-llm-provider.md](docs/decisions/001-llm-provider.md) | Anthropic (Claude) |
| [docs/decisions/003-two-tier-knowledge.md](docs/decisions/003-two-tier-knowledge.md) | Clinical vs peer |
| [src/README.md](src/README.md) | Code layout and commands |

## Eval

```bash
python scripts/eval_smoke.py --dry-run   # priority logic only
python scripts/eval_smoke.py             # full run → data/eval/runs/
```

## MVP status

- [x] Dual-tier RAG (clinical + peer)
- [x] Anthropic + structured JSON responses
- [x] BG + EN
- [x] PatientContext in CLI and Streamlit
- [ ] Embeddings RAG (keyword search for now)
- [ ] Weekly menu + daily override (Phase 2 — example questions work in Q&A mode now)
- [ ] Seasonal produce data per country/region (beyond LLM general knowledge)

## Data / sources

References under `docs/references/` are for educational use. Archived sources are not edited — terminology normalization applies only to app output (`src/terminology.py`).
