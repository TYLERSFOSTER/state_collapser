"""Tests for action-side partition layers."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.action_layer import ActionPartitionLayer
from state_collapser.tower.partition.base_registry import BaseGraphRegistry
from state_collapser.tower.partition.ids import StateId
from state_collapser.tower.partition.loop_policy import LoopPolicy
from state_collapser.tower.partition.state_layer import StatePartitionLayer


def edge(source: str, target: str, action_name: str | None = None) -> BaseEdge:
    action_identity = action_name if action_name is not None else f"{source}->{target}"
    return BaseEdge(
        source=State(payload=(source,), identity=source),
        action=PrimitiveAction(payload=("move", action_identity), identity=action_identity),
        target=State(payload=(target,), identity=target),
    )


def registry_with_edges(*edges: BaseEdge) -> BaseGraphRegistry:
    registry = BaseGraphRegistry()
    registry.register_edges(edges)
    return registry


def test_tier0_outgoing_collections_initialize_from_source_buckets() -> None:
    ab = edge("a", "b")
    ac = edge("a", "c")
    registry = registry_with_edges(ab, ac)
    state_layer = StatePartitionLayer.singleton_layer(tier=0, state_ids=registry.state_ids)

    action_layer = ActionPartitionLayer.from_state_layer_and_registry(
        tier=0,
        state_layer=state_layer,
        registry=registry,
    )

    a_cell = state_layer.cell_of(registry.state_id_by_state[ab.source])
    b_cell = state_layer.cell_of(registry.state_id_by_state[ab.target])
    a_collection = action_layer.outgoing_collection(a_cell)
    b_collection = action_layer.outgoing_collection(b_cell)
    assert action_layer.edge_ids_for_collection(a_collection) == (
        registry.edge_id_by_edge[ab],
        registry.edge_id_by_edge[ac],
    )
    assert action_layer.edge_ids_for_collection(b_collection) == ()


def test_carry_forward_preserves_outgoing_edges_with_new_state_cells() -> None:
    ab = edge("a", "b")
    registry = registry_with_edges(ab)
    previous_state_layer = StatePartitionLayer.singleton_layer(
        tier=0,
        state_ids=registry.state_ids,
    )
    previous_action_layer = ActionPartitionLayer.from_state_layer_and_registry(
        tier=0,
        state_layer=previous_state_layer,
        registry=registry,
    )
    current_state_layer = StatePartitionLayer.carry_forward_from(previous_state_layer, tier=1)

    current_action_layer = ActionPartitionLayer.carry_forward_from(
        previous_action_layer,
        current_state_layer,
        tier=1,
        loop_policy=LoopPolicy.drop_internal(),
    )

    a_cell = current_state_layer.cell_of(registry.state_id_by_state[ab.source])
    collection = current_action_layer.outgoing_collection(a_cell)
    assert current_action_layer.edge_ids_for_collection(collection) == (
        registry.edge_id_by_edge[ab],
    )


def test_merge_collections_unions_outgoing_data_and_records_internal_edges() -> None:
    ab = edge("a", "b")
    ac = edge("a", "c")
    bd = edge("b", "d")
    registry = registry_with_edges(ab, ac, bd)
    state_layer = StatePartitionLayer.singleton_layer(tier=1, state_ids=registry.state_ids)
    action_layer = ActionPartitionLayer.from_state_layer_and_registry(
        tier=1,
        state_layer=state_layer,
        registry=registry,
    )
    a_cell = state_layer.cell_of(registry.state_id_by_state[ab.source])
    b_cell = state_layer.cell_of(registry.state_id_by_state[ab.target])
    a_collection = action_layer.outgoing_collection(a_cell)
    b_collection = action_layer.outgoing_collection(b_cell)

    state_merge = state_layer.merge_cells(a_cell, b_cell)
    action_merge = action_layer.merge_collections(
        a_collection,
        b_collection,
        state_merge.state_cell_id,
        state_layer,
        registry,
        LoopPolicy.drop_internal(),
    )

    assert action_layer.edge_ids_for_collection(action_merge.action_collection_id) == (
        registry.edge_id_by_edge[ac],
        registry.edge_id_by_edge[bd],
    )
    assert action_layer.internal_edge_ids(state_merge.state_cell_id) == (
        registry.edge_id_by_edge[ab],
    )
    assert action_merge.internal_edges[0].edge_id == registry.edge_id_by_edge[ab]


def test_dirty_collection_tracking_is_local_to_affected_collection() -> None:
    ab = edge("a", "b")
    cd = edge("c", "d")
    registry = registry_with_edges(ab, cd)
    state_layer = StatePartitionLayer.singleton_layer(tier=1, state_ids=registry.state_ids)
    action_layer = ActionPartitionLayer.from_state_layer_and_registry(
        tier=1,
        state_layer=state_layer,
        registry=registry,
    )
    # Initial construction indexes collections and clears dirty flags.
    assert action_layer.dirty_collection_ids == {}
    a_cell = state_layer.cell_of(registry.state_id_by_state[ab.source])
    b_cell = state_layer.cell_of(registry.state_id_by_state[ab.target])
    c_cell = state_layer.cell_of(registry.state_id_by_state[cd.source])
    c_collection = action_layer.outgoing_collection(c_cell)

    state_merge = state_layer.merge_cells(a_cell, b_cell)
    action_merge = action_layer.merge_collections(
        action_layer.outgoing_collection(a_cell),
        action_layer.outgoing_collection(b_cell),
        state_merge.state_cell_id,
        state_layer,
        registry,
        LoopPolicy.drop_internal(),
    )

    assert c_collection not in action_layer.dirty_collection_ids
    assert action_merge.action_collection_id not in action_layer.dirty_collection_ids


def test_action_cell_grouping_uses_source_target_and_action_identity() -> None:
    ab_1 = edge("a", "b", action_name="first")
    ab_2 = edge("a", "b", action_name="second")
    registry = registry_with_edges(ab_1, ab_2)
    state_layer = StatePartitionLayer.singleton_layer(tier=0, state_ids=registry.state_ids)
    action_layer = ActionPartitionLayer.from_state_layer_and_registry(
        tier=0,
        state_layer=state_layer,
        registry=registry,
    )

    a_cell = state_layer.cell_of(registry.state_id_by_state[ab_1.source])
    collection = action_layer.outgoing_collection(a_cell)
    action_cells = action_layer.action_cells_for_collection(collection)

    assert len(action_cells) == 2
    assert tuple(
        action_layer.edge_ids_for_action_cell(action_cell)[0] for action_cell in action_cells
    ) == (registry.edge_id_by_edge[ab_1], registry.edge_id_by_edge[ab_2])


def test_representative_edge_ids_are_deterministic() -> None:
    ab = edge("a", "b")
    registry = registry_with_edges(ab)
    state_layer = StatePartitionLayer.singleton_layer(tier=0, state_ids=registry.state_ids)
    action_layer = ActionPartitionLayer.from_state_layer_and_registry(
        tier=0,
        state_layer=state_layer,
        registry=registry,
    )
    a_cell = state_layer.cell_of(StateId(0))
    collection = action_layer.outgoing_collection(a_cell)
    action_cell = action_layer.action_cells_for_collection(collection)[0]

    assert action_layer.representative_edge_ids(action_cell) == (registry.edge_id_by_edge[ab],)
