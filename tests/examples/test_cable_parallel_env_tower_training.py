from __future__ import annotations

from state_collapser.examples.cable_parallel_env import (
    CableParallelEnv,
    TowerTrainingConfig,
    run_tower_training,
)


def test_tower_training_runs_end_to_end() -> None:
    result = run_tower_training(
        env=CableParallelEnv(),
        config=TowerTrainingConfig(episodes=3, max_steps_per_episode=12, seed=0),
    )

    assert len(result.episodes) == 3
    assert result.q_table
