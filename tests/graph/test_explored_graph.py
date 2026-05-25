"""Tests for the explored graph."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.graph.explored_graph import ExploredGraph


def test_adding_a_state_once() -> None:
    graph = ExploredGraph()
    state = State(payload=("region", 1), identity="s1")

    graph.add_state(state)
    graph.add_state(state)

    assert graph.visited_states() == (state,)


def test_adding_multiple_states() -> None:
    graph = ExploredGraph()
    state_a = State(payload=("region", 1), identity="s1")
    state_b = State(payload=("region", 2), identity="s2")

    graph.add_state(state_a)
    graph.add_state(state_b)

    assert graph.visited_states() == (state_a, state_b)


def test_adding_edges() -> None:
    graph = ExploredGraph()
    state_a = State(payload=("region", 1), identity="s1")
    state_b = State(payload=("region", 2), identity="s2")
    action = PrimitiveAction(payload=("step", 1), identity="a1")
    edge = BaseEdge(source=state_a, action=action, target=state_b)

    graph.add_edge(edge)

    assert graph.visited_edges() == (edge,)
    assert graph.has_edge(edge)


def test_path_ordering() -> None:
    graph = ExploredGraph()
    state_a = State(payload=("region", 1), identity="s1")
    state_b = State(payload=("region", 2), identity="s2")
    state_c = State(payload=("region", 3), identity="s3")
    action_ab = PrimitiveAction(payload=("step", 1), identity="a1")
    action_bc = PrimitiveAction(payload=("step", 2), identity="a2")

    graph.add_edge(BaseEdge(source=state_a, action=action_ab, target=state_b))
    graph.add_edge(BaseEdge(source=state_b, action=action_bc, target=state_c))

    assert graph.current_path() == (state_a, state_b, state_c)


def test_current_state_tracking() -> None:
    graph = ExploredGraph()
    state_a = State(payload=("region", 1), identity="s1")
    state_b = State(payload=("region", 2), identity="s2")
    action = PrimitiveAction(payload=("step", 1), identity="a1")

    graph.add_edge(BaseEdge(source=state_a, action=action, target=state_b))

    assert graph.current_state() == state_b
