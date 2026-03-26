"""SOPHY embodied server scaffolding.

This module intentionally focuses on deterministic planning helpers that can be
used from unit tests without requiring a running Evennia/Django stack.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from evennia.game_template.world.timeline import iso_z_from_utc, utc_room_key


@dataclass(frozen=True, slots=True)
class TimelineCoordinate:
    """Normalized timeline-space coordinates for one memory event."""

    x: int
    y: float
    z: int
    t: int


@dataclass(frozen=True, slots=True)
class MemoryNode:
    """One memory artifact projected into timeline-space."""

    event_id: str
    room_key: str
    iso_alias: str
    coordinate: TimelineCoordinate
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DeploymentPhase:
    """Represents one implementation phase in project rollout."""

    phase_id: str
    description: str


DEFAULT_DEPLOYMENT_PHASES: tuple[DeploymentPhase, ...] = (
    DeploymentPhase("PHASE_1", "Server & Evennia Installation"),
    DeploymentPhase("PHASE_2", "MUD Core Mechanics & AI Admin Integration"),
    DeploymentPhase("PHASE_3", "Timeline-Based World Structure Implementation"),
    DeploymentPhase("PHASE_4", "AI Memory Optimization & Vector Search Tuning"),
    DeploymentPhase("PHASE_5", "Full System Testing & Failover Scenarios"),
)


def create_memory_node(
    *,
    event_id: str,
    utc_seconds: int,
    importance_weight: float,
    recurrence: int,
    interaction_count: int,
    metadata: dict[str, Any] | None = None,
) -> MemoryNode:
    """Create a normalized memory node from temporal and relevance inputs.

    Args:
        event_id: Stable identifier for the event.
        utc_seconds: Event timestamp in UTC epoch seconds.
        importance_weight: Importance score between 0.0 and 1.0.
        recurrence: Topic recurrence count.
        interaction_count: Number of cross-thread/user interactions.
        metadata: Optional event payload metadata.

    Raises:
        ValueError: If provided values are out of expected ranges.
    """
    if not event_id.strip():
        raise ValueError("event_id must be a non-empty string")
    if not 0.0 <= importance_weight <= 1.0:
        raise ValueError("importance_weight must be between 0.0 and 1.0")
    if recurrence < 0:
        raise ValueError("recurrence must be >= 0")
    if interaction_count < 0:
        raise ValueError("interaction_count must be >= 0")

    # Dev Agent Breadcrumb: deterministic normalization checkpoint.
    coordinate = TimelineCoordinate(
        x=int(utc_seconds),
        y=round(float(importance_weight), 4),
        z=int(recurrence),
        t=int(interaction_count),
    )
    safe_metadata = dict(metadata or {})

    return MemoryNode(
        event_id=event_id,
        room_key=utc_room_key(utc_seconds),
        iso_alias=iso_z_from_utc(utc_seconds),
        coordinate=coordinate,
        metadata=safe_metadata,
    )


def summarize_vector_backends() -> tuple[str, ...]:
    """Return supported vector memory backend labels for initial planning."""
    return ("faiss", "pinecone", "postgresql+pgvector")


def phase_status_snapshot(
    completed_phase_ids: set[str] | None = None,
) -> list[dict[str, str]]:
    """Build a human-readable status view for rollout phases."""
    completed = completed_phase_ids or set()
    snapshot = []
    for phase in DEFAULT_DEPLOYMENT_PHASES:
        state = "completed" if phase.phase_id in completed else "pending"
        snapshot.append(
            {
                "phase_id": phase.phase_id,
                "description": phase.description,
                "state": state,
            }
        )
    return snapshot


def utc_now_room_key(now: datetime | None = None) -> str:
    """Return canonical room key for current UTC second."""
    moment = now or datetime.now(timezone.utc)
    return utc_room_key(int(moment.timestamp()))
