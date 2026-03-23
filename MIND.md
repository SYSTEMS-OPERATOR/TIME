# MIND.md

## Purpose
TIME-EVE now has a small, explicit reasoning layer in the game template:
- object and account lifecycle hooks initialize sensible defaults;
- developer breadcrumbs capture recent logic flow in memory;
- commands write lightweight execution traces to the active caller when possible.

## Logic Flow
1. **Accounts** initialize a default profile tagline and record login lifecycle breadcrumbs.
2. **Commands** record invocation breadcrumbs before command execution.
3. **Objects / Rooms / Characters / Exits** record creation, movement, traversal, and display breadcrumbs.
4. **Channels / Scripts** use safer defaults so template behavior is useful before heavy customization.

## Debugging Note
Breadcrumbs are stored on `ndb.dev_breadcrumbs`, so they are intentionally non-persistent and safe for development.
