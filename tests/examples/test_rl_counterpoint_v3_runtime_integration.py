"""Runtime integration checks for the rl_counterpoint_v3 example."""

from schema_assertions import (
    assert_runtime_scheduled_schema_assignments,
    assert_snapshot_has_nontrivial_tower,
    scheduled_assignment_count,
)

from state_collapser.examples.rl_counterpoint_v3 import (
    DEFAULT_GRAPH_SPEC,
    START_STATE,
    RlCounterpointEnv,
    RlCounterpointEnvRuntime,
    RlCounterpointHiddenGraph,
    default_rl_counterpoint_v3_schema,
    rl_counterpoint_state_to_core_state,
    semantic_rl_counterpoint_v3_schema,
    valid_outgoing_transitions,
)
from state_collapser.examples.tower_depth_probe import continuous_probe
from state_collapser.tower.partition.schema import NoContractionSchema


def test_hidden_graph_edges_expose_neutral_motion_labels() -> None:
    hidden_graph = RlCounterpointHiddenGraph(DEFAULT_GRAPH_SPEC)
    start_state = rl_counterpoint_state_to_core_state(START_STATE)

    labels = {label for edge in hidden_graph.out_edges(start_state) for label in edge.labels}

    assert "rl-counterpoint-v3-transition" in labels
    assert "rl-counterpoint-v3-beat-advance" in labels
    assert "rl-counterpoint-v3-bass-motion" in labels
    assert "rl-counterpoint-v3-inner-motion" in labels
    assert "rl-counterpoint-v3-upper-motion" in labels
    assert "rl-counterpoint-v3-oblique-motion" in labels
    assert "rl-counterpoint-v3-parallel-direction-motion" in labels
    assert "rl-counterpoint-v3-contrary-direction-motion" in labels


def test_schema_helpers_are_importable() -> None:
    assert default_rl_counterpoint_v3_schema().ordered_blocks()
    assert semantic_rl_counterpoint_v3_schema().ordered_blocks()


def test_runtime_reset_returns_snapshot() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    reset_result = runtime.reset(seed=0)
    assert reset_result.runtime_snapshot.current_position_at_every_tier
    assert runtime.hidden_graph.is_valid_state(
        reset_result.runtime_snapshot.current_base_state
    )


def test_default_schema_reset_builds_nontrivial_tower() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())

    reset_result = runtime.reset(seed=0)

    assert_snapshot_has_nontrivial_tower(reset_result.runtime_snapshot)
    assert_runtime_scheduled_schema_assignments(runtime)


def test_explicit_no_schema_reset_stays_flat() -> None:
    runtime = RlCounterpointEnvRuntime(
        env=RlCounterpointEnv(),
        contraction_schema=NoContractionSchema(),
    )

    reset_result = runtime.reset(seed=0)

    assert len(reset_result.runtime_snapshot.current_position_at_every_tier) == 1
    assert scheduled_assignment_count(runtime) == 0


def test_runtime_step_tracks_env_step() -> None:
    runtime = RlCounterpointEnvRuntime(env=RlCounterpointEnv())
    runtime.reset(seed=0)
    action, _ = valid_outgoing_transitions(runtime.env.state, spec=DEFAULT_GRAPH_SPEC)[0]
    step_result = runtime.step(action)
    assert isinstance(step_result.reward, float)
    assert step_result.runtime_snapshot.current_position_at_every_tier


def test_post_refactor_probe_reaches_nontrivial_counterpoint_depth() -> None:
    # The historical legacy dynamic-builder probe reported max_depth = 15. The
    # partition schema has different semantics, so this test only requires the
    # post-refactor nontriviality contract.
    result = continuous_probe(
        env_name="rl_counterpoint_v3",
        steps=40,
        seed=0,
        sample_size=1,
        use_contraction_policy=True,
        reset_on_terminal=True,
    )

    assert result.max_depth >= 2
    assert result.scheduled_assignment_count > 0
