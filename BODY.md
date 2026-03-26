# BODY.md

## Core Runtime Anatomy (TIME game-template surface)

### Timeline and World Memory Primitives
- `evennia/game_template/world/timeline.py`
  - canonical UTC key parsing/rendering
  - monthly anchor generation and chronological validation
- `evennia/game_template/world/sophy_embodied.py`
  - timeline coordinate and memory-node dataclasses
  - phase snapshots and UTC-now room routing

### Vector Memory Integration (Custom Layer)
- `evennia/game_template/world/pgvector_memory.py`
  - safe identifier validation
  - extension/table/index SQL generation
  - deterministic upsert/search payload builders
- `evennia/game_template/world/README_pgvector_integration.md`
  - phased rollout playbook and known gotchas

### Architecture/Deployment Control Plane
- `evennia/game_template/world/sophy_config.py`
  - architecture config normalization
  - backend support checks
  - deployment readiness gates and findings summaries

### Existing Template Foundations
- `evennia/game_template/typeclasses/*.py`
  - object/account/room/exit/character defaults and breadcrumb hooks
- `evennia/game_template/commands/command.py`
  - command execution breadcrumbing

## Testing Surface
- `evennia/game_template/tests/test_template_core.py`
- `evennia/game_template/tests/test_timeline.py`
- `evennia/game_template/tests/test_sophy_embodied.py`
- `evennia/game_template/tests/test_pgvector_memory.py`
- `evennia/game_template/tests/test_sophy_config.py`

## Structural Principle
TIME-specific functionality should remain modular and easy to lift/rebase
without entangling upstream Evennia core files.
