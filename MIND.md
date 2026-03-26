# MIND.md

## Purpose
TIME's "mind" is the planning and recall layer that turns events into
navigable timeline knowledge.

Current implementation direction in the game template:
- timeline helpers normalize canonical UTC room keys and anchors;
- SOPHY embodied helpers map events into timeline dimensions (`x/y/z/t`);
- pgvector helpers produce deterministic SQL/payloads for persistent memory;
- RAG helpers build ranked memory context and augmented prompts for LLM use;
- architecture config helpers normalize deployment intent into typed readiness
  gates and implementation findings.

## Reasoning Model
1. **Normalize inputs first** (identifiers, dimensions, architecture fields).
2. **Generate deterministic artifacts** (room keys, SQL snippets, payloads).
3. **Validate safety assumptions** (supported backends, phase readiness,
   sandbox/rollback cautions).
4. **Expose the path** through small, testable helper functions and lightweight
   Dev Agent Breadcrumb checkpoints.

## Near-Term Cognitive Priorities
- Wire pgvector helpers into a game-template service boundary.
- Add memory retrieval orchestration that combines temporal and semantic ranks.
- Keep read/write contracts explicit so migrations stay predictable.

## Debugging Notes
- Prefer inspectable pure functions over hidden side effects.
- Keep traces non-persistent by default unless audit persistence is intentional.
