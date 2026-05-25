"""Tests for core reward objects and path summaries."""

from __future__ import annotations

from state_collapser.core.rewards import StepReward, primitive_step_reward, summarize_path_rewards


def test_step_reward_construction() -> None:
    reward = primitive_step_reward(2.5, weight=0.5)

    assert reward == StepReward(value=2.5, weight=0.5)


def test_cumulative_weighted_path_reward() -> None:
    summary = summarize_path_rewards(
        (
            StepReward(value=2.0, weight=0.5),
            StepReward(value=3.0, weight=2.0),
        )
    )

    assert summary.total == 7.0
