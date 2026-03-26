"""Tests for SOPHY architecture config normalization helpers."""

from __future__ import annotations

import unittest

from evennia.game_template.world.sophy_config import (
    deployment_readiness_gates,
    normalize_architecture_config,
    summarize_config_findings,
    validate_vector_backends,
)


SAMPLE_CONFIG = {
    "PROJECT_NAME": "SOPHY Embodied Evennia Server",
    "DESCRIPTION": "AI-driven Evennia-based MUD server",
    "ARCHITECTURE": {
        "OS_ENVIRONMENT": "Ubuntu Server (Minimal Deployment)",
        "CORE_FRAMEWORK": "Evennia MUD Framework",
        "AI_PIPELINE": {
            "VECTOR_DATABASE": ["FAISS", "Pinecone", "PostgreSQL with pgvector"],
            "MODEL_INTEGRATION": ["Local LLM", "External API"],
        },
        "ADMIN CONTROL & SELF-MANAGEMENT": {
            "ROOT-LEVEL ACCESS": "AI has administrative privileges",
        },
        "TESTING & DEPLOYMENT": {
            "PHASE_1": "Server & Evennia Installation",
            "PHASE_2": "MUD Core Mechanics & AI Admin Integration",
        },
    },
}


class SophyConfigTests(unittest.TestCase):
    """Validate config parsing and readiness gate output."""

    def test_normalize_architecture_config(self):
        config = normalize_architecture_config(SAMPLE_CONFIG)

        self.assertEqual(config.project_name, "SOPHY Embodied Evennia Server")
        self.assertEqual(config.vector_databases[0], "FAISS")
        self.assertEqual(len(config.deployment_phases), 2)
        self.assertTrue(config.allows_root_level_ai_control)

    def test_validate_vector_backends(self):
        config = normalize_architecture_config(
            {
                **SAMPLE_CONFIG,
                "ARCHITECTURE": {
                    **SAMPLE_CONFIG["ARCHITECTURE"],
                    "AI_PIPELINE": {
                        "VECTOR_DATABASE": ["FAISS", "UnknownDB"],
                        "MODEL_INTEGRATION": ["Local LLM"],
                    },
                },
            }
        )

        self.assertEqual(validate_vector_backends(config), ["UnknownDB"])

    def test_deployment_readiness_gates(self):
        config = normalize_architecture_config(SAMPLE_CONFIG)

        gates = deployment_readiness_gates(config, {"PHASE_1"})

        self.assertEqual(gates[0].phase_id, "PHASE_1")
        self.assertTrue(gates[0].ready)
        self.assertIn("sandbox + rollback controls", gates[0].notes)
        self.assertFalse(gates[1].ready)

    def test_summarize_config_findings(self):
        findings = summarize_config_findings(SAMPLE_CONFIG)

        self.assertEqual(findings["phase_count"], 2)
        self.assertTrue(findings["has_pgvector_backend"])
        self.assertTrue(findings["requires_security_review"])


if __name__ == "__main__":
    unittest.main()
