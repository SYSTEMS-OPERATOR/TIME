"""Retrieval-Augmented Generation (RAG) helpers for TIME/SOPHY.

This module intentionally focuses on deterministic prompt-construction and
retrieval-shaping logic. Runtime DB/LLM clients should call these helpers
rather than re-implementing ranking or context assembly inline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .pgvector_memory import (
    PgvectorMemoryConfig,
    build_search_payload,
    search_memory_sql,
)


@dataclass(frozen=True, slots=True)
class RetrievedMemory:
    """One recalled memory candidate returned by vector search.

    Attributes:
        event_id: Stable event identifier in memory storage.
        text: Human-readable memory text to place into RAG context.
        relevance_score: Similarity-derived score in the ``0..1`` range.
        utc_seconds: UTC timestamp used for timeline ordering.
        metadata: Optional additional machine-readable memory details.
    """

    event_id: str
    text: str
    relevance_score: float
    utc_seconds: int
    metadata: dict[str, Any] = field(default_factory=dict)


def normalize_relevance(score: float) -> float:
    """Clamp a relevance score into the inclusive ``0..1`` range."""
    return max(0.0, min(1.0, float(score)))


def rank_memories(
    memories: list[RetrievedMemory],
    *,
    max_results: int = 8,
    min_score: float = 0.2,
) -> list[RetrievedMemory]:
    """Filter and rank memory candidates for prompt injection.

    Ranking policy:
    1. Keep candidates with normalized relevance >= ``min_score``.
    2. Sort by relevance descending.
    3. Break ties by `utc_seconds` descending (newer memory first).
    """
    if max_results <= 0:
        raise ValueError("max_results must be > 0")

    filtered = [
        memory
        for memory in memories
        if normalize_relevance(memory.relevance_score) >= min_score
    ]
    ordered = sorted(
        filtered,
        key=lambda memory: (
            normalize_relevance(memory.relevance_score),
            int(memory.utc_seconds),
        ),
        reverse=True,
    )
    return ordered[:max_results]


def _format_utc(utc_seconds: int) -> str:
    """Format UTC seconds for compact context readability."""
    dt = datetime.fromtimestamp(int(utc_seconds), tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%SZ")


def build_rag_context(memories: list[RetrievedMemory], *, max_chars: int = 2400) -> str:
    """Build a compact, deterministic context block from ranked memories.

    Args:
        memories: Ranked memory rows (typically output of ``rank_memories``).
        max_chars: Maximum context character budget.

    Returns:
        A newline-delimited memory context block suitable for prompt injection.
    """
    if max_chars <= 0:
        raise ValueError("max_chars must be > 0")

    lines: list[str] = []
    used = 0

    for index, memory in enumerate(memories, start=1):
        line = (
            f"[{index}] {memory.event_id} @ {_format_utc(memory.utc_seconds)} "
            f"(score={normalize_relevance(memory.relevance_score):.3f}) "
            f"{memory.text.strip()}"
        )
        if used + len(line) + 1 > max_chars:
            break
        lines.append(line)
        used += len(line) + 1

    return "\n".join(lines)


def build_augmented_prompt(
    *,
    system_prompt: str,
    user_query: str,
    rag_context: str,
) -> str:
    """Compose a final LLM prompt with explicit RAG boundaries.

    The format is intentionally simple and provider-agnostic so the same
    prompt can be used for local and API-backed language models.
    """
    clean_system_prompt = system_prompt.strip()
    clean_user_query = user_query.strip()
    clean_context = rag_context.strip()

    if not clean_system_prompt:
        raise ValueError("system_prompt must be non-empty")
    if not clean_user_query:
        raise ValueError("user_query must be non-empty")

    context_block = clean_context if clean_context else "(no relevant memories found)"
    return (
        f"SYSTEM INSTRUCTIONS:\n{clean_system_prompt}\n\n"
        "RECALLED MEMORIES (RAG):\n"
        f"{context_block}\n\n"
        f"USER QUERY:\n{clean_user_query}\n\n"
        "ASSISTANT RESPONSE:"
    )


def prepare_recall_query(
    *,
    config: PgvectorMemoryConfig,
    query_embedding: list[float],
    top_k: int,
    min_importance_weight: float | None = None,
) -> tuple[str, tuple[Any, ...]]:
    """Return SQL + payload tuple for a pgvector recall request.

    This wrapper keeps SQL string construction and payload ordering aligned,
    reducing common integration bugs during DB wiring.
    """
    sql = search_memory_sql(
        config,
        top_k=top_k,
        min_importance_weight=min_importance_weight,
    )

    # Dev Agent Breadcrumb: query/payload coupling checkpoint.
    payload = build_search_payload(
        query_embedding=query_embedding,
        top_k=top_k,
        config=config,
        min_importance_weight=min_importance_weight,
    )
    return sql, payload
