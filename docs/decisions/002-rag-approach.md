# 002 — RAG Approach

**Date:** 2026-05-21  
**Status:** Accepted (updated 2026-05-21 — pgvector backend)

## Context

The MVP used keyword overlap on `chunks.jsonl`. For a portfolio demo we need semantic retrieval across **Bulgarian and English** chunks, while keeping **dual-tier** separation (clinical vs peer).

## Options considered

| Option | Pros | Cons |
|--------|------|------|
| **LangChain + Chroma** | Widely used, metadata filters, local persistence, zero infra | Heavier deps; first index downloads ~400MB embedding model |
| **LangChain + PostgreSQL pgvector** | Production-shaped store, SQL ops, same embedding pipeline | Requires Postgres (`docker compose` or external DB) |
| LlamaIndex | Strong document focus | Team chose LangChain for ecosystem / hiring signal |
| Keyword only | Zero extra deps | Weak cross-language and paraphrase matching |

## Decision

**LangChain** orchestration with:

- **Embeddings:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384-dim, BG + EN)
- **Vector store (pick one via `VECTOR_STORE`):**
  - **`chroma` (default)** — persisted under `data/processed/chroma/`
  - **`pgvector`** — table `onco_chunk_embeddings` in PostgreSQL; schema created on `python -m src.cli index` (no separate migration tool)
- **Dual-tier:** metadata filter `tier: clinical | peer` on each query (same for both stores)
- **Fallback:** keyword retriever when index missing or `RETRIEVAL=keyword`
- **Mode:** `RETRIEVAL=auto|vector|keyword` (`auto` → vector if Chroma dir or pgvector table has rows)

Optional later: **LangSmith** tracing via standard LangChain env vars (not required for MVP).

## Implementation

```
ingest → chunks.jsonl
index  → Chroma (local)  OR  pgvector (PostgreSQL)
ask    → ChunkStore.retrieve() → clinical k=5, peer k=3
```

**Chroma:**

```bash
# VECTOR_STORE=chroma  (default)
python -m src.cli ingest
python -m src.cli index
python -m src.cli ask "..."
```

**pgvector:**

```bash
docker compose up -d
# .env: VECTOR_STORE=pgvector, DATABASE_URL=postgresql://onco:onco@localhost:5432/onco_nutrition
python -m src.cli ingest
python -m src.cli index
python -m src.cli ask "..."
```

## Consequences

- First `index` run downloads the embedding model (CPU by default).
- `data/processed/` remains gitignored (includes `chroma/` when using Chroma).
- pgvector needs the [pgvector](https://github.com/pgvector/pgvector) extension on the server (`pgvector/pgvector` Docker image in `docker-compose.yml`).
- CI unit tests avoid loading the embedding model; integration index is manual.

## References

- [003 — Two-tier knowledge](003-two-tier-knowledge.md)
- [architecture.md](../architecture.md)
- `src/retrieval/` — `keyword.py`, `vector.py`, `pgvector.py`, `backend.py`, `index_build.py`, `store.py`
