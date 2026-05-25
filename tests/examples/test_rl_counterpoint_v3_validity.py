"""Validity checks for the rl_counterpoint_v3 example."""

from state_collapser.examples.rl_counterpoint_v3 import (
    CANDIDATE_GOAL_STATE,
    DEFAULT_GRAPH_SPEC,
    START_STATE,
    RlCounterpointState,
    has_valid_goal_state,
    has_valid_start_state,
    is_goal_state,
    is_valid_state,
)


def test_default_start_and_goal_surfaces_are_valid() -> None:
    assert has_valid_start_state(DEFAULT_GRAPH_SPEC)
    assert has_valid_goal_state(DEFAULT_GRAPH_SPEC)
    assert is_valid_state(START_STATE, spec=DEFAULT_GRAPH_SPEC)
    assert is_valid_state(CANDIDATE_GOAL_STATE, spec=DEFAULT_GRAPH_SPEC)
    assert not is_goal_state(START_STATE, spec=DEFAULT_GRAPH_SPEC)
    assert is_goal_state(CANDIDATE_GOAL_STATE, spec=DEFAULT_GRAPH_SPEC)


def test_strict_voice_order_is_required() -> None:
    invalid = RlCounterpointState(
        bass_pitch=60,
        inner_pitch=60,
        upper_pitch=67,
        beat_index=0,
    )
    assert not is_valid_state(invalid, spec=DEFAULT_GRAPH_SPEC)


def test_pitch_range_is_enforced() -> None:
    invalid = RlCounterpointState(
        bass_pitch=47,
        inner_pitch=51,
        upper_pitch=55,
        beat_index=0,
    )
    assert not is_valid_state(invalid, spec=DEFAULT_GRAPH_SPEC)


def test_root_pitch_class_family_is_enforced() -> None:
    invalid = RlCounterpointState(
        bass_pitch=49,
        inner_pitch=52,
        upper_pitch=56,
        beat_index=0,
    )
    assert not is_valid_state(invalid, spec=DEFAULT_GRAPH_SPEC)
