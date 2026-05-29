"""Tests for shared tower/fiber encoding registry."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition import LabelBlockSchema
from state_collapser.tower.partition.tower import build_partition_tower_full
from state_collapser.training import EncodingRegistry


def _state(index: int) -> State:
    return State(payload=("node", index), identity=("node", index))


def _edge(index: int, source: State, target: State, label: str) -> BaseEdge:
    return BaseEdge(
        source=source,
        action=PrimitiveAction(
            payload=("edge", index),
            identity=("edge", index),
            labels=(label,),
        ),
        target=target,
        labels=(label,),
    )


def _tower_fixture() -> tuple[tuple[State, ...], tuple[BaseEdge, ...]]:
    states = tuple(_state(index) for index in range(4))
    edges = (
        _edge(0, states[0], states[1], "collapse"),
        _edge(1, states[1], states[2], "collapse"),
        _edge(2, states[2], states[3], "message"),
        _edge(3, states[0], states[3], "message"),
    )
    return states, edges


def test_encoding_registry_reuses_partition_tower_ids() -> None:
    states, edges = _tower_fixture()
    tower = build_partition_tower_full(
        states=states,
        edges=edges,
        current_state=states[0],
        schema=LabelBlockSchema.from_labels(("collapse",)),
    )

    registry = EncodingRegistry.from_tower(tower)

    assert registry.encode_state(states[0]) == tower.registry.state_id_by_state[states[0]].value
    assert registry.encode_edge(edges[0]) == tower.registry.edge_id_by_edge[edges[0]].value
    for tier, state_layer in enumerate(tower.state_layers):
        assert registry.encode_tier(tier) == tier
        for state_cell_id in state_layer.all_cell_ids():
            assert registry.encode_state_cell(state_cell_id) is not None
    for action_layer in tower.action_layers:
        for action_cell_id in action_layer.edge_ids_by_action_cell:
            assert registry.encode_action_cell(action_cell_id) is not None


def test_encoding_registry_is_hgraphml_compatible_without_rl_objects() -> None:
    states, edges = _tower_fixture()
    tower = build_partition_tower_full(
        states=states,
        edges=edges,
        current_state=None,
        schema=LabelBlockSchema.from_labels(("collapse",)),
    )

    left = EncodingRegistry.from_tower(tower)
    right = EncodingRegistry.from_tower(tower)

    assert left.registry_id == right.registry_id
    assert left.to_dict()["summary"]
    assert all(left.encode_state(state) is not None for state in states)
    assert all(left.encode_edge(edge) is not None for edge in edges)
