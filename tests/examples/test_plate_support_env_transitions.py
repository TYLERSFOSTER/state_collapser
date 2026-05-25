from __future__ import annotations

from state_collapser.examples.plate_support_env import (
    START_STATE,
    PlateSupportState,
    primitive_transition,
)


def test_valid_plate_motion_actions() -> None:
    assert primitive_transition(START_STATE, 0).next_state == PlateSupportState(3, 2, 0, 1, 1, 1)
    assert primitive_transition(START_STATE, 2).next_state == PlateSupportState(2, 3, 0, 1, 1, 1)

    rotatable = PlateSupportState(1, 1, 0, 2, 2, 2)
    assert primitive_transition(rotatable, 4).next_state == PlateSupportState(1, 1, 1, 2, 2, 2)


def test_invalid_plate_motion_actions_self_loop() -> None:
    state = PlateSupportState(0, 2, 1, 2, 2, 2)

    move_left = primitive_transition(state, 1)
    assert move_left.invalid_move is True
    assert move_left.next_state == state

    move_right = primitive_transition(PlateSupportState(4, 2, 0, 2, 2, 2), 0)
    assert move_right.invalid_move is True
    assert move_right.next_state == PlateSupportState(4, 2, 0, 2, 2, 2)


def test_valid_arm_extension_actions() -> None:
    state = PlateSupportState(2, 2, 0, 1, 1, 1)

    assert primitive_transition(state, 6).next_state == PlateSupportState(2, 2, 0, 2, 1, 1)
    assert primitive_transition(state, 8).next_state == PlateSupportState(2, 2, 0, 1, 2, 1)
    assert primitive_transition(state, 10).next_state == PlateSupportState(2, 2, 0, 1, 1, 2)


def test_invalid_resulting_arm_action_self_loop() -> None:
    state = PlateSupportState(2, 2, 0, 1, 1, 1)

    result = primitive_transition(state, 7)
    assert result.invalid_move is True
    assert result.next_state == state


def test_valid_self_transition_from_clipped_arm_action() -> None:
    state = PlateSupportState(2, 2, 0, 2, 2, 2)

    result = primitive_transition(state, 6)
    assert result.valid_transition is True
    assert result.valid_self_transition is True
    assert result.invalid_move is False
    assert result.next_state == state


def test_transition_metadata_distinguishes_candidate_and_result() -> None:
    state = PlateSupportState(2, 2, 0, 1, 1, 1)

    result = primitive_transition(state, 7)
    assert result.candidate_state == PlateSupportState(2, 2, 0, 0, 1, 1)
    assert result.next_state == state
    assert result.candidate_valid is False
    assert result.valid_transition is False
