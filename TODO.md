# TODO — onco-nutrition

Планове от разговора в Cursor (май 2026). Актуализирай `[x]` ръчно.

---

## A. LangChain + RAG (портфолио / job demo)

> Източник: препоръка „Ако не си ползвал нито един — ред на учене“ (LangChain vs LlamaIndex).

### 1-ви ден — LangChain основи

- [ ] Прочети LangChain docs: **LCEL**, `VectorStoreRetriever`, **metadata filter** (`tier`)
- [ ] По желание: 2–3 ч. LlamaIndex за сравнение в интервю („помислих и двата…“)

### 2-ри ден — embeddings + Chroma

- [ ] `python -m src.cli ingest` (ако няма `chunks.jsonl`)
- [ ] `python -m src.cli index` — embed ~799 chunks, Chroma
- [ ] Сравни **vector vs keyword** на 5 въпроса от `data/eval/cases.yaml`
- [ ] Intel Mac: `numpy<2`, `torch==2.2.2`, `transformers<5`, `sentence-transformers<4` (виж `README.md`)

### 3-ти ден — интеграция в продукта

- [x] Вкарай retrieval в `ask()` — `ChunkStore` + dual-tier filter
- [x] Запази CLI + Streamlit (`demo_app.py`, `./scripts/run_demo_mobile.sh`)
- [x] ADR 002: LangChain + Chroma + multilingual embeddings

### 4-ти ден (½) — портфолио материали

- [ ] README diagram на pipeline (ingest → index → retrieve → LLM)
- [ ] LangSmith: 1 trace screenshot или линк в README (optional)
- [ ] 2–3 изречения за cover letter / CV
- [ ] Таблица eval: keyword vs vector на 5–10 cases

### Не за MVP (избягвай шум)

- Agents, multi-tool, memory, multi-agent

### Как да го разкажеш на интервю

- Проблем: clinical vs peer не се смесват
- Решение: dual-tier retrieval + отделни UI секции
- Tech: LangChain + Anthropic + structured JSON
- Product: `PatientContext` (cycle day, symptoms, country/city)
- Demo: Streamlit на телефон + CLI + `data/eval/cases.yaml`

---

## B. Домейн — какво да четеш (онко хранене)

> Източници вече са в `docs/references/`. Това е ред на **прочитане**, не сваляне.

### 1-ви ден — концепт + седмица 1

- [ ] [`docs/concept.md`](docs/concept.md) — two-tier, меню, PatientContext, приоритети
- [ ] [`docs/weekly/week-01.md`](docs/weekly/week-01.md) — симптоми, MVP scope, пазар
- [ ] [`docs/architecture.md`](docs/architecture.md) — pipeline

### 2-ри ден — клинични източници (BG)

- [ ] `docs/references/sources/acs-nutrition-during-treatment-bg.pdf` (skim по симптом)
- [ ] `docs/references/web/onco-bg-problemi-hranene.md`
- [ ] `docs/references/web/cancerinfo-hranene-po-vreme-na-lechenie.md`

### 3-ти ден — клинични (EN) + инструменти

- [ ] `docs/references/sources/espen-clinical-nutrition-in-cancer.pdf` (ключови препоръки)
- [ ] `docs/references/sources/nci-eating-hints.pdf` (симптоми + рецепти — изборочно)
- [ ] `docs/references/sources/maw-nutrition-oncology-practice-tool.pdf` (PG-SGA, MUST — skim)

### 4-ти ден — peer tier (език на пациентите)

- [ ] `docs/references/forums/README.md` + 2–3 CSN threads (`csn/`)
- [ ] 1–2 Macmillan threads (`macmillan/`)
- [ ] `docs/references/web/anticancer-bratan-dieta.md` (peer, не clinical)
- [ ] [`docs/references/communities.md`](docs/references/communities.md) — къде още има общности

### 5-ти ден — продукт + данни

- [ ] [`docs/decisions/001-llm-provider.md`](docs/decisions/001-llm-provider.md)
- [ ] [`docs/decisions/002-rag-approach.md`](docs/decisions/002-rag-approach.md)
- [ ] [`docs/decisions/003-two-tier-knowledge.md`](docs/decisions/003-two-tier-knowledge.md)
- [ ] [`docs/user-query-collection.md`](docs/user-query-collection.md) — преди интервю с пациент

---

## C. Реални user queries (среща с пациент)

> Източник: „За утре“ — guide + template.

- [ ] Прочети [`docs/user-query-collection.md`](docs/user-query-collection.md) (6 отворени въпроса)
- [ ] Среща → попълни [`data/raw/user-queries/TEMPLATE.md`](data/raw/user-queries/TEMPLATE.md)
- [ ] Цел: **≥10 реални BG фрази** от **≥3 симптома**
- [ ] Копирай в `data/raw/user-queries/queries.json` (не се commit-ва)
- [ ] Тествай с `python scripts/eval_smoke.py`

---

## D. Следващи продуктови задачи

- [ ] Phase 2: седмично меню + дневен override в UI
- [ ] Календар сезонни продукти по `country` / `city` (структурирани данни)
- [ ] Повече BG user queries в RAG
- [ ] LangSmith tracing (optional)

---

## Бързи команди

```bash
python -m src.cli ingest
python -m src.cli index
python -m src.cli ask "..." --symptoms nausea --cycle-day 2 --lang bg
./scripts/run_demo_mobile.sh
python scripts/eval_smoke.py --dry-run
```