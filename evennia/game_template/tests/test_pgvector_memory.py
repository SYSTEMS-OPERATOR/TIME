"""Unit tests for pgvector integration helpers."""

from __future__ import annotations

import unittest

from evennia.game_template.world.pgvector_memory import (
    PgvectorMemoryConfig,
    build_search_payload,
    build_upsert_payload,
    create_memory_table_sql,
    create_similarity_index_sql,
    embedding_to_pgvector_literal,
    ensure_dimensions,
    extension_sql,
    sanitize_identifier,
    search_memory_sql,
    upsert_memory_sql,
)


class PgvectorMemoryTests(unittest.TestCase):
    """Validate deterministic SQL and payload generation helpers."""

    def test_extension_sql(self):
        self.assertEqual(extension_sql(), "CREATE EXTENSION IF NOT EXISTS vector;")

    def test_create_memory_table_sql_contains_vector_dimension(self):
        sql = create_memory_table_sql(PgvectorMemoryConfig(embedding_dimensions=384))

        self.assertIn("embedding vector(384) NOT NULL", sql)
        self.assertIn("public.sophy_memory_nodes", sql)

    def test_similarity_index_sql(self):
        sql = create_similarity_index_sql(PgvectorMemoryConfig(table_name="memory"))

        self.assertIn("CREATE INDEX IF NOT EXISTS memory_embedding_hnsw_idx", sql)
        self.assertIn("USING hnsw", sql)

    def test_upsert_sql_targets_event_id_conflict(self):
        sql = upsert_memory_sql(PgvectorMemoryConfig())

        self.assertIn("ON CONFLICT (event_id)", sql)
        self.assertIn("embedding = EXCLUDED.embedding", sql)

    def test_search_memory_sql_with_threshold(self):
        sql = search_memory_sql(
            PgvectorMemoryConfig(),
            top_k=8,
            min_importance_weight=0.5,
        )

        self.assertIn("WHERE importance_weight >= %s", sql)
        self.assertIn("ORDER BY embedding <=> %s::vector", sql)

    def test_search_memory_sql_without_threshold(self):
        sql = search_memory_sql(PgvectorMemoryConfig(), top_k=8)

        self.assertNotIn("WHERE importance_weight", sql)
        self.assertIn("LIMIT %s", sql)

    def test_embedding_literal_formatter(self):
        self.assertEqual(
            embedding_to_pgvector_literal([0.1, 1.25, 2.0]),
            "[0.1,1.25,2]",
        )

    def test_build_upsert_payload_validates_dimensions(self):
        with self.assertRaises(ValueError):
            build_upsert_payload(
                event_id="evt",
                room_key="UTC:10",
                utc_seconds=10,
                importance_weight=0.2,
                recurrence=1,
                interaction_count=0,
                metadata={},
                embedding=[0.1],
                config=PgvectorMemoryConfig(embedding_dimensions=2),
            )

    def test_build_upsert_payload_builds_expected_tuple(self):
        payload = build_upsert_payload(
            event_id="evt",
            room_key="UTC:10",
            utc_seconds=10,
            importance_weight=0.2,
            recurrence=1,
            interaction_count=0,
            metadata={"topic": "intro"},
            embedding=[0.1, 0.2],
            config=PgvectorMemoryConfig(embedding_dimensions=2),
        )

        self.assertEqual(payload[0], "evt")
        self.assertEqual(payload[7], "[0.1,0.2]")

    def test_build_search_payload_with_optional_threshold(self):
        payload = build_search_payload(
            query_embedding=[0.1, 0.2],
            top_k=5,
            config=PgvectorMemoryConfig(embedding_dimensions=2),
            min_importance_weight=0.4,
        )

        self.assertEqual(payload, ("[0.1,0.2]", 0.4, "[0.1,0.2]", 5))

    def test_build_search_payload_without_optional_threshold(self):
        payload = build_search_payload(
            query_embedding=[0.1, 0.2],
            top_k=5,
            config=PgvectorMemoryConfig(embedding_dimensions=2),
        )

        self.assertEqual(payload, ("[0.1,0.2]", "[0.1,0.2]", 5))

    def test_identifier_validation(self):
        self.assertEqual(sanitize_identifier("valid_name_1"), "valid_name_1")
        with self.assertRaises(ValueError):
            sanitize_identifier("invalid-name")

    def test_ensure_dimensions(self):
        ensure_dimensions([0.1, 0.2], 2)
        with self.assertRaises(ValueError):
            ensure_dimensions([0.1], 2)


if __name__ == "__main__":
    unittest.main()
