# Degenerate Tier Control Blueprint

Date: 2026-05-30

Status: implementation blueprint, not yet executed

Source diagnosis:

- `docs/design/degenerate_tier_control/error_diagnosis_conversation.md`
- `src/state_collapser/tower/runtime.py`
- `src/state_collapser/tower/control/controller.py`
- `src/state_collapser/tower/control/signals.py`
- `src/state_collapser/tower/partition/tower.py`
- `src/state_collapser/examples/plate_support_env/runtime.py`

## Purpose

This blueprint describes the small but important controller correction exposed
by the downstream `big_boy_benchmarking` counterpoint evaluation.

The observed failure is not primarily a reward failure, model failure, or
scientific negative result about tower learning. It is a generic active-tier
control failure:

```text
the controller can descend into a coarsened tier whose current state-cell has
no outgoing action cells, then ask the learner to choose an action there.
```

The correct rule is simple:

```text
if the current active tier has empty Out, move to a finer tier.
Repeat until Out is nonempty.
Only if tier 0 also has empty Out is the problem locally trivial/dead-ended.
```

This should be implemented as a small controller/runtime invariant in
`state_collapser`, not as a large new learner subsystem and not only as a
counterpoint-specific fix in `big_boy_benchmarking`.

## Attribution

The Project Owner identified the conceptual fix after reviewing the
`big_boy_benchmarking` readout:

```text
if you find yourself in the degenerate case, hop up one tier
```

The embedded downstream diagnosis established the concrete failure path:

```text
non-empty tower schema
    -> active coarse tier has zero outgoing action cells
    -> BBB learner sees empty action vocabulary
    -> BBB learner returns sentinel -1
    -> BBB lift/resolve executor logs invalid_action_index
    -> no concrete environment step
    -> zero reward and zero training
```

This blueprint preserves the PO's simplification: the durable package fix
should be a direct empty-`Out` guard, not a heavy replacement of the training
surface.

## Current Repo Reality

### Existing active-tier controller

`ActiveTierController` lives in:

```text
src/state_collapser/tower/control/controller.py
```

Its `decide(...)` method currently chooses among:

- `LIFT`
- `DESCEND`
- `TRAIN`
- `EXPLORE`
- `EXPLOIT_EXECUTE`

The decision is based on productive-learning signals:

- visit count
- TD error
- success/failure rate
- reward residual
- lowest unclosed tier
- training due
- epsilon/exploration pressure

It does not currently know whether the active tier has any outgoing action
cells.

### Existing lowest-unclosed selection

`select_lowest_unclosed_tier(...)` lives in:

```text
src/state_collapser/tower/control/signals.py
```

It scans from the deepest known tier down to tier `0` and returns the
highest-indexed unclosed tier. This is the right direction for "go as coarse as
possible while productive work remains open", but it currently ignores whether
the tier is executable.

That means a fully collapsed tier with no outgoing action cells can still be
selected as the target tier simply because it is unvisited and therefore
unclosed.

### Existing runtime execution point

`ExploitExploreTowerRuntime.step()` lives in:

```text
src/state_collapser/tower/runtime.py
```

For `EXPLORE` and `EXPLOIT_EXECUTE`, it currently does:

```text
action = learner.behavior_action(active_tier_state.tier_state, mode=mode)
transition = executor.execute(active_tier_state, action, ...)
learner.observe(transition, ...)
```

There is no preflight check that the active tier's current state has any
available outgoing actions.

### Existing outgoing-action query

`PartitionTower` already exposes the exact local query needed:

```text
PartitionTower.outgoing_action_cells(tier, state_cell_id)
```

This lives in:

```text
src/state_collapser/tower/partition/tower.py
```

It returns the abstract decision action cells available from a state cell at
one tier. If the returned tuple is empty, that tier-state is not an executable
decision locus.

### Existing example integration

`PlateSupportExploitExploreRuntime` constructs an
`ExploitExploreTowerRuntime` in:

```text
src/state_collapser/examples/plate_support_env/runtime.py
```

It already tracks:

- the latest `LiveRuntimeView`;
- `current_position_at_every_tier`;
- the current `partition_tower_view`;
- movement closures `move_down(...)` and `move_up(...)`.

This means the example runtime can cheaply answer:

```text
for tier i, does the current tier position have outgoing action cells?
```

using the current snapshot and partition tower.

## Core Mathematical / Runtime Invariant

Let `C_i(s)` denote the active state-cell at tier `i` containing the current
base state. Let:

```text
Out_i(C_i(s))
```

be the tier-`i` outgoing action-cell collection.

The invariant is:

```text
The learner may only be asked to choose an executable active-tier action at a
tier i when Out_i(C_i(s)) is nonempty.
```

If:

```text
Out_i(C_i(s)) = empty
```

and:

```text
i > 0
```

then tier `i` is a pass-through or lift-through tier for the current decision.
The controller should move to tier `i - 1`.

If:

```text
Out_0(C_0(s)) = empty
```

then the base graph itself has no currently executable outgoing action from the
current state. That is not a tower-control problem. It is a terminal/dead-end,
undiscovered-vista, or trivial local graph condition.

## Why The Fix Is Not A Learner Fix

A learner answers:

```text
given this state and this action vocabulary, which action should I choose?
```

The learner should not be responsible for deciding:

```text
is the active tier an executable decision surface?
```

That question belongs to the tower controller/runtime because it depends on
the tower's nested state/action partition structure.

In the failing downstream run, the learner received an empty vocabulary and
returned `-1`. That sentinel was then reported as `invalid_action_index`. The
real upstream condition was not "the learner chose an invalid action"; it was:

```text
the learner was asked to choose at a tier where no action existed.
```

The implementation should prevent that call.

## Why A Single Local Guard Is Almost Enough But Not Quite

The intuitive fix is:

```text
if Out(active tier) is empty:
    active tier -= 1
```

That is the correct control law.

However, the current runtime has two separate places where the degenerate tier
can matter:

1. target-tier selection;
2. immediate action execution.

If only the immediate execution path is guarded, the controller may still
choose to descend back into the same degenerate tier on the next control step,
because `select_lowest_unclosed_tier(...)` still sees that tier as unclosed.

Therefore the implementation should be small but two-sided:

```text
1. Skip non-executable tiers when selecting the lowest unclosed tier.
2. Before action selection, lift out of any currently non-executable tier.
```

This avoids both:

```text
descend -> lift -> descend -> lift
```

oscillation and:

```text
empty vocabulary -> learner returns sentinel -> executor failure
```

## Terminology

### Executable Tier-State

A tier-state is executable when the current state-cell at that tier has at
least one outgoing action cell.

For the partition tower:

```text
executable(i)
    := current_position_at_every_tier[i] is not None
       and bool(tower.outgoing_action_cells(i, current_position_at_every_tier[i]))
```

### Degenerate Tier-State

A tier-state is degenerate for action selection when:

```text
not executable(i)
```

The common nontrivial case is:

```text
i > 0
and all outgoing concrete edges have become internal loops in the coarse cell
```

### Trivial / Dead-End Base State

The only true terminal edge case for this guard is:

```text
i = 0
and Out_0(current singleton/base state) is empty
```

This means there is no currently known executable outgoing action at the base
tier. The control runtime should not invent an action or ask the learner for
one.

## Design Principle

The fix should preserve the package's current division of responsibilities:

```text
PartitionTower:
    owns state/action partition data and outgoing-action queries.

ExploitExploreTowerRuntime:
    owns active-tier control step orchestration.

ActiveTierController:
    owns generic control decisions from signals/configs.

TierLearner:
    owns action choice only after a valid action surface exists.

LiftResolveExecutor:
    owns environment-specific realization of an abstract/chosen action.
```

The new invariant belongs at the controller/runtime boundary.

## Proposed API Shape

### Add A Lightweight Executability Predicate

Add an optional predicate to `ExploitExploreTowerRuntime`:

```python
tier_is_executable: Callable[[int], bool] | None = None
```

Semantics:

```text
tier_is_executable(i) returns whether tier i is currently a valid action
selection locus for the current runtime state.
```

Default:

```text
lambda tier: True
```

The default preserves existing behavior for callers that do not yet provide a
tower-backed predicate.

Why tier-index only instead of `(tier, state)`?

The active runtime already treats the current base state as ambient. Example
and downstream adapters have access to the latest snapshot and can answer
executability by tier index:

```text
positions = latest_snapshot.current_position_at_every_tier
state_cell = positions[tier]
return bool(partition_tower.outgoing_action_cells(tier, state_cell))
```

This keeps the controller signature small and avoids forcing generic control
code to understand `StateCellId`.

### Add Optional Predicate To Controller Decision

Extend `ActiveTierController.decide(...)` with:

```python
tier_is_executable: Callable[[int], bool] | None = None
```

The controller should pass this into `select_lowest_unclosed_tier(...)`.

Default:

```text
all tiers are executable
```

This preserves current tests and behavior unless a runtime explicitly supplies
the predicate.

### Extend Lowest-Unclosed Selection

Update `select_lowest_unclosed_tier(...)` to accept:

```python
tier_is_executable: Callable[[int], bool] | None = None
```

The scan should skip non-executable tiers:

```python
for tier_index in range(deepest_known_tier, -1, -1):
    if tier_is_executable is not None and not tier_is_executable(tier_index):
        continue
    ...
```

This means an unvisited but action-empty coarse tier will no longer attract the
controller downward.

### Add Runtime Normalization Before Action Selection

Add a private method to `ExploitExploreTowerRuntime`:

```python
def _lift_to_executable_tier(self) -> bool:
    while not self._tier_is_executable(self._active_tier_state.active_tier):
        if not self._active_tier_state.has_upstairs():
            return False
        self._active_tier_state = self._move_up(self._active_tier_state)
    return True
```

Call it before choosing a learner action.

Recommended placement:

1. At the start of `step()`, before controller decision, normalize the current
   active tier.
2. Immediately before `behavior_action(...)`, run the same normalization again
   as a defensive guard.

The second guard protects against stale or downstream-specific movement
behavior.

### Add A Clean No-Action Control Result

If `_lift_to_executable_tier()` reaches tier `0` and tier `0` is still not
executable, the runtime should not call:

```text
learner.behavior_action(...)
executor.execute(...)
learner.observe(...)
```

Add:

```python
ControlAction.NO_AVAILABLE_ACTION = "no_available_action"
```

When base tier has no available action, return:

```text
ExploitExploreStepResult(
    decision=ControlAction.NO_AVAILABLE_ACTION,
    active_tier_state=current_state,
    signal_state=signal,
    learner_summary=None,
    transition=None,
)
```

Do not record a fake learner failure. Do not create an artificial transition.
Do not call the executor.

This keeps the behavior honest:

```text
the control runtime had no action surface
```

rather than:

```text
the learner chose an invalid action
```

## Proposed Internal Control Flow

The runtime's `step()` should become logically:

```text
step():
    if not lift_to_executable_tier():
        return no_available_action

    active_tier_state = current active tier
    signal = signal_state(active_tier_state)
    config = tier config for active tier
    frozen_context = frozen context for active tier

    decision = controller.decide(
        ...,
        tier_is_executable=tier_is_executable,
    )

    if decision is LIFT:
        move up one tier

    elif decision is DESCEND:
        move down one tier
        # Because controller skipped non-executable tiers, this should normally
        # be executable or on the path toward an executable tier.

    elif decision is TRAIN:
        train

    else:
        if not lift_to_executable_tier():
            return no_available_action
        action = learner.behavior_action(...)
        transition = executor.execute(...)
        learner.observe(...)
```

The core guard remains the simple PO rule:

```text
empty Out -> up one tier
```

The surrounding changes only ensure the existing controller does not keep
targeting the empty tier.

## Plate-Support Example Wiring

`PlateSupportExploitExploreRuntime` should pass a concrete predicate into
`ExploitExploreTowerRuntime`.

Add a private method:

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

Then construct:

```python
ExploitExploreTowerRuntime(
    ...,
    tier_is_executable=self._tier_is_executable,
)
```

This makes the package example exercise the real invariant with the real
partition tower.

## BBB / Downstream Handoff

`big_boy_benchmarking` should eventually pass the same predicate from its
counterpoint tower-control adapter.

The downstream predicate may be stricter than the package default:

```text
tier is executable if:
    outgoing_action_cells(tier, current_cell) is nonempty
    and at least one action can be lifted/resolved to a legal concrete action
```

For the immediate failure, checking `outgoing_action_cells(...)` is sufficient,
because the artifact rows show:

```text
candidate_count = 0
abstract_action = -1
```

meaning BBB never reached a real action-cell lift candidate.

The downstream artifact taxonomy should later distinguish:

```text
no_available_tier_action
```

from:

```text
invalid_action_index
```

But that is a BBB artifact/readout improvement, not required for the upstream
control invariant.

## What Not To Build

Do not build a new learner abstraction just to handle empty action sets.

Do not require every `TierLearner` to expose an action vocabulary.

Do not push `PartitionTower` objects into learner code.

Do not make the executor responsible for deciding whether a tier is executable.

Do not turn this into a new action taxonomy or planning subsystem.

Do not make tensorization, Torch, replay buffers, or model surfaces part of
this fix.

The whole point is to keep the fix close to:

```text
empty Out -> lift
```

## Test Blueprint

### Unit Tests For `select_lowest_unclosed_tier`

Add tests in:

```text
tests/tower/control/test_signals.py
```

Cases:

1. With no predicate, current behavior is unchanged.
2. With all tiers executable, current behavior is unchanged.
3. If deepest tier is unclosed but non-executable, selection skips it.
4. If all unclosed tiers are non-executable, returns `None`.
5. If tier `2` is non-executable and tier `1` is executable/unclosed, returns
   tier `1`.

### Unit Tests For `ActiveTierController`

Extend:

```text
tests/tower/control/test_controller.py
```

Cases:

1. Controller descends toward deepest unclosed executable tier.
2. Controller does not descend toward a non-executable unclosed tier.
3. Controller lifts if current tier is above the nearest unclosed executable
   tier.
4. Existing train/explore/exploit tests still pass with the default predicate.

### Runtime Tests For Degenerate Guard

Extend:

```text
tests/tower/control/test_runtime_loop.py
```

Add spy learner/executor objects that record calls.

Cases:

1. Current active tier is non-executable and tier `0` is executable.

Expected:

```text
runtime lifts before calling learner
learner is called only after active tier becomes executable
executor receives executable tier state
```

2. Current active tier is non-executable, tier `1` is non-executable, tier `0`
   is executable.

Expected:

```text
runtime lifts repeatedly to tier 0
learner is not called at tiers 2 or 1
```

3. Tier `0` is non-executable.

Expected:

```text
decision == ControlAction.NO_AVAILABLE_ACTION
transition is None
learner.behavior_action was not called
executor.execute was not called
active tier remains 0
```

4. Predicate omitted.

Expected:

```text
all existing behavior remains unchanged
```

### Integration Test For Plate Support

Extend:

```text
tests/examples/test_plate_support_env_exploit_explore_runtime.py
```

The test should verify the example runtime passes a real executability
predicate and does not call action selection at a known empty tier.

If constructing a natural empty-tier plate-support case is awkward, use a
targeted monkeypatch of `runtime._tier_is_executable(...)` or a custom
contraction policy/schema that collapses the coarse tier. The test should be
small and focused on the control invariant, not on plate-support physics.

### Partition-Tower Regression Test

A partition-level test can document the condition that motivates the guard:

```text
coarse tier may have empty outgoing action cells
while finer tier has nonempty outgoing action cells
```

This belongs in:

```text
tests/tower/partition/test_queries_and_lift.py
```

or a new:

```text
tests/tower/partition/test_degenerate_tier_queries.py
```

The test should not assert that empty coarse tiers are wrong. They are valid
quotient structures. The regression is only that the active controller must not
execute from them.

## Backward Compatibility

The change should be backward-compatible if:

- `tier_is_executable` defaults to `None` / all tiers executable;
- `ActiveTierController.decide(...)` gives the new parameter a default;
- `select_lowest_unclosed_tier(...)` gives the new parameter a default;
- `ControlAction.NO_AVAILABLE_ACTION` is additive;
- existing tests are adjusted only where they enumerate all possible actions.

No public partition-tower query should be removed or renamed.

No learner protocol method should be changed.

No executor protocol method should be changed.

## Documentation Updates After Implementation

After the implementation is complete, update:

- `docs/design/degenerate_tier_control/error_diagnosis_conversation.md` only if
  we intentionally append an implementation note; do not rewrite the imported
  conversation.
- `docs/design/system_flow/01_001_system_flowcharts_and_control_flow.md` to
  show the new empty-`Out` guard in the exploit/explore flow.
- `docs/usage/01_002_tower_runtime_mental_model.md` if it currently implies
  all tiers are executable action surfaces.
- `CONTRIBUTING.md` if contributor testing guidance should include the new
  control tests.
- `CHANGELOG.md` if this ships as a release-visible behavior fix.

## Expected Impact On BBB

After this is implemented and BBB wires the predicate:

```text
non-empty tower arms should no longer fail before the first concrete step
solely because the active tier has zero outgoing action cells.
```

The benchmark may still reveal:

- poor structured-schema quality;
- bad lift candidate selection;
- legal-mask failures;
- weak learning;
- no tower advantage.

Those would be real next-layer results. The current `invalid_action_index`
caused by empty active-tier vocabulary should disappear or be replaced by a
clean `no_available_action` only in the genuinely trivial base-tier case.

## Open Implementation Details

### Should The Runtime Normalize Before Or After Controller Decision?

Recommendation:

```text
both, but cheaply
```

Normalize once at the start of `step()` so stale active tiers are corrected
before signal selection. Normalize again before learner action selection as a
last-mile guard.

### Should Lifting Through Empty Tiers Count As A `LIFT` Decision?

Recommendation:

```text
not for the normalized internal loop
```

The empty-`Out` lift is not a learned or strategic control decision. It is a
validity correction. The returned decision should describe the final productive
step when one occurs.

If detailed metrics are later needed, add a separate diagnostic counter such
as:

```text
degenerate_tier_lift_count
```

Do not block the minimal fix on that metric.

### Should Training Be Allowed At A Degenerate Tier?

Recommendation:

```text
no, not by default
```

The PO rule says if the tier is degenerate, hop up. Training at a tier with no
current outgoing action surface is at best ambiguous in this first-release
control regime.

### Should The Predicate Know Concrete Legal Masks?

Recommendation:

```text
state_collapser default: no
downstream adapter: may be stricter
```

The package invariant is about the tower action surface:

```text
Out_i(C_i(s)) nonempty
```

BBB can additionally decide that a tier is not executable if no outgoing action
cell has a concrete legal lift candidate.

## Acceptance Criteria

The implementation is complete when:

1. `ExploitExploreTowerRuntime` cannot call `learner.behavior_action(...)` at a
   tier marked non-executable.
2. `select_lowest_unclosed_tier(...)` skips non-executable tiers when a
   predicate is supplied.
3. A current active tier with empty `Out` lifts to the nearest finer executable
   tier.
4. Tier `0` with empty `Out` returns a clean no-action control result.
5. Existing exploit/explore runtime tests still pass.
6. New tests prove the learner and executor are not called in the base-tier
   no-action case.
7. Plate-support example wiring demonstrates the package-native predicate
   using the real partition tower.
8. No training, tensorization, learner, or executor protocol is broadened
   unnecessarily.

## Final Design Summary

The implementation should be intentionally small:

```text
PartitionTower already knows Out.
Runtime asks whether the active tier's Out is empty.
If empty and not tier 0, runtime moves up.
Controller stops targeting empty tiers.
Learner is called only once a nonempty action surface exists.
```

This turns the downstream failure from a mysterious `invalid_action_index`
artifact into the obvious tower-control law it should have been from the
beginning:

```text
do not execute in a quotient cell with no outgoing doors;
walk upstairs until there is a door.
```
