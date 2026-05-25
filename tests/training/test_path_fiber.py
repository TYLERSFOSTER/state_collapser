"""Tests for concrete path-fiber behavior over partition tower queries."""

from __future__ import annotations

import pytest

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.schema import DimensionwiseSchema
from state_collapser.tower.partition.tower import PartitionTower
from state_collapser.training import (
    FiberDeparture,
    FiberDepartureReason,
    FrozenQuotientBehavior,
    PathFiber,
)


def state(name: str) -> State:
    return State(payload=(name,), identity=name)


def edge(source: State, target: State, label: str) -> BaseEdge:
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


def build_path_fiber_fixture() -> tuple[
    PartitionTower,
    State,
    State,
    State,
    State,
    BaseEdge,
    BaseEdge,
    BaseEdge,
    PathFiber,
]:
    start = state("start")
    left = state("left")
    right = state("right")
    goal = state("goal")
    start_left = edge(start, left, "choose")
    start_right = edge(start, right, "choose")
    start_goal = edge(start, goal, "bad")
    contract = edge(left, right, "contract")
    left_goal = edge(left, goal, "finish")
    right_goal = edge(right, goal, "finish")
    tower = PartitionTower(schema=DimensionwiseSchema(("contract",)))
    tower.initialize(
        initial_states=(start, left, right, goal),
        initial_edges=(start_left, start_right, start_goal, contract, left_goal, right_goal),
        current_state=start,
    )

    source_cell = tower.current_state_cell(1, start)
    target_cell = tower.current_state_cell(1, left)
    coarse_action_cell = tower.action_cell_for_edge(1, start_left)
    behavior = FrozenQuotientBehavior.from_step(
        behavior_id="frozen-choose",
        coarse_tier=1,
        supported_fine_tier=0,
        source_cell=source_cell,
        action_cell=coarse_action_cell,
        target_cell=target_cell,
    )
    path_fiber = PathFiber(
        fiber_id="choose-fiber",
        tower=tower,
        fine_tier=0,
        coarse_tier=1,
        frozen_behavior=behavior,
    )
    return tower, start, left, right, goal, start_left, start_right, start_goal, path_fiber


def test_path_fiber_validates_adjacent_tiers() -> None:
    tower, start, *_rest, path_fiber = build_path_fiber_fixture()

    with pytest.raises(ValueError, match="coarse_tier == fine_tier"):
        PathFiber(
            fiber_id="bad",
            tower=tower,
            fine_tier=0,
            coarse_tier=2,
            frozen_behavior=path_fiber.frozen_behavior,
        )

    assert path_fiber.current_fine_state_cell(start) == tower.current_state_cell(0, start)
    assert path_fiber.current_coarse_state_cell(start) == tower.current_state_cell(1, start)


def test_admissible_action_cells_are_computed_from_tower_queries() -> None:
    tower, start, _left, _right, _goal, start_left, start_right, _bad, path_fiber = (
        build_path_fiber_fixture()
    )
    admissible = path_fiber.admissible_action_cells(start)

    assert tuple(tower.action_cell_members(0, cell) for cell in admissible) == (
        (start_left,),
        (start_right,),
    )


def test_action_mask_matches_admissibility() -> None:
    _tower, start, *_rest, path_fiber = build_path_fiber_fixture()
    vocabulary = path_fiber.action_vocabulary(start)

    assert len(vocabulary) == 3
    assert path_fiber.action_mask(start, action_vocabulary=vocabulary) == (
        True,
        True,
        False,
    )


def test_lift_candidates_prefer_executable_representatives() -> None:
    tower, start, _left, _right, _goal, start_left, start_right, _bad, path_fiber = (
        build_path_fiber_fixture()
    )
    admissible = path_fiber.admissible_action_cells(start)

    assert tower.action_cell_members(0, admissible[0]) == (start_left,)
    assert path_fiber.lift_candidates(start, admissible[0]) == (start_left,)
    assert path_fiber.lift_candidates(start, admissible[1]) == (start_right,)


def test_departure_diagnostics_are_explicit() -> None:
    _tower, start, _left, _right, _goal, _start_left, _start_right, bad, path_fiber = (
        build_path_fiber_fixture()
    )
    bad_action_cell = path_fiber.tower.action_cell_for_edge(0, bad)

    assert bad_action_cell is not None
    departure = path_fiber.diagnose_departure(start, bad_action_cell)

    assert isinstance(departure, FiberDeparture)
    assert departure.reason is FiberDepartureReason.PROJECTED_TARGET_MISMATCH


def test_unknown_state_produces_departure_instead_of_exception() -> None:
    _tower, _start, _left, _right, _goal, _start_left, _start_right, bad, path_fiber = (
        build_path_fiber_fixture()
    )
    bad_action_cell = path_fiber.tower.action_cell_for_edge(0, bad)

    assert bad_action_cell is not None
    departure = path_fiber.diagnose_departure(state("ghost"), bad_action_cell)

    assert isinstance(departure, FiberDeparture)
    assert departure.reason is FiberDepartureReason.UNKNOWN_STATE_CELL
