# Synthetic Blow Review Revision Blueprint

Generated: 2026-05-24

Source review:

- `docs/code_review/02_001_synthetic_blow_full_repo_review.md`

Purpose:

This document converts the completed synthetic-Blow-style full-repo review into
a concrete revision blueprint. It is not yet a Phase.Stage.Action
implementation gameplan. It is the design-level answer to the question:

> Have we made enough decisions to plan the code revisions?

Answer:

Yes. The review has converged enough to produce a hyper-detailed implementation
gameplan. The major decisions are now settled. The only major topic intentionally
deferred is the deeper language/runtime question of whether the Python package
should eventually grow a compiled partition-kernel core. That concern is real,
but the PO explicitly decided to pause direct work on it. Many revisions in this
blueprint still move the codebase in the right direction for such a future
split.

## Readiness Verdict

The review is ready to become an implementation gameplan because it no longer
contains only open-ended criticism. It now contains decisions about:

- lift-aware continuation and bootstrap semantics
- first-class action-mask propagation and masked target computation
- lazy compatibility readouts outside the hot runtime path
- splitting live runtime views from real serializable snapshots
- making loop/pre-image aggregation explicit
- strict Gymnasium action-boundary behavior
- replacing the toy `GymnasiumAdapter` with a real three-world bridge design
- benchmark and regression-test obligations
- preserving Python as the research/control surface for now

The review is not asking for one giant rewrite. It is asking for a sequence of
targeted revisions that make the package honest at the most important
boundaries:

- what did the learner actually train against?
- what actions were actually legal?
- what did the agent actually observe at time `t`?
- did the tower runtime actually update locally?
- is a public abstraction real, or only a name?
- what parts of Gymnasium are environment shell, and what parts belong to
  `state_collapser`?

## Current Ground Truth

This blueprint was checked against the current repository shape.

Relevant current files:

- `src/state_collapser/training/transitions.py`
- `src/state_collapser/training/collectors.py`
- `src/state_collapser/training/learners.py`
- `src/state_collapser/training/reference_loops.py`
- `src/state_collapser/tower/runtime.py`
- `src/state_collapser/tower/snapshot.py`
- `src/state_collapser/tower/partition/tower.py`
- `src/state_collapser/tower/partition/action_layer.py`
- `src/state_collapser/tower/partition/loop_policy.py`
- `src/state_collapser/tower/partition/reward_aggregation.py`
- `src/state_collapser/adapters/gymnasium.py`
- `src/state_collapser/examples/*_env/env.py`
- `src/state_collapser/examples/*_env/training.py`
- `src/state_collapser/examples/tower_depth_probe.py`
- `README.md`
- `CONTRIBUTING.md`

Current confirmed mismatches:

- `TrainingTransition` has `terminated` and `truncated`, but no explicit
  bootstrap or continuation contract.
- `StepCollector` only supplies an action mask when an `action_mask_factory` is
  provided; it does not automatically extract `info["action_mask"]`.
- `StepCollector.collect_step(...)` does not reject a masked-off chosen action.
- `TabularQLearner.update(...)` zeroes bootstrap on `terminated or truncated`.
- `TabularQLearner.update(...)` bootstraps over all target actions, not only
  legal target actions.
- Several per-example training loops duplicate tabular update semantics and
  bootstrap through terminal states.
- `RuntimeSnapshot` is documented as serializable, but carries live graph,
  vista, partition tower, and update-result objects.
- `TowerRuntime._apply_partition_update_result(...)` eagerly rebuilds
  compatibility `QuotientTierView` readouts.
- `PartitionTower.update_with_delta(...)` always captures a full morphism
  domain.
- `ActionPartitionLayer.carry_forward_from(...)` hard-codes
  `LoopPolicy.drop_internal()`.
- `RewardAggregator` already has `sum`, `mean`, `max`, `softmax`, `p_mean`, and
  `p_norm`, but loop/pre-image aggregation is not yet a separate explicit
  surface.
- The toy `GymnasiumAdapter` does not wrap an arbitrary `gymnasium.Env`, is not
  a `gymnasium.Env`, has no spaces, and does not express the three-world
  architecture.
- Several example Gymnasium envs still coerce `int(action)` before validating
  `action_space.contains(action)`.
- Benchmarking exists only as a probe-style utility, not as a real performance
  regression surface.

## Non-Goals For This Revision Series

These are intentionally out of scope for the first implementation response to
the review.

### Do Not Rewrite The Package In Another Language

The language/runtime addendum concluded that Python is not neutral for a
performance-sensitive graph-runtime package, but the PO explicitly paused direct
work on this issue.

This blueprint should therefore:

- keep Python as the research/control surface
- avoid a C/Rust/Zig/C++/Jai rewrite
- avoid introducing a compiled extension
- avoid designing an FFI boundary prematurely
- make data layout cleaner where it naturally supports later compiled work

The later compiled-core question should be documented as future architecture
work, not mixed into this revision series.

### Do Not Solve Automatic Observation-To-State Inference

The Gymnasium discussion clarified that a serious open problem remains:

- Gymnasium gives observations.
- `state_collapser` needs graph state identities.
- In some envs, observation equals state.
- In many serious envs, observation does not equal Markov state.

The first bridge should use explicit hooks. It should not attempt to infer
state identity automatically from arbitrary observations.

The README and `CONTRIBUTING.md` should name this as a future contribution
area.

### Do Not Introduce Neural Model Infrastructure Yet

The review was explicit that no serious model work should be treated as
meaningful until:

- transition semantics are explicit
- masks are first-class
- snapshots are honest
- runtime hot paths are benchmarked

This revision series should harden these surfaces before adding PyTorch model
training abstractions.

### Do Not Over-Engineer Checkpointing Yet

The review notes that checkpointing and run manifests are missing. That is a
real maturity gap, but the first response should focus on:

- value snapshots
- run metrics/benchmark outputs where needed
- enough serialization behavior to prove snapshots are not live mutable views

Full experiment management can follow after the training/runtime semantics are
stable.

## Target Architecture

The target architecture is a stricter separation of five concerns:

1. **Training semantics layer**

   Owns transitions, continuation metadata, masks, target surfaces, and learner
   update contracts.

2. **Partition runtime layer**

   Owns authoritative state/action partition tables, local updates, internal
   edge records, and tower positions.

3. **Runtime view/snapshot layer**

   Separates live convenience views from stable serializable value snapshots.

4. **Environment adapter layer**

   Treats Gymnasium as the environment shell and uses explicit hooks to connect
   observations/actions/info to `state_collapser` graph/tower semantics.

5. **Compatibility/debug/readout layer**

   Provides `QuotientTierView` compatibility, rich debug objects, and legacy
   readouts only when explicitly requested.

The organizing principle is:

> The hot path should use stable ids and partition tables. Rich Python objects,
> compatibility views, and debug payloads should live outside the default hot
> path.

## Decision Inventory

### Decision 1: Continuation Is Package-Native, Not Just Gymnasium Boolean Logic

The review initially identified wrong `terminated`/`truncated` semantics. The
PO refined this: in `state_collapser`, continuation is dictated by lift logic.

The package-level rule:

- termination at tier `i + 1` does not imply the whole process is dead
- a lift may still resolve to forward action at tier `i`
- the learner should train against the actual next decision surface
- the collector/runtime should compute continuation metadata after lift
  resolution
- the learner should not infer this from raw `terminated` and `truncated`

Implementation implication:

- keep `terminated` and `truncated` as external Gymnasium episode facts
- add explicit package-native continuation metadata to `TrainingTransition`
- prefer `bootstrap_allowed` plus an explicit `bootstrap_input` or
  `target_decision_input` over hard-coded learner logic

### Decision 2: Masks Are Part Of The Decision Surface

Action masks are not optional decoration in constrained RL. They define the
legal action surface.

Implementation implication:

- default collectors should extract `info["action_mask"]` if present
- callers may still override with `action_mask_factory`
- selected actions should be checked against source masks before stepping
- target bootstrap should consider only legal target actions
- no-legal-action states should have explicit behavior

### Decision 3: PartitionTower Is Authoritative; QuotientTierView Is Compatibility

The partition tower is the new runtime model. `QuotientTierView` is now a
compatibility/debug/readout format.

Implementation implication:

- default runtime updates should not eagerly rebuild full quotient-tier views
- positions should come from partition tower cell ids
- compatibility readouts should be lazy and explicit
- tests that need quotient tiers should request them
- old APIs can remain temporarily, but should be marked compatibility-facing

### Decision 4: Live Runtime Views And Serializable Snapshots Are Different

The current `RuntimeSnapshot` claims to be serializable but contains live
mutable graph/runtime objects.

Implementation implication:

- introduce a live runtime view object for convenience and backwards migration
- introduce a true serializable value snapshot
- old snapshots from time `t` must not change after runtime advances
- JSON serialization should be possible for the value snapshot once ids are
  normalized
- training transitions should prefer value summaries over live object graphs

### Decision 5: Loop Handling And Pre-Image Aggregation Are Separate Choices

The review identified fake loop-policy configurability. The PO added the
important missing idea: aggregate over pre-image loops with `avg`, `max`, etc.

Implementation implication:

- `LoopPolicy` should decide retention/stutter semantics
- a separate pre-image/internal-edge aggregation surface should decide how
  retained loop data is pushed downstairs
- aggregation choices should include at least `sum`, `mean`, `max`
- p-style or soft aggregation should remain possible
- `max` is especially important for RL because downstream value often wants best
  lift, not average lift

### Decision 6: Gymnasium Bridge Should Be Explicit-Hook Plumbing

The review and PO discussion settled the three-world architecture:

- Gymnasium environment world
- `state_collapser` graph/tower structural world
- training/model world

Implementation implication:

- replace or supersede toy `GymnasiumAdapter`
- implement a small bridge that wraps an arbitrary Gymnasium env
- require explicit hooks for semantic interpretation
- do not infer state identity automatically
- document observation-vs-state as a future contribution problem

### Decision 7: Strict Action Boundaries Are Required

Gymnasium envs should validate actions before coercing to int.

Implementation implication:

- all example envs should call `action_space.contains(action)` before
  conversion
- invalid action values and types should raise consistently
- tests should cover negative, out-of-range, float, and bool behavior

### Decision 8: Benchmarks Must Prove Cost Shape

Fast tests are not enough. The package must prove the local-update cost story.

Implementation implication:

- add a benchmark/profiling surface
- separate partition update without readout from partition update with readout
- benchmark default schema vs no-schema probe
- record enough output to detect regressions
- do not let compatibility readouts hide in the benchmarked hot path

## Proposed Revision Modules

The implementation response should be organized into nine revision modules.

## Revision Module 1: Training Continuation And Bootstrap Semantics

### Goal

Make training targets explicit, lift-aware, and independent of ad hoc learner
interpretations of `terminated` and `truncated`.

### Current State

`TrainingTransition` currently contains:

- `source_input`
- `chosen_action`
- `reward`
- `target_input`
- `terminated`
- `truncated`
- diagnostics and tower metadata

`TabularQLearner.update(...)` currently computes:

```python
bootstrap = 0.0 if (transition.terminated or transition.truncated) else max(
    next_row.values()
)
```

This is wrong for:

- time-limit truncation
- lift-aware continuation
- any future transition where the next bootstrap surface is not the same as the
  raw target input

### Target Design

Add a package-native continuation object.

Candidate surface:

```python
@dataclass(frozen=True, slots=True)
class BootstrapSemantics:
    bootstrap_on_truncation: bool = True

@dataclass(frozen=True, slots=True)
class TransitionContinuation:
    bootstrap_allowed: bool
    bootstrap_input: ActionSelectionInput | None = None
    reason: str = "unspecified"
    source: str = "collector"
```

Then extend `TrainingTransition`:

```python
continuation: TransitionContinuation
```

or, if the first implementation should stay flatter:

```python
bootstrap_allowed: bool
bootstrap_input: ActionSelectionInput | None = None
bootstrap_reason: str = "unspecified"
```

Recommended first implementation:

- use the flatter fields first
- migrate to a nested object later if the surface grows

Reason:

- fewer call-site changes
- easier test updates
- easier for a Phase.Stage.Action plan

### Required Semantics

The collector/runtime should compute:

- `bootstrap_allowed = False` for true environment terminal unless a package
  lift explicitly supplies a continuation surface
- `bootstrap_allowed = True` for non-terminal time-limit truncation by default
- `bootstrap_allowed = False` for truncation only when configured to use
  episodic time-limit semantics
- `bootstrap_input = target_input` in ordinary one-step settings
- `bootstrap_input = lower_or_lift_resolved_input` when lift logic says the next
  valid training surface differs from the raw target input

### Required Files

Add or modify:

- `src/state_collapser/training/transitions.py`
- `src/state_collapser/training/collectors.py`
- `src/state_collapser/training/learners.py`
- `src/state_collapser/training/reference_loops.py`
- `tests/training/test_inputs_and_transitions.py`
- `tests/training/test_collectors.py`
- `tests/training/test_learners_and_reference_loops.py`

Possibly add:

- `src/state_collapser/training/continuation.py`
- `tests/training/test_continuation.py`

### Acceptance Tests

Required tests:

- terminal transition sets `bootstrap_allowed=False`
- non-terminal truncation sets `bootstrap_allowed=True` by default
- configured episodic truncation sets `bootstrap_allowed=False`
- learner uses `transition.bootstrap_input` when present
- learner uses `target_input` when no separate bootstrap input is present
- learner does not inspect raw `terminated/truncated` to decide bootstrap
- transition summary diagnostics record the continuation reason

### Migration Requirements

Existing code that constructs `TrainingTransition` must be updated.

Known call sites:

- `StepCollector.collect_step(...)`
- tests constructing transitions directly
- any example training path that migrates onto generic transitions

## Revision Module 2: First-Class Action Masks

### Goal

Make legal action masks part of the default training contract.

### Current State

`ActionSelectionInput` already has `action_mask`.

`StepCollector` only attaches a mask if `action_mask_factory` exists.

`RlCounterpointEnv` already returns an `action_mask` in `info`.

`TabularQLearner.act(...)` uses source masks for action selection.

`TabularQLearner.update(...)` ignores target masks during bootstrap.

### Target Design

Add a small mask utility surface.

Candidate file:

- `src/state_collapser/training/masks.py`

Candidate functions:

```python
def mask_from_info(info: Mapping[str, object]) -> tuple[bool, ...] | None:
    ...

def legal_actions(mask: tuple[bool, ...] | None, action_count: int) -> tuple[int, ...]:
    ...

def action_is_legal(action: int, mask: tuple[bool, ...] | None) -> bool:
    ...
```

### Collector Behavior

`StepCollector.reset_episode(...)`:

- build initial input
- if `action_mask_factory` is provided, use it
- otherwise inspect `reset_result.info.get("action_mask")`
- attach normalized tuple mask if present

`StepCollector.collect_step(...)`:

- before calling runtime step, validate `decision.chosen_action`
- if source input has mask and action is masked off, raise `ValueError`
- after step, build next input and attach mask from factory or info

### Learner Behavior

`TabularQLearner.act(...)`:

- continue selecting only from legal source actions
- if no legal source actions exist, behavior should be explicit
- recommended first behavior: raise `ValueError`
- do not silently fall back to all actions when a mask exists but all entries
  are false

`TabularQLearner.update(...)`:

- compute bootstrap over legal actions from `bootstrap_input.action_mask`
- if no legal target actions exist, bootstrap should be `0.0`
- diagnostics should record `legal_target_action_count`

### Required Files

Add or modify:

- `src/state_collapser/training/masks.py`
- `src/state_collapser/training/__init__.py`
- `src/state_collapser/training/collectors.py`
- `src/state_collapser/training/learners.py`
- `tests/training/test_masks.py`
- `tests/training/test_collectors.py`
- `tests/training/test_learners_and_reference_loops.py`
- `tests/examples/test_rl_counterpoint_v3_tower_training.py`

### Acceptance Tests

Required tests:

- collector extracts `info["action_mask"]`
- explicit `action_mask_factory` overrides info extraction
- collector rejects masked-off chosen action
- learner action selection never chooses masked-off actions
- learner raises or explicitly handles all-false source mask
- learner bootstrap ignores masked-off target actions
- all-false target mask yields zero bootstrap
- `rl_counterpoint_v3` generic training path uses masks without custom glue

## Revision Module 3: Reference Training Loop Consolidation

### Goal

Eliminate divergent copied Q-learning target semantics in example training
loops.

### Current State

Generic loops exist in:

- `src/state_collapser/training/reference_loops.py`

But several mechanical examples still use local tabular loops:

- `src/state_collapser/examples/articulated_loop_env/training.py`
- `src/state_collapser/examples/cable_parallel_env/training.py`
- `src/state_collapser/examples/dual_arm_manipulation_env/training.py`
- `src/state_collapser/examples/parallelogram_singularity_env/training.py`
- `src/state_collapser/examples/plate_support_env/training.py`

These loops currently duplicate update logic.

### Target Design

Two acceptable approaches:

1. migrate all ordinary example training paths to
   `state_collapser.training.run_reference_online_loop`
2. introduce one shared helper used by all examples

Recommended approach:

- migrate simple tower-aware tabular training to generic reference loop
- leave exploit/explore-specific `PlateSupportTierLearner` alone for now, but
  mark it experimental and test its target semantics separately

### Required Files

Modify:

- `src/state_collapser/examples/articulated_loop_env/training.py`
- `src/state_collapser/examples/cable_parallel_env/training.py`
- `src/state_collapser/examples/dual_arm_manipulation_env/training.py`
- `src/state_collapser/examples/parallelogram_singularity_env/training.py`
- `src/state_collapser/examples/plate_support_env/training.py`
- existing example training tests

Possibly add:

- `src/state_collapser/examples/_shared_training.py`
- `tests/examples/test_training_semantics_shared.py`

### Acceptance Tests

Required tests:

- every `run_tower_training(...)` example path uses the same target semantics
- terminal success target does not bootstrap
- truncation behavior follows configured continuation semantics
- existing training smoke tests still pass

## Revision Module 4: Runtime Views, Serializable Snapshots, And Value Summaries

### Goal

Stop calling live mutable runtime objects serializable.

### Current State

`RuntimeSnapshot` contains:

- live `ExploredGraph`
- live `VistaGraph`
- live `PartitionTower`
- live `TowerUpdateResult`
- compatibility `QuotientTierView` tuple

### Target Design

Introduce two explicit concepts:

1. `LiveRuntimeView`
2. `RuntimeSnapshot`

`LiveRuntimeView`:

- may carry live graph/runtime objects
- is not serializable
- is for internal/debug/convenience use
- replaces the current semantic role of `RuntimeSnapshot`

`RuntimeSnapshot`:

- frozen value object
- contains only stable value data
- suitable for `to_dict()`
- does not carry live graph objects

Candidate value fields:

```python
@dataclass(frozen=True, slots=True)
class RuntimeSnapshot:
    current_base_state: object | None
    current_position_at_every_tier: tuple[object | None, ...]
    tower_depth: int
    discovered_state_count: int
    discovered_edge_count: int
    current_step_reward: float | None
    cumulative_reward: float
    active_control_tier: int | None = None
    last_control_action: str | None = None
    update_changed: bool | None = None
    update_diagnostics: Mapping[str, object] = field(default_factory=dict)
```

Potential issue:

- `current_base_state` may be arbitrary Python object and not JSON-safe

First implementation decision:

- support stable value snapshots as frozen objects
- `to_dict()` should either require JSON-safe ids or stringify arbitrary values
  through a documented serializer
- do not over-promise universal JSON for arbitrary user state objects

### Compatibility Strategy

Avoid breaking every call site at once:

1. Introduce `LiveRuntimeView`.
2. Update `TowerRuntime.reset(...)` and `TowerRuntime.step(...)` to return
   `LiveRuntimeView`.
3. Keep a compatibility alias or migration shim only if tests require it.
4. Update training surfaces to depend on the live view protocol, not on the
   serializable snapshot class.
5. Add `live_view.snapshot()` or `TowerRuntime.snapshot_value()` to produce the
   value snapshot.

Alternative:

- keep return type name `RuntimeSnapshot` for now and introduce
  `SerializableRuntimeSnapshot`

Recommended approach:

- if broad compatibility churn is manageable, rename honestly now
- if not, introduce `LiveRuntimeSnapshot` and deprecate current docstring first

### Required Files

Modify:

- `src/state_collapser/tower/snapshot.py`
- `src/state_collapser/tower/runtime.py`
- `src/state_collapser/training/inputs.py`
- `src/state_collapser/training/transitions.py`
- `src/state_collapser/training/collectors.py`
- tests under `tests/tower`
- tests under `tests/training`
- runtime integration tests under `tests/examples`

### Acceptance Tests

Required tests:

- value snapshot does not contain `ExploredGraph`
- value snapshot does not contain `VistaGraph`
- value snapshot does not contain `PartitionTower`
- old value snapshot does not change after `runtime.step(...)`
- `to_dict()` succeeds for JSON-safe states
- live view remains available for debug/runtime internals
- training transitions store value summaries, not live mutable objects, where
  possible

## Revision Module 5: Lazy Compatibility Readouts And Optional Morphisms

### Goal

Make the default partition runtime hot path local.

### Current State

`TowerRuntime._apply_partition_update_result(...)` always calls:

```python
self._quotient_tiers = self._partition_tower.to_quotient_tier_views()
```

`PartitionTower.update_with_delta(...)` always calls:

```python
morphism_domain = self._capture_morphism_domain()
```

### Target Design

Runtime should store:

- authoritative `PartitionTower`
- current positions from partition cell ids
- last update result

Compatibility quotient-tier views should be built only when requested.

Candidate runtime API:

```python
def compatibility_quotient_tiers(self) -> tuple[QuotientTierView, ...]:
    ...

def snapshot(self, *, include_quotient_readout: bool = False) -> LiveRuntimeView:
    ...
```

Candidate partition API:

```python
def update_with_delta(
    *,
    delta_states: Iterable[State],
    delta_edges: Iterable[BaseEdge],
    current_state: State | None,
    build_morphism: bool = False,
) -> TowerUpdateResult:
    ...
```

### Cache Policy

Compatibility readouts may be cached, but only if:

- cache is invalidated on partition updates
- default hot path does not build readout eagerly
- benchmarks can prove readout disabled/enabled difference

### Required Files

Modify:

- `src/state_collapser/tower/runtime.py`
- `src/state_collapser/tower/partition/tower.py`
- `src/state_collapser/tower/partition/update.py`
- `tests/tower/test_runtime.py`
- `tests/tower/partition/test_incremental_update.py`
- `tests/tower/partition/test_readout.py`
- `tests/examples/test_tower_depth_probe.py`

### Acceptance Tests

Required tests:

- default `TowerRuntime.step(...)` does not call
  `PartitionTower.to_quotient_tier_views()`
- explicit compatibility call returns the same tier data as before
- `build_morphism=False` avoids full morphism-domain capture
- `build_morphism=True` preserves old morphism behavior
- current position at every tier remains available without quotient readout
- tower depth can be computed without full quotient views

## Revision Module 6: Loop Policy And Pre-Image Aggregation

### Goal

Make internal-loop semantics real and separate aggregation from retention.

### Current State

`LoopPolicy` exposes:

- `DROP_INTERNAL`
- `AGGREGATE_INTERNAL`
- `FORMAL_STUTTER`

But `ActionPartitionLayer.carry_forward_from(...)` hard-codes:

```python
LoopPolicy.drop_internal()
```

`RewardAggregator` already supports many aggregation modes, but is direct-image
reward-focused rather than internal/pre-image-loop-specific.

### Target Design

Split concerns:

1. `LoopPolicy`

   Decides whether internal edges are dropped, retained for aggregation, or
   represented as stutters.

2. `PreimageLoopAggregator` or `InternalEdgeAggregator`

   Decides how retained internal/pre-image data contributes to quotient-level
   values.

Candidate file:

- `src/state_collapser/tower/partition/internal_aggregation.py`

Candidate surface:

```python
class InternalAggregationName(StrEnum):
    SUM = "sum"
    MEAN = "mean"
    MAX = "max"
    SOFTMAX = "softmax"
    P_MEAN = "p_mean"
    P_NORM = "p_norm"
    CUSTOM = "custom"

@dataclass(frozen=True, slots=True)
class InternalEdgeAggregator:
    name: InternalAggregationName | str = InternalAggregationName.MAX
    ...
```

The implementation may reuse `RewardAggregator` internally, but the public name
should make it clear that this concerns pre-image/internal-loop data.

### Required Files

Modify:

- `src/state_collapser/tower/partition/action_layer.py`
- `src/state_collapser/tower/partition/loop_policy.py`
- `src/state_collapser/tower/partition/tower.py`
- `src/state_collapser/tower/partition/__init__.py`

Add:

- `src/state_collapser/tower/partition/internal_aggregation.py`
- tests under `tests/tower/partition`

### Acceptance Tests

Required tests:

- `LoopPolicy.aggregate_internal()` survives carry-forward
- `LoopPolicy.formal_stutter()` survives carry-forward
- carry-forward no longer hard-codes `drop_internal`
- internal edge records preserve selected policy name
- `InternalEdgeAggregator.max()` returns max pre-image contribution
- `InternalEdgeAggregator.mean()` returns mean contribution
- aggregator choice is visible in diagnostics

## Revision Module 7: Strict Example Environment Action Boundaries

### Goal

Make every Gymnasium environment validate actions before conversion.

### Current State

These envs call `int(action)` before validation:

- `ArticulatedLoopEnv`
- `CableParallelEnv`
- `DualArmManipulationEnv`
- `ParallelogramSingularityEnv`

`PlateSupportEnv` already validates first.

### Target Design

Every env should use:

```python
if not self.action_space.contains(action):
    raise ValueError(f"Unsupported action index: {action}")
action_index = int(action)
```

### Required Files

Modify:

- `src/state_collapser/examples/articulated_loop_env/env.py`
- `src/state_collapser/examples/cable_parallel_env/env.py`
- `src/state_collapser/examples/dual_arm_manipulation_env/env.py`
- `src/state_collapser/examples/parallelogram_singularity_env/env.py`

Update tests:

- `tests/examples/test_articulated_loop_env_validity.py`
- `tests/examples/test_cable_parallel_env_validity.py`
- `tests/examples/test_dual_arm_manipulation_env_validity.py`
- `tests/examples/test_parallelogram_singularity_env_validity.py`
- possibly `tests/examples/test_plate_support_env_gymnasium.py`
- possibly `tests/examples/test_rl_counterpoint_v3_gymnasium.py`

### Acceptance Tests

For each env:

- `env.step(-1)` raises
- `env.step(ACTION_COUNT)` raises
- `env.step(1.9)` raises
- `env.step(True)` is explicitly accepted or rejected

Recommended bool behavior:

- reject `True` and `False`

Reason:

- bool is a subclass of int in Python
- accepting it silently recreates coercion ambiguity

## Revision Module 8: Real Gymnasium Bridge With Explicit Hooks

### Goal

Replace the toy `GymnasiumAdapter` with a professional bridge that expresses
the three-world architecture.

### Current State

`src/state_collapser/adapters/gymnasium.py` contains `GymnasiumAdapter`, which:

- constructs `RobotConstraintToy`
- is not a `gymnasium.Env`
- does not wrap arbitrary envs
- has no `action_space` or `observation_space`
- is not the serious package integration surface

### Target Design

Introduce a new bridge surface.

Candidate names:

- `StateCollapserGymWrapper`
- `TowerAugmentedEnv`
- `GymnasiumTowerBridge`

Recommended first name:

- `StateCollapserGymWrapper`

Reason:

- clear relationship to external Gymnasium env
- explicit that it wraps rather than replaces
- avoids overclaiming that it is itself the whole tower runtime

### Three-World Contract

The bridge should separate:

1. Gymnasium world

   - `reset`
   - `step`
   - observations
   - actions
   - rewards
   - terminated/truncated

2. `state_collapser` structural world

   - discovered graph
   - local vistas when available
   - partition tower
   - quotient cells
   - lift/cross-tier context

3. training/model world

   - `ActionSelectionInput`
   - masks
   - tower context
   - target/continuation metadata
   - learner updates

### Hook Surface

Candidate config:

```python
@dataclass(frozen=True, slots=True)
class GymnasiumBridgeHooks:
    state_key: Callable[[object, Mapping[str, object]], object]
    action_key: Callable[[object, object, Mapping[str, object]], object]
    action_mask: Callable[[Mapping[str, object], gymnasium.Env], tuple[bool, ...] | None] | None
    edge_labeler: Callable[[object, object, object, Mapping[str, object]], tuple[object, ...]]
    vista_provider: Callable[..., tuple[BaseEdge, ...]] | None = None
```

Need exact signatures in implementation, but the blueprint decision is:

- these hooks are explicit
- state identity is not inferred
- action identity is not inferred for complex spaces
- action mask is optional
- edge/contraction labels are package-specific
- vista/model providers are optional and enable richer than empirical graph
  discovery

### Operating Modes

Mode 1: empirical opaque Gymnasium env

- wrapper only sees realized transitions
- discovered graph grows from sampled `(s, a, s_next)`
- no unseen outgoing edges
- tower updates only from discovered edges

Mode 2: transparent Gymnasium env with helper hooks

- env or hooks expose legal actions and local transition model
- wrapper can construct richer local vistas
- tower can update with more complete local outgoing information

Mode 3: package-native env/runtime

- current example runtimes may stay package-native
- bridge is not required for examples already exposing tower runtimes

### Current Adapter Treatment

Options:

1. delete `GymnasiumAdapter`
2. rename it to `RobotConstraintRuntimeAdapter`
3. keep it as legacy smoke adapter but remove any claim that it is the primary
   Gymnasium bridge

Recommended:

- introduce the new bridge
- rename current toy adapter to `RobotConstraintRuntimeAdapter`
- keep tests for toy adapter under the new name
- add new tests for real Gymnasium bridge

### Required Files

Modify:

- `src/state_collapser/adapters/gymnasium.py`
- `tests/adapters/test_gymnasium_adapter.py`
- `README.md`
- `CONTRIBUTING.md`

Possibly add:

- `src/state_collapser/adapters/gymnasium_hooks.py`
- `tests/adapters/test_state_collapser_gym_wrapper.py`

### Acceptance Tests

Required tests:

- wrapper exposes `action_space` and `observation_space` from wrapped env
- wrapper reset returns Gymnasium five-compatible reset surface
- wrapper step returns Gymnasium five-tuple
- wrapper attaches runtime/tower metadata in info
- wrapper uses `state_key` hook to build discovered graph nodes
- wrapper uses `action_key` hook to build edge identities
- wrapper extracts action masks through hook
- wrapper records transition labels through edge labeler
- opaque env mode discovers only realized transitions
- transparent/vista hook mode can add richer local outgoing edges

### Documentation Requirements

README TODO should add:

- explicit hook-based Gymnasium bridge
- observation-vs-state inference as future contribution area

`CONTRIBUTING.md` should add:

- guidance for contributors adding Gymnasium integrations
- warning that observation identity and graph-state identity may differ
- examples of acceptable hooks

## Revision Module 9: Benchmark And Performance Regression Surface

### Goal

Prove the local-update runtime story and prevent compatibility readouts from
silently re-entering the hot path.

### Current State

`tower_depth_probe` is useful but structural. It is not enough to prove runtime
cost shape.

### Target Design

Add a benchmark namespace.

Candidate package path:

- `src/state_collapser/benchmarks`

Candidate scripts:

- `src/state_collapser/benchmarks/tower_runtime_bench.py`
- `src/state_collapser/benchmarks/partition_update_bench.py`

Alternative:

- `scripts/benchmark_tower_runtime.py`

Recommended:

- start with package module under `state_collapser.benchmarks`
- provide CLI entry point through `python -m`
- avoid adding heavyweight benchmark framework unless needed

### Required Benchmarks

Minimum benchmark table:

| benchmark | metric |
|---|---|
| no-schema flat probe | steps/sec |
| default schema probe | steps/sec |
| partition update without readout | updates/sec |
| partition update with readout | updates/sec |
| full rebuild legacy tower | updates/sec |

Additional useful metrics:

- discovered states
- discovered edges
- tower depth
- schema assignment count
- state cell merge count
- action collection merge count
- internal edge count
- readout requested yes/no
- morphism requested yes/no

### Required Files

Add:

- `src/state_collapser/benchmarks/__init__.py`
- `src/state_collapser/benchmarks/tower_runtime_bench.py`
- `tests/benchmarks/test_tower_runtime_bench.py`

Possibly add:

- `docs/design/synthetic_blow_revisions_01/benchmark_notes.md` after
  implementation

### Acceptance Tests

Required tests:

- benchmark module imports
- benchmark runs with tiny step count
- benchmark returns structured result
- readout-disabled benchmark does not request quotient readout
- readout-enabled benchmark does request quotient readout
- output includes enough fields to compare cost shape

## Documentation Revision Requirements

### README

Update TODOs to include:

- hook-based Gymnasium bridge
- observation-vs-state interface as future work
- benchmark surface for proving local update cost
- live view vs serializable snapshot hardening
- training transition semantics and mask hardening

Do not make README sound like these are complete before implementation.

### CONTRIBUTING

Add guidance on:

- how to add a Gymnasium environment integration
- when observation can be treated as state
- when a `state_key` hook is required
- how to expose action masks
- how to label transitions for contraction schemas
- why hot-path benchmarks matter

### Code Review Report

The code review report should remain as a diagnosis record. Do not rewrite it
into implementation docs. This blueprint now serves as the design response.

## Test Strategy

The implementation gameplan should be test-first where possible.

### New Test Groups

Add or expand:

- `tests/training/test_continuation.py`
- `tests/training/test_masks.py`
- `tests/tower/test_runtime_snapshot_values.py`
- `tests/tower/test_runtime_lazy_readouts.py`
- `tests/tower/partition/test_internal_aggregation.py`
- `tests/adapters/test_state_collapser_gym_wrapper.py`
- `tests/examples/test_env_action_boundaries.py`
- `tests/benchmarks/test_tower_runtime_bench.py`

### Existing Test Groups To Update

Update:

- `tests/training/test_collectors.py`
- `tests/training/test_inputs_and_transitions.py`
- `tests/training/test_learners_and_reference_loops.py`
- `tests/tower/test_snapshot.py`
- `tests/tower/test_runtime.py`
- `tests/tower/partition/test_incremental_update.py`
- `tests/tower/partition/test_loop_policy.py`
- `tests/tower/partition/test_readout.py`
- all example tower-training tests
- old Gymnasium adapter tests

### Required Full Validation

Every implementation phase should end with:

```bash
uv run ruff check .
uv run mypy src
uv run pytest
```

After benchmark module exists:

```bash
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only
```

## Risk Register

### Risk 1: Snapshot Rename Causes Large Churn

Mitigation:

- introduce `LiveRuntimeView` first
- preserve compatibility alias temporarily if necessary
- update training protocols to accept a runtime-view protocol rather than a
  concrete class

### Risk 2: Lazy Readout Breaks Existing Tests

Mitigation:

- add explicit `compatibility_quotient_tiers()` call
- update tests that truly need readout
- keep readout cached but lazy

### Risk 3: Mask Enforcement Breaks Existing Smoke Runs

Mitigation:

- fix env masks and learner action choices first
- make all-false source mask behavior explicit
- update tests to expect errors where actions are invalid

### Risk 4: Lift-Aware Bootstrap Surface Is Under-Specified

Mitigation:

- implement ordinary Gymnasium continuation first
- add field names that can support lift-aware override
- write tests for the simple case now
- add one explicit lift-aware synthetic test using a manually supplied
  `bootstrap_input`

### Risk 5: Gymnasium Bridge Becomes Too Magical

Mitigation:

- require explicit hooks
- document opaque vs transparent modes
- refuse to infer state identity from arbitrary observations
- keep automatic helpers as convenience functions, not hidden behavior

### Risk 6: Loop Aggregation Collapses Into Reward Aggregation Confusion

Mitigation:

- keep public name specific to internal/pre-image loops
- reuse lower-level aggregation implementation if useful
- test policy retention separately from aggregation values

### Risk 7: Benchmark Tests Become Flaky

Mitigation:

- unit tests should verify benchmark surfaces and flags, not strict timing
- performance thresholds should be optional/local at first
- store structured benchmark output before enforcing budgets

## Implementation Order Recommendation

This is not yet a gameplan, but the implementation order should probably be:

1. strict action boundaries in example envs
2. action-mask utilities and collector propagation
3. continuation/bootstrap transition contract
4. learner masked/continuation-aware update semantics
5. example training loop consolidation
6. live view vs value snapshot split
7. lazy compatibility readouts and optional morphisms
8. loop policy carry-forward and internal aggregation
9. hook-based Gymnasium bridge
10. benchmark surface
11. README and `CONTRIBUTING.md` updates

Rationale:

- start with small correctness fixes
- then harden training semantics
- then alter runtime surfaces
- then add new adapter and benchmark surfaces
- update docs only once the code direction is real

Alternative ordering:

- If runtime performance is the immediate priority, move lazy readouts and
  benchmarks before example training consolidation.

## Completion Definition

This revision series is complete when:

- training transitions carry explicit continuation/bootstrap semantics
- learners no longer infer bootstrap from raw `terminated/truncated`
- action masks propagate automatically from Gymnasium info where present
- learners select and bootstrap only over legal actions
- simple example training paths share one target semantics implementation
- live runtime views are not called serializable snapshots
- value snapshots are stable across runtime mutation
- partition runtime does not eagerly build compatibility readouts by default
- morphism capture is optional
- loop policy choices survive carry-forward
- internal/pre-image aggregation has an explicit surface
- all example envs validate actions before conversion
- a real hook-based Gymnasium bridge exists or the toy adapter is clearly
  renamed and superseded
- README and `CONTRIBUTING.md` document the observation-vs-state future problem
- benchmark tooling can measure local update cost with readout disabled and
  enabled
- `uv run ruff check .`, `uv run mypy src`, and `uv run pytest` pass

## Final Blueprint Verdict

The review has made enough decisions to proceed to an implementation gameplan.

The most important architectural decision is that the package must stop letting
rich Python convenience objects define core runtime semantics. The immediate
answer is not a language rewrite. The immediate answer is to clarify boundaries:

- training semantics belong in explicit transition metadata
- masks belong in the decision surface
- partition tables are authoritative runtime state
- quotient views are compatibility readouts
- live views are not serializable snapshots
- Gymnasium is the environment shell, not the graph/tower ontology
- benchmark results must prove the local-update story

That is enough to plan implementation in Phase.Stage.Action detail.
