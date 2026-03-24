# TIME-EVE

[![template-smoke](https://github.com/SYSTEMS-OPERATOR/TIME/actions/workflows/github_action_template_smoke.yml/badge.svg)](https://github.com/SYSTEMS-OPERATOR/TIME/actions/workflows/github_action_template_smoke.yml)

TIME-EVE is a **timeline-first world model built on Evennia**.

At its core, the project treats moments in time as addressable places. Instead of using rooms only as conventional locations, TIME-EVE establishes a **canonical temporal grid** in which each timeline node is represented by a room labeled by UTC seconds. The repo is therefore not just a generic Evennia fork; it is an Evennia-based foundation for building a navigable, extensible timeline world.

## What TIME-EVE is trying to do

The guiding idea in `docs/ops/setup.md` is simple and strict:

- **Canonical identity is integer UTC seconds**.
- Timeline rooms are labeled as `UTC:<unix_seconds>`.
- The same value is stored on the room as `room.db.utc`.
- Optional ISO-8601 aliases can be added for readability.
- Rooms are **not auto-created on teleport**; they are either pre-created as anchors or inserted by controlled logic.

This makes the timeline deterministic, searchable, and upgrade-safe.

## Timeline model

The current setup plan defines a practical starting structure:

1. Create **1,200 monthly anchor rooms** from January 1970 through December 2069.
2. Link them with `prev` and `next` exits.
3. Allow travel only to rooms that already exist.
4. Insert new event rooms deliberately, by rewiring neighboring exits rather than generating world state implicitly.

That means TIME-EVE is best understood as a **temporal navigation substrate** first, and a game/application layer second.

## Why this repo looks the way it does

This repository still contains the broad upstream Evennia engine, but TIME-EVE’s customization intent is concentrated in the project-facing surfaces rather than the whole engine at once.

The included design notes make that split clearer:

- `BODY.md` points to the concrete runtime hooks in the game-template layer.
- `MIND.md` describes a lightweight reasoning/observability layer built from developer breadcrumbs.
- `SOUL.md` states the philosophy: useful defaults, graceful failure, and readable extension points.

Together, those files suggest that TIME-EVE should remain understandable and inspectable while it evolves.

## Functional overview of the repository

```text
TIME-EVE/
├── README.md                     # project overview and orientation
├── BODY.md                       # concrete runtime touchpoints
├── MIND.md                       # reasoning / breadcrumb layer
├── SOUL.md                       # design philosophy
├── docs/
│   ├── ops/
│   │   └── setup.md              # timeline bootstrap and canonical room model
│   ├── source/                   # user/developer docs inherited from Evennia
│   └── pylib/                    # docs build helpers
├── evennia/
│   ├── game_template/            # primary customization surface for your project
│   │   ├── commands/             # custom command sets and command behavior
│   │   ├── server/               # project settings and server-side hooks
│   │   ├── tests/                # project-level tests
│   │   ├── typeclasses/          # rooms, objects, exits, accounts, scripts
│   │   ├── web/                  # project web overrides
│   │   └── world/                # world data, prototypes, batch content
│   ├── commands/                 # upstream/default Evennia command system
│   ├── contrib/                  # optional subsystems and examples
│   ├── server/                   # engine server, portal, sessions, launcher internals
│   ├── utils/                    # core helpers, creation/search/menu/table utilities
│   └── web/                      # engine web stack and API
├── bin/                          # launchers, helper scripts, rename tools
└── .github/                      # workflows and repository automation
```

## Where to customize first

If your goal is to evolve TIME-EVE rather than maintain Evennia itself, start here:

### 1. `evennia/game_template/typeclasses/`
Use this for the core behavior of timeline rooms, event objects, exits, accounts, and scripts.

This is the best place to implement or refine:

- timeline room metadata
- traversal constraints
- event insertion behavior
- developer-visible diagnostics
- richer descriptions of moments, states, and entities

### 2. `evennia/game_template/commands/`
Use this for commands such as:

- jumping to a UTC node
- moving forward/backward through anchors
- inspecting timeline state
- inserting events or markers
- debugging chronology and links

### 3. `evennia/game_template/world/`
Use this for structured world/timeline content:

- prototypes
- seed data
- event definitions
- batch creation flows
- timeline import/export utilities

### 4. `evennia/game_template/server/`
Use this for project configuration and hook-up:

- settings
- startup behavior
- registration of custom systems
- service integration for timeline maintenance or automation

### 5. `evennia/game_template/tests/`
Use this to lock in the timeline contract:

- canonical UTC labeling
- correct `prev` / `next` rewiring
- no unintended room auto-creation
- search and movement behavior
- command and typeclass invariants

## Suggested mental model

A helpful way to think about the repo is in three layers:

### Layer 1: Engine
The large `evennia/` package provides networking, sessions, accounts, commands, web support, scripts, search, object creation, and persistence.

### Layer 2: Project template
`evennia/game_template/` is the intended place to shape TIME-EVE into an actual timeline application/world.

### Layer 3: Project intent
`docs/ops/setup.md`, `BODY.md`, `MIND.md`, and `SOUL.md` define what this fork is *for*:

- a navigable timeline
- controlled world insertion
- visible, debuggable behavior
- safe defaults for further development

## Bootstrap path

For the timeline bootstrap model, use `docs/ops/setup.md`.

That document already defines:

- the canonical room key format
- the `room.db.utc` identity field
- the monthly anchor generation plan
- the `prev` / `next` linking pattern
- a one-time `evennia shell` population script
- an insertion rule that preserves upgrade safety

In other words, `setup.md` should be treated as the operational source of truth for the initial timeline topology.

## Customization roadmap

A practical progression for extending TIME-EVE is:

1. **Lock the temporal model**
   - keep `UTC:<unix_seconds>` canonical
   - keep insertion explicit
   - keep navigation deterministic

2. **Implement timeline-native commands**
   - `goto` helpers
   - timeline inspection commands
   - event creation / insertion tools

3. **Enrich rooms as moments**
   - descriptions
   - tags
   - metadata
   - linked entities and state snapshots

4. **Add observability early**
   - preserve breadcrumb-style debug traces
   - expose traversal and insertion logic clearly

5. **Keep engine changes deliberate**
   - prefer customizing the game template first
   - only modify deeper engine code when the requirement truly belongs there

## Relationship to upstream Evennia

TIME-EVE currently inherits the breadth of Evennia’s engine and documentation. That is useful, but the project should be read as **an opinionated temporal application built on top of that engine**, not as an unmodified general-purpose MUD starter.

So the fastest way to understand the repo is:

1. read this README;
2. read `docs/ops/setup.md`;
3. inspect `BODY.md`, `MIND.md`, and `SOUL.md`;
4. work inside `evennia/game_template/` first.

## In one sentence

**TIME-EVE is an Evennia-based timeline substrate where UTC-addressed rooms form a controlled navigable chronology that can be extended into richer temporal simulation, storytelling, and world logic.**
