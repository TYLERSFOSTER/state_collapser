# Fiber-Conditioned Training Spine Implementation Gameplan

## Status

This document is the Phase.Stage.Action implementation gameplan for:

- `docs/design/RL_framework_maturity/01_002_fiber_conditioned_training_spine_blueprint.md`

It is paired with:

- `docs/design/RL_framework_maturity/01_005_fiber_conditioned_training_spine_engineer_documentation_implementation_gameplan.md`

It is downstream of:

- `docs/design/RL_framework_maturity/01_001_rl_framework_maturity_and_tower_training_spine_discussion.md`
- `docs/design/RL_framework_maturity/01_003_fiber_conditioned_training_spine_engineer_documentation_blueprint.md`

It is governed by:

- `docs/prime_directive/prime_directive.md`
- `docs/prime_directive/git_practices.md`
- `docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md`
- `docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md`

This is an implementation gameplan.

It is not an implementation.

No source-code execution should begin until the Project Owner explicitly
approves execution of this gameplan.

Once approved, this gameplan is law. If implementation reality conflicts with
any Phase.Stage.Action item below, the implementer must stop, identify the exact
item that failed, and ask the Project Owner for guidance. Silent simplification,
silent reordering, and silent reinterpretation are forbidden.

## Paired Reality Contract

This code gameplan and the paired documentation gameplan must reflect the same
architecture.

The shared reality is:

```text
PartitionTower
    -> FrozenQuotientBehavior
        -> PathFiber
            -> FiberConditionedStage
                -> existing learner-facing training surfaces
```

The implementation must not drift into:

```text
state_collapser as an RLlib clone
state_collapser as a Stable-Baselines3 clone
state_collapser as a hidden .learn(...) training framework
```

The package owns the tower/fiber/stage semantics.

The engineer or external framework owns the learner, model, optimizer, and
training loop mechanics.

## Fixed Decisions From Blueprint Review

The Project Owner resolved the open questions in
`01_002_fiber_conditioned_training_spine_blueprint.md`.

These decisions are fixed for this gameplan.

1. The frozen behavior object is named:

   ```text
   FrozenQuotientBehavior
   ```

2. `FrozenQuotientBehavior` may represent either:

   - a concrete frozen path or path prefix
   - a policy-level or decision-surface behavior

3. `FiberConditionedStage` is not a Gymnasium env in the first implementation.

4. `tower/control` is not immediately rewritten wholesale.

   It is preserved as proto control infrastructure and mined only where useful.

5. Old terminology is not swept-renamed in the first implementation.

   New surfaces use corrected vocabulary. Compatibility fields can remain.

6. `CONTRIBUTING.md` must receive TODO items to revisit:

   - the long-term fate of `tower/control`
   - terminology cleanup for `base` / `lower` vocabulary

The paired documentation gameplan carries the same decisions.

## Fixed Defaults For This Gameplan

Unless the Project Owner changes these before execution, implementation must use
the following defaults.

1. The dedicated implementation branch is:

   ```text
   codex/fiber-conditioned-training-spine
   ```

2. The shared running implementation log is:

   ```text
   docs/design/RL_framework_maturity/01_006_fiber_conditioned_training_spine_paired_implementation_log.md
   ```

3. New code lives initially under:

   ```text
   src/state_collapser/training/
   ```

4. New files are:

   ```text
   src/state_collapser/training/frozen.py
   src/state_collapser/training/fibers.py
   src/state_collapser/training/stages.py
   ```

5. New public training exports are added through:

   ```text
   src/state_collapser/training/__init__.py
   ```

6. First-scope implementation supports adjacent tier pairs only:

   ```text
   fine_tier = coarse_tier - 1
   ```

7. First-scope `PathFiber` supports concrete frozen quotient steps before
   general policy-surface evaluation.

8. First-scope `FrozenQuotientBehavior` still includes fields that can later
   support policy-level behavior.

9. First-scope `FiberConditionedStage` is package-native. It exposes a direct
   stage API and does not pretend to be Gymnasium.

10. The first runnable stage loop should be intentionally boring:

    ```python
    current_input = stage.reset(seed=0)
    for _ in range(max_steps):
        decision = learner.act(current_input)
        transition = stage.step(decision)
        learner.observe(transition)
        learner.update()
        current_input = transition.target_input
    ```

11. Existing `StepCollector` and reference loops must remain backward
    compatible.

12. If reference-loop compatibility requires a wrapper, introduce a small wrapper
    rather than turning `StepCollector` into a fiber-stage framework.

13. No Torch, SB3, RLlib, replay buffer, checkpoint, manifest, or vectorized
    rollout implementation belongs in this first slice.

14. Compatibility names such as `current_base_state` and `frozen_lower_context`
    may remain. New names must prefer:

    ```text
    total_state
    fine_tier
    coarse_tier
    frozen_quotient_behavior
    path_fiber
    stage_context
    ```

15. Documentation updates are not optional. The paired documentation gameplan is
    part of the same implementation reality.

## Required Branch Discipline

Execution must not start on `main`.

Before implementation begins, create or switch to:

```text
codex/fiber-conditioned-training-spine
```

If the Project Owner requests a different branch name, use that name.

Before editing implementation files, record the active branch, current commit,
and starting `git status --short` in the shared implementation log.

## Required Running Implementation Log

Execution must maintain:

```text
docs/design/RL_framework_maturity/01_006_fiber_conditioned_training_spine_paired_implementation_log.md
```

The log must record:

- branch name
- starting commit
- starting git status
- each completed Phase.Stage.Action item
- exact files edited
- exact tests run
- test outcomes
- documentation files updated
- surprises and failures
- Project Owner clarifications
- any authorized deviations

The log must not hide weakened work behind phrases like "first pass",
"minimal slice", or "good enough" unless the Project Owner explicitly
authorizes that framing for a specific item.

## Validation Command Set

Focused training validation:

```text
uv run pytest tests/training
```

Tower query validation:

```text
uv run pytest tests/tower/partition tests/tower/test_runtime.py
```

Example regression validation:

```text
uv run pytest tests/examples/test_plate_support_env_tower_training.py tests/examples/test_training_semantics_shared.py tests/examples/test_training_schema_pass_through.py
```

Full validation:

```text
uv run pytest
```

Static validation:

```text
uv run ruff check .
uv run mypy src
```

If any validation command fails unexpectedly, stop and reconstruct reality before
editing further.

## Global Stop Conditions

Implementation must stop and ask the Project Owner if any of the following
occur.

- A Phase.Stage.Action item cannot be implemented as written.
- A source file or symbol named here no longer exists.
- Existing tests encode semantics that contradict this gameplan.
- `PartitionTower` lacks a query needed by `PathFiber` and adding it would
  require broad tower rewrites.
- Concrete frozen quotient steps cannot be represented without deciding the full
  policy-surface design.
- Stage stepping requires choosing between incompatible public APIs not fixed by
  this gameplan.
- Maintaining backward compatibility with `ActionSelectionInput`,
  `TrainingTransition`, or `TabularQLearner` would require weakening the new
  stage/fiber semantics.
- The implementation would force a sweeping rename of `base` or `lower`
  vocabulary.
- `tower/control` integration requires a broad rewrite.
- A documentation example would require an import path that does not exist.
- A validation command fails unexpectedly.
- The working tree contains unrelated user changes in files this gameplan must
  edit.
- The implementation would need to revert user work.

## Phase 0: Execution Setup And Reality Binding

### Stage 0.1: Confirm Execution Authority

#### Action 0.1.1

Confirm that the Project Owner explicitly approved execution of this gameplan.

Completion criteria:

- The implementation log quotes or references the approval.
- No source-code edits occur before approval.

Stop condition:

- If approval is ambiguous, do not implement.

#### Action 0.1.2

Create or switch to the dedicated implementation branch.

Required branch:

```text
codex/fiber-conditioned-training-spine
```

Completion criteria:

- The active branch is the implementation branch.
- The implementation log records branch, commit, and starting status.

Stop condition:

- If branch creation/switching reveals unexpected worktree state, stop and ask.

### Stage 0.2: Re-Bind Repository Reality

#### Action 0.2.1

Re-read the source blueprints and paired gameplans from disk.

Required files:

```text
docs/design/RL_framework_maturity/01_002_fiber_conditioned_training_spine_blueprint.md
docs/design/RL_framework_maturity/01_003_fiber_conditioned_training_spine_engineer_documentation_blueprint.md
docs/design/RL_framework_maturity/01_004_fiber_conditioned_training_spine_implementation_gameplan.md
docs/design/RL_framework_maturity/01_005_fiber_conditioned_training_spine_engineer_documentation_implementation_gameplan.md
```

Completion criteria:

- The implementation log records that the files were re-read.
- The fixed PO decisions are still present and consistent.

#### Action 0.2.2

Re-read the relevant current source files from disk.

Required files:

```text
src/state_collapser/training/__init__.py
src/state_collapser/training/inputs.py
src/state_collapser/training/transitions.py
src/state_collapser/training/decisions.py
src/state_collapser/training/learners.py
src/state_collapser/training/collectors.py
src/state_collapser/training/reference_loops.py
src/state_collapser/tower/partition/tower.py
src/state_collapser/tower/partition/ids.py
src/state_collapser/tower/runtime.py
src/state_collapser/tower/control/frozen_context.py
src/state_collapser/tower/control/executor.py
src/state_collapser/tower/control/transition.py
```

Completion criteria:

- The implementation log records any discovered drift.
- No code edits begin until drift is understood.

#### Action 0.2.3

Run baseline focused validation.

Command:

```text
uv run pytest tests/training tests/tower/partition
```

Completion criteria:

- The command passes.
- The result is recorded in the implementation log.

Stop condition:

- If the command fails, stop and diagnose before editing source.

## Phase 1: Introduce Shared Fiber Vocabulary

### Stage 1.1: Create New Training Modules

#### Action 1.1.1

Create the new training modules.

Files:

```text
src/state_collapser/training/frozen.py
src/state_collapser/training/fibers.py
src/state_collapser/training/stages.py
```

Completion criteria:

- Files exist.
- Files contain only typed, importable definitions needed by this phase.
- No behavior is wired into existing runtime yet.

#### Action 1.1.2

Update `src/state_collapser/training/__init__.py` to export only the new stable
surface names introduced in this gameplan.

Initial expected exports:

```text
FrozenQuotientBehavior
FrozenQuotientStep
FiberDeparture
FiberDepartureReason
FiberStageContext
PathFiber
FiberConditionedStage
```

Completion criteria:

- Imports from `state_collapser.training` work.
- Existing exports remain intact.

### Stage 1.2: Define Stage Context And Departure Diagnostics

#### Action 1.2.1

Implement `FiberStageContext`.

Required fields:

```python
stage_id: str
fiber_id: str
fine_tier: int
coarse_tier: int
frozen_behavior_id: str
frozen_behavior_version: int | str
```

Completion criteria:

- The dataclass is frozen and uses slots.
- It validates that `coarse_tier == fine_tier + 1` for first-scope use.
- It has no dependency on Torch, Gymnasium, SB3, or RLlib.

#### Action 1.2.2

Implement `FiberDepartureReason`.

Required initial reason names:

```text
ACTION_NOT_IN_FIBER
PROJECTED_TARGET_MISMATCH
NO_LIFT_CANDIDATE
STALE_TOWER_CONTEXT
UNKNOWN_STATE_CELL
UNKNOWN_ACTION_CELL
ILLEGAL_ACTION_INDEX
UNSPECIFIED
```

Completion criteria:

- The reasons are represented by a typed enum or equivalent stable surface.
- Names are readable in diagnostics.

#### Action 1.2.3

Implement `FiberDeparture`.

Required fields:

```python
reason: FiberDepartureReason
stage_context: FiberStageContext | None
expected: object | None
actual: object | None
attempted: object | None
diagnostics: Mapping[str, object]
```

Completion criteria:

- The dataclass is frozen and uses slots.
- Diagnostics default safely.
- Tests can assert exact reasons.

### Stage 1.3: Test Shared Vocabulary

#### Action 1.3.1

Create tests for `FiberStageContext`.

Suggested file:

```text
tests/training/test_fiber_stage_context.py
```

Required assertions:

- valid adjacent tiers construct successfully
- invalid non-adjacent tiers raise a clear error
- field values are preserved

#### Action 1.3.2

Create tests for `FiberDeparture`.

Suggested file:

```text
tests/training/test_fiber_departure.py
```

Required assertions:

- reasons are stable
- diagnostics default safely
- expected/actual/attempted payloads are preserved

#### Action 1.3.3

Run focused validation.

Command:

```text
uv run pytest tests/training/test_fiber_stage_context.py tests/training/test_fiber_departure.py
```

Completion criteria:

- The command passes.
- The implementation log records the result.

## Phase 2: Implement Frozen Quotient Behavior

### Stage 2.1: Define Concrete Frozen Quotient Step

#### Action 2.1.1

Implement `FrozenQuotientStep`.

Required fields:

```python
coarse_tier: int
source_cell: object
action_cell: object | None
target_cell: object | None
metadata: Mapping[str, object]
```

Completion criteria:

- The dataclass is frozen and uses slots.
- It can represent a concrete coarse decision with or without a known target.
- It does not depend on a specific partition id class in its public annotation,
  but tests should use real partition IDs where possible.

### Stage 2.2: Define Frozen Quotient Behavior

#### Action 2.2.1

Implement `FrozenQuotientBehavior`.

Required fields:

```python
behavior_id: str
coarse_tier: int
supported_fine_tier: int
tower_fingerprint: str | None
schema_fingerprint: str | None
decision_surface: object | None
current_step: FrozenQuotientStep | None
path_prefix: tuple[object, ...]
action_prefix: tuple[object, ...]
version: int | str
metadata: Mapping[str, object]
```

Completion criteria:

- The dataclass is frozen and uses slots.
- It validates `coarse_tier == supported_fine_tier + 1`.
- It supports both concrete `current_step` behavior and future
  `decision_surface` behavior.
- It does not mutate learner/model objects.

#### Action 2.2.2

Implement a convenience constructor for concrete frozen steps if useful.

Potential name:

```python
FrozenQuotientBehavior.from_step(...)
```

Completion criteria:

- The constructor reduces example-doc boilerplate.
- It does not hide tier direction.
- It requires explicit `coarse_tier` and `supported_fine_tier`.

### Stage 2.3: Preserve Existing Frozen Context Compatibility

#### Action 2.3.1

Do not delete or broadly refactor `FrozenLowerContext`.

Completion criteria:

- Existing `tower/control` tests still import `FrozenLowerContext`.
- No existing exploit/explore behavior is intentionally changed in this phase.

#### Action 2.3.2

If a compatibility adapter is cheap and unambiguous, implement it as a narrow
helper. Otherwise, defer it.

Potential helper:

```python
frozen_behavior_from_lower_context(...)
```

Completion criteria:

- If implemented, it is documented as compatibility only.
- If deferred, the implementation log records why.

Stop condition:

- If the adapter requires deciding broad `tower/control` semantics, stop and ask.

### Stage 2.4: Test Frozen Behavior

#### Action 2.4.1

Create tests for `FrozenQuotientStep`.

Suggested file:

```text
tests/training/test_frozen_quotient_behavior.py
```

Required assertions:

- concrete source/action/target values are preserved
- metadata defaults safely
- coarse tier is preserved

#### Action 2.4.2

Create tests for `FrozenQuotientBehavior`.

Required assertions:

- valid adjacent tier behavior constructs
- invalid tier pair raises
- current concrete step is preserved
- path/action prefixes are preserved
- metadata is immutable-by-convention through frozen dataclass fields

#### Action 2.4.3

Run focused validation.

Command:

```text
uv run pytest tests/training/test_frozen_quotient_behavior.py
```

Completion criteria:

- The command passes.
- The implementation log records the result.

## Phase 3: Add Stage/Fiber Context To Existing Training Surfaces

### Stage 3.1: Extend `ActionSelectionInput`

#### Action 3.1.1

Add additive fields to `ActionSelectionInput`.

Required fields:

```python
stage_context: FiberStageContext | None = None
fiber_departure: FiberDeparture | None = None
```

Completion criteria:

- Existing constructor calls continue working.
- Existing tests continue passing without modification unless test expectations
  explicitly inspect dataclass fields.

#### Action 3.1.2

Update `build_action_selection_input(...)` to accept the new fields.

Completion criteria:

- Existing callers do not need to pass new arguments.
- New stage code can pass explicit stage/fiber context.

### Stage 3.2: Extend `TrainingTransition`

#### Action 3.2.1

Add additive fields to `TrainingTransition`.

Required fields:

```python
stage_context: FiberStageContext | None = None
projected_coarse_step: object | None = None
fiber_departure: FiberDeparture | None = None
```

Completion criteria:

- Existing transition construction remains valid.
- Existing learner behavior remains unchanged.
- The new fields can be asserted in tests.

### Stage 3.3: Test Backward Compatibility

#### Action 3.3.1

Update or add tests in:

```text
tests/training/test_inputs_and_transitions.py
```

Required assertions:

- old input construction works
- new input construction carries stage context
- old transition construction works
- new transition construction carries stage context and departure fields

#### Action 3.3.2

Run focused validation.

Command:

```text
uv run pytest tests/training/test_inputs_and_transitions.py tests/training/test_collectors.py tests/training/test_learners_and_reference_loops.py
```

Completion criteria:

- The command passes.
- The implementation log records the result.

## Phase 4: Implement Path Fiber

### Stage 4.1: Bind Path Fiber To Existing Tower Queries

#### Action 4.1.1

Implement `PathFiber`.

Required fields:

```python
fiber_id: str
tower: PartitionTower
fine_tier: int
coarse_tier: int
frozen_behavior: FrozenQuotientBehavior
metadata: Mapping[str, object]
```

Completion criteria:

- The dataclass validates adjacent tier relation.
- It rejects mismatch between its tiers and the frozen behavior tiers.
- It does not copy or rebuild the tower.
- It uses `PartitionTower` query methods rather than compatibility
  `QuotientTierView` readouts.

#### Action 4.1.2

Implement current-cell helpers.

Required behavior:

- compute current fine state cell for a total state
- compute current coarse state cell for a total state
- produce `FiberDeparture` for unknown states or cells

Completion criteria:

- Helpers are deterministic.
- Helpers return typed results or explicit departures.

### Stage 4.2: Add Missing Narrow Tower Query If Required

#### Action 4.2.1

Determine whether `PartitionTower` already exposes a way to map a concrete edge
or edge id to its action cell at a tier.

Completion criteria:

- The implementation log records the finding.

#### Action 4.2.2

If no such query exists, add the narrowest possible query to `PartitionTower`.

Potential method:

```python
action_cell_for_edge(self, tier: int, edge: BaseEdge) -> ActionCellId | None
```

Completion criteria:

- The method uses existing action-layer data.
- The method does not trigger compatibility readout construction.
- Tests cover the method.

Stop condition:

- If adding this query requires broad action-layer redesign, stop and ask.

### Stage 4.3: Implement Admissibility

#### Action 4.3.1

Implement `PathFiber.admissible_action_cells(...)` for concrete frozen steps.

Required behavior:

- start from outgoing fine action cells at the current fine state cell
- project each represented edge to the coarse tier
- keep only fine action cells compatible with the frozen coarse action/target
- return deterministic ordering

Completion criteria:

- The method works for a concrete `FrozenQuotientStep`.
- The method produces an empty tuple when no action is admissible.
- Empty admissibility is not silently treated as success.

#### Action 4.3.2

Implement `PathFiber.action_mask(...)`.

Required behavior:

- accept or derive a stable fine-stage action vocabulary
- mark admissible actions as `True`
- mark inadmissible actions as `False`
- return `None` only when no finite action vocabulary is available

Completion criteria:

- The method can be used by `ActionSelectionInput.action_mask`.
- Tests assert exact masks.

#### Action 4.3.3

Implement `PathFiber.lift_candidates(...)`.

Required behavior:

- delegate to `PartitionTower.lift_candidates(...)` where possible
- restrict candidates to fiber-admissible action cells
- prefer candidates executable from the current total state
- return deterministic ordering

Completion criteria:

- The method does not define the fiber from scratch.
- It is visibly a local realization helper over the path fiber.

#### Action 4.3.4

Implement `PathFiber.diagnose_departure(...)`.

Required behavior:

- return `None` for admissible candidates
- return `FiberDeparture` with exact reason for inadmissible candidates

Completion criteria:

- Tests cover at least one admissible and one inadmissible candidate.

### Stage 4.4: Test Path Fiber

#### Action 4.4.1

Create tests for `PathFiber` on a tiny synthetic graph.

Suggested file:

```text
tests/training/test_path_fiber.py
```

Required fixture:

```text
total graph:
    s0 -> s1 -> g
    s0 -> s2 -> g

coarser tier:
    relevant fine choices project to one frozen coarse decision
```

Required assertions:

- `PathFiber` validates adjacent tiers
- admissible fine action cells are computed from tower queries
- action masks match admissibility
- lift candidates prefer executable representatives
- departure diagnostics are explicit

#### Action 4.4.2

Run focused validation.

Command:

```text
uv run pytest tests/training/test_path_fiber.py tests/tower/partition/test_queries_and_lift.py
```

Completion criteria:

- The command passes.
- The implementation log records the result.

## Phase 5: Implement Fiber-Conditioned Stage

### Stage 5.1: Define Stage Result Surfaces

#### Action 5.1.1

Define any small reset/step result helpers needed by `FiberConditionedStage`.

Completion criteria:

- Helpers are private or narrow unless they are clearly part of the public
  training surface.
- No Gymnasium dependency is introduced.

### Stage 5.2: Implement Direct Stage API

#### Action 5.2.1

Implement `FiberConditionedStage`.

Required constructor data:

```python
stage_id: str
runtime: object
tower: PartitionTower
fine_tier: int
coarse_tier: int
frozen_behavior: FrozenQuotientBehavior
path_fiber: PathFiber
```

Completion criteria:

- The stage validates consistency between tower, tiers, frozen behavior, and path
  fiber.
- The stage does not own model or optimizer state.
- The stage does not subclass or depend on Gymnasium.

#### Action 5.2.2

Implement `FiberConditionedStage.reset(...)`.

Required behavior:

- delegate to the underlying runtime or accept a pre-reset runtime state
- produce an `ActionSelectionInput`
- attach `FiberStageContext`
- attach an action mask from `PathFiber`
- preserve existing diagnostics where available

Completion criteria:

- A learner can consume the returned input.
- Tests assert the stage context and action mask.

#### Action 5.2.3

Implement `FiberConditionedStage.current_input(...)`.

Required behavior:

- build the current `ActionSelectionInput` without advancing the runtime
- attach current stage/fiber metadata
- attach current fiber mask

Completion criteria:

- Repeated calls without stepping are stable.

#### Action 5.2.4

Implement `FiberConditionedStage.step(...)`.

Required behavior:

- accept an `ActionDecision`
- resolve the chosen stage action to a fiber-admissible primitive action or
  action-cell realization
- diagnose illegal departures
- step the underlying runtime only for admissible choices
- produce `TrainingTransition`
- attach `FiberStageContext`
- attach projected coarse step information
- attach departure diagnostics when applicable

Completion criteria:

- Valid actions produce transitions with source and target inputs.
- Invalid actions do not silently step outside the fiber.
- Error-vs-diagnostic behavior is explicit and tested.

### Stage 5.3: Keep Existing Loops Simple

#### Action 5.3.1

Add a tiny direct stage loop test using `TabularQLearner` or a trivial learner.

Completion criteria:

- The loop is readable.
- The learner sees `ActionSelectionInput`.
- The transition is a normal `TrainingTransition`.
- No Torch dependency is required.

#### Action 5.3.2

Decide whether a wrapper is needed for existing `run_reference_online_loop(...)`
compatibility.

Completion criteria:

- If not needed for the first slice, record deferral in the implementation log.
- If needed, implement only a small adapter or loop helper.

Stop condition:

- If compatibility requires broad `StepCollector` redesign, stop and ask.

### Stage 5.4: Test Fiber-Conditioned Stage

#### Action 5.4.1

Create tests for stage reset/current input.

Suggested file:

```text
tests/training/test_fiber_conditioned_stage.py
```

Required assertions:

- reset returns `ActionSelectionInput`
- input carries `FiberStageContext`
- input carries fiber-derived mask
- current input is stable before stepping

#### Action 5.4.2

Create tests for stage stepping.

Required assertions:

- admissible action produces `TrainingTransition`
- transition carries stage context
- transition carries projected coarse step
- inadmissible action is rejected or diagnosed as specified
- frozen behavior remains unchanged

#### Action 5.4.3

Run focused validation.

Command:

```text
uv run pytest tests/training/test_fiber_conditioned_stage.py tests/training/test_learners_and_reference_loops.py
```

Completion criteria:

- The command passes.
- The implementation log records the result.

## Phase 6: Existing Environment Smoke Integration

### Stage 6.1: Select Existing Example Target

#### Action 6.1.1

Use `plate_support_env` as the first existing-environment smoke target unless
current repo reality makes it unsuitable.

Completion criteria:

- The implementation log records the selected target.
- If another target is selected, the Project Owner authorizes the change.

### Stage 6.2: Add Fiber Stage Smoke Test

#### Action 6.2.1

Create a minimal `plate_support_env` fiber-conditioned stage smoke test.

Suggested file:

```text
tests/examples/test_plate_support_env_fiber_conditioned_stage.py
```

Required assertions:

- existing runtime can expose or provide a `PartitionTower`
- a simple frozen quotient behavior can be built
- a `PathFiber` can be constructed
- a `FiberConditionedStage` can reset
- a short direct loop can run without Torch
- existing flat training tests still pass

Stop condition:

- If the example requires broad runtime changes unrelated to fiber stage
  semantics, stop and ask.

### Stage 6.3: Run Example Regression

#### Action 6.3.1

Run focused example validation.

Command:

```text
uv run pytest tests/examples/test_plate_support_env_fiber_conditioned_stage.py tests/examples/test_plate_support_env_tower_training.py tests/examples/test_training_semantics_shared.py tests/examples/test_training_schema_pass_through.py
```

Completion criteria:

- The command passes.
- The implementation log records the result.

## Phase 7: Preserve And Mark Deferred Control/Terminology Work

### Stage 7.1: Add `CONTRIBUTING.md` TODOs

#### Action 7.1.1

Add a roadmap TODO to revisit the long-term fate of `tower/control`.

Required content:

```text
Revisit whether the proto exploit/explore `tower/control` stack should be
refactored around `FiberConditionedStage`, preserved as a reference controller,
or deprecated after the fiber-conditioned training spine is stable.
```

Completion criteria:

- The TODO appears in `CONTRIBUTING.md`.
- It does not imply the rewrite happens in this implementation.

#### Action 7.1.2

Add a roadmap TODO to revisit terminology cleanup.

Required content:

```text
Plan a deliberate compatibility/deprecation pass for old `base` and `lower`
vocabulary after new `total_state`, `fine_tier`, `coarse_tier`, and
`frozen_quotient_behavior` surfaces are established.
```

Completion criteria:

- The TODO appears in `CONTRIBUTING.md`.
- It does not authorize a sweeping rename in this implementation.

### Stage 7.2: Guard Existing Control Tests

#### Action 7.2.1

Run control regression tests.

Command:

```text
uv run pytest tests/tower/control
```

Completion criteria:

- Existing control tests pass.
- Any failure is treated as a stop condition unless directly caused by an
  approved compatibility update.

## Phase 8: Paired Documentation Handoff

### Stage 8.1: Trigger Documentation Gameplan Milestones

#### Action 8.1.1

Coordinate with
`01_005_fiber_conditioned_training_spine_engineer_documentation_implementation_gameplan.md`.

Completion criteria:

- The documentation plan's Milestone 1 and Milestone 2 can truthfully describe
  implemented names and import paths.
- No user-facing usage doc claims an API exists before it does.

#### Action 8.1.2

Provide exact import paths and minimal snippets to the documentation work.

Required imports:

```python
from state_collapser.training import FrozenQuotientBehavior
from state_collapser.training import PathFiber
from state_collapser.training import FiberConditionedStage
```

Completion criteria:

- These imports work.
- The documentation snippets can use them directly.

## Phase 9: Final Validation

### Stage 9.1: Focused Full Subsystem Validation

#### Action 9.1.1

Run training and tower validation.

Command:

```text
uv run pytest tests/training tests/tower
```

Completion criteria:

- The command passes.
- The implementation log records the result.

#### Action 9.1.2

Run example validation.

Command:

```text
uv run pytest tests/examples
```

Completion criteria:

- The command passes.
- The implementation log records the result.

### Stage 9.2: Full Repo Validation

#### Action 9.2.1

Run full tests.

Command:

```text
uv run pytest
```

Completion criteria:

- The command passes.
- The implementation log records the result.

#### Action 9.2.2

Run static checks.

Commands:

```text
uv run ruff check .
uv run mypy src
```

Completion criteria:

- Both commands pass.
- The implementation log records the result.

## Phase 10: Readiness Review

### Stage 10.1: Verify Acceptance Criteria

#### Action 10.1.1

Verify the code blueprint acceptance criteria.

Required checklist:

- `FrozenQuotientBehavior` exists.
- `PathFiber` exists.
- `FiberConditionedStage` exists.
- `ActionSelectionInput` carries stage/fiber context.
- `TrainingTransition` carries stage/fiber context.
- Simple learner loop runs inside a fiber-conditioned stage.
- Fiber admissibility is visible as masks or diagnostics.
- Existing flat training examples still work.
- Existing partition tower tests still work.

Completion criteria:

- The checklist is recorded in the implementation log.

### Stage 10.2: Verify Paired Documentation Reality

#### Action 10.2.1

Verify that the paired documentation gameplan's generated docs describe the
actual implemented surfaces.

Completion criteria:

- No docs mention non-existent imports as if implemented.
- No docs describe `FiberConditionedStage` as Gymnasium-first.
- No docs claim Torch/SB3/RLlib support was implemented.

### Stage 10.3: Final Status Report

#### Action 10.3.1

Write a final implementation-log summary.

Required content:

- what was implemented
- what was intentionally deferred
- exact validation commands and outcomes
- remaining risks
- whether execution is ready for Project Owner review

Completion criteria:

- The implementation log is complete.
- The Project Owner can review without reconstructing context from chat.

## Final Non-Negotiable

The implementation is successful only if the package now has the missing
semantic bridge:

```text
frozen coarser quotient behavior
    -> path fiber at the finer tier
        -> learner-facing fiber-conditioned stage
```

It is not successful merely because new names exist.

The names must be connected to the existing `PartitionTower` runtime and usable
by the existing training surfaces.
