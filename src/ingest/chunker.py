import hashlib
import re
import uuid
from pathlib import Path

from src.config import CHUNK_OVERLAP, CHUNK_SIZE
from src.ingest.registry import infer_language, source_title
from src.models import Chunk, Tier


def _split_markdown_sections(text: str) -> list[str]:
    parts = re.split(r"\n(?=#{1,3}\s)", text)
    sections = [p.strip() for p in parts if p.strip()]
    return sections if sections else [text.strip()]


def _split_fixed(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= size:
        return [text] if text else []

    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def _chunk_id(source_path: str, index: int, text: str) -> str:
    digest = hashlib.sha256(f"{source_path}:{index}:{text[:80]}".encode()).hexdigest()[:12]
    return f"chk-{digest}"


def chunk_document(path: Path, tier: Tier, text: str) -> list[Chunk]:
    from src.config import PROJECT_ROOT

    try:
        path_str = str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        path_str = str(path)

    title = source_title(path)
    language = infer_language(path, text)

    if path.suffix.lower() == ".md":
        raw_sections = _split_markdown_sections(text)
    else:
        raw_sections = [text]

    pieces: list[str] = []
    for section in raw_sections:
        if len(section) <= CHUNK_SIZE * 1.5:
            pieces.append(section)
        else:
            pieces.extend(_split_fixed(section))

    chunks: list[Chunk] = []
    for i, piece in enumerate(pieces):
        if len(piece) < 40:
            continue
        chunks.append(
            Chunk(
                id=_chunk_id(path_str, i, piece),
                tier=tier,
                source_path=path_str,
                source_title=title,
                language=language,
                text=piece,
            )
        )
    return chunks
