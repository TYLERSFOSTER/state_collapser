"""Focused tests for first-scope learner and reference loops."""

from __future__ import annotations

from dataclasses import replace

from state_collapser.examples.rl_counterpoint_v3 import RlCounterpointEnv, RlCounterpointEnvRuntime
from state_collapser.training import (
    ActionSelectionInput,
    TabularQLearner,
    TrainingTransition,
    build_action_selection_input,
    run_reference_episode_loop,
    run_reference_online_loop,
)


def _input_with_key(
    action_input: ActionSelectionInput,
    key: tuple[object | None, ...],
    *,
    action_mask: tuple[bool, ...] | None = None,
) -> ActionSelectionInput:
    return replace(action_input, tower_position_key=key, action_mask=action_mask)


def test_tabular_q_learner_produces_decision_and_updates() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    reset_result = runtime.reset(seed=0)
    action_input = build_action_selection_input(
        observation=reset_result.observation,
        runtime_snapshot=reset_result.runtime_snapshot,
    )
    learner = TabularQLearner(action_count=runtime.env.action_count, seed=0)

    decision = learner.act(action_input)
    assert isinstance(decision.chosen_action, int)

    step_result = runtime.step(decision.chosen_action)
    next_input = build_action_selection_input(
        observation=step_result.observation,
        runtime_snapshot=step_result.runtime_snapshot,
    )
    learner.observe(
        transition=TrainingTransition(
            source_input=action_input,
            chosen_action=decision.chosen_action,
            reward=step_result.reward,
            target_input=next_input,
            terminated=step_result.terminated,
            truncated=step_result.truncated,
            bootstrap_allowed=not step_result.terminated,
            bootstrap_input=next_input,
            bootstrap_reason="test",
        )
    )
    summary = learner.update()
    assert summary.updated
    assert learner.q_table


def test_reference_online_loop_runs_end_to_end() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    learner = TabularQLearner(action_count=runtime.env.action_count, seed=0)

    result = run_reference_online_loop(
        runtime=runtime,
        learner=learner,
        episodes=2,
        max_steps_per_episode=4,
        seed=0,
    )

    assert len(result.episodes) == 2
    assert learner.q_table


def test_tabular_q_learner_raises_when_source_mask_has_no_legal_actions() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    reset_result = runtime.reset(seed=0)
    action_input = build_action_selection_input(
        observation=reset_result.observation,
        runtime_snapshot=reset_result.runtime_snapshot,
        action_mask=(False, False),
    )
    learner = TabularQLearner(action_count=2, seed=0)

    try:
        learner.act(action_input)
    except ValueError as exc:
        assert "no legal source actions" in str(exc)
    else:  # pragma: no cover - assertion clarity
        raise AssertionError("expected all-false mask to raise")


def test_tabular_q_learner_never_selects_masked_off_source_actions() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    reset_result = runtime.reset(seed=0)
    action_input = build_action_selection_input(
        observation=reset_result.observation,
        runtime_snapshot=reset_result.runtime_snapshot,
        action_mask=(False, True, False),
    )
    learner = TabularQLearner(action_count=3, epsilon=1.0, seed=0)

    decisions = tuple(learner.act(action_input).chosen_action for _ in range(20))

    assert decisions == (1,) * 20


def test_tabular_q_learner_terminal_transition_target_equals_reward() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    base_input = build_action_selection_input(
        observation=runtime.reset(seed=0).observation,
        runtime_snapshot=runtime.reset(seed=0).runtime_snapshot,
    )
    source_input = _input_with_key(base_input, ("source",))
    target_input = _input_with_key(base_input, ("target",))
    learner = TabularQLearner(action_count=2, alpha=1.0, gamma=0.5)

    learner.observe(
        TrainingTransition(
            source_input=source_input,
            chosen_action=0,
            reward=3.0,
            target_input=target_input,
            terminated=True,
            truncated=False,
            bootstrap_allowed=False,
            bootstrap_reason="terminated",
        )
    )
    summary = learner.update()

    assert learner.q_table[("source",)][0] == 3.0
    assert summary.diagnostics["bootstrap_allowed"] is False


def test_tabular_q_learner_truncation_can_bootstrap() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    reset_result = runtime.reset(seed=0)
    base_input = build_action_selection_input(
        observation=reset_result.observation,
        runtime_snapshot=reset_result.runtime_snapshot,
    )
    source_input = _input_with_key(base_input, ("source",))
    target_input = _input_with_key(base_input, ("target",))
    learner = TabularQLearner(action_count=2, alpha=1.0, gamma=0.5)
    learner.q_table[("target",)] = {0: 4.0, 1: 7.0}

    learner.observe(
        TrainingTransition(
            source_input=source_input,
            chosen_action=0,
            reward=1.0,
            target_input=target_input,
            terminated=False,
            truncated=True,
            bootstrap_allowed=True,
            bootstrap_input=target_input,
            bootstrap_reason="truncated_bootstrap",
        )
    )
    learner.update()

    assert learner.q_table[("source",)][0] == 4.5


def test_tabular_q_learner_truncation_can_disable_bootstrap() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    reset_result = runtime.reset(seed=0)
    base_input = build_action_selection_input(
        observation=reset_result.observation,
        runtime_snapshot=reset_result.runtime_snapshot,
    )
    source_input = _input_with_key(base_input, ("source",))
    target_input = _input_with_key(base_input, ("target",))
    learner = TabularQLearner(action_count=2, alpha=1.0, gamma=0.5)
    learner.q_table[("target",)] = {0: 4.0, 1: 7.0}

    learner.observe(
        TrainingTransition(
            source_input=source_input,
            chosen_action=0,
            reward=1.0,
            target_input=target_input,
            terminated=False,
            truncated=True,
            bootstrap_allowed=False,
            bootstrap_input=target_input,
            bootstrap_reason="truncated_no_bootstrap",
        )
    )
    learner.update()

    assert learner.q_table[("source",)][0] == 1.0


def test_tabular_q_learner_uses_manual_bootstrap_input_key() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    reset_result = runtime.reset(seed=0)
    base_input = build_action_selection_input(
        observation=reset_result.observation,
        runtime_snapshot=reset_result.runtime_snapshot,
    )
    source_input = _input_with_key(base_input, ("source",))
    target_input = _input_with_key(base_input, ("target",))
    bootstrap_input = _input_with_key(base_input, ("bootstrap",))
    learner = TabularQLearner(action_count=2, alpha=1.0, gamma=1.0)
    learner.q_table[("target",)] = {0: 100.0, 1: 100.0}
    learner.q_table[("bootstrap",)] = {0: 5.0, 1: 7.0}

    learner.observe(
        TrainingTransition(
            source_input=source_input,
            chosen_action=0,
            reward=1.0,
            target_input=target_input,
            terminated=False,
            truncated=False,
            bootstrap_allowed=True,
            bootstrap_input=bootstrap_input,
            bootstrap_reason="lift_override",
        )
    )
    summary = learner.update()

    assert learner.q_table[("source",)][0] == 8.0
    assert summary.diagnostics["bootstrap_key"] == ("bootstrap",)


def test_tabular_q_learner_ignores_masked_off_bootstrap_actions() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    reset_result = runtime.reset(seed=0)
    base_input = build_action_selection_input(
        observation=reset_result.observation,
        runtime_snapshot=reset_result.runtime_snapshot,
    )
    source_input = _input_with_key(base_input, ("source",))
    target_input = _input_with_key(base_input, ("target",), action_mask=(False, True, False))
    learner = TabularQLearner(action_count=3, alpha=1.0, gamma=1.0)
    learner.q_table[("target",)] = {0: 100.0, 1: 7.0, 2: 50.0}

    learner.observe(
        TrainingTransition(
            source_input=source_input,
            chosen_action=0,
            reward=1.0,
            target_input=target_input,
            terminated=False,
            truncated=False,
            bootstrap_allowed=True,
            bootstrap_input=target_input,
            bootstrap_reason="continuing",
        )
    )
    summary = learner.update()

    assert learner.q_table[("source",)][0] == 8.0
    assert summary.diagnostics["legal_target_action_count"] == 1


def test_tabular_q_learner_all_false_bootstrap_mask_yields_zero_bootstrap() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    reset_result = runtime.reset(seed=0)
    base_input = build_action_selection_input(
        observation=reset_result.observation,
        runtime_snapshot=reset_result.runtime_snapshot,
    )
    source_input = _input_with_key(base_input, ("source",))
    target_input = _input_with_key(base_input, ("target",), action_mask=(False, False))
    learner = TabularQLearner(action_count=2, alpha=1.0, gamma=1.0)
    learner.q_table[("target",)] = {0: 100.0, 1: 100.0}

    learner.observe(
        TrainingTransition(
            source_input=source_input,
            chosen_action=0,
            reward=2.0,
            target_input=target_input,
            terminated=False,
            truncated=False,
            bootstrap_allowed=True,
            bootstrap_input=target_input,
            bootstrap_reason="continuing",
        )
    )
    learner.update()

    assert learner.q_table[("source",)][0] == 2.0


def test_reference_episode_loop_runs_end_to_end() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    learner = TabularQLearner(action_count=runtime.env.action_count, seed=0)

    result = run_reference_episode_loop(
        runtime=runtime,
        learner=learner,
        episodes=2,
        max_steps_per_episode=4,
        seed=0,
    )

    assert len(result.episodes) == 2
    assert learner.q_table
