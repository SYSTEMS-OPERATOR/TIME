"""Config normalization for the SOPHY Embodied Evennia Server blueprint.

The helpers in this module convert the large architecture dictionary into a
stable, testable representation that follow-on runtime code can consume.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SUPPORTED_VECTOR_BACKENDS = frozenset(
    {
        "faiss",
        "pinecone",
        "postgresql with pgvector",
        "postgresql+pgvector",
    }
)


@dataclass(frozen=True, slots=True)
class DeploymentGate:
    """One deployment phase gate with readiness state."""

    phase_id: str
    description: str
    ready: bool
    notes: str


@dataclass(frozen=True, slots=True)
class SophyArchitectureConfig:
    """Normalized subset of the SOPHY architecture specification."""

    project_name: str
    description: str
    os_environment: str
    core_framework: str
    vector_databases: tuple[str, ...]
    model_integrations: tuple[str, ...]
    deployment_phases: tuple[tuple[str, str], ...]
    allows_root_level_ai_control: bool


def _normalize_sequence(values: Any) -> tuple[str, ...]:
    """Normalize configuration list values to lowercase string tuples."""
    if not isinstance(values, list):
        return tuple()
    return tuple(str(value).strip() for value in values if str(value).strip())


def normalize_architecture_config(raw_config: dict[str, Any]) -> SophyArchitectureConfig:
    """Normalize raw project config into strongly typed architecture data."""
    architecture = raw_config.get("ARCHITECTURE", {})
    ai_pipeline = architecture.get("AI_PIPELINE", {})
    testing = architecture.get("TESTING & DEPLOYMENT", {})
    admin = architecture.get("ADMIN CONTROL & SELF-MANAGEMENT", {})

    deployment_phases: list[tuple[str, str]] = []
    for phase_id in sorted(testing):
        deployment_phases.append((phase_id, str(testing[phase_id]).strip()))

    return SophyArchitectureConfig(
        project_name=str(raw_config.get("PROJECT_NAME", "")).strip(),
        description=str(raw_config.get("DESCRIPTION", "")).strip(),
        os_environment=str(architecture.get("OS_ENVIRONMENT", "")).strip(),
        core_framework=str(architecture.get("CORE_FRAMEWORK", "")).strip(),
        vector_databases=_normalize_sequence(ai_pipeline.get("VECTOR_DATABASE", [])),
        model_integrations=_normalize_sequence(
            ai_pipeline.get("MODEL_INTEGRATION", [])
        ),
        deployment_phases=tuple(deployment_phases),
        allows_root_level_ai_control="ROOT-LEVEL ACCESS" in admin,
    )


def validate_vector_backends(config: SophyArchitectureConfig) -> list[str]:
    """Return unsupported vector backend entries from configuration."""
    unsupported = []
    for backend in config.vector_databases:
        backend_key = backend.lower()
        if backend_key not in SUPPORTED_VECTOR_BACKENDS:
            unsupported.append(backend)
    return unsupported


def deployment_readiness_gates(
    config: SophyArchitectureConfig,
    completed_phases: set[str] | None = None,
) -> list[DeploymentGate]:
    """Generate a deterministic readiness report across rollout phases.

    The root-level AI control mode is surfaced as a caution note so operators
    can explicitly validate sandboxing and audit controls before phase unlocks.
    """
    completed = completed_phases or set()
    gates: list[DeploymentGate] = []

    for phase_id, description in config.deployment_phases:
        ready = phase_id in completed
        notes = "pending completion evidence"
        if ready:
            notes = "phase evidence provided"

        if config.allows_root_level_ai_control:
            # Dev Agent Breadcrumb: Security caution surfaced at each gate.
            notes = f"{notes}; verify sandbox + rollback controls"

        gates.append(
            DeploymentGate(
                phase_id=phase_id,
                description=description,
                ready=ready,
                notes=notes,
            )
        )
    return gates


def summarize_config_findings(raw_config: dict[str, Any]) -> dict[str, Any]:
    """Return actionable findings for advancing implementation safely."""
    config = normalize_architecture_config(raw_config)
    unsupported_backends = validate_vector_backends(config)

    findings = {
        "project_name": config.project_name,
        "phase_count": len(config.deployment_phases),
        "unsupported_vector_backends": unsupported_backends,
        "has_pgvector_backend": any(
            "pgvector" in backend.lower() for backend in config.vector_databases
        ),
        "requires_security_review": config.allows_root_level_ai_control,
    }
    return findings
