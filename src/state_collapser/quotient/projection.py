"""Projection-map contract surface."""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass, field

from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State


@dataclass(slots=True)
class ProjectionMap:
    """Explicit projection maps from base objects into quotient identifiers."""

    state_projection: dict[State, Hashable] = field(default_factory=dict)
    edge_projection: dict[BaseEdge, Hashable] = field(default_factory=dict)

    def project_state(self, state: State) -> Hashable | None:
        """Return the quotient-node identifier for a state, if known."""

        return self.state_projection.get(state)

    def project_edge(self, edge: BaseEdge) -> Hashable | None:
        """Return the quotient-edge identifier for an edge, if known."""

        return self.edge_projection.get(edge)

    def set_state_projection(self, state: State, quotient_node: Hashable) -> None:
        """Record the quotient-node identifier for a state."""

        self.state_projection[state] = quotient_node

    def set_edge_projection(self, edge: BaseEdge, quotient_edge: Hashable) -> None:
        """Record the quotient-edge identifier for an edge."""

        self.edge_projection[edge] = quotient_edge


__all__ = ["ProjectionMap"]
