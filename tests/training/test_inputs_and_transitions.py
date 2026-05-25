"""Focused tests for training input and transition surfaces."""

from state_collapser.examples.rl_counterpoint_v3 import RlCounterpointEnv, RlCounterpointEnvRuntime
from state_collapser.training import (
    FiberDeparture,
    FiberDepartureReason,
    FiberStageContext,
    TrainingTransition,
    build_action_selection_input,
    summarize_runtime_snapshot,
    tower_position_key,
)


def test_action_selection_input_uses_runtime_snapshot_shape() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    reset_result = runtime.reset(seed=0)

    action_input = build_action_selection_input(
        observation=reset_result.observation,
        runtime_snapshot=reset_result.runtime_snapshot,
    )

    assert action_input.current_base_state == reset_result.runtime_snapshot.current_base_state
    assert action_input.tower_position_key == tuple(
        reset_result.runtime_snapshot.current_position_at_every_tier
    )
    assert action_input.active_tier_state is None


def test_runtime_snapshot_summary_tracks_tower_key_and_depth() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    reset_result = runtime.reset(seed=0)

    summary = summarize_runtime_snapshot(reset_result.runtime_snapshot)

    assert summary.tower_position_key == tower_position_key(reset_result.runtime_snapshot)
    assert summary.tower_depth == len(
        reset_result.runtime_snapshot.current_position_at_every_tier
    )


def test_training_transition_exposes_explicit_bootstrap_fields() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    reset_result = runtime.reset(seed=0)
    action_input = build_action_selection_input(
        observation=reset_result.observation,
        runtime_snapshot=reset_result.runtime_snapshot,
    )

    transition = TrainingTransition(
        source_input=action_input,
        chosen_action=0,
        reward=1.0,
        target_input=action_input,
        terminated=False,
        truncated=False,
        bootstrap_allowed=True,
    )

    assert transition.bootstrap_allowed
    assert transition.bootstrap_input is None
    assert transition.bootstrap_reason == "unspecified"


def test_action_selection_input_can_carry_stage_context() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    reset_result = runtime.reset(seed=0)
    context = FiberStageContext(
        stage_id="stage",
        fiber_id="fiber",
        fine_tier=0,
        coarse_tier=1,
        frozen_behavior_id="frozen",
        frozen_behavior_version=0,
    )
    departure = FiberDeparture(reason=FiberDepartureReason.ACTION_NOT_IN_FIBER)

    action_input = build_action_selection_input(
        observation=reset_result.observation,
        runtime_snapshot=reset_result.runtime_snapshot,
        stage_context=context,
        fiber_departure=departure,
    )

    assert action_input.stage_context == context
    assert action_input.fiber_departure == departure


def test_training_transition_can_carry_stage_context_and_departure() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    reset_result = runtime.reset(seed=0)
    action_input = build_action_selection_input(
        observation=reset_result.observation,
        runtime_snapshot=reset_result.runtime_snapshot,
    )
    context = FiberStageContext(
        stage_id="stage",
        fiber_id="fiber",
        fine_tier=0,
        coarse_tier=1,
        frozen_behavior_id="frozen",
        frozen_behavior_version=0,
    )
    departure = FiberDeparture(reason=FiberDepartureReason.NO_LIFT_CANDIDATE)

    transition = TrainingTransition(
        source_input=action_input,
        chosen_action=0,
        reward=0.0,
        target_input=action_input,
        terminated=False,
        truncated=False,
        bootstrap_allowed=False,
        stage_context=context,
        projected_coarse_step="coarse-step",
        fiber_departure=departure,
    )

    assert transition.stage_context == context
    assert transition.projected_coarse_step == "coarse-step"
    assert transition.fiber_departure == departure
