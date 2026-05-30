"""Vista-graph contract surface."""

from __future__ import annotations

from state_collapser.core.annotations import NodeAnnotationStore, VistaPayload
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.graph.explored_graph import ExploredGraph
from state_collapser.graph.hidden_graph import HiddenGraph


class VistaGraph:
    """Explored graph plus maintained one-hop visible fringe."""

    def __init__(self, hidden_graph: HiddenGraph, explored_graph: ExploredGraph) -> None:
        """Bind hidden/explored graphs and initialize empty vista caches."""

        self._hidden_graph = hidden_graph
        self._explored_graph = explored_graph
        self._vista_edge_cache: dict[State, tuple[BaseEdge, ...]] = {}
        self._vista_neighbor_cache: dict[State, tuple[State, ...]] = {}
        self._annotation_stores: dict[State, NodeAnnotationStore] = {}

    def refresh_local_vista(self, state: State) -> None:
        """Refresh cached one-hop vista information for a visited state."""

        edges = tuple(self._hidden_graph.out_edges(state))
        self._vista_edge_cache[state] = edges
        self._vista_neighbor_cache[state] = tuple(edge.target for edge in edges)
        self._annotation_stores.setdefault(state, NodeAnnotationStore())

    def vista_neighbors(self, state: State) -> tuple[State, ...]:
        """Return cached one-hop vista neighbors for a state."""

        return self._vista_neighbor_cache.get(state, ())

    def vista_edges(self, state: State) -> tuple[BaseEdge, ...]:
        """Return cached one-hop vista edges for a state."""

        return self._vista_edge_cache.get(state, ())

    def push_message(self, source: State, target: State, payload: VistaPayload) -> None:
        """Push payload-derived annotation information toward a target node."""

        self._annotation_stores.setdefault(source, NodeAnnotationStore())
        target_store = self._annotation_stores.setdefault(target, NodeAnnotationStore())
        target_store.receive_pushed_payload(payload)
        for edge in payload.outgoing_edges:
            target_store.add_outgoing_knowledge(0, edge)

    def pull_message(self, source: State, target: State, payload: VistaPayload) -> None:
        """Pull payload-derived annotation information back toward a source node."""

        self._annotation_stores.setdefault(target, NodeAnnotationStore())
        source_store = self._annotation_stores.setdefault(source, NodeAnnotationStore())
        source_store.receive_pulled_payload(payload)
        for edge in payload.outgoing_edges:
            source_store.add_outgoing_knowledge(0, edge)

    def node_payload(self, state: State) -> NodeAnnotationStore:
        """Return the node-local annotation store for a state."""

        return self._annotation_stores.setdefault(state, NodeAnnotationStore())


__all__ = ["VistaGraph"]
