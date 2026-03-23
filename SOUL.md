# SOUL.md

## Design Intent
TIME-EVE should feel understandable before it feels complex.

This repository ships a broad Evennia codebase, but the game-template layer is where a new builder first learns the project. The template should therefore:
- do something useful immediately;
- fail gracefully when unfinished;
- expose its own logic flow to the next developer.

## Developer Philosophy
- Prefer safe defaults over silent placeholders.
- Prefer lightweight observability over hidden magic.
- Prefer small, readable hooks that are easy to extend.
