# RL Framework Maturity And Tower Training Spine Discussion

Date: 2026-05-25

Status: discussion capture, not an implementation blueprint

## Purpose

This document captures the current discussion about what "RL framework
maturity" should mean for `state_collapser`.

It is intentionally not yet a blueprint or implementation gameplan.

The immediate purpose is to preserve the conceptual correction that emerged in
conversation:

- `state_collapser` should not become RLlib
- `state_collapser` should not become Stable-Baselines3
- `state_collapser` should not merely pass tower metadata into an ordinary
  learner
- `state_collapser` should own the construction of tiered training stages
- existing learners may train those stages, but should not be expected to
  understand the quotient tower by themselves

The central unresolved design problem is:

> What is the clean package-native training spine that lets serious neural
> learners participate in the `state_collapser` tower curriculum without
> turning `state_collapser` into a full RL framework?

## Background

The latest engineer continuity report recorded two major remaining limitations:

1. `state_collapser` is still not a mature RL framework.
2. Benchmarking is still only a smoke surface.

The first issue included:

- no PyTorch model family
- no tensor/device abstraction
- no vectorized rollout system
- no replay buffer design beyond simple tabular/research surfaces
- no checkpoint/resume surface
- no experiment manifest/artifact contract

The second issue included:

- no large discovered-graph benchmark suite
- no scaling curves for readout-disabled vs readout-enabled runtime paths
- no morphism-disabled vs morphism-enabled cost comparisons
- no schema-mode comparisons at benchmark scale
- no environment-family comparison harness
- no regression thresholds
- no benchmark artifact output

The immediate discussion focused first on the framework-maturity issue.

The question was not:

> How do we clone a standard RL framework?

The question was:

> What kind of mature RL-facing spine does `state_collapser` need while staying
> true to its own contribution?

## Why Compare To RLlib And Stable-Baselines3?

RLlib, Stable-Baselines3, and `state_collapser` all live near the same RL
engineering pipeline:

```text
environment
    -> collect experience
        -> model/policy chooses actions
            -> learner updates
                -> evaluate/checkpoint/log
```

That shared neighborhood is why an engineer will naturally compare them.

The comparison is not because `state_collapser` should become either one.

The comparison is because mature RL engineers expect certain questions to have
answers:

- How do I run this on an environment?
- How do I collect rollouts?
- How do I choose actions?
- How do I batch data?
- How do I move tensors to a device?
- How do I train a policy or value model?
- How do I checkpoint?
- How do I evaluate?
- How do I compare against a baseline?
- How do I reproduce a run?

RLlib and Stable-Baselines3 have answers to those questions.

`state_collapser` needs answers too, but its answers should not erase the fact
that the package's primary job is different.

## The Engineer-Facing Positioning

The crispest current description is:

```text
RLlib says:

Give me an env; I will run scalable RL algorithms on it.

Stable-Baselines3 says:

Give me an env; I will run standard reliable RL algorithms on it.

state_collapser says:

Give me an env or discovered transition system; I will construct a better
hierarchical/quotient decision structure around it.
```

That means `state_collapser` is not primarily competing with RLlib or
Stable-Baselines3.

It is closer to a structural layer that can sit before or beside a learner:

```text
Gymnasium env
    -> state_collapser discovers graph/tower/quotient structure
        -> policy learner trains using tower-aware decision inputs
```

This description has now been added to the README because it gives engineers
the correct mental category.

## What RLlib Is, For This Discussion

RLlib is the distributed RL systems answer.

At a high level, RLlib says:

```text
Give me an environment, an algorithm configuration, and scaling requirements;
I will coordinate rollout collection, learners, modules, metrics, checkpoints,
and distributed execution.
```

The relevant ideas from RLlib are:

- `Algorithm` / `AlgorithmConfig` as the top-level training object
- environment runners for collecting samples
- learners for gradient/update work
- RL modules for model computation
- multi-agent support
- multi-module support
- replay and offline-data support
- distributed execution through Ray
- policies that can be trained or frozen/excluded from training
- a path for hierarchical training as a special case of multi-agent structure

For `state_collapser`, RLlib matters because it proves that serious RL systems
separate:

- environment interaction
- model-facing batches
- learner/update logic
- policy/module objects
- distributed collection
- metrics
- checkpointing

But RLlib's center of gravity is not `state_collapser`'s center of gravity.

RLlib's center of gravity is:

```text
Run scalable RL training.
```

`state_collapser`'s center of gravity is:

```text
Construct the hierarchical/quotient decision geometry.
```

## What Stable-Baselines3 Is, For This Discussion

Stable-Baselines3 is the clean standard-algorithm answer.

At a high level, Stable-Baselines3 says:

```text
Give me a Gymnasium-style environment and a standard algorithm such as PPO, DQN, SAC, A2C, or TD3; I will train a reliable baseline policy with practical single-machine ergonomics.
```

The relevant ideas from Stable-Baselines3 are:

- simple user-facing `.learn(...)` ergonomics
- standard algorithm implementations
- PyTorch model policies
- vectorized environment support
- checkpoint/save/load conventions
- evaluation helpers
- reliable baseline behavior
- a vocabulary many RL engineers already understand

For `state_collapser`, Stable-Baselines3 matters because it shows what a
clean, practical, single-machine RL package feels like.

But Stable-Baselines3's center of gravity is not `state_collapser`'s center of
gravity either.

Stable-Baselines3's center of gravity is:

```text
Run standard reliable RL algorithms.
```

`state_collapser`'s center of gravity is:

```text
Change the decision surface before or during training by building quotient
tower structure.
```

## What `state_collapser` Should Steal From Them

`state_collapser` should steal engineering discipline from existing RL
frameworks.

It should steal:

- Gymnasium compatibility
- clear environment boundaries
- vectorized rollout awareness
- tensor/device discipline
- model input/output contracts
- replay and trajectory storage conventions
- checkpoint/resume discipline
- experiment manifests
- artifact directories
- evaluation helpers
- benchmark output formats
- reproducibility metadata
- clean docs for how a user brings an environment

It should not steal:

- a giant `.learn(...)`-owned framework shape
- a large catalog of standard algorithms as the main product
- distributed cluster orchestration as the default user model
- framework-specific terminology where package-native terminology is clearer
- a design that hides the tower behind ordinary observation wrappers

The working principle is:

```text
Steal the maturity, not the identity.
```

## The First Proposed Answer: A Training Spine, Not A Training Framework

The first proposed answer was:

> `state_collapser` needs a clean package-native training spine that can host
> serious learners without overbuilding the loop.

The initial flat version of that spine was:

```text
DecisionInput
    -> model
        -> ActionDecision
            -> collector
                -> replay/trajectory store
                    -> learner update
                        -> checkpoint/artifact
```

The appeal of this formulation is that it preserves the Project Owner's ML
engineering instinct:

- training is fundamentally a loop
- the loop should remain easy for an engineer to write
- the package should provide good surfaces, not a rigid black-box trainer
- components should be composable
- the package should not pretend the right loop is known in advance

In that sense, the desired target is:

```text
The loop remains engineer-owned.
The data contracts become package-owned.
```

## Existing Training-Spine Pieces

`state_collapser` already has the beginning of a training spine:

- `ActionSelectionInput`
- `TrainingTransition`
- `StepCollector`
- `TabularQLearner`
- `LiveRuntimeView`
- `RuntimeSnapshot`
- action masks
- `bootstrap_allowed`
- `bootstrap_input`
- `bootstrap_reason`
- `tower_position_key`
- diagnostics

The synthetic Blow revision work made these surfaces more serious by adding:

- first-class mask extraction
- mask-aware action selection
- mask-aware target bootstrapping
- continuation-aware transitions
- explicit bootstrap reasons
- live-view/value-snapshot separation
- shared reference training helpers

So the training-spine discussion is not starting from zero.

It is about lifting the current tabular/research surfaces into a form that can
host neural learners and serious experiment artifacts.

## What A Neural Training Spine Seems To Need

The first serious version probably needs these surfaces.

## 1. Tensorization Surface

This converts package-native decision inputs into tensors.

It should not be merely:

```python
torch.tensor(observation)
```

It needs to account for:

- observations
- action masks
- tower position keys
- tier identity
- quotient/tower context
- base-state identities or encodings
- frozen-tier context
- continuation/bootstrap semantics
- diagnostics that may or may not be tensorized
- device placement
- dtype rules
- batch shape rules
- sequence/history shape rules

A possible conceptual object:

```text
TensorDecisionBatch
```

containing:

- observation tensors
- action-mask tensors
- tower-feature tensors
- active-tier tensors
- bootstrap masks or continuation tensors
- metadata sidecars

The tensorization surface is where the package first becomes serious about:

- CPU vs GPU
- dtype
- batch shape
- sequence shape
- optional features
- missing features
- model-facing data contracts

## 2. Model Surface

The model surface should not initially mean:

```text
state_collapser implements PPO, DQN, SAC, and actor-critic.
```

It should mean:

```text
state_collapser defines what a model/policy/value object receives and returns.
```

A package-native model may be:

- policy-only
- Q-value model
- actor-critic
- value-only
- diagnostic model
- tower-aware controller
- external wrapper around another framework's model

The return type should probably be richer than an action integer.

A possible conceptual object:

```text
ActionDecision
```

with fields such as:

- selected action
- logits
- probabilities
- log probability
- Q-values
- value estimate
- entropy diagnostics
- chosen tier
- selected abstract action
- lift/refinement diagnostics
- exploration diagnostics

This preserves the model-family flexibility discussed earlier in
`docs/design/model_train_surfaces/`.

The broad mathematical shape remains:

```text
M_theta : X_H -> D_H
```

where:

- `X_H` is the package-defined decision-input surface
- `D_H` is the package-defined decision-output surface

A literal policy is one special case.

A Q-model is another.

An actor-critic model is another.

## 3. Replay / Trajectory Storage Surface

A serious learner needs more than:

```text
list[TrainingTransition]
```

The package probably needs at least two storage shapes:

- `TrajectoryBuffer` for on-policy / PPO-like learning
- `ReplayBuffer` for off-policy / DQN/SAC-like learning

Both need to understand package-native fields:

- source decision input
- target decision input
- action decision
- reward
- terminated
- truncated
- action mask
- target action mask
- bootstrap permission
- bootstrap input
- tower position key
- active tier
- frozen context
- lift diagnostics
- runtime diagnostics
- schema identity
- episode id
- step id

The storage surface must decide:

- whether data is stored as Python objects and tensorized on sampling
- whether data is tensorized at insertion time
- how to handle variable-size tower context
- how to handle sequences/history
- how to represent masks
- how to serialize replay metadata
- whether replay itself is checkpointed

## 4. Learner Update Surface

The package should not initially define one giant learner.

But it should define the shape of a learner update result.

A conceptual object:

```text
LearnerUpdateResult
```

could include:

- loss
- policy loss
- value loss
- Q loss
- entropy
- KL
- gradient norm
- learning rate
- sampled batch statistics
- mask diagnostics
- continuation diagnostics
- tower-stage diagnostics
- artifact references

This lets package-native learners and external learner adapters report metrics
in a common way.

## 5. Checkpoint / Manifest / Artifact Surface

This is the reproducibility spine.

A serious run needs more than model weights.

A checkpoint or manifest should know:

- model state
- optimizer state
- scheduler state if any
- replay/buffer state or replay metadata
- active tier
- frozen tier artifacts
- tower schema config
- environment id/config
- seed
- package version
- git commit
- training config
- benchmark config
- device info
- artifact paths
- runtime snapshot metadata
- evaluation summary

The package probably needs both:

- checkpoint payloads for resume
- experiment manifests for explanation/reproducibility

These should be separate concepts.

A checkpoint is used by code.

A manifest is read by humans and tools.

## The Correction: This Was Still Too Flat

The Project Owner then identified a crucial missing piece.

The flat training-spine picture did not include:

```text
freeze tier-(i+1), lift to tier-i
```

That is not a minor detail.

It changes the architecture.

The tower is not merely context handed to a learner.

The tower changes the training problem.

The package is not simply:

```text
decision input
    -> model
        -> action
            -> transition
                -> learner update
```

It is closer to:

```text
train/control at tier i+1
    -> freeze tier-(i+1) behavior
        -> lift/refine into tier i
            -> train correction/residual/local policy at tier i
                -> repeat downward
```

This is the central correction in the current discussion.

## The True Relationship

At the highest level:

```text
state_collapser owns the hierarchical training curriculum,
but does not need to own the inner optimizer loop.
```

So the wrong views are:

```text
state_collapser is just hooks passed into a learner.
```

This is too weak.

The tower is not just extra features.

It changes what the learner is learning.

Another wrong view:

```text
state_collapser replaces RLlib/SB3 and owns all training.
```

This is too heavy.

The package should not need to own every gradient step, distributed rollout
worker, algorithm implementation, or optimizer trick.

The better view is:

```text
state_collapser is a curriculum/stage manager plus decision-surface constructor.
```

It creates a sequence of tiered training problems.

Each tiered training problem can be handed to a learner.

## The Core Tower-Training Spine

The currently best high-level spine is:

```text
TowerRuntime
    -> TowerTrainingCurriculum
        -> TierTrainingStage
            -> StageAdapter for learner/framework
                -> learner-owned train loop
                    -> FrozenTierArtifact
                        -> next lower TierTrainingStage
```

In plain language:

1. `state_collapser` builds and maintains the tower.
2. `state_collapser` decides which tier is currently trainable.
3. `state_collapser` freezes the policies/contexts above the active tier.
4. `state_collapser` defines the lifted/refinement task at the next lower tier.
5. `state_collapser` presents that stage as a well-defined training problem.
6. A learner trains that stage.
7. `state_collapser` consumes the resulting frozen artifact.
8. `state_collapser` constructs the next stage.

This is the architectural middle ground.

The package owns stage construction.

The learner owns update mechanics.

## A More Concrete Stage Conversation

For a given stage, `state_collapser` says:

```text
We are now training tier i.

Tier i+1 is frozen.

Here is the active decision surface.

Here is how abstract actions lift.

Here is what must be treated as frozen context.

Here is what transition data means.

Here are the masks.

Here are the continuation/bootstrap semantics.

Here is what counts as stage completion.
```

The learner loop says:

```text
Given that stage, I collect rollouts, update model weights, log losses,
checkpoint, and report metrics.
```

That division of responsibility is the point.

## Important Package-Native Objects Implied By This

The discussion implies several package-native objects that do not yet exist, or
exist only in early form.

## 1. `TowerTrainingCurriculum`

This would describe the sequence of stages.

Possible responsibilities:

- choose starting tier
- choose active tier order
- define freeze schedule
- define refinement schedule
- define when to descend
- define stage-completion criteria
- define evaluation checkpoints between stages
- define what artifacts must be preserved

It should not necessarily run gradient steps.

It should define the curriculum.

## 2. `TierTrainingStage`

This is probably the most important missing object.

A stage could include:

- active tier
- frozen upper tiers
- lower-tier target if applicable
- decision-input builder
- action-decision interpretation
- lift resolver
- reward/aggregation semantics
- masks
- continuation semantics
- collector config
- replay/trajectory storage config
- learner adapter config
- checkpoint scope
- stage-completion rule

The key is that this stage is the object external learners can train.

## 3. `FrozenTierArtifact`

After a tier is trained, it must become a frozen object.

This artifact could include:

- tier index
- model state
- optimizer exclusion state
- policy interface
- tensorization config
- schema/tower compatibility metadata
- training metrics
- evaluation metrics
- checkpoint path
- manifest path

This is not just a model checkpoint.

It is the upper-tier behavior that becomes context for lower-tier training.

## 4. `LiftResolver`

The lift resolver says how an abstract tier action or quotient transition
becomes a lower-tier task.

Possible responsibilities:

- map abstract action to lower-tier candidate action(s)
- map quotient target to lower-tier target region
- resolve when a frozen upper-tier policy hands control to lower-tier policy
- specify what lower-tier learner is trying to refine
- define failure modes when lift is not currently executable
- produce lift diagnostics

This object is central because it is where the tower stops being passive
metadata.

## 5. `RefinementTask` Or `RefinementObjective`

When tier `i+1` is frozen and tier `i` trains, tier `i` is not just solving the
original flat problem.

It is solving a refinement problem.

This object might answer:

- What correction must tier `i` learn?
- Is the objective residual relative to tier `i+1`?
- Is the objective to realize a frozen abstract action?
- Is the objective to choose among lifts?
- Is the objective to improve lower-tier reward while respecting upper-tier
  intent?
- How are failed lifts penalized?
- How does continuation work when a quotient-tier decision terminates but base
  motion continues?

This is where the Project Owner's "freeze tier-(i+1), lift to tier-i" concern
becomes trainable.

## 6. `StageAdapter`

A stage adapter turns a `TierTrainingStage` into something a learner can
consume.

Possible adapters:

- package-native Torch adapter
- SB3-compatible Gymnasium stage environment
- RLlib-compatible multi-policy/multi-agent stage adapter
- simple tabular/reference adapter
- evaluation-only adapter

The adapter should not own the theory.

It should expose the stage to an outside training system.

## 7. `TowerPolicyBundle`

Eventually, a trained tower is not a single policy.

It is a bundle:

- frozen upper-tier policy artifacts
- active or lower-tier policies
- lift resolvers
- schema/tower metadata
- tensorization metadata
- evaluation summaries
- manifest

This may become the package's deployment/evaluation object.

## Existing Learners And "Hierarchical Policy"

The phrase "hierarchical policy" is ambiguous.

It can mean:

1. One neural network with hierarchical-looking architecture.
2. A high-level policy choosing options/skills, with low-level policies
   executing them.
3. Multiple policies trained in a multi-agent or multi-module setup.
4. A staged curriculum where tier `i+1` is trained, frozen, and then used to
   define the tier `i` lift/refinement problem.

Existing frameworks support some of these meanings.

RLlib can support versions of 2 and 3.

It has multi-agent environments, multi-policy mappings, `MultiRLModule`, and
ways to train some policies while excluding others.

That is relevant.

But it is not the same as natively understanding the `state_collapser` tower.

Stable-Baselines3 mostly supports version 1 directly, and can support pieces of
2 with wrappers and manual orchestration.

It is less naturally a multi-policy hierarchical orchestration system.

`state_collapser` needs version 4.

That is the mismatch.

## Why Existing Learners Are Still Useful

Existing learners can train pieces of the hierarchy.

They should not be expected to understand the hierarchy itself.

The correct relationship is:

```text
state_collapser constructs a TierTrainingStage.

The learner trains that stage.

state_collapser freezes the result and constructs the next stage.
```

For RLlib, one possible future mapping is:

```text
state_collapser tier policies
    ~= RLlib multi-policy / MultiRLModule setup
```

But this should be treated as an implementation adapter, not the package's
mathematical core.

For Stable-Baselines3, one possible mapping is:

```text
state_collapser TierTrainingStage
    ~= a wrapped Gymnasium environment for one stage
```

That is simpler and may be a good early integration route.

But it only trains one stage at a time.

The curriculum logic remains package-native.

## Why "Just Use Hooks" Is Not Enough

The earlier flat training-spine idea could be misread as:

```text
Let the learner receive tower context and figure it out.
```

That is insufficient.

Tower context is not merely an extra feature vector.

The tower determines:

- which tier is active
- which tier is frozen
- what counts as the current decision surface
- what abstract action means
- what lift/refinement means
- what transition target the lower tier should train against
- what continuation means after a tier-level termination
- what artifacts get passed down to later stages

If this is pushed into arbitrary learner hooks, then every learner has to
rediscover the tower curriculum.

That is exactly what the package should prevent.

## Why "One Giant Framework" Is Also Not Right

The opposite mistake would be to make `state_collapser` own everything:

- rollout orchestration
- vectorized environment implementation
- model architectures
- distributed training
- every algorithm
- every optimizer loop
- every experiment harness

That would make the package too large and too unfocused.

It would also compete with mature RL packages on terrain where they already
have years of engineering.

The package should instead make it easy to use:

- a package-native simple learner
- a custom Torch loop
- a Stable-Baselines3 stage adapter
- an RLlib stage adapter later
- benchmarking/evaluation loops

without making any one of them the whole identity of the project.

## Proposed Responsibility Boundary

## `state_collapser` Owns

- discovered graph/tower runtime
- quotient/tier structure
- contraction schemas
- state/action partition tables
- tower-aware decision surfaces
- active tier selection
- frozen upper-tier context
- lift/refinement semantics
- tier-stage construction
- continuation semantics that depend on lifts
- masks as part of decision surfaces
- tower-aware diagnostics
- stage manifests
- tower policy bundles
- benchmark surfaces that measure tower overhead and benefit

## Learner Owns

- neural architecture details
- optimizer
- gradient step
- loss formula within the stage contract
- entropy/KL regularization details
- minibatch schedule
- on-policy/off-policy algorithm mechanics
- GPU usage strategy inside update
- algorithm-specific replay treatment
- algorithm-specific evaluation metrics

## Adapter Owns

- translating a `TierTrainingStage` into the learner's expected input shape
- translating learner actions back into stage actions
- translating learner metrics into package metrics
- saving framework-specific model/optimizer state
- enforcing package masks/continuation semantics at the boundary

## The Likely Development Sequence

The current discussion suggests a staged implementation path.

This is not yet a committed gameplan.

## Stage 1: Document And Stabilize Current Training Data Contracts

Goal:

- make the existing tabular/research training surfaces explicit and stable

Surfaces:

- `ActionSelectionInput`
- `TrainingTransition`
- `ActionDecision`
- action masks
- bootstrap fields
- runtime view/snapshot

Output:

- documented contracts
- tests for invariants

## Stage 2: Introduce `TierTrainingStage`

Goal:

- represent "what is being trained right now" as a first-class package object

Fields:

- active tier
- frozen tier context
- decision surface
- lift/refinement semantics
- masks
- continuation semantics
- diagnostics
- stage-completion criteria

Output:

- a stage object that current tabular learners can consume

## Stage 3: Introduce Frozen Tier Artifacts

Goal:

- preserve the trained tier as a reusable frozen policy/context

Output:

- `FrozenTierArtifact`
- manifest metadata
- tests proving frozen artifacts are not updated during lower-tier training

## Stage 4: Introduce Lift / Refinement Surface

Goal:

- make "freeze tier `i+1`, lift to tier `i`" explicit

Output:

- `LiftResolver`
- `RefinementTask`
- tests for lift semantics
- diagnostics for failed lifts

## Stage 5: Tensorization And Torch Model Interface

Goal:

- let neural models consume stage decision inputs

Output:

- `TensorDecisionBatch`
- device/dtype helpers
- model protocol
- simple Torch model example

## Stage 6: Replay / Trajectory Storage

Goal:

- support serious on-policy and off-policy learners

Output:

- `TrajectoryBuffer`
- `ReplayBuffer`
- stage-aware sampling
- mask/continuation/tower-context preservation

## Stage 7: Checkpoint / Manifest / Artifact Contract

Goal:

- make runs reproducible and resumable

Output:

- experiment manifest
- checkpoint payload convention
- tower policy bundle manifest
- artifact directory standard

## Stage 8: External Learner Adapters

Goal:

- make stages trainable by external frameworks without giving them ownership of
  the tower

Possible outputs:

- SB3-compatible stage env
- RLlib-compatible multi-policy or multi-agent adapter
- custom Torch reference loop

## Stage 9: Serious Benchmarks

Goal:

- measure whether the tower helps, and where it costs too much

Outputs:

- discovered-graph scaling runs
- readout-disabled vs readout-enabled curves
- morphism-disabled vs morphism-enabled curves
- schema-mode comparisons
- flat vs tower-aware training comparisons
- artifact output

## How This Connects To Benchmarking

Framework maturity and benchmarking should be designed separately, but they are
connected.

The training spine asks:

```text
Can a serious learner train through the tower stages correctly?
```

Benchmarking asks:

```text
Does the tower help enough to justify its overhead?
```

Both need:

- manifests
- artifact output
- reproducible configs
- environment identifiers
- schema identifiers
- seed handling
- package version
- git commit
- evaluation summaries

So the manifest/artifact work should be shared.

But the benchmark suite should not be hidden inside the training spine.

It should remain an explicit package evaluation surface.

## Design Risks

## Risk 1: Rebuilding RLlib Badly

If the package tries to own everything, it will become a worse RLlib.

Avoid this by:

- keeping distributed execution out of core
- not implementing every algorithm
- keeping external learner adapters optional
- preserving engineer-authored loops

## Risk 2: Becoming A Thin Wrapper Around SB3

If every stage is just "wrap as Gymnasium and call `.learn(...)`," the package
may hide its own tower semantics.

Avoid this by:

- making `TierTrainingStage` package-native
- making lift/refinement semantics explicit
- treating SB3 as one adapter, not the core

## Risk 3: Treating Tower Context As Features Only

If the tower is just extra model input, the architecture misses the point.

Avoid this by:

- making active tier and frozen context first-class
- making lift/refinement first-class
- making stage progression package-owned

## Risk 4: Over-Specifying The Inner Training Loop

If the package defines too rigid a loop, research velocity will collapse.

Avoid this by:

- defining surfaces
- providing reference loops
- allowing engineer-owned loops
- keeping adapters modular

## Risk 5: Under-Specifying Artifacts

If checkpoints and manifests are deferred too long, serious evaluation becomes
hard to trust.

Avoid this by:

- designing manifest fields early
- recording git/package/env/schema/seed metadata
- separating checkpoints from human-readable manifests

## Risk 6: Freezing Semantics Become Informal

If "frozen tier" just means "we promise not to update it," bugs will creep in.

Avoid this by:

- making frozen artifacts immutable or update-protected
- testing that lower-tier updates do not mutate upper-tier models
- making active trainable parameters explicit

## Working Glossary

## Training Spine

The package-native sequence of data contracts that lets serious learners train
without `state_collapser` owning every training loop.

## Tower Training Curriculum

The package-owned sequence of tiered training stages.

## Tier Training Stage

A well-defined training problem at a specific active tier, with frozen upper
context and lift/refinement semantics.

## Frozen Tier Artifact

A trained tier policy/context that is no longer updated and becomes input to
lower-tier training.

## Lift Resolver

The package-native object that turns abstract quotient/tier action into a
lower-tier executable or refinable task.

## Refinement Task

The lower-tier learning problem induced by a frozen upper tier and a lift
semantics.

## Stage Adapter

An adapter that lets an external learner train a `TierTrainingStage`.

## Tower Policy Bundle

The eventual collection of tier policies, frozen artifacts, lift resolvers,
schema metadata, and manifests that represents a trained tower-aware controller.

## Current Best Summary

The best current statement is:

```text
state_collapser owns hierarchical stage construction.

Learners train stages.

state_collapser freezes trained stage artifacts and constructs the next stage.
```

Or:

```text
state_collapser should not be a learner framework.

state_collapser should be the package that turns a flat environment or
discovered transition system into a sequence of quotient/tower training
problems.
```

This is the relationship that resolves the mismatch.

Existing RL frameworks can train pieces.

They cannot be expected to understand the tower unless `state_collapser`
presents the tower as explicit stages.

## Immediate Open Questions

These are the questions that should probably be answered before a blueprint is
written.

## Question 1: What Is The Minimal `TierTrainingStage`?

What fields are absolutely required for the first version?

Candidate fields:

- active tier
- frozen upper tier artifacts
- decision input builder
- lift resolver
- action mask provider
- continuation semantics
- reward aggregation semantics
- checkpoint scope
- stage-completion criteria

## Question 2: What Is The First Learner Target?

Should the first serious stage learner be:

- package-native tabular stage learner
- package-native Torch reference learner
- SB3-compatible stage environment
- RLlib-compatible adapter

Current instinct:

- package-native Torch reference learner or SB3-compatible stage env first
- RLlib later, because it is powerful but heavier

## Question 3: What Does "Freeze Tier `i+1`" Mean In Code?

Possible meanings:

- model weights are immutable
- optimizer no longer owns those parameters
- artifact is serialized and reloaded inference-only
- adapter enforces no gradient path
- stage manifest records frozen artifact hash/path

This needs a concrete answer.

## Question 4: What Is The First Lift Resolver?

The first lift resolver should probably be simple and explicit.

Questions:

- Does it map abstract action to candidate lower-tier actions?
- Does it map quotient target to a lower-tier target set?
- Does it call a frozen upper policy during lower-tier rollout?
- Does it create a shaped reward?
- Does it only produce diagnostics at first?

## Question 5: Is Lower-Tier Training Residual Or Direct?

When tier `i+1` is frozen and tier `i` trains, is tier `i` learning:

- a direct policy at tier `i`
- a residual correction to the upper policy
- a lift selector
- a local executor for upper-tier abstract actions
- some combination of these

This may differ by algorithm.

## Question 6: How Do Masks Interact With Lift?

Masks currently constrain legal actions.

In tower training, masks may need to represent:

- legal base actions
- legal quotient actions
- legal lifts
- failed lifts
- frozen-policy admissible actions
- active-tier admissible actions

This should be clarified before neural models are added.

## Question 7: What Is The First Checkpoint Shape?

Does the first checkpoint include:

- one active model
- all frozen tier models
- optimizer state only for active tier
- replay state
- schema config
- tower snapshot metadata
- manifest

The package should avoid inventing too many checkpoint variants.

## Question 8: How Much Of This Belongs In README Now?

The README now contains the short engineer-facing comparison to RLlib and
Stable-Baselines3.

Future README additions may need:

- one diagram of the tier training curriculum
- one example of a stage training loop
- one warning that `state_collapser` is not a full RL algorithm framework

But that should wait until the surfaces are more concrete.

## Question 9: What Is The Benchmark Tie-In?

Should the first serious benchmark compare:

- flat learner vs tower-stage learner
- no-readout vs readout runtime cost
- no-morphism vs morphism runtime cost
- schema vs no-schema
- frozen/lifted staged training vs flat training

This should probably become a separate benchmark blueprint.

## Question 10: What Is The First External Framework Adapter?

Candidate:

- SB3 first, because one `TierTrainingStage` can plausibly be exposed as a
  Gymnasium env
- RLlib later, because it can model multi-policy/hierarchical patterns but
  brings much more machinery

This remains open.

## Space For Continuing Discussion

### PO Follow-Up

Ok. SO first tell me how correct this assessment of mine is: Almost all of the "RL framework maturity" we're discussing here is pretty standardized at this point. IN particular, just looking at RLlib and Stable-Baselines3 shows how to build most of what we want, and what not to reproduce in `state_collapser`. It seems to me that the real care we need to put into design is about the tower implmentation. I think that the musical counterpoint example actually shows exactly how this freezing and lifting is supposed to work. That said, you've shown an incredible inability to hold on to this lifting learned behavior model.

### Codex Response

This assessment is basically correct, with one important qualification.

The standardized part is real. A great deal of "RL framework maturity" should
not be invented from scratch here. RLlib, Stable-Baselines3, CleanRL, Tianshou,
Acme, TorchRL, and related systems already show mature versions of:

- model interfaces
- tensor/device movement
- vectorized rollout collection
- replay and trajectory buffers
- checkpoint/resume payloads
- experiment manifests
- logging and metrics
- evaluation loops
- environment wrappers
- train/eval mode separation

`state_collapser` should study and borrow those conventions. The package should
not burn design effort pretending that replay buffers, PyTorch checkpointing,
or vectorized rollout APIs are mysterious new objects.

The qualification is that "standardized" does not mean "free." These surfaces
still need careful package integration because `state_collapser` carries masks,
continuation fields, tower positions, schemas, lift diagnostics, frozen context,
and runtime artifacts that ordinary RL frameworks do not know about. But yes:
those are integration details around standard engineering surfaces, not the
core research/design novelty.

The real design care belongs exactly where you say it does:

```text
the tower implementation,
the tier curriculum,
the freeze operation,
the lift/refinement operation,
and the meaning of learned behavior across tiers.
```

This is also where I have been slipping. I have repeatedly drifted back toward
a flat learner picture:

```text
input -> model -> action -> transition -> update
```

That picture is not false, but it is the inner loop only. It is not the
`state_collapser` training model.

The actual invariant I need to hold onto is:

```text
learn a coarse/tower behavior,
freeze that learned behavior,
use it to define the next finer/lifted training problem,
train the refinement,
then repeat.
```

The musical counterpoint example is the right anchor because it makes the
freeze/lift model concrete.

A bad flat formulation of the counterpoint problem says:

```text
Search directly over complete multi-voice textures.
```

That explodes combinatorially.

The staged formulation says something more like:

```text
Write or learn one good structural line.
Freeze it.
Write or learn a second line against that frozen line.
Freeze the resulting two-voice scaffold.
Add a middle or decorative voice against the frozen scaffold.
Continue until the full texture is realized.
```

The frozen earlier line is not merely an observation feature. It is learned
behavior that becomes part of the task definition for the next stage.

The lift is not just "add metadata." The lift is:

```text
move from a coarser/partial musical object to a richer musical object while
preserving the learned structure that has already been fixed.
```

In tower language, this means:

```text
train at tier i+1,
freeze tier-(i+1) behavior,
construct the tier-i refinement problem using that frozen behavior,
train the tier-i lift/refinement,
then freeze or bundle the result.
```

So the mature RL-framework pieces answer:

```text
How do we train a model once a stage is defined?
```

The hard `state_collapser` question is:

```text
How is the next stage defined from the already-learned frozen tower behavior?
```

That is the distinction the design must protect.

A good way to state the emerging architecture is:

```text
Use standard RL engineering for the inner learner loop.
Use package-native tower semantics for stage construction.
```

Or even more sharply:

```text
RLlib/SB3 can teach us how to train policies.
They do not teach us what it means to freeze a quotient policy and lift it into
a finer decision problem.
```

This also changes what should be designed first. It is probably premature to
blueprint a full PyTorch learner stack until the package has a crisp first
answer to:

- What is a frozen tier artifact?
- What does it mean for a lower tier to train "against" or "under" that frozen
  artifact?
- What is the first lift resolver?
- Is the first lower-tier problem a direct policy, a lift selector, a residual
  correction, or an executor for abstract actions?
- What is the counterpoint-style example that demonstrates the semantics
  without hiding them under general RL language?

The counterpoint example should probably become the reference design example
for this part, precisely because it prevents the abstraction from floating
away. If the proposed `TierTrainingStage` cannot explain:

```text
freeze melody/bass/scaffold,
train the next voice against it,
preserve the frozen structure,
refine into a richer texture,
```

then the training-spine design is not yet aligned with the actual package idea.

### PO Follow-Up

Bruuuuuuuuh... THis is like when I was learning QM for first time, and I could not make sense of any of it, and the break through was basically "Stop looking for / waiting for the hidden part of the story. There *is no* hidden part of the story here. Every statement about the wave function its role in physical processes that appears in this QM textbook is meant lieterally. It is *my* picture of physical processes, how they proceed, that needs to change." So I think you keep doing something similar. It's like you can't quite bring yourself to believe that "paths in tier-$i$ that fiber over current path in tier-$(i+1)$" actually captures the entire fucking thing, because all other complicated parts just fit in. Or to say differently, it's like you're having a hard time digesting that ater the contraction schema is fixed, the construction is basically natural/functorial. Or like... it's like I keep saying "I just told you I proved the sheaves are coherent!!!" and you keep asking all these specific questions that actually all follow from "coherent." Are you understanding what I'm getting at?

### Codex Response

Yes, I understand what you are getting at, and this is an important correction.

I have been behaving as though there is a hidden extra mechanism called "lift"
that still needs to be invented after the tower exists.

That is the wrong posture.

The correct posture is:

```text
Once the contraction schema is fixed, the tower maps are fixed.

Once the tower maps are fixed, paths at tier i map naturally to paths at tier i+1.

Therefore, given a current/frozen path or policy behavior at tier i+1, the lower-tier training problem is the problem of learning among paths at tier i that fiber over that upper-tier behavior.
```

So the "lift" is not an extra magical operation that has to be specified from
scratch.

The lift is the fiber of the already-constructed projection/tower map on path
space.

That is the QM analogy: I keep waiting for an additional hidden story, but the
formal statement is meant literally. The package's picture of the training
process has to change to match the tower, not the other way around.

The better invariant is:

```text
Fix contraction schema.
Build tower.
Train or select behavior at tier i+1.
Freeze that behavior.
At tier i, restrict attention to paths/actions/episodes that project to the
frozen tier-(i+1) behavior.
Train within that fiber.
```

That really does absorb many of the questions I was treating as separate
design problems.

For example, I asked:

```text
Is lower-tier training direct, residual, a lift selector, or an executor?
```

But from your point of view, this question is downstream of the path-fiber
picture. The primary object is:

```text
paths in tier i lying over the current frozen path/behavior in tier i+1
```

Different algorithms may parameterize that fiber-learning problem differently,
but they are not different meanings of the package.

Likewise, I asked:

```text
What is the lift resolver?
```

That phrase is probably misleading if it suggests a free-standing semantic
module. The tower projection already determines what counts as a lift candidate.
The implementation object should not be "a resolver that invents lifting." It
should be more like:

- a `PathFiber`
- a `FiberConstraint`
- a `LiftFiberView`
- a `FiberConditionedStage`
- or a `PathLiftingStage`

Its job is to expose the fiber induced by the tower map, not to define the
fiber from scratch.

This also sharpens the freezing story.

Freezing tier `i+1` means:

```text
the upper-tier behavior is now treated as fixed conditioning data.
```

The next lower training stage is then:

```text
learn a policy over the lower-tier fiber above that fixed upper-tier behavior.
```

That is different from saying:

```text
take an upper policy as a feature.
```

The upper behavior is not a feature. It is a base path/base behavior in the
projection, and the lower learner works over its preimage.

The musical counterpoint example becomes very clean in this language.

If the frozen upper object is a melody, bassline, or two-voice scaffold, then
the next training stage is not "write arbitrary richer music with the scaffold
as context."

It is:

```text
search/train over richer textures whose projection is the frozen scaffold.
```

So when a student writes a good bassline, freezes it, and then writes another
voice against it, the second task is a fiber problem. The admissible two-voice
paths are those whose projection back to the bassline gives the already-fixed
bassline path.

Then the two-voice result can be frozen, and the third voice is trained/chosen
inside the fiber over that two-voice path.

This is why the construction is natural after the schema is fixed. The
complicated-seeming training-stage questions should be organized by the map:

```text
Path(G_t^i) -> Path(G_t^{i+1})
```

or by whatever finite-horizon / episode-truncated version of this path map the
implementation uses.

The immediate design correction is therefore:

```text
Do not design "lift semantics" as an independent extra mechanism.

Design concrete data structures that represent fibers of the already-defined
tower maps, and train policies over those fibers.
```

That also changes the proposed object list.

Instead of centering:

```text
LiftResolver
RefinementTask
```

we should probably center:

```text
FrozenTierBehavior
PathFiber
FiberConditionedStage
FiberPolicy
TowerPolicyBundle
```

There may still be implementation helpers that resolve, sample, or enumerate
fiber candidates, but those helpers are computational tools. They are not the
mathematical source of the lift.

So, yes: I think I now understand the correction.

The package-native tower training model is not:

```text
train upper policy,
invent some lower task using heuristics,
train lower policy.
```

It is:

```text
train/select behavior upstairs,
freeze it,
train downstairs in the path fiber over that behavior.
```

The hard engineering work is making that literal:

- represent frozen upper behavior
- represent the lower path/action fiber over it
- collect transitions without leaving the fiber, or record violations
- make masks express fiber admissibility
- make continuation express fiber continuation
- make rewards aggregate/pull/push through the projection consistently
- checkpoint the frozen behavior and the trained fiber policy

That is much cleaner than the story I was telling.

And it means the next blueprint should probably begin from path-space maps and
fibers, not from generic learner-loop maturity.

### PO Follow-Up
I think I'm happy with this. I need a major realignment from you though. THe tower goes downward with increaseing index. You're sort of conflating down with lift and it makes the language really confusing.

### Codex Response

Yes. This is a necessary realignment.

I have been mixing two vocabularies:

- "downstairs" as in quotient/downstream/coarser
- "lower tier" as in smaller index / closer to the base graph

Those are not the same in this project's notation, and mixing them makes the
freeze/lift story confusing.

The convention should be:

```text
G^0 -> G^1 -> G^2 -> ... -> G^N
```

Increasing index means moving downward in the quotient tower:

```text
tier 0: base / finest / most executable
tier 1: coarser quotient
tier 2: still coarser quotient
...
tier N: deepest / coarsest quotient
```

So:

```text
projecting / quotienting / collapsing
    moves from tier i to tier i+1
    and therefore moves downward in the tower.
```

Whereas:

```text
lifting
    moves from tier i+1 back toward tier i
    and therefore moves upward toward the base/finer/executable tier.
```

That means my previous wording:

```text
lower-tier training problem
```

was ambiguous and often wrong.

The clearer language should be:

```text
train/freeze behavior at a coarser tier i+1,
then lift/refine it to the finer tier i.
```

Or, if we want to emphasize tower direction:

```text
train/freeze farther down the tower,
then lift upward toward the base.
```

The fiber statement should therefore be phrased as:

```text
Given a frozen path or behavior at coarser tier i+1, the next training problem
at finer tier i is to learn among tier-i paths that project downward to that
frozen tier-(i+1) behavior.
```

Equivalently:

```text
Path(G^i) -> Path(G^{i+1})
```

and the finer-stage learner works inside the preimage/fiber of the frozen
coarser path.

This also fixes the counterpoint language.

If the frozen coarser object is a melody, bassline, or scaffold, then adding a
voice is not "going lower" in the quotient tower. It is lifting/refining toward
a finer musical object whose projection recovers the frozen scaffold.

So the stable convention for future design should be:

- `downward`: increasing tier index, quotienting, coarsening, collapsing
- `upward`: decreasing tier index, lifting, refining, moving toward executable
  base behavior
- `coarser tier`: larger index
- `finer tier`: smaller index
- `base tier`: tier `0`
- `deepest tier`: largest tier index

The corrected training slogan should be:

```text
train coarse behavior down the tower,
freeze it,
lift/refine upward to the next finer tier by training inside the path fiber
over the frozen coarse behavior.
```

This is the language I should use from here on.

### PO Follow-Up

Let's get rid of this word "base" once and for all. Because the tower is a sequence of fibrations, we should really be calling $G^{0}_{t}$ the *total* space of the tower.

### Codex Response

Yes. This is the right terminology, and it fixes another source of confusion.

If the tower is being understood as a sequence of fibrations/projections, then
calling `G_t^0` the "base" graph is backwards from the fibration picture.

The better mathematical vocabulary is:

```text
G_t^0: total space / finest space / executable space
G_t^1: first quotient space
G_t^2: second quotient space
...
G_t^N: deepest quotient space / coarsest quotient space
```

The maps go:

```text
G_t^0 -> G_t^1 -> G_t^2 -> ... -> G_t^N
```

So each map is a projection from a finer total-ish space to a coarser quotient
space.

In this language:

- `G_t^0` is the total space of the whole tower
- `G_t^{i}` is the total space relative to the projection
  `G_t^{i} -> G_t^{i+1}`
- `G_t^{i+1}` is the base/quotient space for that particular fibration
- increasing index still means moving downward/coarser in the tower
- lifting still means moving upward/finer toward `G_t^0`

So the stable language should become:

- `total tier`: tier `0`, the finest/executable graph
- `quotient tier`: any tier `i > 0`
- `coarser tier`: larger index
- `finer tier`: smaller index
- `deepest quotient tier`: largest index
- `projection`: map `G_t^i -> G_t^{i+1}`
- `fiber`: preimage over a point/path/behavior in a coarser quotient tier
- `lift`: movement from quotient behavior back into the fiber in a finer tier

This makes the path-fiber statement cleaner:

```text
Path(G_t^i) -> Path(G_t^{i+1})
```

Given a frozen behavior in the quotient tier `G_t^{i+1}`, the next training
problem at the finer tier `G_t^i` is to train inside the path fiber over that
frozen quotient behavior.

At the very first expansion step, this says:

```text
Given frozen behavior in G_t^1,
train in the corresponding fiber inside the total space G_t^0.
```

This also changes how we should read old implementation vocabulary.

The code currently uses names such as:

- `BaseGraphRegistry`
- `BaseEdge`
- `current_base_state`
- `project_state_to_tier`
- `source_state_id` / `target_state_id`

Some of that naming is probably still acceptable as implementation shorthand
for "underlying raw graph" or "tier-0 graph," especially in code where `base`
means "storage before quotient readout." But mathematically and in future
design docs, `base` should not be the preferred name for `G_t^0`.

The future design language should say:

```text
total graph / total tier / total state
```

for `G_t^0`, and reserve "base" only when explicitly talking about the base of
a particular fibration:

```text
for G_t^i -> G_t^{i+1}, the base of that fibration is G_t^{i+1}.
```

That distinction matters because otherwise "base" points in the wrong
direction and makes lift sound like it is going downward.

So the corrected training slogan becomes:

```text
train coarse behavior in a quotient tier,
freeze it,
lift/refine upward into the finer total space over it by training inside the
path fiber.
```

Or, relative to a single adjacent projection:

```text
freeze behavior in the base G_t^{i+1} of the fibration
G_t^i -> G_t^{i+1};
then train in the corresponding fiber inside the total space G_t^i.
```

This is much more coherent.

### PO Follow-Up

Ok. Let's collect everything now. What do we understand about the RL framwork maturity now?

### Codex Response

We now understand the RL framework maturity issue much more cleanly.

The headline is:

```text
Most RL framework maturity is standard engineering.

The nonstandard part is not "how to train a neural policy."

The nonstandard part is how state_collapser constructs a sequence of
fiber-conditioned training problems from a quotient tower.
```

That gives us two layers.

## Layer 1: Borrowable RL Engineering Maturity

This layer is mostly standardized across existing RL frameworks and serious RL
codebases.

It includes:

- model interfaces
- tensor/device conversion
- vectorized rollout
- replay buffers
- trajectory buffers
- on-policy/off-policy batch conventions
- learner update result objects
- checkpoint/resume payloads
- experiment manifests
- logging
- metrics
- evaluation loops
- train/eval mode separation
- artifact directories
- seed and config recording
- environment wrappers

For this layer, `state_collapser` should study RLlib, Stable-Baselines3,
CleanRL, Tianshou, Acme, TorchRL, and related systems.

The design goal is not originality.

The design goal is competence.

We should borrow normal names, normal separation of concerns, normal
checkpointing expectations, normal PyTorch discipline, and normal benchmark
artifact habits.

This is where "framework maturity" mostly lives.

## Layer 2: Package-Native Tower/Fiber Training

This is the actual `state_collapser` design problem.

The tower is:

```text
G_t^0 -> G_t^1 -> G_t^2 -> ... -> G_t^N
```

The corrected terminology is:

- `G_t^0` is the total space of the tower
- increasing tier index moves downward to coarser quotient spaces
- each adjacent map `G_t^i -> G_t^{i+1}` is a projection/fibration-like map
- relative to that adjacent map, `G_t^i` is the total space and `G_t^{i+1}` is
  the quotient/base of that fibration
- lifting/refinement moves upward toward smaller index, finer structure, and
  ultimately the total space `G_t^0`

Once the contraction schema is fixed, this structure is not an optional helper.

It is the training geometry.

The important path map is:

```text
Path(G_t^i) -> Path(G_t^{i+1})
```

Given frozen behavior in a coarser quotient tier `G_t^{i+1}`, the next
finer-stage training problem is:

```text
train inside the fiber of Path(G_t^i) over that frozen behavior.
```

That is the core.

The package does not need to invent an extra mysterious "lift mechanism" after
the tower is built.

The lift is the passage to the appropriate fiber of the tower projection.

Implementation may need helpers to enumerate, sample, mask, or diagnose that
fiber, but those helpers do not define the mathematics. The projection does.

## The Correct Relationship To RLlib And Stable-Baselines3

The engineer-facing comparison remains:

```text
RLlib says:
Give me an env; I will run scalable RL algorithms on it.

Stable-Baselines3 says:
Give me an env; I will run standard reliable RL algorithms on it.

state_collapser says:
Give me an env or discovered transition system; I will construct a better
hierarchical/quotient decision structure around it.
```

But we now understand the deeper version:

```text
RLlib/SB3 can help train a policy once a training problem is presented.

state_collapser's job is to construct the tower-induced training problems.
```

So existing learners are useful, but they are not conceptually in charge.

They can train a stage.

They cannot be expected to know what the quotient tower means, what frozen
coarse behavior means, or what fiber the finer policy is supposed to stay
inside unless `state_collapser` presents that explicitly.

## The Correct Training Slogan

The current best slogan is:

```text
Train behavior in a coarser quotient tier.
Freeze it.
Lift/refine upward into the finer total space over it by training inside the
path fiber.
Repeat toward G_t^0.
```

Equivalently, for one adjacent projection:

```text
freeze behavior in G_t^{i+1};
train at G_t^i inside the fiber over that frozen behavior.
```

This should replace the earlier, confusing language about "lower-tier training"
or "base tier training."

## What The Musical Counterpoint Example Shows

The counterpoint example is not just motivational.

It is the cleanest intuitive model of the training process.

The bad flat problem is:

```text
search directly over full multi-voice textures.
```

The staged tower/fiber problem is:

```text
learn or choose a coarse musical scaffold;
freeze it;
train/choose richer textures that project back to that scaffold;
freeze the richer scaffold;
train/choose still richer textures in the fiber above it.
```

For example:

```text
write a good bassline or melody;
freeze it;
write another voice whose projection recovers that frozen line;
freeze the two-voice scaffold;
write a middle/decorative voice whose projection recovers the two-voice
scaffold.
```

This is not "use the earlier voice as context" in the loose feature-engineering
sense.

It is:

```text
train inside the fiber over the frozen earlier musical path.
```

That is why the example matters.

It keeps the design from degenerating back into generic RL metadata.

## What The Training Spine Becomes

The earlier flat training spine was:

```text
DecisionInput -> model -> ActionDecision -> collector -> replay -> learner
```

That is still a useful inner-loop spine.

But it is not the whole package-level training spine.

The package-level spine is now:

```text
TowerRuntime
    -> contraction schema
        -> tower projections
            -> frozen quotient behavior
                -> path fiber in finer total space
                    -> fiber-conditioned training stage
                        -> learner trains policy inside that stage
                            -> frozen artifact / tower policy bundle
```

So a better object sequence is:

```text
FrozenTierBehavior
    -> PathFiber
        -> FiberConditionedStage
            -> FiberPolicy / stage learner
                -> FrozenTierArtifact
                    -> TowerPolicyBundle
```

The ordinary RL machinery attaches inside `FiberConditionedStage`.

It does not define the stage.

## What Should Be Borrowed

The package should borrow from mature RL frameworks for:

- Torch model protocols
- tensor batches
- rollout collectors
- replay and trajectory storage
- checkpoint payloads
- manifests
- train/eval separation
- vectorized environments
- logging
- evaluation loops
- artifact output

This work is important, but it should be treated as professionalization of the
inner learner loop.

## What Must Be Package-Native

The package must own:

- total-space / quotient-tier vocabulary
- contraction schema
- tower projections
- path projection maps
- frozen quotient behavior
- fiber representation
- fiber admissibility masks
- fiber-conditioned transition semantics
- continuation inside a fiber
- reward aggregation across projection/fiber structure
- stage construction
- tower policy bundle construction

This is the nonstandard part.

This is where the careful design effort belongs.

## What We Should Stop Saying

We should stop saying:

```text
base graph
base tier
lower-tier training
lift resolver as if lift is externally invented
tower context as metadata
```

At least in mathematical/design documents.

Some code names may remain for compatibility in the short term, but future
design language should use:

```text
total graph
total tier
finer tier
coarser quotient tier
projection
fiber
fiber-conditioned stage
frozen quotient behavior
```

## What This Means For The Next Blueprint

The next blueprint should probably not start with:

```text
How do we add PyTorch models?
```

It should start with:

```text
How do we represent frozen quotient behavior and the path fiber over it?
```

Then it should ask:

- How do we expose a fiber-conditioned stage to a learner?
- How do masks represent fiber admissibility?
- How do collectors stay inside or diagnose departure from the fiber?
- How do rewards and continuation behave inside the fiber?
- What does a frozen artifact contain?
- What does a tower policy bundle contain?
- What is the simplest counterpoint-like example that proves the semantics?

Only after that should the design import standard RL maturity surfaces:

- tensors
- devices
- replay
- checkpoints
- manifests
- external framework adapters

## Current Understanding In One Sentence

`state_collapser` should use standard RL framework engineering to train
policies, but its core maturity problem is package-native: representing and
training within path fibers over frozen quotient-tier behavior in a tower whose
total space is `G_t^0`.

### PO Follow-Up

Question: To what extent should we be reproducing stuff in those other libraries, and to what extent shoudl be jsut have interfaces or like calls to them?

### Codex Response

The rule should be:

```text
Reproduce only the minimum machinery needed to make tower/fiber semantics
package-native and enforceable.

Interface with mature RL libraries for generic algorithm and optimization
machinery wherever the tower semantics can be cleanly preserved at the
boundary.
```

So the split is not:

```text
build everything ourselves
```

versus:

```text
delegate everything to RLlib/SB3
```

The split is:

```text
own the semantics;
borrow or adapt the commodity training machinery.
```

## What `state_collapser` Should Implement Itself

`state_collapser` should implement package-native versions of anything that
defines the tower/fiber training problem.

That includes:

- tower construction
- contraction schemas
- total-space / quotient-tier projections
- path projection or finite-episode projection
- frozen quotient behavior
- fiber representation
- fiber-conditioned stage construction
- masks expressing fiber admissibility
- continuation semantics inside a fiber
- transition records carrying tower/fiber context
- reward aggregation across projection/fiber structure
- tower policy bundle metadata
- package-level manifests that record schema/tower/fiber facts

These are not commodity RL objects.

If they are delegated too early to RLlib or SB3, the package loses the thing
that makes it `state_collapser`.

## What `state_collapser` Should Provide As Small Reference Implementations

There are some generic RL components where the package should have small,
boring reference versions, but not aspire to compete with mature frameworks.

Examples:

- a simple Torch model protocol
- a minimal policy/value model example
- a simple tensor batch object
- a small replay or trajectory buffer sufficient for package tests
- a reference training loop
- a basic checkpoint format for package-native examples
- a lightweight benchmark artifact writer

The purpose of these is not to beat RLlib or SB3.

The purpose is:

- test the package semantics without external framework complexity
- provide examples users can read
- make the package self-contained enough for research
- define adapter contracts against something concrete

These should be deliberately modest.

If a component starts turning into "our own PPO framework" or "our own
distributed rollout system," that is probably a smell.

## What Should Mostly Be External Adapters

The package should prefer adapters or interfaces for mature commodity machinery
such as:

- PPO/SAC/DQN/A2C algorithm implementations
- large replay systems
- distributed rollout
- multi-GPU training
- hyperparameter tuning
- advanced logging dashboards
- production experiment management
- large vectorized environment infrastructure

Those are the places where RLlib, Stable-Baselines3, CleanRL, Tianshou, Acme,
TorchRL, and similar systems already have real engineering.

`state_collapser` should not reproduce them unless there is a very specific
tower-semantic reason.

## The Adapter Shape

The right adapter shape is:

```text
FiberConditionedStage
    -> adapter
        -> external learner/framework
            -> trained policy/model artifact
                -> state_collapser FrozenTierBehavior / TowerPolicyBundle
```

The adapter must preserve package semantics at the boundary.

For example, an SB3 adapter should not merely wrap a stage as a Gymnasium env
and hope the semantics survive. It should make clear:

- what the stage observation is
- how fiber admissibility becomes action masking or environment constraints
- how illegal departures from the fiber are handled
- how termination/truncation maps to fiber continuation
- how the trained policy artifact is brought back into
  `FrozenTierBehavior`
- what manifest metadata records the tower schema and frozen quotient behavior

Similarly, an RLlib adapter might use multi-policy or multi-agent machinery,
but the tower/fiber semantics should still be package-native.

RLlib should not become the source of truth about what a tier means.

## Dependency Posture

The package should probably keep hard dependencies small.

Possible posture:

- core `state_collapser`: no heavy RL framework dependency
- `rl` extra: Gymnasium-facing and standard RL integration dependencies
- `ml` extra: Torch-facing model/tensor dependencies
- optional future extras:
  - `sb3`
  - `rllib`
  - `torchrl`

That lets the core package remain about graph/tower/fiber semantics, while
users who want a particular learner stack can install the relevant adapter.

## Practical First Choice

The first serious version should probably implement:

1. package-native `FiberConditionedStage`
2. package-native transition/batch/checkpoint/manifest contracts
3. a small readable reference learner or Torch loop
4. one adapter to an external training style only after the stage semantics are
   stable

The first external adapter should probably be SB3-shaped before RLlib-shaped,
because one `FiberConditionedStage` can plausibly be exposed as a
Gymnasium-style environment. That is easier to reason about than RLlib's
distributed and multi-policy machinery.

But even for SB3, the adapter should be treated as:

```text
a way to train a package-defined stage
```

not:

```text
the definition of the stage.
```

## Short Answer

`state_collapser` should reproduce:

- tower/fiber semantics
- minimal reference training components
- manifests/checkpoints needed to preserve package meaning

`state_collapser` should interface with:

- mature neural RL algorithms
- large-scale rollout/training systems
- advanced replay and distributed infrastructure
- external logging/tuning ecosystems

The boundary is:

```text
If the component determines what the quotient tower means, own it.

If the component merely optimizes a policy once the fiber-conditioned stage is
defined, adapt to it.
```

### PO Follow-Up

Ok. Do an EXTENSIVE code review of the whole repo, and re-evaluate how much of the structure you described in your last reply is already present *in some form*.

### Codex Response

Yes. I re-read the relevant runtime, partition, training, adapter, benchmark,
example, and test surfaces. The answer is more favorable than my previous
high-level framing implied, but also sharper.

The short version:

`state_collapser` already contains much of the package-native semantic spine in
embryonic form.

It does not yet contain the unified fiber-conditioned training architecture.

The repo is not blank on this problem. It has a serious partition tower runtime,
incremental maintenance, adjacent refinement-fiber queries, lift-candidate
queries, action-decision surfaces, collectors, transitions, masks, continuation
semantics, reference learners, Gymnasium adapters, smoke benchmarks, and an
older exploit/explore active-tier control stack. Those are real structures.

What is missing is the conceptual consolidation layer that names and composes
these pieces as:

```text
frozen quotient-tier behavior
    -> path fiber over that behavior
        -> fiber-conditioned stage
            -> learner/model/training loop
                -> frozen behavior artifact
                    -> next finer stage
```

So the next implementation should not be greenfield. It should be a
consolidation/refactor that lifts existing pieces into the correct mathematical
surface.

## High-Level Re-Evaluation

My earlier answer said:

```text
If the component determines what the quotient tower means, own it.

If the component merely optimizes a policy once the fiber-conditioned stage is
defined, adapt to it.
```

After reviewing the repo, I would refine that to:

```text
state_collapser already owns most of the quotient-tower meaning layer.

state_collapser already owns a minimal research training layer.

state_collapser does not yet own the missing middle layer:
path fibers over frozen quotient-tier behavior.
```

That missing middle layer is the important one.

The code already understands a tower as nested state/action partitions
decorating the discovered total transition graph. The code already has
incremental updates and enough query methods to ask about state cells, action
cells, representatives, internal edges, adjacent refinement fibers, and
primitive lift candidates. That is the hard structural substrate.

But the code does not yet turn a frozen path or policy at tier `i + 1` into a
finer tier-`i` training problem whose admissible behavior is precisely the path
fiber over that frozen downstairs/coarser behavior.

That is the real architectural gap.

## What Is Already Present In Strong Form

### 1. The Young-tableaux / nested-partition tower runtime is real.

The new runtime model is not merely documented. It is implemented in
`src/state_collapser/tower/partition`.

The most important object is `PartitionTower` in
`src/state_collapser/tower/partition/tower.py`.

It owns:

- a `BaseGraphRegistry`
- persistent `state_layers`
- persistent `action_layers`
- a `ContractionSchema`
- loop/internal-edge policy
- reward/internal aggregation configuration
- incremental update results
- optional morphism information

Key evidence:

- `PartitionTower` stores state/action partition layers directly at
  `tower.py:42-56`.
- `initialize(...)` builds tier `0` as singleton state cells plus outgoing action
  collections, then applies ordered contraction blocks at `tower.py:61-149`.
- `update_with_delta(...)` incrementally registers newly discovered states and
  edges and contracts only newly assigned edges at `tower.py:278-367`.
- `TowerRuntime` now defaults to the partition backend and keeps legacy quotient
  readouts lazy/compatibility-only at `runtime.py:56-96` and `runtime.py:199-210`.

This means the code has already absorbed the major TeX/document shift:

```text
old picture: rebuild quotient graphs directly
new picture: maintain state/action partition tables decorating the total graph
```

That part is fundamentally in place.

### 2. The contraction schema / ordered edge-block story is implemented.

The repo has `ContractionSchema` and concrete schema types in
`src/state_collapser/tower/partition/schema.py`.

Key evidence:

- `ContractionSchema.assign_edge(...)` and `ordered_blocks(...)` are the package
  surface for assigning discovered total-space edges to contraction blocks at
  `schema.py:19-30`.
- `SchemaAssignmentStore` persists assignments so old edge assignments remain
  stable at `schema.py:41-95`.
- `DimensionwiseSchema`, `LabelBlockSchema`, `SeededRandomRateSchema`, and
  `DiscoveryOrderChunkSchema` cover several first-scope scheduling modes at
  `schema.py:112-208`.

This is the concrete code-level analogue of the paper's:

```text
\mathcal{A}_t^0 = \Sigma_0^1 \sqcup \Sigma_0^2 \sqcup \cdots \sqcup \Sigma_0^d.
```

That is not missing.

### 3. The repo already has local fiber-like query primitives.

This was the biggest correction to my earlier mental model.

`PartitionTower` already exposes:

- `state_cell_members(...)`
- `outgoing_action_cells(...)`
- `action_cell_members(...)`
- `representative_edges(...)`
- `internal_edges(...)`
- `lift_candidates(...)`
- `refinement_fiber(...)`

Key evidence:

- state-cell and action-cell query methods are at `tower.py:151-245`.
- `lift_candidates(...)` returns primitive edges that can realize an abstract
  action cell at `tower.py:247-259`.
- `refinement_fiber(...)` returns adjacent finer cells under a tier cell at
  `tower.py:261-276`.
- the corresponding private state/action fiber methods are at
  `tower.py:399-449`.
- tests explicitly cover these in
  `tests/tower/partition/test_queries_and_lift.py:45-99`.

This means the repo already has the low-level operation:

```text
given a cell/action at tier i, ask what finer things lie over it
```

But it does not yet have the high-level operation:

```text
given a frozen path/policy behavior at tier i+1,
construct the tier-i path/action/state training stage that fibers over it
```

That distinction matters.

The current `refinement_fiber(...)` is an adjacent cell-fiber query. It is not
yet a path-fiber object. It is a necessary primitive, not the finished training
surface.

### 4. Incremental tower maintenance is implemented in the runtime path.

`TowerRuntime` already updates the partition tower by local visible deltas.

Key evidence:

- `TowerRuntime.step(...)` refreshes only the current and next local vistas,
  then calls `_update_partition_tower(...)` at `runtime.py:145-174`.
- `_update_partition_tower(...)` computes `delta_states` and `delta_edges`
  against the partition tower registry at `runtime.py:355-385`.
- `PartitionTower.update_with_delta(...)` registers the deltas and contracts
  newly assigned edges through the existing layers at `tower.py:278-367`.
- `_contract_edge_from_tier_downward(...)` propagates a new contraction from its
  assigned tier through existing deeper/coarser layers at `tower.py:619-645`.

So the repo already made the important runtime transition:

```text
not repeated global reconstruction
but amortized local maintenance
```

This is a serious foundation for the scaling story.

### 5. Compatibility quotient readouts are intentionally not the runtime model.

The partition package explicitly states that `QuotientTierView` objects are
compatibility readouts, not the source of truth.

Key evidence:

- `src/state_collapser/tower/partition/__init__.py:1-6` says the partition tower
  is the runtime model and `QuotientTierView` objects are readouts.
- `PartitionTower.to_quotient_tier_views(...)` is a readout method at
  `tower.py:384-389`.
- `TowerRuntime.compatibility_quotient_tiers(...)` lazily builds those readouts
  only when requested at `runtime.py:199-210`.

This is exactly the posture the paper wants.

### 6. Reward aggregation is already more general than mean/average.

The reward aggregation concern we discussed is already reflected in code.

Key evidence:

- `RewardAggregationName` includes `SUM`, `MEAN`, `MAX`, `SOFTMAX`, `P_MEAN`,
  `P_NORM`, and `CUSTOM` at `reward_aggregation.py:11-20`.
- `aggregate_rewards(...)` implements those options at
  `reward_aggregation.py:53-94`.
- internal-edge aggregation also supports `SUM`, `MEAN`, and `MAX` at
  `internal_aggregation.py:10-16`.

This means the package already avoids hard-coding average direct image as the
only reward projection rule.

### 7. The training spine exists as a first-scope research surface.

The repo already has a clean small training package under
`src/state_collapser/training`.

Key evidence:

- `ActionSelectionInput` carries observation, current state, runtime snapshot,
  tower position, mask, history, active tier state, frozen context, and
  diagnostics at `inputs.py:17-29`.
- `ActionDecision` carries chosen action, probabilities, logits, Q-values,
  value estimate, and diagnostics at `decisions.py:9-18`.
- `TrainingTransition` carries source/target inputs, reward,
  terminated/truncated, bootstrap semantics, diagnostics, runtime summary,
  tower position, active tier, and frozen context version at
  `transitions.py:36-53`.
- `StepCollector` and `EpisodeCollector` are implemented at
  `collectors.py:83-253`.
- `BootstrapSemantics` handles truncation/continuation at
  `continuation.py:8-44`.
- `TabularQLearner` provides a minimal mask-aware learner at
  `learners.py:45-154`.
- `run_reference_online_loop(...)` and `run_reference_episode_loop(...)` are
  present at `reference_loops.py:19-110`.

So the repo already has:

```text
DecisionInput -> learner -> ActionDecision -> collector -> transition -> update
```

What it lacks is:

```text
FiberConditionedStage -> learner -> FrozenTierBehavior
```

The existing loop is flat tower-aware training keyed by tower position. It is
not yet staged fiber training over frozen quotient behavior.

### 8. Masks, continuation, and diagnostics are already present.

This is important because masks are probably the first implementation mechanism
for fiber admissibility.

Key evidence:

- `mask_from_info(...)`, `legal_actions(...)`, and `action_is_legal(...)` are in
  `masks.py:8-42`.
- `StepCollector.collect_step(...)` rejects masked-off actions at
  `collectors.py:125-134`.
- `StepCollector.collect_step(...)` records bootstrap/continuation behavior at
  `collectors.py:153-179`.

This means the first `FiberConditionedStage` does not need to invent action
masking from scratch. It can use the existing mask machinery and make
fiber-admissibility a particular source of masks/constraints.

### 9. Gymnasium integration exists, but only at the env/transition boundary.

The repo has a real Gymnasium-like adapter layer.

Key evidence:

- `StateCollapserGymHooks` defines hooks for state keys, action keys, edge
  labels, and action masks at `adapters/gymnasium.py:48-55`.
- `StateCollapserGymWrapper` records realized transitions into an
  `ExploredGraph` at `adapters/gymnasium.py:90-207`.
- optional `rl` dependencies include Gymnasium and NumPy at
  `pyproject.toml:49-52`.

This is enough to say:

```text
state_collapser can observe external Gymnasium-like envs structurally
```

It is not enough to say:

```text
state_collapser can expose fiber-conditioned stages as Gymnasium envs
```

That adapter is still missing.

### 10. Optional dependency posture is already aligned with the design.

The package already keeps heavyweight dependencies optional.

Key evidence:

- core dependencies are tiny at `pyproject.toml:35-37`.
- `rl` extra contains `gymnasium` and `numpy` at `pyproject.toml:49-52`.
- `ml` extra contains `torch` at `pyproject.toml:53-55`.

This matches the proposed posture:

```text
core package owns graph/tower/fiber semantics
optional extras support RL/ML framework integrations
```

The code does not yet use the `ml` extra for real model training, but the
dependency boundary is already in the right shape.

### 11. Benchmarking exists as a smoke surface.

The repo has a benchmark module:

- `TowerRuntimeBenchResult` at `benchmarks/tower_runtime_bench.py:20-47`.
- `run_tower_runtime_benchmark(...)` at `benchmarks/tower_runtime_bench.py:50-108`.

It already compares:

- schema mode
- readout requested/not requested
- morphism requested/not requested
- discovered states/edges
- tower depth
- operations per second

This supports the previous statement that benchmarking is no longer absent.

But it is still a smoke benchmark, not the serious evaluation suite.

It does not yet produce durable benchmark artifacts, scaling curves, regression
thresholds, environment-family comparisons, or separate cost attribution for
fiber-stage construction.

### 12. The older exploit/explore active-tier stack is highly relevant.

This is the other major thing my prior high-level answer underweighted.

There is already a control package at `src/state_collapser/tower/control`.

It includes:

- `ActiveTierState`
- `ActiveTierController`
- `ControlAction`
- `FrozenLowerContext`
- `TierLearner`
- `LiftResolveExecutor`
- `ActiveTierTransition`
- control metrics/signals/config

Key evidence:

- `ActiveTierState` has tier direction helpers at `active_tier.py:8-67`.
- `ControlAction` includes `EXPLORE`, `TRAIN`, `DESCEND`, `LIFT`, and
  `EXPLOIT_EXECUTE` at `controller.py:20-27`.
- `FrozenLowerContext` exists at `frozen_context.py:8-17`.
- `TierLearner` has `behavior_action(...)`, `observe(...)`, `should_train(...)`,
  and `train(...)` at `learner.py:21-40`.
- `LiftResolveExecutor.execute(...)` is a protocol for realizing abstract
  active-tier actions through support context at `executor.py:12-24`.
- `ActiveTierTransition` has tier, source, action, target, aggregated reward,
  duration, context version, representative jump, and success at
  `transition.py:8-20`.
- `ExploitExploreTowerRuntime` wires controller, learner, executor, frozen
  contexts, lift/descend callbacks, signals, and metrics at
  `runtime.py:451-554`.

This is not the final fiber-conditioned training spine, but it is not throwaway.
It is a previous attempt at exactly the area we are now clarifying.

The best interpretation is:

```text
tower/control is proto-stage-control infrastructure
```

It should be refactored or wrapped, not ignored.

## What Is Present, But Under The Wrong Conceptual Name

### 1. `current_base_state` should probably become `current_total_state`.

The code still repeatedly uses "base state" for what the paper now calls the
total-space / tier-0 state.

Examples:

- `ActionSelectionInput.current_base_state` at `inputs.py:21-23`.
- `RuntimeSnapshotSummary.current_base_state` at `transitions.py:13-21`.
- `LiveRuntimeView.current_base_state` at `snapshot.py:72-88`.
- `TowerRuntime.reset(... current_base_state=...)` and
  `TowerRuntime.step(...)` throughout `runtime.py`.

This is not a functional bug, but it is a terminology bug. It will keep pulling
the engineering model back toward the old picture.

Given the latest mathematical discussion:

```text
G_t^0 is the total discovered transition graph.

G_t^{i+1} is downstairs/coarser relative to G_t^i.

The "base" of a fibration G_t^i -> G_t^{i+1} is context-dependent.
```

So code names like `current_base_state` are misleading now.

### 2. `FrozenLowerContext` has the wrong direction for the new semantics.

The object exists, and it is close enough to matter, but its name and docstring
are oriented around an older story:

```text
FrozenLowerContext
Lower-tier support treated as fixed while an active tier is trained.
```

In the current mathematical picture, when training tier `i`, the frozen thing is
usually coarser/downstairs behavior at tier `i + 1`, and the active training
problem is the finer/upstairs fiber at tier `i`.

So the object should probably become something like:

```text
FrozenQuotientBehavior
FrozenCoarserBehavior
FrozenTierBehavior
```

The existing fields are useful:

- supporting tier
- policy state
- representative data
- cached lift data
- version
- metadata

But the meaning should be re-centered around frozen quotient behavior and path
fibers over that behavior.

### 3. `lift_candidates(...)` is a primitive representative query, not the lift.

`PartitionTower.lift_candidates(...)` is valuable. It returns primitive edges
representing an abstract action cell, preferring those directly executable from
the current total state.

But this is not yet the full lift/fiber construction.

The mathematical lift we now mean is:

```text
paths in tier i that project to the frozen path/behavior in tier i+1
```

`lift_candidates(...)` is one local, one-step primitive used inside that story.

It should not be renamed away, but the future architecture should make clear:

```text
lift_candidates = local edge realization helper
PathFiber = stage-level admissible path/action space over frozen behavior
```

### 4. `refinement_fiber(...)` is adjacent-cell fiber, not path-fiber.

Same point, but even more important.

`refinement_fiber(tier, cell_id)` tells us which tier-`i-1` cells refine a
tier-`i` cell.

That is exactly the kind of primitive the path-fiber construction needs.

But a path fiber is not just a set of adjacent refining cells. It is a temporal
constraint over a frozen quotient path or policy behavior.

So this should probably remain a low-level tower query while a new training
module builds:

```text
FrozenTierBehavior
PathFiber
FiberConditionedStage
```

on top of it.

### 5. The active-tier controller knows about lift/descend, but not about
fiber-conditioned training.

`ActiveTierController` can choose to lift, descend, train, explore, or exploit.

That is close to the desired control flow, but not the same as:

```text
train coarser tier
freeze coarser behavior
construct finer path fiber over it
train finer tier inside that fiber
```

The controller currently gates on visit count, TD error, success, and
exploration pressure. It explicitly ignores the frozen context in
`controller.py:41-53`.

That is not wrong for its current tests. But it means this controller is not yet
the semantic owner of the freeze/fiber/lift curriculum.

## What Is Truly Missing

### 1. No first-class `FrozenTierBehavior`.

There is `FrozenLowerContext`, but no object whose job is:

```text
represent a frozen policy/path/behavior at tier i+1
```

The missing object should probably record:

- tier index
- behavior type
- policy/model/artifact identity
- deterministic or stochastic decision surface
- action vocabulary at that tier
- path or rollout prefix, if path-conditioned
- schema/tower version
- frozen artifact hash/version
- evaluation metrics at freeze time

This is package-native. External RL libraries cannot own this.

### 2. No first-class `PathFiber`.

There is no object that says:

```text
Here is the admissible tier-i training problem over this frozen tier-(i+1)
behavior.
```

The missing object should probably connect:

- tower projection map
- current fine tier `i`
- frozen coarser tier `i + 1`
- coarser path/action/cell sequence
- admissible fine states/actions at each step
- departure diagnostics
- local masks
- continuation rules

This is the key missing mathematical object.

### 3. No first-class `FiberConditionedStage`.

There is no stage object that packages:

- environment/runtime handle
- tower handle
- active fine tier
- frozen coarser behavior
- path-fiber view
- observation builder
- mask builder
- reward/continuation semantics
- diagnostics

This is the object that should be handed to a learner, wrapped as a Gymnasium
env, or adapted to SB3/RLlib later.

This is the main architecture gap.

### 4. No `TowerPolicyBundle`.

There is no package-level artifact representing:

```text
the collection of trained/frozen tier behaviors plus lift/fiber metadata
```

The current training outputs return Q-tables or episode summaries. That is fine
for examples. It is not enough for a trained tower-aware controller.

### 5. No neural model surface beyond optional dependency posture.

The package declares `torch>=2.4.0` in the `ml` extra, but the repo currently has
no serious Torch-facing training layer.

Missing:

- model protocols
- policy/value model interfaces
- tensorization of `ActionSelectionInput`
- tensor/device/dtype utilities
- batched decision inputs
- sequence handling
- optimizer/checkpoint payloads

That confirms the earlier RL maturity statement.

### 6. No replay/trajectory buffer beyond list-based reference learners.

`TabularQLearner.replay` is just a list of `TrainingTransition`.

`PlateSupportTierLearner.replay` is just a list of `ActiveTierTransition`.

That is enough for first-scope tests. It is not a replay-buffer design.

Missing:

- replay sampling
- capacity/eviction
- trajectory storage
- stage/fiber metadata indexing
- mask-aware batching
- episode boundaries
- serialization policy

### 7. No checkpoint/resume/manifest/artifact contract.

The repo has runtime snapshots and structured results, but no training artifact
contract.

Missing:

- experiment manifest
- checkpoint format
- replay metadata format
- frozen tier artifact format
- package version/git commit capture
- environment/schema/config identity
- benchmark artifact writer

This is still a major maturity gap.

### 8. No external learner adapters yet.

There is a Gymnasium wrapper for observing external envs, but no adapter of:

```text
FiberConditionedStage -> SB3-style env
FiberConditionedStage -> RLlib-style env/runner/module
FiberConditionedStage -> TorchRL/Tianshou-style batch source
```

This is fine. It should come after the stage semantics are stable.

## Code Review Findings

### Finding 1: The repo already has the hard tower runtime substrate.

Severity: positive architectural finding.

The partition runtime is exactly the kind of package-native component that
should not be delegated to RLlib/SB3. It owns the meaning of discovered graph,
state partition layers, action partition layers, contraction schemas,
incremental updates, loop handling, reward aggregation, and quotient readout.

This strongly supports the design direction:

```text
state_collapser should own tower semantics.
```

Action implication:

Do not rewrite the tower runtime. Build the fiber/stage training layer on top of
`PartitionTower` query methods.

### Finding 2: The repo has enough low-level fiber primitives to avoid a
greenfield path-fiber implementation.

Severity: positive architectural finding.

`refinement_fiber(...)`, `lift_candidates(...)`, `state_cell_members(...)`, and
`action_cell_members(...)` are already present and tested.

Action implication:

The first `PathFiber` implementation should be a composition layer over these
queries, not a second partition/tower implementation.

### Finding 3: There is a conceptual split between `training` and
`tower/control` that should be resolved.

Severity: medium design risk.

`src/state_collapser/training` contains the clean generic collector/learner loop.
`src/state_collapser/tower/control` contains the active-tier, frozen-context,
lift/descend/exploit/explore loop.

Both are relevant to the desired training spine, but they are currently separate
worlds.

The generic training layer knows about `active_tier_state` and
`frozen_lower_context` only as optional opaque fields. The control layer knows
about active tiers and frozen contexts but not about `ActionSelectionInput`,
`TrainingTransition`, collectors, masks, or the reference loops.

Action implication:

The refactor should introduce a bridge layer rather than choose one package over
the other. Likely shape:

```text
training/stages.py
training/fibers.py
training/frozen.py
```

or:

```text
tower/training/fiber_stage.py
```

with careful exports into `state_collapser.training`.

### Finding 4: Directional terminology is now actively dangerous.

Severity: medium design risk.

The code still says:

- `current_base_state`
- `BaseGraphRegistry`
- `FrozenLowerContext`
- `supporting_tier`
- `lower-tier support`

Some of this is harmless historical naming, but some of it directly conflicts
with the clarified math.

In the current picture:

```text
G_t^0 = total discovered transition graph
larger tier index = more quotient/coarser/downstairs
smaller tier index = finer/upstairs/executable
```

When training tier `i` over frozen tier `i + 1`, the frozen behavior is
coarser/downstairs, not finer/lower in the old loose sense.

Action implication:

Do not do a giant rename immediately, but future new surfaces should use the
correct vocabulary:

```text
total_state
fine_tier
coarse_tier
frozen_quotient_behavior
refinement_fiber
path_fiber
```

Then gradually alias/deprecate old names.

### Finding 5: The exploit/explore stack should be mined, not trusted as final.

Severity: medium design risk.

The active-tier runtime already has useful pieces:

- control actions
- active tier state
- frozen context version
- lift/descend callbacks
- tier learner protocol
- lift/resolve executor protocol
- active-tier transitions

But it is not yet the final freeze/fiber/lift architecture.

The strongest signal is that `ActiveTierController.decide(...)` accepts
`frozen_context` and then deletes it. That was reasonable for the first
exploit/explore slice, but it means the controller is not yet semantically
conditioned on frozen behavior.

Action implication:

Keep tests around this stack, but treat it as proto-control infrastructure.
Either refactor it to consume `FiberConditionedStage`, or leave it as a
reference controller while introducing a clearer stage API.

### Finding 6: The existing training loop is deliberately simple, and that is
still correct.

Severity: positive architectural finding.

The generic loop in `reference_loops.py` is exactly the kind of simple loop the
PO wanted: collector, learner act, collect step, observe, update, metrics.

It does not overbuild the training loop.

Action implication:

Keep the loop simple. Add better components around it:

- stage constructors
- fiber masks
- frozen behavior artifacts
- tensorization
- replay/trajectory stores
- manifests/checkpoints

Do not turn `run_reference_online_loop(...)` into a framework monster.

### Finding 7: The example training surfaces prove package-wide wiring, but not
serious learning.

Severity: low/medium maturity risk.

The example families all use the shared tabular training helper, and tests
verify schema pass-through and continuation semantics. This is good.

But the training results are still Q-tables keyed by tower-position tuples.
That demonstrates a package path, not a mature learner path.

Action implication:

Use examples as regression fixtures for new fiber-stage code, but do not mistake
them for final RL training infrastructure.

### Finding 8: The benchmark surface is useful but too narrow for the next claim.

Severity: medium maturity risk.

The benchmark can already vary readout and morphism flags, which is excellent.
But it does not yet produce the artifact/report shape needed to claim serious
scaling behavior.

Action implication:

Future benchmark work should add:

- artifact output
- environment-family matrix
- schema-mode matrix
- readout/morphism/fiber-stage ablations
- larger discovered graphs
- regression thresholds
- stored summaries suitable for release notes/paper plots

### Finding 9: External-framework integration should still wait.

Severity: strategic finding.

Because `FiberConditionedStage` does not yet exist, an SB3 or RLlib adapter right
now would wrap the wrong thing.

The Gymnasium wrapper is useful for observed external envs. But wrapping the
current flat training loop as SB3-ready would not preserve the actual tower/fiber
semantics we care about.

Action implication:

Implement package-native frozen behavior and fiber-stage objects first. Then
build one adapter, probably SB3-shaped, against that stable surface.

## Revised Answer To The PO Question

To what extent should we reproduce other RL libraries?

Less than before.

The repo already has a package-native structural layer and a minimal research
training spine. It should not reproduce mature learner ecosystems.

To what extent should we interface with them?

Eventually, more than before.

But the interface point is not the raw environment and not the current flat
training loop. The interface point should be:

```text
FiberConditionedStage
```

That stage should be native to `state_collapser`, because it is where the tower
math enters training.

After that, external systems can optimize policies on that stage.

## What The Next Blueprint Should Actually Target

The next design/implementation step should not be:

```text
Build RL framework maturity from scratch.
```

It should be:

```text
Consolidate the existing tower/query/training/control pieces into a first-class
fiber-conditioned training spine.
```

Specifically:

1. Define `FrozenTierBehavior` or `FrozenQuotientBehavior`.

2. Define `PathFiber` using existing `PartitionTower` projection,
   `refinement_fiber(...)`, action-cell, and lift-candidate queries.

3. Define `FiberConditionedStage` as the package-native object a learner trains
   against.

4. Teach `ActionSelectionInput` and `TrainingTransition` to carry explicit
   stage/fiber identity rather than opaque `frozen_lower_context`.

5. Decide whether `tower/control` becomes an implementation of this stage flow
   or remains a legacy/reference exploit/explore controller.

6. Keep `reference_loops.py` simple and component-oriented.

7. Add minimal tests proving:

```text
frozen coarser behavior induces admissible finer candidates
fiber masks exclude departures
collector transitions carry fiber identity
training a finer stage does not mutate frozen behavior
existing flat tabular examples still run
```

8. Only after that, consider SB3/Gymnasium-style adaptation.

## Final Assessment

The repo is closer than my previous answer suggested.

Already present in real code:

- partition-tower runtime
- ordered contraction schemas
- incremental updates
- lazy quotient readouts
- morphism support
- reward aggregation choices
- adjacent refinement-fiber queries
- primitive lift candidates
- training inputs/decisions/transitions
- masks and continuation semantics
- collectors and simple loops
- tabular reference learners
- Gymnasium observation wrapper
- smoke benchmarks
- proto active-tier/frozen-context control stack

Missing as first-class architecture:

- frozen quotient-tier behavior
- path fibers over frozen quotient behavior
- fiber-conditioned training stages
- tower policy bundles
- neural model/tensor surfaces
- replay/trajectory buffers
- checkpoints/manifests/artifacts
- external learner adapters
- serious benchmark artifacts

So the right mental model is:

```text
The tower runtime exists.
The research training surface exists.
The active-tier proto-control surface exists.

The missing piece is the semantic bridge:
freeze tier i+1, construct the tier-i path fiber over it, train inside that
fiber, freeze the resulting behavior, repeat.
```

That bridge is exactly the part `state_collapser` must own.


### PO Follow-Up

I think this brings us to a place where we're ready to start blueprinting. Just let me know if you agree.

### Codex Response

Yes. I agree.

I think this discussion is now ready to become a blueprint, and the blueprint
should be tightly scoped around one central architectural move:

```text
Promote the already-existing tower/query/training/control fragments into a
first-class fiber-conditioned training spine.
```

The important thing is that we should not write a blueprint for "make
`state_collapser` into RLlib" or "add a generic neural RL stack." That would be
the wrong abstraction level.

The correct blueprint should be about the missing semantic bridge:

```text
FrozenQuotientBehavior
    -> PathFiber
        -> FiberConditionedStage
            -> existing collector / learner / reference-loop surfaces
                -> FrozenQuotientBehavior for the next finer stage
```

The blueprint should therefore treat the current repo as having three existing
piles of material:

1. The partition tower runtime.

   This is already strong and should mostly be reused.

2. The generic research training surfaces.

   These are already good as component surfaces and should not be overbuilt.

3. The proto active-tier / frozen-context / lift-resolve control stack.

   This should be mined and either refactored into the new vocabulary or
   preserved as a reference/control prototype.

The blueprint should not spend most of its energy on Torch, SB3, RLlib,
checkpoints, or benchmark artifacts yet. Those matter, but they are downstream.
They become clean only after the package has a native object that says:

```text
This is the tier-i training problem induced by freezing this tier-(i+1)
behavior.
```

So yes: ready to blueprint.

The blueprint should probably be titled something like:

```text
Fiber-Conditioned Training Spine Blueprint
```

and it should live in:

```text
docs/design/RL_framework_maturity/
```

It should answer, in detail:

- What is a frozen quotient behavior?
- What is a path fiber in code?
- What is a fiber-conditioned stage?
- How does the stage use existing `PartitionTower` queries?
- How does the stage expose masks, observations, rewards, and continuation?
- How do existing `ActionSelectionInput`, `TrainingTransition`, collectors, and
  reference loops change?
- What happens to `FrozenLowerContext`, `LiftResolveExecutor`,
  `ActiveTierTransition`, and `ExploitExploreTowerRuntime`?
- What tests prove the new semantics?
- What work is explicitly deferred to later RL maturity phases?

My recommendation is:

```text
Blueprint first.
Then Phase.Stage.Action implementation gameplan.
Then branch before execution.
```

That order matches the prime-directive git practice and keeps this from turning
into a blurry framework rewrite.

