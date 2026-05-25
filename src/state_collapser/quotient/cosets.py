"""Coset-storage contract surface."""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass, field

from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State


@dataclass(slots=True)
class CosetStore:
    """Reverse-membership storage for quotient nodes and quotient edges."""

    quotient_node_members: dict[Hashable, set[State]] = field(default_factory=dict)
    quotient_edge_members: dict[Hashable, set[BaseEdge]] = field(default_factory=dict)

    def add_node_member(self, quotient_node: Hashable, state: State) -> None:
        """Record a state as a member of a quotient node."""

        self.quotient_node_members.setdefault(quotient_node, set()).add(state)

    def add_edge_member(self, quotient_edge: Hashable, edge: BaseEdge) -> None:
        """Record a base edge as a member of a quotient edge."""

        self.quotient_edge_members.setdefault(quotient_edge, set()).add(edge)

    def node_members(self, quotient_node: Hashable) -> frozenset[State]:
        """Return the members of a quotient node."""

        return frozenset(self.quotient_node_members.get(quotient_node, set()))

    def edge_members(self, quotient_edge: Hashable) -> frozenset[BaseEdge]:
        """Return the members of a quotient edge."""

        return frozenset(self.quotient_edge_members.get(quotient_edge, set()))


__all__ = ["CosetStore"]
