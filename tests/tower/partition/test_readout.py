"""Tests for partition tower quotient readouts."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.schema import DimensionwiseSchema
from state_collapser.tower.partition.tower import PartitionTower


def edge(source: State, target: State, label: object = "x") -> BaseEdge:
    return BaseEdge(
        source=source,
        action=PrimitiveAction(payload=("move", label), identity=("move", label), labels=(label,)),
        target=target,
    )


def test_readout_projects_states_by_partition_cells() -> None:
    start = State(payload=("start",), identity="start")
    goal = State(payload=("goal",), identity="goal")
    base_edge = edge(start, goal)
    tower = PartitionTower(schema=DimensionwiseSchema(("x",)))
    tower.initialize(initial_states=(start,), initial_edges=(base_edge,), current_state=goal)

    readouts = tower.to_quotient_tier_views()

    assert len(readouts) == 2
    assert readouts[1].same_coset(start, goal) is True
    assert readouts[1].current_position == tower.current_state_cell(1, goal)


def test_readout_projects_live_action_cells_and_trivial_internal_edges() -> None:
    start = State(payload=("start",), identity="start")
    middle = State(payload=("middle",), identity="middle")
    goal = State(payload=("goal",), identity="goal")
    contracted = edge(start, middle, "x")
    live = edge(start, goal, "z")
    tower = PartitionTower(schema=DimensionwiseSchema(("x",)))
    tower.initialize(
        initial_states=(start,),
        initial_edges=(contracted, live),
        current_state=start,
    )

    readouts = tower.to_quotient_tier_views()

    assert readouts[1].projected_edge_is_trivial(contracted) is True
    assert readouts[1].projection.project_edge(contracted) is None
    assert readouts[1].projection.project_edge(live) is not None
    projected_live = readouts[1].projection.project_edge(live)
    assert readouts[1].cosets.edge_members(projected_live) == frozenset({live})
