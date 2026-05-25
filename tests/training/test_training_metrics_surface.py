"""Focused tests for first-scope training metrics."""

from state_collapser.training import EpisodeMetrics, TrainingMetrics


def test_training_metrics_records_episode_summaries() -> None:
    metrics = TrainingMetrics()
    summary = EpisodeMetrics(
        episode_index=0,
        total_reward=1.5,
        steps=3,
        success=True,
        max_tower_depth=4,
    )

    metrics.on_episode_end(summary)

    assert metrics.episodes == [summary]
