"""PlateSupportEnv smoke test for the fiber-conditioned training stage."""

from __future__ import annotations

from state_collapser.examples.plate_support_env.env import PlateSupportEnv
from state_collapser.examples.plate_support_env.runtime import (
    PlateSupportEnvRuntime,
    primitive_action_to_action_index,
)
from state_collapser.training import (
    ActionDecision,
    FiberConditionedStage,
    FrozenQuotientBehavior,
    PathFiber,
    TabularQLearner,
    TrainingTransition,
)


def build_plate_support_stage() -> FiberConditionedStage:
    runtime = PlateSupportEnvRuntime(env=PlateSupportEnv())
    reset_result = runtime.reset(seed=0)
    tower = reset_result.runtime_snapshot.partition_tower_view
    current_state = reset_result.runtime_snapshot.current_base_state

    assert tower is not None
    assert current_state is not None

    fine_tier = 0
    coarse_tier = 1
    fine_state_cell = tower.current_state_cell(fine_tier, current_state)
    fine_action_cell = tower.outgoing_action_cells(fine_tier, fine_state_cell)[0]
    representative_edge = tower.representative_edges(fine_tier, fine_action_cell)[0]
    source_cell = tower.current_state_cell(coarse_tier, representative_edge.source)
    target_cell = tower.current_state_cell(coarse_tier, representative_edge.target)

    frozen_behavior = FrozenQuotientBehavior.from_step(
        behavior_id="plate-support-frozen-coarse-step",
        coarse_tier=coarse_tier,
        supported_fine_tier=fine_tier,
        source_cell=source_cell,
        action_cell=tower.action_cell_for_edge(coarse_tier, representative_edge),
        target_cell=target_cell,
    )
    path_fiber = PathFiber(
        fiber_id="plate-support-path-fiber",
        tower=tower,
        fine_tier=fine_tier,
        coarse_tier=coarse_tier,
        frozen_behavior=frozen_behavior,
    )
    return FiberConditionedStage(
        stage_id="plate-support-stage",
        runtime=runtime,
        tower=tower,
        fine_tier=fine_tier,
        coarse_tier=coarse_tier,
        frozen_behavior=frozen_behavior,
        path_fiber=path_fiber,
        action_resolver=lambda edge: primitive_action_to_action_index(edge.action),
    )


def test_plate_support_fiber_stage_can_reset() -> None:
    stage = build_plate_support_stage()

    action_input = stage.reset(seed=0)

    assert action_input.stage_context == stage.stage_context
    assert action_input.action_mask is not None
    assert any(action_input.action_mask)


def test_plate_support_fiber_stage_short_loop_runs_without_torch() -> None:
    stage = build_plate_support_stage()
    current_input = stage.reset(seed=0)
    action_count = 0 if current_input.action_mask is None else len(current_input.action_mask)
    learner = TabularQLearner(action_count=action_count, epsilon=0.0, seed=0)

    decision = learner.act(current_input)
    transition = stage.step(decision)
    learner.observe(transition)
    summary = learner.update()

    assert isinstance(transition, TrainingTransition)
    assert transition.stage_context == stage.stage_context
    assert transition.projected_coarse_step == stage.frozen_behavior.current_step
    assert transition.fiber_departure is None
    assert summary.updated


def test_plate_support_stage_rejects_illegal_action_index_without_stepping() -> None:
    stage = build_plate_support_stage()
    current_input = stage.reset(seed=0)
    action_count = 0 if current_input.action_mask is None else len(current_input.action_mask)

    transition = stage.step(ActionDecision(chosen_action=action_count + 100))

    assert transition.fiber_departure is not None
    assert transition.bootstrap_reason == "fiber_departure"
