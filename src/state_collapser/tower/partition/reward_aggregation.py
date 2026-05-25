"""Reward aggregation utilities for quotient action cells."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum


class RewardAggregationName(StrEnum):
    """Supported quotient reward aggregation rules."""

    SUM = "sum"
    MEAN = "mean"
    MAX = "max"
    SOFTMAX = "softmax"
    P_MEAN = "p_mean"
    P_NORM = "p_norm"
    CUSTOM = "custom"


@dataclass(frozen=True, slots=True)
class RewardAggregationResult:
    """Result of aggregating fine rewards into a quotient reward."""

    aggregator_name: str
    contributing_rewards: tuple[float, ...]
    aggregate_reward: float


@dataclass(frozen=True, slots=True)
class RewardAggregator:
    """Configuration object for direct-image reward aggregation."""

    name: RewardAggregationName | str = RewardAggregationName.MEAN
    p: float = 2.0
    temperature: float = 1.0
    custom: Callable[[tuple[float, ...]], float] | None = None

    def aggregate(self, values: tuple[float, ...]) -> RewardAggregationResult:
        """Aggregate values according to this configuration."""

        return aggregate_rewards(
            values,
            aggregator=self.name,
            p=self.p,
            temperature=self.temperature,
            custom=self.custom,
        )


def aggregate_rewards(
    values: tuple[float, ...],
    *,
    aggregator: RewardAggregationName | str = RewardAggregationName.MEAN,
    p: float = 2.0,
    temperature: float = 1.0,
    custom: Callable[[tuple[float, ...]], float] | None = None,
) -> RewardAggregationResult:
    """Aggregate fine rewards into one quotient-level reward."""

    name = _normalize_name(aggregator)
    if not values:
        return RewardAggregationResult(
            aggregator_name=name.value,
            contributing_rewards=(),
            aggregate_reward=0.0,
        )

    if name is RewardAggregationName.SUM:
        reward = sum(values)
    elif name is RewardAggregationName.MEAN:
        reward = sum(values) / len(values)
    elif name is RewardAggregationName.MAX:
        reward = max(values)
    elif name is RewardAggregationName.SOFTMAX:
        reward = _softmax_aggregate(values, temperature)
    elif name is RewardAggregationName.P_MEAN:
        reward = _p_mean(values, p)
    elif name is RewardAggregationName.P_NORM:
        reward = _p_norm(values, p)
    elif name is RewardAggregationName.CUSTOM:
        if custom is None:
            raise ValueError("custom reward aggregation requires a callable.")
        reward = custom(values)
    else:
        raise AssertionError(f"Unhandled reward aggregator: {name!r}")

    return RewardAggregationResult(
        aggregator_name=name.value,
        contributing_rewards=values,
        aggregate_reward=float(reward),
    )


def _normalize_name(aggregator: RewardAggregationName | str) -> RewardAggregationName:
    if isinstance(aggregator, RewardAggregationName):
        return aggregator
    return RewardAggregationName(aggregator)


def _softmax_aggregate(values: tuple[float, ...], temperature: float) -> float:
    if temperature <= 0:
        raise ValueError("softmax reward aggregation temperature must be positive.")
    scaled = tuple(value / temperature for value in values)
    max_scaled = max(scaled)
    weights = tuple(math.exp(value - max_scaled) for value in scaled)
    denominator = sum(weights)
    return sum(weight * value for weight, value in zip(weights, values, strict=True)) / denominator


def _p_mean(values: tuple[float, ...], p: float) -> float:
    if math.isinf(p):
        return max(values)
    if p <= 0:
        raise ValueError("p_mean requires p > 0.")
    return float((sum(abs(value) ** p for value in values) / len(values)) ** (1 / p))


def _p_norm(values: tuple[float, ...], p: float) -> float:
    if math.isinf(p):
        return max(abs(value) for value in values)
    if p <= 0:
        raise ValueError("p_norm requires p > 0.")
    return float(sum(abs(value) ** p for value in values) ** (1 / p))


__all__ = [
    "RewardAggregationName",
    "RewardAggregationResult",
    "RewardAggregator",
    "aggregate_rewards",
]
