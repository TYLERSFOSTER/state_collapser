"""Update records for partition-tower maintenance."""

from __future__ import annotations

from dataclasses import dataclass, field

from state_collapser.tower.partition.action_layer import ActionCollectionMergeResult
from state_collapser.tower.partition.diagnostics import TowerUpdateDiagnostics
from state_collapser.tower.partition.ids import (
    ActionCellId,
    ActionCollectionId,
    EdgeId,
    StateCellId,
    StateId,
)
from state_collapser.tower.partition.loop_policy import InternalEdgeRecord
from state_collapser.tower.partition.schema import SchemaAssignment
from state_collapser.tower.partition.state_layer import StateCellMergeResult


@dataclass(frozen=True, slots=True)
class StateCellMergeRecord:
    """Tower-level record of one state-cell merge."""

    tier: int
    result: StateCellMergeResult


@dataclass(frozen=True, slots=True)
class ActionCollectionMergeRecord:
    """Tower-level record of one action-collection merge."""

    tier: int
    result: ActionCollectionMergeResult


@dataclass(frozen=True, slots=True)
class TowerMorphism:
    """Cell-image data for an update from an old tower state to a new one."""

    state_cell_image_by_tier: dict[int, dict[StateCellId, StateCellId]] = field(
        default_factory=dict
    )
    action_collection_image_by_tier: dict[
        int,
        dict[ActionCollectionId, ActionCollectionId],
    ] = field(default_factory=dict)
    action_cell_image_by_tier: dict[int, dict[ActionCellId, ActionCellId]] = field(
        default_factory=dict
    )
    unchanged_tiers: tuple[int, ...] = ()
    created_tiers: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class TowerUpdateResult:
    """Result of one partition-tower initialization or update."""

    changed: bool
    delta_state_ids: tuple[StateId, ...] = ()
    delta_edge_ids: tuple[EdgeId, ...] = ()
    schema_assignments: tuple[SchemaAssignment, ...] = ()
    affected_tiers: tuple[int, ...] = ()
    state_merges: tuple[StateCellMergeRecord, ...] = ()
    action_merges: tuple[ActionCollectionMergeRecord, ...] = ()
    internal_edges: tuple[InternalEdgeRecord, ...] = ()
    current_position_by_tier: tuple[StateCellId | None, ...] = ()
    morphism: TowerMorphism = field(default_factory=TowerMorphism)
    diagnostics: TowerUpdateDiagnostics = field(default_factory=TowerUpdateDiagnostics)


__all__ = [
    "ActionCollectionMergeRecord",
    "StateCellMergeRecord",
    "TowerMorphism",
    "TowerUpdateDiagnostics",
    "TowerUpdateResult",
]
