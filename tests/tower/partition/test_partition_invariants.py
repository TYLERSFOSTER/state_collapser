"""Invariant checks for partition tower source-support tables."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.ids import ActionCellId, ActionCollectionId
from state_collapser.tower.partition.schema import DimensionwiseSchema
from state_collapser.tower.partition.tower import PartitionTower


def state(name: str) -> State:
    """Build a named test state."""

    return State(payload=(name,), identity=name)


def edge(source: State, label: str, target: State) -> BaseEdge:
    """Build a labeled primitive edge."""

    return BaseEdge(
        source=source,
        action=PrimitiveAction(
            payload=("move", label),
            identity=("move", label),
            labels=(label,),
        ),
        target=target,
        labels=(label,),
    )


def build_nontrivial_tower() -> tuple[PartitionTower, State, State, State]:
    """Build a tower with a contraction and live outgoing quotient actions."""

    zero = state("0")
    one = state("1")
    two = state("2")
    contract = edge(zero, "contract", one)
    zero_to_two = edge(zero, "to2", two)
    one_to_two = edge(one, "to2", two)
    tower = PartitionTower(schema=DimensionwiseSchema(("contract",)))
    tower.initialize(
        initial_states=(zero, one, two),
        initial_edges=(contract, zero_to_two, one_to_two),
        current_state=zero,
    )
    return tower, zero, one, two


def build_incremental_tower() -> PartitionTower:
    """Build the same shape through incremental exploration."""

    zero = state("0")
    one = state("1")
    two = state("2")
    contract = edge(zero, "contract", one)
    zero_to_two = edge(zero, "to2", two)
    one_to_two = edge(one, "to2", two)
    tower = PartitionTower(schema=DimensionwiseSchema(("contract",)))
    tower.initialize(initial_states=(zero,), initial_edges=(), current_state=zero)
    tower.update_with_delta(
        delta_states=(one,),
        delta_edges=(contract,),
        current_state=one,
    )
    tower.update_with_delta(
        delta_states=(two,),
        delta_edges=(zero_to_two, one_to_two),
        current_state=two,
    )
    return tower


def first_live_action_cell(
    tower: PartitionTower,
    tier: int,
) -> tuple[ActionCollectionId, ActionCellId]:
    """Return one live action cell from a tower tier."""

    action_layer = tower.action_layers[tier]
    for state_cell_id in tower.state_layers[tier].all_cell_ids():
        collection_id = action_layer.outgoing_collection(state_cell_id)
        action_cells = action_layer.action_cells_for_collection(collection_id)
        if action_cells:
            return collection_id, action_cells[0]
    raise AssertionError("expected at least one live action cell")


def issue_codes(tower: PartitionTower) -> set[str]:
    """Return invariant issue codes for a tower."""

    return {issue.code for issue in tower.invariant_report().issues}


def test_initialized_tower_invariants_are_clean() -> None:
    """A normal initialized tower satisfies partition invariants."""

    tower, *_states = build_nontrivial_tower()

    report = tower.invariant_report()

    assert report.ok
    tower.assert_consistent()


def test_incremental_tower_invariants_are_clean() -> None:
    """A normal incrementally updated tower satisfies partition invariants."""

    tower = build_incremental_tower()

    report = tower.invariant_report()

    assert report.ok
    tower.assert_consistent()


def test_invariants_detect_corrupted_action_cell_reverse_index() -> None:
    """Reverse edge indexes must point back to the containing action cell."""

    tower, *_states = build_nontrivial_tower()
    _collection_id, action_cell_id = first_live_action_cell(tower, tier=0)
    action_layer = tower.action_layers[0]
    edge_id = action_layer.edge_ids_for_action_cell(action_cell_id)[0]
    action_layer.action_cell_by_edge_id.pop(edge_id)

    assert "action_cell_reverse_index_mismatch" in issue_codes(tower)


def test_invariants_detect_corrupted_base_source_cache() -> None:
    """Flattened base-source caches must agree with action-cell edge data."""

    tower, *_states = build_nontrivial_tower()
    _collection_id, action_cell_id = first_live_action_cell(tower, tier=1)
    action_layer = tower.action_layers[1]
    action_layer.edge_ids_by_action_cell_by_base_source[action_cell_id] = {}

    assert "base_source_edge_mismatch" in issue_codes(tower)


def test_invariants_detect_corrupted_source_child_support() -> None:
    """Adjacent-tier source-child support must agree with action-cell edges."""

    tower, *_states = build_nontrivial_tower()
    _collection_id, action_cell_id = first_live_action_cell(tower, tier=1)
    action_layer = tower.action_layers[1]
    action_layer.edge_ids_by_action_cell_by_source_child[action_cell_id] = {}

    assert "source_child_edge_mismatch" in issue_codes(tower)


def test_invariants_detect_dirty_collection_unless_allowed() -> None:
    """Dirty collections are failures only when dirty state is disallowed."""

    tower, *_states = build_nontrivial_tower()
    collection_id, _action_cell_id = first_live_action_cell(tower, tier=0)
    action_layer = tower.action_layers[0]
    action_layer.dirty_collection_ids[collection_id] = None

    strict_report = tower.invariant_report()
    dirty_allowed_report = tower.invariant_report(allow_dirty=True)

    assert "dirty_collection" in {issue.code for issue in strict_report.issues}
    assert dirty_allowed_report.ok
