# SOUL.md

## Design Intent
TIME is about memory as place and history as something players can explore.
The project should feel coherent, inspectable, and resilient as it grows from
prototype to embodied timeline server.

## Project Spirit
- **Now**: build practical foundations that run and test cleanly.
- **Forever**: prefer designs that survive upgrades and handoffs.
- **Always**: keep humans in the loop with transparent logic and audit trails.

## Engineering Values
- Determinism before cleverness.
- Safety before autonomy.
- Explicit contracts before implicit coupling.
- Small composable modules before monoliths.

## AI Governance Posture
SOPHY can be ambitious without becoming opaque:
- keep operational control bounded by sandbox and rollback expectations;
- treat self-modifying capabilities as gated features with strong observability;
- document intent and continuation points so future developers can reason about
  behavior quickly.

## Builder Experience
A new developer should be able to open the game-template layer and understand:
1. what exists,
2. why it exists,
3. how to extend it safely.
