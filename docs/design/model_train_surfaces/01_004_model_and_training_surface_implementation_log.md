# Model And Training Surface Implementation Log

## Status

This log records execution of:

- [01_003_model_and_training_surface_implementation_gameplan.md]([state_collapser repository root]/docs/design/model_train_surfaces/01_003_model_and_training_surface_implementation_gameplan.md)

## Branch

- `codex/model-training-surfaces`

## Start State

- execution started from a clean `main` worktree
- implementation branch created before code edits

## Intended First Migration Target

- `rl_counterpoint_v3`

## Running Notes

- package skeleton and implementation log created
- first package locus is `src/state_collapser/training/`
- first-scope package was implemented with:
  - `inputs.py`
  - `decisions.py`
  - `transitions.py`
  - `collectors.py`
  - `learners.py`
  - `metrics.py`
  - `reference_loops.py`
  - curated `__init__.py`
- the first-scope package includes:
  - decision-input object
  - action-decision object
  - transition object
  - concrete `StepCollector`
  - concrete `EpisodeCollector`
  - general learner protocol
  - one concrete tabular reference learner
  - minimal metrics surface
  - online and episode reference loops
- `rl_counterpoint_v3` was used as the first real migration target
- `src/state_collapser/examples/rl_counterpoint_v3/training.py` now delegates its training loop to the new generic training surfaces instead of owning the full tabular loop locally
- the migrated example preserved its problem/runtime ownership split and still returns the same example-local structured training result shape

## Files Touched

- `src/state_collapser/training/__init__.py`
- `src/state_collapser/training/inputs.py`
- `src/state_collapser/training/decisions.py`
- `src/state_collapser/training/transitions.py`
- `src/state_collapser/training/collectors.py`
- `src/state_collapser/training/learners.py`
- `src/state_collapser/training/metrics.py`
- `src/state_collapser/training/reference_loops.py`
- `src/state_collapser/examples/rl_counterpoint_v3/training.py`
- `tests/training/test_inputs_and_transitions.py`
- `tests/training/test_collectors.py`
- `tests/training/test_learners_and_reference_loops.py`
- `tests/training/test_training_metrics_surface.py`

## Architectural Notes

- the first implementation stayed internal-first and did not attempt to freeze a public API promise
- the first implementation did not unify `TierLearner` with the broader learner surface
- the first implementation did not rewrite exploit/explore training surfaces
- the first implementation kept runtime structure downstream and available through `ActionSelectionInput` and `TrainingTransition` rather than collapsing runtime ownership into the training package
- the first implementation used a concrete tabular learner as a reference vertical slice only; it was not treated as the final long-term learner architecture

## Transitional Compromises

- `RuntimeLike` in `collectors.py` currently uses permissive `Any` return typing for `reset(...)` and `step(...)` so the new collector surface composes cleanly with the existing example runtimes without requiring a larger first-scope runtime-result type refactor
- reference loops are generic-first in structure but still consume current runtime reset/step result shapes directly through the collectors

## Validation

- focused training slice:
  - `.venv/bin/pytest tests/training tests/examples/test_rl_counterpoint_v3_tower_training.py`
  - result: `9 passed`
- broader examples slice:
  - `.venv/bin/pytest tests/examples`
  - result: `137 passed`
- full repo suite:
  - `.venv/bin/pytest`
  - result: `251 passed`
- type checking:
  - `.venv/bin/python -m mypy src`
  - result: passed
- linting:
  - `.venv/bin/python -m ruff check .`
  - result: passed

## Deferred Hardening

- vectorization
- device/tensor semantics
- batching / sequence semantics
- checkpointing / serialization
- explicit train / eval mode hardening

## Completion Assessment

- `state_collapser.training` now exists as a real internal package
- the package is organized by surface role, not algorithm family
- reusable decision-input, action-decision, and transition objects exist
- concrete collectors exist
- a general learner surface and one concrete reference learner exist
- a minimal metrics surface exists
- reference loops exist
- one real migrated example exists
- focused tests prove the surfaces compose

The implementation satisfies the first-scope completion standard set by:

- [01_003_model_and_training_surface_implementation_gameplan.md]([state_collapser repository root]/docs/design/model_train_surfaces/01_003_model_and_training_surface_implementation_gameplan.md)
