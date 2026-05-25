"""Tests for the core BaseEdge type."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State


def test_edge_equality() -> None:
    source = State(payload=("region", 1), identity="s1")
    target = State(payload=("region", 2), identity="s2")
    action = PrimitiveAction(payload=("step", 1), identity="a1", labels=("x",))

    edge_a = BaseEdge(source=source, action=action, target=target, labels=("boundary",))
    edge_b = BaseEdge(source=source, action=action, target=target, labels=("boundary",))

    assert edge_a == edge_b


def test_edge_hashing() -> None:
    source = State(payload=("region", 1), identity="s1")
    target = State(payload=("region", 2), identity="s2")
    action = PrimitiveAction(payload=("step", 1), identity="a1", labels=("x",))

    edge_a = BaseEdge(source=source, action=action, target=target, labels=("boundary",))
    edge_b = BaseEdge(source=source, action=action, target=target, labels=("boundary",))

    assert hash(edge_a) == hash(edge_b)


def test_edge_field_preservation() -> None:
    source = State(payload=("region", 1), identity="s1")
    target = State(payload=("region", 2), identity="s2")
    action = PrimitiveAction(payload=("step", 1), identity="a1", labels=("x",))

    edge = BaseEdge(source=source, action=action, target=target, labels=("boundary",))

    assert edge.source == source
    assert edge.action == action
    assert edge.target == target
