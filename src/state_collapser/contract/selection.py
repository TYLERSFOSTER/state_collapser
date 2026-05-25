"""Edge-selection contract surface."""

from __future__ import annotations

from dataclasses import dataclass

from state_collapser.core.edges import BaseEdge


@dataclass(frozen=True, slots=True)
class EdgeSelection:
    """Immutable set of selected edges returned by a contraction policy."""

    edges: tuple[BaseEdge, ...] = ()


__all__ = ["EdgeSelection"]
