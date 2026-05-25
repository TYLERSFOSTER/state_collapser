"""Tests for state-side partition layers."""

from __future__ import annotations

from state_collapser.tower.partition.ids import StateCellId, StateId
from state_collapser.tower.partition.state_layer import StatePartitionLayer


def test_singleton_layer_maps_each_state_to_own_cell() -> None:
    states = (StateId(0), StateId(1), StateId(2))

    layer = StatePartitionLayer.singleton_layer(tier=0, state_ids=states)

    assert layer.all_cell_ids() == (
        StateCellId(tier=0, ordinal=0),
        StateCellId(tier=0, ordinal=1),
        StateCellId(tier=0, ordinal=2),
    )
    for state_id in states:
        assert layer.members(layer.cell_of(state_id)) == (state_id,)


def test_carry_forward_layer_preserves_membership_with_new_tier_ids() -> None:
    previous = StatePartitionLayer.singleton_layer(tier=0, state_ids=(StateId(0), StateId(1)))

    current = StatePartitionLayer.carry_forward_from(previous, tier=1)

    assert current.all_cell_ids() == (
        StateCellId(tier=1, ordinal=0),
        StateCellId(tier=1, ordinal=1),
    )
    assert current.members(StateCellId(tier=1, ordinal=0)) == (StateId(0),)
    assert current.parent_cell_by_previous_cell_id[StateCellId(tier=0, ordinal=0)] == StateCellId(
        tier=1,
        ordinal=0,
    )


def test_merge_cells_creates_new_cell_and_updates_members() -> None:
    layer = StatePartitionLayer.singleton_layer(tier=1, state_ids=(StateId(0), StateId(1)))

    result = layer.merge_cells(StateCellId(tier=1, ordinal=0), StateCellId(tier=1, ordinal=1))

    assert result.changed is True
    assert result.state_cell_id == StateCellId(tier=1, ordinal=2)
    assert layer.members(result.state_cell_id) == (StateId(0), StateId(1))
    assert layer.cell_of(StateId(0)) == result.state_cell_id
    assert layer.cell_of(StateId(1)) == result.state_cell_id
    assert layer.all_cell_ids() == (result.state_cell_id,)


def test_merge_preserves_unaffected_cells() -> None:
    layer = StatePartitionLayer.singleton_layer(
        tier=1,
        state_ids=(StateId(0), StateId(1), StateId(2)),
    )

    result = layer.merge_cells(StateCellId(tier=1, ordinal=0), StateCellId(tier=1, ordinal=1))

    assert layer.all_cell_ids() == (StateCellId(tier=1, ordinal=2), result.state_cell_id)
    assert layer.members(StateCellId(tier=1, ordinal=2)) == (StateId(2),)


def test_repeated_merge_of_same_cell_is_noop() -> None:
    layer = StatePartitionLayer.singleton_layer(tier=1, state_ids=(StateId(0),))

    result = layer.merge_cells(StateCellId(tier=1, ordinal=0), StateCellId(tier=1, ordinal=0))

    assert result.changed is False
    assert result.state_cell_id == StateCellId(tier=1, ordinal=0)
    assert layer.members(result.state_cell_id) == (StateId(0),)


def test_contains_state_reports_membership() -> None:
    layer = StatePartitionLayer.singleton_layer(tier=0, state_ids=(StateId(4),))

    assert layer.contains_state(StateId(4)) is True
    assert layer.contains_state(StateId(5)) is False
