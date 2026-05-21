"""Keyword retriever tests (no embeddings)."""

import json
import tempfile
from pathlib import Path

from src.models import Chunk, Tier
from src.retrieval.keyword import KeywordRetriever


def _write_chunks(path: Path, chunks: list[Chunk]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c.to_dict()) + "\n")


def test_keyword_search_respects_tier():
    clinical = Chunk(
        id="c1",
        tier=Tier.CLINICAL,
        source_path="a.pdf",
        source_title="A",
        language="en",
        text="Eat bland foods when nauseous after chemotherapy.",
    )
    peer = Chunk(
        id="p1",
        tier=Tier.PEER,
        source_path="forum.md",
        source_title="Forum",
        language="en",
        text="I ate crackers when nauseous, helped me.",
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "chunks.jsonl"
        _write_chunks(path, [clinical, peer])
        store = KeywordRetriever(path)
        clin, peer_res = store.retrieve("nauseous chemotherapy", locale="en")
        assert all(c.tier == Tier.CLINICAL for c in clin)
        assert all(c.tier == Tier.PEER for c in peer_res)
        assert clin[0].id == "c1"
