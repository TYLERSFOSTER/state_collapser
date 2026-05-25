from __future__ import annotations

from state_collapser.examples.cable_parallel_env import (
    CANDIDATE_GOAL_STATE,
    START_STATE,
    primitive_transition,
    transition_reward,
)


def test_invalid_move_self_loops_with_penalty() -> None:
    result = primitive_transition(CANDIDATE_GOAL_STATE, 4)

    assert result.invalid_move is True
    assert result.next_state == CANDIDATE_GOAL_STATE
    assert transition_reward(CANDIDATE_GOAL_STATE, 4, result.next_state) == -2.0


def test_valid_move_changes_state() -> None:
    result = primitive_transition(START_STATE, 6)

    assert result.invalid_move is False
    assert result.next_state != START_STATE
