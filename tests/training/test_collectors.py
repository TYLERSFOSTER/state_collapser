"""Focused tests for first-scope training collectors."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from state_collapser.examples.rl_counterpoint_v3 import RlCounterpointEnv, RlCounterpointEnvRuntime
from state_collapser.tower.snapshot import LiveRuntimeView
from state_collapser.training import (
    ActionDecision,
    BootstrapSemantics,
    EpisodeCollector,
    StepCollector,
)


@dataclass(frozen=True, slots=True)
class _FakeResetResult:
    observation: object
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


@dataclass(frozen=True, slots=True)
class _FakeStepResult:
    observation: object
    reward: float
    terminated: bool
    truncated: bool
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


class _MaskRuntime:
    def __init__(
        self,
        *,
        reset_info: dict[str, object] | None = None,
        step_info: dict[str, object] | None = None,
        step_terminated: bool = False,
        step_truncated: bool = False,
    ) -> None:
        self._base_runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
        self._base_reset = self._base_runtime.reset(seed=0)
        self.reset_info = {} if reset_info is None else reset_info
        self.step_info = {} if step_info is None else step_info
        self.step_terminated = step_terminated
        self.step_truncated = step_truncated
        self.step_calls = 0

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, object] | None = None,
    ) -> _FakeResetResult:
        del seed, options
        return _FakeResetResult(
            observation=self._base_reset.observation,
            info=self.reset_info,
            runtime_snapshot=self._base_reset.runtime_snapshot,
        )

    def step(self, action: int) -> _FakeStepResult:
        del action
        self.step_calls += 1
        return _FakeStepResult(
            observation=self._base_reset.observation,
            reward=1.0,
            terminated=self.step_terminated,
            truncated=self.step_truncated,
            info=self.step_info,
            runtime_snapshot=self._base_reset.runtime_snapshot,
        )


def _first_legal_action(mask: tuple[bool, ...] | None) -> int:
    if mask is None:
        return 0
    return next(action for action, allowed in enumerate(mask) if allowed)


def test_step_collector_builds_transition_from_runtime_step() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    collector = StepCollector(runtime=runtime)
    initial_input = collector.reset_episode(seed=0)
    action = _first_legal_action(initial_input.action_mask)

    collected_step = collector.collect_step(
        initial_input,
        ActionDecision(chosen_action=action),
    )

    assert collected_step.transition.source_input == initial_input
    assert collected_step.transition.reward == collected_step.reward
    assert collected_step.transition.target_input == collected_step.next_input
    assert collected_step.transition.runtime_snapshot_summary is not None


def test_episode_collector_accumulates_episode_summary() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    collector = EpisodeCollector(step_collector=StepCollector(runtime=runtime))

    episode = collector.collect_episode(
        decision_fn=lambda action_input: ActionDecision(
            chosen_action=_first_legal_action(action_input.action_mask)
        ),
        max_steps=4,
        episode_index=0,
        seed=0,
    )

    assert episode.steps_taken <= 4
    assert episode.total_reward == sum(step.reward for step in episode.steps)
    assert episode.max_tower_depth >= 1


def test_step_collector_reset_extracts_info_action_mask() -> None:
    runtime = _MaskRuntime(reset_info={"action_mask": [1, 0, True]})
    collector = StepCollector(runtime=runtime)

    initial_input = collector.reset_episode()

    assert initial_input.action_mask == (True, False, True)


def test_step_collector_mask_factory_overrides_reset_info_action_mask() -> None:
    runtime = _MaskRuntime(reset_info={"action_mask": [1, 0, True]})
    collector = StepCollector(
        runtime=runtime,
        action_mask_factory=lambda action_input: (False, True),
    )

    initial_input = collector.reset_episode()

    assert initial_input.action_mask == (False, True)


def test_step_collector_rejects_masked_off_action_before_runtime_step() -> None:
    runtime = _MaskRuntime(reset_info={"action_mask": [True, False]})
    collector = StepCollector(runtime=runtime)
    initial_input = collector.reset_episode()

    with pytest.raises(ValueError):
        collector.collect_step(initial_input, ActionDecision(chosen_action=1))

    assert runtime.step_calls == 0


def test_step_collector_step_extracts_target_info_action_mask() -> None:
    runtime = _MaskRuntime(step_info={"action_mask": [0, 1]})
    collector = StepCollector(runtime=runtime)
    initial_input = collector.reset_episode()

    collected_step = collector.collect_step(initial_input, ActionDecision(chosen_action=0))

    assert collected_step.next_input.action_mask == (False, True)


def test_step_collector_mask_factory_overrides_target_info_action_mask() -> None:
    runtime = _MaskRuntime(step_info={"action_mask": [0, 1]})
    collector = StepCollector(
        runtime=runtime,
        action_mask_factory=lambda action_input: (True, False, True),
    )
    initial_input = collector.reset_episode()

    collected_step = collector.collect_step(initial_input, ActionDecision(chosen_action=0))

    assert collected_step.next_input.action_mask == (True, False, True)


def test_step_collector_terminal_transition_disables_bootstrap() -> None:
    runtime = _MaskRuntime(step_terminated=True)
    collector = StepCollector(runtime=runtime)
    initial_input = collector.reset_episode()

    collected_step = collector.collect_step(initial_input, ActionDecision(chosen_action=0))

    assert not collected_step.transition.bootstrap_allowed
    assert collected_step.transition.bootstrap_reason == "terminated"
    assert collected_step.transition.bootstrap_input == collected_step.next_input


def test_step_collector_truncation_bootstraps_by_default() -> None:
    runtime = _MaskRuntime(step_truncated=True)
    collector = StepCollector(runtime=runtime)
    initial_input = collector.reset_episode()

    collected_step = collector.collect_step(initial_input, ActionDecision(chosen_action=0))

    assert collected_step.transition.bootstrap_allowed
    assert collected_step.transition.bootstrap_reason == "truncated_bootstrap"
    assert collected_step.transition.bootstrap_input == collected_step.next_input


def test_step_collector_truncation_can_disable_bootstrap() -> None:
    runtime = _MaskRuntime(step_truncated=True)
    collector = StepCollector(
        runtime=runtime,
        bootstrap_semantics=BootstrapSemantics(bootstrap_on_truncation=False),
    )
    initial_input = collector.reset_episode()

    collected_step = collector.collect_step(initial_input, ActionDecision(chosen_action=0))

    assert not collected_step.transition.bootstrap_allowed
    assert collected_step.transition.bootstrap_reason == "truncated_no_bootstrap"


def test_step_collector_continuing_transition_allows_bootstrap() -> None:
    runtime = _MaskRuntime()
    collector = StepCollector(runtime=runtime)
    initial_input = collector.reset_episode()

    collected_step = collector.collect_step(initial_input, ActionDecision(chosen_action=0))

    assert collected_step.transition.bootstrap_allowed
    assert collected_step.transition.bootstrap_reason == "continuing"
