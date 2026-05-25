"""Active-tier runtime state for exploit/explore control."""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True, slots=True)
class ActiveTierState:
    """Single active control tier plus the tier-local runtime state bound to it."""

    active_tier: int
    tier_state: object | None
    context_version: int | str | None = None
    event_index: int = 0
    deepest_known_tier: int | None = None

    def has_upstairs(self) -> bool:
        """Return whether a finer upstairs tier exists."""

        return self.active_tier > 0

    def has_downstairs(self) -> bool:
        """Return whether a more collapsed downstairs tier exists."""

        return self.deepest_known_tier is not None and self.active_tier < self.deepest_known_tier

    def upstairs_tier(self) -> int:
        """Return the immediate upstairs tier index."""

        if not self.has_upstairs():
            raise ValueError("Tier 0 has no upstairs tier.")
        return self.active_tier - 1

    def downstairs_tier(self) -> int:
        """Return the immediate downstairs tier index."""

        if not self.has_downstairs():
            raise ValueError("Current tier has no downstairs tier.")
        return self.active_tier + 1

    def descend(self, next_state: object | None = None) -> ActiveTierState:
        """Return a new active-tier state one level downstairs."""

        return replace(
            self,
            active_tier=self.downstairs_tier(),
            tier_state=self.tier_state if next_state is None else next_state,
        )

    def lift(self, next_state: object | None = None) -> ActiveTierState:
        """Return a new active-tier state one level upstairs."""

        return replace(
            self,
            active_tier=self.upstairs_tier(),
            tier_state=self.tier_state if next_state is None else next_state,
        )

    def advance_event(self, next_state: object | None = None) -> ActiveTierState:
        """Return a new active-tier state advanced by one action-time event."""

        return replace(
            self,
            event_index=self.event_index + 1,
            tier_state=self.tier_state if next_state is None else next_state,
        )


__all__ = ["ActiveTierState"]
