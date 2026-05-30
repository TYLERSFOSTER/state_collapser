"""Tests for valid empty-outgoing coarse tier query states."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.schema import DimensionwiseSchema
from state_collapser.tower.partition.tower import PartitionTower


def state(name: str) -> State:
    return State(payload=(name,), identity=name)


def edge(source: State, target: State, label: object = "x") -> BaseEdge:
    return BaseEdge(
        source=source,
        action=PrimitiveAction(
            payload=("move", source.identity, target.identity),
            identity=("move", source.identity, target.identity),
            labels=(label,),
        ),
        target=target,
        labels=(label,),
    )


def test_coarse_tier_can_have_empty_outgoing_actions_while_base_tier_is_executable() -> None:
    left = state("left")
    right = state("right")
    left_to_right = edge(left, right)
    right_to_left = edge(right, left)
    tower = PartitionTower(schema=DimensionwiseSchema(("x",)))

    tower.initialize(
        initial_states=(left, right),
        initial_edges=(left_to_right, right_to_left),
        current_state=left,
    )

    base_cell = tower.current_state_cell(0, left)
    coarse_cell = tower.current_state_cell(1, left)

    assert tower.outgoing_action_cells(0, base_cell)
    assert tower.current_state_cell(1, right) == coarse_cell
    assert tower.outgoing_action_cells(1, coarse_cell) == ()
