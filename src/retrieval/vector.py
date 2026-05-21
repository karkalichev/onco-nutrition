"""LangChain + Chroma vector retrieval with dual-tier metadata filters."""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.documents import Document

from src.config import CHROMA_COLLECTION, CHROMA_DIR, CLINICAL_TOP_K, PEER_TOP_K
from src.i18n import Locale
from src.models import Chunk, Tier
from src.retrieval.documents import document_to_chunk
from src.retrieval.embeddings import get_embeddings
from src.retrieval.index_build import chroma_ready
from src.retrieval.parallel import retrieve_dual_tier

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


def _rank_chunks(
    pairs: list[tuple[Chunk, float]],
    top_k: int,
) -> list[Chunk]:
    pairs.sort(key=lambda x: x[1], reverse=True)
    seen: set[str] = set()
    results: list[Chunk] = []
    for chunk, _ in pairs:
        if chunk.id in seen:
            continue
        seen.add(chunk.id)
        results.append(chunk)
        if len(results) >= top_k:
            break
    return results


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

    def embed_query(self, query: str) -> list[float]:
        """Single embedding per user question (reuse for both tiers)."""
        return self._get_store().embeddings.embed_query(query)

    def search_with_vector(
        self,
        query_vector: list[float],
        tier: Tier,
        top_k: int,
        locale: Locale | None = None,
    ) -> list[Chunk]:
        """Chroma query with precomputed embedding — no second embed call."""
        store = self._get_store()
        collection = store._collection
        fetch_k = max(top_k * 2, top_k + 2)
        result = collection.query(
            query_embeddings=[query_vector],
            n_results=fetch_k,
            where={"tier": tier.value},
            include=["documents", "metadatas", "distances"],
        )

        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        if not documents:
            return []

        scored: list[tuple[Chunk, float]] = []
        for text, meta, distance in zip(documents, metadatas, distances):
            if not meta:
                continue
            doc = Document(page_content=text or "", metadata=meta)
            chunk = document_to_chunk(doc)
            sim = 1.0 / (1.0 + float(distance))
            scored.append((chunk, _language_boost(sim, chunk.language, locale)))

        return _rank_chunks(scored, top_k)

    def search(
        self,
        query: str,
        tier: Tier,
        top_k: int,
        locale: Locale | None = None,
    ) -> list[Chunk]:
        """Single-tier search (embeds once per call)."""
        return self.search_with_vector(self.embed_query(query), tier, top_k, locale)

    def retrieve(self, query: str, locale: Locale | None = None) -> tuple[list[Chunk], list[Chunk]]:
        query_vector = self.embed_query(query)
        return retrieve_dual_tier(
            lambda _q, tier, top_k, loc: self.search_with_vector(
                query_vector, tier, top_k, loc
            ),
            query,
            locale,
        )
