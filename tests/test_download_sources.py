"""PDF manifest loading (no network)."""

from src.ingest.download_sources import load_pdf_manifest


def test_load_pdf_manifest_has_eight_entries():
    sources = load_pdf_manifest()
    assert len(sources) == 8
    assert all(s.url.startswith("https://") for s in sources)
    assert sources[0].filename.endswith(".pdf")
