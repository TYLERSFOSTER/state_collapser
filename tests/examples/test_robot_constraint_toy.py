"""Tests for the robot-constraint toy environment."""

from __future__ import annotations

from state_collapser.examples.robot_constraint_toy import (
    RobotConstraintHiddenGraph,
    RobotConstraintToy,
)
from state_collapser.tower.partition.schema import DimensionwiseSchema
from state_collapser.tower.runtime import TowerRuntime


def test_valid_state_generation() -> None:
    env = RobotConstraintToy()

    states = env.valid_states()

    assert env.start_state in states
    assert env.goal_state in states
    assert len(states) == 11


def test_valid_action_generation() -> None:
    env = RobotConstraintToy()

    actions = env.valid_actions()

    assert len(actions) == 4
    assert {action.payload[1] for action in actions} == {"left", "right", "up", "down"}


def test_edge_legality() -> None:
    env = RobotConstraintToy()
    hidden = RobotConstraintHiddenGraph(env)
    start = env.start_state

    edges = hidden.out_edges(start)

    assert all(hidden.is_valid_edge(edge) for edge in edges)


def test_local_label_availability_in_some_regions() -> None:
    env = RobotConstraintToy()

    assert env.region_labels(env.state_at(0, 2)) == ("hinge",)


def test_absence_of_label_support_in_other_regions_where_intended() -> None:
    env = RobotConstraintToy()

    assert env.region_labels(env.state_at(0, 0)) == ()


def test_schema_controlled_partition_runtime_contracts_labeled_vista_edge() -> None:
    env = RobotConstraintToy()
    hidden = RobotConstraintHiddenGraph(env)
    runtime = TowerRuntime(
        hidden_graph=hidden,
        contraction_schema=DimensionwiseSchema(("hinge",)),
    )
    up_action = next(action for action in env.valid_actions() if action.payload[1] == "up")

    runtime.reset(initial_state=env.start_state)
    runtime.step(up_action)

    source = env.state_at(0, 1)
    target = env.state_at(0, 2)
    assert runtime.states_share_coset(source, target, 1)
    assert runtime.last_tower_update_result is not None
    assert runtime.last_tower_update_result.schema_assignments
