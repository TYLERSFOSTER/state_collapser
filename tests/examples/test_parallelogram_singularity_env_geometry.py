from __future__ import annotations

from state_collapser.examples.parallelogram_singularity_env import (
    CANDIDATE_GOAL_STATE,
    START_STATE,
    cyclic_angle_gap,
    is_singular_state,
)


def test_cyclic_angle_gap_wraps_correctly() -> None:
    assert cyclic_angle_gap(0, 3) == 1
    assert cyclic_angle_gap(0, 2) == 2


def test_start_and_goal_are_singular_states() -> None:
    assert is_singular_state(START_STATE) is True
    assert is_singular_state(CANDIDATE_GOAL_STATE) is True
