"""Base graph registry for partition-tower ids and lookups.

The registry is the immutable-base side of the tower runtime: states, edges, and
primitive action identities receive stable ids once and partition layers point
back to those ids. This keeps tier updates local to partition tables instead of
copying graph objects through every quotient tier.
"""

from __future__ import annotations

from collections.abc import Hashable, Iterable
from dataclasses import dataclass

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.ids import ActionId, EdgeId, IdAllocator, StateId


@dataclass(frozen=True, slots=True)
class RegistryDelta:
    """New and previously known ids produced by one registry update."""

    new_state_ids: tuple[StateId, ...] = ()
    known_state_ids: tuple[StateId, ...] = ()
    new_edge_ids: tuple[EdgeId, ...] = ()
    known_edge_ids: tuple[EdgeId, ...] = ()


class BaseGraphRegistry:
    """Stable id registry for the currently discovered base graph.

    The registry owns base-state ids, base-edge ids, primitive-action ids, and
    source/target/outgoing/incoming lookup tables. Partition layers use these
    ids as their stable substrate, so registering an existing object is
    idempotent and never changes prior layer semantics.
    """

    def __init__(self) -> None:
        """Initialize empty id allocators and lookup tables for a base graph."""

        self._state_allocator = IdAllocator()
        self._edge_allocator = IdAllocator()
        self._action_allocator = IdAllocator()
        self.state_id_by_state: dict[State, StateId] = {}
        self.state_by_id: dict[StateId, State] = {}
        self.edge_id_by_edge: dict[BaseEdge, EdgeId] = {}
        self.edge_by_id: dict[EdgeId, BaseEdge] = {}
        self.action_id_by_identity: dict[Hashable, ActionId] = {}
        self.action_by_id: dict[ActionId, PrimitiveAction] = {}
        self.action_id_by_edge_id: dict[EdgeId, ActionId] = {}
        self.source_by_edge_id: dict[EdgeId, StateId] = {}
        self.target_by_edge_id: dict[EdgeId, StateId] = {}
        self.action_by_edge_id: dict[EdgeId, PrimitiveAction] = {}
        self.labels_by_edge_id: dict[EdgeId, tuple[Hashable, ...]] = {}
        self.outgoing_edge_ids_by_state_id: dict[StateId, dict[EdgeId, None]] = {}
        self.incoming_edge_ids_by_state_id: dict[StateId, dict[EdgeId, None]] = {}

    def register_state(self, state: State) -> StateId:
        """Register a state idempotently and return its stable id."""

        existing = self.state_id_by_state.get(state)
        if existing is not None:
            return existing
        state_id = StateId(self._state_allocator.next())
        self.state_id_by_state[state] = state_id
        self.state_by_id[state_id] = state
        self.outgoing_edge_ids_by_state_id.setdefault(state_id, {})
        self.incoming_edge_ids_by_state_id.setdefault(state_id, {})
        return state_id

    def register_states(self, states: Iterable[State]) -> tuple[StateId, ...]:
        """Register states and return their stable ids in input order."""

        return tuple(self.register_state(state) for state in states)

    def register_edge(self, edge: BaseEdge) -> EdgeId:
        """Register an edge idempotently and update graph adjacency indexes."""

        existing = self.edge_id_by_edge.get(edge)
        if existing is not None:
            return existing

        source_id = self.register_state(edge.source)
        target_id = self.register_state(edge.target)
        action_id = self._register_action(edge.action)
        edge_id = EdgeId(self._edge_allocator.next())
        self.edge_id_by_edge[edge] = edge_id
        self.edge_by_id[edge_id] = edge
        self.source_by_edge_id[edge_id] = source_id
        self.target_by_edge_id[edge_id] = target_id
        self.action_by_edge_id[edge_id] = edge.action
        self.action_id_by_edge_id[edge_id] = action_id
        self.labels_by_edge_id[edge_id] = _combined_labels(edge)
        self.outgoing_edge_ids_by_state_id.setdefault(source_id, {})[edge_id] = None
        self.outgoing_edge_ids_by_state_id.setdefault(target_id, {})
        self.incoming_edge_ids_by_state_id.setdefault(target_id, {})[edge_id] = None
        self.incoming_edge_ids_by_state_id.setdefault(source_id, {})
        return edge_id

    def register_edges(self, edges: Iterable[BaseEdge]) -> tuple[EdgeId, ...]:
        """Register edges and return their stable ids in input order."""

        return tuple(self.register_edge(edge) for edge in edges)

    def register_delta(
        self,
        states: Iterable[State],
        edges: Iterable[BaseEdge],
    ) -> RegistryDelta:
        """Register a discovered graph delta and classify new versus known ids."""

        new_state_ids: list[StateId] = []
        known_state_ids: list[StateId] = []
        new_edge_ids: list[EdgeId] = []
        known_edge_ids: list[EdgeId] = []

        for state in states:
            existing_state_id = self.state_id_by_state.get(state)
            state_id = self.register_state(state)
            if existing_state_id is None:
                new_state_ids.append(state_id)
            else:
                known_state_ids.append(state_id)

        for edge in edges:
            existing_edge_id = self.edge_id_by_edge.get(edge)
            edge_id = self.register_edge(edge)
            if existing_edge_id is None:
                new_edge_ids.append(edge_id)
            else:
                known_edge_ids.append(edge_id)

        return RegistryDelta(
            new_state_ids=tuple(new_state_ids),
            known_state_ids=tuple(known_state_ids),
            new_edge_ids=tuple(new_edge_ids),
            known_edge_ids=tuple(known_edge_ids),
        )

    def state_for_id(self, state_id: StateId) -> State:
        """Return the base state for a registry-local state id."""

        return self.state_by_id[state_id]

    def edge_for_id(self, edge_id: EdgeId) -> BaseEdge:
        """Return the base edge for a registry-local edge id."""

        return self.edge_by_id[edge_id]

    def source_state_id(self, edge_id: EdgeId) -> StateId:
        """Return the source state id for a base-edge id."""

        return self.source_by_edge_id[edge_id]

    def target_state_id(self, edge_id: EdgeId) -> StateId:
        """Return the target state id for a base-edge id."""

        return self.target_by_edge_id[edge_id]

    def action_for_edge_id(self, edge_id: EdgeId) -> PrimitiveAction:
        """Return the primitive action carried by a base-edge id."""

        return self.action_by_edge_id[edge_id]

    def action_id_for_edge_id(self, edge_id: EdgeId) -> ActionId:
        """Return the stable primitive-action id carried by a base-edge id."""

        return self.action_id_by_edge_id[edge_id]

    def labels_for_edge_id(self, edge_id: EdgeId) -> tuple[Hashable, ...]:
        """Return combined edge and primitive-action labels for an edge id."""

        return self.labels_by_edge_id[edge_id]

    def outgoing_edge_ids(self, state_id: StateId) -> tuple[EdgeId, ...]:
        """Return outgoing edge ids from a state id in discovery order."""

        return tuple(self.outgoing_edge_ids_by_state_id.get(state_id, {}).keys())

    def incoming_edge_ids(self, state_id: StateId) -> tuple[EdgeId, ...]:
        """Return incoming edge ids to a state id in discovery order."""

        return tuple(self.incoming_edge_ids_by_state_id.get(state_id, {}).keys())

    @property
    def state_ids(self) -> tuple[StateId, ...]:
        """Return all registered state ids in registry allocation order."""

        return tuple(self.state_by_id.keys())

    @property
    def edge_ids(self) -> tuple[EdgeId, ...]:
        """Return all registered edge ids in registry allocation order."""

        return tuple(self.edge_by_id.keys())

    def _register_action(self, action: PrimitiveAction) -> ActionId:
        identity = action.canonical_identity
        existing = self.action_id_by_identity.get(identity)
        if existing is not None:
            return existing
        action_id = ActionId(self._action_allocator.next())
        self.action_id_by_identity[identity] = action_id
        self.action_by_id[action_id] = action
        return action_id


def _combined_labels(edge: BaseEdge) -> tuple[Hashable, ...]:
    ordered: dict[Hashable, None] = {}
    for label in edge.labels:
        ordered.setdefault(label, None)
    for label in edge.action.labels:
        ordered.setdefault(label, None)
    return tuple(ordered.keys())


__all__ = [
    "BaseGraphRegistry",
    "RegistryDelta",
]
