"""Current-tier controller for exploit/explore runtime control."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from state_collapser.tower.control.active_tier import ActiveTierState
from state_collapser.tower.control.config import TierControlConfig
from state_collapser.tower.control.frozen_context import FrozenLowerContext
from state_collapser.tower.control.signals import (
    TierSignalState,
    exploration_pressure,
    select_lowest_unclosed_tier,
    should_descend,
    should_lift,
)


class ControlAction(StrEnum):
    """First-release controller action modes."""

    EXPLORE = "explore"
    TRAIN = "train"
    DESCEND = "descend"
    LIFT = "lift"
    EXPLOIT_EXECUTE = "exploit_execute"


@dataclass(frozen=True, slots=True)
class ControllerDecision:
    """One controller decision at one active-tier action-time event."""

    action: ControlAction
    pressure: float


class ActiveTierController:
    """Single-active-tier gating controller for the first reference regime."""

    def decide(
        self,
        active_tier_state: ActiveTierState,
        signal: TierSignalState,
        config: TierControlConfig,
        *,
        signals_by_tier: dict[int, TierSignalState],
        tier_configs: dict[int, TierControlConfig],
        frozen_context: FrozenLowerContext,
        training_due: bool,
    ) -> ControllerDecision:
        """Choose the next exploit/explore/train/lift/descend control action."""

        del frozen_context  # first-release controller gates on explicit signals/config only

        pressure = exploration_pressure(signal, config)
        lowest_unclosed_tier = select_lowest_unclosed_tier(
            (
                active_tier_state.active_tier
                if active_tier_state.deepest_known_tier is None
                else active_tier_state.deepest_known_tier
            ),
            signals_by_tier,
            tier_configs,
        )
        if active_tier_state.has_upstairs() and should_lift(
            active_tier_state.active_tier, lowest_unclosed_tier
        ):
            return ControllerDecision(action=ControlAction.LIFT, pressure=pressure)
        if active_tier_state.has_downstairs() and should_descend(
            active_tier_state.active_tier, lowest_unclosed_tier
        ):
            return ControllerDecision(action=ControlAction.DESCEND, pressure=pressure)
        if training_due:
            return ControllerDecision(action=ControlAction.TRAIN, pressure=pressure)
        if pressure > config.epsilon:
            return ControllerDecision(action=ControlAction.EXPLORE, pressure=pressure)
        return ControllerDecision(action=ControlAction.EXPLOIT_EXECUTE, pressure=pressure)


__all__ = ["ActiveTierController", "ControlAction", "ControllerDecision"]
