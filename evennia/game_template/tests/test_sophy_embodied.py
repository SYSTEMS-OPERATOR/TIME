"""Tests for SOPHY embodied scaffolding helpers."""

from __future__ import annotations

from datetime import datetime, timezone
import unittest

from evennia.game_template.world.sophy_embodied import (
    DEFAULT_DEPLOYMENT_PHASES,
    create_memory_node,
    phase_status_snapshot,
    summarize_vector_backends,
    utc_now_room_key,
)


class SophyEmbodiedTests(unittest.TestCase):
    """Validate deterministic world-memory helper behavior."""

    def test_create_memory_node_maps_timeline_dimensions(self):
        node = create_memory_node(
            event_id="evt-1",
            utc_seconds=60,
            importance_weight=0.75,
            recurrence=3,
            interaction_count=5,
            metadata={"topic": "greeting"},
        )

        self.assertEqual(node.room_key, "UTC:60")
        self.assertEqual(node.iso_alias, "1970-01-01T00:01:00Z")
        self.assertEqual(node.coordinate.x, 60)
        self.assertEqual(node.coordinate.y, 0.75)
        self.assertEqual(node.coordinate.z, 3)
        self.assertEqual(node.coordinate.t, 5)
        self.assertEqual(node.metadata["topic"], "greeting")

    def test_create_memory_node_validates_ranges(self):
        with self.assertRaises(ValueError):
            create_memory_node(
                event_id="evt-2",
                utc_seconds=0,
                importance_weight=2,
                recurrence=0,
                interaction_count=0,
            )

    def test_vector_backend_summary(self):
        self.assertEqual(
            summarize_vector_backends(),
            ("faiss", "pinecone", "postgresql+pgvector"),
        )

    def test_phase_snapshot_marks_completed(self):
        snapshot = phase_status_snapshot({"PHASE_1", "PHASE_3"})
        by_phase = {entry["phase_id"]: entry["state"] for entry in snapshot}

        self.assertEqual(by_phase["PHASE_1"], "completed")
        self.assertEqual(by_phase["PHASE_3"], "completed")
        self.assertEqual(by_phase["PHASE_2"], "pending")
        self.assertEqual(len(snapshot), len(DEFAULT_DEPLOYMENT_PHASES))

    def test_utc_now_room_key_uses_supplied_datetime(self):
        now = datetime(1970, 1, 1, 0, 2, 0, tzinfo=timezone.utc)

        self.assertEqual(utc_now_room_key(now), "UTC:120")


if __name__ == "__main__":
    unittest.main()
