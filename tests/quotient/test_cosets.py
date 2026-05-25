"""Tests for quotient coset storage."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.quotient.cosets import CosetStore


def test_reverse_membership_correctness() -> None:
    state = State(payload=("region", 1), identity="s1")
    target = State(payload=("region", 2), identity="s2")
    action = PrimitiveAction(payload=("step",), identity="a1")
    edge = BaseEdge(source=state, action=action, target=target)
    cosets = CosetStore()

    cosets.add_node_member("Q0", state)
    cosets.add_edge_member("E0", edge)

    assert cosets.node_members("Q0") == frozenset({state})
    assert cosets.edge_members("E0") == frozenset({edge})
