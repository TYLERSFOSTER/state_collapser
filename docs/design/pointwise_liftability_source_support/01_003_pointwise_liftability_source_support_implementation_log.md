# Pointwise Liftability And Source-Support Implementation Log

Date: 2026-06-04

Branch:

```text
codex/pointwise-liftability-source-support
```

Blueprint:

```text
docs/design/pointwise_liftability_source_support/01_001_pointwise_liftability_source_support_blueprint.md
```

Gameplan:

```text
docs/design/pointwise_liftability_source_support/01_002_pointwise_liftability_source_support_implementation_gameplan.md
```

## Status Table

| Phase | Status | Notes |
| --- | --- | --- |
| Phase 0 | completed | Branch created; focused baseline passed. |
| Phase 1 | completed | Added asymmetric and recursive partition fixtures. |
| Phase 2 | completed | Added action-layer support maps, base-source caches, and edge lookup index. |
| Phase 3 | completed | Added strict executable APIs and adjacent support APIs on `PartitionTower`. |
| Phase 4 | completed | Updated `PathFiber` vocabulary, masks, candidates, and diagnostics. |
| Phase 5 | completed | Added stage safety regression for non-current-source representatives. |
| Phase 6 | completed | Updated plate-support executability predicate to strict tower API. |
| Phase 7 | completed | Updated runtime/API docs, README/CONTRIBUTING routing, and BBB handoff. |
| Phase 8 | completed | Focused tests, full pytest, Ruff, and mypy passed. |
| Phase 9 | completed | Final status/diff review completed; implementation is ready for PO review. |

## Phase Log

### Phase 0.Stage 1

- Action 1 completed: reread Prime Directive branch/gameplan rules before
  implementation.
- Action 2 completed: checked repository status before branch creation.
- Action 3 completed: created implementation branch
  `codex/pointwise-liftability-source-support`.

### Phase 0.Stage 2

- Action 1 completed: created this implementation log.
- Action 2 completed: recorded Phase 0 start before package source edits.

### Phase 1

- Phase 1.Stage 1 completed: added
  `tests/tower/partition/test_pointwise_liftability.py` with the asymmetric
  quotient-available/non-current-source fixture.
- Phase 1.Stage 2 completed: added a recursive nested-coset fixture protecting
  the tier-2 cell refined by tier-1 child bins.

### Phase 2

- Phase 2.Stage 1 completed: added adjacent source-support fields, flattened
  base-source cache fields, and `action_cell_by_edge_id`.
- Phase 2.Stage 2 completed: obsolete action-cell rebuild cleanup now removes
  stale support/cache/index entries.
- Phase 2.Stage 3 completed: extended action-cell rebuild and merge paths with
  lower-layer context and threaded that context through `PartitionTower`.
- Phase 2.Stage 4 completed: rebuild now records source-child support,
  base-source support, active collection support, lower action-cell support,
  and edge-to-action-cell indexes.
- Phase 2.Stage 5 completed: added action-layer query helpers and direct test
  coverage for base-source/source-child support indexes.

### Phase 3

- Phase 3.Stage 1 completed: added
  `PartitionTower.executable_lift_candidates(...)` with strict current-source
  semantics and no representative fallback.
- Phase 3.Stage 2 completed: added
  `PartitionTower.executable_action_cells(...)`.
- Phase 3.Stage 3 completed: added
  `PartitionTower.tier_is_executable_from_state(...)`.
- Phase 3.Stage 4 completed: added adjacent support APIs:
  `supported_child_state_cells(...)`, `active_child_state_cells(...)`, and
  `lower_action_cells_for_supported_child(...)`.
- Phase 3.Stage 5 completed: updated `action_cell_for_edge(...)` to use the
  direct `action_cell_by_edge_id` index.

### Phase 4

- Phase 4.Stage 1 completed: added `PathFiber.executable_action_vocabulary(...)`.
- Phase 4.Stage 2 completed: made `PathFiber.admissible_action_cells(...)`
  evaluate frozen-step compatibility over executable current-source edges.
- Phase 4.Stage 3 completed: made `PathFiber.lift_candidates(...)` strict.
- Phase 4.Stage 4 completed: updated `PathFiber.diagnose_departure(...)` so
  quotient-known but non-current-source actions report
  `NO_LIFT_CANDIDATE` with lift-count diagnostics.
- Phase 4.Stage 5 completed: added PathFiber tests for quotient vocabulary,
  executable vocabulary, masks, strict candidates, and pointwise diagnostics.

### Phase 5

- Phase 5.Stage 1 completed: verified `FiberConditionedStage` consumes strict
  `PathFiber` lift candidates.
- Phase 5.Stage 2 completed: added a stage regression proving a selected
  non-current-source representative does not call `runtime.step(...)`.

### Phase 6

- Phase 6.Stage 1 completed: updated `PlateSupportExploitExploreRuntime` to
  use `tower.tier_is_executable_from_state(...)`.
- Phase 6.Stage 2 completed: added/updated example tests proving the runtime
  calls the pointwise tower API.

### Phase 7

- Phase 7.Stage 1 completed: updated
  `docs/usage/01_002_tower_runtime_mental_model.md` to distinguish quotient
  availability, representative/readout candidates, strict executable
  candidates, and adjacent source-support APIs.
- Phase 7.Stage 2 completed: added minimal README and CONTRIBUTING routing to
  the pointwise liftability/source-support design folder and focused tests.
- Phase 7.Stage 3 completed: updated relevant API notes for `PartitionTower`
  and `PathFiber`.
- Phase 7.Stage 4 completed: added
  `01_004_big_boy_benchmarking_pointwise_liftability_handoff.md`.

## Validation Log

- Phase 0 baseline:

  ```bash
  uv run pytest tests/tower/partition tests/training tests/tower/control tests/examples/test_plate_support_env_exploit_explore_runtime.py
  ```

  Result:

  ```text
  202 passed, 3 skipped
  ```

- Phase 1 focused fixture validation:

  ```bash
  uv run pytest tests/tower/partition/test_pointwise_liftability.py
  ```

  Result:

  ```text
  3 passed
  ```

- Phase 2 focused action-layer/support validation:

  ```bash
  uv run pytest tests/tower/partition/test_action_layer.py tests/tower/partition/test_pointwise_liftability.py
  ```

  Result:

  ```text
  10 passed
  ```

- Phase 3 focused partition validation:

  ```bash
  uv run pytest tests/tower/partition/test_queries_and_lift.py tests/tower/partition/test_pointwise_liftability.py
  ```

  Result:

  ```text
  12 passed
  ```

- Phase 4 PathFiber/training validation:

  ```bash
  uv run pytest tests/training/test_path_fiber.py tests/training
  ```

  Result:

  ```text
  74 passed, 3 skipped
  ```

- Phase 5 FiberConditionedStage/training validation:

  ```bash
  uv run pytest tests/training/test_fiber_conditioned_stage.py tests/training
  ```

  Result:

  ```text
  75 passed, 3 skipped
  ```

- Phase 6 example/control validation:

  ```bash
  uv run pytest tests/examples/test_plate_support_env_exploit_explore_runtime.py tests/tower/control
  ```

  Result:

  ```text
  55 passed
  ```

- Phase 8 new pointwise test validation:

  ```bash
  uv run pytest tests/tower/partition/test_pointwise_liftability.py
  ```

  Result:

  ```text
  7 passed
  ```

- Phase 8 focused validation:

  ```bash
  uv run pytest tests/tower/partition tests/training tests/tower/control tests/examples/test_plate_support_env_exploit_explore_runtime.py
  ```

  Result:

  ```text
  215 passed, 3 skipped
  ```

- Phase 8 full validation:

  ```bash
  uv run pytest
  ```

  Result:

  ```text
  503 passed, 4 skipped
  ```

- Phase 8 static validation:

  ```bash
  uv run ruff check .
  uv run mypy src
  ```

  Result:

  ```text
  Ruff: All checks passed.
  mypy: Success: no issues found in 90 source files.
  ```

- Phase 9 patch hygiene validation:

  ```bash
  git diff --check
  ```

  Result:

  ```text
  no output
  ```

## Completion Summary

- The implementation adds source-support indexes to the action partition layer
  so quotient action cells can be distinguished from action cells executable at
  a particular concrete source state.
- `PartitionTower` now exposes strict pointwise execution APIs while preserving
  the existing quotient/readout APIs.
- `PathFiber` and the fiber-conditioned stage now use strict current-source
  lift candidates for execution-facing behavior.
- Plate-support tier fallback now checks pointwise executability instead of
  abstract quotient nonemptiness.
- Documentation and the downstream `big_boy_benchmarking` handoff note now
  explain the quotient/readout versus executable-control distinction.

## Surprises And Blockers

- During Phase 3 validation, `action_cell_by_edge_id` initially returned an
  obsolete action cell after merges because dirty merged-away collections could
  rebuild later and overwrite the index. Fixed by clearing action-cell indexes
  for obsolete merged collections and removing their dirty flags.
