"""Tests for the partition base graph registry."""

from __future__ import annotations

import pytest

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.base_registry import BaseGraphRegistry
from state_collapser.tower.partition.ids import EdgeId, StateId


def make_edge(
    source_name: str = "s1",
    target_name: str = "s2",
    *,
    edge_labels: tuple[object, ...] = (),
    action_labels: tuple[object, ...] = (),
) -> BaseEdge:
    source = State(payload=(source_name,), identity=source_name)
    target = State(payload=(target_name,), identity=target_name)
    action = PrimitiveAction(
        payload=("step", source_name, target_name),
        identity=("a", source_name, target_name),
        labels=action_labels,
    )
    return BaseEdge(source=source, action=action, target=target, labels=edge_labels)


def test_register_state_is_stable() -> None:
    registry = BaseGraphRegistry()
    state = State(payload=("s",), identity="s")

    first = registry.register_state(state)
    second = registry.register_state(state)

    assert first == StateId(0)
    assert second == first
    assert registry.state_for_id(first) == state


def test_register_edge_registers_endpoint_states_and_outgoing_index() -> None:
    registry = BaseGraphRegistry()
    edge = make_edge(edge_labels=("boundary",), action_labels=("x",))

    edge_id = registry.register_edge(edge)

    source_id = registry.source_state_id(edge_id)
    target_id = registry.target_state_id(edge_id)
    assert edge_id == EdgeId(0)
    assert registry.edge_for_id(edge_id) == edge
    assert registry.state_for_id(source_id) == edge.source
    assert registry.state_for_id(target_id) == edge.target
    assert registry.outgoing_edge_ids(source_id) == (edge_id,)
    assert registry.outgoing_edge_ids(target_id) == ()
    assert registry.incoming_edge_ids(source_id) == ()
    assert registry.incoming_edge_ids(target_id) == (edge_id,)


def test_register_edge_is_idempotent() -> None:
    registry = BaseGraphRegistry()
    edge = make_edge()

    first = registry.register_edge(edge)
    second = registry.register_edge(edge)

    assert second == first
    assert registry.edge_ids == (first,)


def test_lookup_helpers_raise_for_missing_ids() -> None:
    registry = BaseGraphRegistry()

    with pytest.raises(KeyError):
        registry.edge_for_id(EdgeId(99))

    with pytest.raises(KeyError):
        registry.state_for_id(StateId(99))


def test_register_delta_reports_new_and_known_ids() -> None:
    registry = BaseGraphRegistry()
    edge = make_edge()
    known_state = edge.source
    known_edge = edge
    registry.register_delta((known_state,), (known_edge,))

    new_edge = make_edge("s2", "s3")
    delta = registry.register_delta((known_state,), (known_edge, new_edge))

    assert delta.known_state_ids == (registry.state_id_by_state[known_state],)
    assert delta.known_edge_ids == (registry.edge_id_by_edge[known_edge],)
    assert delta.new_edge_ids == (registry.edge_id_by_edge[new_edge],)


def test_labels_combine_edge_and_action_labels_in_order() -> None:
    registry = BaseGraphRegistry()
    edge = make_edge(edge_labels=("boundary", "x"), action_labels=("x", "fast"))
    edge_id = registry.register_edge(edge)

    assert registry.labels_for_edge_id(edge_id) == ("boundary", "x", "fast")


def test_action_ids_are_stable_by_action_identity() -> None:
    registry = BaseGraphRegistry()
    first = make_edge("s1", "s2")
    second = BaseEdge(
        source=State(payload=("s2",), identity="s2"),
        action=first.action,
        target=State(payload=("s3",), identity="s3"),
    )

    first_id = registry.register_edge(first)
    second_id = registry.register_edge(second)

    assert registry.action_id_for_edge_id(first_id) == registry.action_id_for_edge_id(second_id)
