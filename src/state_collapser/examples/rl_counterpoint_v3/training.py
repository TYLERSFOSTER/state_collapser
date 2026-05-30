"""Minimal runnable tower-training loop for RlCounterpointEnv."""

from __future__ import annotations

from dataclasses import dataclass

from state_collapser.contract.policy import ContractionPolicy
from state_collapser.examples.rl_counterpoint_v3.env import RlCounterpointEnv
from state_collapser.examples.rl_counterpoint_v3.runtime import RlCounterpointEnvRuntime
from state_collapser.tower.partition.schema import ContractionSchema
from state_collapser.tower.snapshot import LiveRuntimeView
from state_collapser.training import (
    TabularQLearner,
    run_reference_online_loop,
    tower_position_key,
)


@dataclass(frozen=True, slots=True)
class TowerTrainingConfig:
    """Configuration for the counterpoint tower-aware tabular loop."""

    episodes: int = 10
    max_steps_per_episode: int = 16
    alpha: float = 0.5
    gamma: float = 0.95
    epsilon: float = 0.2
    seed: int = 0


@dataclass(frozen=True, slots=True)
class TowerTrainingEpisodeSummary:
    """Summary of one counterpoint tower-training episode."""

    episode_index: int
    total_reward: float
    steps: int
    success: bool


@dataclass(frozen=True, slots=True)
class TowerTrainingResult:
    """Structured result of a counterpoint tower-training run."""

    config: TowerTrainingConfig
    q_table: dict[tuple[object | None, ...], dict[int, float]]
    episodes: tuple[TowerTrainingEpisodeSummary, ...]


def tower_state_key(snapshot: LiveRuntimeView) -> tuple[object | None, ...]:
    """Return the tower-position key used by the counterpoint learner."""

    return tower_position_key(snapshot)


def run_tower_training(
    *,
    env: RlCounterpointEnv | None = None,
    contraction_policy: ContractionPolicy | None = None,
    contraction_schema: ContractionSchema | None = None,
    config: TowerTrainingConfig | None = None,
) -> TowerTrainingResult:
    """Run the counterpoint tower-aware tabular training loop."""

    training_config = TowerTrainingConfig() if config is None else config
    runtime = RlCounterpointEnvRuntime(
        env=RlCounterpointEnv() if env is None else env,
        contraction_policy=contraction_policy,
        contraction_schema=contraction_schema,
    )
    learner = TabularQLearner(
        action_count=runtime.env.action_count,
        alpha=training_config.alpha,
        gamma=training_config.gamma,
        epsilon=training_config.epsilon,
        seed=training_config.seed,
    )
    loop_result = run_reference_online_loop(
        runtime=runtime,
        learner=learner,
        episodes=training_config.episodes,
        max_steps_per_episode=training_config.max_steps_per_episode,
        seed=training_config.seed,
    )
    episode_summaries = tuple(
        TowerTrainingEpisodeSummary(
            episode_index=summary.episode_index,
            total_reward=summary.total_reward,
            steps=summary.steps,
            success=summary.success,
        )
        for summary in loop_result.episodes
    )

    return TowerTrainingResult(
        config=training_config,
        q_table=learner.q_table,
        episodes=episode_summaries,
    )


__all__ = [
    "TowerTrainingConfig",
    "TowerTrainingEpisodeSummary",
    "TowerTrainingResult",
    "run_tower_training",
    "tower_state_key",
]
