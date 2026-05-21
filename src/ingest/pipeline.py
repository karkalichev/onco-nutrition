import json
from pathlib import Path

from src.config import CHUNKS_FILE, CLINICAL_DIRS, DATA_PROCESSED, PEER_DIRS, PROJECT_ROOT
from src.ingest.chunker import chunk_document
from src.ingest.readers import read_markdown, read_pdf
from src.ingest.registry import resolve_tier
from src.models import Tier


def _collect_files() -> list[Path]:
    files: list[Path] = []
    for directory in CLINICAL_DIRS + PEER_DIRS:
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                files.append(path)
    return files


def _read_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return read_pdf(path)
    if path.suffix.lower() == ".md":
        return read_markdown(path)
    return ""


def run_ingest(output: Path | None = None) -> dict[str, int]:
    """Read docs/references + user-queries, tag tier, write chunks.jsonl."""
    out = output or CHUNKS_FILE
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    stats = {"clinical": 0, "peer": 0, "skipped": 0, "files": 0}
    all_chunks = []

    for path in _collect_files():
        tier = resolve_tier(path)
        if tier is None:
            stats["skipped"] += 1
            continue

        try:
            text = _read_file(path)
        except Exception as exc:
            print(f"  skip (read error): {path.name} — {exc}")
            stats["skipped"] += 1
            continue

        if not text.strip():
            print(f"  skip (empty): {path.name}")
            stats["skipped"] += 1
            continue

        chunks = chunk_document(path, tier, text)
        all_chunks.extend(chunks)
        stats["files"] += 1
        stats[tier.value] += len(chunks)
        print(f"  {tier.value:8} {len(chunks):4} chunks  {path.relative_to(PROJECT_ROOT)}")

    with out.open("w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")

    stats["total"] = len(all_chunks)
    print(f"\nWrote {stats['total']} chunks → {out.relative_to(PROJECT_ROOT)}")
    return stats
