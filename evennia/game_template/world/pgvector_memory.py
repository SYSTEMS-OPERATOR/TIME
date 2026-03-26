"""PostgreSQL + pgvector integration helpers for SOPHY memory storage.

This module is intentionally self-contained and framework-agnostic so we can
keep custom database integrations separate from Evennia core internals.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class PgvectorMemoryConfig:
    """Configuration required to build pgvector SQL snippets.

    Attributes:
        table_name: Name of the memory table.
        embedding_dimensions: Length of each embedding vector.
        schema_name: Optional database schema; defaults to ``public``.
    """

    table_name: str = "sophy_memory_nodes"
    embedding_dimensions: int = 1536
    schema_name: str = "public"

    def qualified_table_name(self) -> str:
        """Return ``schema.table`` after strict identifier validation."""
        return (
            f"{sanitize_identifier(self.schema_name)}."
            f"{sanitize_identifier(self.table_name)}"
        )


def sanitize_identifier(identifier: str) -> str:
    """Validate SQL identifiers and return a safe value.

    The helper only accepts unquoted identifiers to avoid SQL injection in the
    schema/table locations where parameter binding is unavailable.
    """
    if not isinstance(identifier, str) or not _IDENTIFIER_PATTERN.match(identifier):
        raise ValueError(f"Invalid SQL identifier: {identifier!r}")
    return identifier


def ensure_dimensions(embedding: list[float], expected_dimensions: int) -> None:
    """Validate that an embedding has the expected vector dimensions."""
    if len(embedding) != expected_dimensions:
        raise ValueError(
            "Embedding dimension mismatch: "
            f"expected {expected_dimensions}, got {len(embedding)}"
        )


def embedding_to_pgvector_literal(embedding: list[float]) -> str:
    """Encode a Python float list to pgvector literal syntax.

    Example output: ``[0.1,0.2,0.3]``.
    """
    # Dev Agent Breadcrumb: Literal serialization checkpoint for DB writes.
    return "[" + ",".join(f"{float(value):.10g}" for value in embedding) + "]"


def extension_sql() -> str:
    """Return SQL that enables pgvector extension idempotently."""
    return "CREATE EXTENSION IF NOT EXISTS vector;"


def create_memory_table_sql(config: PgvectorMemoryConfig) -> str:
    """Return DDL for the memory storage table used by SOPHY."""
    if config.embedding_dimensions <= 0:
        raise ValueError("embedding_dimensions must be > 0")

    table_name = config.qualified_table_name()

    return (
        f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        "    id BIGSERIAL PRIMARY KEY,\n"
        "    event_id TEXT UNIQUE NOT NULL,\n"
        "    room_key TEXT NOT NULL,\n"
        "    utc_seconds BIGINT NOT NULL,\n"
        "    importance_weight DOUBLE PRECISION NOT NULL,\n"
        "    recurrence INTEGER NOT NULL DEFAULT 0,\n"
        "    interaction_count INTEGER NOT NULL DEFAULT 0,\n"
        "    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,\n"
        f"    embedding vector({config.embedding_dimensions}) NOT NULL,\n"
        "    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),\n"
        "    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()\n"
        ");"
    )


def create_similarity_index_sql(config: PgvectorMemoryConfig) -> str:
    """Return HNSW cosine index SQL for embedding similarity search."""
    table_name = config.qualified_table_name()
    index_name = sanitize_identifier(f"{config.table_name}_embedding_hnsw_idx")

    return (
        f"CREATE INDEX IF NOT EXISTS {index_name} "
        f"ON {table_name} USING hnsw (embedding vector_cosine_ops);"
    )


def upsert_memory_sql(config: PgvectorMemoryConfig) -> str:
    """Return upsert SQL for inserting/updating vectorized memory nodes.

    Parameter order:
        1 event_id
        2 room_key
        3 utc_seconds
        4 importance_weight
        5 recurrence
        6 interaction_count
        7 metadata (JSON-compatible object)
        8 embedding literal in ``[0,1,...]`` form
    """
    table_name = config.qualified_table_name()

    return (
        f"INSERT INTO {table_name} ("
        "event_id, room_key, utc_seconds, importance_weight, "
        "recurrence, interaction_count, metadata, embedding"
        ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector) "
        "ON CONFLICT (event_id) DO UPDATE SET "
        "room_key = EXCLUDED.room_key, "
        "utc_seconds = EXCLUDED.utc_seconds, "
        "importance_weight = EXCLUDED.importance_weight, "
        "recurrence = EXCLUDED.recurrence, "
        "interaction_count = EXCLUDED.interaction_count, "
        "metadata = EXCLUDED.metadata, "
        "embedding = EXCLUDED.embedding, "
        "updated_at = NOW();"
    )


def search_memory_sql(
    config: PgvectorMemoryConfig,
    top_k: int,
    min_importance_weight: float | None = None,
) -> str:
    """Return similarity search SQL for retrieval-augmented memory recall.

    Parameter order:
        1 query embedding literal in ``[0,1,...]`` form (SELECT score)
        2 min_importance_weight (optional)
        3 query embedding literal in ``[0,1,...]`` form (ORDER BY)
        4 top_k
    """
    if top_k <= 0:
        raise ValueError("top_k must be > 0")

    table_name = config.qualified_table_name()
    where_clause = ""
    if min_importance_weight is not None:
        where_clause = "WHERE importance_weight >= %s "

    return (
        "SELECT event_id, room_key, utc_seconds, importance_weight, "
        "recurrence, interaction_count, metadata, "
        "(1 - (embedding <=> %s::vector)) AS relevance_score "
        f"FROM {table_name} "
        f"{where_clause}"
        "ORDER BY embedding <=> %s::vector "
        "LIMIT %s;"
    )


def build_search_payload(
    *,
    query_embedding: list[float],
    top_k: int,
    config: PgvectorMemoryConfig,
    min_importance_weight: float | None = None,
) -> tuple[Any, ...]:
    """Build a validated parameter tuple for ``search_memory_sql``.

    The query embedding is repeated because the SQL calculates both a
    relevance score and an ORDER BY distance using separate placeholders.
    """
    if top_k <= 0:
        raise ValueError("top_k must be > 0")
    if min_importance_weight is not None and not 0.0 <= min_importance_weight <= 1.0:
        raise ValueError("min_importance_weight must be between 0.0 and 1.0")

    ensure_dimensions(query_embedding, config.embedding_dimensions)
    embedding_literal = embedding_to_pgvector_literal(query_embedding)

    # Dev Agent Breadcrumb: Search payload normalization checkpoint.
    if min_importance_weight is None:
        return (embedding_literal, embedding_literal, int(top_k))
    return (
        embedding_literal,
        float(min_importance_weight),
        embedding_literal,
        int(top_k),
    )


def build_upsert_payload(
    *,
    event_id: str,
    room_key: str,
    utc_seconds: int,
    importance_weight: float,
    recurrence: int,
    interaction_count: int,
    metadata: dict[str, Any],
    embedding: list[float],
    config: PgvectorMemoryConfig,
) -> tuple[Any, ...]:
    """Create a validated parameter tuple for ``upsert_memory_sql``."""
    if not event_id.strip():
        raise ValueError("event_id must be non-empty")
    if not room_key.strip():
        raise ValueError("room_key must be non-empty")
    if not 0.0 <= importance_weight <= 1.0:
        raise ValueError("importance_weight must be between 0.0 and 1.0")
    if recurrence < 0 or interaction_count < 0:
        raise ValueError("recurrence and interaction_count must be >= 0")

    ensure_dimensions(embedding, config.embedding_dimensions)

    return (
        event_id,
        room_key,
        int(utc_seconds),
        float(importance_weight),
        int(recurrence),
        int(interaction_count),
        dict(metadata),
        embedding_to_pgvector_literal(embedding),
    )
