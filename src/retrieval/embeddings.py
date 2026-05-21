"""Multilingual embedding model for vector retrieval."""

from functools import lru_cache
from typing import Any

from src.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embeddings() -> Any:
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
