from __future__ import annotations

from state_collapser.examples.cable_parallel_env import (
    ANCHOR_1,
    ANCHOR_2,
    ANCHOR_3,
    START_STATE,
    manhattan_distance,
    required_tensions,
)


def test_manhattan_distance_matches_workspace_metric() -> None:
    assert manhattan_distance((0, 0), (2, 2)) == 4


def test_required_tensions_reflect_pose_and_theta() -> None:
    assert required_tensions(START_STATE) == (2, 2, 1)


def test_anchor_layout_is_asymmetric() -> None:
    assert ANCHOR_1 == (0, 2)
    assert ANCHOR_2 == (2, 2)
    assert ANCHOR_3 == (1, 0)
