from __future__ import annotations

from state_collapser.examples.dual_arm_manipulation_env import (
    LEFT_BASE,
    RIGHT_BASE,
    START_STATE,
    arm_can_contact_object,
    manhattan_distance,
)


def test_manhattan_distance_matches_workspace_metric() -> None:
    assert manhattan_distance((0, 0), (2, 1)) == 3


def test_arm_contact_depends_on_reach_and_object_pose() -> None:
    assert arm_can_contact_object(START_STATE, left_arm=True) is True
    assert arm_can_contact_object(START_STATE, left_arm=False) is True


def test_arm_bases_are_fixed_on_opposite_sides() -> None:
    assert LEFT_BASE == (0, 1)
    assert RIGHT_BASE == (2, 1)
