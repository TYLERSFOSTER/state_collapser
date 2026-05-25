"""Core reward contract surface."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StepReward:
    """Reward assigned to one primitive transition."""

    value: float
    weight: float = 1.0


@dataclass(frozen=True, slots=True)
class PathRewardSummary:
    """Weighted cumulative reward summary over a base-tier path."""

    step_rewards: tuple[StepReward, ...] = ()
    total: float = 0.0


@dataclass(frozen=True, slots=True)
class QuotientRewardSummary:
    """Aggregated reward summary over quotient-level contributors."""

    contributing_rewards: tuple[float, ...] = ()
    mean_reward: float = 0.0
    aggregator_name: str = "mean"
    aggregate_reward: float | None = None
    internal_loop_policy: str | None = None
    internal_contributors: tuple[float, ...] = ()


def primitive_step_reward(value: float, weight: float = 1.0) -> StepReward:
    """Construct one primitive step-reward contribution."""

    return StepReward(value=value, weight=weight)


def summarize_path_rewards(step_rewards: tuple[StepReward, ...]) -> PathRewardSummary:
    """Construct the weighted cumulative reward summary for a base-tier path."""

    total = sum(step.value * step.weight for step in step_rewards)
    return PathRewardSummary(step_rewards=step_rewards, total=total)


def summarize_quotient_rewards(
    contributing_rewards: tuple[float, ...],
) -> QuotientRewardSummary:
    """Construct quotient reward summary from boundary-crossing contributors only."""

    if not contributing_rewards:
        return QuotientRewardSummary(
            contributing_rewards=(),
            mean_reward=0.0,
            aggregate_reward=0.0,
        )
    mean_reward = sum(contributing_rewards) / len(contributing_rewards)
    return QuotientRewardSummary(
        contributing_rewards=contributing_rewards,
        mean_reward=mean_reward,
        aggregate_reward=mean_reward,
    )


__all__ = [
    "PathRewardSummary",
    "QuotientRewardSummary",
    "StepReward",
    "primitive_step_reward",
    "summarize_path_rewards",
    "summarize_quotient_rewards",
]
