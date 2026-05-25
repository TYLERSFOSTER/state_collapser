"""Tests for quotient projection maps."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.quotient.projection import ProjectionMap


def test_projection_correctness() -> None:
    state = State(payload=("region", 1), identity="s1")
    target = State(payload=("region", 2), identity="s2")
    action = PrimitiveAction(payload=("step",), identity="a1")
    edge = BaseEdge(source=state, action=action, target=target)
    projection = ProjectionMap()

    projection.set_state_projection(state, "Q0")
    projection.set_edge_projection(edge, "E0")

    assert projection.project_state(state) == "Q0"
    assert projection.project_edge(edge) == "E0"
