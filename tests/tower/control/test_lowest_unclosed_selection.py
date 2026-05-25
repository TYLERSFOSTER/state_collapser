from state_collapser.tower.control.config import TierControlConfig
from state_collapser.tower.control.signals import (
    TierSignalState,
    select_lowest_unclosed_tier,
    should_descend,
)


def test_select_lowest_unclosed_tier_prefers_highest_index() -> None:
    configs = {
        0: TierControlConfig(epsilon=0.0, min_visit_count=1, success_threshold=0.5),
        1: TierControlConfig(epsilon=0.0, min_visit_count=1, success_threshold=0.5),
        2: TierControlConfig(epsilon=0.0, min_visit_count=1, success_threshold=0.5),
    }
    signals = {
        0: TierSignalState(visit_count=1, success_count=1, td_error_ema=0.0),
        1: TierSignalState(),
        2: TierSignalState(),
    }

    assert select_lowest_unclosed_tier(2, signals, configs) == 2


def test_should_descend_toward_selected_lowest_unclosed_tier() -> None:
    assert should_descend(0, 2)
