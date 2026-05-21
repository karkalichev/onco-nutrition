"""Download clinical PDFs from urls in docs/references/sources/pdfs.yaml."""

from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import yaml

from src.config import PROJECT_ROOT, SOURCES_DIR, SOURCES_PDF_MANIFEST

PDF_MANIFEST = SOURCES_PDF_MANIFEST
USER_AGENT = "onco-nutrition/1.0 (local research; +https://github.com)"


@dataclass(frozen=True)
class PdfSource:
    filename: str
    url: str
    language: str
    publisher: str
    note: str | None = None

    @property
    def path(self) -> Path:
        return SOURCES_DIR / self.filename


def load_pdf_manifest(manifest_path: Path | None = None) -> list[PdfSource]:
    path = manifest_path or PDF_MANIFEST
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path.relative_to(PROJECT_ROOT)}. See docs/references/sources/README.md"
        )
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    entries = data.get("pdfs") or []
    sources: list[PdfSource] = []
    for entry in entries:
        sources.append(
            PdfSource(
                filename=entry["filename"],
                url=entry["url"],
                language=entry.get("language", "unknown"),
                publisher=entry.get("publisher", ""),
                note=entry.get("note"),
            )
        )
    return sources


def _is_pdf_bytes(data: bytes) -> bool:
    return len(data) >= 4 and data[:4] == b"%PDF"


def download_pdf(source: PdfSource, *, force: bool = False, timeout: int = 120) -> Path:
    dest = source.path
    if dest.exists() and not force:
        print(f"  skip (exists): {dest.name}")
        return dest

    request = urllib.request.Request(source.url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code} for {source.url}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error for {source.url}: {exc.reason}") from exc

    if not _is_pdf_bytes(data):
        raise RuntimeError(
            f"Not a PDF from {source.url} (got {len(data)} bytes). "
            f"Try opening the link in a browser."
        )

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    print(f"  saved {dest.name} ({len(data) // 1024} KB)")
    return dest


def download_all_pdfs(
    *,
    force: bool = False,
    manifest_path: Path | None = None,
) -> dict[str, int]:
    """Download every PDF in the manifest. Continues on per-file errors."""
    sources = load_pdf_manifest(manifest_path)
    stats = {"ok": 0, "skipped": 0, "failed": 0}

    for source in sources:
        if source.path.exists() and not force:
            print(f"  skip (exists): {source.filename}")
            stats["skipped"] += 1
            continue
        try:
            download_pdf(source, force=force)
            stats["ok"] += 1
        except Exception as exc:
            stats["failed"] += 1
            print(f"  FAIL {source.filename}: {exc}")
            if source.note:
                print(f"       note: {source.note}")

    print(
        f"\nPDFs → {SOURCES_DIR.relative_to(PROJECT_ROOT)} "
        f"(ok={stats['ok']}, skipped={stats['skipped']}, failed={stats['failed']})"
    )
    return stats
