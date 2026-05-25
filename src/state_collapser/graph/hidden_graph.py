"""Hidden graph contract surface."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State


class HiddenGraph(Protocol):
    """Protocol for legality and local-neighborhood hidden-graph queries."""

    def is_valid_state(self, state: State) -> bool:
        """Return whether the provided state belongs to the hidden graph."""

    def is_valid_action(self, action: PrimitiveAction) -> bool:
        """Return whether the provided action belongs to the hidden graph."""

    def apply_action(self, state: State, action: PrimitiveAction) -> State | None:
        """Apply a primitive action to a state, if that transition is defined."""

    def is_valid_edge(self, edge: BaseEdge) -> bool:
        """Return whether the provided edge is a valid hidden-graph edge."""

    def out_actions(self, state: State) -> Iterable[PrimitiveAction]:
        """Return the outgoing primitive actions from the provided state."""

    def out_neighbors(self, state: State) -> Iterable[State]:
        """Return the outgoing neighbor states from the provided state."""

    def out_edges(self, state: State) -> Iterable[BaseEdge]:
        """Return the outgoing edges from the provided state."""


__all__ = ["HiddenGraph"]
