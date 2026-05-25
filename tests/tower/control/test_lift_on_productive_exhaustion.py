from state_collapser.tower.control.signals import should_lift


def test_should_lift_when_current_tier_is_above_the_lowest_unclosed_tier() -> None:
    assert should_lift(2, 1)


def test_should_not_lift_when_current_tier_is_already_lowest_unclosed_tier() -> None:
    assert not should_lift(1, 1)
