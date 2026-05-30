"""CLI utility for probing dynamic tower depth in example environments."""

from __future__ import annotations

import argparse
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from state_collapser.contract.policy import ContractionPolicy, SeededRandomContractionPolicy
from state_collapser.examples.articulated_loop_env import (
    ACTION_COUNT as ARTICULATED_LOOP_ACTION_COUNT,
)
from state_collapser.examples.articulated_loop_env import (
    ArticulatedLoopEnv,
    ArticulatedLoopEnvRuntime,
)
from state_collapser.examples.cable_parallel_env import (
    ACTION_COUNT as CABLE_PARALLEL_ACTION_COUNT,
)
from state_collapser.examples.cable_parallel_env import (
    CableParallelEnv,
    CableParallelEnvRuntime,
)
from state_collapser.examples.dual_arm_manipulation_env import (
    ACTION_COUNT as DUAL_ARM_ACTION_COUNT,
)
from state_collapser.examples.dual_arm_manipulation_env import (
    DualArmManipulationEnv,
    DualArmManipulationEnvRuntime,
)
from state_collapser.examples.parallelogram_singularity_env import (
    ACTION_COUNT as PARALLELOGRAM_ACTION_COUNT,
)
from state_collapser.examples.parallelogram_singularity_env import (
    ParallelogramSingularityEnv,
    ParallelogramSingularityEnvRuntime,
)
from state_collapser.examples.plate_support_env import (
    ACTION_COUNT as PLATE_SUPPORT_ACTION_COUNT,
)
from state_collapser.examples.plate_support_env import (
    PlateSupportEnv,
    PlateSupportEnvRuntime,
)
from state_collapser.examples.rl_counterpoint_v3 import (
    ACTION_COUNT as RL_COUNTERPOINT_V3_ACTION_COUNT,
)
from state_collapser.examples.rl_counterpoint_v3 import (
    RlCounterpointEnv,
    RlCounterpointEnvRuntime,
)
from state_collapser.tower.partition.schema import (
    ContractionSchema,
    NoContractionSchema,
)


class ProbeTowerRuntimeHandle(Protocol):
    """Minimal tower-runtime handle required by the probe utility."""

    @property
    def quotient_tiers(self) -> tuple[object, ...]:
        """Return currently exposed quotient-tier readouts."""
        ...


class ProbeRuntime(Protocol):
    """Shared runtime surface used by the tower-depth probe."""

    @property
    def tower_runtime(self) -> ProbeTowerRuntimeHandle:
        """Return the underlying tower runtime handle."""
        ...

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, object] | None = None,
    ) -> Any:
        """Reset the probed environment/runtime pair."""
        ...

    def step(self, action: int) -> Any:
        """Advance one action in the probed environment/runtime pair."""
        ...


@dataclass(frozen=True, slots=True)
class ProbeEnvironment:
    """Bundle of env/runtime builders and action-count metadata."""

    name: str
    action_count: int
    runtime_factory: Callable[[ContractionPolicy | None, ContractionSchema | None], ProbeRuntime]


@dataclass(frozen=True, slots=True)
class DepthProbeResult:
    """Structured output of one continuous depth probe."""

    env_name: str
    schema_mode: str
    depth_curve: tuple[int, ...]
    max_depth: int
    scheduled_assignment_count: int
    unscheduled_assignment_count: int
    reset_events: tuple[tuple[int, bool, bool], ...]


SUPPORTED_ENVIRONMENTS: dict[str, ProbeEnvironment] = {
    "plate_support_env": ProbeEnvironment(
        name="plate_support_env",
        action_count=PLATE_SUPPORT_ACTION_COUNT,
        runtime_factory=lambda policy, schema: PlateSupportEnvRuntime(
            env=PlateSupportEnv(),
            contraction_policy=policy,
            contraction_schema=schema,
        ),
    ),
    "articulated_loop_env": ProbeEnvironment(
        name="articulated_loop_env",
        action_count=ARTICULATED_LOOP_ACTION_COUNT,
        runtime_factory=lambda policy, schema: ArticulatedLoopEnvRuntime(
            env=ArticulatedLoopEnv(),
            contraction_policy=policy,
            contraction_schema=schema,
        ),
    ),
    "dual_arm_manipulation_env": ProbeEnvironment(
        name="dual_arm_manipulation_env",
        action_count=DUAL_ARM_ACTION_COUNT,
        runtime_factory=lambda policy, schema: DualArmManipulationEnvRuntime(
            env=DualArmManipulationEnv(),
            contraction_policy=policy,
            contraction_schema=schema,
        ),
    ),
    "cable_parallel_env": ProbeEnvironment(
        name="cable_parallel_env",
        action_count=CABLE_PARALLEL_ACTION_COUNT,
        runtime_factory=lambda policy, schema: CableParallelEnvRuntime(
            env=CableParallelEnv(),
            contraction_policy=policy,
            contraction_schema=schema,
        ),
    ),
    "parallelogram_singularity_env": ProbeEnvironment(
        name="parallelogram_singularity_env",
        action_count=PARALLELOGRAM_ACTION_COUNT,
        runtime_factory=lambda policy, schema: ParallelogramSingularityEnvRuntime(
            env=ParallelogramSingularityEnv(),
            contraction_policy=policy,
            contraction_schema=schema,
        ),
    ),
    "rl_counterpoint_v3": ProbeEnvironment(
        name="rl_counterpoint_v3",
        action_count=RL_COUNTERPOINT_V3_ACTION_COUNT,
        runtime_factory=lambda policy, schema: RlCounterpointEnvRuntime(
            env=RlCounterpointEnv(),
            contraction_policy=policy,
            contraction_schema=schema,
        ),
    ),
}

SUPPORTED_SCHEMA_MODES = ("default", "none")


def build_contraction_policy(
    *,
    use_contraction_policy: bool,
    seed: int,
    sample_size: int,
) -> ContractionPolicy | None:
    """Return the contraction policy used for the probe."""

    if not use_contraction_policy:
        return None
    return SeededRandomContractionPolicy(seed=seed, sample_size=sample_size)


def build_contraction_schema(*, schema_mode: str) -> ContractionSchema | None:
    """Return the contraction schema override used for the probe."""

    if schema_mode == "default":
        return None
    if schema_mode == "none":
        return NoContractionSchema()
    raise ValueError(f"Unsupported schema mode: {schema_mode}")


def _schema_assignment_counts(runtime: ProbeRuntime) -> tuple[int, int]:
    """Return scheduled and unscheduled assignment counts for the latest update."""

    update_result = getattr(runtime.tower_runtime, "last_tower_update_result", None)
    if update_result is None:
        return (0, 0)
    scheduled = 0
    unscheduled = 0
    for assignment in update_result.schema_assignments:
        if assignment.block_id is None:
            unscheduled += 1
        else:
            scheduled += 1
    return (scheduled, unscheduled)


def continuous_probe(
    *,
    env_name: str,
    steps: int,
    seed: int,
    sample_size: int,
    use_contraction_policy: bool,
    reset_on_terminal: bool,
    schema_mode: str = "default",
) -> DepthProbeResult:
    """Run one continuous random-discovery probe and return the depth curve."""

    if env_name not in SUPPORTED_ENVIRONMENTS:
        raise ValueError(f"Unsupported environment: {env_name}")

    probe_env = SUPPORTED_ENVIRONMENTS[env_name]
    policy = build_contraction_policy(
        use_contraction_policy=use_contraction_policy,
        seed=seed,
        sample_size=sample_size,
    )
    schema = build_contraction_schema(schema_mode=schema_mode)
    runtime = probe_env.runtime_factory(policy, schema)
    rng = random.Random(seed)

    reset_result = runtime.reset(seed=seed)
    depth_curve = [len(reset_result.runtime_snapshot.current_position_at_every_tier)]
    reset_events: list[tuple[int, bool, bool]] = []
    scheduled_assignment_count, unscheduled_assignment_count = _schema_assignment_counts(runtime)

    for step_index in range(steps):
        action = rng.randrange(probe_env.action_count)
        step_result = runtime.step(action)
        depth_curve.append(len(step_result.runtime_snapshot.current_position_at_every_tier))
        scheduled_count, unscheduled_count = _schema_assignment_counts(runtime)
        scheduled_assignment_count += scheduled_count
        unscheduled_assignment_count += unscheduled_count
        if (step_result.terminated or step_result.truncated) and reset_on_terminal:
            reset_events.append(
                (step_index + 1, step_result.terminated, step_result.truncated)
            )
            reset_result = runtime.reset(seed=seed + step_index + 1)
            depth_curve.append(len(reset_result.runtime_snapshot.current_position_at_every_tier))
            scheduled_count, unscheduled_count = _schema_assignment_counts(runtime)
            scheduled_assignment_count += scheduled_count
            unscheduled_assignment_count += unscheduled_count

    return DepthProbeResult(
        env_name=env_name,
        schema_mode=schema_mode,
        depth_curve=tuple(depth_curve),
        max_depth=max(depth_curve),
        scheduled_assignment_count=scheduled_assignment_count,
        unscheduled_assignment_count=unscheduled_assignment_count,
        reset_events=tuple(reset_events),
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the tower-depth probe utility."""

    parser = argparse.ArgumentParser(
        description="Probe dynamic tower depth in state_collapser example environments.",
    )
    parser.add_argument(
        "envs",
        nargs="*",
        help="Environment names to probe. Defaults to all supported environments.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=80,
        help="Number of primitive steps to take in each continuous probe.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Random seed for action selection and the seeded random contraction policy.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=1,
        help=(
            "Per-local-star sample size for the legacy/annotation contraction policy. "
            "Partition coarsening is controlled by --schema-mode."
        ),
    )
    parser.add_argument(
        "--schema-mode",
        choices=SUPPORTED_SCHEMA_MODES,
        default="default",
        help=(
            "Schema mode for partition-tower contraction: default uses each runtime's "
            "default schema, none disables schema scheduling."
        ),
    )
    parser.add_argument(
        "--no-contraction-policy",
        action="store_true",
        help=(
            "Disable the seeded random legacy/annotation policy. This does not disable "
            "partition schema scheduling; use --schema-mode none for a flat schema baseline."
        ),
    )
    parser.add_argument(
        "--no-reset-on-terminal",
        action="store_true",
        help="Do not reset when an episode terminates or truncates during the continuous probe.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print only the max depth per environment instead of the full depth curve.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI tower-depth probe."""

    args = parse_args(argv)
    env_names = list(args.envs) if args.envs else list(SUPPORTED_ENVIRONMENTS)
    unsupported_env_names = [
        env_name for env_name in env_names if env_name not in SUPPORTED_ENVIRONMENTS
    ]
    if unsupported_env_names:
        joined = ", ".join(unsupported_env_names)
        supported = ", ".join(SUPPORTED_ENVIRONMENTS)
        raise ValueError(f"Unsupported environment(s): {joined}. Supported: {supported}")

    for env_name in env_names:
        result = continuous_probe(
            env_name=env_name,
            steps=args.steps,
            seed=args.seed,
            sample_size=args.sample_size,
            use_contraction_policy=not args.no_contraction_policy,
            reset_on_terminal=not args.no_reset_on_terminal,
            schema_mode=args.schema_mode,
        )
        print(result.env_name)
        if args.summary_only:
            print(f"max_depth: {result.max_depth}")
            print(f"scheduled_assignments: {result.scheduled_assignment_count}")
            print(f"unscheduled_assignments: {result.unscheduled_assignment_count}")
        else:
            print(f"schema_mode: {result.schema_mode}")
            print(f"depth_curve: {list(result.depth_curve)}")
            print(f"max_depth: {result.max_depth}")
            print(f"scheduled_assignments: {result.scheduled_assignment_count}")
            print(f"unscheduled_assignments: {result.unscheduled_assignment_count}")
            print(f"reset_events: {list(result.reset_events)}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
