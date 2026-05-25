from __future__ import annotations

from schema_assertions import (
    assert_runtime_scheduled_schema_assignments,
    assert_snapshot_has_nontrivial_tower,
    scheduled_assignment_count,
)

from state_collapser.examples.articulated_loop_env import (
    START_STATE,
    ArticulatedLoopEnv,
    ArticulatedLoopEnvRuntime,
    ArticulatedLoopHiddenGraph,
    articulated_loop_state_to_core_state,
    default_articulated_loop_schema,
    semantic_articulated_loop_schema,
)
from state_collapser.tower.partition.schema import NoContractionSchema


def test_hidden_graph_edges_expose_schema_labels() -> None:
    hidden_graph = ArticulatedLoopHiddenGraph()
    start_state = articulated_loop_state_to_core_state(START_STATE)

    labels = {label for edge in hidden_graph.out_edges(start_state) for label in edge.labels}

    assert "articulated-loop-transition" in labels
    assert "articulated-loop-link-1" in labels
    assert "articulated-loop-link-2" in labels
    assert "articulated-loop-link-3" in labels
    assert "articulated-loop-brace-mode" in labels
    assert "articulated-loop-coupler-slack" in labels


def test_schema_helpers_are_importable() -> None:
    assert default_articulated_loop_schema().ordered_blocks()
    assert semantic_articulated_loop_schema().ordered_blocks()


def test_runtime_reset_materializes_initial_tower_snapshot() -> None:
    runtime = ArticulatedLoopEnvRuntime(env=ArticulatedLoopEnv())

    reset_result = runtime.reset(seed=0)

    assert reset_result.runtime_snapshot.current_base_state is not None
    assert reset_result.runtime_snapshot.current_position_at_every_tier


def test_default_schema_reset_builds_nontrivial_tower() -> None:
    runtime = ArticulatedLoopEnvRuntime(env=ArticulatedLoopEnv())

    reset_result = runtime.reset(seed=0)

    assert_snapshot_has_nontrivial_tower(reset_result.runtime_snapshot)
    assert_runtime_scheduled_schema_assignments(runtime)


def test_explicit_no_schema_reset_stays_flat() -> None:
    runtime = ArticulatedLoopEnvRuntime(
        env=ArticulatedLoopEnv(),
        contraction_schema=NoContractionSchema(),
    )

    reset_result = runtime.reset(seed=0)

    assert len(reset_result.runtime_snapshot.current_position_at_every_tier) == 1
    assert scheduled_assignment_count(runtime) == 0


def test_runtime_step_updates_snapshot() -> None:
    runtime = ArticulatedLoopEnvRuntime(env=ArticulatedLoopEnv())
    runtime.reset(seed=0)

    step_result = runtime.step(2)

    assert step_result.runtime_snapshot.current_base_state is not None
    assert step_result.info["state"] is not None
