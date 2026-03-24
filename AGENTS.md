# AGENTS.md

## Scope
This file applies to the full repository tree.

## Dev Agent Breadcrumb Standard
- When filling template placeholders, prefer lightweight logging or non-persistent breadcrumbs over silent `pass` blocks.
- Use the phrase `Dev Agent Breadcrumb` in comments or log messages where control flow checkpoints are intentionally added.
- Keep breadcrumbs safe-by-default (no secrets, no tokens, no personal data).

## PEP 8 and Testing Expectations
- Favor PEP 8-compliant line lengths, naming, and spacing in modified files.
- Add or update focused tests when behavior changes.
- Prefer small, deterministic unit tests over heavy integration setup in template-level code.
