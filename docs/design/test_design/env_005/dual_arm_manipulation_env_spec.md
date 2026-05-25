# Dual-Arm Manipulation Env Specification

## Purpose

`dual_arm_manipulation_env` is intended to model a shared-object manipulation problem in which valid motion depends on two coordinated effectors.

This environment is conceptually central to the package’s motivating story:

- strong coupling
- hidden feasible transitions
- no obvious clean subtask decomposition

## Conceptual picture

The world contains:

- a small shared object in a discrete workspace
- left and right arm mode variables
- left and right reach variables
- object pose variables

The state is valid only when:

- both arms remain consistent with the object pose
- the object is supportable or manipulable under the current coordination state

## State shape

Recommended first state:

```python
@dataclass(frozen=True, slots=True)
class DualArmManipulationState:
    obj_x: int
    obj_y: int
    obj_theta: int
    left_mode: int
    right_mode: int
    left_reach: int
    right_reach: int
```

## Action set

Discrete actions should:

- adjust left-arm state
- adjust right-arm state
- move or rotate the object when joint support permits

## Validity rule

The validity rule must encode:

- left/right reach feasibility
- coordinated support of the shared object
- object-motion feasibility under current arm states

## Why this is a good `state_collapser` env

- hidden coordination geometry
- strong coupling without obvious subtasks
- likely repeated quotientable local structure

## Implementation caution

The first version must be aggressively minimized.

It must remain a small discrete constrained RL problem, not a manipulation simulator.
