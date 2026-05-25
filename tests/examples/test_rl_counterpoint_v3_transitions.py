"""Transition checks for the rl_counterpoint_v3 example."""

from state_collapser.examples.rl_counterpoint_v3 import (
    ACTION_COUNT,
    DEFAULT_GRAPH_SPEC,
    START_STATE,
    RlCounterpointState,
    action_index_to_step_delta,
    is_parallel_perfect_outer_motion,
    is_valid_step_delta_action,
    primitive_transition,
    propose_primitive_action,
    step_delta_to_action_index,
    valid_outgoing_transitions,
)


def test_candidate_proposal_advances_beat_index() -> None:
    action, _ = valid_outgoing_transitions(START_STATE, spec=DEFAULT_GRAPH_SPEC)[0]
    candidate = propose_primitive_action(START_STATE, action, spec=DEFAULT_GRAPH_SPEC)
    assert candidate.beat_index == 1


def test_start_state_has_valid_outgoing_transitions() -> None:
    outgoing = valid_outgoing_transitions(START_STATE, spec=DEFAULT_GRAPH_SPEC)
    assert outgoing


def test_invalid_action_produces_self_transition() -> None:
    valid_actions = {
        action
        for action, _ in valid_outgoing_transitions(
            START_STATE,
            spec=DEFAULT_GRAPH_SPEC,
        )
    }
    invalid_action = next(
        action for action in range(ACTION_COUNT) if action not in valid_actions
    )
    result = primitive_transition(START_STATE, invalid_action, spec=DEFAULT_GRAPH_SPEC)
    assert result.invalid_move
    assert result.next_state == START_STATE


def test_parallel_perfect_outer_motion_is_rejected() -> None:
    source = RlCounterpointState(51, 55, 58, 0)
    step_delta = (1, 1, 1)
    target = RlCounterpointState(52, 56, 59, 1)
    assert is_parallel_perfect_outer_motion(source, target, spec=DEFAULT_GRAPH_SPEC)
    assert not is_valid_step_delta_action(source, step_delta, spec=DEFAULT_GRAPH_SPEC)
    assert step_delta_to_action_index(step_delta, spec=DEFAULT_GRAPH_SPEC) >= 0
    assert action_index_to_step_delta(
        step_delta_to_action_index(step_delta, spec=DEFAULT_GRAPH_SPEC),
        spec=DEFAULT_GRAPH_SPEC,
    ) == step_delta
