"""Reference loop surfaces for first-scope training work."""

from __future__ import annotations

from dataclasses import dataclass

from .collectors import CollectedStep, EpisodeCollector, RuntimeLike, StepCollector
from .learners import Learner
from .metrics import EpisodeMetrics, MetricsHook, TrainingMetrics


@dataclass(frozen=True, slots=True)
class ReferenceLoopResult:
    """Structured output of one reference loop run."""

    episodes: tuple[EpisodeMetrics, ...]


def run_reference_online_loop(
    *,
    runtime: RuntimeLike,
    learner: Learner,
    episodes: int,
    max_steps_per_episode: int,
    seed: int = 0,
    metrics_hook: MetricsHook | None = None,
) -> ReferenceLoopResult:
    """Run a minimal online loop over the first training surfaces."""

    step_collector = StepCollector(runtime=runtime)
    resolved_metrics = metrics_hook or TrainingMetrics()
    episode_summaries: list[EpisodeMetrics] = []

    for episode_index in range(episodes):
        current_input = step_collector.reset_episode(seed=seed + episode_index)
        total_reward = 0.0
        steps_taken = 0
        success = False
        max_tower_depth = len(current_input.runtime_snapshot.current_position_at_every_tier)

        for _ in range(max_steps_per_episode):
            decision = learner.act(current_input, mode="train")
            collected_step = step_collector.collect_step(current_input, decision)
            learner.observe(collected_step.transition)
            learner.update()
            total_reward += collected_step.reward
            steps_taken += 1
            current_input = collected_step.next_input
            max_tower_depth = max(
                max_tower_depth,
                len(current_input.runtime_snapshot.current_position_at_every_tier),
            )
            if collected_step.terminated:
                success = True
                break
            if collected_step.truncated:
                break

        summary = EpisodeMetrics(
            episode_index=episode_index,
            total_reward=total_reward,
            steps=steps_taken,
            success=success,
            max_tower_depth=max_tower_depth,
        )
        resolved_metrics.on_episode_end(summary)
        episode_summaries.append(summary)

    return ReferenceLoopResult(episodes=tuple(episode_summaries))


def run_reference_episode_loop(
    *,
    runtime: RuntimeLike,
    learner: Learner,
    episodes: int,
    max_steps_per_episode: int,
    seed: int = 0,
    metrics_hook: MetricsHook | None = None,
) -> ReferenceLoopResult:
    """Run a minimal episode-collector-driven loop over the new surfaces."""

    step_collector = StepCollector(runtime=runtime)
    episode_collector = EpisodeCollector(step_collector=step_collector)
    resolved_metrics = metrics_hook or TrainingMetrics()
    episode_summaries: list[EpisodeMetrics] = []

    def on_step(collected_step: CollectedStep) -> None:
        learner.observe(collected_step.transition)
        learner.update()

    for episode_index in range(episodes):
        collected_episode = episode_collector.collect_episode(
            decision_fn=lambda action_input: learner.act(action_input, mode="train"),
            max_steps=max_steps_per_episode,
            episode_index=episode_index,
            seed=seed + episode_index,
            on_step=on_step,
        )
        summary = EpisodeMetrics(
            episode_index=episode_index,
            total_reward=collected_episode.total_reward,
            steps=collected_episode.steps_taken,
            success=collected_episode.success,
            max_tower_depth=collected_episode.max_tower_depth,
        )
        resolved_metrics.on_episode_end(summary)
        episode_summaries.append(summary)

    return ReferenceLoopResult(episodes=tuple(episode_summaries))


__all__ = [
    "ReferenceLoopResult",
    "run_reference_episode_loop",
    "run_reference_online_loop",
]
