"""Per-tier control configuration for exploit/explore control."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TierControlConfig:
    """Persistent control knobs for one tier in the first reference controller."""

    epsilon: float = 0.2
    min_visit_count: int = 5
    td_error_threshold: float = 0.5
    success_threshold: float = 0.6
    reward_residual_threshold: float | None = None
    training_interval: int = 4
    batch_size: int = 8


__all__ = ["TierControlConfig"]
