"""Action-side partition table for one tier of the partition tower.

An action collection is storage-level outgoing edge data attached to a state
cell. An action cell is decision-level data: a selectable abstract action class
inside one outgoing collection. The layer keeps these separate so state-cell
coarsening can update outgoing data without forcing callers to rebuild quotient
graphs from scratch.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from state_collapser.tower.partition.base_registry import BaseGraphRegistry
from state_collapser.tower.partition.ids import (
    ActionCellId,
    ActionCollectionId,
    EdgeId,
    StateCellId,
    StateId,
)
from state_collapser.tower.partition.loop_policy import (
    InternalEdgeRecord,
    LoopPolicy,
    record_internal_edge,
)
from state_collapser.tower.partition.state_layer import StatePartitionLayer


@dataclass(frozen=True, slots=True)
class ActionCollectionMergeResult:
    """Result of coalescing outgoing-action collections after a state merge.

    `internal_edges` records edges that became loops inside the merged state
    cell and were removed from the live outgoing decision surface according to
    the active loop policy.
    """

    action_collection_id: ActionCollectionId
    merged_from: tuple[ActionCollectionId, ...]
    internal_edges: tuple[InternalEdgeRecord, ...] = ()


@dataclass(slots=True)
class ActionPartitionLayer:
    """Action partition table aligned with a state partition tier.

    Each state cell points to one outgoing-action collection. Each collection is
    then partitioned into action cells by source cell, target cell, and primitive
    action identity. Dirty collections mark the small part of the table that
    must be rebuilt after state-cell merges or target-cell changes.
    """

    tier_index: int
    outgoing_collection_by_state_cell: dict[StateCellId, ActionCollectionId] = field(
        default_factory=dict
    )
    edge_ids_by_collection: dict[ActionCollectionId, dict[EdgeId, None]] = field(
        default_factory=dict
    )
    internal_edge_ids_by_state_cell: dict[StateCellId, dict[EdgeId, None]] = field(
        default_factory=dict
    )
    internal_edge_records_by_state_cell: dict[
        StateCellId,
        tuple[InternalEdgeRecord, ...],
    ] = field(default_factory=dict)
    action_cell_ids_by_collection: dict[
        ActionCollectionId,
        tuple[ActionCellId, ...],
    ] = field(default_factory=dict)
    edge_ids_by_action_cell: dict[ActionCellId, dict[EdgeId, None]] = field(
        default_factory=dict
    )
    source_cell_by_action_cell: dict[ActionCellId, StateCellId] = field(default_factory=dict)
    target_cell_by_action_cell: dict[ActionCellId, StateCellId | None] = field(
        default_factory=dict
    )
    label_key_by_action_cell: dict[ActionCellId, object | None] = field(default_factory=dict)
    source_child_cells_by_action_cell: dict[ActionCellId, tuple[StateCellId, ...]] = field(
        default_factory=dict
    )
    edge_ids_by_action_cell_by_source_child: dict[
        ActionCellId,
        dict[StateCellId, tuple[EdgeId, ...]],
    ] = field(default_factory=dict)
    lower_action_cells_by_action_cell_by_source_child: dict[
        ActionCellId,
        dict[StateCellId, tuple[ActionCellId, ...]],
    ] = field(default_factory=dict)
    active_child_cells_by_collection: dict[
        ActionCollectionId,
        tuple[StateCellId, ...],
    ] = field(default_factory=dict)
    edge_ids_by_action_cell_by_base_source: dict[
        ActionCellId,
        dict[StateId, tuple[EdgeId, ...]],
    ] = field(default_factory=dict)
    base_source_ids_by_action_cell: dict[ActionCellId, tuple[StateId, ...]] = field(
        default_factory=dict
    )
    base_active_source_ids_by_collection: dict[
        ActionCollectionId,
        tuple[StateId, ...],
    ] = field(default_factory=dict)
    action_cell_by_edge_id: dict[EdgeId, ActionCellId] = field(default_factory=dict)
    dirty_collection_ids: dict[ActionCollectionId, None] = field(default_factory=dict)
    _next_collection_ordinal: int = 0
    _next_action_cell_ordinal: int = 0

    @classmethod
    def from_state_layer_and_registry(
        cls,
        *,
        tier: int,
        state_layer: StatePartitionLayer,
        registry: BaseGraphRegistry,
    ) -> ActionPartitionLayer:
        """Initialize tier-0 outgoing collections from base graph buckets."""

        layer = cls(tier_index=tier)
        for state_cell_id in state_layer.all_cell_ids():
            edge_ids: list[EdgeId] = []
            for state_id in state_layer.members(state_cell_id):
                edge_ids.extend(registry.outgoing_edge_ids(state_id))
            collection_id = layer._new_collection_id()
            layer.outgoing_collection_by_state_cell[state_cell_id] = collection_id
            layer.edge_ids_by_collection[collection_id] = {
                edge_id: None for edge_id in edge_ids
            }
            layer.dirty_collection_ids[collection_id] = None
            layer.rebuild_action_cells_for_collection(collection_id, state_layer, registry)
        return layer

    @classmethod
    def carry_forward_from(
        cls,
        previous_action_layer: ActionPartitionLayer,
        new_state_layer: StatePartitionLayer,
        tier: int,
        loop_policy: LoopPolicy,
    ) -> ActionPartitionLayer:
        """Create a new tier by carrying forward previous outgoing data.

        Previous live outgoing edges and already-internal edges are inherited
        into the new state partition. Action cells are rebuilt lazily through the
        dirty-collection mechanism.
        """

        layer = cls(tier_index=tier)
        for state_cell_id in new_state_layer.all_cell_ids():
            edge_ids: dict[EdgeId, None] = {}
            for previous_cell_id in new_state_layer.previous_cells_by_cell_id[state_cell_id]:
                previous_collection_id = previous_action_layer.outgoing_collection(
                    previous_cell_id
                )
                for edge_id in previous_action_layer.edge_ids_for_collection(
                    previous_collection_id
                ):
                    edge_ids[edge_id] = None
                for edge_id in previous_action_layer.internal_edge_ids(previous_cell_id):
                    layer.internal_edge_ids_by_state_cell.setdefault(
                        state_cell_id,
                        {},
                    )[edge_id] = None
            collection_id = layer._new_collection_id()
            layer.outgoing_collection_by_state_cell[state_cell_id] = collection_id
            layer.edge_ids_by_collection[collection_id] = edge_ids
            if state_cell_id in layer.internal_edge_ids_by_state_cell:
                layer.internal_edge_records_by_state_cell[state_cell_id] = tuple(
                    record_internal_edge(
                        edge_id=edge_id,
                        tier=tier,
                        state_cell_id=state_cell_id,
                        loop_policy=loop_policy,
                    )
                    for edge_id in layer.internal_edge_ids(state_cell_id)
                )
            layer.dirty_collection_ids[collection_id] = None
        return layer

    def outgoing_collection(self, state_cell_id: StateCellId) -> ActionCollectionId:
        """Return the outgoing-action collection attached to a state cell."""

        return self.outgoing_collection_by_state_cell[state_cell_id]

    def ensure_outgoing_collection(
        self,
        state_cell_id: StateCellId,
    ) -> ActionCollectionId:
        """Create an empty outgoing collection for a state cell if needed."""

        existing = self.outgoing_collection_by_state_cell.get(state_cell_id)
        if existing is not None:
            return existing
        collection_id = self._new_collection_id()
        self.outgoing_collection_by_state_cell[state_cell_id] = collection_id
        self.edge_ids_by_collection[collection_id] = {}
        self.dirty_collection_ids[collection_id] = None
        return collection_id

    def insert_edge_for_source_cell(
        self,
        edge_id: EdgeId,
        source_cell_id: StateCellId,
    ) -> ActionCollectionId:
        """Insert a newly discovered edge into its source-cell collection."""

        collection_id = self.ensure_outgoing_collection(source_cell_id)
        self.edge_ids_by_collection.setdefault(collection_id, {})[edge_id] = None
        self.dirty_collection_ids[collection_id] = None
        return collection_id

    def edge_ids_for_collection(
        self,
        collection_id: ActionCollectionId,
    ) -> tuple[EdgeId, ...]:
        """Return live non-internal edge ids for an outgoing collection."""

        return tuple(sorted(self.edge_ids_by_collection.get(collection_id, {})))

    def internal_edge_ids(self, state_cell_id: StateCellId) -> tuple[EdgeId, ...]:
        """Return edge ids recorded as loops internal to a state cell."""

        return tuple(sorted(self.internal_edge_ids_by_state_cell.get(state_cell_id, {})))

    def merge_collections(
        self,
        left_collection_id: ActionCollectionId,
        right_collection_id: ActionCollectionId,
        merged_state_cell_id: StateCellId,
        state_layer: StatePartitionLayer,
        registry: BaseGraphRegistry,
        loop_policy: LoopPolicy,
        lower_state_layer: StatePartitionLayer | None = None,
        lower_action_layer: ActionPartitionLayer | None = None,
    ) -> ActionCollectionMergeResult:
        """Merge outgoing collections and remove edges now internal to the cell.

        This is the action-side counterpart of state-cell coalescence. The live
        outgoing set becomes the union of predecessor outgoing sets minus edges
        whose source and target now lie in the merged state cell.
        """

        candidate_edge_ids: dict[EdgeId, None] = {}
        for edge_id in self.edge_ids_for_collection(left_collection_id):
            candidate_edge_ids[edge_id] = None
        for edge_id in self.edge_ids_for_collection(right_collection_id):
            candidate_edge_ids[edge_id] = None

        internal_edge_ids: dict[EdgeId, None] = {}
        for previous_cell_id in state_layer.previous_cells_by_cell_id.get(
            merged_state_cell_id,
            (),
        ):
            for edge_id in self.internal_edge_ids(previous_cell_id):
                internal_edge_ids[edge_id] = None

        live_edge_ids: dict[EdgeId, None] = {}
        for edge_id in candidate_edge_ids:
            source_cell = state_layer.cell_of(registry.source_state_id(edge_id))
            target_cell = state_layer.cell_of(registry.target_state_id(edge_id))
            if source_cell == merged_state_cell_id and target_cell == merged_state_cell_id:
                internal_edge_ids[edge_id] = None
            else:
                live_edge_ids[edge_id] = None

        internal_records = tuple(
            record_internal_edge(
                edge_id=edge_id,
                tier=self.tier_index,
                state_cell_id=merged_state_cell_id,
                loop_policy=loop_policy,
            )
            for edge_id in sorted(internal_edge_ids)
        )

        collection_id = self._new_collection_id()
        for obsolete_collection_id in {left_collection_id, right_collection_id}:
            self._clear_action_cells_for_collection(obsolete_collection_id)
            self.dirty_collection_ids.pop(obsolete_collection_id, None)
        self.edge_ids_by_collection[collection_id] = live_edge_ids
        self.outgoing_collection_by_state_cell[merged_state_cell_id] = collection_id
        self.internal_edge_ids_by_state_cell[merged_state_cell_id] = internal_edge_ids
        self.internal_edge_records_by_state_cell[merged_state_cell_id] = internal_records
        self.dirty_collection_ids[collection_id] = None
        self.rebuild_action_cells_for_collection(
            collection_id,
            state_layer,
            registry,
            lower_state_layer=lower_state_layer,
            lower_action_layer=lower_action_layer,
        )
        self._mark_incoming_source_collections_dirty(
            merged_state_cell_id,
            state_layer,
            registry,
        )
        return ActionCollectionMergeResult(
            action_collection_id=collection_id,
            merged_from=(left_collection_id, right_collection_id),
            internal_edges=internal_records,
        )

    def rebuild_action_cells_for_collection(
        self,
        collection_id: ActionCollectionId,
        state_layer: StatePartitionLayer,
        registry: BaseGraphRegistry,
        *,
        lower_state_layer: StatePartitionLayer | None = None,
        lower_action_layer: ActionPartitionLayer | None = None,
    ) -> tuple[ActionCellId, ...]:
        """Rebuild decision-level action cells for one dirty collection.

        Edges are grouped by source cell, target cell, and primitive action
        identity. This makes every representative state in a coset see the same
        abstract outgoing decision surface.
        """

        self._clear_action_cells_for_collection(collection_id)
        self.active_child_cells_by_collection.pop(collection_id, None)
        self.base_active_source_ids_by_collection.pop(collection_id, None)

        grouped: dict[tuple[StateCellId, StateCellId, object], dict[EdgeId, None]] = {}
        for edge_id in self.edge_ids_for_collection(collection_id):
            source_cell = state_layer.cell_of(registry.source_state_id(edge_id))
            target_cell = state_layer.cell_of(registry.target_state_id(edge_id))
            if source_cell == target_cell:
                continue
            label_key = registry.action_for_edge_id(edge_id).canonical_identity
            grouped.setdefault((source_cell, target_cell, label_key), {})[edge_id] = None

        action_cell_ids: list[ActionCellId] = []
        active_child_cells: dict[StateCellId, None] = {}
        base_active_source_ids: dict[StateId, None] = {}
        for (source_cell, target_cell, label_key), edge_ids in sorted(
            grouped.items(),
            key=lambda item: repr(item[0]),
        ):
            action_cell_id = self._new_action_cell_id()
            action_cell_ids.append(action_cell_id)
            self.edge_ids_by_action_cell[action_cell_id] = edge_ids
            self.source_cell_by_action_cell[action_cell_id] = source_cell
            self.target_cell_by_action_cell[action_cell_id] = target_cell
            self.label_key_by_action_cell[action_cell_id] = label_key
            source_child_edge_ids: dict[StateCellId, dict[EdgeId, None]] = {}
            lower_action_cells_by_source_child: dict[
                StateCellId,
                dict[ActionCellId, None],
            ] = {}
            base_source_edge_ids: dict[StateId, dict[EdgeId, None]] = {}
            for edge_id in sorted(edge_ids):
                source_state_id = registry.source_state_id(edge_id)
                source_child = (
                    lower_state_layer.cell_of(source_state_id)
                    if lower_state_layer is not None
                    else state_layer.cell_of(source_state_id)
                )
                source_child_edge_ids.setdefault(source_child, {})[edge_id] = None
                active_child_cells[source_child] = None
                base_source_edge_ids.setdefault(source_state_id, {})[edge_id] = None
                base_active_source_ids[source_state_id] = None
                self.action_cell_by_edge_id[edge_id] = action_cell_id
                if lower_action_layer is not None:
                    lower_action_cell = lower_action_layer.action_cell_for_edge_id(edge_id)
                    if lower_action_cell is not None:
                        lower_action_cells_by_source_child.setdefault(
                            source_child,
                            {},
                        )[lower_action_cell] = None
            self.source_child_cells_by_action_cell[action_cell_id] = tuple(
                sorted(source_child_edge_ids)
            )
            self.edge_ids_by_action_cell_by_source_child[action_cell_id] = {
                source_child: tuple(sorted(child_edge_ids))
                for source_child, child_edge_ids in sorted(source_child_edge_ids.items())
            }
            self.lower_action_cells_by_action_cell_by_source_child[action_cell_id] = {
                source_child: tuple(sorted(lower_action_cells))
                for source_child, lower_action_cells in sorted(
                    lower_action_cells_by_source_child.items()
                )
            }
            self.edge_ids_by_action_cell_by_base_source[action_cell_id] = {
                source_id: tuple(sorted(source_edge_ids))
                for source_id, source_edge_ids in sorted(base_source_edge_ids.items())
            }
            self.base_source_ids_by_action_cell[action_cell_id] = tuple(
                sorted(base_source_edge_ids)
            )
        self.action_cell_ids_by_collection[collection_id] = tuple(action_cell_ids)
        self.active_child_cells_by_collection[collection_id] = tuple(
            sorted(active_child_cells)
        )
        self.base_active_source_ids_by_collection[collection_id] = tuple(
            sorted(base_active_source_ids)
        )
        self.dirty_collection_ids.pop(collection_id, None)
        return tuple(action_cell_ids)

    def action_cells_for_collection(
        self,
        collection_id: ActionCollectionId,
    ) -> tuple[ActionCellId, ...]:
        """Return action-cell ids exposed by an outgoing collection."""

        return self.action_cell_ids_by_collection.get(collection_id, ())

    def edge_ids_for_action_cell(self, action_cell_id: ActionCellId) -> tuple[EdgeId, ...]:
        """Return primitive edge ids represented by an action cell."""

        return tuple(sorted(self.edge_ids_by_action_cell[action_cell_id]))

    def representative_edge_ids(self, action_cell_id: ActionCellId) -> tuple[EdgeId, ...]:
        """Return deterministic primitive representatives for an action cell."""

        return self.edge_ids_for_action_cell(action_cell_id)

    def source_child_cells(self, action_cell_id: ActionCellId) -> tuple[StateCellId, ...]:
        """Return adjacent lower-tier source cells supporting an action cell."""

        return self.source_child_cells_by_action_cell.get(action_cell_id, ())

    def edge_ids_for_source_child(
        self,
        action_cell_id: ActionCellId,
        child_state_cell_id: StateCellId,
    ) -> tuple[EdgeId, ...]:
        """Return action-cell edge ids sourced in a lower-tier child cell."""

        return self.edge_ids_by_action_cell_by_source_child.get(
            action_cell_id,
            {},
        ).get(child_state_cell_id, ())

    def lower_action_cells_for_source_child(
        self,
        action_cell_id: ActionCellId,
        child_state_cell_id: StateCellId,
    ) -> tuple[ActionCellId, ...]:
        """Return lower action cells supporting an action through a child cell."""

        return self.lower_action_cells_by_action_cell_by_source_child.get(
            action_cell_id,
            {},
        ).get(child_state_cell_id, ())

    def active_child_cells(
        self,
        collection_id: ActionCollectionId,
    ) -> tuple[StateCellId, ...]:
        """Return lower-tier child state cells supporting a collection."""

        return self.active_child_cells_by_collection.get(collection_id, ())

    def edge_ids_for_base_source(
        self,
        action_cell_id: ActionCellId,
        source_state_id: StateId,
    ) -> tuple[EdgeId, ...]:
        """Return action-cell edge ids sourced at one base state."""

        return self.edge_ids_by_action_cell_by_base_source.get(
            action_cell_id,
            {},
        ).get(source_state_id, ())

    def base_source_ids(self, action_cell_id: ActionCellId) -> tuple[StateId, ...]:
        """Return base source ids that support an action cell."""

        return self.base_source_ids_by_action_cell.get(action_cell_id, ())

    def base_active_source_ids(
        self,
        collection_id: ActionCollectionId,
    ) -> tuple[StateId, ...]:
        """Return base source ids supporting some action in a collection."""

        return self.base_active_source_ids_by_collection.get(collection_id, ())

    def action_cell_for_edge_id(self, edge_id: EdgeId) -> ActionCellId | None:
        """Return the current action cell containing an edge id, if any."""

        return self.action_cell_by_edge_id.get(edge_id)

    def _clear_action_cells_for_collection(
        self,
        collection_id: ActionCollectionId,
    ) -> None:
        for action_cell_id in self.action_cell_ids_by_collection.pop(collection_id, ()):
            for edge_id in self.edge_ids_by_action_cell.get(action_cell_id, {}):
                if self.action_cell_by_edge_id.get(edge_id) == action_cell_id:
                    self.action_cell_by_edge_id.pop(edge_id, None)
            self.edge_ids_by_action_cell.pop(action_cell_id, None)
            self.source_cell_by_action_cell.pop(action_cell_id, None)
            self.target_cell_by_action_cell.pop(action_cell_id, None)
            self.label_key_by_action_cell.pop(action_cell_id, None)
            self.source_child_cells_by_action_cell.pop(action_cell_id, None)
            self.edge_ids_by_action_cell_by_source_child.pop(action_cell_id, None)
            self.lower_action_cells_by_action_cell_by_source_child.pop(action_cell_id, None)
            self.edge_ids_by_action_cell_by_base_source.pop(action_cell_id, None)
            self.base_source_ids_by_action_cell.pop(action_cell_id, None)

    def _mark_incoming_source_collections_dirty(
        self,
        state_cell_id: StateCellId,
        state_layer: StatePartitionLayer,
        registry: BaseGraphRegistry,
    ) -> None:
        """Dirty action collections whose target partition data just changed."""

        for state_id in state_layer.members(state_cell_id):
            for edge_id in registry.incoming_edge_ids(state_id):
                source_cell = state_layer.cell_of(registry.source_state_id(edge_id))
                target_cell = state_layer.cell_of(registry.target_state_id(edge_id))
                if source_cell == target_cell:
                    continue
                source_collection = self.outgoing_collection(source_cell)
                self.dirty_collection_ids[source_collection] = None

    def _new_collection_id(self) -> ActionCollectionId:
        collection_id = ActionCollectionId(
            tier=self.tier_index,
            ordinal=self._next_collection_ordinal,
        )
        self._next_collection_ordinal += 1
        return collection_id

    def _new_action_cell_id(self) -> ActionCellId:
        action_cell_id = ActionCellId(tier=self.tier_index, ordinal=self._next_action_cell_ordinal)
        self._next_action_cell_ordinal += 1
        return action_cell_id


__all__ = [
    "ActionCollectionMergeResult",
    "ActionPartitionLayer",
]
