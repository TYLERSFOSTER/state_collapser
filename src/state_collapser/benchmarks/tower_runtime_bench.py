"""Lightweight tower-runtime benchmark CLI."""

from __future__ import annotations

import argparse
import random
import time
from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast

from state_collapser.examples.tower_depth_probe import (
    SUPPORTED_ENVIRONMENTS,
    build_contraction_policy,
    build_contraction_schema,
)
from state_collapser.tower.runtime import TowerRuntime


@dataclass(frozen=True, slots=True)
class TowerRuntimeBenchResult:
    """Structured result from a tower-runtime benchmark run."""

    benchmark_name: str
    mode: str
    steps: int
    elapsed_seconds: float
    operations_per_second: float
    discovered_state_count: int
    discovered_edge_count: int
    tower_depth: int
    readout_requested: bool
    morphism_requested: bool

    def summary_line(self) -> str:
        """Return a concise human-readable benchmark summary."""

        return (
            f"{self.benchmark_name} mode={self.mode} steps={self.steps} "
            f"elapsed_seconds={self.elapsed_seconds:.6f} "
            f"operations_per_second={self.operations_per_second:.2f} "
            f"readout_requested={self.readout_requested} "
            f"morphism_requested={self.morphism_requested} "
            f"tower_depth={self.tower_depth} "
            f"discovered_states={self.discovered_state_count} "
            f"discovered_edges={self.discovered_edge_count}"
        )


def run_tower_runtime_benchmark(
    *,
    steps: int,
    seed: int = 0,
    mode: str = "default",
    readout_requested: bool = False,
    morphism_requested: bool = False,
) -> TowerRuntimeBenchResult:
    """Run a tiny deterministic tower-runtime benchmark."""

    if steps < 0:
        raise ValueError("steps must be non-negative.")
    schema_mode = "none" if mode == "none" else "default"
    probe_env = SUPPORTED_ENVIRONMENTS["plate_support_env"]
    runtime = probe_env.runtime_factory(
        build_contraction_policy(
            use_contraction_policy=True,
            seed=seed,
            sample_size=1,
        ),
        build_contraction_schema(schema_mode=schema_mode),
    )
    tower_runtime = cast(TowerRuntime, runtime.tower_runtime)
    tower_runtime._build_morphism = morphism_requested
    rng = random.Random(seed)

    start = time.perf_counter()
    reset_result = runtime.reset(seed=seed)
    tower_depth = len(reset_result.runtime_snapshot.current_position_at_every_tier)
    if readout_requested:
        tower_runtime.compatibility_quotient_tiers()

    for _ in range(steps):
        action = rng.randrange(probe_env.action_count)
        step_result = runtime.step(action)
        tower_depth = len(step_result.runtime_snapshot.current_position_at_every_tier)
        if readout_requested:
            tower_runtime.compatibility_quotient_tiers()

    elapsed = time.perf_counter() - start
    partition_tower = tower_runtime.partition_tower
    discovered_state_count = 0
    discovered_edge_count = 0
    if partition_tower is not None:
        discovered_state_count = len(partition_tower.registry.state_ids)
        discovered_edge_count = len(partition_tower.registry.edge_ids)

    return TowerRuntimeBenchResult(
        benchmark_name="tower_runtime_bench",
        mode=mode,
        steps=steps,
        elapsed_seconds=elapsed,
        operations_per_second=steps / elapsed if elapsed > 0 else 0.0,
        discovered_state_count=discovered_state_count,
        discovered_edge_count=discovered_edge_count,
        tower_depth=tower_depth,
        readout_requested=readout_requested,
        morphism_requested=morphism_requested,
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse benchmark CLI arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--mode", choices=("none", "default"), default="default")
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--readout", action="store_true")
    parser.add_argument("--morphism", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> TowerRuntimeBenchResult:
    """CLI entry point."""

    args = parse_args(argv)
    result = run_tower_runtime_benchmark(
        steps=args.steps,
        seed=args.seed,
        mode=args.mode,
        readout_requested=args.readout,
        morphism_requested=args.morphism,
    )
    if args.summary_only:
        print(result.summary_line())
    else:
        print(result)
    return result


if __name__ == "__main__":  # pragma: no cover
    main()


__all__ = [
    "TowerRuntimeBenchResult",
    "main",
    "parse_args",
    "run_tower_runtime_benchmark",
]
