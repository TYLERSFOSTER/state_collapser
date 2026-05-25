"""Tests for partition loop policies."""

from __future__ import annotations

import pytest

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.action_layer import ActionPartitionLayer
from state_collapser.tower.partition.base_registry import BaseGraphRegistry
from state_collapser.tower.partition.ids import EdgeId, StateCellId
from state_collapser.tower.partition.loop_policy import (
    LoopPolicy,
    LoopPolicyName,
    record_internal_edge,
)
from state_collapser.tower.partition.state_layer import StatePartitionLayer


def test_drop_internal_is_default_policy() -> None:
    assert LoopPolicy().name is LoopPolicyName.DROP_INTERNAL
    assert LoopPolicy.drop_internal().name is LoopPolicyName.DROP_INTERNAL


def test_all_loop_policies_are_representable() -> None:
    assert LoopPolicy.aggregate_internal().name is LoopPolicyName.AGGREGATE_INTERNAL
    assert LoopPolicy.formal_stutter().name is LoopPolicyName.FORMAL_STUTTER


def test_internal_edge_record_carries_policy_and_tier_data() -> None:
    record = record_internal_edge(
        edge_id=EdgeId(3),
        tier=2,
        state_cell_id=StateCellId(tier=2, ordinal=5),
        loop_policy=LoopPolicy.drop_internal(),
        reward_contributor=1.25,
    )

    assert record.edge_id == EdgeId(3)
    assert record.tier == 2
    assert record.state_cell_id == StateCellId(tier=2, ordinal=5)
    assert record.policy_name is LoopPolicyName.DROP_INTERNAL
    assert record.reward_contributor == 1.25


@pytest.mark.parametrize(
    "loop_policy",
    (LoopPolicy.aggregate_internal(), LoopPolicy.formal_stutter()),
)
def test_loop_policy_survives_action_layer_carry_forward(loop_policy: LoopPolicy) -> None:
    left = State(payload=("a",), identity="a")
    right = State(payload=("b",), identity="b")
    base_edge = BaseEdge(
        source=left,
        action=PrimitiveAction(payload=("move",), identity="move"),
        target=right,
    )
    registry = BaseGraphRegistry()
    registry.register_edges((base_edge,))
    state_layer = StatePartitionLayer.singleton_layer(tier=0, state_ids=registry.state_ids)
    action_layer = ActionPartitionLayer.from_state_layer_and_registry(
        tier=0,
        state_layer=state_layer,
        registry=registry,
    )
    left_cell = state_layer.cell_of(registry.state_id_by_state[left])
    right_cell = state_layer.cell_of(registry.state_id_by_state[right])
    merged_cell = state_layer.merge_cells(left_cell, right_cell).state_cell_id
    action_layer.merge_collections(
        action_layer.outgoing_collection(left_cell),
        action_layer.outgoing_collection(right_cell),
        merged_cell,
        state_layer,
        registry,
        loop_policy,
    )

    next_state_layer = StatePartitionLayer.carry_forward_from(state_layer, tier=1)
    next_action_layer = ActionPartitionLayer.carry_forward_from(
        action_layer,
        next_state_layer,
        tier=1,
        loop_policy=loop_policy,
    )
    next_cell = next_state_layer.cell_of(registry.state_id_by_state[left])

    records = next_action_layer.internal_edge_records_by_state_cell[next_cell]
    assert records[0].policy_name is loop_policy.name
