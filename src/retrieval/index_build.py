"""Build vector index from chunks.jsonl (Chroma or PostgreSQL pgvector)."""

import json
import shutil
from pathlib import Path

from src.config import (
    CHROMA_DIR,
    CHROMA_COLLECTION,
    CHUNKS_FILE,
    PROJECT_ROOT,
    get_vector_store,
)
from src.models import Chunk
from src.retrieval.documents import chunk_to_document
from src.retrieval.embeddings import get_embeddings


def chroma_ready(chroma_dir: Path | None = None) -> bool:
    path = chroma_dir or CHROMA_DIR
    return path.exists() and any(path.iterdir())


def load_chunks(chunks_path: Path | None = None) -> list[Chunk]:
    path = chunks_path or CHUNKS_FILE
    chunks: list[Chunk] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(Chunk.from_dict(json.loads(line)))
    return chunks


def _build_chroma_index(
    chunks: list[Chunk],
    chroma_dir: Path,
    *,
    reset: bool,
) -> dict[str, int]:
    if reset and chroma_dir.exists():
        shutil.rmtree(chroma_dir)

    chroma_dir.mkdir(parents=True, exist_ok=True)
    documents = [chunk_to_document(c) for c in chunks]
    ids = [c.id for c in chunks]

    from langchain_chroma import Chroma

    print(f"  Embedding {len(documents)} chunks (model loads on first run)...")
    Chroma.from_documents(
        documents=documents,
        embedding=get_embeddings(),
        ids=ids,
        collection_name=CHROMA_COLLECTION,
        persist_directory=str(chroma_dir),
    )
    print(f"  Vector index → {chroma_dir.relative_to(PROJECT_ROOT)}")
    return _chunk_stats(chunks)


def _build_pgvector_index(
    chunks: list[Chunk],
    *,
    reset: bool,
) -> dict[str, int]:
    from src.retrieval.pgvector import (
        ensure_pgvector_schema,
        pg_connection,
        reset_pgvector_index,
        upsert_chunk_embeddings,
    )

    embeddings_model = get_embeddings()
    texts = [c.text for c in chunks]

    print(f"  Embedding {len(chunks)} chunks (model loads on first run)...")
    vectors = embeddings_model.embed_documents(texts)

    with pg_connection() as conn:
        ensure_pgvector_schema(conn)
        if reset:
            reset_pgvector_index(conn)
        upsert_chunk_embeddings(conn, chunks, vectors)

    print(f"  Vector index → PostgreSQL ({get_vector_store()})")
    return _chunk_stats(chunks)


def _chunk_stats(chunks: list[Chunk]) -> dict[str, int]:
    return {
        "total": len(chunks),
        "clinical": sum(1 for c in chunks if c.tier.value == "clinical"),
        "peer": sum(1 for c in chunks if c.tier.value == "peer"),
    }


def build_vector_index(
    chunks_path: Path | None = None,
    chroma_dir: Path | None = None,
    *,
    reset: bool = True,
) -> dict[str, int]:
    """Embed all chunks and persist to the configured vector store."""
    chunks_path = chunks_path or CHUNKS_FILE
    chroma_dir = chroma_dir or CHROMA_DIR

    if not chunks_path.exists():
        raise FileNotFoundError(
            f"Missing {chunks_path.relative_to(PROJECT_ROOT)}. Run: python -m src.cli ingest"
        )

    chunks = load_chunks(chunks_path)
    if not chunks:
        raise ValueError("No chunks to index.")

    if get_vector_store() == "pgvector":
        return _build_pgvector_index(chunks, reset=reset)
    return _build_chroma_index(chunks, chroma_dir, reset=reset)
