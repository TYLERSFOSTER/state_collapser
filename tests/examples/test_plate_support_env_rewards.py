from __future__ import annotations

from state_collapser.examples.plate_support_env import (
    CANDIDATE_GOAL_STATE,
    MAX_STEPS,
    START_STATE,
    PlateSupportState,
    primitive_transition,
    transition_reward,
    transition_terminated,
    transition_truncated,
)


def test_reward_on_valid_non_goal_move() -> None:
    next_state = primitive_transition(START_STATE, 0).next_state
    assert transition_reward(START_STATE, 0, next_state) == -1.0


def test_reward_on_invalid_self_loop() -> None:
    state = PlateSupportState(0, 2, 1, 2, 2, 2)
    result = primitive_transition(state, 1)
    assert result.next_state == state
    assert transition_reward(state, 1, result.next_state) == -3.0


def test_reward_on_goal_reaching_move() -> None:
    pre_goal = PlateSupportState(1, 1, 0, 2, 2, 2)
    result = primitive_transition(pre_goal, 4)
    assert result.next_state == CANDIDATE_GOAL_STATE
    assert transition_reward(pre_goal, 4, result.next_state) == 100.0


def test_termination_on_goal() -> None:
    assert transition_terminated(CANDIDATE_GOAL_STATE) is True


def test_non_termination_on_non_goal() -> None:
    assert transition_terminated(START_STATE) is False


def test_truncation_at_max_steps() -> None:
    assert transition_truncated(MAX_STEPS, terminated=False) is True
    assert transition_truncated(MAX_STEPS - 1, terminated=False) is False
    assert transition_truncated(MAX_STEPS, terminated=True) is False
