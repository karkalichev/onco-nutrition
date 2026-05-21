"""Build persisted Chroma index from chunks.jsonl (LangChain)."""

import json
import shutil
from pathlib import Path

from src.config import CHROMA_DIR, CHROMA_COLLECTION, CHUNKS_FILE, PROJECT_ROOT
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


def build_vector_index(
    chunks_path: Path | None = None,
    chroma_dir: Path | None = None,
    *,
    reset: bool = True,
) -> dict[str, int]:
    """Embed all chunks and persist to Chroma. First run downloads the embedding model."""
    chunks_path = chunks_path or CHUNKS_FILE
    chroma_dir = chroma_dir or CHROMA_DIR

    if not chunks_path.exists():
        raise FileNotFoundError(
            f"Missing {chunks_path.relative_to(PROJECT_ROOT)}. Run: python -m src.cli ingest"
        )

    chunks = load_chunks(chunks_path)
    if not chunks:
        raise ValueError("No chunks to index.")

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

    stats = {
        "total": len(chunks),
        "clinical": sum(1 for c in chunks if c.tier.value == "clinical"),
        "peer": sum(1 for c in chunks if c.tier.value == "peer"),
    }
    print(f"  Vector index → {chroma_dir.relative_to(PROJECT_ROOT)}")
    return stats
