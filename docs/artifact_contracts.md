# Artifact Contracts

This document is the authoritative registry for shared file artifacts produced or consumed by project tooling.

## Current state

The project is now entering the first implementation phase.

The artifacts below are the first cross-tool runtime/documentation artifacts that should be treated as canonical for the initial implementation pass.

## Artifact: Final Initial Blueprint

- Owner: design / implementation planning
- Canonical path: `docs/design/final_initial/final_initial_blueprint.md`
- Lifecycle: maintained while the first implementation pass is active; updated only when implementation decisions materially change
- Writers:
  - Project Owner
  - assistant, when explicitly directed
- Readers:
  - all implementation contributors
  - future continuity reports
  - future design-sync updates to root docs

## Artifact: Final Initial Implementation Gameplan

- Owner: implementation planning
- Canonical path: `docs/design/final_initial/final_initial_implementation_gameplan.md`
- Lifecycle: maintained while the first implementation pass is active; updated when implementation order, scope, or test plan changes
- Writers:
  - Project Owner
  - assistant, when explicitly directed
- Readers:
  - all implementation contributors
  - future continuity reports
  - anyone executing the first code-scaffolding pass

## Artifact: Runtime Snapshot Contract

- Owner: runtime layer
- Canonical path: defined conceptually in `docs/design/implementation_contracts.md`; code-level canonical location expected to begin in `src/state_collapser/tower/snapshot.py`
- Lifecycle: will become active when the first implementation of `RuntimeSnapshot` lands
- Writers:
  - runtime update engine
  - test fixtures that intentionally construct snapshots
- Readers:
  - training/control logic
  - adapters such as `gymnasium`
  - integration tests
  - debugging and continuity tooling

## Artifact: First Toy Environment

- Owner: examples / integration proving ground
- Canonical path: expected to begin at `src/state_collapser/examples/robot_constraint_toy.py`
- Lifecycle: active during the first honest vertical slice; should persist as the primary end-to-end example until a better proving ground supersedes it
- Writers:
  - implementation contributors
- Readers:
  - unit and integration tests
  - adapters
  - documentation examples

## Registry Rule

Whenever a new shared artifact becomes important to more than one subsystem, record:

- Owner
- Canonical path
- Lifecycle
- Writers
- Readers
