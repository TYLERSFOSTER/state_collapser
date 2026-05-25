from __future__ import annotations

from state_collapser.examples.dual_arm_manipulation_env import (
    CANDIDATE_GOAL_STATE,
    START_STATE,
    DualArmManipulationState,
    all_valid_states,
    has_valid_goal_state,
    has_valid_start_state,
    is_valid_state,
)


def test_start_and_goal_states_are_valid() -> None:
    assert has_valid_start_state() is True
    assert has_valid_goal_state() is True
    assert is_valid_state(START_STATE) is True
    assert is_valid_state(CANDIDATE_GOAL_STATE) is True


def test_invalid_state_without_active_support_is_rejected() -> None:
    assert is_valid_state(DualArmManipulationState(1, 1, 0, 0, 0, 1, 1)) is False


def test_valid_state_set_is_nontrivial() -> None:
    assert len(all_valid_states()) > 10
