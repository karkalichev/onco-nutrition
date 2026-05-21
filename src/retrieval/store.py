"""Unified retrieval: LangChain vector (default) with keyword fallback."""

import os
from pathlib import Path

from src.config import CHROMA_DIR, CHUNKS_FILE
from src.i18n import Locale
from src.models import Chunk
from src.retrieval.index_build import chroma_ready
from src.retrieval.keyword import KeywordRetriever
from src.retrieval.vector import VectorRetriever


def resolve_retrieval_mode() -> str:
    """auto | vector | keyword — auto uses vector when Chroma index exists."""
    mode = os.getenv("RETRIEVAL", "auto").lower()
    if mode not in ("auto", "vector", "keyword"):
        mode = "auto"
    if mode == "auto":
        return "vector" if chroma_ready(CHROMA_DIR) else "keyword"
    return mode


class ChunkStore:
    """Dual-tier retrieval facade used by assistant.ask()."""

    def __init__(
        self,
        chunks_path: Path | None = None,
        *,
        mode: str | None = None,
    ):
        self.chunks_path = chunks_path or CHUNKS_FILE
        self.mode = mode or resolve_retrieval_mode()
        self._keyword = KeywordRetriever(self.chunks_path)
        self._vector = VectorRetriever(CHROMA_DIR)
        self.chunks = self._keyword.chunks

    def load(self) -> None:
        self._keyword.load()
        self.chunks = self._keyword.chunks

    @property
    def retrieval_mode(self) -> str:
        return self.mode

    def retrieve(self, query: str, locale: Locale | None = None) -> tuple[list[Chunk], list[Chunk]]:
        if self.mode == "vector":
            try:
                return self._vector.retrieve(query, locale)
            except FileNotFoundError:
                return self._keyword.retrieve(query, locale)
        return self._keyword.retrieve(query, locale)
