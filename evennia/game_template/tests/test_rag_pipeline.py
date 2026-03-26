"""Unit tests for deterministic RAG helper behavior."""

from __future__ import annotations

import unittest

from evennia.game_template.world.pgvector_memory import PgvectorMemoryConfig
from evennia.game_template.world.rag_pipeline import (
    RetrievedMemory,
    build_augmented_prompt,
    build_rag_context,
    normalize_relevance,
    prepare_recall_query,
    rank_memories,
)


class RagPipelineTests(unittest.TestCase):
    """Validate ranking, context building, and SQL/payload preparation."""

    def test_normalize_relevance_clamps_bounds(self):
        self.assertEqual(normalize_relevance(-5), 0.0)
        self.assertEqual(normalize_relevance(5), 1.0)

    def test_rank_memories_filters_and_orders(self):
        memories = [
            RetrievedMemory("a", "old", 0.9, 10),
            RetrievedMemory("b", "low", 0.1, 20),
            RetrievedMemory("c", "new", 0.9, 30),
        ]

        ranked = rank_memories(memories, max_results=5, min_score=0.2)

        self.assertEqual([item.event_id for item in ranked], ["c", "a"])

    def test_build_rag_context_respects_budget(self):
        memories = [
            RetrievedMemory("evt-1", "alpha", 0.8, 0),
            RetrievedMemory("evt-2", "beta", 0.7, 1),
        ]

        context = build_rag_context(memories, max_chars=70)

        self.assertIn("evt-1", context)
        self.assertNotIn("evt-2", context)

    def test_build_augmented_prompt_includes_sections(self):
        prompt = build_augmented_prompt(
            system_prompt="Be concise.",
            user_query="What happened?",
            rag_context="[1] evt context",
        )

        self.assertIn("SYSTEM INSTRUCTIONS", prompt)
        self.assertIn("RECALLED MEMORIES (RAG)", prompt)
        self.assertIn("USER QUERY", prompt)

    def test_prepare_recall_query_shapes_sql_and_payload(self):
        sql, payload = prepare_recall_query(
            config=PgvectorMemoryConfig(embedding_dimensions=2),
            query_embedding=[0.2, 0.4],
            top_k=3,
            min_importance_weight=0.5,
        )

        self.assertIn("ORDER BY embedding <=> %s::vector", sql)
        self.assertEqual(payload, ("[0.2,0.4]", 0.5, "[0.2,0.4]", 3))


if __name__ == "__main__":
    unittest.main()
