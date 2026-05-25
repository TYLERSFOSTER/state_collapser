from state_collapser.tower.control.controller import ControlAction
from state_collapser.tower.control.metrics import TierControlMetrics


def test_metrics_accumulate_by_tier_and_mode() -> None:
    metrics = TierControlMetrics()
    metrics.record(active_tier=0, action=ControlAction.EXPLORE)
    metrics.record(active_tier=0, action=ControlAction.EXPLORE)
    metrics.record(active_tier=1, action=ControlAction.LIFT)

    assert metrics.active_tier_counts[0] == 2
    assert metrics.active_tier_counts[1] == 1
    assert metrics.mode_counts[ControlAction.EXPLORE] == 2
    assert metrics.mode_counts[ControlAction.LIFT] == 1


def test_metrics_reset_clears_accumulators() -> None:
    metrics = TierControlMetrics()
    metrics.record(active_tier=0, action=ControlAction.TRAIN)

    metrics.reset()

    assert not metrics.active_tier_counts
    assert not metrics.mode_counts
