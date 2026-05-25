from __future__ import annotations

from collections.abc import Callable

from state_collapser.examples.articulated_loop_env import (
    ArticulatedLoopEnv,
)
from state_collapser.examples.articulated_loop_env import (
    TowerTrainingConfig as ArticulatedLoopTrainingConfig,
)
from state_collapser.examples.articulated_loop_env import (
    run_tower_training as run_articulated_loop_training,
)
from state_collapser.examples.cable_parallel_env import (
    CableParallelEnv,
)
from state_collapser.examples.cable_parallel_env import (
    TowerTrainingConfig as CableParallelTrainingConfig,
)
from state_collapser.examples.cable_parallel_env import (
    run_tower_training as run_cable_parallel_training,
)
from state_collapser.examples.dual_arm_manipulation_env import (
    DualArmManipulationEnv,
)
from state_collapser.examples.dual_arm_manipulation_env import (
    TowerTrainingConfig as DualArmTrainingConfig,
)
from state_collapser.examples.dual_arm_manipulation_env import (
    run_tower_training as run_dual_arm_training,
)
from state_collapser.examples.parallelogram_singularity_env import (
    ParallelogramSingularityEnv,
)
from state_collapser.examples.parallelogram_singularity_env import (
    TowerTrainingConfig as ParallelogramTrainingConfig,
)
from state_collapser.examples.parallelogram_singularity_env import (
    run_tower_training as run_parallelogram_training,
)
from state_collapser.examples.plate_support_env import (
    PlateSupportEnv,
)
from state_collapser.examples.plate_support_env import (
    TowerTrainingConfig as PlateSupportTrainingConfig,
)
from state_collapser.examples.plate_support_env import (
    run_tower_training as run_plate_support_training,
)
from state_collapser.examples.rl_counterpoint_v3 import (
    RlCounterpointEnv,
)
from state_collapser.examples.rl_counterpoint_v3 import (
    TowerTrainingConfig as RlCounterpointTrainingConfig,
)
from state_collapser.examples.rl_counterpoint_v3 import (
    run_tower_training as run_rl_counterpoint_training,
)
from state_collapser.tower.partition.schema import NoContractionSchema


def _key_lengths(q_table: dict[tuple[object | None, ...], dict[int, float]]) -> set[int]:
    return {len(key) for key in q_table}


def test_training_schema_pass_through_for_mechanical_examples() -> None:
    cases: tuple[tuple[Callable[..., object], object, object], ...] = (
        (
            run_articulated_loop_training,
            ArticulatedLoopEnv(),
            ArticulatedLoopTrainingConfig(episodes=1, max_steps_per_episode=2, seed=0),
        ),
        (
            run_cable_parallel_training,
            CableParallelEnv(),
            CableParallelTrainingConfig(episodes=1, max_steps_per_episode=2, seed=0),
        ),
        (
            run_dual_arm_training,
            DualArmManipulationEnv(),
            DualArmTrainingConfig(episodes=1, max_steps_per_episode=2, seed=0),
        ),
        (
            run_parallelogram_training,
            ParallelogramSingularityEnv(),
            ParallelogramTrainingConfig(episodes=1, max_steps_per_episode=2, seed=0),
        ),
        (
            run_plate_support_training,
            PlateSupportEnv(),
            PlateSupportTrainingConfig(episodes=1, max_steps_per_episode=2, seed=0),
        ),
    )

    for run_training, env, config in cases:
        default_result = run_training(env=env, config=config)
        flat_result = run_training(
            env=env,
            config=config,
            contraction_schema=NoContractionSchema(),
        )

        assert default_result.q_table
        assert flat_result.q_table
        assert _key_lengths(default_result.q_table) == {2}
        assert _key_lengths(flat_result.q_table) == {1}


def test_training_schema_pass_through_for_counterpoint_example() -> None:
    default_result = run_rl_counterpoint_training(
        env=RlCounterpointEnv(),
        config=RlCounterpointTrainingConfig(episodes=1, max_steps_per_episode=2, seed=0),
    )
    flat_result = run_rl_counterpoint_training(
        env=RlCounterpointEnv(),
        config=RlCounterpointTrainingConfig(episodes=1, max_steps_per_episode=2, seed=0),
        contraction_schema=NoContractionSchema(),
    )

    assert default_result.q_table
    assert flat_result.q_table
    assert _key_lengths(default_result.q_table) == {2}
    assert _key_lengths(flat_result.q_table) == {1}
