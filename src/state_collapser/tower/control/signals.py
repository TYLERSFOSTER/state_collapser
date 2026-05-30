"""Tier-level control signals and lowest-unclosed helpers."""

from __future__ import annotations

from dataclasses import dataclass

from state_collapser.tower.control.config import TierControlConfig


@dataclass(slots=True)
class TierSignalState:
    """Mutable signal summary for one tier-level productive-learning locus."""

    visit_count: int = 0
    td_error_ema: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    reward_residual_ema: float = 0.0
    has_reward_residual: bool = False

    @property
    def success_rate(self) -> float:
        """Return empirical success rate, or zero before outcomes exist."""

        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total

    def record_visit(self) -> None:
        """Record one visit to this tier-local learning locus."""

        self.visit_count += 1

    def record_td_error(self, td_error: float, *, alpha: float = 0.5) -> None:
        """Update the exponential moving average of absolute TD error."""

        absolute_td = abs(td_error)
        self.td_error_ema = _ema(self.td_error_ema, absolute_td, alpha)

    def record_outcome(self, *, success: bool) -> None:
        """Record a successful or failed observed outcome."""

        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

    def record_reward_residual(self, reward_residual: float, *, alpha: float = 0.5) -> None:
        """Update the reward-residual moving average and mark it available."""

        self.reward_residual_ema = _ema(self.reward_residual_ema, abs(reward_residual), alpha)
        self.has_reward_residual = True


def _ema(previous: float, value: float, alpha: float) -> float:
    return alpha * value + (1.0 - alpha) * previous


def count_pressure(signal: TierSignalState, config: TierControlConfig) -> float:
    """Return exploration pressure from under-sampling."""

    if signal.visit_count >= config.min_visit_count:
        return 0.0
    deficit = config.min_visit_count - signal.visit_count
    return deficit / max(config.min_visit_count, 1)


def td_error_pressure(signal: TierSignalState, config: TierControlConfig) -> float:
    """Return exploration pressure from TD error."""

    if signal.td_error_ema <= config.td_error_threshold:
        return 0.0
    return signal.td_error_ema - config.td_error_threshold


def failure_pressure(signal: TierSignalState, config: TierControlConfig) -> float:
    """Return exploration pressure from poor success rate."""

    if signal.visit_count == 0:
        return 1.0
    if signal.success_rate >= config.success_threshold:
        return 0.0
    return config.success_threshold - signal.success_rate


def reward_residual_pressure(signal: TierSignalState, config: TierControlConfig) -> float:
    """Return exploration pressure from reward mismatch."""

    threshold = config.reward_residual_threshold
    if threshold is None or not signal.has_reward_residual:
        return 0.0
    if signal.reward_residual_ema <= threshold:
        return 0.0
    return signal.reward_residual_ema - threshold


def exploration_pressure(signal: TierSignalState, config: TierControlConfig) -> float:
    """Return the first-release exploration pressure at one tier-local control locus."""

    return max(
        config.epsilon,
        count_pressure(signal, config),
        td_error_pressure(signal, config),
        failure_pressure(signal, config),
        reward_residual_pressure(signal, config),
    )


def productive_learning_pressure(signal: TierSignalState, config: TierControlConfig) -> float:
    """Return pressure measuring how unclosed/productive the current tier still is."""

    return max(
        count_pressure(signal, config),
        td_error_pressure(signal, config),
        failure_pressure(signal, config),
        reward_residual_pressure(signal, config),
    )


def is_unclosed(signal: TierSignalState, config: TierControlConfig) -> bool:
    """Return whether productive learning still appears open at this tier."""

    return productive_learning_pressure(signal, config) > 0.0


def select_lowest_unclosed_tier(
    deepest_known_tier: int,
    signals_by_tier: dict[int, TierSignalState],
    tier_configs: dict[int, TierControlConfig],
) -> int | None:
    """Return the lowest/highest-indexed productive unclosed tier, if any."""

    for tier_index in range(deepest_known_tier, -1, -1):
        signal = signals_by_tier.get(tier_index, TierSignalState())
        config = tier_configs[tier_index]
        if is_unclosed(signal, config):
            return tier_index
    return None


def should_descend(active_tier: int, lowest_unclosed_tier: int | None) -> bool:
    """Return whether the controller should move downward toward the lowest unclosed tier."""

    return lowest_unclosed_tier is not None and lowest_unclosed_tier > active_tier


def should_lift(active_tier: int, lowest_unclosed_tier: int | None) -> bool:
    """Return whether the controller should move upward toward the next productive locus."""

    return lowest_unclosed_tier is not None and lowest_unclosed_tier < active_tier


__all__ = [
    "TierSignalState",
    "count_pressure",
    "exploration_pressure",
    "failure_pressure",
    "is_unclosed",
    "productive_learning_pressure",
    "reward_residual_pressure",
    "select_lowest_unclosed_tier",
    "should_descend",
    "should_lift",
    "td_error_pressure",
]
