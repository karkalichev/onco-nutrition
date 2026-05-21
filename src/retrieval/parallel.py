"""Run clinical + peer tier searches concurrently.

VectorRetriever embeds the query once, then runs two filtered Chroma queries in parallel.
KeywordRetriever scans chunks in parallel (no embedding).
"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

from src.config import CLINICAL_TOP_K, PEER_TOP_K
from src.i18n import Locale
from src.models import Chunk, Tier

SearchFn = Callable[[str, Tier, int, Locale | None], list[Chunk]]


def retrieve_dual_tier(
    search: SearchFn,
    query: str,
    locale: Locale | None = None,
) -> tuple[list[Chunk], list[Chunk]]:
    """Execute clinical and peer retrieval in parallel (same query, different tier filter)."""
    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="retrieve") as pool:
        clinical_future = pool.submit(
            search, query, Tier.CLINICAL, CLINICAL_TOP_K, locale
        )
        peer_future = pool.submit(search, query, Tier.PEER, PEER_TOP_K, locale)
        return clinical_future.result(), peer_future.result()
