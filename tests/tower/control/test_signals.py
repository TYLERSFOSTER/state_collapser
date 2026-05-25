from state_collapser.tower.control.config import TierControlConfig
from state_collapser.tower.control.signals import (
    TierSignalState,
    exploration_pressure,
    is_unclosed,
    productive_learning_pressure,
    select_lowest_unclosed_tier,
    should_descend,
    should_lift,
)


def test_signal_state_accumulates_visits() -> None:
    signal = TierSignalState()
    signal.record_visit()
    signal.record_visit()
    assert signal.visit_count == 2


def test_signal_state_tracks_td_error_ema() -> None:
    signal = TierSignalState()
    signal.record_td_error(1.0)
    assert signal.td_error_ema > 0.0


def test_signal_state_tracks_success_and_failure_rate() -> None:
    signal = TierSignalState()
    signal.record_outcome(success=True)
    signal.record_outcome(success=False)
    assert signal.success_rate == 0.5


def test_exploration_pressure_increases_under_under_sampling() -> None:
    config = TierControlConfig(epsilon=0.0, min_visit_count=5)
    signal = TierSignalState()
    assert exploration_pressure(signal, config) > 0.0


def test_exploration_pressure_increases_under_td_error_spike() -> None:
    config = TierControlConfig(epsilon=0.0, td_error_threshold=0.25, min_visit_count=0)
    signal = TierSignalState()
    signal.record_td_error(1.0)
    assert exploration_pressure(signal, config) > 0.0


def test_exploration_pressure_increases_under_failure() -> None:
    config = TierControlConfig(epsilon=0.0, min_visit_count=0, success_threshold=0.9)
    signal = TierSignalState()
    signal.record_outcome(success=False)
    assert exploration_pressure(signal, config) > 0.0


def test_productive_learning_pressure_vanishes_when_learning_looks_closed() -> None:
    config = TierControlConfig(epsilon=0.0, min_visit_count=2, td_error_threshold=0.5)
    signal = TierSignalState()
    signal.record_visit()
    signal.record_visit()
    signal.record_outcome(success=True)
    signal.record_outcome(success=True)
    signal.record_td_error(0.1)
    assert productive_learning_pressure(signal, config) == 0.0
    assert not is_unclosed(signal, config)


def test_lowest_unclosed_selection_prefers_deepest_productive_tier() -> None:
    configs = {
        0: TierControlConfig(epsilon=0.0, min_visit_count=1, success_threshold=0.5),
        1: TierControlConfig(epsilon=0.0, min_visit_count=1, success_threshold=0.5),
    }
    signals = {
        0: TierSignalState(visit_count=1, success_count=1, td_error_ema=0.0),
        1: TierSignalState(),
    }
    assert select_lowest_unclosed_tier(1, signals, configs) == 1


def test_should_descend_when_deeper_unclosed_tier_exists() -> None:
    assert should_descend(0, 1)


def test_should_lift_when_current_tier_is_no_longer_lowest_unclosed() -> None:
    assert should_lift(1, 0)


def test_is_unclosed_under_high_td_error() -> None:
    config = TierControlConfig(min_visit_count=1, td_error_threshold=0.25, epsilon=0.0)
    signal = TierSignalState()
    signal.record_visit()
    signal.record_outcome(success=True)
    signal.record_td_error(2.0)
    assert is_unclosed(signal, config)
