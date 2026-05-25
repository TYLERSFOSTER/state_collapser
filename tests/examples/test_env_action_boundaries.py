"""Shared Gymnasium action-boundary checks for example environments."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from state_collapser.examples.articulated_loop_env import (
    ACTION_COUNT as ARTICULATED_LOOP_ACTION_COUNT,
)
from state_collapser.examples.articulated_loop_env import ArticulatedLoopEnv
from state_collapser.examples.cable_parallel_env import (
    ACTION_COUNT as CABLE_PARALLEL_ACTION_COUNT,
)
from state_collapser.examples.cable_parallel_env import CableParallelEnv
from state_collapser.examples.dual_arm_manipulation_env import (
    ACTION_COUNT as DUAL_ARM_ACTION_COUNT,
)
from state_collapser.examples.dual_arm_manipulation_env import DualArmManipulationEnv
from state_collapser.examples.parallelogram_singularity_env import (
    ACTION_COUNT as PARALLELOGRAM_ACTION_COUNT,
)
from state_collapser.examples.parallelogram_singularity_env import (
    ParallelogramSingularityEnv,
)
from state_collapser.examples.plate_support_env import (
    ACTION_COUNT as PLATE_SUPPORT_ACTION_COUNT,
)
from state_collapser.examples.plate_support_env import PlateSupportEnv
from state_collapser.examples.rl_counterpoint_v3 import (
    ACTION_COUNT as RL_COUNTERPOINT_V3_ACTION_COUNT,
)
from state_collapser.examples.rl_counterpoint_v3 import RlCounterpointEnv


@pytest.mark.parametrize(
    ("env_factory", "action_count"),
    (
        (ArticulatedLoopEnv, ARTICULATED_LOOP_ACTION_COUNT),
        (CableParallelEnv, CABLE_PARALLEL_ACTION_COUNT),
        (DualArmManipulationEnv, DUAL_ARM_ACTION_COUNT),
        (ParallelogramSingularityEnv, PARALLELOGRAM_ACTION_COUNT),
        (PlateSupportEnv, PLATE_SUPPORT_ACTION_COUNT),
        (RlCounterpointEnv, RL_COUNTERPOINT_V3_ACTION_COUNT),
    ),
)
@pytest.mark.parametrize("invalid_action", (-1, "ACTION_COUNT", 1.9, True, False))
def test_example_envs_reject_invalid_actions_before_coercion(
    env_factory: Callable[[], object],
    action_count: int,
    invalid_action: object,
) -> None:
    env = env_factory()
    if invalid_action == "ACTION_COUNT":
        invalid_action = action_count

    with pytest.raises(ValueError):
        env.step(invalid_action)  # type: ignore[attr-defined]
