from dataclasses import dataclass

from state_collapser.tower.control.frozen_context import FrozenLowerContext
from state_collapser.tower.control.learner import LearnerUpdateSummary
from state_collapser.tower.control.transition import ActiveTierTransition


@dataclass
class StubLearner:
    def behavior_action(self, state: object | None, *, mode: str) -> object:
        return (state, mode)

    def observe(
        self,
        transition: ActiveTierTransition,
        *,
        frozen_context: FrozenLowerContext,
    ) -> LearnerUpdateSummary:
        return LearnerUpdateSummary(td_error=0.25, success=transition.success)

    def should_train(self, event_index: int) -> bool:
        return event_index % 2 == 0

    def train(self, *, frozen_context: FrozenLowerContext) -> LearnerUpdateSummary:
        return LearnerUpdateSummary(td_error=0.1, success=True)


def test_stub_learner_matches_first_release_contract_shape() -> None:
    learner = StubLearner()
    transition = ActiveTierTransition(
        tier_index=0,
        source_state=("src",),
        action=("act",),
        target_state=("dst",),
        aggregated_reward=1.0,
    )
    summary = learner.observe(
        transition,
        frozen_context=FrozenLowerContext(supporting_tier=None, version=0),
    )
    assert summary.td_error == 0.25
    assert summary.success
