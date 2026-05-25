from state_collapser.tower.control.active_tier import ActiveTierState


def test_active_tier_state_preserves_index_and_state() -> None:
    state = ActiveTierState(active_tier=1, tier_state=("tier-state",), deepest_known_tier=3)
    assert state.active_tier == 1
    assert state.tier_state == ("tier-state",)


def test_upstairs_downstairs_helpers_follow_repo_indexing() -> None:
    state = ActiveTierState(active_tier=1, tier_state=None, deepest_known_tier=3)
    assert state.has_upstairs()
    assert state.has_downstairs()
    assert state.upstairs_tier() == 0
    assert state.downstairs_tier() == 2


def test_tier_zero_has_no_upstairs() -> None:
    state = ActiveTierState(active_tier=0, tier_state=None, deepest_known_tier=2)
    assert not state.has_upstairs()


def test_deepest_known_tier_has_no_downstairs() -> None:
    state = ActiveTierState(active_tier=2, tier_state=None, deepest_known_tier=2)
    assert not state.has_downstairs()
