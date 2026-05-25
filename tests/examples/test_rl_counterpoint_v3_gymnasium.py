"""Gymnasium-surface checks for the rl_counterpoint_v3 example."""

from state_collapser.examples.rl_counterpoint_v3 import (
    DEFAULT_GRAPH_SPEC,
    RlCounterpointEnv,
    action_index_to_step_delta,
    is_valid_state,
    valid_outgoing_transitions,
)


def test_reset_returns_valid_start_state() -> None:
    env = RlCounterpointEnv()
    _, info = env.reset(seed=0)
    assert is_valid_state(env.state, spec=DEFAULT_GRAPH_SPEC)
    assert env.state.beat_index == 0
    assert info["has_legal_actions"]


def test_valid_step_advances_state_and_step_index() -> None:
    env = RlCounterpointEnv()
    env.reset(seed=0)
    action, next_state = valid_outgoing_transitions(env.state, spec=DEFAULT_GRAPH_SPEC)[0]
    _, reward, terminated, truncated, _ = env.step(action)
    assert env.step_index == 1
    assert env.state == next_state
    assert action_index_to_step_delta(action, spec=DEFAULT_GRAPH_SPEC) != (0, 0, 0)
    assert isinstance(reward, float)
    assert not (terminated and truncated)


def test_episode_truncates_at_max_steps_with_repeated_invalid_action() -> None:
    env = RlCounterpointEnv()
    env.reset(seed=0)
    valid_actions = {
        action
        for action, _ in valid_outgoing_transitions(
            env.state,
            spec=DEFAULT_GRAPH_SPEC,
        )
    }
    invalid_action = next(
        action for action in range(env.action_count) if action not in valid_actions
    )
    terminated = False
    truncated = False
    for _ in range(DEFAULT_GRAPH_SPEC.max_steps):
        _, _, terminated, truncated, _ = env.step(invalid_action)
        if terminated or truncated:
            break
    assert env.step_index == DEFAULT_GRAPH_SPEC.max_steps
    assert not terminated
    assert truncated
