# SOPHY pgvector Integration Plan (Game Template Customization)

This document tracks the **custom** PostgreSQL + pgvector implementation path for
SOPHY memory storage. The code lives in `world/pgvector_memory.py` so the
integration remains isolated from Evennia core modules.

## Why this separation exists

- Keeps upstream Evennia upgrades easier by avoiding core-file edits.
- Makes SQL generation deterministic and unit-testable without a running DB.
- Documents handoff points for future Dev Agents.

## Phase-by-phase plan (tried-and-true sequence)

1. **Environment readiness**
   - Use PostgreSQL 15+ (or distribution-supported version with pgvector).
   - Install pgvector extension package at OS level.
   - Ensure DB role used by Evennia can run `CREATE EXTENSION vector`.

2. **Schema bootstrap**
   - Run DDL from helper outputs in this order:
     1. `extension_sql()`
     2. `create_memory_table_sql(config)`
     3. `create_similarity_index_sql(config)`
   - Verify index build succeeds before enabling production writes.

3. **Write path integration**
   - Convert embeddings to pgvector literal using
     `embedding_to_pgvector_literal(...)`.
   - Validate dimensions with `ensure_dimensions(...)`.
   - Execute `upsert_memory_sql(config)` with payload from
     `build_upsert_payload(...)`.

4. **Read path integration**
   - Use `search_memory_sql(config, top_k, min_importance_weight=...)` for
     similarity retrieval.
   - Bind query vector consistently to every `%s::vector` placeholder.

5. **Operational hardening**
   - Add migration/management command wrappers in game-specific modules only.
   - Add audit logging for upsert/search timings and failures.
   - Load-test retrieval latency and tune HNSW parameters if needed.

## Gotchas to avoid

- Do not pass user-controlled values into schema/table identifiers.
  `sanitize_identifier` exists to prevent SQL injection.
- Keep embedding dimensions stable per table. Changing dimensions requires a
  coordinated migration and index rebuild.
- The search SQL uses pgvector cosine distance; relevance is computed as
  `1 - distance`. Treat this as a heuristic score, not probability.
- If adding async jobs for embeddings later, preserve ordering guarantees for
  timeline events (`utc_seconds`, `room_key`) during writes.

## Current status

- ✅ Deterministic SQL/payload helper layer implemented.
- ✅ Unit tests added for helper correctness and validation behavior.
- ⏳ Runtime DB wiring into Evennia services is pending the next phase.
