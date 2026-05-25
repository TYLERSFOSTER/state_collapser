"""State-side partition layer for the partition tower."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from state_collapser.tower.partition.ids import StateCellId, StateId


@dataclass(frozen=True, slots=True)
class StateCellMergeResult:
    """Result of merging two state cells."""

    changed: bool
    state_cell_id: StateCellId
    merged_from: tuple[StateCellId, ...] = ()


@dataclass(slots=True)
class StatePartitionLayer:
    """State-side partition layer at one tower tier."""

    tier_index: int
    cell_of_state_id: dict[StateId, StateCellId] = field(default_factory=dict)
    members_by_cell_id: dict[StateCellId, dict[StateId, None]] = field(default_factory=dict)
    parent_cell_by_previous_cell_id: dict[StateCellId, StateCellId] = field(
        default_factory=dict
    )
    previous_cells_by_cell_id: dict[StateCellId, tuple[StateCellId, ...]] = field(
        default_factory=dict
    )
    _next_ordinal: int = 0

    @classmethod
    def singleton_layer(
        cls,
        tier: int,
        state_ids: Iterable[StateId],
    ) -> StatePartitionLayer:
        """Create a layer whose cells are singletons."""

        layer = cls(tier_index=tier)
        for state_id in state_ids:
            cell_id = layer._new_cell_id()
            layer.cell_of_state_id[state_id] = cell_id
            layer.members_by_cell_id[cell_id] = {state_id: None}
            layer.previous_cells_by_cell_id[cell_id] = ()
        return layer

    @classmethod
    def carry_forward_from(
        cls,
        previous_layer: StatePartitionLayer,
        tier: int,
    ) -> StatePartitionLayer:
        """Create a new tier initialized from the previous active partition."""

        layer = cls(tier_index=tier)
        for previous_cell_id in previous_layer.all_cell_ids():
            new_cell_id = layer._new_cell_id()
            members = previous_layer.members(previous_cell_id)
            layer.members_by_cell_id[new_cell_id] = {state_id: None for state_id in members}
            layer.previous_cells_by_cell_id[new_cell_id] = (previous_cell_id,)
            layer.parent_cell_by_previous_cell_id[previous_cell_id] = new_cell_id
            for state_id in members:
                layer.cell_of_state_id[state_id] = new_cell_id
        return layer

    def cell_of(self, state_id: StateId) -> StateCellId:
        """Return the active state cell containing a state."""

        return self.cell_of_state_id[state_id]

    def members(self, cell_id: StateCellId) -> tuple[StateId, ...]:
        """Return deterministic members for a state cell."""

        return tuple(sorted(self.members_by_cell_id[cell_id]))

    def all_cell_ids(self) -> tuple[StateCellId, ...]:
        """Return active state cell ids in deterministic order."""

        return tuple(sorted(self.members_by_cell_id))

    def contains_state(self, state_id: StateId) -> bool:
        """Return whether a state id belongs to this layer."""

        return state_id in self.cell_of_state_id

    def add_singleton_state(self, state_id: StateId) -> StateCellId:
        """Add a state as a singleton active cell if absent."""

        existing = self.cell_of_state_id.get(state_id)
        if existing is not None:
            return existing
        cell_id = self._new_cell_id()
        self.cell_of_state_id[state_id] = cell_id
        self.members_by_cell_id[cell_id] = {state_id: None}
        self.previous_cells_by_cell_id[cell_id] = ()
        return cell_id

    def merge_cells(
        self,
        left_cell_id: StateCellId,
        right_cell_id: StateCellId,
    ) -> StateCellMergeResult:
        """Merge two active state cells in this layer."""

        if left_cell_id == right_cell_id:
            return StateCellMergeResult(
                changed=False,
                state_cell_id=left_cell_id,
                merged_from=(left_cell_id,),
            )

        left_members = self.members(left_cell_id)
        right_members = self.members(right_cell_id)
        merged_members = tuple(sorted((*left_members, *right_members)))
        merged_cell_id = self._new_cell_id()
        self.members_by_cell_id[merged_cell_id] = {state_id: None for state_id in merged_members}
        self.previous_cells_by_cell_id[merged_cell_id] = (left_cell_id, right_cell_id)
        self.parent_cell_by_previous_cell_id[left_cell_id] = merged_cell_id
        self.parent_cell_by_previous_cell_id[right_cell_id] = merged_cell_id
        for state_id in merged_members:
            self.cell_of_state_id[state_id] = merged_cell_id
        del self.members_by_cell_id[left_cell_id]
        del self.members_by_cell_id[right_cell_id]
        return StateCellMergeResult(
            changed=True,
            state_cell_id=merged_cell_id,
            merged_from=(left_cell_id, right_cell_id),
        )

    def _new_cell_id(self) -> StateCellId:
        cell_id = StateCellId(tier=self.tier_index, ordinal=self._next_ordinal)
        self._next_ordinal += 1
        return cell_id


__all__ = [
    "StateCellMergeResult",
    "StatePartitionLayer",
]
