from __future__ import annotations

from state_collapser.examples.dual_arm_manipulation_env import (
    DualArmManipulationEnv,
    TowerTrainingConfig,
    run_tower_training,
)


def test_tower_training_runs_end_to_end() -> None:
    result = run_tower_training(
        env=DualArmManipulationEnv(),
        config=TowerTrainingConfig(episodes=3, max_steps_per_episode=12, seed=0),
    )

    assert len(result.episodes) == 3
    assert result.q_table
