from __future__ import annotations

from state_collapser.examples.plate_support_env import (
    run_tower_training as exported_run_tower_training,
)
from state_collapser.examples.plate_support_env.env import PlateSupportEnv
from state_collapser.examples.plate_support_env.runtime import PlateSupportEnvRuntime
from state_collapser.examples.plate_support_env.training import (
    TowerTrainingConfig,
    run_tower_training,
    tower_state_key,
)


def test_tower_training_runs_for_at_least_one_episode() -> None:
    result = run_tower_training(
        config=TowerTrainingConfig(episodes=1, max_steps_per_episode=5, seed=7)
    )

    assert len(result.episodes) == 1
    assert result.episodes[0].steps > 0


def test_q_table_changes_across_training() -> None:
    result = run_tower_training(
        config=TowerTrainingConfig(episodes=2, max_steps_per_episode=6, seed=11)
    )

    assert result.q_table
    assert any(any(value != 0.0 for value in row.values()) for row in result.q_table.values())


def test_tower_state_key_comes_from_runtime_snapshot() -> None:
    runtime = PlateSupportEnvRuntime(env=PlateSupportEnv())
    reset_result = runtime.reset()

    key = tower_state_key(reset_result.runtime_snapshot)

    assert key == reset_result.runtime_snapshot.current_position_at_every_tier
    assert len(key) >= 2
    assert key[0] is not None
    assert key[1] is not None


def test_training_loop_is_not_script_replay() -> None:
    result_a = run_tower_training(
        config=TowerTrainingConfig(episodes=1, max_steps_per_episode=8, seed=3)
    )
    result_b = run_tower_training(
        config=TowerTrainingConfig(episodes=1, max_steps_per_episode=8, seed=19)
    )

    table_a = {key: tuple(sorted(row.items())) for key, row in result_a.q_table.items()}
    table_b = {key: tuple(sorted(row.items())) for key, row in result_b.q_table.items()}

    assert table_a != table_b


def test_tower_training_smoke_path_returns_structured_result() -> None:
    result = run_tower_training(
        config=TowerTrainingConfig(episodes=2, max_steps_per_episode=4, seed=5)
    )

    assert result.config.episodes == 2
    assert len(result.episodes) == 2
    assert isinstance(result.q_table, dict)


def test_exported_run_tower_training_entry_point_is_usable() -> None:
    result = exported_run_tower_training(
        config=TowerTrainingConfig(episodes=1, max_steps_per_episode=3, seed=13)
    )

    assert len(result.episodes) == 1
