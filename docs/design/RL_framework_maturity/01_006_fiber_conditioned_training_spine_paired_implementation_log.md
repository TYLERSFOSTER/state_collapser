# Fiber-Conditioned Training Spine Paired Implementation Log

## Status

This is the running implementation log for the paired execution of:

- `docs/design/RL_framework_maturity/01_004_fiber_conditioned_training_spine_implementation_gameplan.md`
- `docs/design/RL_framework_maturity/01_005_fiber_conditioned_training_spine_engineer_documentation_implementation_gameplan.md`

The implementation branch is:

```text
codex/fiber-conditioned-training-spine
```

The starting commit is:

```text
d4e716155fbc7c9adc023d4c4930b94674626664
```

The starting `git status --short` output was empty.

## Approval

Project Owner approval was given in the implementation request:

```text
Ok. Implement both, following `prime_directive`. Make new git branch first forst work on both
```

This approval covers the paired code and engineer-documentation implementation
gameplans.

## Phase 0: Execution Setup And Reality Binding

### Code Plan

- Action 0.1.1 completed: Project Owner execution approval confirmed and recorded.
- Action 0.1.2 completed: dedicated branch created and active.
- Action 0.2.1 completed: source blueprints and paired gameplans were re-read from disk.
- Action 0.2.2 completed: required current source files were re-read from disk.

Observed repository reality:

- `src/state_collapser/training/frozen.py` does not yet exist.
- `src/state_collapser/training/fibers.py` does not yet exist.
- `src/state_collapser/training/stages.py` does not yet exist.
- Existing training surfaces live in `inputs.py`, `transitions.py`, `decisions.py`,
  `learners.py`, `collectors.py`, and `reference_loops.py`.
- Existing partition tower query surfaces already expose state cells, outgoing
  action cells, action-cell members, representative edges, lift candidates, and
  local refinement fibers.
- `PartitionTower` does not yet expose a direct `action_cell_for_edge(...)`
  method.
- Existing `tower/control` frozen-context code remains separate and should not
  be broadly rewritten in this execution.

### Documentation Plan

- Documentation Action 0.1.1 completed: paired execution approval confirmed and recorded.
- Documentation Action 0.2.1 completed: paired source and gameplan files were re-read.
- Documentation Action 0.2.2 completed: planned code-surface files checked before
  user-facing docs were created.

## Validation Log

- `uv run pytest tests/training tests/tower/partition`
  - Result: passed.
  - Observed output: `110 passed in 0.92s`.
- `uv run pytest tests/training/test_fiber_stage_context.py tests/training/test_fiber_departure.py tests/training/test_frozen_quotient_behavior.py tests/training/test_inputs_and_transitions.py tests/tower/partition/test_queries_and_lift.py`
  - Result: passed.
  - Observed output: `21 passed in 0.47s`.
- `uv run pytest tests/training/test_path_fiber.py tests/tower/partition/test_queries_and_lift.py`
  - Result: passed.
  - Observed output: `11 passed in 0.05s`.
- `uv run pytest tests/training/test_fiber_conditioned_stage.py tests/training/test_learners_and_reference_loops.py`
  - Result: passed.
  - Observed output: `17 passed in 0.68s`.
- `uv run pytest tests/training/test_inputs_and_transitions.py tests/training/test_collectors.py tests/training/test_learners_and_reference_loops.py`
  - Result: passed.
  - Observed output: `27 passed in 0.81s`.
- `uv run pytest tests/examples/test_plate_support_env_fiber_conditioned_stage.py tests/examples/test_plate_support_env_tower_training.py tests/examples/test_training_semantics_shared.py tests/examples/test_training_schema_pass_through.py`
  - Result: passed.
  - Observed output: `12 passed in 0.51s`.
- `uv run pytest tests/tower/control`
  - Result: passed.
  - Observed output: `38 passed in 0.06s`.
- `uv run python -c "from state_collapser.training import FrozenQuotientBehavior, PathFiber, FiberConditionedStage"`
  - Result: passed.
- `uv run pytest tests/training tests/tower`
  - Result: passed.
  - Observed output: `193 passed in 0.97s`.
- `uv run pytest tests/examples`
  - Result: passed.
  - Observed output: `203 passed in 1.28s`.
- `uv run pytest`
  - First full run result before lint cleanup: passed.
  - Observed output: `466 passed in 2.01s`.
- `uv run ruff check .`
  - First result: failed on two mechanical lint issues:
    `FiberDepartureReason` needed `StrEnum`, and `stages.py` had an unused
    `Sequence` import.
  - Final result after targeted lint fixes: passed with `All checks passed!`.
- `uv run mypy src`
  - Result: passed.
  - Observed output: `Success: no issues found in 88 source files`.
- `uv run pytest`
  - Final result after lint/type cleanup: passed.
  - Observed output: `466 passed in 2.03s`.

## Phase 1: Introduce Shared Fiber Vocabulary

- Action 1.1.1 completed: created `src/state_collapser/training/frozen.py`,
  `src/state_collapser/training/fibers.py`, and
  `src/state_collapser/training/stages.py`.
- Action 1.1.2 completed: exported the new public names through
  `src/state_collapser/training/__init__.py` while preserving existing exports.
- Action 1.2.1 completed: implemented `FiberStageContext`.
- Action 1.2.2 completed: implemented `FiberDepartureReason`.
- Action 1.2.3 completed: implemented `FiberDeparture`.
- Action 1.3.1 completed: added `tests/training/test_fiber_stage_context.py`.
- Action 1.3.2 completed: added `tests/training/test_fiber_departure.py`.
- Action 1.3.3 completed: focused validation passed.

## Phase 2: Implement Frozen Quotient Behavior

- Action 2.1.1 completed: implemented `FrozenQuotientStep`.
- Action 2.2.1 completed: implemented `FrozenQuotientBehavior`.
- Action 2.2.2 completed: implemented `FrozenQuotientBehavior.from_step(...)`.
- Action 2.3.1 completed: `FrozenLowerContext` was not deleted or broadly refactored.
- Action 2.3.2 deferred: no compatibility adapter was added because mapping the
  proto `FrozenLowerContext.supporting_tier` semantics into the new
  `FrozenQuotientBehavior` semantics would require deciding broader
  `tower/control` fate that this gameplan explicitly defers.
- Action 2.4.1 completed: added frozen step tests in
  `tests/training/test_frozen_quotient_behavior.py`.
- Action 2.4.2 completed: added frozen behavior tests in
  `tests/training/test_frozen_quotient_behavior.py`.
- Action 2.4.3 completed: focused validation passed.

## Phase 3: Add Stage/Fiber Context To Existing Training Surfaces

- Action 3.1.1 completed: added additive `stage_context` and `fiber_departure`
  fields to `ActionSelectionInput`.
- Action 3.1.2 completed: added the same optional fields to
  `build_action_selection_input(...)`.
- Action 3.2.1 completed: added additive `stage_context`,
  `projected_coarse_step`, and `fiber_departure` fields to
  `TrainingTransition`.
- Action 3.3.1 completed: added backward-compatible stage/fiber field
  assertions to `tests/training/test_inputs_and_transitions.py`.
- Action 3.3.2 completed: focused backward-compatibility validation passed.

## Phase 4: Implement Path Fiber

- Action 4.1.1 completed: implemented `PathFiber` with adjacent-tier and frozen
  behavior consistency validation.
- Action 4.1.2 completed: implemented current fine/coarse state-cell helpers and
  explicit unknown-state departures.
- Action 4.2.1 completed: `PartitionTower` did not previously expose a direct
  edge-to-action-cell query.
- Action 4.2.2 completed: added narrow
  `PartitionTower.action_cell_for_edge(...)` without constructing compatibility
  quotient readouts.
- Action 4.3.1 completed: implemented concrete-step
  `PathFiber.admissible_action_cells(...)`.
- Action 4.3.2 completed: implemented `PathFiber.action_mask(...)`.
- Action 4.3.3 completed: implemented `PathFiber.lift_candidates(...)` by
  delegating to `PartitionTower.lift_candidates(...)` and restricting to the
  active path fiber.
- Action 4.3.4 completed: implemented `PathFiber.diagnose_departure(...)`.
- Action 4.4.1 completed: added `tests/training/test_path_fiber.py`.
- Action 4.4.2 completed: focused validation passed.

## Phase 5: Implement Fiber-Conditioned Stage

- Action 5.1.1 completed: added the narrow `FiberStageStepResult` helper.
- Action 5.2.1 completed: implemented package-native `FiberConditionedStage`
  without Gymnasium inheritance or model/optimizer ownership.
- Action 5.2.2 completed: implemented `FiberConditionedStage.reset(...)`.
- Action 5.2.3 completed: implemented `FiberConditionedStage.current_input(...)`.
- Action 5.2.4 completed: implemented `FiberConditionedStage.step(...)` with
  fiber-admissible stepping and explicit departure diagnostics.
- Action 5.3.1 completed: added a tiny direct stage loop test using
  `TabularQLearner`.
- Action 5.3.2 completed: no wrapper was needed for
  `run_reference_online_loop(...)` compatibility in this slice; existing
  reference-loop validation passes unchanged.
- Action 5.4.1 completed: added reset/current-input tests in
  `tests/training/test_fiber_conditioned_stage.py`.
- Action 5.4.2 completed: added valid/invalid stepping tests in
  `tests/training/test_fiber_conditioned_stage.py`.
- Action 5.4.3 completed: focused validation passed.

## Phase 6: Existing Environment Smoke Integration

- Action 6.1.1 completed: selected `plate_support_env` as the existing
  environment smoke target.
- Action 6.2.1 completed: added
  `tests/examples/test_plate_support_env_fiber_conditioned_stage.py`.
- Action 6.3.1 completed: focused example validation passed.

## Phase 7: Preserve And Mark Deferred Control/Terminology Work

- Action 7.1.1 completed: added the `tower/control` fate TODO to
  `CONTRIBUTING.md`.
- Action 7.1.2 completed: added the terminology cleanup TODO to
  `CONTRIBUTING.md`.
- Action 7.2.1 completed: existing `tower/control` tests passed.

## Phase 8: Paired Documentation Handoff

- Action 8.1.1 completed: the documentation plan can truthfully describe the
  implemented names and import paths.
- Action 8.1.2 completed: the required imports work:
  `FrozenQuotientBehavior`, `PathFiber`, and `FiberConditionedStage`.

## Documentation Phase 0: Setup And Synchronization

- Documentation Action 0.1.1 completed: approval recorded.
- Documentation Action 0.2.1 completed: paired source and gameplan files were
  re-read.
- Documentation Action 0.2.2 completed: code surfaces were checked before
  user-facing docs were written.

## Documentation Phase 1: Roadmap And Design Indexing

- Documentation Action 1.1.1 completed: `CONTRIBUTING.md` contains the
  `tower/control` fate TODO.
- Documentation Action 1.1.2 completed: `CONTRIBUTING.md` contains the old
  terminology cleanup TODO.
- Documentation Action 1.2.1 completed: README remains concise and links to
  usage/API docs.

## Documentation Phase 2: Usage Documentation

- Documentation Action 2.1.1 completed: created `docs/usage/`.
- Documentation Action 2.2.1 completed: created
  `docs/usage/01_001_what_state_collapser_is.md`.
- Documentation Action 2.2.2 completed: created
  `docs/usage/01_002_tower_runtime_mental_model.md`.
- Documentation Action 2.2.3 completed: created
  `docs/usage/01_003_training_surface_quickstart.md`.
- Documentation Action 2.2.4 completed: created
  `docs/usage/01_004_fiber_conditioned_training.md`.
- Documentation Action 2.2.5 completed: created
  `docs/usage/01_005_using_your_own_training_loop.md`.
- Documentation Action 2.2.6 completed: created
  `docs/usage/01_006_gymnasium_integration.md`.
- Documentation Action 2.2.7 completed: created
  `docs/usage/01_007_glossary.md`.
- Documentation Action 2.2.8 completed: created
  `docs/usage/01_008_common_misunderstandings.md`.

## Documentation Phase 3: API Notes

- Documentation Action 3.1.1 completed: created `docs/api_notes/`.
- Documentation Action 3.2.1 completed: created
  `docs/api_notes/partition_tower.md`.
- Documentation Action 3.2.2 completed: created
  `docs/api_notes/training_inputs_and_transitions.md`.
- Documentation Action 3.3.1 completed: created
  `docs/api_notes/frozen_quotient_behavior.md`.
- Documentation Action 3.3.2 completed: created
  `docs/api_notes/path_fiber.md`.
- Documentation Action 3.3.3 completed: created
  `docs/api_notes/fiber_conditioned_stage.md`.

## Documentation Phase 4: Runnable Examples

- Documentation Action 4.1.1 completed: tiny graph walkthrough added to
  `docs/usage/01_004_fiber_conditioned_training.md`.
- Documentation Action 4.1.2 completed: public imports validated.
- Documentation Action 4.2.1 completed: `plate_support_env` walkthrough added
  to `docs/usage/01_004_fiber_conditioned_training.md`.

## Documentation Phase 5: Cross-Links And Navigation

- Documentation Action 5.1.1 completed: README links to `docs/usage` and
  `docs/api_notes`.
- Documentation Action 5.2.1 completed: `CONTRIBUTING.md` links to
  `docs/design/RL_framework_maturity`, `docs/usage`, and `docs/api_notes`.
- Documentation Action 5.3.1 completed: usage docs and API notes cross-link.

## Documentation Phase 6: Consistency Review

- Documentation Action 6.1.1 completed: direction-vocabulary search found only
  quoted misunderstandings or compatibility caveats in new docs.
- Documentation Action 6.2.1 completed: RLlib/SB3/Torch/Gymnasium mentions are
  positioning, non-goals, or future-adapter boundaries.
- Documentation Action 6.3.1 completed: public import baseline passes.

## Phase 9: Final Validation

- Action 9.1.1 completed: `uv run pytest tests/training tests/tower` passed.
- Action 9.1.2 completed: `uv run pytest tests/examples` passed.
- Action 9.2.1 completed: final `uv run pytest` passed.
- Action 9.2.2 completed: `uv run ruff check .` and `uv run mypy src` passed.

## Documentation Phase 7: Test And Static Validation

- Documentation Action 7.1.1 completed: focused validation through training and
  tower tests passed.
- Documentation Action 7.2.1 completed: full validation passed.
- Documentation Action 7.2.2 completed: static validation passed.

## Phase 10: Readiness Review

- Action 10.1.1 completed: code acceptance checklist:
  - `FrozenQuotientBehavior` exists.
  - `PathFiber` exists.
  - `FiberConditionedStage` exists.
  - `ActionSelectionInput` carries stage/fiber context.
  - `TrainingTransition` carries stage/fiber context.
  - A simple learner loop runs inside a fiber-conditioned stage.
  - Fiber admissibility is visible as masks and diagnostics.
  - Existing flat training examples still work.
  - Existing partition tower tests still work.
- Action 10.2.1 completed: paired docs describe the actual implemented
  surfaces and do not claim Gymnasium-first, Torch, SB3, or RLlib support.
- Action 10.3.1 completed: this implementation-log summary is complete for
  Project Owner review.

## Documentation Phase 8: Final Documentation Readiness Review

- Documentation Action 8.1.1 completed: docs answer the required engineer
  orientation questions.
- Documentation Action 8.2.1 completed: docs match implemented code surfaces.
- Documentation Action 8.3.1 completed: final documentation summary recorded.

## Completed Files

Created:

- `docs/design/RL_framework_maturity/01_006_fiber_conditioned_training_spine_paired_implementation_log.md`
- `src/state_collapser/training/frozen.py`
- `src/state_collapser/training/fibers.py`
- `src/state_collapser/training/stages.py`
- `tests/training/test_fiber_stage_context.py`
- `tests/training/test_fiber_departure.py`
- `tests/training/test_frozen_quotient_behavior.py`
- `tests/training/test_path_fiber.py`
- `tests/training/test_fiber_conditioned_stage.py`
- `tests/examples/test_plate_support_env_fiber_conditioned_stage.py`
- `docs/usage/01_001_what_state_collapser_is.md`
- `docs/usage/01_002_tower_runtime_mental_model.md`
- `docs/usage/01_003_training_surface_quickstart.md`
- `docs/usage/01_004_fiber_conditioned_training.md`
- `docs/usage/01_005_using_your_own_training_loop.md`
- `docs/usage/01_006_gymnasium_integration.md`
- `docs/usage/01_007_glossary.md`
- `docs/usage/01_008_common_misunderstandings.md`
- `docs/api_notes/partition_tower.md`
- `docs/api_notes/training_inputs_and_transitions.md`
- `docs/api_notes/frozen_quotient_behavior.md`
- `docs/api_notes/path_fiber.md`
- `docs/api_notes/fiber_conditioned_stage.md`

Edited:

- `docs/design/RL_framework_maturity/01_006_fiber_conditioned_training_spine_paired_implementation_log.md`
- `src/state_collapser/training/__init__.py`
- `src/state_collapser/training/inputs.py`
- `src/state_collapser/training/transitions.py`
- `src/state_collapser/training/collectors.py`
- `src/state_collapser/tower/partition/tower.py`
- `tests/training/test_inputs_and_transitions.py`
- `tests/tower/partition/test_queries_and_lift.py`
- `CONTRIBUTING.md`
- `README.md`

## Deferred Decisions

- A direct compatibility adapter from `FrozenLowerContext` to
  `FrozenQuotientBehavior` is deferred until the long-term fate of
  `tower/control` is decided.

## Surprises

- Ruff caught two mechanical issues during static validation:
  - `FiberDepartureReason` needed to inherit from `StrEnum`.
  - `src/state_collapser/training/stages.py` had an unused `Sequence` import.
- Both issues were fixed directly and final Ruff, mypy, and pytest validation
  passed.
