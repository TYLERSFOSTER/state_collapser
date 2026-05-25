"""Tests for partition-tower ids."""

from __future__ import annotations

from state_collapser.tower.partition.ids import (
    ActionCellId,
    ActionCollectionId,
    EdgeId,
    IdAllocator,
    SchemaBlockId,
    StateCellId,
    StateId,
    TierIndex,
)


def test_id_types_are_hashable_and_value_equal() -> None:
    assert StateId(1) == StateId(1)
    assert hash(StateId(1)) == hash(StateId(1))
    assert EdgeId(1) == EdgeId(1)
    assert SchemaBlockId("x") == SchemaBlockId("x")


def test_distinct_id_types_do_not_compare_equal() -> None:
    assert StateId(1) != EdgeId(1)
    assert StateCellId(tier=0, ordinal=1) != ActionCollectionId(tier=0, ordinal=1)
    assert ActionCollectionId(tier=0, ordinal=1) != ActionCellId(tier=0, ordinal=1)


def test_cell_ids_carry_tier_and_ordinal() -> None:
    state_cell = StateCellId(tier=2, ordinal=7)
    action_collection = ActionCollectionId(tier=2, ordinal=8)
    action_cell = ActionCellId(tier=2, ordinal=9)

    assert state_cell.tier == 2
    assert state_cell.ordinal == 7
    assert action_collection.tier == 2
    assert action_collection.ordinal == 8
    assert action_cell.tier == 2
    assert action_cell.ordinal == 9


def test_repr_is_deterministic_and_includes_type() -> None:
    assert repr(StateId(3)) == "StateId(value=3)"
    assert repr(TierIndex(4)) == "TierIndex(value=4)"
    assert repr(StateCellId(tier=1, ordinal=2)) == "StateCellId(tier=1, ordinal=2)"


def test_id_allocator_is_monotone() -> None:
    allocator = IdAllocator()

    assert allocator.next() == 0
    assert allocator.next() == 1
    assert allocator.next() == 2
