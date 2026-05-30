"""Metrics and reporting surfaces for training-facing code."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True, slots=True)
class EpisodeMetrics:
    """Minimal episode-level metrics surface."""

    episode_index: int
    total_reward: float
    steps: int
    success: bool
    max_tower_depth: int | None = None
    diagnostics: Mapping[str, object] = field(default_factory=dict)


class MetricsHook(Protocol):
    """Minimal reporting hook for training loops and collectors."""

    def on_episode_end(self, metrics: EpisodeMetrics) -> None:
        """Record one completed episode summary."""


@dataclass(slots=True)
class TrainingMetrics:
    """Simple in-memory recorder for first-scope training metrics."""

    episodes: list[EpisodeMetrics] = field(default_factory=list)

    def on_episode_end(self, metrics: EpisodeMetrics) -> None:
        """Append one completed episode's metrics to the in-memory history."""

        self.episodes.append(metrics)


__all__ = ["EpisodeMetrics", "MetricsHook", "TrainingMetrics"]
