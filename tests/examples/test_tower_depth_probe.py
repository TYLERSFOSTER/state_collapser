from __future__ import annotations

from state_collapser.examples.tower_depth_probe import (
    SUPPORTED_ENVIRONMENTS,
    continuous_probe,
    main,
    parse_args,
)

SCHEMA_ENABLED_ENVIRONMENTS = (
    "plate_support_env",
    "articulated_loop_env",
    "dual_arm_manipulation_env",
    "cable_parallel_env",
    "parallelogram_singularity_env",
    "rl_counterpoint_v3",
)


def test_supported_environments_include_plate_support_env() -> None:
    assert "plate_support_env" in SUPPORTED_ENVIRONMENTS
    assert "rl_counterpoint_v3" in SUPPORTED_ENVIRONMENTS


def test_continuous_probe_runs_for_plate_support_env() -> None:
    result = continuous_probe(
        env_name="plate_support_env",
        steps=5,
        seed=0,
        sample_size=1,
        use_contraction_policy=True,
        reset_on_terminal=True,
    )

    assert result.env_name == "plate_support_env"
    assert result.schema_mode == "default"
    assert len(result.depth_curve) >= 6
    assert result.max_depth >= 1
    assert result.scheduled_assignment_count > 0


def test_parse_args_accepts_default_environment_selection() -> None:
    args = parse_args([])

    assert args.envs == []


def test_main_rejects_unsupported_environment_name() -> None:
    try:
        main(["not_an_env", "--steps", "1"])
    except ValueError as exc:
        assert "Unsupported environment" in str(exc)
    else:
        raise AssertionError("Expected unsupported environment to raise ValueError.")


def test_continuous_probe_runs_with_no_schema_mode() -> None:
    result = continuous_probe(
        env_name="plate_support_env",
        steps=5,
        seed=0,
        sample_size=1,
        use_contraction_policy=True,
        reset_on_terminal=True,
        schema_mode="none",
    )

    assert result.env_name == "plate_support_env"
    assert result.schema_mode == "none"
    assert result.scheduled_assignment_count == 0
    assert result.unscheduled_assignment_count >= 0


def test_schema_enabled_environments_reach_nontrivial_default_depth() -> None:
    for env_name in SCHEMA_ENABLED_ENVIRONMENTS:
        result = continuous_probe(
            env_name=env_name,
            steps=5,
            seed=0,
            sample_size=1,
            use_contraction_policy=True,
            reset_on_terminal=True,
        )

        assert result.max_depth >= 2
        assert result.scheduled_assignment_count > 0


def test_schema_enabled_environments_support_flat_schema_mode() -> None:
    for env_name in SCHEMA_ENABLED_ENVIRONMENTS:
        result = continuous_probe(
            env_name=env_name,
            steps=5,
            seed=0,
            sample_size=1,
            use_contraction_policy=True,
            reset_on_terminal=True,
            schema_mode="none",
        )

        assert result.scheduled_assignment_count == 0
