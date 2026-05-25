from state_collapser.tower.control.config import TierControlConfig


def test_default_tier_control_config_is_constructible() -> None:
    config = TierControlConfig()
    assert config.min_visit_count > 0
    assert config.training_interval > 0


def test_tier_control_config_preserves_explicit_thresholds() -> None:
    config = TierControlConfig(
        epsilon=0.1,
        min_visit_count=9,
        td_error_threshold=0.25,
        success_threshold=0.8,
        reward_residual_threshold=0.15,
        training_interval=7,
        batch_size=16,
    )
    assert config.epsilon == 0.1
    assert config.min_visit_count == 9
    assert config.td_error_threshold == 0.25
    assert config.success_threshold == 0.8
    assert config.reward_residual_threshold == 0.15
    assert config.training_interval == 7
    assert config.batch_size == 16
