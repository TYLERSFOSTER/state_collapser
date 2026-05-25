"""Tower-training checks for the rl_counterpoint_v3 example."""

from state_collapser.examples.rl_counterpoint_v3 import (
    TowerTrainingConfig,
    run_tower_training,
)


def test_run_tower_training_returns_structured_result() -> None:
    result = run_tower_training(
        config=TowerTrainingConfig(
            episodes=2,
            max_steps_per_episode=8,
            seed=0,
        )
    )
    assert len(result.episodes) == 2
    assert result.q_table
    assert all(summary.steps <= 8 for summary in result.episodes)
