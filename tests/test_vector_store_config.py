"""Vector store env selection."""

from src.config import VECTOR_STORE_CHROMA, VECTOR_STORE_PGVECTOR, get_vector_store


def test_get_vector_store_default_chroma(monkeypatch):
    monkeypatch.delenv("VECTOR_STORE", raising=False)
    assert get_vector_store() == VECTOR_STORE_CHROMA


def test_get_vector_store_pgvector(monkeypatch):
    monkeypatch.setenv("VECTOR_STORE", "pgvector")
    assert get_vector_store() == VECTOR_STORE_PGVECTOR


def test_get_vector_store_invalid_falls_back_to_chroma(monkeypatch):
    monkeypatch.setenv("VECTOR_STORE", "weaviate")
    assert get_vector_store() == VECTOR_STORE_CHROMA
