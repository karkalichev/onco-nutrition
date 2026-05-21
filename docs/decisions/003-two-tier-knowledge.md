# 003 — Two-Tier Knowledge Model

**Дата:** 2026-05-21  
**Статус:** Прието

## Контекст

Събрани са два типа материали:
- **Официални насоки** (ESPEN, ACS, NCI, onco.bg, CancerInfo.bg)
- **Patient forums и peer съвети** (CSN, Macmillan, бъдещи user interviews)

Смесването им в един RAG index без етикетиране създава риск — LLM може да представи форумен анекдот като медицинска препоръка.

## Решение

Разделяме knowledge base на **два tier-а** с различно доверие, retrieval priority и UI presentation.

| | Tier 1: `clinical` | Tier 2: `peer` |
|---|-------------------|----------------|
| **Съдържание** | Медицински насоки, official patient booklets | Форуми, patient chats, experiential tips |
| **Доверие** | Авторитетна база | Ориентир, не факт |
| **Retrieval** | Primary, always queried | Secondary, optional |
| **UI label** | „Препоръчано от медицински насоки“ | „Това споделят други пациенти“ |
| **Override** | Never overridden by peer | Never overrides clinical without conflict flag |

## Response structure (задължително)

1. Clinical recommendations (+ source)
2. Peer insights (optional, with disclaimer)
3. App synthesis („Приложението предлага…“)
4. Footer: „Съгласувайте с лекар/диетолог“

## RAG implementation

- Две vector collections **или** един index с metadata filter `tier: clinical | peer`
- Prompt template с разделени `[CLINICAL_CONTEXT]` и `[PEER_CONTEXT]`
- System prompt: peer context explicitly marked as anecdotal

## Последствия

- `docs/references/sources/` → predominantly Tier 1
- `docs/references/forums/` → Tier 2
- `data/raw/user-queries/` → Tier 2
- Chunk pipeline must tag every document at ingest time

## Алтернативи (отхвърлени)

- **Един index, без tier** — отхвърлено (trust/safety)
- **Само clinical, без peer** — отхвърлено (губим patient language и practical tips)
- **Peer като отделно „community tab“** — може по-късно; за MVP peer е секция в същия отговор

## Референции

- [concept.md](../concept.md)
- [architecture.md](../architecture.md)
