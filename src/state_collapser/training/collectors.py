"""Collector surfaces for training-facing code."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from state_collapser.tower.snapshot import LiveRuntimeView

from .continuation import (
    BootstrapSemantics,
    default_bootstrap_allowed,
    default_bootstrap_reason,
)
from .decisions import ActionDecision
from .inputs import ActionSelectionInput, build_action_selection_input
from .masks import action_is_legal, mask_from_info
from .transitions import TrainingTransition, summarize_runtime_snapshot


class RuntimeResetLike(Protocol):
    """Minimal reset result surface required by the collectors."""

    observation: object
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


class RuntimeStepLike(Protocol):
    """Minimal step result surface required by the collectors."""

    observation: object
    reward: float
    terminated: bool
    truncated: bool
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


class RuntimeLike(Protocol):
    """Runtime surface consumed by the first collectors."""

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, object] | None = None,
    ) -> Any:
        """Reset the runtime and return an object with observation/info/snapshot."""
        ...

    def step(self, action: int) -> Any:
        """Advance one action and return an object with step and snapshot data."""
        ...


@dataclass(frozen=True, slots=True)
class CollectedStep:
    """Structured result of one collected environment/runtime step."""

    decision: ActionDecision
    transition: TrainingTransition
    next_input: ActionSelectionInput
    reward: float
    terminated: bool
    truncated: bool
    info: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CollectedEpisode:
    """Structured result of one collected episode."""

    episode_index: int
    initial_input: ActionSelectionInput
    steps: tuple[CollectedStep, ...]
    total_reward: float
    steps_taken: int
    success: bool
    terminated: bool
    truncated: bool
    max_tower_depth: int
    final_input: ActionSelectionInput


@dataclass(slots=True)
class StepCollector:
    """Concrete first collector for one-step runtime collection."""

    runtime: RuntimeLike
    action_mask_factory: Callable[[ActionSelectionInput], tuple[bool, ...] | None] | None = None
    bootstrap_semantics: BootstrapSemantics = field(default_factory=BootstrapSemantics)

    def reset_episode(
        self,
        *,
        seed: int | None = None,
        options: dict[str, object] | None = None,
    ) -> ActionSelectionInput:
        """Reset the runtime and build the first action-selection input."""

        reset_result = self.runtime.reset(seed=seed, options=options)
        initial_input = build_action_selection_input(
            observation=reset_result.observation,
            runtime_snapshot=reset_result.runtime_snapshot,
            diagnostics=reset_result.info,
        )
        action_mask = self._build_action_mask(initial_input)
        if action_mask is not None:
            initial_input = build_action_selection_input(
                observation=initial_input.observation,
                runtime_snapshot=initial_input.runtime_snapshot,
                action_mask=action_mask,
                history_window=initial_input.history_window,
                active_tier_state=initial_input.active_tier_state,
                frozen_lower_context=initial_input.frozen_lower_context,
                stage_context=initial_input.stage_context,
                fiber_departure=initial_input.fiber_departure,
                diagnostics=initial_input.diagnostics,
            )
        return initial_input

    def collect_step(
        self,
        source_input: ActionSelectionInput,
        decision: ActionDecision,
    ) -> CollectedStep:
        """Collect one realized runtime step from a chosen action."""

        if not isinstance(decision.chosen_action, int):
            raise ValueError(
                "StepCollector requires ActionDecision.chosen_action to be an int "
                "for the current first-scope discrete runtime surface."
            )
        if not action_is_legal(decision.chosen_action, source_input.action_mask):
            raise ValueError(
                f"Chosen action is masked off for the current source input: "
                f"{decision.chosen_action}"
            )
        step_result = self.runtime.step(decision.chosen_action)
        next_input = build_action_selection_input(
            observation=step_result.observation,
            runtime_snapshot=step_result.runtime_snapshot,
            diagnostics=step_result.info,
        )
        action_mask = self._build_action_mask(next_input)
        if action_mask is not None:
            next_input = build_action_selection_input(
                observation=next_input.observation,
                runtime_snapshot=next_input.runtime_snapshot,
                action_mask=action_mask,
                history_window=next_input.history_window,
                active_tier_state=next_input.active_tier_state,
                frozen_lower_context=next_input.frozen_lower_context,
                stage_context=next_input.stage_context,
                fiber_departure=next_input.fiber_departure,
                diagnostics=next_input.diagnostics,
            )

        transition_diagnostics: dict[str, object] = dict(step_result.info)
        transition_diagnostics.update(decision.diagnostics)
        bootstrap_allowed = default_bootstrap_allowed(
            terminated=step_result.terminated,
            truncated=step_result.truncated,
            semantics=self.bootstrap_semantics,
        )
        bootstrap_reason = default_bootstrap_reason(
            terminated=step_result.terminated,
            truncated=step_result.truncated,
            semantics=self.bootstrap_semantics,
        )
        transition = TrainingTransition(
            source_input=source_input,
            chosen_action=decision.chosen_action,
            reward=step_result.reward,
            target_input=next_input,
            terminated=step_result.terminated,
            truncated=step_result.truncated,
            bootstrap_allowed=bootstrap_allowed,
            diagnostics=transition_diagnostics,
            bootstrap_input=next_input,
            bootstrap_reason=bootstrap_reason,
            runtime_snapshot_summary=summarize_runtime_snapshot(step_result.runtime_snapshot),
            tower_position_key=next_input.tower_position_key,
            active_tier=step_result.runtime_snapshot.active_control_tier,
        )
        return CollectedStep(
            decision=decision,
            transition=transition,
            next_input=next_input,
            reward=step_result.reward,
            terminated=step_result.terminated,
            truncated=step_result.truncated,
            info=step_result.info,
        )

    def _build_action_mask(
        self,
        action_input: ActionSelectionInput,
    ) -> tuple[bool, ...] | None:
        if self.action_mask_factory is not None:
            return self.action_mask_factory(action_input)
        return mask_from_info(action_input.diagnostics)


@dataclass(slots=True)
class EpisodeCollector:
    """Concrete first collector for episode-level accumulation."""

    step_collector: StepCollector

    def collect_episode(
        self,
        *,
        decision_fn: Callable[[ActionSelectionInput], ActionDecision],
        max_steps: int,
        episode_index: int,
        seed: int | None = None,
        on_step: Callable[[CollectedStep], None] | None = None,
    ) -> CollectedEpisode:
        """Collect one episode using a caller-supplied decision function."""

        initial_input = self.step_collector.reset_episode(seed=seed)
        current_input = initial_input
        collected_steps: list[CollectedStep] = []
        total_reward = 0.0
        max_tower_depth = len(initial_input.runtime_snapshot.current_position_at_every_tier)

        for _ in range(max_steps):
            decision = decision_fn(current_input)
            collected_step = self.step_collector.collect_step(current_input, decision)
            collected_steps.append(collected_step)
            total_reward += collected_step.reward
            if collected_step.next_input.runtime_snapshot.current_position_at_every_tier:
                max_tower_depth = max(
                    max_tower_depth,
                    len(
                        collected_step.next_input.runtime_snapshot.current_position_at_every_tier
                    ),
                )
            if on_step is not None:
                on_step(collected_step)
            current_input = collected_step.next_input
            if collected_step.terminated or collected_step.truncated:
                break

        terminated = bool(collected_steps and collected_steps[-1].terminated)
        truncated = bool(collected_steps and collected_steps[-1].truncated)
        return CollectedEpisode(
            episode_index=episode_index,
            initial_input=initial_input,
            steps=tuple(collected_steps),
            total_reward=total_reward,
            steps_taken=len(collected_steps),
            success=terminated,
            terminated=terminated,
            truncated=truncated,
            max_tower_depth=max_tower_depth,
            final_input=current_input,
        )


__all__ = [
    "CollectedEpisode",
    "CollectedStep",
    "EpisodeCollector",
    "RuntimeLike",
    "RuntimeResetLike",
    "RuntimeStepLike",
    "StepCollector",
]
