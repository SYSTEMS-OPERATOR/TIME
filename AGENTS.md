# AGENTS.md

## Scope
This file applies to the full repository tree.

## Mission Context (TIME)
TIME is the timeline-forward SOPHY project on top of Evennia. Contributions
should favor deterministic primitives, testable helpers, and clean boundaries
between upstream Evennia core and TIME-specific customization modules.

## Dev Agent Breadcrumb Standard
- When filling template placeholders, prefer lightweight logging or
  non-persistent breadcrumbs over silent `pass` blocks.
- Use the phrase `Dev Agent Breadcrumb` in comments or log messages where
  control-flow checkpoints are intentionally added.
- Keep breadcrumbs safe-by-default (no secrets, no tokens, no personal data).
- Prefer breadcrumbs at integration boundaries (config normalization,
  SQL/payload building, and world-state transitions).

## PEP 8 and Testing Expectations
- Favor PEP 8-compliant line lengths, naming, spacing, and imports.
- Add or update focused tests whenever behavior changes.
- Prefer small deterministic unit tests over heavy integration setup in
  template-level code.
- For SQL helpers, test both success and validation/error paths.

## Upgrade-Safe Customization Policy
- Keep TIME-specific logic in `evennia/game_template/...` whenever possible.
- Avoid editing Evennia core paths unless strictly necessary.
- If core edits are unavoidable, add concise comments explaining why and what
  must be preserved during upstream merges.

## Security and Control Boundaries
- Treat any "root/admin AI control" language as an architecture goal requiring
  explicit safeguards, not a default runtime assumption.
- Preserve auditability, rollback intent, and sandbox-first behavior in new
  automation features.
