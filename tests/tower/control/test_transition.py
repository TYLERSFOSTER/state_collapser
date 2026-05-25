from state_collapser.tower.control.transition import ActiveTierTransition


def test_transition_preserves_fields() -> None:
    transition = ActiveTierTransition(
        tier_index=1,
        source_state=("src",),
        action=("act",),
        target_state=("dst",),
        aggregated_reward=1.5,
        duration=3,
        context_version=9,
        representative_jump=("rep-jump",),
        success=False,
    )
    assert transition.tier_index == 1
    assert transition.duration == 3
    assert transition.context_version == 9
    assert transition.representative_jump == ("rep-jump",)
    assert not transition.success
