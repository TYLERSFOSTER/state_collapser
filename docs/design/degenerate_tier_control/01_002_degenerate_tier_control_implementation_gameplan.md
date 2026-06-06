# Degenerate Tier Control Implementation Workplan

Date: 2026-05-30

Status: implementation workplan, not yet executed

Source blueprint:

- `docs/design/degenerate_tier_control/01_001_degenerate_tier_control_blueprint.md`

Source diagnosis:

- `docs/design/degenerate_tier_control/error_diagnosis_conversation.md`

Primary implementation targets:

- `src/state_collapser/tower/control/signals.py`
- `src/state_collapser/tower/control/controller.py`
- `src/state_collapser/tower/runtime.py`
- `src/state_collapser/examples/plate_support_env/runtime.py`
- `tests/tower/control/test_signals.py`
- `tests/tower/control/test_controller.py`
- `tests/tower/control/test_runtime_loop.py`
- `tests/examples/test_plate_support_env_exploit_explore_runtime.py`

## Implementation Thesis

The implementation should encode one simple control invariant:

```text
Do not ask a learner to choose an executable action at a tier whose current
state-cell has empty outgoing action cells.
```

The operational rule is:

```text
if Out(active tier) is empty:
    lift to the nearest finer tier whose Out is nonempty
```

If tier `0` is also empty, the runtime should return a clean no-action control
result rather than calling the learner or executor.

This is a controller/runtime correction, not a learner rewrite.

## Branch Discipline

### Phase 0. Stage 1. Action 1: Create Implementation Branch

Create a dedicated implementation branch before making code changes:

```bash
git switch main
git pull --ff-only
git switch -c codex/degenerate-tier-control
```

Rationale:

- This is a behavior change in the active-tier control path.
- It affects downstream `big_boy_benchmarking` behavior.
- It should merge cleanly back to `main` after tests pass.

### Phase 0. Stage 1. Action 2: Confirm Starting State

Run:

```bash
git status --short --branch
```

Expected:

```text
## codex/degenerate-tier-control
```

Any pre-existing untracked or modified files should be inspected before
implementation begins.

## Phase 1: Add Executability Filtering To Tier Signal Selection

Goal:

```text
Lowest-unclosed tier selection must not target a tier that is known to be
non-executable.
```

### Phase 1. Stage 1. Action 1: Add Predicate Type Import

Target:

```text
src/state_collapser/tower/control/signals.py
```

Add:

```python
from collections.abc import Callable
```

This avoids using `typing.Callable` and matches modern code style.

### Phase 1. Stage 1. Action 2: Extend `select_lowest_unclosed_tier`

Current signature:

```python
def select_lowest_unclosed_tier(
    deepest_known_tier: int,
    signals_by_tier: dict[int, TierSignalState],
    tier_configs: dict[int, TierControlConfig],
) -> int | None:
```

New signature:

```python
def select_lowest_unclosed_tier(
    deepest_known_tier: int,
    signals_by_tier: dict[int, TierSignalState],
    tier_configs: dict[int, TierControlConfig],
    *,
    tier_is_executable: Callable[[int], bool] | None = None,
) -> int | None:
```

### Phase 1. Stage 1. Action 3: Skip Non-Executable Tiers

Inside the scan loop:

```python
for tier_index in range(deepest_known_tier, -1, -1):
    if tier_is_executable is not None and not tier_is_executable(tier_index):
        continue
    ...
```

Do not treat a non-executable tier as closed. It is not closed; it is simply
not a valid execution locus for the current active decision.

### Phase 1. Stage 1. Action 4: Preserve Default Behavior

When `tier_is_executable is None`, behavior must be byte-for-byte equivalent in
meaning to the current behavior.

This is important because existing users of `select_lowest_unclosed_tier(...)`
should not be forced to understand tower action availability.

## Phase 2: Teach The Controller About Executable Tiers

Goal:

```text
ActiveTierController.decide(...) should not steer toward an unclosed tier if
that tier is known to have no outgoing action surface.
```

### Phase 2. Stage 1. Action 1: Add Predicate Type Import

Target:

```text
src/state_collapser/tower/control/controller.py
```

Add:

```python
from collections.abc import Callable
```

### Phase 2. Stage 1. Action 2: Extend `ActiveTierController.decide`

Current method receives:

```python
signals_by_tier: dict[int, TierSignalState],
tier_configs: dict[int, TierControlConfig],
frozen_context: FrozenLowerContext,
training_due: bool,
```

Add:

```python
tier_is_executable: Callable[[int], bool] | None = None,
```

Recommended final keyword-only tail:

```python
signals_by_tier: dict[int, TierSignalState],
tier_configs: dict[int, TierControlConfig],
frozen_context: FrozenLowerContext,
training_due: bool,
tier_is_executable: Callable[[int], bool] | None = None,
```

### Phase 2. Stage 1. Action 3: Pass Predicate To Signal Selection

Update:

```python
lowest_unclosed_tier = select_lowest_unclosed_tier(
    deepest_known_tier,
    signals_by_tier,
    tier_configs,
)
```

to:

```python
lowest_unclosed_tier = select_lowest_unclosed_tier(
    deepest_known_tier,
    signals_by_tier,
    tier_configs,
    tier_is_executable=tier_is_executable,
)
```

### Phase 2. Stage 1. Action 4: Do Not Add Learner Knowledge

Do not add action-vocabulary arguments to the controller.

Do not add `PartitionTower` arguments to the controller.

The controller only needs an opaque predicate:

```text
tier index -> executable?
```

This keeps the controller generic.

## Phase 3: Add Runtime-Level Degenerate-Tier Guard

Goal:

```text
ExploitExploreTowerRuntime.step() must never call behavior_action(...) at a
non-executable active tier.
```

### Phase 3. Stage 1. Action 1: Add Predicate Support To Runtime Constructor

Target:

```text
src/state_collapser/tower/runtime.py
```

Add import:

```python
from collections.abc import Callable
```

if not already available in the file.

Extend `ExploitExploreTowerRuntime.__init__(...)`:

```python
tier_is_executable: Callable[[int], bool] | None = None,
```

Store:

```python
self._tier_is_executable = tier_is_executable
```

### Phase 3. Stage 1. Action 2: Add Internal Predicate Helper

Add a private method:

```python
def _is_tier_executable(self, tier: int) -> bool:
    if self._tier_is_executable is None:
        return True
    return self._tier_is_executable(tier)
```

Rationale:

- Keeps the default behavior centralized.
- Keeps `None` handling out of the control loop.
- Makes tests easier to reason about.

### Phase 3. Stage 1. Action 3: Add Internal Lift Normalizer

Add:

```python
def _lift_to_executable_tier(self) -> bool:
    while not self._is_tier_executable(self._active_tier_state.active_tier):
        if not self._active_tier_state.has_upstairs():
            return False
        self._active_tier_state = self._move_up(self._active_tier_state)
    return True
```

This is the core PO rule in code.

It should be intentionally boring.

### Phase 3. Stage 1. Action 4: Add No-Action Control Mode

Target:

```text
src/state_collapser/tower/control/controller.py
```

Add to `ControlAction`:

```python
NO_AVAILABLE_ACTION = "no_available_action"
```

This is additive and should not disturb existing enum values.

### Phase 3. Stage 1. Action 5: Return Clean No-Action Result

In `ExploitExploreTowerRuntime.step()`, at the start:

```python
if not self._lift_to_executable_tier():
    active_tier_state = self._active_tier_state
    signal = self.signal_state(active_tier_state)
    self._metrics.record(
        active_tier=active_tier_state.active_tier,
        action=ControlAction.NO_AVAILABLE_ACTION,
    )
    return ExploitExploreStepResult(
        decision=ControlAction.NO_AVAILABLE_ACTION,
        active_tier_state=active_tier_state,
        signal_state=signal,
        learner_summary=None,
        transition=None,
    )
```

This should happen before computing `config`, `frozen_context`, or asking the
learner whether training is due.

### Phase 3. Stage 1. Action 6: Pass Predicate Into Controller Decision

When calling `self._controller.decide(...)`, pass:

```python
tier_is_executable=self._is_tier_executable,
```

Important:

- Pass the helper, not the raw optional predicate.
- This means the controller always sees a total function.

### Phase 3. Stage 1. Action 7: Defensive Normalize Before Action Selection

Immediately before:

```python
action = self._learner.behavior_action(...)
```

run:

```python
if not self._lift_to_executable_tier():
    ...
```

Return `NO_AVAILABLE_ACTION` if no executable tier exists.

This second guard handles cases where:

- movement functions produce a new non-executable active tier;
- the downstream predicate is stale between decision and action;
- a caller mutates active state in tests;
- a future controller action skips through an unexpected path.

### Phase 3. Stage 1. Action 8: Recompute Local Variables After Defensive Lift

If the defensive guard lifts the active tier, refresh:

```python
active_tier_state
signal
config
frozen_context
```

before calling:

```python
behavior_action(...)
executor.execute(...)
learner.observe(...)
```

Do not call the learner with stale `active_tier_state`.

### Phase 3. Stage 1. Action 9: Preserve Event Index Semantics

The internal lift-through operation should not increment `event_index`.

Reason:

```text
empty-Out lifting is a validity correction, not a productive environment or
learner event.
```

Only `TRAIN`, `EXPLORE`, and `EXPLOIT_EXECUTE` should continue to advance
events as currently implemented.

### Phase 3. Stage 1. Action 10: Preserve Movement Semantics

Use existing injected movement closures:

```python
self._move_up(...)
```

Do not manually mutate tier numbers in runtime code.

This keeps downstream adapters responsible for updating tier-local state during
movement.

## Phase 4: Wire Plate-Support Example To Real Partition-Tower Availability

Goal:

```text
The package's own exploit/explore example should exercise the real
outgoing-action predicate.
```

### Phase 4. Stage 1. Action 1: Add `_tier_is_executable`

Target:

```text
src/state_collapser/examples/plate_support_env/runtime.py
```

Add method to `PlateSupportExploitExploreRuntime`:

```python
def _tier_is_executable(self, tier: int) -> bool:
    snapshot = self._last_runtime_snapshot
    if snapshot is None:
        return True
    tower = snapshot.partition_tower_view
    if tower is None:
        return True
    positions = snapshot.current_position_at_every_tier
    if tier < 0 or tier >= len(positions):
        return False
    state_cell = positions[tier]
    if state_cell is None:
        return False
    outgoing = tower.outgoing_action_cells(tier, state_cell)
    return bool(outgoing)
```

### Phase 4. Stage 1. Action 2: Pass Predicate Into Runtime

In the `ExploitExploreTowerRuntime(...)` constructor call, add:

```python
tier_is_executable=self._tier_is_executable,
```

### Phase 4. Stage 1. Action 3: Keep Predicate Package-Local

Do not expose this plate-support method in `__all__`.

It is an example binding detail.

### Phase 4. Stage 1. Action 4: Do Not Change Plate-Support Learner

Do not modify `PlateSupportTierLearner.behavior_action(...)` for this work.

The whole point is to avoid putting empty-tier correction inside learners.

## Phase 5: Unit Tests For Signal Selection

Goal:

```text
select_lowest_unclosed_tier(...) skips known non-executable tiers without
changing default behavior.
```

### Phase 5. Stage 1. Action 1: Locate Or Create Test File

Preferred target:

```text
tests/tower/control/test_signals.py
```

If it does not exist, create it.

### Phase 5. Stage 1. Action 2: Test Default Behavior

Test:

```text
without tier_is_executable, deepest unclosed tier is selected exactly as before
```

### Phase 5. Stage 1. Action 3: Test All-Executable Behavior

Test:

```text
tier_is_executable=lambda tier: True
```

Expected:

```text
same selected tier as default
```

### Phase 5. Stage 1. Action 4: Test Deepest Non-Executable Skip

Scenario:

```text
tier 2 unclosed but non-executable
tier 1 unclosed and executable
tier 0 executable
```

Expected:

```text
select_lowest_unclosed_tier(...) == 1
```

### Phase 5. Stage 1. Action 5: Test All Unclosed Non-Executable

Scenario:

```text
all unclosed tiers return False from tier_is_executable
```

Expected:

```text
None
```

### Phase 5. Stage 1. Action 6: Test Closed Non-Executable Does Not Matter

Scenario:

```text
non-executable tier is already closed
another executable tier is unclosed
```

Expected:

```text
executable unclosed tier selected
```

## Phase 6: Unit Tests For Controller Decisions

Goal:

```text
ActiveTierController respects executable-tier filtering while preserving
existing signal behavior.
```

### Phase 6. Stage 1. Action 1: Extend Existing Controller Tests

Target:

```text
tests/tower/control/test_controller.py
```

### Phase 6. Stage 1. Action 2: Test No Descend Into Non-Executable Tier

Scenario:

```text
active tier = 0
deepest known tier = 1
tier 1 unclosed
tier 1 non-executable
tier 0 executable
```

Expected:

```text
decision.action is not DESCEND
```

The exact action may be `EXPLORE`, `EXPLOIT_EXECUTE`, or `TRAIN` depending on
signal configuration. Make the signal configuration force the desired expected
mode cleanly.

### Phase 6. Stage 1. Action 3: Test Descend To Executable Tier Still Works

Use the existing descend test and pass:

```python
tier_is_executable=lambda tier: True
```

Expected:

```text
DESCEND
```

### Phase 6. Stage 1. Action 4: Test Lift Toward Executable Unclosed Tier

Scenario:

```text
active tier = 2
tier 2 signal closed
tier 1 non-executable
tier 0 executable and unclosed
```

Expected:

```text
LIFT
```

This proves the controller can still move upward when the nearest productive
executable locus is above the current tier.

### Phase 6. Stage 1. Action 5: Keep Existing Tests Stable

Existing tests should continue to pass without supplying `tier_is_executable`.

If tests fail because of argument ordering, the API change was not
backward-compatible enough.

## Phase 7: Runtime Tests For Degenerate Guard

Goal:

```text
ExploitExploreTowerRuntime never calls the learner or executor at a
non-executable tier.
```

### Phase 7. Stage 1. Action 1: Extend Runtime Loop Test Doubles

Target:

```text
tests/tower/control/test_runtime_loop.py
```

Extend `StubLearner` with counters:

```python
behavior_action_calls: int = 0
observed_transitions: list[ActiveTierTransition] = field(default_factory=list)
```

or create a new spy learner class for the degenerate tests.

Extend `StubExecutor` with:

```python
execute_calls: int = 0
```

or create a new spy executor.

### Phase 7. Stage 1. Action 2: Add Runtime Factory Predicate Support

Extend the local `_runtime(...)` test helper with:

```python
tier_is_executable: Callable[[int], bool] | None = None
```

Pass it into `ExploitExploreTowerRuntime(...)`.

### Phase 7. Stage 1. Action 3: Test Single-Hop Lift Before Learner Call

Scenario:

```text
active tier = 1
deepest known tier = 1
tier 1 non-executable
tier 0 executable
```

Expected:

```text
runtime.step() does not call behavior_action at tier 1
runtime active tier becomes 0
if an action executes, executor receives active_tier_state.active_tier == 0
```

Depending on the controller signal setup, the returned decision may be
`EXPLORE` or `EXPLOIT_EXECUTE`. The critical assertion is that the learner and
executor are not called at tier `1`.

### Phase 7. Stage 1. Action 4: Test Multi-Hop Lift

Scenario:

```text
active tier = 2
deepest known tier = 2
tier 2 non-executable
tier 1 non-executable
tier 0 executable
```

Expected:

```text
runtime lifts through tier 1 to tier 0
behavior_action is called at most once, at tier 0
executor is called at most once, at tier 0
```

The helper may need tier configs and frozen contexts for tier `2`.

### Phase 7. Stage 1. Action 5: Test Base-Tier No-Action Case

Scenario:

```text
active tier = 0
deepest known tier = 0
tier 0 non-executable
```

Expected:

```text
decision == ControlAction.NO_AVAILABLE_ACTION
transition is None
learner_summary is None
learner.behavior_action_calls == 0
executor.execute_calls == 0
active_tier_state.active_tier == 0
```

### Phase 7. Stage 1. Action 6: Test Predicate-Omitted Backward Compatibility

Existing runtime tests should continue to pass when no predicate is supplied.

No existing caller should need to change unless it wants real degenerate-tier
behavior.

## Phase 8: Plate-Support Integration Tests

Goal:

```text
The package example wires the real partition tower to the generic
executability predicate.
```

### Phase 8. Stage 1. Action 1: Add Focused Predicate Test

Target:

```text
tests/examples/test_plate_support_env_exploit_explore_runtime.py
```

Add a test that:

1. constructs `PlateSupportExploitExploreRuntime`;
2. calls `reset(...)`;
3. asserts `_tier_is_executable(0)` is true for the current initial state;
4. asserts invalid tier indexes return false.

This verifies the method is wired to the live snapshot and tower.

### Phase 8. Stage 1. Action 2: Add Degenerate Guard Test If Cheap

If an easy schema/policy fixture can produce an empty coarse tier, add a test
that proves the runtime lifts out of it.

If this is not cheap, use a monkeypatch-style targeted test:

```python
runtime._tier_is_executable = lambda tier: tier == 0
```

Then force active tier `1` and assert `runtime.step()` does not execute from
tier `1`.

Keep this test focused on the controller invariant, not on plate-support
domain semantics.

### Phase 8. Stage 1. Action 3: Do Not Overfit To BBB

Do not add counterpoint concepts to `state_collapser` tests.

The downstream failure motivates the fix, but the package test should be
generic and example-local.

## Phase 9: Partition-Tower Regression Test

Goal:

```text
Document that empty outgoing action cells at coarse tiers are a valid tower
condition, not a partition-tower bug.
```

### Phase 9. Stage 1. Action 1: Add New Test File

Preferred target:

```text
tests/tower/partition/test_degenerate_tier_queries.py
```

### Phase 9. Stage 1. Action 2: Construct Fully Collapsed Small Graph

Build a graph where:

```text
A -> B
B -> A
```

or another small strongly connected graph whose contraction schema merges all
states at tier `1`.

Expected:

```text
tower.outgoing_action_cells(1, merged_cell) == ()
tower.outgoing_action_cells(0, singleton_cell) != ()
```

### Phase 9. Stage 1. Action 3: Assert Semantics Explicitly

The assertion should make clear:

```text
empty coarse outgoing action cells are valid because all edges are internal at
that tier
```

The control runtime, not the partition tower, is responsible for lifting out
before executable action choice.

## Phase 10: Documentation Updates

Goal:

```text
Reflect the new invariant in docs without rewriting the incoming BBB
diagnosis conversation.
```

### Phase 10. Stage 1. Action 1: Update System Flow Diagram

Target:

```text
docs/design/system_flow/01_001_system_flowcharts_and_control_flow.md
```

Update the exploit/explore runtime flow to include:

```text
empty active-tier Out?
    yes -> lift until nonempty
    no -> learner behavior_action
```

### Phase 10. Stage 1. Action 2: Update Usage Mental Model If Needed

Target:

```text
docs/usage/01_002_tower_runtime_mental_model.md
```

If this doc implies every tower tier is directly executable, add a small note:

```text
Coarse tiers may be address/diagnostic levels rather than executable action
surfaces. Active-tier control lifts through tiers with empty outgoing action
cells.
```

### Phase 10. Stage 1. Action 3: Update CONTRIBUTING Testing Guidance If Needed

Target:

```text
CONTRIBUTING.md
```

If the contributor guide lists focused validation for active-tier or training
changes, add the new tests:

```text
uv run pytest tests/tower/control tests/examples/test_plate_support_env_exploit_explore_runtime.py
```

### Phase 10. Stage 1. Action 4: Update CHANGELOG If Release-Visible

Target:

```text
CHANGELOG.md
```

Add an unreleased entry only if the repo already has an `Unreleased` section.
Otherwise leave this for release prep.

Suggested wording:

```text
- Added active-tier degenerate control handling so exploit/explore runtime
  lifts through tiers whose current state-cell has no outgoing action cells
  instead of asking learners to choose from an empty action surface.
```

### Phase 10. Stage 1. Action 5: Do Not Rewrite Imported Diagnosis

Do not edit:

```text
docs/design/degenerate_tier_control/error_diagnosis_conversation.md
```

unless the PO explicitly requests an appended implementation note.

## Phase 11: Validation

Goal:

```text
Prove the control invariant and protect existing package behavior.
```

### Phase 11. Stage 1. Action 1: Run Focused Control Tests

Run:

```bash
uv run pytest tests/tower/control
```

Expected:

```text
all control tests pass
```

### Phase 11. Stage 1. Action 2: Run Partition Query Tests

Run:

```bash
uv run pytest tests/tower/partition/test_queries_and_lift.py tests/tower/partition/test_degenerate_tier_queries.py
```

If the new partition test is placed elsewhere, adjust command accordingly.

### Phase 11. Stage 1. Action 3: Run Plate-Support Example Tests

Run:

```bash
uv run pytest tests/examples/test_plate_support_env_exploit_explore_runtime.py
```

### Phase 11. Stage 1. Action 4: Run Training Boundary Smoke Tests

Run:

```bash
uv run pytest tests/training tests/examples/test_torch_tensor_boundary_smoke_model.py
```

Reason:

The change touches control runtime but should not affect training/tensorization
surfaces.

### Phase 11. Stage 1. Action 5: Run Full Test Suite

Run:

```bash
uv run pytest
```

Expected:

```text
all tests pass
```

### Phase 11. Stage 1. Action 6: Inspect Git Diff

Run:

```bash
git diff --stat
git diff -- src/state_collapser/tower/control/signals.py
git diff -- src/state_collapser/tower/control/controller.py
git diff -- src/state_collapser/tower/runtime.py
```

Check:

- no learner protocol expansion;
- no executor protocol expansion;
- no tensorization changes;
- no broad refactor;
- no unrelated documentation churn.

## Phase 12: Handoff To `big_boy_benchmarking`

Goal:

```text
Make the downstream fix obvious after upstream support exists.
```

### Phase 12. Stage 1. Action 1: Record BBB Integration Note

After implementation, create or update a short bridge note under:

```text
docs/design/degenerate_tier_control/
```

The note should say:

```text
BBB should pass a tier_is_executable predicate from its counterpoint
tower-control adapter using current_position_at_every_tier and
PartitionTower.outgoing_action_cells(...).
```

### Phase 12. Stage 1. Action 2: Do Not Edit BBB From This Branch Unless Asked

This implementation branch is for `state_collapser`.

Downstream BBB changes should happen in the BBB repo after this package
support lands and is released or pointed to by dependency.

## Phase 13: Completion Criteria

The implementation is complete when:

1. `select_lowest_unclosed_tier(...)` accepts an optional executability
   predicate and skips non-executable tiers.
2. `ActiveTierController.decide(...)` passes that predicate through.
3. `ExploitExploreTowerRuntime` accepts an optional executability predicate.
4. `ExploitExploreTowerRuntime` lifts through non-executable active tiers
   before action selection.
5. `ExploitExploreTowerRuntime` returns `NO_AVAILABLE_ACTION` when tier `0`
   is non-executable.
6. Learner `behavior_action(...)` is never called in the base-tier no-action
   case.
7. Executor `execute(...)` is never called in the base-tier no-action case.
8. Plate-support example runtime wires the predicate to real
   partition-tower outgoing-action cells.
9. Focused tests and full test suite pass.
10. Documentation reflects the invariant without inflating it into a new
    learner/model/training subsystem.

## Phase 14: Commit Guidance

Suggested commit message:

```text
Add degenerate active-tier control guard
```

Suggested commit body:

```text
- skip non-executable tiers during lowest-unclosed selection
- lift active-tier control through empty outgoing-action tiers
- return clean no-action result at base-tier dead ends
- wire plate-support exploit/explore runtime to partition-tower availability
- add focused control and partition regression tests
```

## Final Reminder

The implementation should remain close to the PO's observation:

```text
empty Out means you are in a room with no doors;
walk upstairs until there is a door.
```

Anything substantially more complicated than that should be treated as design
drift unless a test proves it is necessary.
