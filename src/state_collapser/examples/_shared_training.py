"""Shared example training helpers built on package training surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from state_collapser.tower.snapshot import LiveRuntimeView
from state_collapser.training import TabularQLearner, run_reference_online_loop
from state_collapser.training.collectors import RuntimeLike


class TowerTrainingConfigLike(Protocol):
    """Config attributes required by the shared example training loop."""

    @property
    def episodes(self) -> int: ...

    @property
    def max_steps_per_episode(self) -> int: ...

    @property
    def alpha(self) -> float: ...

    @property
    def gamma(self) -> float: ...

    @property
    def epsilon(self) -> float: ...

    @property
    def seed(self) -> int: ...


@dataclass(frozen=True, slots=True)
class SharedTowerTrainingEpisodeSummary:
    """Example-independent summary of one tower-training episode."""

    episode_index: int
    total_reward: float
    steps: int
    success: bool


@dataclass(frozen=True, slots=True)
class SharedTowerTrainingResult:
    """Example-independent result of a tower-training run."""

    q_table: dict[tuple[object | None, ...], dict[int, float]]
    episodes: tuple[SharedTowerTrainingEpisodeSummary, ...]


def tower_state_key(snapshot: LiveRuntimeView) -> tuple[object | None, ...]:
    """Return the tower-position key used by the shared tabular learner."""

    return tuple(snapshot.current_position_at_every_tier)


def run_shared_tower_training(
    *,
    runtime: RuntimeLike,
    action_count: int,
    config: TowerTrainingConfigLike,
) -> SharedTowerTrainingResult:
    """Run a tower-aware tabular loop through the package learner surfaces."""

    learner = TabularQLearner(
        action_count=action_count,
        alpha=config.alpha,
        gamma=config.gamma,
        epsilon=config.epsilon,
        seed=config.seed,
    )
    loop_result = run_reference_online_loop(
        runtime=runtime,
        learner=learner,
        episodes=config.episodes,
        max_steps_per_episode=config.max_steps_per_episode,
        seed=config.seed,
    )
    return SharedTowerTrainingResult(
        q_table=learner.q_table,
        episodes=tuple(
            SharedTowerTrainingEpisodeSummary(
                episode_index=episode.episode_index,
                total_reward=episode.total_reward,
                steps=episode.steps,
                success=episode.success,
            )
            for episode in loop_result.episodes
        ),
    )


__all__ = [
    "SharedTowerTrainingEpisodeSummary",
    "SharedTowerTrainingResult",
    "TowerTrainingConfigLike",
    "run_shared_tower_training",
    "tower_state_key",
]
