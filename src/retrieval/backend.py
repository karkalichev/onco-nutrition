"""Vector store backend selection (Chroma local vs PostgreSQL pgvector)."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from src.config import CHROMA_DIR, get_vector_store
from src.i18n import Locale
from src.models import Chunk
from src.retrieval.index_build import chroma_ready
from src.retrieval.pgvector import PgVectorRetriever, pgvector_ready
from src.retrieval.vector import VectorRetriever


class VectorRetrieverProtocol(Protocol):
    @property
    def ready(self) -> bool: ...

    def retrieve(
        self, query: str, locale: Locale | None = None
    ) -> tuple[list[Chunk], list[Chunk]]: ...


def vector_index_ready() -> bool:
    if get_vector_store() == "pgvector":
        return pgvector_ready()
    return chroma_ready(CHROMA_DIR)


def get_vector_retriever(chroma_dir: Path | None = None) -> VectorRetrieverProtocol:
    if get_vector_store() == "pgvector":
        return PgVectorRetriever()
    return VectorRetriever(chroma_dir)
