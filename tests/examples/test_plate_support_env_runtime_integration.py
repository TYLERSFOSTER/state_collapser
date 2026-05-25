from __future__ import annotations

from schema_assertions import (
    assert_runtime_scheduled_schema_assignments,
    assert_snapshot_has_nontrivial_tower,
    scheduled_assignment_count,
)

from state_collapser.examples.plate_support_env import START_STATE
from state_collapser.examples.plate_support_env.env import PlateSupportEnv
from state_collapser.examples.plate_support_env.runtime import (
    PlateSupportEnvRuntime,
    action_index_to_primitive_action,
    default_plate_support_schema,
    plate_support_state_to_core_state,
    primitive_action_to_action_index,
)
from state_collapser.tower.partition.schema import NoContractionSchema


def test_runtime_constructs_from_plate_support_env() -> None:
    env = PlateSupportEnv()
    runtime = PlateSupportEnvRuntime(env=env)

    assert runtime.env is env
    assert runtime.quotient_tiers == ()


def test_default_plate_support_schema_is_importable() -> None:
    schema = default_plate_support_schema()

    assert schema.ordered_blocks()


def test_runtime_reset_produces_env_and_runtime_state() -> None:
    env = PlateSupportEnv()
    runtime = PlateSupportEnvRuntime(env=env)

    reset_result = runtime.reset()

    assert reset_result.info["state"] == START_STATE
    assert reset_result.runtime_snapshot.current_base_state == plate_support_state_to_core_state(
        START_STATE
    )
    assert reset_result.runtime_snapshot.current_position_at_every_tier[0] is not None


def test_default_schema_reset_builds_nontrivial_tower() -> None:
    runtime = PlateSupportEnvRuntime(env=PlateSupportEnv())

    reset_result = runtime.reset()

    assert_snapshot_has_nontrivial_tower(reset_result.runtime_snapshot)
    assert_runtime_scheduled_schema_assignments(runtime)


def test_explicit_no_schema_reset_stays_flat() -> None:
    runtime = PlateSupportEnvRuntime(
        env=PlateSupportEnv(),
        contraction_schema=NoContractionSchema(),
    )

    reset_result = runtime.reset()

    assert len(reset_result.runtime_snapshot.current_position_at_every_tier) == 1
    assert scheduled_assignment_count(runtime) == 0


def test_runtime_step_updates_env_and_runtime_state() -> None:
    env = PlateSupportEnv()
    runtime = PlateSupportEnvRuntime(env=env)
    runtime.reset()

    step_result = runtime.step(0)

    assert env.state.x_idx == 3
    assert step_result.info["state"] == env.state
    assert step_result.runtime_snapshot.current_base_state == plate_support_state_to_core_state(
        env.state
    )
    assert step_result.runtime_snapshot.current_step_reward is not None


def test_env_remains_reward_and_transition_authority() -> None:
    env = PlateSupportEnv()
    runtime = PlateSupportEnvRuntime(env=env)
    runtime.reset()

    step_result = runtime.step(0)

    assert step_result.reward == -1.0
    assert step_result.runtime_snapshot.current_step_reward is not None
    assert step_result.runtime_snapshot.current_step_reward.value == -1.0


def test_runtime_uses_core_primitive_actions() -> None:
    env = PlateSupportEnv()
    runtime = PlateSupportEnvRuntime(env=env)
    runtime.reset()

    step_result = runtime.step(2)

    assert action_index_to_primitive_action(2).canonical_identity == "plate-support-action:2"
    assert step_result.runtime_snapshot.current_base_state == plate_support_state_to_core_state(
        env.state
    )


def test_state_mapping_is_stable() -> None:
    mapped = plate_support_state_to_core_state(START_STATE)

    assert mapped.payload == START_STATE
    assert mapped.canonical_identity == ("plate-support-state", START_STATE)


def test_action_mapping_is_stable() -> None:
    primitive = action_index_to_primitive_action(11)

    assert primitive.canonical_identity == "plate-support-action:11"
    assert primitive_action_to_action_index(primitive) == 11


def test_runtime_step_matches_direct_env_step() -> None:
    direct_env = PlateSupportEnv()
    runtime_env = PlateSupportEnv()
    runtime = PlateSupportEnvRuntime(env=runtime_env)

    direct_env.reset()
    runtime.reset()

    direct_result = direct_env.step(2)
    runtime_result = runtime.step(2)

    assert direct_result[0].tolist() == runtime_result.observation.tolist()
    assert direct_env.state == runtime_env.state
    assert runtime_result.runtime_snapshot.current_base_state == plate_support_state_to_core_state(
        runtime_env.state
    )


def test_runtime_reset_initializes_runtime_state_consistently() -> None:
    env = PlateSupportEnv()
    runtime = PlateSupportEnvRuntime(env=env)

    reset_result = runtime.reset()

    assert reset_result.runtime_snapshot.current_base_state == plate_support_state_to_core_state(
        START_STATE
    )
    assert (
        reset_result.runtime_snapshot.explored_graph.current_state()
        == plate_support_state_to_core_state(START_STATE)
    )


def test_invalid_self_loop_action_produces_coherent_runtime_update() -> None:
    env = PlateSupportEnv()
    runtime = PlateSupportEnvRuntime(env=env)
    runtime.reset()

    result = runtime.step(7)

    assert result.info["invalid_move"] is True
    assert result.info["state"] == START_STATE
    assert result.runtime_snapshot.current_base_state == plate_support_state_to_core_state(
        START_STATE
    )
    assert result.runtime_snapshot.current_step_reward is not None
    assert result.runtime_snapshot.current_step_reward.value == -3.0


def test_runtime_snapshot_evolves_across_short_rollout() -> None:
    env = PlateSupportEnv()
    runtime = PlateSupportEnvRuntime(env=env)
    runtime.reset()

    step_one = runtime.step(0)
    step_two = runtime.step(1)

    assert (
        step_one.runtime_snapshot.current_base_state != step_two.runtime_snapshot.current_base_state
    )
    assert len(step_one.runtime_snapshot.cumulative_path_reward.step_rewards) == 1
    assert len(step_two.runtime_snapshot.cumulative_path_reward.step_rewards) == 2
