"""Tests for partition tower initialization."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.ids import SchemaBlockId, StateCellId
from state_collapser.tower.partition.schema import DimensionwiseSchema, NoContractionSchema
from state_collapser.tower.partition.tower import PartitionTower, build_partition_tower_full


def edge(source: State, target: State, label: object = "x") -> BaseEdge:
    return BaseEdge(
        source=source,
        action=PrimitiveAction(payload=("move", label), identity=("move", label), labels=(label,)),
        target=target,
    )


def test_empty_initialization() -> None:
    tower = PartitionTower()

    result = tower.initialize(initial_states=(), initial_edges=(), current_state=None)

    assert len(tower.state_layers) == 1
    assert len(tower.action_layers) == 1
    assert result.changed is False
    assert result.current_position_by_tier == (None,)


def test_one_state_no_edge_initialization() -> None:
    state = State(payload=("s",), identity="s")
    tower = PartitionTower(schema=NoContractionSchema())

    result = tower.initialize(initial_states=(state,), initial_edges=(), current_state=state)

    assert tower.current_position_at_every_tier(state) == (StateCellId(tier=0, ordinal=0),)
    assert result.diagnostics.discovered_state_count == 1
    assert result.diagnostics.discovered_edge_count == 0


def test_two_state_one_edge_collapses_under_matching_schema() -> None:
    start = State(payload=("start",), identity="start")
    goal = State(payload=("goal",), identity="goal")
    base_edge = edge(start, goal, "x")
    tower = PartitionTower(schema=DimensionwiseSchema(("x",)))

    result = tower.initialize(
        initial_states=(start,),
        initial_edges=(base_edge,),
        current_state=goal,
    )

    assert len(tower.state_layers) == 2
    start_cell = tower.state_layers[1].cell_of(tower.registry.state_id_by_state[start])
    goal_cell = tower.state_layers[1].cell_of(tower.registry.state_id_by_state[goal])
    assert start_cell == goal_cell
    assert result.state_merges
    assert result.schema_assignments[0].block_id == SchemaBlockId("x")
    assert result.internal_edges[0].edge_id == tower.registry.edge_id_by_edge[base_edge]


def test_full_build_helper_uses_initialization_semantics() -> None:
    start = State(payload=("start",), identity="start")
    goal = State(payload=("goal",), identity="goal")
    base_edge = edge(start, goal, "x")

    tower = build_partition_tower_full(
        states=(start,),
        edges=(base_edge,),
        current_state=goal,
        schema=DimensionwiseSchema(("x",)),
    )

    assert len(tower.state_layers) == 2
    assert tower.last_update_result is not None
    assert tower.last_update_result.state_merges
