# Cable Parallel Env Specification

## Purpose

`cable_parallel_env` is intended to model a cable-driven platform with coupled support/tension feasibility.

It should stay close enough to `plate_support_env` to be comparable, while differing structurally in the governing support logic.

## Conceptual picture

The world contains:

- a small platform pose on a discrete grid
- three anchored cables
- discrete cable-state variables

The state is valid only when:

- the current cable states can support the current platform pose
- at least two cables are effectively supporting
- the cable geometry stays inside simple discrete reach/balance bounds

## State shape

Recommended first state:

```python
@dataclass(frozen=True, slots=True)
class CableParallelState:
    x_idx: int
    y_idx: int
    theta_idx: int
    c1: int
    c2: int
    c3: int
```

## Action set

Discrete actions should:

- move platform pose
- rotate platform
- increase or decrease one cable state at a time

## Validity rule

The validity rule must reflect cable-style support coupling rather than rigid arm reach.

This env must not reduce to `plate_support_env` with renamed supports.

## Why this is a good `state_collapser` env

- hidden feasible region inside a simple ambient state product
- repeated local support regularity
- a second support-constrained comparison family

## Implementation caution

The cable constraints should be structurally different from the rigid-support story in `plate_support_env`.
