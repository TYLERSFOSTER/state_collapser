from collections.abc import Callable
from dataclasses import dataclass, field

from state_collapser.tower.control import (
    ActiveTierController,
    ActiveTierState,
    ControlAction,
    FrozenLowerContext,
    LearnerUpdateSummary,
    TierControlConfig,
)
from state_collapser.tower.control.transition import ActiveTierTransition
from state_collapser.tower.runtime import ExploitExploreTowerRuntime


@dataclass
class StubLearner:
    train_due: bool = False
    behavior_action_calls: int = 0
    behavior_action_states: list[object | None] = field(default_factory=list)
    observed_transitions: list[ActiveTierTransition] = field(default_factory=list)

    def behavior_action(self, state: object | None, *, mode: str) -> object:
        self.behavior_action_calls += 1
        self.behavior_action_states.append(state)
        return (state, mode)

    def observe(
        self,
        transition: ActiveTierTransition,
        *,
        frozen_context: FrozenLowerContext,
    ) -> LearnerUpdateSummary:
        del frozen_context
        self.observed_transitions.append(transition)
        return LearnerUpdateSummary(td_error=0.1, success=transition.success)

    def should_train(self, event_index: int) -> bool:
        del event_index
        return self.train_due

    def train(self, *, frozen_context: FrozenLowerContext) -> LearnerUpdateSummary:
        del frozen_context
        return LearnerUpdateSummary(td_error=0.05, success=True)


@dataclass
class StubExecutor:
    success: bool = True
    execute_calls: int = 0
    executed_tiers: list[int] = field(default_factory=list)

    def execute(
        self,
        active_tier_state: ActiveTierState,
        action: object,
        *,
        frozen_context: FrozenLowerContext,
        mode: str,
    ) -> ActiveTierTransition:
        self.execute_calls += 1
        self.executed_tiers.append(active_tier_state.active_tier)
        return ActiveTierTransition(
            tier_index=active_tier_state.active_tier,
            source_state=active_tier_state.tier_state,
            action=action,
            target_state=("next", mode),
            aggregated_reward=1.0,
            duration=1,
            context_version=frozen_context.version,
            success=self.success,
        )


def _runtime(
    *,
    active_tier: int = 0,
    deepest_known_tier: int = 1,
    train_due: bool = False,
    min_visit_count: int = 2,
    td_error_threshold: float = 0.5,
    success_threshold: float = 0.5,
    learner: StubLearner | None = None,
    executor: StubExecutor | None = None,
    tier_is_executable: Callable[[int], bool] | None = None,
) -> ExploitExploreTowerRuntime:
    resolved_learner = StubLearner(train_due=train_due) if learner is None else learner
    resolved_executor = StubExecutor() if executor is None else executor
    tier_configs = {
        tier_index: TierControlConfig(
            epsilon=0.0,
            min_visit_count=min_visit_count,
            td_error_threshold=td_error_threshold,
            success_threshold=success_threshold,
            training_interval=1,
        )
        for tier_index in range(deepest_known_tier + 1)
    }
    return ExploitExploreTowerRuntime(
        active_tier_state=ActiveTierState(
            active_tier=active_tier,
            tier_state=("state", active_tier),
            deepest_known_tier=deepest_known_tier,
        ),
        tier_configs=tier_configs,
        controller=ActiveTierController(),
        learner=resolved_learner,
        executor=resolved_executor,
        frozen_contexts={
            tier_index: FrozenLowerContext(
                supporting_tier=(
                    tier_index + 1 if tier_index + 1 <= deepest_known_tier else None
                ),
            )
            for tier_index in range(deepest_known_tier + 1)
        },
        move_down=lambda state: state.descend(next_state=("down", state.active_tier + 1)),
        move_up=lambda state: state.lift(next_state=("up", state.active_tier - 1)),
        tier_is_executable=tier_is_executable,
    )


def test_runtime_loop_lifts_before_any_other_choice_when_signal_demands_it() -> None:
    runtime = _runtime(active_tier=1, deepest_known_tier=1, min_visit_count=1)
    signal = runtime.signal_state()
    signal.record_visit()
    signal.record_outcome(success=True)
    signal.record_td_error(0.0)
    upstairs_signal = runtime.signal_state(
        ActiveTierState(
            active_tier=0,
            tier_state=("state", 0),
            deepest_known_tier=1,
        )
    )
    upstairs_signal.record_visit()
    upstairs_signal.record_outcome(success=False)
    result = runtime.step()
    assert result.decision is ControlAction.LIFT
    assert result.active_tier_state.active_tier == 0


def test_runtime_loop_descends_when_deeper_tier_is_lowest_unclosed() -> None:
    runtime = _runtime(active_tier=0, deepest_known_tier=1, min_visit_count=1)
    signal = runtime.signal_state()
    signal.record_visit()
    signal.record_outcome(success=True)
    signal.record_td_error(0.0)
    result = runtime.step()
    assert result.decision is ControlAction.DESCEND
    assert result.active_tier_state.active_tier == 1


def test_runtime_loop_trains_when_due_and_no_gate_fires() -> None:
    runtime = _runtime(active_tier=0, deepest_known_tier=0, train_due=True, min_visit_count=1)
    signal = runtime.signal_state()
    signal.record_visit()
    signal.record_outcome(success=True)
    signal.record_td_error(0.0)
    result = runtime.step()
    assert result.decision is ControlAction.TRAIN
    assert result.learner_summary is not None


def test_runtime_loop_explores_when_pressure_is_high() -> None:
    runtime = _runtime(active_tier=0, deepest_known_tier=0, min_visit_count=3)
    result = runtime.step()
    assert result.decision is ControlAction.EXPLORE


def test_runtime_loop_exploit_executes_when_pressure_is_low() -> None:
    runtime = _runtime(active_tier=0, deepest_known_tier=0, min_visit_count=1)
    signal = runtime.signal_state()
    signal.record_visit()
    signal.record_outcome(success=True)
    signal.record_td_error(0.0)
    result = runtime.step()
    assert result.decision is ControlAction.EXPLOIT_EXECUTE


def test_runtime_lifts_out_of_non_executable_active_tier_before_action_choice() -> None:
    learner = StubLearner()
    executor = StubExecutor()
    runtime = _runtime(
        active_tier=1,
        deepest_known_tier=1,
        min_visit_count=3,
        learner=learner,
        executor=executor,
        tier_is_executable=lambda tier: tier == 0,
    )

    result = runtime.step()

    assert result.active_tier_state.active_tier == 0
    assert learner.behavior_action_calls == 1
    assert learner.behavior_action_states == [("up", 0)]
    assert executor.executed_tiers == [0]


def test_runtime_lifts_through_multiple_non_executable_tiers() -> None:
    learner = StubLearner()
    executor = StubExecutor()
    runtime = _runtime(
        active_tier=2,
        deepest_known_tier=2,
        min_visit_count=3,
        learner=learner,
        executor=executor,
        tier_is_executable=lambda tier: tier == 0,
    )

    result = runtime.step()

    assert result.active_tier_state.active_tier == 0
    assert learner.behavior_action_calls == 1
    assert learner.behavior_action_states == [("up", 0)]
    assert executor.executed_tiers == [0]


def test_runtime_returns_no_available_action_when_base_tier_is_not_executable() -> None:
    learner = StubLearner()
    executor = StubExecutor()
    runtime = _runtime(
        active_tier=0,
        deepest_known_tier=0,
        learner=learner,
        executor=executor,
        tier_is_executable=lambda tier: False,
    )

    result = runtime.step()

    assert result.decision is ControlAction.NO_AVAILABLE_ACTION
    assert result.transition is None
    assert result.learner_summary is None
    assert result.active_tier_state.active_tier == 0
    assert learner.behavior_action_calls == 0
    assert executor.execute_calls == 0


def test_runtime_metrics_record_decisions() -> None:
    runtime = _runtime(active_tier=0, deepest_known_tier=0)
    result = runtime.step()
    assert runtime.metrics.mode_counts[result.decision] == 1
