"""State-side partition table for one tier of the partition tower."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from state_collapser.tower.partition.ids import StateCellId, StateId


@dataclass(frozen=True, slots=True)
class StateCellMergeResult:
    """Result of coalescing active state cells in a single tier.

    A merge may be a no-op if both endpoints already point at the same cell.
    When it changes the layer, `merged_from` records the predecessor cells that
    form the Young-diagram parent relation for this tier.
    """

    changed: bool
    state_cell_id: StateCellId
    merged_from: tuple[StateCellId, ...] = ()


@dataclass(slots=True)
class StatePartitionLayer:
    """State partition table at one tower tier.

    The layer maps each base-state id to exactly one active state cell and keeps
    the inverse member table. It also records how tier-`i` cells were carried
    from or merged out of tier-`i-1` cells so refinement fibers can be queried
    without reconstructing quotient graphs.
    """

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
        """Create the tier-0 partition where every state is its own cell."""

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
        """Create a new tier by copying the previous tier's active cells."""

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
        """Return the active cell containing a registered base-state id."""

        return self.cell_of_state_id[state_id]

    def members(self, cell_id: StateCellId) -> tuple[StateId, ...]:
        """Return deterministic base-state members of an active state cell."""

        return tuple(sorted(self.members_by_cell_id[cell_id]))

    def all_cell_ids(self) -> tuple[StateCellId, ...]:
        """Return active state-cell ids in deterministic order."""

        return tuple(sorted(self.members_by_cell_id))

    def contains_state(self, state_id: StateId) -> bool:
        """Return whether a registered state id is represented in this layer."""

        return state_id in self.cell_of_state_id

    def add_singleton_state(self, state_id: StateId) -> StateCellId:
        """Add a newly discovered state as a singleton active cell if absent."""

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
        """Replace two active cells by a new coarser state cell.

        The old cells are removed from the active partition but preserved in the
        predecessor maps, which is why callers should treat cell ids as tiered
        historical identities rather than mutable labels.
        """

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
