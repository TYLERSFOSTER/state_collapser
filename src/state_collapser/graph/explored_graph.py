"""Explored-graph contract surface."""

from __future__ import annotations

from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State


class ExploredGraph:
    """Visited-history restriction of the hidden graph."""

    def __init__(self) -> None:
        """Initialize empty visited-state, visited-edge, and path history."""

        self._visited_states: dict[State, None] = {}
        self._visited_edges: dict[BaseEdge, None] = {}
        self._current_state: State | None = None
        self._current_path: list[State] = []

    def has_state(self, state: State) -> bool:
        """Return whether the explored graph already contains the state."""

        return state in self._visited_states

    def has_edge(self, edge: BaseEdge) -> bool:
        """Return whether the explored graph already contains the edge."""

        return edge in self._visited_edges

    def add_state(self, state: State) -> None:
        """Add a visited state and update path/current-state tracking."""

        self._visited_states.setdefault(state, None)
        self._current_state = state
        self._current_path.append(state)

    def add_edge(self, edge: BaseEdge) -> None:
        """Add a visited edge and update the explored-state/path view."""

        self._visited_edges.setdefault(edge, None)
        self._visited_states.setdefault(edge.source, None)
        self._visited_states.setdefault(edge.target, None)
        if not self._current_path:
            self._current_path.append(edge.source)
        elif self._current_path[-1] != edge.source:
            self._current_path.append(edge.source)
        self._current_path.append(edge.target)
        self._current_state = edge.target

    def visited_states(self) -> tuple[State, ...]:
        """Return the unique visited states in insertion order."""

        return tuple(self._visited_states.keys())

    def visited_edges(self) -> tuple[BaseEdge, ...]:
        """Return the unique visited edges in insertion order."""

        return tuple(self._visited_edges.keys())

    def current_state(self) -> State | None:
        """Return the current base-tier state."""

        return self._current_state

    def current_path(self) -> tuple[State, ...]:
        """Return the ordered current base-tier path."""

        return tuple(self._current_path)


__all__ = ["ExploredGraph"]
