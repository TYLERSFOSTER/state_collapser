"""Lift/resolve executor contract surface."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from state_collapser.tower.control.active_tier import ActiveTierState
from state_collapser.tower.control.frozen_context import FrozenLowerContext
from state_collapser.tower.control.transition import ActiveTierTransition


@runtime_checkable
class LiftResolveExecutor(Protocol):
    """Execute one active-tier abstract choice through lower-tier support."""

    def execute(
        self,
        active_tier_state: ActiveTierState,
        action: object,
        *,
        frozen_context: FrozenLowerContext,
        mode: str,
    ) -> ActiveTierTransition:
        """Realize an abstract active-tier action and return the realized transition."""


__all__ = ["LiftResolveExecutor"]
