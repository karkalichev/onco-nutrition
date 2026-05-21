"""LangChain + Chroma vector retrieval with dual-tier metadata filters."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.config import CHROMA_COLLECTION, CHROMA_DIR, CLINICAL_TOP_K, PEER_TOP_K
from src.i18n import Locale
from src.models import Chunk, Tier
from src.retrieval.documents import document_to_chunk
from src.retrieval.embeddings import get_embeddings
from src.retrieval.index_build import chroma_ready

if TYPE_CHECKING:
    from langchain_chroma import Chroma


def _language_boost(score: float, chunk_lang: str, locale: Locale | None) -> float:
    if not locale:
        return score
    if chunk_lang == locale:
        return score * 1.1
    if chunk_lang not in (locale, "unknown"):
        return score * 0.9
    return score


class VectorRetriever:
    def __init__(self, chroma_dir=None):
        self._chroma_dir = chroma_dir or CHROMA_DIR
        self._store: "Chroma | None" = None

    @property
    def ready(self) -> bool:
        return chroma_ready(self._chroma_dir)

    def _get_store(self) -> Chroma:
        if not self.ready:
            raise FileNotFoundError(
                "Vector index not found. Run: python -m src.cli index"
            )
        if self._store is None:
            from langchain_chroma import Chroma

            self._store = Chroma(
                collection_name=CHROMA_COLLECTION,
                persist_directory=str(self._chroma_dir),
                embedding_function=get_embeddings(),
            )
        return self._store

    def search(
        self,
        query: str,
        tier: Tier,
        top_k: int,
        locale: Locale | None = None,
    ) -> list[Chunk]:
        store = self._get_store()
        # Fetch extra candidates, then rerank with language preference
        fetch_k = max(top_k * 2, top_k + 2)
        pairs = store.similarity_search_with_score(
            query,
            k=fetch_k,
            filter={"tier": tier.value},
        )
        if not pairs:
            return []

        # Chroma returns distance (lower = better); convert to similarity-like score
        scored: list[tuple[Chunk, float]] = []
        for doc, distance in pairs:
            chunk = document_to_chunk(doc)
            sim = 1.0 / (1.0 + float(distance))
            scored.append((chunk, _language_boost(sim, chunk.language, locale)))

        scored.sort(key=lambda x: x[1], reverse=True)
        seen: set[str] = set()
        results: list[Chunk] = []
        for chunk, _ in scored:
            if chunk.id in seen:
                continue
            seen.add(chunk.id)
            results.append(chunk)
            if len(results) >= top_k:
                break
        return results

    def retrieve(self, query: str, locale: Locale | None = None) -> tuple[list[Chunk], list[Chunk]]:
        clinical = self.search(query, Tier.CLINICAL, CLINICAL_TOP_K, locale)
        peer = self.search(query, Tier.PEER, PEER_TOP_K, locale)
        return clinical, peer
