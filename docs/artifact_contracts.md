# Artifact Contracts

This document is the authoritative registry for shared artifacts produced,
consumed, or treated as durable coordination surfaces by project tooling.

## Current State

The package is no longer in its first implementation phase. The current
artifact posture is research-mode but concrete: runtime values, tower views,
linearization reports, design documents, implementation logs, and continuity
reports are real coordination surfaces. Serious benchmark result artifacts are
still future work.

## Artifact: Live Runtime View

- Owner: runtime layer
- Canonical code location: `src/state_collapser/tower/snapshot.py`
- Primary type: `LiveRuntimeView`
- Lifecycle: active runtime value, not a serialized artifact by default
- Writers:
  - package runtimes
  - example runtimes
  - tests constructing live runtime state
- Readers:
  - training/control logic
  - fiber-conditioned stages
  - adapters and example integrations

## Artifact: Runtime Snapshot

- Owner: runtime layer
- Canonical code location: `src/state_collapser/tower/snapshot.py`
- Primary type: `RuntimeSnapshot`
- Lifecycle: serializable runtime-value artifact for tests, diagnostics, and
  future benchmark/reporting surfaces
- Writers:
  - runtime snapshot helpers
  - tests that intentionally construct serializable runtime records
- Readers:
  - diagnostics
  - documentation examples
  - future benchmark artifact tooling

## Artifact: Linearization Configuration

- Owner: training / tensorization boundary
- Canonical code location: `src/state_collapser/training/linearization.py`
- Primary type: `LinearizationConfig`
- Lifecycle: manifest-style configuration payload for numeric conversion
- Writers:
  - learner or benchmark setup code
  - tests for tensorization and linearization surfaces
- Readers:
  - linearization helpers
  - optional Torch conversion helpers
  - future benchmark manifests

## Artifact: Linearization Report

- Owner: training / tensorization boundary
- Canonical code location: `src/state_collapser/training/linearization.py`
- Primary type: `LinearizationReport`
- Lifecycle: lightweight manifest/report payload describing one conversion
  boundary, not a replay log
- Writers:
  - `build_linearization_report(...)`
  - benchmark or learner setup code
- Readers:
  - tests
  - documentation
  - future benchmark artifact tooling

## Artifact: Design Blueprint

- Owner: design / implementation planning
- Canonical path pattern: `docs/design/<topic>/01_00N_<topic>_blueprint.md`
- Lifecycle: durable design authority until superseded by a later blueprint or
  explicit Project Owner decision
- Writers:
  - Project Owner
  - Codex when explicitly directed
- Readers:
  - implementation gameplans
  - continuity reports
  - future repo audits

## Artifact: Implementation Gameplan

- Owner: implementation planning
- Canonical path pattern:
  `docs/design/<topic>/01_00N_<topic>_implementation_gameplan.md`
- Lifecycle: execution authority after Project Owner approval
- Writers:
  - Codex when explicitly directed
  - Project Owner through review/comments
- Readers:
  - implementation agents
  - implementation logs
  - continuity reports

## Artifact: Implementation Log

- Owner: implementation execution
- Canonical path pattern:
  `docs/design/<topic>/01_00N_<topic>_implementation_log.md`
- Lifecycle: created during implementation and retained as traceability
- Writers:
  - implementation agents
- Readers:
  - Project Owner
  - future audits
  - engineer continuity reports

## Artifact: Engineer Continuity Report

- Owner: continuity / project memory
- Canonical path pattern: `docs/engineer_continuity/YYYY/MM/DD/*.md`
- Lifecycle: durable session and release memory
- Writers:
  - Codex when explicitly directed
- Readers:
  - future agents
  - Project Owner
  - downstream project handoffs

## Deferred Artifact: Serious Benchmark Result Bundle

- Owner: future benchmark track
- Canonical path: not yet implemented
- Lifecycle: future work
- Expected future contents:
  - benchmark manifest
  - environment/schema/config metadata
  - git/package version metadata
  - timing and scaling result tables
  - optional linearization reports
  - regression thresholds
- Current status:
  - benchmark smoke commands exist
  - serious artifact output is intentionally not claimed as implemented

## Registry Rule

Whenever a new shared artifact becomes important to more than one subsystem,
record:

- Owner
- Canonical path or code location
- Lifecycle
- Writers
- Readers
- Whether it is implemented now or future work
