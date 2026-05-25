"""Tests for tower runtime benchmark surfaces."""

from __future__ import annotations

from state_collapser.benchmarks.tower_runtime_bench import (
    TowerRuntimeBenchResult,
    main,
    run_tower_runtime_benchmark,
)
from state_collapser.tower.runtime import TowerRuntime


def test_benchmark_result_can_be_constructed() -> None:
    result = TowerRuntimeBenchResult(
        benchmark_name="x",
        mode="default",
        steps=1,
        elapsed_seconds=0.1,
        operations_per_second=10.0,
        discovered_state_count=1,
        discovered_edge_count=0,
        tower_depth=1,
        readout_requested=False,
        morphism_requested=False,
    )

    assert "readout_requested=False" in result.summary_line()


def test_tiny_no_schema_and_default_schema_runs_return_results() -> None:
    no_schema = run_tower_runtime_benchmark(steps=1, mode="none", seed=0)
    default_schema = run_tower_runtime_benchmark(steps=1, mode="default", seed=0)

    assert no_schema.mode == "none"
    assert default_schema.mode == "default"
    assert no_schema.steps == 1
    assert default_schema.steps == 1


def test_readout_disabled_and_enabled_modes_record_flags(monkeypatch) -> None:
    readout_calls = 0
    original = TowerRuntime.compatibility_quotient_tiers

    def counted_readout(self: TowerRuntime) -> tuple[object, ...]:
        nonlocal readout_calls
        readout_calls += 1
        return original(self)

    monkeypatch.setattr(TowerRuntime, "compatibility_quotient_tiers", counted_readout)

    disabled = run_tower_runtime_benchmark(steps=1, readout_requested=False)
    assert not disabled.readout_requested
    assert readout_calls == 0

    enabled = run_tower_runtime_benchmark(steps=1, readout_requested=True)
    assert enabled.readout_requested
    assert readout_calls > 0


def test_morphism_requested_flag_is_recorded() -> None:
    result = run_tower_runtime_benchmark(steps=1, morphism_requested=True)

    assert result.morphism_requested


def test_main_summary_only_outputs_concise_line(capsys) -> None:
    result = main(["--steps", "1", "--summary-only", "--mode", "none"])
    captured = capsys.readouterr()

    assert result.steps == 1
    assert "tower_runtime_bench" in captured.out
    assert "readout_requested=False" in captured.out
