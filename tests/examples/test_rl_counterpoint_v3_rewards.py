"""Reward checks for the rl_counterpoint_v3 example."""

from state_collapser.examples.rl_counterpoint_v3 import (
    ACTION_COUNT,
    CANDIDATE_GOAL_STATE,
    DEFAULT_GRAPH_SPEC,
    START_STATE,
    RlCounterpointState,
    all_valid_states,
    transition_reward,
    valid_outgoing_transitions,
)


def _find_goal_predecessor() -> tuple[RlCounterpointState, int]:
    for state in all_valid_states(DEFAULT_GRAPH_SPEC):
        for action, next_state in valid_outgoing_transitions(state, spec=DEFAULT_GRAPH_SPEC):
            if next_state == CANDIDATE_GOAL_STATE:
                return state, action
    raise AssertionError("Expected at least one valid predecessor of the candidate goal state.")


def test_invalid_move_reward_marks_hard_violation() -> None:
    valid_actions = {
        action
        for action, _ in valid_outgoing_transitions(
            START_STATE,
            spec=DEFAULT_GRAPH_SPEC,
        )
    }
    invalid_action = next(action for action in range(ACTION_COUNT) if action not in valid_actions)
    reward_result = transition_reward(
        START_STATE,
        invalid_action,
        START_STATE,
        spec=DEFAULT_GRAPH_SPEC,
    )
    assert reward_result.hard_violation
    assert not reward_result.terminal_success
    assert reward_result.reward < 0.0


def test_terminal_transition_reward_sets_success_flag() -> None:
    predecessor, action = _find_goal_predecessor()
    reward_result = transition_reward(
        predecessor,
        action,
        CANDIDATE_GOAL_STATE,
        spec=DEFAULT_GRAPH_SPEC,
    )
    assert reward_result.terminal_success
    assert reward_result.reward > 0.0
    assert "terminal_bonus" in reward_result.diagnostics
