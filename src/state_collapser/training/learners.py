"""Learner surfaces for training-facing code."""

from __future__ import annotations

import random
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Protocol, cast, runtime_checkable

from .decisions import ActionDecision
from .inputs import ActionSelectionInput
from .masks import legal_actions
from .transitions import TrainingTransition


@dataclass(frozen=True, slots=True)
class LearnerUpdateSummary:
    """Summary of one generic learner update."""

    updated: bool
    td_error: float | None = None
    diagnostics: Mapping[str, object] = field(default_factory=dict)


@runtime_checkable
class Learner(Protocol):
    """General first-scope learner surface."""

    def act(self, action_input: ActionSelectionInput, *, mode: str = "train") -> ActionDecision:
        """Produce an action-decision object for the current input."""

    def observe(self, transition: TrainingTransition) -> None:
        """Record one realized transition."""

    def update(self) -> LearnerUpdateSummary:
        """Run one learner update step."""


def default_tower_position_key(action_input: ActionSelectionInput) -> tuple[object | None, ...]:
    """Return the default tabular key for the first reference learner."""

    return action_input.tower_position_key


@dataclass(slots=True)
class TabularQLearner:
    """Minimal non-canonical reference learner for the first package slice."""

    action_count: int
    alpha: float = 0.5
    gamma: float = 0.95
    epsilon: float = 0.2
    seed: int = 0
    key_fn: Callable[[ActionSelectionInput], tuple[object | None, ...]] = (
        default_tower_position_key
    )
    q_table: dict[tuple[object | None, ...], dict[int, float]] = field(default_factory=dict)
    replay: list[TrainingTransition] = field(default_factory=list)
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def act(
        self,
        action_input: ActionSelectionInput,
        *,
        mode: str = "train",
    ) -> ActionDecision:
        """Choose an action using a minimal epsilon-greedy tabular rule."""

        state_key = self.key_fn(action_input)
        row = self._ensure_q_row(state_key)

        candidate_actions = legal_actions(action_input.action_mask, self.action_count)
        if not candidate_actions:
            raise ValueError("TabularQLearner cannot act with no legal source actions.")

        if mode != "eval" and self._rng.random() < self.epsilon:
            chosen_action = self._rng.choice(candidate_actions)
        else:
            best_value = max(row[action] for action in candidate_actions)
            best_actions = [
                action for action in candidate_actions if row[action] == best_value
            ]
            chosen_action = self._rng.choice(best_actions)

        action_values = {
            action: row[action] for action in candidate_actions
        }
        return ActionDecision(
            chosen_action=chosen_action,
            action_values=cast(Mapping[object, float], action_values),
            diagnostics={"state_key": state_key, "mode": mode},
        )

    def observe(self, transition: TrainingTransition) -> None:
        """Record one realized transition for later update."""

        self.replay.append(transition)

    def update(self) -> LearnerUpdateSummary:
        """Run one minimal Q-learning-style update from the last observed transition."""

        if not self.replay:
            return LearnerUpdateSummary(updated=False, td_error=None)

        transition = self.replay[-1]
        if not isinstance(transition.chosen_action, int):
            raise ValueError(
                "TabularQLearner requires integer actions in first-scope reference use."
            )

        source_key = self.key_fn(transition.source_input)
        target_key = self.key_fn(transition.target_input)
        bootstrap_input = (
            transition.target_input
            if transition.bootstrap_input is None
            else transition.bootstrap_input
        )
        bootstrap_key = self.key_fn(bootstrap_input)
        row = self._ensure_q_row(source_key)
        legal_bootstrap_actions = legal_actions(bootstrap_input.action_mask, self.action_count)
        if transition.bootstrap_allowed and legal_bootstrap_actions:
            next_row = self._ensure_q_row(bootstrap_key)
            bootstrap = max(next_row[action] for action in legal_bootstrap_actions)
        else:
            bootstrap = 0.0
        td_target = transition.reward + self.gamma * bootstrap
        td_error = td_target - row[transition.chosen_action]
        row[transition.chosen_action] = (
            row[transition.chosen_action] + self.alpha * td_error
        )
        return LearnerUpdateSummary(
            updated=True,
            td_error=td_error,
            diagnostics={
                "source_key": source_key,
                "target_key": target_key,
                "bootstrap_allowed": transition.bootstrap_allowed,
                "bootstrap_key": bootstrap_key,
                "legal_target_action_count": len(legal_bootstrap_actions),
                "bootstrap_reason": transition.bootstrap_reason,
            },
        )

    def _ensure_q_row(
        self,
        key: tuple[object | None, ...],
    ) -> dict[int, float]:
        if key not in self.q_table:
            self.q_table[key] = {action: 0.0 for action in range(self.action_count)}
        return self.q_table[key]


__all__ = [
    "Learner",
    "LearnerUpdateSummary",
    "TabularQLearner",
    "default_tower_position_key",
]
