"""Persistent nested state/action partition tower."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.action_layer import ActionPartitionLayer
from state_collapser.tower.partition.base_registry import BaseGraphRegistry
from state_collapser.tower.partition.diagnostics import TowerUpdateDiagnostics
from state_collapser.tower.partition.ids import (
    ActionCellId,
    ActionCollectionId,
    EdgeId,
    SchemaBlockId,
    StateCellId,
    StateId,
)
from state_collapser.tower.partition.internal_aggregation import InternalEdgeAggregator
from state_collapser.tower.partition.loop_policy import InternalEdgeRecord, LoopPolicy
from state_collapser.tower.partition.reward_aggregation import RewardAggregator
from state_collapser.tower.partition.schema import (
    ContractionSchema,
    NoContractionSchema,
    SchemaAssignmentStore,
)
from state_collapser.tower.partition.state_layer import StatePartitionLayer
from state_collapser.tower.partition.update import (
    ActionCollectionMergeRecord,
    StateCellMergeRecord,
    TowerMorphism,
    TowerUpdateResult,
)

if TYPE_CHECKING:
    from state_collapser.quotient.tier_view import QuotientTierView


@dataclass(slots=True)
class PartitionTower:
    """Persistent nested state/action partition tower."""

    schema: ContractionSchema = field(default_factory=NoContractionSchema)
    loop_policy: LoopPolicy = field(default_factory=LoopPolicy.drop_internal)
    reward_aggregator: RewardAggregator = field(default_factory=RewardAggregator)
    internal_edge_aggregator: InternalEdgeAggregator = field(
        default_factory=InternalEdgeAggregator.sum
    )
    registry: BaseGraphRegistry = field(default_factory=BaseGraphRegistry)
    schema_assignment_store: SchemaAssignmentStore = field(init=False)
    state_layers: list[StatePartitionLayer] = field(default_factory=list)
    action_layers: list[ActionPartitionLayer] = field(default_factory=list)
    last_update_result: TowerUpdateResult | None = None

    def __post_init__(self) -> None:
        self.schema_assignment_store = SchemaAssignmentStore(self.schema)

    def initialize(
        self,
        *,
        initial_states: Iterable[State],
        initial_edges: Iterable[BaseEdge],
        current_state: State | None,
    ) -> TowerUpdateResult:
        """Initialize the tower from discovered base graph data."""

        delta = self.registry.register_delta(initial_states, initial_edges)
        assignments = self.schema_assignment_store.assign_edges(
            delta.new_edge_ids,
            self.registry,
        )
        state_layer = StatePartitionLayer.singleton_layer(
            tier=0,
            state_ids=self.registry.state_ids,
        )
        action_layer = ActionPartitionLayer.from_state_layer_and_registry(
            tier=0,
            state_layer=state_layer,
            registry=self.registry,
        )
        self.state_layers = [state_layer]
        self.action_layers = [action_layer]

        state_merges: list[StateCellMergeRecord] = []
        action_merges: list[ActionCollectionMergeRecord] = []
        internal_edges: list[InternalEdgeRecord] = []
        affected_tiers: list[int] = [0]

        for tier, block_id in enumerate(self._effective_ordered_blocks(), start=1):
            previous_state_layer = self.state_layers[-1]
            previous_action_layer = self.action_layers[-1]
            current_state_layer = StatePartitionLayer.carry_forward_from(
                previous_state_layer,
                tier=tier,
            )
            current_action_layer = ActionPartitionLayer.carry_forward_from(
                previous_action_layer,
                current_state_layer,
                tier=tier,
                loop_policy=self.loop_policy,
            )

            for edge_id in self.schema_assignment_store.edges_in_block(block_id):
                self._contract_edge_in_layer(
                    edge_id=edge_id,
                    tier=tier,
                    state_layer=current_state_layer,
                    action_layer=current_action_layer,
                    state_merges=state_merges,
                    action_merges=action_merges,
                    internal_edges=internal_edges,
                )

            self._rebuild_dirty_action_cells(current_state_layer, current_action_layer)
            self.state_layers.append(current_state_layer)
            self.action_layers.append(current_action_layer)
            affected_tiers.append(tier)

        result = TowerUpdateResult(
            changed=bool(delta.new_state_ids or delta.new_edge_ids or state_merges),
            delta_state_ids=delta.new_state_ids,
            delta_edge_ids=delta.new_edge_ids,
            schema_assignments=assignments,
            affected_tiers=tuple(affected_tiers),
            state_merges=tuple(state_merges),
            action_merges=tuple(action_merges),
            internal_edges=tuple(internal_edges),
            current_position_by_tier=self.current_position_at_every_tier(current_state),
            morphism=TowerMorphism(created_tiers=tuple(affected_tiers)),
            diagnostics=TowerUpdateDiagnostics(
                discovered_state_count=len(self.registry.state_ids),
                discovered_edge_count=len(self.registry.edge_ids),
                delta_state_count=len(delta.new_state_ids),
                delta_edge_count=len(delta.new_edge_ids),
                schema_assignment_count=len(assignments),
                state_cell_merge_count=len(state_merges),
                action_collection_merge_count=len(action_merges),
                internal_edge_count=len(internal_edges),
                dirty_collection_count=sum(
                    len(layer.dirty_collection_ids) for layer in self.action_layers
                ),
                internal_aggregation_name=self.internal_edge_aggregator.name.value,
            ),
        )
        self.last_update_result = result
        return result

    def current_state_cell(self, tier: int, state: State) -> StateCellId | None:
        """Return the state cell containing a base state at a tier."""

        if tier < 0 or tier >= len(self.state_layers):
            return None
        state_id = self.registry.state_id_by_state.get(state)
        if state_id is None:
            return None
        return self.state_layers[tier].cell_of(state_id)

    def current_position_at_every_tier(
        self,
        current_state: State | None,
    ) -> tuple[StateCellId | None, ...]:
        """Return the current state-cell position at every tier."""

        if current_state is None:
            return tuple(None for _ in self.state_layers)
        return tuple(
            self.current_state_cell(tier, current_state)
            for tier in range(len(self.state_layers))
        )

    def state_cell_members(
        self,
        tier: int,
        state_cell_id: StateCellId,
    ) -> tuple[State, ...]:
        """Return base states contained in a state cell."""

        if tier < 0 or tier >= len(self.state_layers):
            return ()
        state_layer = self.state_layers[tier]
        return tuple(
            self.registry.state_for_id(state_id)
            for state_id in state_layer.members(state_cell_id)
        )

    def outgoing_action_cells(
        self,
        tier: int,
        state_cell_id: StateCellId,
    ) -> tuple[ActionCellId, ...]:
        """Return decision-level action cells available from a state cell."""

        if tier < 0 or tier >= len(self.action_layers):
            return ()
        action_layer = self.action_layers[tier]
        collection_id = action_layer.outgoing_collection(state_cell_id)
        return action_layer.action_cells_for_collection(collection_id)

    def action_cell_members(
        self,
        tier: int,
        action_cell_id: ActionCellId,
    ) -> tuple[BaseEdge, ...]:
        """Return base edges represented by a decision-level action cell."""

        if tier < 0 or tier >= len(self.action_layers):
            return ()
        action_layer = self.action_layers[tier]
        return tuple(
            self.registry.edge_for_id(edge_id)
            for edge_id in action_layer.edge_ids_for_action_cell(action_cell_id)
        )

    def action_cell_for_edge(
        self,
        tier: int,
        edge: BaseEdge,
    ) -> ActionCellId | None:
        """Return the action cell containing a concrete edge at a tier."""

        if tier < 0 or tier >= len(self.action_layers):
            return None
        edge_id = self.registry.edge_id_by_edge.get(edge)
        if edge_id is None:
            return None
        action_layer = self.action_layers[tier]
        for action_cell_id in sorted(action_layer.edge_ids_by_action_cell):
            if edge_id in action_layer.edge_ids_by_action_cell[action_cell_id]:
                return action_cell_id
        return None

    def representative_edges(
        self,
        tier: int,
        action_cell_id: ActionCellId,
    ) -> tuple[BaseEdge, ...]:
        """Return deterministic representative base edges for an action cell."""

        if tier < 0 or tier >= len(self.action_layers):
            return ()
        action_layer = self.action_layers[tier]
        return tuple(
            self.registry.edge_for_id(edge_id)
            for edge_id in action_layer.representative_edge_ids(action_cell_id)
        )

    def internal_edges(
        self,
        tier: int,
        state_cell_id: StateCellId,
    ) -> tuple[BaseEdge, ...]:
        """Return base edges that are internal to a state cell at a tier."""

        if tier < 0 or tier >= len(self.action_layers):
            return ()
        action_layer = self.action_layers[tier]
        return tuple(
            self.registry.edge_for_id(edge_id)
            for edge_id in action_layer.internal_edge_ids(state_cell_id)
        )

    def lift_candidates(
        self,
        tier: int,
        action_cell_id: ActionCellId,
        current_base_state: State,
    ) -> tuple[BaseEdge, ...]:
        """Return primitive edges that can realize an abstract action cell."""

        representatives = self.representative_edges(tier, action_cell_id)
        directly_executable = tuple(
            edge for edge in representatives if edge.source == current_base_state
        )
        return directly_executable if directly_executable else representatives

    def refinement_fiber(
        self,
        tier: int,
        cell_id: StateCellId | ActionCollectionId | ActionCellId,
    ) -> tuple[StateCellId | ActionCollectionId | ActionCellId, ...]:
        """Return adjacent lower-tier cells refining a tier cell when available."""

        if tier <= 0:
            return ()
        if isinstance(cell_id, StateCellId):
            return self._state_cell_refinement_fiber(tier, cell_id)
        if isinstance(cell_id, ActionCollectionId):
            return self._action_collection_refinement_fiber(tier, cell_id)
        if isinstance(cell_id, ActionCellId):
            return self._action_cell_refinement_fiber(tier, cell_id)
        return ()

    def update_with_delta(
        self,
        *,
        delta_states: Iterable[State],
        delta_edges: Iterable[BaseEdge],
        current_state: State | None,
        build_morphism: bool = False,
    ) -> TowerUpdateResult:
        """Incrementally update the tower with newly discovered graph data."""

        morphism_domain = self._capture_morphism_domain() if build_morphism else None
        delta = self.registry.register_delta(delta_states, delta_edges)
        assignments = self.schema_assignment_store.assign_edges(
            delta.new_edge_ids,
            self.registry,
        )
        for state_id in delta.new_state_ids:
            self._add_state_to_existing_layers(state_id)

        internal_edges: list[InternalEdgeRecord] = []
        affected_tiers: dict[int, None] = {}
        self._insert_delta_edges_into_existing_layers(
            delta.new_edge_ids,
            internal_edges,
            affected_tiers,
        )

        state_merges: list[StateCellMergeRecord] = []
        action_merges: list[ActionCollectionMergeRecord] = []
        ordered_blocks = self._effective_ordered_blocks()
        block_tier_by_id = {block_id: tier for tier, block_id in enumerate(ordered_blocks, start=1)}
        for assignment in assignments:
            if assignment.block_id is None:
                continue
            tier = block_tier_by_id[assignment.block_id]
            self._ensure_tier_exists(tier)
            self._contract_edge_from_tier_downward(
                edge_id=assignment.edge_id,
                start_tier=tier,
                state_merges=state_merges,
                action_merges=action_merges,
                internal_edges=internal_edges,
                affected_tiers=affected_tiers,
            )

        for tier_index in tuple(affected_tiers):
            if 0 <= tier_index < len(self.action_layers):
                self._rebuild_dirty_action_cells(
                    self.state_layers[tier_index],
                    self.action_layers[tier_index],
                )

        changed = bool(delta.new_state_ids or delta.new_edge_ids or state_merges)
        morphism = (
            self._build_morphism_from_domain(
                morphism_domain,
                unchanged_tiers=tuple(range(len(self.state_layers))) if not changed else (),
                created_tiers=(),
            )
            if morphism_domain is not None
            else TowerMorphism()
        )
        result = TowerUpdateResult(
            changed=changed,
            delta_state_ids=delta.new_state_ids,
            delta_edge_ids=delta.new_edge_ids,
            schema_assignments=assignments,
            affected_tiers=tuple(sorted(affected_tiers)),
            state_merges=tuple(state_merges),
            action_merges=tuple(action_merges),
            internal_edges=tuple(internal_edges),
            current_position_by_tier=self.current_position_at_every_tier(current_state),
            morphism=morphism,
            diagnostics=TowerUpdateDiagnostics(
                discovered_state_count=len(self.registry.state_ids),
                discovered_edge_count=len(self.registry.edge_ids),
                delta_state_count=len(delta.new_state_ids),
                delta_edge_count=len(delta.new_edge_ids),
                schema_assignment_count=len(assignments),
                state_cell_merge_count=len(state_merges),
                action_collection_merge_count=len(action_merges),
                internal_edge_count=len(internal_edges),
                dirty_collection_count=sum(
                    len(layer.dirty_collection_ids) for layer in self.action_layers
                ),
                internal_aggregation_name=self.internal_edge_aggregator.name.value,
            ),
        )
        self.last_update_result = result
        return result

    def build_full(
        self,
        *,
        states: Iterable[State],
        edges: Iterable[BaseEdge],
        current_state: State | None,
    ) -> TowerUpdateResult:
        """Build a full partition tower using the initialization semantics."""

        return self.initialize(
            initial_states=states,
            initial_edges=edges,
            current_state=current_state,
        )

    def to_quotient_tier_views(self) -> tuple[QuotientTierView, ...]:
        """Return compatibility quotient-tier views."""

        from state_collapser.tower.partition.readout import to_quotient_tier_views

        return to_quotient_tier_views(self)

    def _effective_ordered_blocks(self) -> tuple[SchemaBlockId, ...]:
        ordered: dict[SchemaBlockId, None] = {}
        for block_id in self.schema_assignment_store.ordered_blocks():
            ordered.setdefault(block_id, None)
        for block_id in sorted(self.schema_assignment_store.edge_ids_by_block, key=repr):
            ordered.setdefault(block_id, None)
        return tuple(ordered.keys())

    def _state_cell_refinement_fiber(
        self,
        tier: int,
        state_cell_id: StateCellId,
    ) -> tuple[StateCellId, ...]:
        state_layer = self.state_layers[tier]
        previous_state_layer = self.state_layers[tier - 1]
        member_ids = set(state_layer.members(state_cell_id))
        return tuple(
            previous_cell_id
            for previous_cell_id in previous_state_layer.all_cell_ids()
            if set(previous_state_layer.members(previous_cell_id)).issubset(member_ids)
        )

    def _action_collection_refinement_fiber(
        self,
        tier: int,
        action_collection_id: ActionCollectionId,
    ) -> tuple[ActionCollectionId, ...]:
        state_cell_id = self._active_state_cell_for_collection(tier, action_collection_id)
        if state_cell_id is None:
            return ()
        previous_state_cells = self._state_cell_refinement_fiber(tier, state_cell_id)
        previous_action_layer = self.action_layers[tier - 1]
        return tuple(
            previous_action_layer.outgoing_collection(previous_state_cell)
            for previous_state_cell in previous_state_cells
        )

    def _action_cell_refinement_fiber(
        self,
        tier: int,
        action_cell_id: ActionCellId,
    ) -> tuple[ActionCellId, ...]:
        current_action_layer = self.action_layers[tier]
        previous_action_layer = self.action_layers[tier - 1]
        edge_ids = set(current_action_layer.edge_ids_for_action_cell(action_cell_id))
        previous_action_cells: list[ActionCellId] = []
        for previous_state_cell in self.state_layers[tier - 1].all_cell_ids():
            previous_collection = previous_action_layer.outgoing_collection(
                previous_state_cell
            )
            for previous_action_cell in previous_action_layer.action_cells_for_collection(
                previous_collection
            ):
                previous_edge_ids = set(
                    previous_action_layer.edge_ids_for_action_cell(previous_action_cell)
                )
                if edge_ids.intersection(previous_edge_ids):
                    previous_action_cells.append(previous_action_cell)
        return tuple(previous_action_cells)

    def _active_state_cell_for_collection(
        self,
        tier: int,
        action_collection_id: ActionCollectionId,
    ) -> StateCellId | None:
        state_layer = self.state_layers[tier]
        action_layer = self.action_layers[tier]
        for state_cell_id in state_layer.all_cell_ids():
            if action_layer.outgoing_collection(state_cell_id) == action_collection_id:
                return state_cell_id
        return None

    def _capture_morphism_domain(
        self,
    ) -> dict[int, tuple[
        dict[StateCellId, tuple[StateId, ...]],
        dict[StateCellId, ActionCollectionId],
        dict[StateCellId, tuple[ActionCellId, ...]],
        dict[ActionCellId, tuple[EdgeId, ...]],
    ]]:
        """Capture active cells before an update mutates partition layers."""

        domain = {}
        for tier, state_layer in enumerate(self.state_layers):
            action_layer = self.action_layers[tier]
            state_members_by_cell: dict[StateCellId, tuple[StateId, ...]] = {}
            collection_by_state_cell: dict[StateCellId, ActionCollectionId] = {}
            action_cells_by_state_cell: dict[StateCellId, tuple[ActionCellId, ...]] = {}
            edge_ids_by_action_cell: dict[ActionCellId, tuple[EdgeId, ...]] = {}
            for state_cell_id in state_layer.all_cell_ids():
                state_members_by_cell[state_cell_id] = state_layer.members(state_cell_id)
                collection_id = action_layer.outgoing_collection(state_cell_id)
                collection_by_state_cell[state_cell_id] = collection_id
                action_cell_ids = action_layer.action_cells_for_collection(collection_id)
                action_cells_by_state_cell[state_cell_id] = action_cell_ids
                for action_cell_id in action_cell_ids:
                    edge_ids_by_action_cell[action_cell_id] = (
                        action_layer.edge_ids_for_action_cell(action_cell_id)
                    )
            domain[tier] = (
                state_members_by_cell,
                collection_by_state_cell,
                action_cells_by_state_cell,
                edge_ids_by_action_cell,
            )
        return domain

    def _build_morphism_from_domain(
        self,
        domain: dict[int, tuple[
            dict[StateCellId, tuple[StateId, ...]],
            dict[StateCellId, ActionCollectionId],
            dict[StateCellId, tuple[ActionCellId, ...]],
            dict[ActionCellId, tuple[EdgeId, ...]],
        ]],
        *,
        unchanged_tiers: tuple[int, ...],
        created_tiers: tuple[int, ...],
    ) -> TowerMorphism:
        """Build explicit old-cell image maps after an update."""

        state_cell_image_by_tier: dict[int, dict[StateCellId, StateCellId]] = {}
        action_collection_image_by_tier: dict[
            int,
            dict[ActionCollectionId, ActionCollectionId],
        ] = {}
        action_cell_image_by_tier: dict[int, dict[ActionCellId, ActionCellId]] = {}

        for tier, (
            state_members_by_cell,
            collection_by_state_cell,
            action_cells_by_state_cell,
            edge_ids_by_action_cell,
        ) in domain.items():
            if tier >= len(self.state_layers):
                continue
            state_layer = self.state_layers[tier]
            action_layer = self.action_layers[tier]
            state_images: dict[StateCellId, StateCellId] = {}
            collection_images: dict[ActionCollectionId, ActionCollectionId] = {}
            action_cell_images: dict[ActionCellId, ActionCellId] = {}

            for old_state_cell_id, state_ids in state_members_by_cell.items():
                if not state_ids:
                    continue
                new_state_cell_id = state_layer.cell_of(state_ids[0])
                state_images[old_state_cell_id] = new_state_cell_id
                old_collection_id = collection_by_state_cell[old_state_cell_id]
                new_collection_id = action_layer.outgoing_collection(new_state_cell_id)
                collection_images[old_collection_id] = new_collection_id

                new_action_cell_ids = action_layer.action_cells_for_collection(
                    new_collection_id
                )
                new_action_cells_by_edge: dict[EdgeId, ActionCellId] = {}
                for new_action_cell_id in new_action_cell_ids:
                    for edge_id in action_layer.edge_ids_for_action_cell(
                        new_action_cell_id
                    ):
                        new_action_cells_by_edge[edge_id] = new_action_cell_id
                for old_action_cell_id in action_cells_by_state_cell[old_state_cell_id]:
                    for edge_id in edge_ids_by_action_cell[old_action_cell_id]:
                        mapped_action_cell_id = new_action_cells_by_edge.get(edge_id)
                        if mapped_action_cell_id is not None:
                            action_cell_images[old_action_cell_id] = mapped_action_cell_id
                            break

            state_cell_image_by_tier[tier] = state_images
            action_collection_image_by_tier[tier] = collection_images
            action_cell_image_by_tier[tier] = action_cell_images

        return TowerMorphism(
            state_cell_image_by_tier=state_cell_image_by_tier,
            action_collection_image_by_tier=action_collection_image_by_tier,
            action_cell_image_by_tier=action_cell_image_by_tier,
            unchanged_tiers=unchanged_tiers,
            created_tiers=created_tiers,
        )

    def _add_state_to_existing_layers(self, state_id: StateId) -> None:
        for tier_index, state_layer in enumerate(self.state_layers):
            cell_id = state_layer.add_singleton_state(state_id)
            self.action_layers[tier_index].ensure_outgoing_collection(cell_id)

    def _insert_delta_edges_into_existing_layers(
        self,
        edge_ids: tuple[EdgeId, ...],
        internal_edges: list[InternalEdgeRecord],
        affected_tiers: dict[int, None],
    ) -> None:
        for tier_index, state_layer in enumerate(self.state_layers):
            action_layer = self.action_layers[tier_index]
            for edge_id in edge_ids:
                source_cell = state_layer.cell_of(self.registry.source_state_id(edge_id))
                target_cell = state_layer.cell_of(self.registry.target_state_id(edge_id))
                if source_cell == target_cell:
                    record = InternalEdgeRecord(
                        edge_id=edge_id,
                        tier=tier_index,
                        state_cell_id=source_cell,
                        policy_name=self.loop_policy.name,
                    )
                    internal_edges.append(record)
                    action_layer.internal_edge_ids_by_state_cell.setdefault(
                        source_cell,
                        {},
                    )[edge_id] = None
                    continue
                action_layer.insert_edge_for_source_cell(edge_id, source_cell)
                affected_tiers[tier_index] = None

    def _ensure_tier_exists(self, tier: int) -> None:
        while len(self.state_layers) <= tier:
            new_tier = len(self.state_layers)
            state_layer = StatePartitionLayer.carry_forward_from(
                self.state_layers[-1],
                tier=new_tier,
            )
            action_layer = ActionPartitionLayer.carry_forward_from(
                self.action_layers[-1],
                state_layer,
                tier=new_tier,
                loop_policy=self.loop_policy,
            )
            self._rebuild_dirty_action_cells(state_layer, action_layer)
            self.state_layers.append(state_layer)
            self.action_layers.append(action_layer)

    def _contract_edge_from_tier_downward(
        self,
        *,
        edge_id: EdgeId,
        start_tier: int,
        state_merges: list[StateCellMergeRecord],
        action_merges: list[ActionCollectionMergeRecord],
        internal_edges: list[InternalEdgeRecord],
        affected_tiers: dict[int, None],
    ) -> None:
        for tier in range(start_tier, len(self.state_layers)):
            before_state_merges = len(state_merges)
            before_action_merges = len(action_merges)
            self._contract_edge_in_layer(
                edge_id=edge_id,
                tier=tier,
                state_layer=self.state_layers[tier],
                action_layer=self.action_layers[tier],
                state_merges=state_merges,
                action_merges=action_merges,
                internal_edges=internal_edges,
            )
            state_changed = len(state_merges) != before_state_merges
            action_changed = len(action_merges) != before_action_merges
            if state_changed or action_changed:
                affected_tiers[tier] = None

    def _contract_edge_in_layer(
        self,
        *,
        edge_id: EdgeId,
        tier: int,
        state_layer: StatePartitionLayer,
        action_layer: ActionPartitionLayer,
        state_merges: list[StateCellMergeRecord],
        action_merges: list[ActionCollectionMergeRecord],
        internal_edges: list[InternalEdgeRecord],
    ) -> None:
        source_cell = state_layer.cell_of(self.registry.source_state_id(edge_id))
        target_cell = state_layer.cell_of(self.registry.target_state_id(edge_id))
        if source_cell == target_cell:
            return

        source_collection = action_layer.outgoing_collection(source_cell)
        target_collection = action_layer.outgoing_collection(target_cell)
        state_merge = state_layer.merge_cells(source_cell, target_cell)
        if not state_merge.changed:
            return
        action_merge = action_layer.merge_collections(
            source_collection,
            target_collection,
            state_merge.state_cell_id,
            state_layer,
            self.registry,
            self.loop_policy,
        )
        state_merges.append(StateCellMergeRecord(tier=tier, result=state_merge))
        action_merges.append(ActionCollectionMergeRecord(tier=tier, result=action_merge))
        internal_edges.extend(action_merge.internal_edges)

    def _rebuild_dirty_action_cells(
        self,
        state_layer: StatePartitionLayer,
        action_layer: ActionPartitionLayer,
    ) -> None:
        for collection_id in tuple(action_layer.dirty_collection_ids):
            action_layer.rebuild_action_cells_for_collection(
                collection_id,
                state_layer,
                self.registry,
            )


def build_partition_tower_full(
    *,
    states: Iterable[State],
    edges: Iterable[BaseEdge],
    current_state: State | None,
    schema: ContractionSchema | None = None,
    loop_policy: LoopPolicy | None = None,
    reward_aggregator: RewardAggregator | None = None,
) -> PartitionTower:
    """Build a full partition tower from complete discovered graph data."""

    tower = PartitionTower(
        schema=NoContractionSchema() if schema is None else schema,
        loop_policy=LoopPolicy.drop_internal() if loop_policy is None else loop_policy,
        reward_aggregator=RewardAggregator()
        if reward_aggregator is None
        else reward_aggregator,
    )
    tower.initialize(initial_states=states, initial_edges=edges, current_state=current_state)
    return tower


__all__ = [
    "PartitionTower",
    "build_partition_tower_full",
]
