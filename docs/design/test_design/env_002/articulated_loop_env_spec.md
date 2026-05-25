# Articulated Loop Env Specification

## Purpose

`articulated_loop_env` is the first next-wave evaluation environment after `PlateSupportEnv`.

Its job is to model a small discrete articulated mechanism with loop-closure constraints, so that:

- the ambient parameterization looks simple
- the feasible hidden graph is sharply constrained
- the resulting state graph has nontrivial local equivalence structure without obvious subtasks

## Canonical repository placement

- `src/state_collapser/examples/articulated_loop_env/env.py`

The package should expose the env through:

- `src/state_collapser/examples/articulated_loop_env/__init__.py`

Its env-specific tests should live under:

- `tests/examples/`

Its env-specific design and implementation artifacts should live under:

- `docs/design/test_design/env_002/`

## Conceptual picture

The world contains:

- a three-link planar articulated chain
- discrete quarter-turn link directions
- a brace mode that changes the required closure target
- a small explicit coupler-slack budget

The chain must form a closed loop from a fixed base to a fixed anchor target.

The agent controls:

- local rotation of one link at a time
- brace-mode toggle

The state is valid only when:

- the vector sum of the three link directions is within a small mismatch tolerance of the brace-mode target vector

This makes the feasible graph a small subset of a much larger ambient discrete product.

## State space

Use an immutable state record:

```python
@dataclass(frozen=True, slots=True)
class ArticulatedLoopState:
    d1: int
    d2: int
    d3: int
    brace_mode: int
    coupler_slack: int
```

Semantics:

- `d1`, `d2`, `d3` are direction bins in `{0, 1, 2, 3}`
- `brace_mode` is in `{0, 1}`
- `coupler_slack` is in `{0, 1}`

Direction bins represent unit vectors:

- `0` → `(1, 0)`
- `1` → `(0, 1)`
- `2` → `(-1, 0)`
- `3` → `(0, -1)`

Brace-mode targets:

- `brace_mode = 0` requires closure to `(1, 0)`
- `brace_mode = 1` requires closure to `(0, 1)`

The `coupler_slack` value is a mismatch budget:

- `0` means exact closure only
- `1` means one unit of Manhattan mismatch is permitted
- `2` means two units of Manhattan mismatch are permitted

## Action set

Use a discrete action space of size `9`:

- `0`: rotate `d1` by `+1`
- `1`: rotate `d1` by `-1`
- `2`: rotate `d2` by `+1`
- `3`: rotate `d2` by `-1`
- `4`: rotate `d3` by `+1`
- `5`: rotate `d3` by `-1`
- `6`: toggle `brace_mode`
- `7`: increase `coupler_slack` by `1`
- `8`: decrease `coupler_slack` by `1`

All direction changes are modulo `4`.

## Validity rule

Let `v(d)` denote the unit vector for direction bin `d`.

Let the closure mismatch be:

```text
|| v(d1) + v(d2) + v(d3) - target(brace_mode) ||_1
```

The state is valid iff:

```text
closure_mismatch <= coupler_slack
```

The target depends on `brace_mode`.
The tolerance depends on `coupler_slack`.

This validity rule is exact, not heuristic.

## Observation space

The observation is the full discrete state tuple:

```text
(d1, d2, d3, brace_mode, coupler_slack)
```

The recommended first implementation returns a NumPy integer array encoding of this tuple.

## Reward and task shape

The environment should define:

- a fixed valid start state
- a fixed valid goal state distinct from start

Per-step reward:

- negative step cost by default
- larger positive reward on reaching the goal
- optional invalid-move penalty if an action proposal would leave the feasible set and is rejected

## Why this is a good `state_collapser` env

- the naive ambient state space is a simple product
- the feasible hidden graph is cut down by loop-closure constraints with explicit local slack
- there is no obvious subtask decomposition
- the same closure logic repeats across local neighborhoods in ways that may be quotientable

## Implementation caution

The closure rule must produce:

- enough feasible states to be interesting
- but not so many that the constraint becomes decorative
- and the mismatch budget must remain small enough that the env still feels loop-constrained rather than unconstrained
- the start state should admit valid primitive one-joint motion without requiring pre-coupled actions

This env is not a simulator.

It is a small discrete constrained hidden-graph problem.
