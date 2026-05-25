# API Note: FiberConditionedStage

`FiberConditionedStage` is the package-native learner-facing stage for training
inside a path fiber.

Constructor fields:

- `stage_id`
- `runtime`
- `tower`
- `fine_tier`
- `coarse_tier`
- `frozen_behavior`
- `path_fiber`
- `action_resolver`
- `bootstrap_semantics`
- `metadata`

The required semantic chain is:

```text
runtime + PartitionTower + FrozenQuotientBehavior + PathFiber
    -> FiberConditionedStage
        -> ActionSelectionInput / TrainingTransition
```

## Methods

- `reset(seed=None, options=None, reset_result=None)`
- `current_input()`
- `step(decision)`

`reset(...)` returns `ActionSelectionInput` with stage context and fiber-derived
mask.

`current_input()` rebuilds the current input without advancing the runtime.

`step(...)` accepts `ActionDecision`, resolves an action index or action-cell id
to a fiber-admissible action, steps the runtime only when the choice is
admissible, and returns `TrainingTransition`.

Invalid choices produce explicit `fiber_departure` diagnostics rather than
silently stepping outside the fiber.

## Non-Goals

`FiberConditionedStage` is not:

- a Gymnasium env
- an RLlib worker
- a Stable-Baselines3 algorithm
- a model/optimizer/checkpoint owner

A future adapter can wrap it for those ecosystems.
