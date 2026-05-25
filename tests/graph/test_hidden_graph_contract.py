"""Tests for the hidden graph contract."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.graph.hidden_graph import HiddenGraph
from state_collapser.graph.spec import GraphSpec


class TinyHiddenGraph:
    """Tiny stub hidden graph used to validate the hidden-graph contract."""

    def __init__(self) -> None:
        self.spec = GraphSpec(name="tiny-hidden-graph", rules=(("branching", 1),))
        self.start = State(payload=("start",), identity="start")
        self.goal = State(payload=("goal",), identity="goal")
        self.step = PrimitiveAction(payload=("step",), identity="step", labels=("forward",))
        self.states = {self.start, self.goal}
        self.actions = {self.step}

    def is_valid_state(self, state: State) -> bool:
        return state in self.states

    def is_valid_action(self, action: PrimitiveAction) -> bool:
        return action in self.actions

    def apply_action(self, state: State, action: PrimitiveAction) -> State | None:
        if state == self.start and action == self.step:
            return self.goal
        return None

    def is_valid_edge(self, edge: BaseEdge) -> bool:
        return (
            self.is_valid_state(edge.source)
            and self.is_valid_action(edge.action)
            and self.apply_action(edge.source, edge.action) == edge.target
        )

    def out_actions(self, state: State) -> list[PrimitiveAction]:
        if state == self.start:
            return [self.step]
        return []

    def out_neighbors(self, state: State) -> list[State]:
        return [
            target
            for action in self.out_actions(state)
            if (target := self.apply_action(state, action)) is not None
        ]

    def out_edges(self, state: State) -> list[BaseEdge]:
        return [
            BaseEdge(source=state, action=action, target=target, labels=("boundary",))
            for action in self.out_actions(state)
            if (target := self.apply_action(state, action)) is not None
        ]


def test_apply_action_agrees_with_is_valid_edge() -> None:
    graph: HiddenGraph = TinyHiddenGraph()
    edge = BaseEdge(
        source=graph.start,
        action=graph.step,
        target=graph.apply_action(graph.start, graph.step),
        labels=("boundary",),
    )

    assert edge.target is not None
    assert graph.is_valid_edge(edge)


def test_outgoing_neighbors_derive_from_outgoing_actions() -> None:
    graph: HiddenGraph = TinyHiddenGraph()

    expected_neighbors = [
        target
        for action in graph.out_actions(graph.start)
        if (target := graph.apply_action(graph.start, action)) is not None
    ]

    assert graph.out_neighbors(graph.start) == expected_neighbors


def test_invalid_states_and_actions_are_rejected() -> None:
    graph: HiddenGraph = TinyHiddenGraph()
    invalid_state = State(payload=("invalid",), identity="invalid")
    invalid_action = PrimitiveAction(payload=("invalid-action",), identity="invalid-action")

    assert not graph.is_valid_state(invalid_state)
    assert not graph.is_valid_action(invalid_action)
