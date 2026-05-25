from state_collapser.tower.control.frozen_context import FrozenLowerContext


def test_frozen_context_preserves_lower_support_and_version() -> None:
    context = FrozenLowerContext(
        supporting_tier=2,
        policy_state=("policy", 1),
        representative_data=("rep",),
        cached_lift_data=("lift",),
        version=3,
    )
    assert context.supporting_tier == 2
    assert context.policy_state == ("policy", 1)
    assert context.version == 3
