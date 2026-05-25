"""Tests for partition reward aggregation."""

from __future__ import annotations

import math

import pytest

from state_collapser.tower.partition.reward_aggregation import (
    RewardAggregationName,
    RewardAggregator,
    aggregate_rewards,
)


def test_mean_sum_and_max_aggregation() -> None:
    values = (1.0, 3.0, 9.0)

    assert aggregate_rewards(values, aggregator="mean").aggregate_reward == pytest.approx(13 / 3)
    assert aggregate_rewards(values, aggregator="sum").aggregate_reward == 13.0
    assert aggregate_rewards(values, aggregator="max").aggregate_reward == 9.0


def test_empty_reward_input_returns_zero() -> None:
    result = aggregate_rewards((), aggregator="max")

    assert result.contributing_rewards == ()
    assert result.aggregate_reward == 0.0


def test_softmax_aggregation_is_between_mean_and_max_for_positive_values() -> None:
    values = (1.0, 3.0, 9.0)
    result = aggregate_rewards(values, aggregator=RewardAggregationName.SOFTMAX)

    assert result.aggregate_reward > sum(values) / len(values)
    assert result.aggregate_reward <= max(values)


def test_p_mean_and_p_norm_support_infinity() -> None:
    values = (1.0, 3.0, 9.0)

    assert aggregate_rewards(values, aggregator="p_mean", p=math.inf).aggregate_reward == 9.0
    assert aggregate_rewards(values, aggregator="p_norm", p=math.inf).aggregate_reward == 9.0


def test_reward_aggregator_object_delegates_to_aggregate_rewards() -> None:
    aggregator = RewardAggregator(name=RewardAggregationName.MAX)

    result = aggregator.aggregate((2.0, 8.0))

    assert result.aggregator_name == "max"
    assert result.aggregate_reward == 8.0


def test_custom_aggregation_requires_callable() -> None:
    with pytest.raises(ValueError):
        aggregate_rewards((1.0,), aggregator="custom")

    result = aggregate_rewards((1.0, 4.0), aggregator="custom", custom=lambda values: min(values))
    assert result.aggregate_reward == 1.0


def test_invalid_p_and_temperature_are_rejected() -> None:
    with pytest.raises(ValueError):
        aggregate_rewards((1.0,), aggregator="p_mean", p=0)

    with pytest.raises(ValueError):
        aggregate_rewards((1.0,), aggregator="p_norm", p=0)

    with pytest.raises(ValueError):
        aggregate_rewards((1.0,), aggregator="softmax", temperature=0)
