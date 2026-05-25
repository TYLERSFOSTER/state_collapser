from dataclasses import dataclass

from state_collapser.tower.control.active_tier import ActiveTierState
from state_collapser.tower.control.frozen_context import FrozenLowerContext
from state_collapser.tower.control.transition import ActiveTierTransition


@dataclass
class StubExecutor:
    def execute(
        self,
        active_tier_state: ActiveTierState,
        action: object,
        *,
        frozen_context: FrozenLowerContext,
        mode: str,
    ) -> ActiveTierTransition:
        return ActiveTierTransition(
            tier_index=active_tier_state.active_tier,
            source_state=active_tier_state.tier_state,
            action=action,
            target_state=("next", mode),
            aggregated_reward=2.0,
            duration=2,
            context_version=frozen_context.version,
            representative_jump=("rep",),
            success=True,
        )


def test_executor_contract_shape_is_sufficient_for_first_release() -> None:
    executor = StubExecutor()
    result = executor.execute(
        ActiveTierState(active_tier=1, tier_state=("src",), deepest_known_tier=2),
        ("action",),
        frozen_context=FrozenLowerContext(supporting_tier=2, version=7),
        mode="explore",
    )
    assert result.aggregated_reward == 2.0
    assert result.duration == 2
    assert result.context_version == 7
