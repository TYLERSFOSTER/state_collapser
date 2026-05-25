"""Frozen lower-tier context for higher-resolution correction training."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class FrozenLowerContext:
    """Lower-tier support treated as fixed while an active tier is trained."""

    supporting_tier: int | None
    policy_state: object | None = None
    representative_data: object | None = None
    cached_lift_data: object | None = None
    version: int = 0
    metadata: dict[str, object] = field(default_factory=dict)


__all__ = ["FrozenLowerContext"]
