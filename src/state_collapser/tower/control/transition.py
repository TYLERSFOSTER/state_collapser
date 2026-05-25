"""Tier-local abstract transition records."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ActiveTierTransition:
    """One realized active-tier transition under frozen lower support."""

    tier_index: int
    source_state: object | None
    action: object
    target_state: object | None
    aggregated_reward: float
    duration: int = 1
    context_version: int | str | None = None
    representative_jump: object | None = None
    success: bool = True


__all__ = ["ActiveTierTransition"]
