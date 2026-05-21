"""PostgreSQL + pgvector retrieval with dual-tier metadata filters."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterator

from src.config import DATABASE_URL, EMBEDDING_DIM, PGVECTOR_TABLE
from src.i18n import Locale
from src.models import Chunk, Tier
from src.retrieval.embeddings import get_embeddings
from src.retrieval.parallel import retrieve_dual_tier
from src.retrieval.vector import _language_boost, _rank_chunks

if TYPE_CHECKING:
    import psycopg


def _database_url() -> str | None:
    return os.getenv("DATABASE_URL") or DATABASE_URL


def ensure_vector_extension(conn: "psycopg.Connection") -> None:
    """Enable pgvector before register_vector() or DDL using vector(...)."""
    with conn.cursor() as cur:
        try:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        except Exception as exc:
            raise RuntimeError(
                "PostgreSQL pgvector extension is not available on this server. "
                "Use the pgvector image: docker compose up -d "
                "(see docker-compose.yml), or install pgvector on your Postgres instance."
            ) from exc
    conn.commit()


@contextmanager
def pg_connection() -> Iterator["psycopg.Connection"]:
    url = _database_url()
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Example: postgresql://onco:onco@localhost:5432/onco_nutrition"
        )
    import psycopg
    from pgvector.psycopg import register_vector

    with psycopg.connect(url) as conn:
        ensure_vector_extension(conn)
        register_vector(conn)
        yield conn


def ensure_pgvector_schema(conn: "psycopg.Connection") -> None:
    ensure_vector_extension(conn)
    with conn.cursor() as cur:
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {PGVECTOR_TABLE} (
                id TEXT PRIMARY KEY,
                tier TEXT NOT NULL,
                language TEXT NOT NULL,
                source_path TEXT NOT NULL,
                source_title TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding vector({EMBEDDING_DIM}) NOT NULL
            )
            """
        )
        cur.execute(
            f"""
            CREATE INDEX IF NOT EXISTS {PGVECTOR_TABLE}_tier_idx
            ON {PGVECTOR_TABLE} (tier)
            """
        )
        cur.execute(
            f"""
            CREATE INDEX IF NOT EXISTS {PGVECTOR_TABLE}_embedding_hnsw_idx
            ON {PGVECTOR_TABLE}
            USING hnsw (embedding vector_cosine_ops)
            """
        )
    conn.commit()


def pgvector_ready() -> bool:
    url = _database_url()
    if not url:
        return False
    try:
        import psycopg

        with psycopg.connect(url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                          AND table_name = %s
                    )
                    """,
                    (PGVECTOR_TABLE,),
                )
                if not cur.fetchone()[0]:
                    return False
                cur.execute(f"SELECT COUNT(*) FROM {PGVECTOR_TABLE}")
                return cur.fetchone()[0] > 0
    except Exception:
        return False


def reset_pgvector_index(conn: "psycopg.Connection") -> None:
    with conn.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {PGVECTOR_TABLE}")
    conn.commit()


def upsert_chunk_embeddings(
    conn: "psycopg.Connection",
    chunks: list[Chunk],
    embeddings: list[list[float]],
) -> None:
    from pgvector import Vector

    rows = [
        (
            chunk.id,
            chunk.tier.value,
            chunk.language,
            chunk.source_path,
            chunk.source_title,
            chunk.text,
            Vector(vec),
        )
        for chunk, vec in zip(chunks, embeddings)
    ]
    with conn.cursor() as cur:
        cur.executemany(
            f"""
            INSERT INTO {PGVECTOR_TABLE} (
                id, tier, language, source_path, source_title, content, embedding
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                tier = EXCLUDED.tier,
                language = EXCLUDED.language,
                source_path = EXCLUDED.source_path,
                source_title = EXCLUDED.source_title,
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding
            """,
            rows,
        )
    conn.commit()


class PgVectorRetriever:
    def __init__(self) -> None:
        self._embeddings = None

    @property
    def ready(self) -> bool:
        return pgvector_ready()

    def _get_embeddings(self):
        if self._embeddings is None:
            self._embeddings = get_embeddings()
        return self._embeddings

    def embed_query(self, query: str) -> list[float]:
        return self._get_embeddings().embed_query(query)

    def search_with_vector(
        self,
        query_vector: list[float],
        tier: Tier,
        top_k: int,
        locale: Locale | None = None,
    ) -> list[Chunk]:
        from pgvector import Vector

        fetch_k = max(top_k * 2, top_k + 2)
        with pg_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT id, tier, source_path, source_title, language, content,
                           embedding <=> %s AS distance
                    FROM {PGVECTOR_TABLE}
                    WHERE tier = %s
                    ORDER BY embedding <=> %s
                    LIMIT %s
                    """,
                    (Vector(query_vector), tier.value, Vector(query_vector), fetch_k),
                )
                rows = cur.fetchall()

        if not rows:
            return []

        scored: list[tuple[Chunk, float]] = []
        for row in rows:
            chunk = Chunk(
                id=row[0],
                tier=Tier(row[1]),
                source_path=row[2],
                source_title=row[3],
                language=row[4] or "unknown",
                text=row[5],
            )
            sim = 1.0 / (1.0 + float(row[6]))
            scored.append((chunk, _language_boost(sim, chunk.language, locale)))

        return _rank_chunks(scored, top_k)

    def search(
        self,
        query: str,
        tier: Tier,
        top_k: int,
        locale: Locale | None = None,
    ) -> list[Chunk]:
        return self.search_with_vector(self.embed_query(query), tier, top_k, locale)

    def retrieve(
        self, query: str, locale: Locale | None = None
    ) -> tuple[list[Chunk], list[Chunk]]:
        query_vector = self.embed_query(query)
        return retrieve_dual_tier(
            lambda _q, tier, top_k, loc: self.search_with_vector(
                query_vector, tier, top_k, loc
            ),
            query,
            locale,
        )
