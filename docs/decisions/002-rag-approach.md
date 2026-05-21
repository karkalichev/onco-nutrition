# 002 — RAG Approach

**Date:** 2026-05-21  
**Status:** Accepted

## Context

The MVP used keyword overlap on `chunks.jsonl`. For a portfolio demo we need semantic retrieval across **Bulgarian and English** chunks, while keeping **dual-tier** separation (clinical vs peer).

## Options considered

| Option | Pros | Cons |
|--------|------|------|
| **LangChain + Chroma** | Widely used, metadata filters, local persistence | Heavier deps; first index downloads ~400MB embedding model |
| LlamaIndex | Strong document focus | Team chose LangChain for ecosystem / hiring signal |
| Keyword only | Zero extra deps | Weak cross-language and paraphrase matching |

## Decision

**LangChain** with:

- **Embeddings:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (BG + EN)
- **Vector store:** **Chroma** persisted under `data/processed/chroma/`
- **Dual-tier:** single collection, `filter={"tier": "clinical"|"peer"}` on each query
- **Fallback:** keyword retriever when index missing or `RETRIEVAL=keyword`
- **Mode:** `RETRIEVAL=auto|vector|keyword` (`auto` → vector if Chroma exists)

Optional later: **LangSmith** tracing via standard LangChain env vars (not required for MVP).

## Implementation

```
ingest → chunks.jsonl
index  → Chroma (LangChain HuggingFaceEmbeddings + from_documents)
ask    → ChunkStore.retrieve() → clinical k=5, peer k=3
```

Commands:

```bash
python -m src.cli ingest
python -m src.cli index          # or: ingest --index
python -m src.cli ask "..."
```

## Consequences

- First `index` run downloads the embedding model (CPU by default).
- `data/processed/` remains gitignored (includes `chroma/`).
- CI unit tests avoid loading the embedding model; integration index is manual.

## References

- [003 — Two-tier knowledge](003-two-tier-knowledge.md)
- [architecture.md](../architecture.md)
- `src/retrieval/` — `keyword.py`, `vector.py`, `index_build.py`, `store.py`
