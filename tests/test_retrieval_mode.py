"""Retrieval mode resolution without building a vector index."""

from unittest.mock import patch

from src.retrieval.store import resolve_retrieval_mode


def test_resolve_auto_keyword_when_no_index(monkeypatch):
    monkeypatch.delenv("RETRIEVAL", raising=False)
    with patch("src.retrieval.store.vector_index_ready", return_value=False):
        assert resolve_retrieval_mode() == "keyword"


def test_resolve_auto_vector_when_index_exists(monkeypatch):
    monkeypatch.delenv("RETRIEVAL", raising=False)
    with patch("src.retrieval.store.vector_index_ready", return_value=True):
        assert resolve_retrieval_mode() == "vector"


def test_resolve_forced_keyword(monkeypatch):
    monkeypatch.setenv("RETRIEVAL", "keyword")
    with patch("src.retrieval.store.vector_index_ready", return_value=True):
        assert resolve_retrieval_mode() == "keyword"


def test_resolve_invalid_env_falls_back_to_auto(monkeypatch):
    monkeypatch.setenv("RETRIEVAL", "invalid")
    with patch("src.retrieval.store.vector_index_ready", return_value=False):
        assert resolve_retrieval_mode() == "keyword"
