"""Learner contract surface for active-tier training."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from state_collapser.tower.control.frozen_context import FrozenLowerContext
from state_collapser.tower.control.transition import ActiveTierTransition


@dataclass(frozen=True, slots=True)
class LearnerUpdateSummary:
    """Controller-facing summary of one learner update."""

    td_error: float
    success: bool
    reward_residual: float | None = None


@runtime_checkable
class TierLearner(Protocol):
    """Active-tier learner contract for the first exploit/explore implementation."""

    def behavior_action(self, state: object | None, *, mode: str) -> object:
        """Choose an action at the active tier."""

    def observe(
        self,
        transition: ActiveTierTransition,
        *,
        frozen_context: FrozenLowerContext,
    ) -> LearnerUpdateSummary:
        """Record one realized transition and return controller-facing summary."""

    def should_train(self, event_index: int) -> bool:
        """Return whether a learner update is due at this event index."""

    def train(self, *, frozen_context: FrozenLowerContext) -> LearnerUpdateSummary:
        """Run one learner update and return controller-facing summary."""


__all__ = ["LearnerUpdateSummary", "TierLearner"]
