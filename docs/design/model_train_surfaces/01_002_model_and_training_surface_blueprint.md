# Model And Training Surface Blueprint

## Status

This document is the first blueprint for model and training surfaces in `state_collapser`.

It is downstream of:

- [01_001_model_and_training_surface_architecture.md]([state_collapser repository root]/docs/design/model_train_surfaces/01_001_model_and_training_surface_architecture.md)

It is written under the authority of:

- [docs/design/training_integration_surface_proposal.md]([state_collapser repository root]/docs/design/training_integration_surface_proposal.md)
- [docs/design/module_design_desiderata.md]([state_collapser repository root]/docs/design/module_design_desiderata.md)
- [docs/design/PyPl_readiness/01_001_python_package_readiness_scoping.md]([state_collapser repository root]/docs/design/PyPl_readiness/01_001_python_package_readiness_scoping.md)

This is a blueprint.

It is not:

- an implementation gameplan
- a benchmark harness note
- a backend-specific ML plan
- a promise to solve every professional hardening concern in one pass

Its job is to define the first correct package-facing training/model surface for `state_collapser`.

## Purpose

The purpose of this blueprint is to answer a concrete package-design question:

> What training/model surfaces should `state_collapser` expose so that a serious ML engineer can use the package’s runtime and tower machinery without being trapped inside one rigid package-owned training loop?

The blueprint answers that question in a way that is:

- compatible with the current mathematical model
- compatible with the current package architecture
- credible relative to contemporary RL practice
- honest about what is first-scope versus later hardening

## Central Design Claim

The central claim of this blueprint is:

> The first reusable training surface in `state_collapser` should be a **component surface package**, not a single official trainer framework.

That means the package should expose:

- problem/runtime-facing decision inputs
- action-decision outputs
- transition records
- rollout/collection surfaces
- learner/update surfaces
- metrics/reporting hooks
- a small number of reference loops

But it should **not** first harden around:

- one official package-owned training choreography

This is the most important architectural decision in the blueprint.

## What This Blueprint Is And Is Not Solving

### Solved here

This blueprint will fix:

- the first top-level training package shape
- the first reusable contracts
- the ownership split between package components and engineer-authored loops
- the relation between model surface and runtime surface
- the first-scope reference-loop story

### Not solved here

This blueprint does **not** yet attempt to settle:

- vectorized rollout semantics
- tensor/device placement contracts
- sequence-batch formatting
- serialization/checkpointing standards
- train/eval mode split details
- backend choice such as PyTorch/JAX/TensorFlow

Those are real next-stage hardening questions, but they are intentionally deferred.

## Non-Negotiable Constraints

The following constraints are fixed by the architecture note and are therefore law for this blueprint.

### 1. No policy-only narrowing

The package must not define its training/model boundary only in terms of:

\[
\pi_\theta : \mathcal{S}_H \to \mathcal{P}(\mathcal{A}_H \mid \mathcal{S}_H).
\]

That may remain a valid special case, but it is too narrow for the package boundary.

### 2. No master trainer as first principle

The package must not begin by building:

- one central trainer object that owns all training control flow

This would contradict the core design claim of the architecture note.

### 3. Runtime remains package-owned

The package must continue to own:

- hidden-graph interpretation
- explored/vista graph machinery
- tower construction
- runtime snapshots
- active-tier control surfaces

The training/model package is downstream of those surfaces.

### 4. Environment remains the problem shell

The environment must remain:

- the problem definition
- the transition/reward shell

The training/model package must not collapse the env/runtime split.

### 5. Current example-local loops remain valid reference loops

The package must treat current example training loops as:

- reference loops
- minimal smoke loops

and not declare them architectural mistakes.

## Canonical New Top-Level Package Area

The first training/model surface work should live under:

- `src/state_collapser/training/`

This package should become the home for reusable training-facing surfaces.

It should not begin by absorbing:

- all example-local training code
- all exploit/explore control code
- or all instrumentation code

Instead, it should begin as a reusable surface layer beneath future refactors of those examples.

## First-Scope Package Shape

The first-scope package shape should be:

```text
src/state_collapser/training/
    __init__.py
    inputs.py
    decisions.py
    transitions.py
    collectors.py
    learners.py
    metrics.py
    reference_loops.py
```

This is intentionally by **surface role**, not by RL-family label.

The package should **not** first organize as:

```text
training/
    policy_gradient/
    q_learning/
    actor_critic/
```

because that freezes the wrong taxonomy too early.

## First-Scope Surface Set

The following surfaces are the required first-scope surfaces.

## 1. Decision-Input Surface

### Required first contract

The package should define a first reusable decision-input object.

The canonical first name should be:

- `ActionSelectionInput`

### Why this name

This name is preferred over:

- `PolicyInput`

because the package must support more than literal policy models.

### Required semantics

The object must be able to carry, at minimum:

- env observation
- current base state
- current runtime snapshot
- current tower-position tuple
- optional action mask

### Allowed optional extensions in first scope

The first contract may also include optional fields for:

- finite history window
- active-tier state
- frozen lower context
- arbitrary diagnostics mapping

But those should remain optional and should not force every user into exploit/explore assumptions.

### First-scope principle

The first decision-input object should be:

- rich enough to support tower-aware learning
- simple enough to be inspectable
- not yet tensor-backend-specific

So in first scope, it should remain a typed Python data object, not a tensor bundle contract.

## 2. Action-Decision Surface

### Required first contract

The package should define a first reusable action-decision object.

The canonical first name should be:

- `ActionDecision`

### Required semantics

This object must be broad enough to carry several RL styles.

In first scope, it should allow optional fields for:

- chosen action
- action probabilities
- action logits
- action values or Q-values
- value estimate
- diagnostics mapping

The crucial point is that this object is a **decision surface**, not just an action sample.

### First-scope principle

The package should not require every caller to populate every field.

Instead:

- policy-style methods may populate probabilities or logits
- value-based methods may populate Q-values plus chosen action
- actor-critic methods may populate action fields plus a value estimate

This is the minimal generality needed to avoid a policy-only architectural mistake.

## 3. Transition Surface

### Required first contract

The package should define a first reusable transition object.

The canonical first name should be:

- `TrainingTransition`

### Required fields

The first contract should carry:

- source decision input
- chosen action
- scalar reward
- target decision input
- terminated flag
- truncated flag
- diagnostics mapping

### First-scope tower metadata

Because this is `state_collapser`, the transition object should also allow optional structural fields such as:

- runtime snapshot summary
- tower-position key
- active tier
- frozen-context version

The first contract does not need every one of these to be mandatory.

But it must be designed so they can live naturally inside the object.

### Why this matters

This object becomes the shared handoff surface between:

- collectors
- replay/buffers later
- learners
- metrics hooks
- engineer-authored loops

## 4. Collector Surface

### Required first contract

The package should define a first collector protocol or minimal collector object family.

The canonical first names should be something like:

- `StepCollector`
- `EpisodeCollector`

### First-scope ownership

The collector surface should own:

- env/runtime stepping
- packaging transitions
- simple episode-level accumulation

It should not yet own:

- every evaluation concern
- every replay concern
- every checkpoint concern

### First-scope principle

The collector should exist to make engineer-authored loops easier, not to replace them.

That means the collector API should be composable:

- easy to call directly from a custom loop
- easy to wrap
- not the only route through the package

## 5. Learner / Updater Surface

### Required first contract

The package should define a first general learner/update protocol.

The canonical first name should be:

- `Learner`

or if distinction is needed:

- `TrainingLearner`

### Why not reuse `TierLearner` directly?

`TierLearner` is important and should remain valid.

But it is:

- tied to the first exploit/explore controller
- active-tier-specific

So the first package-wide learner surface should be broader.

### Required first methods

The first contract should support at least:

- `act(...)` or equivalent decision-production method
- `observe(...)` or equivalent transition-ingest method
- `update(...)` or equivalent training step

The exact names can shift slightly, but the separation must remain:

- action-decision production
- transition ingestion
- parameter update

### Relationship to `TierLearner`

`TierLearner` should later either:

- be adapted to this broader surface

or:

- remain a higher-level control-specific special contract built on top of it

This blueprint does not force that full unification immediately.

## 6. Metrics / Reporting Surface

### Required first contract

The package should define a minimal metrics/reporting hook surface.

The canonical first names should be something like:

- `TrainingMetrics`
- `MetricsHook`

### Required first-scope behavior

This surface should allow loops and collectors to report:

- episodic return
- success/failure
- step counts
- optional tower depth
- optional control/tier diagnostics

### First-scope principle

This should be a hook/callback/reporting surface, not yet a full experiment manager.

That is enough to make:

- reference loops
- example loops
- benchmark harnesses

much more coherent later.

## 7. Reference Loop Surface

### Required first package role

The package should include a small `reference_loops.py` surface.

Its role is to hold:

- minimal reusable loop templates

not:

- the one official trainer everyone must use

### Required first examples

The first reference loops should probably include:

1. `run_reference_online_loop(...)`
   - minimal online acting/updating loop
2. `run_reference_episode_loop(...)`
   - minimal episode collector-driven loop

These do not need to be algorithm-rich.

They need to demonstrate:

- how the surfaces compose
- how an engineer can still own the orchestration

## What First Scope Explicitly Defers

The following are **not** first-scope deliverables.

### Deferred hardening topics

- vectorized collection
- multi-env batching
- device placement
- tensor-backend abstraction
- sequence/recurrent batch semantics
- checkpoint serialization
- evaluation-versus-training mode contract

### Deferred algorithm packages

- PPO package surfaces
- DQN package surfaces
- actor-critic package surfaces
- offline RL package surfaces

These may eventually belong under later:

- `learners/`
- `algorithms/`
- `buffers/`

but they should not be used to overdefine first-scope surface architecture.

## Required Relationship To Current Example Code

The first reusable training package should not require an immediate rewrite of every example.

Instead, the migration story should be:

### Stage 1

Define reusable surfaces under:

- `state_collapser.training`

### Stage 2

Let existing example loops continue to run unchanged.

### Stage 3

Gradually refactor examples such as:

- `plate_support_env`
- `rl_counterpoint_v3`

to use the new training surfaces where that clarifies code rather than merely shifting imports around.

This keeps the blueprint realistic.

## Required Relationship To `gymnasium`

The first training/model blueprint must remain fully consistent with the package’s current `gymnasium`-first direction.

That means:

- the env remains the primary problem shell
- the runtime sits above the env
- the training surfaces sit above both

The training package must not try to replace the role of `gymnasium`.

Instead, it should make it easier to build training systems over:

- `gymnasium.Env`
- `state_collapser` runtime

without forcing either to become the other.

## Required Relationship To Tower Runtime

The first reusable training surfaces must treat tower/runtime structure as:

- available structural information

not:

- mandatory baggage every learner must understand in full detail

That means:

- tower-aware features belong naturally in `ActionSelectionInput`
- tower-aware metadata belongs naturally in `TrainingTransition`
- tower-aware metrics belong naturally in the metrics surface

But the package must still allow:

- simpler learners
- flatter loops

to ignore some of that structure when appropriate.

This is important for professional usability.

## Mathematical Boundary

The package-facing model boundary should now be fixed as:

\[
\mathcal{M}_\theta : \mathcal{X}_H \longrightarrow \mathcal{D}_H
\]

where:

- `\mathcal{X}_H` is a package-defined decision-input space
- `\mathcal{D}_H` is a package-defined action-decision surface

### First-scope interpretation

In first scope:

- `\mathcal{X}_H` is represented by `ActionSelectionInput`
- `\mathcal{D}_H` is represented by `ActionDecision`

This should be treated as the canonical package-facing abstraction.

Literal policy models:

\[
\pi_\theta : \mathcal{S}_H \to \mathcal{P}(\mathcal{A}_H \mid \mathcal{S}_H)
\]

remain valid as one special case inside this broader boundary.

## Public API Intent

The first public-facing training package should be small.

It should aim eventually to export only:

- the main data objects
- the main protocols
- the reference loops

and not every internal helper.

This matters for PyPI readiness and public package professionalism.

## Acceptance Standard

The first implementation of this blueprint will count as faithful only if all of the following are true:

1. a new `state_collapser.training` package exists
2. it is organized by surface role, not algorithm-family label
3. it defines a first reusable decision-input object
4. it defines a first reusable action-decision object
5. it defines a first reusable transition object
6. it defines at least one collector-facing surface
7. it defines at least one general learner/update-facing surface
8. it defines a minimal metrics/reporting surface
9. it defines reference loops without hardening into one master trainer
10. it does not contradict the env/runtime/tower ownership boundaries already fixed elsewhere in the repo

If the implementation instead yields:

- a new opaque central trainer
- a policy-only model interface
- a top-level split by RL family
- or a collapse of env/runtime/training ownership

then the blueprint has failed.

## Next Document

The next document after this blueprint should be:

- an implementation gameplan in `Phase.Stage.Action` form

That gameplan should take as fixed:

- the first package shape under `src/state_collapser/training/`
- the first reusable surface set
- the decision not to build one rigid master trainer
- the deferral of next-stage hardening topics

## Remaining Questions Before The Implementation Gameplan

The blueprint is now strong enough to support a gameplan, but there are still a few implementation-binding questions that should be answered explicitly before the gameplan is written.

These are not broad architecture questions anymore.

They are narrow execution-shape questions.

### Question 1

In first scope, should `src/state_collapser/training/learners.py` contain:

- only protocols and summary/result dataclasses

or should it also contain:

- one or more first concrete reference learners, such as a tabular learner

#### PO Answer:
Explain the issue to me.

#### LLM Response:

The issue is about where the first **concrete** learning behavior should live.

There are two different ways to start:

1. keep `learners.py` very abstract at first
   - protocols
   - update summaries
   - maybe small result dataclasses
   - no actual learner implementation

2. let `learners.py` also contain one first concrete learner
   - probably a simple tabular learner
   - mainly so the new training package is immediately runnable end to end

Why this matters:

- if we choose **protocols only**, the package surface stays cleaner and more architectural
- but then the first real runnable reference loop may still depend on example-local concrete learner logic somewhere else

- if we choose **protocols plus one concrete learner**, then the package gets an immediate runnable vertical slice
- but it also risks making the first concrete learner feel more canonical than it really is

My recommendation:

- first scope should include:
  - the protocol
  - the summary/result dataclasses
  - and **one very explicitly non-canonical reference learner**

Why I recommend that:

- it keeps the package runnable
- it gives the new surfaces a real end-to-end demonstration
- it avoids a purely abstract training package that still secretly depends on old example-local concrete logic to work

But the concrete learner should be framed as:

- reference
- minimal
- temporary

not:

- the package’s official long-term learner design.

#### PO Follow-Up:
I support your recommendation.

### Question 2

In first scope, should `src/state_collapser/training/collectors.py` contain:

- only collector protocols

or should it contain:

- concrete `StepCollector` and `EpisodeCollector` implementations immediately

#### PO Answer:
Explain the issue to me.

#### LLM Response:

The issue is similar, but on the data-collection side rather than the learner side.

There are again two plausible first moves:

1. define only collector protocols
   - which says what a collector must do
   - but does not yet give the package a real working collector

2. define actual first collector implementations immediately
   - e.g. `StepCollector`
   - e.g. `EpisodeCollector`

Why this matters:

- if we choose **protocols only**, the architecture stays cleaner at first
- but the package still lacks a real reusable data-collection surface
- and the reference loops would either:
  - duplicate collection logic
  - or keep depending on older example-local rollout code

- if we choose **concrete collectors immediately**, then:
  - the package gets real reusable collection behavior
  - the loops become much more obviously component-based
  - and engineers can actually use the new package surfaces instead of just reading them

My recommendation:

- first scope should include **concrete `StepCollector` and `EpisodeCollector` implementations immediately**

Why:

- collectors are one of the most natural component boundaries in RL
- they are central to the PO’s “give me the parts, not the choreography” idea
- and they are much less dangerous to concretize early than, say, algorithm-family learners

So here I would lean more strongly toward:

- not just protocols
- but real first concrete collectors in scope one

#### PO Follow-Up:
I agree. First scope should include concrete `StepCollector` and `EpisodeCollector` implementations immediately

### Question 3

Should the first `reference_loops.py` surface:

- depend only on the new generic training surfaces

or is it acceptable in first scope for it to adapt current example/runtime patterns directly while the package is in transition

#### PO Answer:
Explain the issue to me.

#### LLM Response:

The issue here is about how pure or transitional the first `reference_loops.py` should be.

There are two paths:

1. make `reference_loops.py` depend **only** on the new generic training surfaces
   - collector objects
   - learner surfaces
   - decision inputs
   - transition objects
   - metrics hooks

2. allow `reference_loops.py` to temporarily adapt existing example/runtime patterns directly
   - while the package is still migrating

Why this matters:

- if we insist on **only the new generic surfaces**, the first implementation is cleaner and more principled
- but it may force a larger first-scope build, because all the generic surfaces must be concrete enough before any loop is runnable

- if we allow **direct adaptation of current example/runtime patterns**, then the migration is easier
- but the first reference loops are less pure as demonstrations of the new architecture

My recommendation:

- first scope should aim for:
  - `reference_loops.py` built primarily on the new generic training surfaces
- but it is acceptable if those loops still consume the current runtime pattern directly where necessary

In other words:

- the loops should not secretly be just copies of old example training files
- but they also do not need to wait for every future abstraction to be perfect before becoming runnable

So I would phrase the rule as:

- generic surfaces first in spirit and structure
- transitional runtime adaptation allowed where needed

#### PO Follow-Up:
Yes I agree.

### Question 4

Should the first reusable training surfaces be purely package-internal at first, or should the initial implementation already be aiming at a small public API under:

- `state_collapser.training`

#### PO Answer:
My intuition is purely package-internal at first, and then we can make the whole fucking API as the project fo some later Phase.

#### LLM Response:

I agree with that.

I think that is the safer and more professional first move.

Why:

- these surfaces are still being designed for correctness of decomposition
- we do not yet want to make stability promises too early
- keeping them package-internal first gives us freedom to:
  - rename
  - merge
  - split
  - refactor

without pretending we already have a settled public API

So my recommendation is:

- implement `state_collapser.training` in first scope as a **real internal package surface**
- use it immediately in package code and reference loops
- but do **not** yet treat it as a finalized public API promise

That fits very well with the repo’s current maturity level.

#### PO Follow-Up:
I support your recommendation.

### Question 5

For first scope, should the gameplan require refactoring at least one existing example loop such as:

- `plate_support_env`

or:

- `rl_counterpoint_v3`

to use the new training surfaces before the work counts as complete, or is defining the reusable surfaces plus reference loops enough for first completion

#### PO Answer:
Explain the issue.

#### LLM Response:

The issue is about what counts as "enough reality" for first completion.

There are two plausible completion standards:

1. **surface-complete only**
   - define the reusable training package pieces
   - define the reference loops
   - stop there

2. **surface-complete plus one real migration**
   - define the reusable pieces
   - and refactor at least one existing example to use them

Why this matters:

- if we stop at **surface-complete only**, the architecture may still be too theoretical
- we would know the pieces exist, but not yet whether they actually improve real example code

- if we require **at least one real example refactor**, then:
  - we force a reality check
  - we see whether the surfaces are actually usable
  - we catch design mistakes earlier

The cost is:

- larger first-scope implementation
- more risk of getting dragged into example-specific cleanup

My recommendation:

- first completion should require:
  - the reusable package surfaces
  - the reference loops
  - **and at least one existing example loop refactored to use them**

Why I recommend that:

- otherwise the new training package risks becoming another abstract layer that is "ready later"
- one real refactor is the minimum proof that the new surface architecture actually works

I would not require every example to migrate in first scope.

But I do think requiring at least one real example migration is the healthier completion standard.

#### PO Follow-Up:
Yeah I want one real migration.
