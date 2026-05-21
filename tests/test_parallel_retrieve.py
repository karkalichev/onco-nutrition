"""Dual-tier parallel retrieval (mocked search, no Chroma)."""

from src.models import Chunk, Tier
from src.retrieval.parallel import retrieve_dual_tier


def _make_chunk(chunk_id: str, tier: Tier) -> Chunk:
    return Chunk(
        id=chunk_id,
        tier=tier,
        source_path="test.md",
        source_title="Test",
        language="en",
        text="sample",
    )


def test_retrieve_dual_tier_calls_both_tiers():
    calls: list[Tier] = []

    def search(_query: str, tier: Tier, _top_k: int, _locale) -> list[Chunk]:
        calls.append(tier)
        return [_make_chunk(f"{tier.value}-1", tier)]

    clinical, peer = retrieve_dual_tier(search, "nausea after chemo", "en")
    assert {c.tier for c in clinical} == {Tier.CLINICAL}
    assert {c.tier for c in peer} == {Tier.PEER}
    assert Tier.CLINICAL in calls
    assert Tier.PEER in calls
    assert len(calls) == 2
