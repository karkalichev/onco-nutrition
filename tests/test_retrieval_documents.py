"""Unit tests for chunk ↔ LangChain document conversion (no embedding download)."""

from src.models import Chunk, Tier
from src.retrieval.documents import chunk_to_document, document_to_chunk


def test_chunk_document_roundtrip():
    chunk = Chunk(
        id="test-1",
        tier=Tier.CLINICAL,
        source_path="docs/references/sources/foo.pdf",
        source_title="Foo Guideline",
        language="bg",
        text="Препоръка за лека храна при гадене.",
    )
    doc = chunk_to_document(chunk)
    assert doc.page_content == chunk.text
    assert doc.metadata["tier"] == "clinical"
    assert doc.metadata["language"] == "bg"

    back = document_to_chunk(doc)
    assert back.id == chunk.id
    assert back.tier == chunk.tier
    assert back.text == chunk.text
