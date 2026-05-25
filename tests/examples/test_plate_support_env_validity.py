from __future__ import annotations

from state_collapser.examples.plate_support_env import (
    CANDIDATE_GOAL_STATE,
    START_STATE,
    PlateSupportState,
    all_sockets_in_bounds,
    engaged_arm_reachability,
    goal_changes_plate_pose,
    goal_changes_support_configuration,
    goal_differs_from_start,
    goal_is_one_primitive_action_from_start,
    has_minimum_engaged_supports,
    has_stable_support_pattern,
    has_valid_goal_state,
    has_valid_start_state,
    is_valid_state,
    plate_center_in_bounds,
)


def test_plate_center_in_bounds_subpredicate() -> None:
    assert plate_center_in_bounds(START_STATE) is True
    assert plate_center_in_bounds(PlateSupportState(-1, 2, 0, 1, 1, 1)) is False
    assert plate_center_in_bounds(PlateSupportState(2, 5, 0, 1, 1, 1)) is False


def test_all_sockets_in_bounds_subpredicate() -> None:
    assert all_sockets_in_bounds(START_STATE) is True
    assert all_sockets_in_bounds(PlateSupportState(0, 2, 0, 1, 1, 1)) is False


def test_engaged_arm_reachability_subpredicate() -> None:
    assert engaged_arm_reachability(START_STATE) == (True, True, True)
    assert engaged_arm_reachability(PlateSupportState(2, 4, 0, 1, 1, 1)) == (
        False,
        False,
        False,
    )
    assert engaged_arm_reachability(PlateSupportState(2, 2, 0, 0, 1, 1)) == (
        False,
        True,
        True,
    )


def test_minimum_engaged_supports_subpredicate() -> None:
    assert has_minimum_engaged_supports(START_STATE) is True
    assert has_minimum_engaged_supports(PlateSupportState(2, 2, 0, 1, 0, 0)) is False


def test_stable_support_pattern_subpredicate() -> None:
    assert has_stable_support_pattern(START_STATE) is True
    assert has_stable_support_pattern(PlateSupportState(2, 2, 0, 0, 1, 1)) is False
    assert has_stable_support_pattern(PlateSupportState(2, 2, 0, 1, 0, 1)) is True


def test_full_validity_for_clearly_valid_states() -> None:
    assert is_valid_state(START_STATE) is True

    valid_shifted = PlateSupportState(2, 3, 0, 1, 1, 1)
    assert is_valid_state(valid_shifted) is True


def test_full_validity_for_clearly_invalid_states() -> None:
    assert is_valid_state(PlateSupportState(-1, 2, 0, 1, 1, 1)) is False
    assert is_valid_state(PlateSupportState(0, 2, 0, 1, 1, 1)) is False
    assert is_valid_state(PlateSupportState(2, 2, 0, 1, 0, 0)) is False
    assert is_valid_state(PlateSupportState(2, 4, 0, 1, 1, 1)) is False
    assert is_valid_state(PlateSupportState(2, 2, 0, 0, 1, 1)) is False


def test_start_and_candidate_goal_are_currently_valid() -> None:
    assert is_valid_state(START_STATE) is True
    assert is_valid_state(CANDIDATE_GOAL_STATE) is True


def test_start_state_validation_helper() -> None:
    assert has_valid_start_state() is True


def test_goal_state_validation_helper() -> None:
    assert has_valid_goal_state() is True


def test_goal_differs_from_start() -> None:
    assert goal_differs_from_start() is True


def test_goal_changes_plate_pose() -> None:
    assert goal_changes_plate_pose() is True


def test_goal_changes_support_configuration() -> None:
    assert goal_changes_support_configuration() is True


def test_goal_is_not_one_primitive_action_from_start() -> None:
    assert goal_is_one_primitive_action_from_start() is False
