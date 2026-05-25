# Fiber-Conditioned Training Spine Engineer Documentation Blueprint

## Status

Documentation blueprint.

This document is paired with
`01_002_fiber_conditioned_training_spine_blueprint.md`.

It designs the engineer-facing documentation that should be written alongside
the fiber-conditioned training spine.

It is not an implementation gameplan.

## Why This Document Exists

The Project Owner asked for the implementation blueprint and the documentation
blueprint to be made in parallel.

That request is strategically important.

The core risk in the fiber-conditioned training spine is not only that the code
could be wrong.

The deeper risk is that the code could be mathematically correct but unusable:

- too many terms
- unclear tier direction
- unclear relation to RLlib/SB3
- unclear relation to Gymnasium
- unclear role of the engineer's own training loop
- unclear distinction between tower queries and training stages
- unclear meaning of "freeze" and "lift"

The documentation must therefore act as a usability constraint on the API.

If the docs cannot explain the surface cleanly, the surface is probably not yet
designed well enough.

## Project Owner Attribution

This documentation blueprint directly reflects Project Owner guidance.

The Project Owner:

- asked to move construction/TODO material out of the README and into more
  appropriate contributor/design spaces
- identified that engineers need a plain explanation of what `state_collapser`
  is relative to RLlib and Stable-Baselines3
- approved the engineer-facing comparison:

```text
RLlib says:
Give me an env; I will run scalable RL algorithms on it.

Stable-Baselines3 says:
Give me an env; I will run standard reliable RL algorithms on it.

state_collapser says:
Give me an env or discovered transition system; I will construct a better
hierarchical/quotient decision structure around it.
```

- corrected the tower direction vocabulary
- insisted that the lift/freeze story is not an additional hidden mechanism but
  the literal path fiber over frozen quotient behavior
- asked for documentation to be designed alongside implementation because
  documentation exposes usability gaps

Codex's role here is to turn that clarified understanding into a concrete
engineer documentation plan.

## Documentation Thesis

The docs should teach engineers that `state_collapser` is a structural layer for
reinforcement learning, not a replacement for mature RL learner frameworks.

The central message should be:

```text
state_collapser constructs tower-aware training stages.

You bring or write the learner.

The package gives you the quotient/fiber structure that makes the learner's
problem better posed.
```

## Intended Audiences

### Audience 1: RL Engineer

This reader knows some combination of:

- Gymnasium
- Stable-Baselines3
- RLlib
- PyTorch
- rollout/collector/learner vocabulary

They may not know:

- quotient towers
- path fibers
- the specific `state_collapser` mathematical model

They need:

- quick orientation
- a runnable example
- clear boundaries with existing RL libraries
- explicit data surfaces
- enough math vocabulary to not misuse the package

### Audience 2: ML Engineer In Research Mode

This reader is comfortable writing custom loops and wants useful components.

They need:

- component surfaces, not a rigid `.learn(...)` framework
- masks
- transitions
- collector behavior
- stage/fiber metadata
- where to plug in their model

### Audience 3: Mathematical / Research Reader

This reader wants the implementation to match the paper.

They need:

- total graph vs quotient tiers
- tier direction
- state/action partition tower
- path fiber semantics
- freeze/lift/refine interpretation
- links to design docs

### Audience 4: Future Maintainer

This reader needs to extend the package without breaking the theory.

They need:

- invariants
- naming rules
- compatibility notes
- examples of forbidden abstractions
- testing expectations

## Documentation Non-Goals

The documentation should not initially attempt to be:

- a full RL textbook
- a full Gymnasium tutorial
- a full RLlib guide
- a full Stable-Baselines3 guide
- a PyTorch model training manual
- a proof of the paper
- a benchmark report

It should instead explain:

```text
what this package uniquely owns,
how to use that surface,
and where ordinary RL tooling plugs in later.
```

## Proposed Documentation Structure

The documentation should be organized in layers.

### Layer 1: README

Purpose:

Fast orientation.

The README should stay relatively clean.

It should include:

- what the package is
- why it is not RLlib/SB3
- where the design docs live
- how to run the simplest examples
- status/maturity posture

It should not include:

- long construction TODOs
- implementation gameplans
- full theory
- full API details

The README should preserve the engineer-facing comparison already added:

```text
RLlib says: give me an env; I will run scalable RL algorithms on it.
SB3 says: give me an env; I will run standard reliable RL algorithms on it.
state_collapser says: give me an env or discovered transition system; I will
construct a better hierarchical/quotient decision structure around it.
```

### Layer 2: Contributing / Roadmap

Purpose:

Explain current development priorities without cluttering the README.

This should include:

- current roadmap
- research-mode package posture
- planned RL maturity phases
- branch/gameplan expectations

### Layer 3: Engineer Guide

Purpose:

Teach practical use.

Recommended folder:

```text
docs/usage/
```

Suggested files:

```text
docs/usage/01_001_what_state_collapser_is.md
docs/usage/01_002_tower_runtime_mental_model.md
docs/usage/01_003_training_surface_quickstart.md
docs/usage/01_004_fiber_conditioned_training.md
docs/usage/01_005_using_your_own_training_loop.md
docs/usage/01_006_gymnasium_integration.md
docs/usage/01_007_glossary.md
docs/usage/01_008_common_misunderstandings.md
```

These docs should be written after or alongside implementation, but the file set
should guide API design now.

### Layer 4: API Reference Notes

Purpose:

Bridge generated API docs and conceptual docs.

Suggested folder:

```text
docs/api_notes/
```

Suggested files:

```text
docs/api_notes/partition_tower.md
docs/api_notes/training_inputs_and_transitions.md
docs/api_notes/frozen_quotient_behavior.md
docs/api_notes/path_fiber.md
docs/api_notes/fiber_conditioned_stage.md
```

These should be concise, engineer-oriented notes, not exhaustive generated
reference.

### Layer 5: Design Docs

Purpose:

Preserve the deep reasoning history.

The existing design docs should remain the place for:

- architectural arguments
- blueprint history
- implementation gameplans
- open questions
- PO/Codex discussion record

The usage docs should link to design docs, but should not require reading them
for basic package use.

## Required Engineer Narrative

The docs should present the package through the following story.

### Step 1: You Have An Environment Or Transition System

An engineer starts with:

- a Gymnasium-like environment
- a package example environment
- an already discovered transition graph
- or a custom hidden graph/runtime

The docs should say:

```text
state_collapser observes or builds a discovered transition graph from this.
```

### Step 2: The Package Builds A Tower

The docs should explain:

```text
G_t^0 is the discovered total graph.
Higher tier indices are coarser quotient tiers.
The runtime stores this as state/action partition tables, not as repeated
global graph rebuilds.
```

This must be stated in engineer language.

### Step 3: Coarser Behavior Can Be Frozen

The docs should explain:

```text
Once you have learned or specified behavior at a coarser tier, you can freeze
that behavior.
```

Freeze means:

- the behavior is treated as fixed
- it is identified by version/fingerprint/metadata
- finer training is conditioned on it
- finer training does not mutate it

### Step 4: Finer Training Happens In A Fiber

The docs should explain:

```text
At tier i, the learner is not choosing arbitrary fine behavior.
It is choosing among fine paths/actions that project down to the frozen
behavior at tier i+1.
```

This is the heart of the package.

It should be repeated in multiple forms:

- short text
- diagram
- tiny graph example
- code example

### Step 5: The Engineer Still Owns The Loop

The docs should explain:

```text
The package gives you the stage, masks, transitions, diagnostics, and tower
context.
You can write the training loop or later adapt to an external learner.
```

This preserves the PO's principle:

Training loops should remain simple and engineer-owned.

The package should provide good components.

## Required Diagrams

The docs should include at least three diagrams.

### Diagram 1: Package Positioning

```text
Gymnasium env / discovered transition system
    -> state_collapser tower + fiber-conditioned stage
        -> engineer-owned learner loop
            -> frozen behavior / policy bundle
```

### Diagram 2: Tier Direction

```text
G_t^0  ->  G_t^1  ->  G_t^2  -> ...
fine      coarser    coarser still
total     quotient   quotient
upstairs  downstairs downstream
```

### Diagram 3: Freeze And Fiber

```text
frozen behavior at tier i+1
        ^
        | projection of paths
        |
fiber of admissible paths at tier i
```

The third diagram is the most important.

It should make the "lift" feel literal rather than magical.

## First User-Facing Example

The first docs example should not use PyTorch.

It should not use SB3 or RLlib.

It should use a tiny graph or existing simple environment to show semantics.

Suggested example:

```text
1. Build or discover a small graph.
2. Build a partition tower.
3. Choose a coarser tier action/path.
4. Freeze it as FrozenQuotientBehavior.
5. Construct PathFiber at the finer tier.
6. Ask for admissible actions or masks.
7. Step through FiberConditionedStage.
8. Show TrainingTransition carrying stage/fiber context.
```

The example should be short enough to read in one sitting.

The point is not performance.

The point is understanding.

## Second User-Facing Example

The second docs example should use an existing package environment.

Recommended:

```text
plate_support_env
```

Reasons:

- it already has tower runtime integration
- it already has tabular training examples
- it already has exploit/explore prototype support
- it is less semantically heavy than counterpoint

The example should show:

- normal flat tower-aware training
- then fiber-conditioned stage training
- what changes in the inputs/transitions
- what remains the engineer's responsibility

## Optional Conceptual Example

A short conceptual counterpoint example should appear in prose.

Purpose:

Explain the human intuition:

```text
write a good coarser/downstairs musical scaffold
freeze it
write a compatible finer/accompanying line in the fiber over it
repeat
```

This should be treated as intuition, not as the first runnable example.

The runnable example should be smaller and more mechanical.

## Glossary Requirements

The documentation must define:

- total graph
- quotient tier
- tier index
- finer tier
- coarser tier
- upstairs
- downstairs
- contraction schema
- state cell
- action cell
- action collection
- frozen quotient behavior
- path fiber
- fiber-conditioned stage
- lift candidate
- refinement fiber
- action mask
- stage context
- tower policy bundle

Each term should have:

- one plain English sentence
- one package/code reference
- one "do not confuse with" note where appropriate

Example:

```text
Path fiber:
The admissible finer-tier paths whose projection matches a frozen coarser-tier
behavior.

Do not confuse this with PartitionTower.refinement_fiber(...), which is a local
adjacent-cell query used to build path fibers.
```

## Common Misunderstandings Page

The docs should explicitly prevent recurring conceptual errors.

Required entries:

### Misunderstanding 1

"`G_t^0` is the base graph."

Correction:

`G_t^0` is the total discovered graph. "Base" is relative to a projection.

### Misunderstanding 2

"Lift is a separate heuristic resolver."

Correction:

Lift is the path fiber of the tower projection. Resolver code may choose among
fiber candidates, but it does not define the fiber.

### Misunderstanding 3

"state_collapser is an RL training framework like RLlib."

Correction:

`state_collapser` constructs tower/fiber decision structure. Learners optimize
policies on stages produced by that structure.

### Misunderstanding 4

"The package should hide the training loop."

Correction:

The package should provide strong components. The engineer may still own the
loop.

### Misunderstanding 5

"A local refinement fiber is already the whole path fiber."

Correction:

Local refinement fibers are query primitives. A path fiber is a temporal
training object over frozen coarser behavior.

## API Documentation Requirements

### `FrozenQuotientBehavior`

The docs must answer:

- What is being frozen?
- Why is it quotient/coarser behavior?
- What does immutability mean?
- How does a learner produce one?
- What metadata should it carry?
- How is it used by a finer stage?

### `PathFiber`

The docs must answer:

- What projection is this fiber over?
- What existing tower queries does it use?
- How are admissible states/actions computed?
- How do masks come from the fiber?
- What happens when an attempted action departs from the fiber?

### `FiberConditionedStage`

The docs must answer:

- What does it wrap?
- What does it expose to the learner?
- How does it build `ActionSelectionInput`?
- How does it produce `TrainingTransition`?
- How does it interact with collectors?
- How would a future Gymnasium adapter wrap it?

### Existing Training Surfaces

The docs must explain how these change or remain stable:

- `ActionSelectionInput`
- `ActionDecision`
- `TrainingTransition`
- `StepCollector`
- `EpisodeCollector`
- `run_reference_online_loop`
- `TabularQLearner`

The core message:

```text
These stay simple.
Stage/fiber context makes them tower-aware in the new sense.
```

## Code Snippet Requirements

The docs should eventually include snippets for:

### Build A Tower

Show how an environment/runtime produces or exposes a `PartitionTower`.

### Inspect A Tier

Show:

- current state cell
- outgoing action cells
- action-cell members
- refinement fiber
- lift candidates

### Freeze Behavior

Show construction of `FrozenQuotientBehavior`.

### Build A Path Fiber

Show a `PathFiber` built from:

- tower
- fine tier
- coarse tier
- frozen behavior

### Build A Stage

Show `FiberConditionedStage`.

### Write A Tiny Training Loop

Show:

```python
current_input = stage.reset(seed=0)
for _ in range(max_steps):
    decision = learner.act(current_input)
    transition = stage.step(decision)
    learner.observe(transition)
    learner.update()
    current_input = transition.target_input
```

The loop should be intentionally boring.

That is the point.

## Documentation Acceptance Criteria

The documentation is successful when a competent engineer can answer:

- What is `state_collapser` for?
- Why is it not RLlib or Stable-Baselines3?
- What does the package own?
- What does the learner own?
- What is the total graph?
- Which direction is down the tower?
- What does it mean to freeze coarser behavior?
- What is the path fiber over that behavior?
- What is a fiber-conditioned stage?
- How do action masks arise from fiber admissibility?
- Where do I plug in my model or learner?
- What should I not expect this package to do yet?

The documentation is not successful if the reader must read the entire design
discussion before running a basic example.

## Documentation-Driven API Pressure

The docs should force these API constraints.

### Constraint 1: Names Must Teach The Direction

Prefer:

- `total_state`
- `fine_tier`
- `coarse_tier`
- `frozen_quotient_behavior`
- `path_fiber`
- `stage_context`

Avoid adding new public API names that deepen:

- `base_state`
- `lower_context`
- ambiguous `supporting_tier`

Compatibility aliases may remain, but new docs should teach the corrected
vocabulary.

### Constraint 2: The First Example Must Be Importable

If the docs show:

```python
from state_collapser.training import FiberConditionedStage
```

then that import should work.

User-facing docs should not require deep internal imports.

### Constraint 3: Diagnostics Must Be Explainable

If the stage rejects an action, the docs must be able to show why.

Therefore, code should expose:

- departure reason
- expected coarse behavior
- actual projection
- attempted fine action

### Constraint 4: Stages Must Be Loop-Compatible

If the docs say engineers own the loop, the stage must be simple to step.

It should be clear whether the loop calls:

```python
stage.step(decision)
```

or:

```python
collector.collect_step(input, decision)
```

The API should not force both in the first example unless the distinction is
obvious.

### Constraint 5: External Adapters Must Be Clearly Downstream

The docs should prevent users from thinking the first serious use requires
SB3/RLlib.

External adapters should be documented as later integration points.

## Proposed Documentation Milestones

### Milestone 1: Conceptual Orientation

Deliver:

- README positioning remains concise
- usage doc: "What state_collapser is"
- usage doc: "Tower runtime mental model"
- glossary skeleton

### Milestone 2: New Surface Guide

Deliver:

- `FrozenQuotientBehavior` guide
- `PathFiber` guide
- `FiberConditionedStage` guide
- common misunderstandings page

### Milestone 3: Runnable Minimal Example

Deliver:

- tiny graph example
- code snippet in docs
- corresponding test that executes the snippet or equivalent path

### Milestone 4: Existing Environment Example

Deliver:

- plate-support fiber-conditioned stage walkthrough
- contrast with existing flat tower-aware training
- show transition metadata

### Milestone 5: Adapter Preview

Deliver:

- short note explaining future Gymnasium/SB3/RLlib adapters
- no promise that these are implemented until they actually are

## How This Documentation Pairs With The Implementation Blueprint

The implementation blueprint asks for:

- `FrozenQuotientBehavior`
- `PathFiber`
- `FiberConditionedStage`
- stage/fiber context in inputs and transitions

This documentation blueprint asks:

- Can an engineer understand those in that order?
- Can an engineer run a no-Torch example?
- Can an engineer see where their own loop goes?
- Can an engineer distinguish local tower queries from path-fiber stages?
- Can an engineer understand why external frameworks are downstream?

If any answer is no, the API should be simplified before implementation hardens.

## Deferred Documentation

Defer docs for:

- PyTorch model families
- tensor/device batching
- replay buffers
- checkpoint/resume
- experiment manifests
- benchmark artifact reports
- SB3 adapter
- RLlib adapter

These should become documentation projects only after the corresponding package
surfaces exist.

## Final Documentation Target

The final engineer-facing message should be:

```text
Use state_collapser when you want to construct and train through hierarchical
quotient/fiber decision structure.

Do not use it because you want another PPO implementation.

The package builds the stage.
You bring the learner.
```

That is the usability north star.
