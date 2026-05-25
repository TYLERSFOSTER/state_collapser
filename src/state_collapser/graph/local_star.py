"""Local-star contract surface."""

from __future__ import annotations

from dataclasses import dataclass

from state_collapser.core.annotations import NodeAnnotationStore
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State


@dataclass(frozen=True, slots=True)
class LocalStar:
    """Tier-0 local selection object for contraction-policy input."""

    center: State
    outgoing_edges: tuple[BaseEdge, ...]
    outgoing_neighbors: tuple[State, ...]
    annotations: NodeAnnotationStore


__all__ = ["LocalStar"]
