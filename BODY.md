# BODY.md

## Core Runtime Pieces
- `evennia/game_template/typeclasses/objects.py`: shared object behavior, fallback descriptions, breadcrumb storage.
- `evennia/game_template/typeclasses/characters.py`: character possession breadcrumbs.
- `evennia/game_template/typeclasses/rooms.py`: room initialization breadcrumbs.
- `evennia/game_template/typeclasses/exits.py`: traversal breadcrumbs.
- `evennia/game_template/typeclasses/accounts.py`: account lifecycle defaults and breadcrumbs.
- `evennia/game_template/typeclasses/channels.py`: safer channel formatting defaults.
- `evennia/game_template/typeclasses/scripts.py`: persistent script defaults.
- `evennia/game_template/commands/command.py`: command invocation breadcrumbs.

## Testing Surface
- `evennia/game_template/tests/test_template_core.py` tests the breadcrumb helpers and the new fallback behaviors in isolation.
