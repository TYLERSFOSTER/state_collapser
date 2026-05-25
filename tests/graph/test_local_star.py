"""Tests for the local star."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.graph.explored_graph import ExploredGraph
from state_collapser.graph.local_star import LocalStar
from state_collapser.graph.vista_graph import VistaGraph


class TinyHiddenGraph:
    """Tiny hidden graph for local-star tests."""

    def __init__(self) -> None:
        self.source = State(payload=("source",), identity="s1")
        self.target = State(payload=("target",), identity="s2")
        self.action = PrimitiveAction(payload=("step",), identity="a1")
        self.edge = BaseEdge(source=self.source, action=self.action, target=self.target)

    def out_edges(self, state: State) -> list[BaseEdge]:
        if state == self.source:
            return [self.edge]
        return []


def test_local_star_reflects_current_vista_data() -> None:
    hidden = TinyHiddenGraph()
    explored = ExploredGraph()
    explored.add_state(hidden.source)
    vista = VistaGraph(hidden, explored)
    vista.refresh_local_vista(hidden.source)

    star = LocalStar(
        center=hidden.source,
        outgoing_edges=vista.vista_edges(hidden.source),
        outgoing_neighbors=vista.vista_neighbors(hidden.source),
        annotations=vista.node_payload(hidden.source),
    )

    assert star.outgoing_edges == (hidden.edge,)
    assert star.outgoing_neighbors == (hidden.target,)


def test_local_labels_and_annotations_are_included() -> None:
    hidden = TinyHiddenGraph()
    explored = ExploredGraph()
    explored.add_state(hidden.source)
    vista = VistaGraph(hidden, explored)
    vista.refresh_local_vista(hidden.source)
    store = vista.node_payload(hidden.source)
    store.add_label("seen")
    store.add_note("color", "blue")

    star = LocalStar(
        center=hidden.source,
        outgoing_edges=vista.vista_edges(hidden.source),
        outgoing_neighbors=vista.vista_neighbors(hidden.source),
        annotations=store,
    )

    assert star.annotations.labels == frozenset({"seen"})
    assert star.annotations.notes == {"color": "blue"}
