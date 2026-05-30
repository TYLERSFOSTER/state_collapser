"""Minimal runnable tower-training loop for PlateSupportEnv."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import cast

from state_collapser.contract.policy import ContractionPolicy
from state_collapser.examples._shared_training import (
    run_shared_tower_training,
)
from state_collapser.examples._shared_training import (
    tower_state_key as shared_tower_state_key,
)
from state_collapser.examples.plate_support_env.env import ACTION_COUNT, PlateSupportEnv
from state_collapser.examples.plate_support_env.runtime import (
    PlateSupportEnvRuntime,
    PlateSupportExploitExploreRuntime,
)
from state_collapser.tower.control import FrozenLowerContext
from state_collapser.tower.control.learner import LearnerUpdateSummary
from state_collapser.tower.control.transition import ActiveTierTransition
from state_collapser.tower.partition.schema import ContractionSchema
from state_collapser.tower.snapshot import LiveRuntimeView


@dataclass(frozen=True, slots=True)
class TowerTrainingConfig:
    """Configuration for the plate-support tower-aware tabular loop."""

    episodes: int = 10
    max_steps_per_episode: int = 50
    alpha: float = 0.5
    gamma: float = 0.95
    epsilon: float = 0.2
    seed: int = 0


@dataclass(frozen=True, slots=True)
class TowerTrainingEpisodeSummary:
    """Summary of one plate-support tower-training episode."""

    episode_index: int
    total_reward: float
    steps: int
    success: bool


@dataclass(frozen=True, slots=True)
class TowerTrainingResult:
    """Structured result of a plate-support tower-training run."""

    config: TowerTrainingConfig
    q_table: dict[tuple[object | None, ...], dict[int, float]]
    episodes: tuple[TowerTrainingEpisodeSummary, ...]


@dataclass(frozen=True, slots=True)
class ExploitExploreTrainingConfig:
    """Configuration for the plate-support exploit/explore training path."""

    episodes: int = 5
    max_control_steps_per_episode: int = 20
    alpha: float = 0.5
    gamma: float = 0.95
    seed: int = 0


@dataclass(frozen=True, slots=True)
class ExploitExploreEpisodeSummary:
    """Summary of one plate-support exploit/explore training episode."""

    episode_index: int
    total_reward: float
    control_steps: int
    active_tiers_seen: tuple[int, ...]
    control_actions_seen: tuple[str, ...]
    success: bool


@dataclass(frozen=True, slots=True)
class ExploitExploreTrainingResult:
    """Structured result of a plate-support exploit/explore training run."""

    config: ExploitExploreTrainingConfig
    q_table: dict[tuple[int, object | None, int | str | None], dict[int, float]]
    episodes: tuple[ExploitExploreEpisodeSummary, ...]


@dataclass(slots=True)
class PlateSupportTierLearner:
    """Simple tabular learner for the exploit/explore reference controller.

    The learner is intentionally small and inspectable. It demonstrates the
    freeze/lift control surface with tabular Q-values keyed by active tier,
    tier-local state, and frozen-context version; it is not a package policy
    model family.
    """

    alpha: float = 0.5
    gamma: float = 0.95
    seed: int = 0
    q_table: dict[tuple[int, object | None, int | str | None], dict[int, float]] = field(
        default_factory=dict
    )
    replay: list[ActiveTierTransition] = field(default_factory=list)
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize deterministic exploration state after dataclass creation."""

        self._rng = random.Random(self.seed)

    def _key(
        self,
        *,
        tier_index: int,
        state: object | None,
        context_version: int | str | None,
    ) -> tuple[int, object | None, int | str | None]:
        return (tier_index, state, context_version)

    def _row(
        self,
        key: tuple[int, object | None, int | str | None],
    ) -> dict[int, float]:
        if key not in self.q_table:
            self.q_table[key] = {action: 0.0 for action in range(ACTION_COUNT)}
        return self.q_table[key]

    def behavior_action(self, state: object | None, *, mode: str) -> object:
        """Choose an action under the requested exploit or explore mode."""

        # The first release keeps action choice simple and inspectable.
        matching_rows = [key for key in self.q_table if key[1] == state]
        if mode == "explore" or not matching_rows:
            return self._rng.randrange(ACTION_COUNT)
        row = self.q_table[matching_rows[-1]]
        best_value = max(row.values())
        best_actions = [action for action, value in row.items() if value == best_value]
        return self._rng.choice(best_actions)

    def observe(
        self,
        transition: ActiveTierTransition,
        *,
        frozen_context: FrozenLowerContext,
    ) -> LearnerUpdateSummary:
        """Record a transition and apply the online tabular update."""

        del frozen_context
        self.replay.append(transition)
        td_error = self._update_from_transition(transition)
        return LearnerUpdateSummary(td_error=abs(td_error), success=transition.success)

    def should_train(self, event_index: int) -> bool:
        """Return whether the controller should request a replay-style train step."""

        return bool(self.replay) and event_index > 0 and event_index % 3 == 0

    def train(self, *, frozen_context: FrozenLowerContext) -> LearnerUpdateSummary:
        """Train from the latest replay item under a frozen lower-tier context."""

        if not self.replay:
            return LearnerUpdateSummary(td_error=0.0, success=True)
        transition = self.replay[-1]
        adjusted = ActiveTierTransition(
            tier_index=transition.tier_index,
            source_state=transition.source_state,
            action=transition.action,
            target_state=transition.target_state,
            aggregated_reward=transition.aggregated_reward,
            duration=transition.duration,
            context_version=frozen_context.version,
            representative_jump=transition.representative_jump,
            success=transition.success,
        )
        td_error = self._update_from_transition(adjusted)
        return LearnerUpdateSummary(td_error=abs(td_error), success=adjusted.success)

    def _update_from_transition(self, transition: ActiveTierTransition) -> float:
        key = self._key(
            tier_index=transition.tier_index,
            state=transition.source_state,
            context_version=transition.context_version,
        )
        next_key = self._key(
            tier_index=transition.tier_index,
            state=transition.target_state,
            context_version=transition.context_version,
        )
        row = self._row(key)
        next_row = self._row(next_key)
        action = cast(int, transition.action)
        td_target = transition.aggregated_reward + self.gamma * max(next_row.values())
        td_error = td_target - row[action]
        row[action] = row[action] + self.alpha * td_error
        return td_error


def tower_state_key(snapshot: LiveRuntimeView) -> tuple[object | None, ...]:
    """Return the tower-position key used by the plate-support tabular learner."""

    return shared_tower_state_key(snapshot)


def run_tower_training(
    *,
    env: PlateSupportEnv | None = None,
    contraction_policy: ContractionPolicy | None = None,
    contraction_schema: ContractionSchema | None = None,
    config: TowerTrainingConfig | None = None,
) -> TowerTrainingResult:
    """Run the plate-support tower-aware tabular training loop."""

    training_config = TowerTrainingConfig() if config is None else config
    runtime = PlateSupportEnvRuntime(
        env=PlateSupportEnv() if env is None else env,
        contraction_policy=contraction_policy,
        contraction_schema=contraction_schema,
    )
    shared_result = run_shared_tower_training(
        runtime=runtime,
        action_count=ACTION_COUNT,
        config=training_config,
    )
    episode_summaries = tuple(
        TowerTrainingEpisodeSummary(
            episode_index=episode.episode_index,
            total_reward=episode.total_reward,
            steps=episode.steps,
            success=episode.success,
        )
        for episode in shared_result.episodes
    )

    return TowerTrainingResult(
        config=training_config,
        q_table=shared_result.q_table,
        episodes=episode_summaries,
    )


def run_exploit_explore_training(
    *,
    env: PlateSupportEnv | None = None,
    contraction_policy: ContractionPolicy | None = None,
    config: ExploitExploreTrainingConfig | None = None,
) -> ExploitExploreTrainingResult:
    """Run the plate-support exploit/explore reference controller."""

    training_config = ExploitExploreTrainingConfig() if config is None else config
    learner = PlateSupportTierLearner(
        alpha=training_config.alpha,
        gamma=training_config.gamma,
        seed=training_config.seed,
    )
    runtime = PlateSupportExploitExploreRuntime(
        env=PlateSupportEnv() if env is None else env,
        contraction_policy=contraction_policy,
        learner=learner,
    )
    episode_summaries: list[ExploitExploreEpisodeSummary] = []

    for episode_index in range(training_config.episodes):
        reset_result = runtime.reset(seed=training_config.seed + episode_index)
        total_reward = 0.0
        control_steps = 0
        active_tiers_seen = [reset_result.active_tier_state.active_tier]
        control_actions_seen: list[str] = []
        success = False

        for _ in range(training_config.max_control_steps_per_episode):
            step_result = runtime.step()
            total_reward += step_result.reward
            control_steps += 1
            active_tiers_seen.append(step_result.active_tier_state.active_tier)
            control_actions_seen.append(step_result.control_action)
            if step_result.terminated:
                success = True
                break
            if step_result.truncated:
                break

        episode_summaries.append(
            ExploitExploreEpisodeSummary(
                episode_index=episode_index,
                total_reward=total_reward,
                control_steps=control_steps,
                active_tiers_seen=tuple(active_tiers_seen),
                control_actions_seen=tuple(control_actions_seen),
                success=success,
            )
        )

    return ExploitExploreTrainingResult(
        config=training_config,
        q_table=learner.q_table,
        episodes=tuple(episode_summaries),
    )


__all__ = [
    "ExploitExploreEpisodeSummary",
    "ExploitExploreTrainingConfig",
    "ExploitExploreTrainingResult",
    "PlateSupportTierLearner",
    "TowerTrainingConfig",
    "TowerTrainingEpisodeSummary",
    "TowerTrainingResult",
    "run_exploit_explore_training",
    "run_tower_training",
    "tower_state_key",
]
