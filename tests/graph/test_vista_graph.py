"""Tests for the vista graph."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.annotations import VistaPayload
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.graph.explored_graph import ExploredGraph
from state_collapser.graph.vista_graph import VistaGraph


class TinyHiddenGraph:
    """Tiny hidden graph for vista-layer tests."""

    def __init__(self) -> None:
        self.source = State(payload=("source",), identity="s1")
        self.target = State(payload=("target",), identity="s2")
        self.action = PrimitiveAction(payload=("step",), identity="a1")
        self.edge = BaseEdge(
            source=self.source,
            action=self.action,
            target=self.target,
            labels=("boundary",),
        )

    def out_edges(self, state: State) -> list[BaseEdge]:
        if state == self.source:
            return [self.edge]
        return []


def test_one_hop_refresh_populates_vista() -> None:
    hidden = TinyHiddenGraph()
    explored = ExploredGraph()
    explored.add_state(hidden.source)
    vista = VistaGraph(hidden, explored)

    vista.refresh_local_vista(hidden.source)

    assert vista.vista_neighbors(hidden.source) == (hidden.target,)
    assert vista.vista_edges(hidden.source) == (hidden.edge,)


def test_push_operation_updates_target_side_annotation_state() -> None:
    hidden = TinyHiddenGraph()
    explored = ExploredGraph()
    vista = VistaGraph(hidden, explored)
    payload = VistaPayload(outgoing_edges=(hidden.edge,), reachable_targets=(hidden.target,))

    vista.push_message(hidden.source, hidden.target, payload)

    assert vista.node_payload(hidden.target).pushed_payloads == (payload,)


def test_pull_operation_updates_source_side_annotation_state() -> None:
    hidden = TinyHiddenGraph()
    explored = ExploredGraph()
    vista = VistaGraph(hidden, explored)
    payload = VistaPayload(outgoing_edges=(hidden.edge,), reachable_targets=(hidden.target,))

    vista.pull_message(hidden.source, hidden.target, payload)

    assert vista.node_payload(hidden.source).pulled_payloads == (payload,)


def test_cumulative_outgoing_edge_knowledge_grows_appropriately() -> None:
    hidden = TinyHiddenGraph()
    explored = ExploredGraph()
    vista = VistaGraph(hidden, explored)
    payload = VistaPayload(outgoing_edges=(hidden.edge,), reachable_targets=(hidden.target,))

    vista.push_message(hidden.source, hidden.target, payload)

    assert hidden.edge in vista.node_payload(hidden.target).outgoing_knowledge_upto(0)
