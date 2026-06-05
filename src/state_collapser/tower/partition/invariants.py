"""Invariant checks for partition-tower state/action support tables."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from state_collapser.tower.partition.ids import (
    ActionCellId,
    ActionCollectionId,
    EdgeId,
    StateCellId,
    StateId,
)

if TYPE_CHECKING:
    from state_collapser.tower.partition.action_layer import ActionPartitionLayer
    from state_collapser.tower.partition.base_registry import BaseGraphRegistry
    from state_collapser.tower.partition.state_layer import StatePartitionLayer


@dataclass(frozen=True, slots=True)
class PartitionInvariantIssue:
    """One structural inconsistency in a partition layer."""

    tier: int
    code: str
    message: str
    state_cell_id: StateCellId | None = None
    action_collection_id: ActionCollectionId | None = None
    action_cell_id: ActionCellId | None = None
    edge_id: EdgeId | None = None


@dataclass(frozen=True, slots=True)
class PartitionInvariantReport:
    """Debug/test report for partition-layer consistency checks."""

    issues: tuple[PartitionInvariantIssue, ...]

    @property
    def ok(self) -> bool:
        """Return whether no invariant issues were found."""

        return not self.issues

    def assert_ok(self) -> None:
        """Raise if the report contains any invariant issue."""

        if self.ok:
            return
        first_issue = self.issues[0]
        raise AssertionError(
            f"{len(self.issues)} partition invariant issue(s); "
            f"first={first_issue.code}: {first_issue.message}"
        )

    @classmethod
    def combine(
        cls,
        reports: tuple[PartitionInvariantReport, ...],
    ) -> PartitionInvariantReport:
        """Merge tier reports into one report."""

        return cls(
            issues=tuple(
                issue for report in reports for issue in report.issues
            )
        )


def action_layer_invariant_report(
    action_layer: ActionPartitionLayer,
    *,
    state_layer: StatePartitionLayer,
    registry: BaseGraphRegistry,
    lower_state_layer: StatePartitionLayer | None = None,
    lower_action_layer: ActionPartitionLayer | None = None,
    allow_dirty: bool = False,
) -> PartitionInvariantReport:
    """Return consistency issues for one action layer."""

    issues: list[PartitionInvariantIssue] = []
    live_collections_by_state = _live_collections_by_state(action_layer, state_layer)
    live_collections = set(live_collections_by_state)

    _validate_state_collections(
        action_layer,
        state_layer,
        live_collections_by_state,
        live_collections,
        issues,
    )
    _validate_dirty_collections(action_layer, allow_dirty, issues)
    _validate_collection_action_cells(action_layer, live_collections, issues)
    _validate_action_cells(
        action_layer,
        state_layer,
        registry,
        lower_state_layer,
        lower_action_layer,
        live_collections,
        issues,
    )
    _validate_collection_support_unions(action_layer, live_collections, issues)
    _validate_internal_edges(action_layer, state_layer, registry, issues)
    return PartitionInvariantReport(issues=tuple(issues))


def _live_collections_by_state(
    action_layer: ActionPartitionLayer,
    state_layer: StatePartitionLayer,
) -> dict[ActionCollectionId, StateCellId]:
    return {
        action_layer.outgoing_collection_by_state_cell[state_cell_id]: state_cell_id
        for state_cell_id in state_layer.all_cell_ids()
        if state_cell_id in action_layer.outgoing_collection_by_state_cell
    }


def _issue(
    issues: list[PartitionInvariantIssue],
    action_layer: ActionPartitionLayer,
    code: str,
    message: str,
    *,
    state_cell_id: StateCellId | None = None,
    action_collection_id: ActionCollectionId | None = None,
    action_cell_id: ActionCellId | None = None,
    edge_id: EdgeId | None = None,
) -> None:
    issues.append(
        PartitionInvariantIssue(
            tier=action_layer.tier_index,
            code=code,
            message=message,
            state_cell_id=state_cell_id,
            action_collection_id=action_collection_id,
            action_cell_id=action_cell_id,
            edge_id=edge_id,
        )
    )


def _validate_state_collections(
    action_layer: ActionPartitionLayer,
    state_layer: StatePartitionLayer,
    live_collections_by_state: dict[ActionCollectionId, StateCellId],
    live_collections: set[ActionCollectionId],
    issues: list[PartitionInvariantIssue],
) -> None:
    for state_cell_id in state_layer.all_cell_ids():
        collection_id = action_layer.outgoing_collection_by_state_cell.get(state_cell_id)
        if collection_id is None:
            _issue(
                issues,
                action_layer,
                "missing_state_collection",
                "State cell has no outgoing action collection.",
                state_cell_id=state_cell_id,
            )
            continue
        if collection_id not in action_layer.edge_ids_by_collection:
            _issue(
                issues,
                action_layer,
                "missing_collection_edges",
                "State cell points to an unknown action collection.",
                state_cell_id=state_cell_id,
                action_collection_id=collection_id,
            )

    for collection_id in action_layer.edge_ids_by_collection:
        if collection_id not in live_collections:
            if (
                action_layer.action_cells_for_collection(collection_id)
                or collection_id in action_layer.dirty_collection_ids
            ):
                _issue(
                    issues,
                    action_layer,
                    "unattached_live_collection",
                    "Unattached historical collection still exposes live action data.",
                    action_collection_id=collection_id,
                )

    for collection_id, state_cell_id in live_collections_by_state.items():
        if collection_id.tier != action_layer.tier_index:
            _issue(
                issues,
                action_layer,
                "collection_tier_mismatch",
                "Action collection tier does not match action layer tier.",
                state_cell_id=state_cell_id,
                action_collection_id=collection_id,
            )


def _validate_dirty_collections(
    action_layer: ActionPartitionLayer,
    allow_dirty: bool,
    issues: list[PartitionInvariantIssue],
) -> None:
    if allow_dirty:
        return
    for collection_id in action_layer.dirty_collection_ids:
        _issue(
            issues,
            action_layer,
            "dirty_collection",
            "Dirty action collection remains after expected rebuild.",
            action_collection_id=collection_id,
        )


def _validate_collection_action_cells(
    action_layer: ActionPartitionLayer,
    live_collections: set[ActionCollectionId],
    issues: list[PartitionInvariantIssue],
) -> None:
    live_action_cells: set[ActionCellId] = set()
    for collection_id in live_collections:
        for action_cell_id in action_layer.action_cells_for_collection(collection_id):
            live_action_cells.add(action_cell_id)
            if action_cell_id not in action_layer.edge_ids_by_action_cell:
                _issue(
                    issues,
                    action_layer,
                    "missing_action_cell_edges",
                    "Collection lists an action cell with no edge table.",
                    action_collection_id=collection_id,
                    action_cell_id=action_cell_id,
                )
            if action_cell_id not in action_layer.source_cell_by_action_cell:
                _issue(
                    issues,
                    action_layer,
                    "missing_action_cell_source",
                    "Action cell has no recorded source state cell.",
                    action_collection_id=collection_id,
                    action_cell_id=action_cell_id,
                )
            if action_cell_id not in action_layer.target_cell_by_action_cell:
                _issue(
                    issues,
                    action_layer,
                    "missing_action_cell_target",
                    "Action cell has no recorded target state cell.",
                    action_collection_id=collection_id,
                    action_cell_id=action_cell_id,
                )
            if action_cell_id not in action_layer.label_key_by_action_cell:
                _issue(
                    issues,
                    action_layer,
                    "missing_action_cell_label",
                    "Action cell has no recorded label key.",
                    action_collection_id=collection_id,
                    action_cell_id=action_cell_id,
                )

    for action_cell_id in action_layer.edge_ids_by_action_cell:
        if action_cell_id not in live_action_cells:
            _issue(
                issues,
                action_layer,
                "unlisted_action_cell",
                "Action cell edge table is not listed by any live collection.",
                action_cell_id=action_cell_id,
            )


def _validate_action_cells(
    action_layer: ActionPartitionLayer,
    state_layer: StatePartitionLayer,
    registry: BaseGraphRegistry,
    lower_state_layer: StatePartitionLayer | None,
    lower_action_layer: ActionPartitionLayer | None,
    live_collections: set[ActionCollectionId],
    issues: list[PartitionInvariantIssue],
) -> None:
    live_action_cells = {
        action_cell_id
        for collection_id in live_collections
        for action_cell_id in action_layer.action_cells_for_collection(collection_id)
    }
    internal_edge_ids = {
        edge_id
        for edge_ids in action_layer.internal_edge_ids_by_state_cell.values()
        for edge_id in edge_ids
    }
    for action_cell_id in live_action_cells:
        source_cell = action_layer.source_cell_by_action_cell.get(action_cell_id)
        target_cell = action_layer.target_cell_by_action_cell.get(action_cell_id)
        edge_ids = tuple(sorted(action_layer.edge_ids_by_action_cell.get(action_cell_id, {})))
        expected_source_child_edges: dict[StateCellId, list[EdgeId]] = {}
        expected_lower_action_cells: dict[StateCellId, set[ActionCellId]] = {}
        expected_base_source_edges: dict[StateId, list[EdgeId]] = {}

        for edge_id in edge_ids:
            if edge_id in internal_edge_ids:
                _issue(
                    issues,
                    action_layer,
                    "internal_edge_in_live_action_cell",
                    "Internal edge appears in a live action cell.",
                    action_cell_id=action_cell_id,
                    edge_id=edge_id,
                )
            reverse_action_cell = action_layer.action_cell_by_edge_id.get(edge_id)
            if reverse_action_cell != action_cell_id:
                _issue(
                    issues,
                    action_layer,
                    "action_cell_reverse_index_mismatch",
                    "Edge reverse index does not point back to containing action cell.",
                    action_cell_id=action_cell_id,
                    edge_id=edge_id,
                )
            edge_source_cell = state_layer.cell_of(registry.source_state_id(edge_id))
            edge_target_cell = state_layer.cell_of(registry.target_state_id(edge_id))
            if edge_source_cell != source_cell:
                _issue(
                    issues,
                    action_layer,
                    "action_cell_source_mismatch",
                    "Edge source state cell does not match action-cell source.",
                    action_cell_id=action_cell_id,
                    edge_id=edge_id,
                )
            if edge_target_cell != target_cell:
                _issue(
                    issues,
                    action_layer,
                    "action_cell_target_mismatch",
                    "Edge target state cell does not match action-cell target.",
                    action_cell_id=action_cell_id,
                    edge_id=edge_id,
                )
            if edge_source_cell == edge_target_cell:
                _issue(
                    issues,
                    action_layer,
                    "internal_edge_exposed",
                    "Live action cell exposes an edge internal to a state cell.",
                    action_cell_id=action_cell_id,
                    edge_id=edge_id,
                )

            source_state_id = registry.source_state_id(edge_id)
            source_child = (
                lower_state_layer.cell_of(source_state_id)
                if lower_state_layer is not None
                else state_layer.cell_of(source_state_id)
            )
            expected_source_child_edges.setdefault(source_child, []).append(edge_id)
            expected_base_source_edges.setdefault(source_state_id, []).append(edge_id)
            if lower_action_layer is not None:
                lower_action_cell = lower_action_layer.action_cell_for_edge_id(edge_id)
                if lower_action_cell is not None:
                    expected_lower_action_cells.setdefault(source_child, set()).add(
                        lower_action_cell
                    )

        expected_child_edge_map = {
            child: tuple(sorted(child_edge_ids))
            for child, child_edge_ids in sorted(expected_source_child_edges.items())
        }
        actual_child_edge_map = (
            action_layer.edge_ids_by_action_cell_by_source_child.get(action_cell_id, {})
        )
        if actual_child_edge_map != expected_child_edge_map:
            _issue(
                issues,
                action_layer,
                "source_child_edge_mismatch",
                "Source-child edge support does not match action-cell edges.",
                action_cell_id=action_cell_id,
            )

        actual_source_children = action_layer.source_child_cells_by_action_cell.get(
            action_cell_id,
            (),
        )
        if actual_source_children != tuple(sorted(expected_child_edge_map)):
            _issue(
                issues,
                action_layer,
                "source_child_cells_mismatch",
                "Source-child cell list does not match source-child edge map.",
                action_cell_id=action_cell_id,
            )

        expected_lower_map = {
            child: tuple(sorted(lower_action_cells))
            for child, lower_action_cells in sorted(expected_lower_action_cells.items())
        }
        actual_lower_map = (
            action_layer.lower_action_cells_by_action_cell_by_source_child.get(
                action_cell_id,
                {},
            )
        )
        if actual_lower_map != expected_lower_map:
            _issue(
                issues,
                action_layer,
                "lower_action_cell_support_mismatch",
                "Lower action-cell support does not match lower layer indexes.",
                action_cell_id=action_cell_id,
            )

        expected_base_source_map = {
            source_id: tuple(sorted(source_edge_ids))
            for source_id, source_edge_ids in sorted(expected_base_source_edges.items())
        }
        actual_base_source_map = (
            action_layer.edge_ids_by_action_cell_by_base_source.get(action_cell_id, {})
        )
        if actual_base_source_map != expected_base_source_map:
            _issue(
                issues,
                action_layer,
                "base_source_edge_mismatch",
                "Flattened base-source support does not match action-cell edges.",
                action_cell_id=action_cell_id,
            )
        actual_base_source_ids = action_layer.base_source_ids_by_action_cell.get(
            action_cell_id,
            (),
        )
        if actual_base_source_ids != tuple(sorted(expected_base_source_map)):
            _issue(
                issues,
                action_layer,
                "base_source_ids_mismatch",
                "Base-source id list does not match flattened base-source map.",
                action_cell_id=action_cell_id,
            )

    for edge_id, action_cell_id in action_layer.action_cell_by_edge_id.items():
        if edge_id not in action_layer.edge_ids_by_action_cell.get(action_cell_id, {}):
            _issue(
                issues,
                action_layer,
                "orphan_action_cell_reverse_index",
                "Reverse action-cell index points to a cell not containing the edge.",
                action_cell_id=action_cell_id,
                edge_id=edge_id,
            )


def _validate_collection_support_unions(
    action_layer: ActionPartitionLayer,
    live_collections: set[ActionCollectionId],
    issues: list[PartitionInvariantIssue],
) -> None:
    for collection_id in live_collections:
        expected_children: set[StateCellId] = set()
        expected_base_sources: set[StateId] = set()
        for action_cell_id in action_layer.action_cells_for_collection(collection_id):
            expected_children.update(
                action_layer.source_child_cells_by_action_cell.get(action_cell_id, ())
            )
            expected_base_sources.update(
                action_layer.base_source_ids_by_action_cell.get(action_cell_id, ())
            )
        actual_children = action_layer.active_child_cells_by_collection.get(
            collection_id,
            (),
        )
        if actual_children != tuple(sorted(expected_children)):
            _issue(
                issues,
                action_layer,
                "active_child_collection_mismatch",
                "Collection active child cells do not equal action-cell support union.",
                action_collection_id=collection_id,
            )
        actual_base_sources = action_layer.base_active_source_ids_by_collection.get(
            collection_id,
            (),
        )
        if actual_base_sources != tuple(sorted(expected_base_sources)):
            _issue(
                issues,
                action_layer,
                "base_active_source_collection_mismatch",
                "Collection base sources do not equal action-cell support union.",
                action_collection_id=collection_id,
            )


def _validate_internal_edges(
    action_layer: ActionPartitionLayer,
    state_layer: StatePartitionLayer,
    registry: BaseGraphRegistry,
    issues: list[PartitionInvariantIssue],
) -> None:
    active_state_cells = set(state_layer.all_cell_ids())
    live_edge_ids = {
        edge_id
        for edge_ids in action_layer.edge_ids_by_action_cell.values()
        for edge_id in edge_ids
    }
    for state_cell_id, internal_edge_ids in action_layer.internal_edge_ids_by_state_cell.items():
        for edge_id in internal_edge_ids:
            if edge_id in live_edge_ids:
                _issue(
                    issues,
                    action_layer,
                    "internal_edge_live",
                    "Internal edge is still present in a live action cell.",
                    state_cell_id=state_cell_id,
                    edge_id=edge_id,
                )
            if state_cell_id not in active_state_cells:
                continue
            source_cell = state_layer.cell_of(registry.source_state_id(edge_id))
            target_cell = state_layer.cell_of(registry.target_state_id(edge_id))
            if source_cell != state_cell_id or target_cell != state_cell_id:
                _issue(
                    issues,
                    action_layer,
                    "internal_edge_cell_mismatch",
                    "Internal edge no longer lies inside its recorded state cell.",
                    state_cell_id=state_cell_id,
                    edge_id=edge_id,
                )
    for state_cell_id, records in action_layer.internal_edge_records_by_state_cell.items():
        for record in records:
            if record.state_cell_id != state_cell_id or record.tier != action_layer.tier_index:
                _issue(
                    issues,
                    action_layer,
                    "internal_edge_record_mismatch",
                    "Internal edge record tier or state cell is inconsistent.",
                    state_cell_id=state_cell_id,
                    edge_id=record.edge_id,
                )
            if record.edge_id not in action_layer.internal_edge_ids_by_state_cell.get(
                state_cell_id,
                {},
            ):
                _issue(
                    issues,
                    action_layer,
                    "internal_edge_record_without_edge",
                    "Internal edge record has no matching internal edge id.",
                    state_cell_id=state_cell_id,
                    edge_id=record.edge_id,
                )


__all__ = [
    "PartitionInvariantIssue",
    "PartitionInvariantReport",
    "action_layer_invariant_report",
]
