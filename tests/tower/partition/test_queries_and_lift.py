"""Tests for partition-tower query, lift, and refinement surfaces."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.ids import ActionCollectionId
from state_collapser.tower.partition.schema import DimensionwiseSchema
from state_collapser.tower.partition.tower import PartitionTower


def state(name: str) -> State:
    return State(payload=(name,), identity=name)


def edge(source: State, target: State, label: object = "x") -> BaseEdge:
    return BaseEdge(
        source=source,
        action=PrimitiveAction(
            payload=("move", label),
            identity=("move", label),
            labels=(label,),
        ),
        target=target,
    )


def build_lift_tower() -> tuple[PartitionTower, State, State, State, BaseEdge, BaseEdge]:
    start = state("start")
    middle = state("middle")
    goal = state("goal")
    contracted = edge(start, middle, "x")
    start_to_goal = edge(start, goal, "z")
    middle_to_goal = edge(middle, goal, "z")
    tower = PartitionTower(schema=DimensionwiseSchema(("x",)))
    tower.initialize(
        initial_states=(start, middle, goal),
        initial_edges=(contracted, start_to_goal, middle_to_goal),
        current_state=start,
    )
    return tower, start, middle, goal, start_to_goal, middle_to_goal


def test_query_methods_expose_state_and_action_cells_without_readout() -> None:
    tower, start, middle, _goal, start_to_goal, middle_to_goal = build_lift_tower()
    merged_cell = tower.current_state_cell(1, start)

    assert merged_cell == tower.current_state_cell(1, middle)
    assert set(tower.state_cell_members(1, merged_cell)) == {start, middle}
    action_cells = tower.outgoing_action_cells(1, merged_cell)

    assert len(action_cells) == 1
    assert set(tower.action_cell_members(1, action_cells[0])) == {
        start_to_goal,
        middle_to_goal,
    }
    assert tower.representative_edges(1, action_cells[0]) == (
        start_to_goal,
        middle_to_goal,
    )


def test_lift_candidates_prefer_directly_executable_edges() -> None:
    tower, start, middle, _goal, start_to_goal, middle_to_goal = build_lift_tower()
    merged_cell = tower.current_state_cell(1, start)
    action_cell = tower.outgoing_action_cells(1, merged_cell)[0]

    assert tower.lift_candidates(1, action_cell, start) == (start_to_goal,)
    assert tower.lift_candidates(1, action_cell, middle) == (middle_to_goal,)


def test_action_cell_for_edge_maps_concrete_edge_without_readout() -> None:
    tower, start, _middle, _goal, start_to_goal, middle_to_goal = build_lift_tower()
    merged_cell = tower.current_state_cell(1, start)
    action_cell = tower.outgoing_action_cells(1, merged_cell)[0]

    assert tower.action_cell_for_edge(1, start_to_goal) == action_cell
    assert tower.action_cell_for_edge(1, middle_to_goal) == action_cell
    assert tower.action_cell_for_edge(999, start_to_goal) is None


def test_lift_candidates_fall_back_to_representatives() -> None:
    tower, start, _middle, goal, start_to_goal, middle_to_goal = build_lift_tower()
    merged_cell = tower.current_state_cell(1, start)
    action_cell = tower.outgoing_action_cells(1, merged_cell)[0]

    assert tower.lift_candidates(1, action_cell, goal) == (
        start_to_goal,
        middle_to_goal,
    )


def test_refinement_fiber_exposes_state_collection_and_action_fibers() -> None:
    tower, start, middle, _goal, _start_to_goal, _middle_to_goal = build_lift_tower()
    merged_cell = tower.current_state_cell(1, start)
    action_collection = tower.action_layers[1].outgoing_collection(merged_cell)
    action_cell = tower.outgoing_action_cells(1, merged_cell)[0]

    state_fiber = tower.refinement_fiber(1, merged_cell)
    collection_fiber = tower.refinement_fiber(1, action_collection)
    action_fiber = tower.refinement_fiber(1, action_cell)

    assert {
        tuple(tower.state_cell_members(0, state_cell_id)) for state_cell_id in state_fiber
    } == {(start,), (middle,)}
    assert all(isinstance(cell_id, ActionCollectionId) for cell_id in collection_fiber)
    assert len(collection_fiber) == 2
    assert len(action_fiber) == 2
