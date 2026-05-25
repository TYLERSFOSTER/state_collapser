# `rl_counterpoint_v3` Transformation Report

## Purpose

This document records the first design reading of `[rl_counterpoint repository root]` for the planned example package:

- `src/state_collapser/examples/rl_counterpoint_v3/`

The purpose of this report is not to begin implementation.

Its purpose is to answer:

- what `rl_counterpoint` was actually trying to do
- what the real underlying RL problem is
- what parts of that repo are musical/problem content
- what parts are old infrastructure choices
- what must change in order to rebuild the problem in the simpler, example-oriented, package surfaces of `state_collapser`

This is a transformation report, not a blueprint and not a gameplan.

## Executive Summary

`rl_counterpoint` is not just “an RL music repo.”

It is a research repo whose active design center became:

- a hand-authored hierarchical RL system over chord rank

The current `tower/` package in `rl_counterpoint` already embodies a specific hierarchy:

- rank 1: pedal/root line
- rank 2: outer voice over rank 1
- rank 3+: interior voices over frozen lower-rank scaffolds

That hierarchy is musically motivated and historically important, but it is **not** the surface we should copy directly into `state_collapser`.

For `state_collapser`, the correct target is:

- rebuild the **underlying counterpoint RL problem**
- in a much smaller example-package shape
- so that `state_collapser` can attempt to **induce** useful tower structure from that problem
- rather than importing a pre-authored rank tower as the example itself

So the main correction is:

- `rl_counterpoint_v3` in this repo should be a **counterpoint environment**
- not a port of the `rl_counterpoint/tower` training stack

## What `rl_counterpoint` Was About

After reading the current repo, the best concise description is:

- the repo studies counterpoint generation as an RL problem
- the legacy system expresses that as a flat graph / flat RL environment
- the active system expresses it as a rank-by-rank hierarchical training tower

The most important high-level points are visible in:

- [`[rl_counterpoint repository root]/README.md`]([rl_counterpoint repository root]/README.md)
- [`[rl_counterpoint repository root]/docs/design/tower/system_design.md`]([rl_counterpoint repository root]/docs/design/tower/system_design.md)
- [`[rl_counterpoint repository root]/docs/design/tower/training_protocol.md`]([rl_counterpoint repository root]/docs/design/tower/training_protocol.md)

The repo’s central technical claims are:

1. Counterpoint can be posed as an RL problem over legal chord / voiceleading transitions.
2. Reward design can be built from local and semi-local contrapuntal rules.
3. The problem admits a musically meaningful HRL decomposition by chord rank.
4. Training higher-rank musical structure over frozen lower-rank scaffolds may create large search and learning speedups.

Historically, this third point is one of the intellectual sources of the later `state_collapser` project.

## What The Basic RL Problem Actually Is

Stripping away the legacy code and the explicit tower redesign, the underlying RL problem in `rl_counterpoint` is:

- a discrete state space of valid pitch tuples
- a discrete action space of per-voice pitch deltas
- graph legality determined by voiceleading and harmonic constraints
- rewards determined by local and terminal musical preferences
- finite-horizon episodic generation of a short contrapuntal passage

The clearest flat-system surfaces for that are:

- [`[rl_counterpoint repository root]/rl_counterpoint/envs/counterpoint_env.py`]([rl_counterpoint repository root]/rl_counterpoint/envs/counterpoint_env.py)
- [`[rl_counterpoint repository root]/rl_counterpoint/graph/graph_spec.py`]([rl_counterpoint repository root]/rl_counterpoint/graph/graph_spec.py)
- [`[rl_counterpoint repository root]/rl_counterpoint/graph/actions.py`]([rl_counterpoint repository root]/rl_counterpoint/graph/actions.py)
- [`[rl_counterpoint repository root]/rl_counterpoint/graph/state_space.py`]([rl_counterpoint repository root]/rl_counterpoint/graph/state_space.py)
- [`[rl_counterpoint repository root]/rl_counterpoint/reward/protocol.py`]([rl_counterpoint repository root]/rl_counterpoint/reward/protocol.py)

So the “basic RL problem” is not:

- transformer training
- artifact writing
- checkpoint lineage
- rank-by-rank frozen-parent rollout

It is:

- constrained discrete voiceleading over chord states

That is the part `state_collapser` should inherit.

## What In `rl_counterpoint` Looks Like True Problem Content

These parts look like the real mathematical / musical content that should inform `rl_counterpoint_v3`.

### 1. State shape as ordered pitch tuples

Both the legacy flat system and the active tower system treat states as:

- tuples of MIDI pitches
- strictly increasing by voice

This is the right starting point for a `state_collapser` example, because it is:

- discrete
- inspectable
- already close to the current example-env style in this repo

### 2. Action shape as bounded per-voice deltas

The flat system’s `StepDelta` action is important:

- actions are tuple-valued signed pitch changes
- legality is checked by decoding the next state and validating the edge

This is a good fit for `state_collapser`, because it creates:

- a simple ambient action lattice
- a hidden legal-action subset

That is exactly the sort of hidden feasible-graph geometry the repo likes.

### 3. Graph legality from counterpoint constraints

The real heart of the problem is the legality surface:

- pitch ordering
- vertical interval restrictions
- chord-width restrictions
- root / tonic-class restrictions
- voiceleading edge legality

This is the part that makes the environment interesting for `state_collapser`.

### 4. Reward as structured local context, not environment-global magic

The reward protocol in the flat system is also worth preserving conceptually:

- source
- target
- small explicit context
- structured reward result

The exact reward terms should probably be simplified in the first port, but the protocol shape is good.

### 5. Finite-horizon episodic passage generation

The environment is not a static graph search toy.

It is an episodic generation problem with:

- step index
- measure position
- horizon
- terminal or deadline-sensitive reward behavior

That should remain true in the new example.

## What In `rl_counterpoint` Is Infrastructure We Should Not Port Directly

These parts belong to the old repo’s training architecture, not to the core example we should build here.

### 1. The explicit rank tower

This is the single most important warning.

The active `tower/` package in `rl_counterpoint` is already a hand-authored HRL decomposition:

- states project by rank
- actions assemble upward by rank
- training proceeds by frozen parent scaffold
- rewards are rank-owned

That is historically important, but it is the wrong object to copy into a `state_collapser` example.

Why:

- `state_collapser` is supposed to induce hierarchical structure from a problem
- not be handed a fully authored tower as the example itself

So we should not port:

- `tower/state_action.py`
- `tower/graph/projection.py`
- `tower/action/assembly.py`
- `tower/train/rollout.py`
- `tower/train/lifecycle.py`
- the rank-local parent/child policy protocol

as the core of `rl_counterpoint_v3`

### 2. Transformer-policy infrastructure

The active and legacy repos include:

- transformer observation encoders
- transformer policies
- PyTorch losses
- checkpoints
- samplers

That is too heavy and too far from the current example surfaces in `state_collapser`.

It is also the wrong abstraction boundary for the first rebuild.

For `state_collapser/examples`, the right first surface is:

- small env
- runtime binding
- simple training entrypoint

not:

- model architecture research stack

### 3. Artifact and lineage infrastructure

The following are real in `rl_counterpoint`, but should not be first-class in the initial port:

- artifact trees
- lineage manifests
- rank checkpoints
- MIDI export pipelines
- staged training scripts

Those may become useful later, but they are not needed to capture the core RL problem inside `state_collapser`.

### 4. Overgrown reward bundles

The reward factories in `rl_counterpoint/tower/reward/factory.py` are sophisticated and musically rich.

For the first port, that is too much.

We should preserve:

- the reward *shape*
- the idea of beat-sensitive and terminal-sensitive scoring

But we should not try to port the whole TC21M-derived reward stack in the first example package.

## The Core Surface Transformation

The transformation we want is:

### From `rl_counterpoint`

- research repo with separate flat and explicit-tower systems
- transformer-heavy training machinery
- hand-authored HRL tower semantics
- large reward and artifact infrastructure

### To `state_collapser/examples/rl_counterpoint_v3`

- one small explicit example package
- one discrete RL environment
- one runtime integration
- one or two simple training/probe entrypoints
- tests
- no hard-coded package-local hierarchy beyond what the environment itself exposes as a flat RL problem

In short:

- port the **problem**
- do not port the old **solution architecture**

## What Must Change In The Surface

### 1. The example must be package-shaped like `state_collapser`, not repo-shaped like `rl_counterpoint`

The target should look like:

```text
src/state_collapser/examples/rl_counterpoint_v3/
  __init__.py
  env.py
  runtime.py
  training.py
```

with matching tests and design docs.

That is very different from:

- `tower/`
- `scripts/`
- `artifacts/`
- model subpackages

### 2. The environment should be a single flat RL problem

This is critical.

The initial environment should be:

- one Gym-style or package-style RL problem
- not already split into rank-1 / rank-2 / rank-3 training stages

That means:

- no frozen parent policies
- no child-extension training lifecycle
- no hand-authored stage training protocol in the environment surface

The hierarchy, if useful, should be something `state_collapser` tries to discover or exploit.

### 3. Observation surfaces must be simplified dramatically

`rl_counterpoint` uses:

- timed windows
- encoded tensors
- metrical features
- transformer-specific observation contracts

For the initial `state_collapser` example, the observation surface should be much simpler:

- likely just the full discrete chord state
- plus possibly a small amount of explicit timing / measure-position state if that is essential

The first port should not depend on:

- `torch`
- tensor encoding
- transformer context windows

### 4. Reward should become a narrow first slice

The first reward bundle should likely be much smaller than `rl_counterpoint`’s full reward stack.

A good first slice would preserve only a few ideas, such as:

- step cost
- terminal/cadential success reward
- one or two local voiceleading preferences
- maybe one beat-sensitive structural preference

The first port should not attempt to reproduce the entire musical reward language of the old repo.

### 5. Episode semantics need to survive, but in a simpler way

The environment should still have:

- horizon
- step index
- measure size or simple beat position
- terminal success condition

But this should be surfaced in the small example style used by `state_collapser`, not in the larger training pipeline style of `rl_counterpoint`.

### 6. The graph should stay hidden-constraint-heavy

This is where the port can be especially good for `state_collapser`.

The ambient problem can still be:

- bounded per-voice pitch deltas
- over ordered pitch tuples

while legality trims that ambient product heavily.

That makes the example naturally suitable for:

- hidden graph
- explored graph
- tower induction

provided we do not short-circuit that by reintroducing the explicit `rl_counterpoint` tower by hand.

## The Main Conceptual Mismatch To Avoid

The biggest danger is:

- accidentally rebuilding `rl_counterpoint/tower` inside `state_collapser/examples`

That would be wrong for two reasons:

1. It would duplicate the old HRL solution architecture instead of expressing the underlying RL problem.
2. It would make the example pre-hierarchical in exactly the way `state_collapser` is supposed to move beyond.

So the first `rl_counterpoint_v3` package should *not* be:

- a rank-local tower package
- a scaffold-first parent-child training package
- a transformer training lab

It should be:

- a compact counterpoint RL environment whose hidden structure may later justify `state_collapser`’s induced hierarchy machinery

## Recommended First Scope

The safest first scope is not “full counterpoint.”

It is something like:

- a small fixed-voice-count counterpoint problem
- probably `n = 2` or `n = 3`
- bounded pitch range
- bounded step-delta actions
- strict voice ordering
- a small trimmed legality surface
- one simple terminal musical target

That would preserve the essential geometry while keeping the example:

- discrete
- inspectable
- testable
- small enough for current package expectations

My strong recommendation is:

- start with a two-voice problem first

Why:

- it is the clearest bridge from the old repo into the new one
- it is musically meaningful
- it is much easier to inspect and test
- it does not force premature reintroduction of the old hand-authored rank tower

If a later extension is desired, then:

- three-voice can follow as a second-wave extension

## Specific Surfaces To Reuse Conceptually

These old surfaces should be treated as conceptual templates:

- [`rl_counterpoint/graph/graph_spec.py`]([rl_counterpoint repository root]/rl_counterpoint/graph/graph_spec.py)
  - for graph-parameter ideas
- [`rl_counterpoint/graph/state_space.py`]([rl_counterpoint repository root]/rl_counterpoint/graph/state_space.py)
  - for state validity logic
- [`rl_counterpoint/graph/actions.py`]([rl_counterpoint repository root]/rl_counterpoint/graph/actions.py)
  - for step-delta action semantics
- [`rl_counterpoint/envs/counterpoint_env.py`]([rl_counterpoint repository root]/rl_counterpoint/envs/counterpoint_env.py)
  - for episode and reward-context semantics
- [`rl_counterpoint/reward/protocol.py`]([rl_counterpoint repository root]/rl_counterpoint/reward/protocol.py)
  - for structured reward contract ideas

These old surfaces should *not* be treated as direct package-port targets:

- `tower/graph/projection.py`
- `tower/action/assembly.py`
- `tower/train/rollout.py`
- `tower/policy/*`
- `tower/train/*`
- the training scripts under `[rl_counterpoint repository root]/scripts/`

## What This Means For The Next Design Step

The next document should not be an implementation gameplan yet.

It should be a narrower design blueprint for:

- what exact counterpoint RL problem `rl_counterpoint_v3` will instantiate in `state_collapser`

That blueprint should answer at least:

1. fixed voice count for the first version
2. exact state tuple
3. exact action tuple
4. legality surface
5. reward surface
6. terminal success condition
7. what timing/measure information is explicit in state versus only in episode context
8. what is intentionally omitted from `rl_counterpoint` for the first port

## Bottom Line

`rl_counterpoint` is best understood as:

- a repo that discovered a rich explicit HRL solution for counterpoint generation

But `state_collapser` needs something different from it:

- not that explicit tower solution
- but the underlying constrained RL problem, rebuilt in a much smaller and cleaner example surface

So the right transformation is:

- keep the discrete chord-state / step-delta / legality / reward-context core
- throw away the transformer-heavy training stack and explicit rank-local tower machinery
- rebuild the counterpoint problem as a compact `state_collapser` example environment
- let `state_collapser` provide the hierarchy story from there
