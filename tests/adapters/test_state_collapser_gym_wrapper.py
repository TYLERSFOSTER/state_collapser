"""Tests for the hook-based Gymnasium wrapper."""

from __future__ import annotations

import gymnasium

from state_collapser.adapters.gymnasium import (
    StateCollapserGymHooks,
    StateCollapserGymWrapper,
)


class _FakeGymEnv:
    def __init__(self) -> None:
        self.action_space = gymnasium.spaces.Discrete(2)
        self.observation_space = gymnasium.spaces.Discrete(4)
        self.state = 0
        self.reset_calls: list[tuple[int | None, dict[str, object] | None]] = []
        self.step_actions: list[object] = []

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, object] | None = None,
    ) -> tuple[int, dict[str, object]]:
        self.reset_calls.append((seed, options))
        self.state = 0
        return self.state, {"reset_seen": True}

    def step(self, action: object) -> tuple[int, float, bool, bool, dict[str, object]]:
        self.step_actions.append(action)
        self.state += 1
        return self.state, 1.5, False, False, {"raw_action": action}


def test_hook_config_construction_accepts_optional_hooks() -> None:
    hooks = StateCollapserGymHooks(
        state_key=lambda observation, info: observation,
        action_key=lambda action, observation, info: action,
    )

    assert hooks.action_mask is None
    assert hooks.edge_labeler("s", "a", "t", {}) == ()


def test_wrapper_exposes_spaces_and_delegates_reset_and_step() -> None:
    env = _FakeGymEnv()
    wrapper = StateCollapserGymWrapper(
        env,
        StateCollapserGymHooks(
            state_key=lambda observation, info: f"s:{observation}",
            action_key=lambda action, observation, info: f"a:{action}",
        ),
    )

    assert wrapper.action_space is env.action_space
    assert wrapper.observation_space is env.observation_space

    observation, info = wrapper.reset(seed=7, options={"x": 1})
    assert observation == 0
    assert env.reset_calls == [(7, {"x": 1})]
    assert info["state_collapser"]["target_state_key"] == "s:0"

    step = wrapper.step(1)
    assert step[0] == 1
    assert step[1] == 1.5
    assert env.step_actions == [1]


def test_wrapper_calls_hooks_and_records_only_realized_transition() -> None:
    calls: list[tuple[str, object]] = []
    env = _FakeGymEnv()

    def state_key(observation: object, info: dict[str, object]) -> str:
        calls.append(("state", observation))
        return f"s:{observation}"

    def action_key(
        action: object,
        observation: object,
        info: dict[str, object],
    ) -> str:
        calls.append(("action", action))
        return f"a:{action}"

    def edge_labeler(
        source_key: object,
        action_key_value: object,
        target_key: object,
        info: dict[str, object],
    ) -> tuple[object, ...]:
        calls.append(("edge", (source_key, action_key_value, target_key)))
        return ("observed",)

    wrapper = StateCollapserGymWrapper(
        env,
        StateCollapserGymHooks(
            state_key=state_key,
            action_key=action_key,
            edge_labeler=edge_labeler,
        ),
    )

    wrapper.reset()
    assert wrapper.observed_edges == ()

    _, _, _, _, info = wrapper.step(1)

    assert len(wrapper.observed_edges) == 1
    assert wrapper.observed_edges[0].labels == ("observed",)
    assert info["state_collapser"]["observed_edge_count"] == 1
    assert ("action", 1) in calls
    assert ("edge", ("s:0", "a:1", "s:1")) in calls


def test_wrapper_propagates_action_mask_hook_result() -> None:
    env = _FakeGymEnv()
    wrapper = StateCollapserGymWrapper(
        env,
        StateCollapserGymHooks(
            state_key=lambda observation, info: observation,
            action_key=lambda action, observation, info: action,
            action_mask=lambda info, env: (True, False),
        ),
    )

    _, reset_info = wrapper.reset()
    _, _, _, _, step_info = wrapper.step(0)

    assert reset_info["action_mask"] == (True, False)
    assert step_info["action_mask"] == (True, False)
