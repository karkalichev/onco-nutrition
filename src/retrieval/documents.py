"""Convert Chunk models to/from LangChain documents."""

from langchain_core.documents import Document

from src.models import Chunk, Tier


def chunk_to_document(chunk: Chunk) -> Document:
    return Document(
        page_content=chunk.text,
        metadata={
            "id": chunk.id,
            "tier": chunk.tier.value,
            "language": chunk.language,
            "source_path": chunk.source_path,
            "source_title": chunk.source_title,
        },
    )


def document_to_chunk(doc: Document) -> Chunk:
    meta = doc.metadata
    return Chunk(
        id=meta["id"],
        tier=Tier(meta["tier"]),
        source_path=meta["source_path"],
        source_title=meta["source_title"],
        language=meta.get("language", "unknown"),
        text=doc.page_content,
    )
