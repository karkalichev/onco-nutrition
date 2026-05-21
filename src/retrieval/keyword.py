"""Keyword overlap retrieval (MVP fallback)."""

import json
import re
from pathlib import Path

from src.config import CHUNKS_FILE
from src.i18n import Locale
from src.models import Chunk, Tier
from src.retrieval.parallel import retrieve_dual_tier


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[\w\u0400-\u04FF]+", text.lower())
    return {w for w in words if len(w) > 2}


def _score(query_tokens: set[str], chunk: Chunk, locale: Locale | None = None) -> float:
    text_tokens = _tokenize(chunk.text)
    if not query_tokens or not text_tokens:
        return 0.0
    overlap = len(query_tokens & text_tokens)
    score = overlap / len(query_tokens)
    if locale and chunk.language == locale:
        score *= 1.25
    elif locale and chunk.language not in (locale, "unknown"):
        score *= 0.85
    return score


class KeywordRetriever:
    def __init__(self, chunks_path: Path | None = None):
        self.chunks_path = chunks_path or CHUNKS_FILE
        self.chunks: list[Chunk] = []
        if self.chunks_path.exists():
            self.load()

    def load(self) -> None:
        self.chunks = []
        with self.chunks_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    self.chunks.append(Chunk.from_dict(json.loads(line)))

    def search(self, query: str, tier: Tier, top_k: int, locale: Locale | None = None) -> list[Chunk]:
        tokens = _tokenize(query)
        scored = [(c, _score(tokens, c, locale)) for c in self.chunks if c.tier == tier]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [c for c, s in scored if s > 0][:top_k]

    def retrieve(self, query: str, locale: Locale | None = None) -> tuple[list[Chunk], list[Chunk]]:
        return retrieve_dual_tier(self.search, query, locale)
