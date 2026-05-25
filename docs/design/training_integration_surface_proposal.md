# Training Integration Surface Proposal

## Purpose

This document narrows the remaining design work for the package-facing training/integration surface of `state_collapser`.

The main usage story we want is:

1. a user already has an RL problem, ideally as a `gymnasium.Env`
2. the user writes a small amount of integration code to expose that problem to `state_collapser`
3. the package runs its graph-discovery / vista / quotient-tier / tower runtime machinery on top of that problem
4. the same problem can then be trained or evaluated in two modes:
   - flat environment training
   - tower-assisted training

This document is not yet a full implementation gameplan. It is the bridge from:

- current package core
- current example environments

to:

- benchmark and training harness work

## What is already clear

The following is now stable enough to treat as design assumptions:

- `gymnasium` should be the first-class RL environment boundary
- reward should remain one-step local
- `state_collapser` should sit as a structural/runtime layer over the problem
- comparison experiments should use the same underlying environment and reward function in both:
  - flat mode
  - tower-assisted mode

## What remains to be designed

The remaining design work is smaller and more concrete than earlier repo-wide design work.

The main unresolved questions are:

1. What exact object does the user pass to `state_collapser`?
2. What exact adapter contract exposes a `gymnasium.Env` to the package?
3. Does the package own the training loop, or does it wrap an external trainer?
4. What benchmark artifacts and metrics should be emitted by default?

## Recommended shape

The cleanest first-pass integration surface is:

### 1. Environment stays primary

The user continues to own or instantiate a `gymnasium.Env`.

Example:

```python
env = PlateSupportEnv()
```

### 2. Add a package-facing env adapter layer

The user then exposes the env to `state_collapser` through a thin integration object.

Conceptually:

```python
runtime = StateCollapserEnvRuntime.from_gymnasium(
    env=env,
    reward_mode="local",
    contraction_policy=...,
)
```

The exact name can change, but the shape should be:

- env in
- package runtime out

### 3. Keep training-mode selection outside the raw env

The user should be able to choose:

- flat training
- tower-assisted training

without modifying the env itself.

Conceptually:

```python
flat_results = run_flat_training(env, trainer_config)
tower_results = run_tower_training(env, runtime_config, trainer_config)
```

### 4. Package should own the tower-side runtime, not the environment

The env should not absorb:

- explored-graph state
- quotient tiers
- tower bookkeeping

Those belong to `state_collapser`.

The env should remain:

- a problem definition
- a transition/reward shell

while the package owns:

- graph discovery
- annotations
- vista refresh
- quotient update
- tower snapshots

### 5. Artifact outputs should be standardized

The first benchmark/training integration layer should emit structured artifacts such as:

- training configuration snapshot
- success-rate summary
- episodic return summary
- invalid-move summary
- optional tower snapshot summaries

This should make it easy to compare:

- flat mode
- tower mode

without bespoke per-env bookkeeping.

## Recommended package-level object split

A reasonable first split is:

- `gymnasium.Env`
  - owns problem dynamics and rewards
- `state_collapser` env adapter/runtime
  - owns graph-discovery and tower machinery
- training runner
  - owns trial execution, metrics, and artifacts

This means the user-facing workflow becomes:

1. instantiate env
2. instantiate optional tower runtime wrapper
3. run flat or tower benchmark harness

## Examples folder convention

The repo is now large enough that example environments should stop living as single flat files whenever they are likely to grow.

Recommended convention:

```text
src/state_collapser/examples/
    robot_constraint_toy.py
    plate_support_env/
        __init__.py
        env.py
        later: benchmark.py, fixtures.py, notes.md, etc.
```

Why this helps:

- each example can grow without turning `examples/` into a flat junk drawer
- env-specific helpers and later benchmark harnesses can live beside the env
- future examples can be added as sibling packages

For `PlateSupportEnv`, this is already the right direction because the environment now has:

- nontrivial helper logic
- several env-specific test files
- likely future benchmark-specific code

## Immediate recommendation

Before building the flat-vs-tower benchmark harness, the next clean implementation move is:

1. use the example-subpackage layout for `PlateSupportEnv`
2. keep the env object itself self-contained
3. design a small benchmark-facing runner surface around it

The remaining design work is therefore real, but narrow:

- define the adapter/runtime entry point
- define the benchmark runner entry points
- define the benchmark artifact contract

That is much smaller than earlier design work and should be feasible to lock down quickly before benchmark implementation begins.
