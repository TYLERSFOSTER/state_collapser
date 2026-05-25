from state_collapser.tower.control.active_tier import ActiveTierState
from state_collapser.tower.control.config import TierControlConfig
from state_collapser.tower.control.controller import ActiveTierController, ControlAction
from state_collapser.tower.control.frozen_context import FrozenLowerContext
from state_collapser.tower.control.signals import TierSignalState


def _context() -> FrozenLowerContext:
    return FrozenLowerContext(supporting_tier=1, version=0)


def test_controller_chooses_lift_when_an_upstairs_tier_is_the_lowest_unclosed() -> None:
    controller = ActiveTierController()
    signal = TierSignalState(visit_count=3, td_error_ema=0.0, success_count=3)
    signals_by_tier = {
        0: TierSignalState(),
        1: signal,
    }
    configs = {
        0: TierControlConfig(epsilon=0.0, min_visit_count=2, success_threshold=0.5),
        1: TierControlConfig(epsilon=0.0, min_visit_count=2, success_threshold=0.5),
    }
    decision = controller.decide(
        ActiveTierState(active_tier=1, tier_state=None, deepest_known_tier=1),
        signal,
        configs[1],
        signals_by_tier=signals_by_tier,
        tier_configs=configs,
        frozen_context=_context(),
        training_due=False,
    )
    assert decision.action is ControlAction.LIFT


def test_controller_chooses_descend_toward_lowest_unclosed_tier() -> None:
    controller = ActiveTierController()
    signal = TierSignalState(visit_count=3, td_error_ema=0.0, success_count=3)
    lower_signal = TierSignalState()
    signals_by_tier = {
        0: signal,
        1: lower_signal,
    }
    configs = {
        0: TierControlConfig(epsilon=0.0, min_visit_count=2, success_threshold=0.5),
        1: TierControlConfig(epsilon=0.0, min_visit_count=2, success_threshold=0.5),
    }
    decision = controller.decide(
        ActiveTierState(active_tier=0, tier_state=None, deepest_known_tier=1),
        signal,
        configs[0],
        signals_by_tier=signals_by_tier,
        tier_configs=configs,
        frozen_context=_context(),
        training_due=False,
    )
    assert decision.action is ControlAction.DESCEND


def test_controller_chooses_train_when_due_and_no_lift_or_descent_fires() -> None:
    controller = ActiveTierController()
    signal = TierSignalState(visit_count=1, td_error_ema=0.0, success_count=1)
    config = TierControlConfig(epsilon=0.0, min_visit_count=1, success_threshold=0.5)
    decision = controller.decide(
        ActiveTierState(active_tier=0, tier_state=None, deepest_known_tier=0),
        signal,
        config,
        signals_by_tier={0: signal},
        tier_configs={0: config},
        frozen_context=_context(),
        training_due=True,
    )
    assert decision.action is ControlAction.TRAIN


def test_controller_chooses_explore_when_pressure_is_high() -> None:
    controller = ActiveTierController()
    signal = TierSignalState()
    config = TierControlConfig(epsilon=0.0, min_visit_count=5)
    decision = controller.decide(
        ActiveTierState(active_tier=0, tier_state=None, deepest_known_tier=0),
        signal,
        config,
        signals_by_tier={0: signal},
        tier_configs={0: config},
        frozen_context=_context(),
        training_due=False,
    )
    assert decision.action is ControlAction.EXPLORE


def test_controller_chooses_exploit_execute_otherwise() -> None:
    controller = ActiveTierController()
    signal = TierSignalState(visit_count=5, td_error_ema=0.0, success_count=5)
    config = TierControlConfig(epsilon=0.1, min_visit_count=1, success_threshold=0.5)
    decision = controller.decide(
        ActiveTierState(active_tier=0, tier_state=None, deepest_known_tier=0),
        signal,
        config,
        signals_by_tier={0: signal},
        tier_configs={0: config},
        frozen_context=_context(),
        training_due=False,
    )
    assert decision.action is ControlAction.EXPLOIT_EXECUTE
