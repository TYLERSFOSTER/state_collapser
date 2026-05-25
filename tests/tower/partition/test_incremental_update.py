"""Tests for incremental partition-tower updates."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.schema import DimensionwiseSchema, NoContractionSchema
from state_collapser.tower.partition.tower import PartitionTower


def state(name: str) -> State:
    return State(payload=(name,), identity=name)


def edge(source: State, target: State, label: object = "x") -> BaseEdge:
    return BaseEdge(
        source=source,
        action=PrimitiveAction(payload=("move", label), identity=("move", label), labels=(label,)),
        target=target,
    )


def test_empty_delta_can_return_identity_morphism_when_requested() -> None:
    start = state("start")
    tower = PartitionTower()
    tower.initialize(initial_states=(start,), initial_edges=(), current_state=start)

    result = tower.update_with_delta(
        delta_states=(),
        delta_edges=(),
        current_state=start,
        build_morphism=True,
    )

    assert result.changed is False
    assert result.morphism.unchanged_tiers == (0,)
    assert result.diagnostics.delta_state_count == 0
    assert result.diagnostics.delta_edge_count == 0
    assert result.diagnostics.state_cell_merge_count == 0
    assert result.diagnostics.action_collection_merge_count == 0
    assert result.diagnostics.full_rebuild_validation_count == 0


def test_new_state_without_edges_extends_existing_layers() -> None:
    start = state("start")
    new = state("new")
    tower = PartitionTower()
    tower.initialize(initial_states=(start,), initial_edges=(), current_state=start)

    result = tower.update_with_delta(delta_states=(new,), delta_edges=(), current_state=new)

    assert result.changed is True
    assert tower.current_state_cell(0, new) is not None
    assert result.diagnostics.delta_state_count == 1


def test_new_unscheduled_edge_between_known_states_updates_outgoing_data() -> None:
    start = state("start")
    goal = state("goal")
    tower = PartitionTower(schema=NoContractionSchema())
    tower.initialize(initial_states=(start, goal), initial_edges=(), current_state=start)
    base_edge = edge(start, goal)

    result = tower.update_with_delta(delta_states=(), delta_edges=(base_edge,), current_state=start)

    source_cell = tower.current_state_cell(0, start)
    collection = tower.action_layers[0].outgoing_collection(source_cell)
    assert tower.action_layers[0].edge_ids_for_collection(collection) == (
        tower.registry.edge_id_by_edge[base_edge],
    )
    assert result.schema_assignments[0].block_id is None


def test_new_edge_to_new_state_can_create_contraction_tier() -> None:
    start = state("start")
    goal = state("goal")
    base_edge = edge(start, goal, "x")
    tower = PartitionTower(schema=DimensionwiseSchema(("x",)))
    tower.initialize(initial_states=(start,), initial_edges=(), current_state=start)

    result = tower.update_with_delta(
        delta_states=(goal,),
        delta_edges=(base_edge,),
        current_state=goal,
    )

    assert len(tower.state_layers) == 2
    assert tower.current_state_cell(1, start) == tower.current_state_cell(1, goal)
    assert result.state_merges
    assert result.action_merges
    assert result.diagnostics.delta_edge_count == 1
    assert result.diagnostics.state_cell_merge_count == 1
    assert result.diagnostics.action_collection_merge_count == 1
    assert result.diagnostics.full_rebuild_validation_count == 0
    assert result.affected_tiers == (0, 1)


def test_default_delta_update_avoids_morphism_capture(monkeypatch) -> None:
    start = state("start")
    goal = state("goal")
    base_edge = edge(start, goal, "x")
    tower = PartitionTower(schema=DimensionwiseSchema(("x",)))
    tower.initialize(initial_states=(start, goal), initial_edges=(), current_state=start)

    def fail_capture(self: PartitionTower) -> object:
        del self
        raise AssertionError("default update should not capture morphism domain")

    monkeypatch.setattr(PartitionTower, "_capture_morphism_domain", fail_capture)

    result = tower.update_with_delta(
        delta_states=(),
        delta_edges=(base_edge,),
        current_state=start,
    )

    assert result.changed
    assert result.morphism.state_cell_image_by_tier == {}
    assert result.morphism.action_collection_image_by_tier == {}
    assert result.morphism.action_cell_image_by_tier == {}


def test_delta_merge_records_explicit_state_cell_morphism() -> None:
    start = state("start")
    goal = state("goal")
    base_edge = edge(start, goal, "x")
    tower = PartitionTower(schema=DimensionwiseSchema(("x",)))
    tower.initialize(initial_states=(start, goal), initial_edges=(), current_state=start)
    old_start_cell = tower.current_state_cell(1, start)
    old_goal_cell = tower.current_state_cell(1, goal)

    result = tower.update_with_delta(
        delta_states=(),
        delta_edges=(base_edge,),
        current_state=start,
        build_morphism=True,
    )

    new_cell = tower.current_state_cell(1, start)
    assert new_cell == tower.current_state_cell(1, goal)
    assert result.morphism.state_cell_image_by_tier[1][old_start_cell] == new_cell
    assert result.morphism.state_cell_image_by_tier[1][old_goal_cell] == new_cell


def test_new_edge_is_outgoing_data_even_when_not_contracted() -> None:
    start = state("start")
    goal = state("goal")
    base_edge = edge(start, goal, "z")
    tower = PartitionTower(schema=DimensionwiseSchema(("x",)))
    tower.initialize(initial_states=(start,), initial_edges=(), current_state=start)

    result = tower.update_with_delta(
        delta_states=(goal,),
        delta_edges=(base_edge,),
        current_state=start,
    )

    source_cell = tower.current_state_cell(0, start)
    collection = tower.action_layers[0].outgoing_collection(source_cell)
    assert tower.action_layers[0].edge_ids_for_collection(collection) == (
        tower.registry.edge_id_by_edge[base_edge],
    )
    assert result.state_merges == ()


def test_random_schema_assignments_remain_stable_for_existing_edges() -> None:
    from state_collapser.tower.partition.schema import SeededRandomRateSchema

    start = state("start")
    first_goal = state("first")
    second_goal = state("second")
    first_edge = edge(start, first_goal, "a")
    second_edge = edge(start, second_goal, "b")
    tower = PartitionTower(schema=SeededRandomRateSchema(seed=5, block_count=3))
    tower.initialize(initial_states=(start,), initial_edges=(first_edge,), current_state=start)
    first_assignment = tower.schema_assignment_store.assignment_by_edge_id[
        tower.registry.edge_id_by_edge[first_edge]
    ]

    tower.update_with_delta(
        delta_states=(second_goal,),
        delta_edges=(second_edge,),
        current_state=start,
    )

    assert (
        tower.schema_assignment_store.assignment_by_edge_id[
            tower.registry.edge_id_by_edge[first_edge]
        ]
        == first_assignment
    )
