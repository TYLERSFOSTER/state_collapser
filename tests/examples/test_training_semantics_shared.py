"""Tests for shared example training semantics."""

from __future__ import annotations

from dataclasses import dataclass

from state_collapser.examples._shared_training import run_shared_tower_training
from state_collapser.examples.rl_counterpoint_v3 import RlCounterpointEnv, RlCounterpointEnvRuntime
from state_collapser.tower.snapshot import LiveRuntimeView


@dataclass(frozen=True, slots=True)
class _Config:
    episodes: int = 1
    max_steps_per_episode: int = 2
    alpha: float = 1.0
    gamma: float = 1.0
    epsilon: float = 0.0
    seed: int = 0


@dataclass(frozen=True, slots=True)
class _ResetResult:
    observation: object
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


@dataclass(frozen=True, slots=True)
class _StepResult:
    observation: object
    reward: float
    terminated: bool
    truncated: bool
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


class _TwoStepTruncatingRuntime:
    def __init__(self) -> None:
        base_runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
        base_reset = base_runtime.reset(seed=0)
        self._observation = base_reset.observation
        self._snapshot = base_reset.runtime_snapshot
        self.step_index = 0

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, object] | None = None,
    ) -> _ResetResult:
        del seed, options
        self.step_index = 0
        return _ResetResult(
            observation=self._observation,
            info={},
            runtime_snapshot=self._snapshot,
        )

    def step(self, action: int) -> _StepResult:
        del action
        self.step_index += 1
        return _StepResult(
            observation=self._observation,
            reward=10.0 if self.step_index == 1 else 1.0,
            terminated=False,
            truncated=self.step_index == 2,
            info={},
            runtime_snapshot=self._snapshot,
        )


def test_shared_training_uses_tabular_continuation_semantics_on_truncation() -> None:
    result = run_shared_tower_training(
        runtime=_TwoStepTruncatingRuntime(),
        action_count=1,
        config=_Config(),
    )

    row = next(iter(result.q_table.values()))
    assert row[0] == 11.0
    assert result.episodes[0].steps == 2
