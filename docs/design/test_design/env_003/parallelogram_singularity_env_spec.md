# Parallelogram Singularity Env Specification

## Purpose

`parallelogram_singularity_env` is intended to model a small discrete linkage whose feasible graph includes singular or near-singular regions where local motion structure changes sharply.

Its job is to test whether `state_collapser` can respond not only to coupled feasibility constraints, but also to hidden structural bottlenecks.

## Conceptual picture

The world contains:

- a small discrete parallelogram-like linkage
- left/right angle bins
- a span bin
- an alignment mode

The state is valid only when:

- left/right linkage constraints are satisfied
- span is consistent with the current linkage alignment

Singular regions occur where:

- the linkage is fully collapsed or fully extended
- local feasible moves become sharply restricted

## State shape

Recommended first state:

```python
@dataclass(frozen=True, slots=True)
class ParallelogramState:
    left_angle: int
    right_angle: int
    span: int
    alignment_mode: int
```

with small discrete bins for each field.

## Action set

Discrete actions should:

- increment or decrement one linkage variable at a time
- toggle alignment mode if needed

## Validity rule

The state is valid iff:

- left/right angle difference stays within a small allowed band
- span is compatible with the angle/alignment configuration

The singular regime must not be merely named.

It must actually induce reduced local feasible motion.

## Why this is a good `state_collapser` env

- hidden structural bottlenecks
- changing local feasible geometry
- no obvious subtask decomposition

## Implementation caution

The singular region must be operational, not decorative.
