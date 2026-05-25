# Fiber-Conditioned Training Spine Blueprint

## Status

Blueprint.

This document translates the end-state of
`01_001_rl_framework_maturity_and_tower_training_spine_discussion.md` into a
concrete architecture target.

It is not an implementation gameplan.

It should be followed by an ultra-detailed Phase.Stage.Action implementation
gameplan only after Project Owner review.

## Source Discussion

The source discussion began with a broad question about RL framework maturity:

- how much `state_collapser` should resemble RLlib
- how much it should resemble Stable-Baselines3
- how much neural training infrastructure should be owned by this package
- how the quotient tower changes ordinary RL training surfaces

The discussion ended somewhere more precise.

The current architecture target is not:

```text
build a generic RL framework
```

and not:

```text
delegate the package's semantics to an external RL framework
```

The architecture target is:

```text
promote the already-existing tower/query/training/control fragments into a
first-class fiber-conditioned training spine.
```

## Project Owner Attribution

This blueprint is substantially shaped by Project Owner corrections and
realignments.

The Project Owner introduced or forced the following key conclusions:

- `state_collapser` should not become a bad clone of RLlib or
  Stable-Baselines3.
- Most ordinary RL framework maturity concerns are standardized enough to borrow
  from existing practice.
- The package-specific design problem is the tower/fiber semantics.
- The tower moves downward as tier index increases.
- `G_t^0` is the total discovered transition graph, not "the base" in a global
  sense.
- Given a tower map `G_t^i -> G_t^{i+1}`, training at tier `i` after freezing
  tier `i+1` means training inside the path fiber over the frozen coarser
  behavior.
- The lift is not an extra hidden mechanism; it is the fiber of the already
  constructed projection on paths.
- The codebase already contains more of the needed structure than the earlier
  high-level discussion assumed.
- The blueprint and the engineer-facing documentation should be designed in
  parallel, because documentation pressure exposes API usability failures.

Codex's contribution in the source discussion was to inspect the repo, revise
its earlier framing, and identify the missing semantic bridge between the
existing partition tower runtime and the existing research training surfaces.

## One-Sentence Target

`state_collapser` should provide a package-native surface that turns frozen
coarser quotient behavior into a finer-tier training problem by constructing the
path fiber over that behavior and exposing it through ordinary, engineer-owned
training components.

## Core Architecture Diagram

```text
Existing discovered total graph and partition tower
    -> choose adjacent tiers i -> i+1
        -> freeze behavior at coarser tier i+1
            -> construct PathFiber over that frozen behavior
                -> expose FiberConditionedStage at finer tier i
                    -> train with existing collector / learner / loop surfaces
                        -> freeze resulting tier-i behavior
                            -> repeat toward finer / executable structure
```

The package-owned part is:

```text
FrozenQuotientBehavior
    -> PathFiber
        -> FiberConditionedStage
```

The engineer-owned or external-framework-owned part is:

```text
model / learner / optimizer / update loop
```

## Current Repo Reality

The repo is not starting from zero.

### Already Present

The repo already has a serious package-native tower runtime:

- `src/state_collapser/tower/partition/tower.py`
- `src/state_collapser/tower/partition/schema.py`
- `src/state_collapser/tower/partition/state_layer.py`
- `src/state_collapser/tower/partition/action_layer.py`
- `src/state_collapser/tower/partition/update.py`

The repo already has useful low-level tower queries:

- state-cell membership
- outgoing action cells
- action-cell membership
- representative edges
- internal edges
- primitive lift candidates
- adjacent refinement fibers

The repo already has generic research training surfaces:

- `ActionSelectionInput`
- `ActionDecision`
- `TrainingTransition`
- `StepCollector`
- `EpisodeCollector`
- mask helpers
- continuation helpers
- simple metrics
- `TabularQLearner`
- reference online and episode loops

The repo already has a proto active-tier control stack:

- `ActiveTierState`
- `ActiveTierController`
- `ControlAction`
- `FrozenLowerContext`
- `TierLearner`
- `LiftResolveExecutor`
- `ActiveTierTransition`
- `ExploitExploreTowerRuntime`

The repo already has an external environment boundary:

- Gymnasium-like wrapper and hooks
- optional `rl` dependency group

The repo already has smoke benchmark infrastructure:

- runtime benchmark
- readout flag
- morphism flag
- schema-mode comparison

### Missing

The repo does not yet have first-class versions of:

- frozen quotient behavior
- path fibers over frozen quotient behavior
- fiber-conditioned training stages
- tower policy bundles
- stage/fiber identity in training transitions
- documentation-grade vocabulary for fine/coarse/upstairs/downstairs
- stable engineer-facing examples for staged freeze/lift/refine training

This blueprint targets those missing pieces.

## Non-Goals

This blueprint does not design a full neural RL framework.

It does not attempt to reproduce:

- PPO
- SAC
- DQN
- A2C
- distributed rollout
- multi-GPU training
- large replay systems
- hyperparameter tuning
- production experiment management
- RLlib-scale actor/learner orchestration
- Stable-Baselines3-style `.learn(...)` ownership of the loop

This blueprint also does not yet design:

- the full PyTorch model stack
- tensor/device/batch/sequence infrastructure
- durable checkpoints
- experiment manifests
- serious benchmark artifact output
- SB3/RLlib adapters

Those are downstream maturity phases.

The present goal is to make the package's own tower/fiber training semantics
explicit, inspectable, and usable.

## Terminology Contract

New code and documentation should use the following terminology.

### Total Space

`G_t^0` is the discovered total transition graph at exploration time `t`.

It should not be globally called "the base graph" in new user-facing surfaces,
because "base" is relative to a projection.

### Tier Direction

Increasing tier index means moving downward in the quotient tower:

```text
G_t^0 -> G_t^1 -> G_t^2 -> ...
fine / total / executable -> coarser / more quotiented / downstairs
```

Decreasing tier index means moving upward toward refinement:

```text
G_t^{i+1} -> G_t^i
coarser / downstairs -> finer / upstairs
```

### Frozen Coarser Behavior

When training tier `i`, the frozen object usually lives at tier `i + 1`.

It is coarser and downstairs relative to the active finer tier.

### Path Fiber

Given a tower projection:

```text
G_t^i -> G_t^{i+1}
```

and a frozen behavior/path/policy at tier `i+1`, the tier-`i` path fiber is the
space of tier-`i` paths whose projection is compatible with that frozen coarser
behavior.

### Fiber-Conditioned Stage

A fiber-conditioned stage is the package-native training surface induced by:

- a tower
- an active finer tier
- a frozen coarser behavior
- the resulting path fiber
- observation/mask/reward/continuation rules

This is the object that learners should train against.

## Proposed Module Placement

The recommended first placement is:

```text
src/state_collapser/training/frozen.py
src/state_collapser/training/fibers.py
src/state_collapser/training/stages.py
```

This keeps the surfaces close to existing training objects while allowing them
to depend on the partition tower runtime.

Alternative placement:

```text
src/state_collapser/tower/training/
```

The first placement is preferred because the central user-facing object is a
training stage, not another tower layer.

The tower should supply the geometry.

The training package should supply the learner-facing surface.

## Proposed Public Surfaces

### `FrozenQuotientBehavior`

Purpose:

Represent behavior at a coarser quotient tier that is treated as fixed while a
finer-tier policy is trained inside the corresponding path fiber.

Initial responsibilities:

- identify the frozen tier
- identify the finer tier it supports
- identify the tower/schema context
- expose a decision surface at the frozen tier
- optionally store a frozen path or rollout prefix
- expose immutable metadata
- provide a stable version/fingerprint
- carry diagnostics from the freeze event

Suggested conceptual shape:

```python
@dataclass(frozen=True, slots=True)
class FrozenQuotientBehavior:
    behavior_id: str
    coarse_tier: int
    supported_fine_tier: int
    tower_fingerprint: str | None
    schema_fingerprint: str | None
    decision_surface: object
    path_prefix: tuple[object, ...] = ()
    action_prefix: tuple[object, ...] = ()
    version: int | str = 0
    metadata: Mapping[str, object] = field(default_factory=dict)
```

The exact implementation may differ, but the semantic requirements are fixed:

- it is frozen
- it is coarser than the active stage
- it is package-owned
- it is not an optimizer object
- it is not merely a model checkpoint

Relationship to existing code:

`FrozenLowerContext` is the closest existing object, but its vocabulary is now
misleading. It should be adapted, renamed, or wrapped rather than treated as the
final concept.

### `PathFiber`

Purpose:

Represent the admissible finer-tier path/action space lying over a frozen
coarser behavior.

Initial responsibilities:

- hold a `PartitionTower` or read-only tower view
- identify `fine_tier`
- identify `coarse_tier`
- reference `FrozenQuotientBehavior`
- expose admissible finer state cells
- expose admissible finer action cells
- produce masks for learner-facing actions
- diagnose departures from the fiber
- project candidate fine transitions downward
- connect to existing tower query methods

Suggested conceptual shape:

```python
@dataclass(frozen=True, slots=True)
class PathFiber:
    fiber_id: str
    tower: PartitionTower
    fine_tier: int
    coarse_tier: int
    frozen_behavior: FrozenQuotientBehavior
    current_fine_cell: object | None
    current_coarse_cell: object | None
    metadata: Mapping[str, object] = field(default_factory=dict)
```

Likely methods:

```python
def admissible_action_cells(self) -> tuple[object, ...]: ...

def action_mask(self, action_space: object | None = None) -> tuple[bool, ...] | None: ...

def lift_candidates(self, action_cell: object, total_state: object) -> tuple[object, ...]: ...

def project_fine_step(self, candidate: object) -> object: ...

def diagnose_departure(self, candidate: object) -> FiberDeparture | None: ...
```

Relationship to existing code:

`PartitionTower.refinement_fiber(...)` and `PartitionTower.lift_candidates(...)`
are low-level query primitives. `PathFiber` composes them into a temporal
training object.

### `FiberDeparture`

Purpose:

Make failure to remain inside the fiber inspectable.

Initial responsibilities:

- identify the attempted fine state/action/transition
- identify the expected coarse behavior
- identify the actual projection
- classify the departure reason
- provide diagnostics usable by tests and training logs

Potential reasons:

- action not in refinement fiber
- projected target does not match frozen behavior
- no lift candidate available
- stale tower version
- unknown state/action cell
- terminated outside stage semantics

### `FiberConditionedStage`

Purpose:

Expose a learner-facing training problem induced by a frozen coarser behavior.

Initial responsibilities:

- wrap or reference the runtime/environment
- hold a `PathFiber`
- build `ActionSelectionInput`
- attach stage/fiber diagnostics
- build masks from fiber admissibility
- collect or delegate step execution
- define reward behavior inside the fiber
- define continuation semantics inside the fiber
- produce `TrainingTransition` objects with stage/fiber identity
- expose enough shape to be later adapted to Gymnasium/SB3/RLlib

Suggested conceptual shape:

```python
@dataclass(slots=True)
class FiberConditionedStage:
    stage_id: str
    runtime: object
    tower: PartitionTower
    fine_tier: int
    coarse_tier: int
    frozen_behavior: FrozenQuotientBehavior
    path_fiber: PathFiber
    observation_builder: object
    reward_semantics: object
    continuation_semantics: object
```

Likely methods:

```python
def reset(self, *, seed: int | None = None, options: dict[str, object] | None = None) -> ActionSelectionInput: ...

def current_input(self) -> ActionSelectionInput: ...

def action_mask(self) -> tuple[bool, ...] | None: ...

def step(self, decision: ActionDecision) -> TrainingTransition: ...

def freeze_behavior(self, policy: object, *, metadata: Mapping[str, object] | None = None) -> FrozenQuotientBehavior: ...
```

The exact API should remain simple enough that an engineer can still write the
training loop themselves.

The stage should not own:

- optimizer stepping
- gradient updates
- policy architecture
- distributed sampling
- full experiment lifecycle

### `FiberStageContext`

Purpose:

Attach explicit stage/fiber information to inputs and transitions without
stuffing opaque objects into diagnostics.

Suggested conceptual shape:

```python
@dataclass(frozen=True, slots=True)
class FiberStageContext:
    stage_id: str
    fiber_id: str
    fine_tier: int
    coarse_tier: int
    frozen_behavior_id: str
    frozen_behavior_version: int | str
```

This object should be referenced by:

- `ActionSelectionInput`
- `TrainingTransition`
- `CollectedStep`
- eventual replay/trajectory objects
- eventual checkpoint/manifest objects

## Changes To Existing Training Surfaces

### `ActionSelectionInput`

Current surface:

- observation
- current base state
- runtime snapshot
- tower position key
- action mask
- history
- active tier state
- frozen lower context
- diagnostics

Target evolution:

- keep backward compatibility initially
- add explicit stage/fiber context
- prefer `current_total_state` in new APIs
- use `fiber_context` or `stage_context` instead of opaque
  `frozen_lower_context`

Potential additive fields:

```python
stage_context: FiberStageContext | None = None
fiber_departure: FiberDeparture | None = None
```

No breaking rename should happen in the first implementation unless the PO
explicitly approves it.

### `TrainingTransition`

Current surface already carries:

- tower position
- active tier
- frozen context version
- runtime summary
- bootstrap semantics

Target evolution:

- add stage/fiber identity
- record projected coarse behavior step
- record whether the transition remained inside the fiber
- record departure diagnostics when not

Potential additive fields:

```python
stage_context: FiberStageContext | None = None
projected_coarse_step: object | None = None
fiber_departure: FiberDeparture | None = None
```

The transition should make it possible to later sample replay by:

- stage
- fiber
- fine tier
- coarse tier
- frozen behavior version

### `StepCollector`

The existing `StepCollector` should not become a giant framework object.

Preferred evolution:

- allow a `FiberConditionedStage` to implement the runtime-like surface consumed
  by the collector
- or add a small `FiberStepCollector` wrapper that injects stage/fiber metadata
  while delegating most behavior to `StepCollector`

The collector should remain simple:

```text
input -> decision -> environment/stage step -> transition
```

### `ReferenceLoop`

The existing reference loops should remain simple.

The first target should be:

```text
run_reference_online_loop(runtime=fiber_stage, learner=learner, ...)
```

or:

```text
run_reference_online_loop(runtime=stage_runtime_adapter, learner=learner, ...)
```

The loop should not learn about the whole curriculum.

The curriculum should be represented by stage construction and frozen behavior
handoff.

## Relationship To `tower/control`

The existing `tower/control` package is proto-stage-control infrastructure.

It should not be deleted or ignored.

It should be reviewed as a source of reusable concepts:

- active tier state
- control actions
- lift/descend transitions
- learner protocol
- executor protocol
- frozen context versioning
- active-tier transition records
- controller metrics

But it should not define the final vocabulary.

### `FrozenLowerContext`

Likely fate:

- keep as compatibility object
- introduce `FrozenQuotientBehavior`
- provide adapter or migration path
- avoid new code that deepens the old "lower" vocabulary

### `LiftResolveExecutor`

Likely fate:

- reinterpret as a local executor over `PathFiber`
- possibly rename later to `FiberActionResolver` or `PathFiberExecutor`
- keep protocol tests where useful

### `ActiveTierTransition`

Likely fate:

- treat as a proto form of stage transition
- either wrap into `TrainingTransition`
- or preserve as a controller-level transition record

### `ExploitExploreTowerRuntime`

Likely fate:

- preserve as reference/prototype
- do not make it the only path into fiber-conditioned training
- ensure new stage surfaces can be tested without this runtime

## Relationship To External RL Libraries

External frameworks should see only a stable stage boundary.

The future adapter shape is:

```text
FiberConditionedStage
    -> adapter
        -> external learner/framework
            -> trained policy/model artifact
                -> state_collapser FrozenQuotientBehavior / TowerPolicyBundle
```

This blueprint does not implement adapters.

It designs the object they will adapt.

## Relationship To Gymnasium

The package already has Gymnasium-like wrappers for observing realized
transitions.

The future Gymnasium-facing stage adapter should be separate:

```text
FiberConditionedStage -> Gymnasium-like Env
```

This adapter should make explicit:

- observation shape
- action mask semantics
- illegal fiber departure behavior
- termination/truncation behavior
- frozen behavior metadata
- tower schema metadata

The first implementation of `FiberConditionedStage` should not require this
adapter, but it should be designed so the adapter is straightforward.

## Minimal First Implementation Slice

The first implementation should be deliberately small.

It should support:

- one adjacent fine/coarse tier pair
- one frozen behavior object
- path-fiber admissibility over existing partition-tower queries
- mask generation from admissible action cells or lift candidates
- stage/fiber metadata on action inputs
- stage/fiber metadata on transitions
- a simple reference learner loop
- one tiny deterministic graph test
- one existing example-family smoke test

It should not support:

- arbitrary multi-stage curriculum orchestration
- neural training
- replay buffers
- checkpoints
- external framework adapters
- distributed training

## Minimal Demonstration Scenario

The first test fixture should be intentionally tiny.

Example:

```text
total graph:
    s0 -> s1 -> g
    s0 -> s2 -> g

coarser tier:
    s1 and s2 are collapsed or share a quotient behavior

frozen coarser behavior:
    choose the coarse action that moves from [s0] to [g]

fiber stage:
    train at the finer tier among the primitive choices that project to that
    frozen coarse behavior
```

The test should prove:

- the coarser behavior is immutable
- the path fiber is computed from tower projection data
- admissible finer actions remain inside the fiber
- non-admissible actions are masked or diagnosed
- the learner-facing transition records stage/fiber metadata

## Documentation-Driven API Constraints

Because the documentation blueprint is being written in parallel, the following
usability constraints should shape code design.

### Constraint 1: The Engineer Mental Model Must Fit In Three Objects

An engineer should be able to learn:

```text
FrozenQuotientBehavior
PathFiber
FiberConditionedStage
```

and understand the first serious training surface.

If the implementation requires ten new concepts before the first example runs,
the surface is too complicated.

### Constraint 2: Every New Concept Needs A Tower Query Anchor

The docs must be able to say:

```text
PathFiber is built from these PartitionTower queries.
```

If a new concept cannot be traced back to the existing tower runtime, it is
probably accidental abstraction.

### Constraint 3: The First Example Must Not Require Torch

The first staged training example should use a simple learner or hand-written
policy.

Torch, SB3, and RLlib should come later.

The goal is to teach semantics first.

### Constraint 4: The Direction Vocabulary Must Be Unambiguous

Docs and code should consistently use:

- finer
- coarser
- upstairs
- downstairs
- total
- quotient

New public surfaces should avoid intensifying the old `base` and `lower`
ambiguity.

## Testing Blueprint

### Unit Tests

Add tests for `FrozenQuotientBehavior`:

- construction
- immutability
- stable identity/version
- metadata preservation
- fine/coarse tier validation

Add tests for `PathFiber`:

- state-cell refinement over a coarse cell
- action-cell refinement over a coarse action
- lift candidates from current total state
- action mask production
- departure diagnostics
- stale/unknown cell handling

Add tests for `FiberConditionedStage`:

- reset produces `ActionSelectionInput`
- input carries stage/fiber context
- action mask reflects fiber admissibility
- step produces `TrainingTransition`
- transition carries stage/fiber context
- illegal action is rejected or diagnosed according to configured semantics

### Integration Tests

Add one tiny synthetic graph integration test:

- build partition tower
- freeze coarse behavior
- train or step fine stage
- verify projected fine behavior matches frozen coarse behavior

Add one existing environment-family smoke test:

- use an existing example runtime
- build a simple frozen behavior
- construct a stage
- run a short reference loop
- verify no existing flat training tests regress

### Compatibility Tests

Existing tests for:

- partition tower initialization
- incremental update
- queries and lift
- training collectors
- reference loops
- exploit/explore control
- example training

should continue passing.

If tests must change, the implementation gameplan should justify why.

## Acceptance Criteria

The blueprint has been implemented successfully when:

- `FrozenQuotientBehavior` exists as a package-native frozen behavior object.
- `PathFiber` exists and composes existing `PartitionTower` queries.
- `FiberConditionedStage` exists and exposes a learner-facing stage.
- `ActionSelectionInput` can carry explicit stage/fiber context.
- `TrainingTransition` can carry explicit stage/fiber context.
- A simple learner can train or step inside a fiber-conditioned stage.
- Fiber admissibility is visible as masks or diagnostics.
- Existing flat training examples still work.
- Existing partition tower tests still work.
- Documentation examples can explain the surface without pretending this is
  RLlib or Stable-Baselines3.

## Deferred Work Register

The following should be explicitly deferred:

- tensor/device abstraction
- Torch model protocols
- vectorized rollout
- replay buffer design
- checkpoint/resume payloads
- experiment manifests
- benchmark artifact output
- SB3 adapter
- RLlib adapter
- production-scale training loop
- multi-stage curriculum manager

These are still important.

They are not the first blueprint's center.

## Open Design Questions

### Question 1

Should the frozen behavior object be named:

- `FrozenQuotientBehavior`
- `FrozenTierBehavior`
- `FrozenCoarseBehavior`

Recommendation:

Use `FrozenQuotientBehavior` in design docs because it names the mathematical
role. Consider shorter aliases in code only if the API becomes verbose.

#### PO Response:
I agree.

### Question 2

Should `PathFiber` represent only path-conditioned behavior, or policy-level
behavior too?

Recommendation:

Allow `FrozenQuotientBehavior` to represent either a concrete path prefix or a
policy/decision surface. `PathFiber` should expose the admissible fine behavior
relative to the frozen object's current decision context.

#### PO Response:
I agree.

### Question 3

Should `FiberConditionedStage` be a Gymnasium env?

Recommendation:

No, not at first.

It should be package-native first. A Gymnasium adapter can wrap it later.

#### PO Response:
I agree.

### Question 4

Should `tower/control` be refactored immediately?

Recommendation:

Only enough to avoid duplicate semantics. The first implementation can add new
training-stage objects while preserving the proto control stack. Later work can
merge or deprecate surfaces once the new stage layer is proven.

#### PO Response:
I agree, but put a TODO to come back to this in `CONTRIBUTING.md`.

### Question 5

Should old terminology be renamed immediately?

Recommendation:

No sweeping rename in the first pass.

New surfaces should use correct terminology. Existing public fields can remain
for compatibility until a deliberate rename/deprecation plan exists.

#### PO Response:
I agree, but put a TODO to come back to this in `CONTRIBUTING.md`.

## Blueprint Output

The expected implementation-ready result of this blueprint is not a framework.

It is a clean semantic bridge:

```text
PartitionTower
    -> FrozenQuotientBehavior
        -> PathFiber
            -> FiberConditionedStage
                -> existing training surfaces
```

That bridge is the package-owned maturity step.
