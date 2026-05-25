from __future__ import annotations

import numpy as np
import pytest

from state_collapser.examples.plate_support_env import (
    ACTION_COUNT,
    CANDIDATE_GOAL_STATE,
    MAX_STEPS,
    START_STATE,
    PlateSupportEnv,
    encode_observation,
)


def test_spaces_match_spec() -> None:
    env = PlateSupportEnv()

    assert env.action_space.n == ACTION_COUNT
    assert env.observation_space.nvec.tolist() == [5, 5, 4, 3, 3, 3]


def test_reset_returns_observation_and_info() -> None:
    env = PlateSupportEnv()

    obs, info = env.reset()

    assert isinstance(obs, np.ndarray)
    assert obs.tolist() == encode_observation(START_STATE).tolist()
    assert info["state"] == START_STATE
    assert info["goal_state"] == CANDIDATE_GOAL_STATE
    assert env.step_count == 0


def test_step_returns_gymnasium_five_tuple_and_info_keys() -> None:
    env = PlateSupportEnv()
    env.reset()

    obs, reward, terminated, truncated, info = env.step(0)

    assert isinstance(obs, np.ndarray)
    assert isinstance(reward, float)
    assert isinstance(terminated, bool)
    assert isinstance(truncated, bool)
    assert {"state", "valid_transition", "invalid_move", "goal_reached"} <= set(info)


def test_step_counter_increments() -> None:
    env = PlateSupportEnv()
    env.reset()

    env.step(0)
    env.step(2)

    assert env.step_count == 2


def test_invalid_action_raises_error() -> None:
    env = PlateSupportEnv()
    env.reset()

    with pytest.raises(ValueError):
        env.step(ACTION_COUNT)


def test_ansi_render_returns_text_summary() -> None:
    env = PlateSupportEnv(render_mode="ansi")
    env.reset()

    rendered = env.render()

    assert isinstance(rendered, str)
    assert "PlateSupportState" in rendered


def test_truncation_occurs_at_max_steps_without_goal() -> None:
    env = PlateSupportEnv()
    env.reset()

    for _ in range(MAX_STEPS):
        obs, reward, terminated, truncated, info = env.step(11)

    assert terminated is False
    assert truncated is True
    assert info["goal_reached"] is False
