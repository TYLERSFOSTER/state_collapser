"""Minimal runnable tower-training loop for ParallelogramSingularityEnv."""

from __future__ import annotations

from dataclasses import dataclass

from state_collapser.contract.policy import ContractionPolicy
from state_collapser.examples._shared_training import (
    run_shared_tower_training,
)
from state_collapser.examples._shared_training import (
    tower_state_key as shared_tower_state_key,
)
from state_collapser.examples.parallelogram_singularity_env.env import (
    ACTION_COUNT,
    ParallelogramSingularityEnv,
)
from state_collapser.examples.parallelogram_singularity_env.runtime import (
    ParallelogramSingularityEnvRuntime,
)
from state_collapser.tower.partition.schema import ContractionSchema
from state_collapser.tower.snapshot import LiveRuntimeView


@dataclass(frozen=True, slots=True)
class TowerTrainingConfig:
    episodes: int = 10
    max_steps_per_episode: int = 24
    alpha: float = 0.5
    gamma: float = 0.95
    epsilon: float = 0.2
    seed: int = 0


@dataclass(frozen=True, slots=True)
class TowerTrainingEpisodeSummary:
    episode_index: int
    total_reward: float
    steps: int
    success: bool


@dataclass(frozen=True, slots=True)
class TowerTrainingResult:
    config: TowerTrainingConfig
    q_table: dict[tuple[object | None, ...], dict[int, float]]
    episodes: tuple[TowerTrainingEpisodeSummary, ...]


def tower_state_key(snapshot: LiveRuntimeView) -> tuple[object | None, ...]:
    return shared_tower_state_key(snapshot)


def run_tower_training(
    *,
    env: ParallelogramSingularityEnv | None = None,
    contraction_policy: ContractionPolicy | None = None,
    contraction_schema: ContractionSchema | None = None,
    config: TowerTrainingConfig | None = None,
) -> TowerTrainingResult:
    training_config = TowerTrainingConfig() if config is None else config
    runtime = ParallelogramSingularityEnvRuntime(
        env=ParallelogramSingularityEnv() if env is None else env,
        contraction_policy=contraction_policy,
        contraction_schema=contraction_schema,
    )
    shared_result = run_shared_tower_training(
        runtime=runtime,
        action_count=ACTION_COUNT,
        config=training_config,
    )
    return TowerTrainingResult(
        config=training_config,
        q_table=shared_result.q_table,
        episodes=tuple(
            TowerTrainingEpisodeSummary(
                episode_index=episode.episode_index,
                total_reward=episode.total_reward,
                steps=episode.steps,
                success=episode.success,
            )
            for episode in shared_result.episodes
        ),
    )


__all__ = [
    "TowerTrainingConfig",
    "TowerTrainingEpisodeSummary",
    "TowerTrainingResult",
    "run_tower_training",
    "tower_state_key",
]
