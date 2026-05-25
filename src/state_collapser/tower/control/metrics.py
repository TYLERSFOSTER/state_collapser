"""Metrics surface for exploit/explore controller observability."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from state_collapser.tower.control.controller import ControlAction


@dataclass(slots=True)
class TierControlMetrics:
    """Accumulate active-tier occupancy and controller-mode counts."""

    active_tier_counts: Counter[int] = field(default_factory=Counter)
    mode_counts: Counter[ControlAction] = field(default_factory=Counter)

    def record(self, *, active_tier: int, action: ControlAction) -> None:
        self.active_tier_counts[active_tier] += 1
        self.mode_counts[action] += 1

    def reset(self) -> None:
        self.active_tier_counts.clear()
        self.mode_counts.clear()


__all__ = ["TierControlMetrics"]
