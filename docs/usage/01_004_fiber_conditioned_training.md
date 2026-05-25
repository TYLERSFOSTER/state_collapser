# Fiber-Conditioned Training

Fiber-conditioned training is the package-native bridge between quotient-tower
structure and ordinary learner loops.

The implemented chain is:

```text
PartitionTower
    -> FrozenQuotientBehavior
        -> PathFiber
            -> FiberConditionedStage
                -> ActionSelectionInput / TrainingTransition
```

The idea is:

1. Choose behavior at a coarser tier.
2. Freeze that behavior.
3. Construct the path fiber over it at the adjacent finer tier.
4. Train a learner only on fine actions that lift that frozen coarse behavior.

## Implemented Imports

```python
from state_collapser.training import ActionDecision
from state_collapser.training import FiberConditionedStage
from state_collapser.training import FrozenQuotientBehavior
from state_collapser.training import PathFiber
```

## Tiny Graph Walkthrough

A tiny use follows this shape:

```python
from state_collapser.training import FiberConditionedStage
from state_collapser.training import FrozenQuotientBehavior
from state_collapser.training import PathFiber

# 1. Build or discover a small graph.
# 2. Build a PartitionTower from that graph.
# 3. Choose an adjacent pair of tiers.
fine_tier = 0
coarse_tier = 1

# 4. Choose a concrete coarse quotient step to freeze.
frozen_behavior = FrozenQuotientBehavior.from_step(
    behavior_id="coarse-choice",
    coarse_tier=coarse_tier,
    supported_fine_tier=fine_tier,
    source_cell=coarse_source_cell,
    action_cell=coarse_action_cell,
    target_cell=coarse_target_cell,
)

# 5. Construct the path fiber over that frozen behavior.
path_fiber = PathFiber(
    fiber_id="fiber-over-coarse-choice",
    tower=tower,
    fine_tier=fine_tier,
    coarse_tier=coarse_tier,
    frozen_behavior=frozen_behavior,
)

# 6. Ask for admissible fine actions or masks.
admissible = path_fiber.admissible_action_cells(current_total_state)
mask = path_fiber.action_mask(current_total_state)

# 7. Wrap the interaction as a direct learner-facing stage.
stage = FiberConditionedStage(
    stage_id="fine-stage",
    runtime=runtime,
    tower=tower,
    fine_tier=fine_tier,
    coarse_tier=coarse_tier,
    frozen_behavior=frozen_behavior,
    path_fiber=path_fiber,
)

current_input = stage.reset(seed=0)
transition = stage.step(ActionDecision(chosen_action=0))
```

The returned `TrainingTransition` carries:

- `stage_context`
- `projected_coarse_step`
- `fiber_departure` when the attempted action leaves the fiber

## PlateSupportEnv Walkthrough

`plate_support_env` can already exercise the same surface. The important extra
detail is that its runtime expects discrete environment actions, while the
stage resolves a fine action cell to a concrete edge. Use `action_resolver` to
translate the realized edge into the runtime action:

```python
from state_collapser.examples.plate_support_env import PlateSupportEnv
from state_collapser.examples.plate_support_env.runtime import PlateSupportEnvRuntime
from state_collapser.examples.plate_support_env.runtime import primitive_action_to_action_index
from state_collapser.training import FiberConditionedStage
from state_collapser.training import FrozenQuotientBehavior
from state_collapser.training import PathFiber

runtime = PlateSupportEnvRuntime(env=PlateSupportEnv())
reset_result = runtime.reset(seed=0)
tower = reset_result.runtime_snapshot.partition_tower_view
current_state = reset_result.runtime_snapshot.current_base_state

fine_tier = 0
coarse_tier = 1
fine_state_cell = tower.current_state_cell(fine_tier, current_state)
fine_action_cell = tower.outgoing_action_cells(fine_tier, fine_state_cell)[0]
representative_edge = tower.representative_edges(fine_tier, fine_action_cell)[0]

frozen_behavior = FrozenQuotientBehavior.from_step(
    behavior_id="plate-support-frozen-step",
    coarse_tier=coarse_tier,
    supported_fine_tier=fine_tier,
    source_cell=tower.current_state_cell(coarse_tier, representative_edge.source),
    action_cell=tower.action_cell_for_edge(coarse_tier, representative_edge),
    target_cell=tower.current_state_cell(coarse_tier, representative_edge.target),
)

path_fiber = PathFiber(
    fiber_id="plate-support-fiber",
    tower=tower,
    fine_tier=fine_tier,
    coarse_tier=coarse_tier,
    frozen_behavior=frozen_behavior,
)

stage = FiberConditionedStage(
    stage_id="plate-support-stage",
    runtime=runtime,
    tower=tower,
    fine_tier=fine_tier,
    coarse_tier=coarse_tier,
    frozen_behavior=frozen_behavior,
    path_fiber=path_fiber,
    action_resolver=lambda edge: primitive_action_to_action_index(edge.action),
)
```

This remains package-native. It does not require Torch, Stable-Baselines3,
RLlib, or Gymnasium.

For field-level details, see:

- [FrozenQuotientBehavior API note](../api_notes/frozen_quotient_behavior.md)
- [PathFiber API note](../api_notes/path_fiber.md)
- [FiberConditionedStage API note](../api_notes/fiber_conditioned_stage.md)
