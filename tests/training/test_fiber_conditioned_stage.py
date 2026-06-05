"""Tests for the direct fiber-conditioned stage API."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.rewards import PathRewardSummary
from state_collapser.core.state import State
from state_collapser.graph.explored_graph import ExploredGraph
from state_collapser.graph.vista_graph import VistaGraph
from state_collapser.tower.partition.schema import DimensionwiseSchema
from state_collapser.tower.partition.tower import PartitionTower
from state_collapser.tower.snapshot import LiveRuntimeView
from state_collapser.training import (
    ActionDecision,
    FiberConditionedStage,
    FiberDepartureReason,
    FrozenQuotientBehavior,
    PathFiber,
    TabularQLearner,
    TrainingTransition,
)
from state_collapser.training.stages import deterministic_first_lift_selector


def state(name: str) -> State:
    return State(payload=(name,), identity=name)


def edge(source: State, target: State, label: str) -> BaseEdge:
    return BaseEdge(
        source=source,
        action=PrimitiveAction(
            payload=("move", label),
            identity=("move", label),
            labels=(label,),
        ),
        target=target,
        labels=(label,),
    )


def duplicate_identity_edge(
    source: State,
    target: State,
    *,
    payload_suffix: str,
    identity: str,
) -> BaseEdge:
    return BaseEdge(
        source=source,
        action=PrimitiveAction(
            payload=("move", identity, payload_suffix),
            identity=("move", identity),
            labels=(identity,),
        ),
        target=target,
        labels=(identity,),
    )


@dataclass(frozen=True, slots=True)
class _ResetResult:
    observation: object
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


@dataclass(frozen=True, slots=True)
class _StepResult:
    observation: object
    reward: float
    terminated: bool
    truncated: bool
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


class _HiddenGraph:
    def __init__(self, edges: tuple[BaseEdge, ...]) -> None:
        self.edges = edges

    def is_valid_state(self, state: State) -> bool:
        return any(edge.source == state or edge.target == state for edge in self.edges)

    def is_valid_action(self, action: PrimitiveAction) -> bool:
        return any(edge.action == action for edge in self.edges)

    def apply_action(self, state: State, action: PrimitiveAction) -> State | None:
        for edge_item in self.edges:
            if edge_item.source == state and edge_item.action == action:
                return edge_item.target
        return None

    def is_valid_edge(self, edge_item: BaseEdge) -> bool:
        return edge_item in self.edges

    def out_actions(self, state: State) -> Iterable[PrimitiveAction]:
        return tuple(edge_item.action for edge_item in self.edges if edge_item.source == state)

    def out_neighbors(self, state: State) -> Iterable[State]:
        return tuple(edge_item.target for edge_item in self.edges if edge_item.source == state)

    def out_edges(self, state: State) -> Iterable[BaseEdge]:
        return tuple(edge_item for edge_item in self.edges if edge_item.source == state)


class _TinyRuntime:
    def __init__(
        self,
        *,
        tower: PartitionTower,
        start: State,
        goal: State,
        edges: tuple[BaseEdge, ...],
    ) -> None:
        self.tower = tower
        self.start = start
        self.goal = goal
        self.edges = edges
        self.state = start
        self.step_count = 0
        self.hidden_graph = _HiddenGraph(edges)

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, object] | None = None,
    ) -> _ResetResult:
        del seed, options
        self.state = self.start
        self.step_count = 0
        return _ResetResult(
            observation=("obs", self.state.identity),
            info={"reset": True},
            runtime_snapshot=self._snapshot(),
        )

    def step(self, action: object) -> _StepResult:
        if not isinstance(action, PrimitiveAction):
            raise TypeError("Tiny runtime expects PrimitiveAction objects.")
        next_state = self.hidden_graph.apply_action(self.state, action)
        if next_state is None:
            raise ValueError("No transition for action.")
        self.state = next_state
        self.step_count += 1
        return _StepResult(
            observation=("obs", self.state.identity),
            reward=1.0,
            terminated=self.state == self.goal,
            truncated=False,
            info={"step_count": self.step_count},
            runtime_snapshot=self._snapshot(),
        )

    def _snapshot(self) -> LiveRuntimeView:
        explored_graph = ExploredGraph()
        vista_graph = VistaGraph(self.hidden_graph, explored_graph)
        return LiveRuntimeView(
            current_base_state=self.state,
            explored_graph=explored_graph,
            vista_graph=vista_graph,
            ordered_quotient_tiers=(),
            current_position_at_every_tier=self.tower.current_position_at_every_tier(
                self.state
            ),
            current_step_reward=None,
            cumulative_path_reward=PathRewardSummary(step_rewards=(), total=0.0),
            quotient_tier_reward_summaries=(),
            partition_tower_view=self.tower,
        )


def build_stage_fixture() -> tuple[
    FiberConditionedStage,
    _TinyRuntime,
    PartitionTower,
    State,
    State,
    BaseEdge,
]:
    start = state("start")
    left = state("left")
    right = state("right")
    goal = state("goal")
    start_left = edge(start, left, "choose")
    start_right = edge(start, right, "choose")
    start_goal = edge(start, goal, "bad")
    contract = edge(left, right, "contract")
    left_goal = edge(left, goal, "finish")
    right_goal = edge(right, goal, "finish")
    edges = (start_left, start_right, start_goal, contract, left_goal, right_goal)
    tower = PartitionTower(schema=DimensionwiseSchema(("contract",)))
    tower.initialize(
        initial_states=(start, left, right, goal),
        initial_edges=edges,
        current_state=start,
    )
    behavior = FrozenQuotientBehavior.from_step(
        behavior_id="frozen-choose",
        coarse_tier=1,
        supported_fine_tier=0,
        source_cell=tower.current_state_cell(1, start),
        action_cell=tower.action_cell_for_edge(1, start_left),
        target_cell=tower.current_state_cell(1, left),
    )
    path_fiber = PathFiber(
        fiber_id="choose-fiber",
        tower=tower,
        fine_tier=0,
        coarse_tier=1,
        frozen_behavior=behavior,
    )
    runtime = _TinyRuntime(tower=tower, start=start, goal=goal, edges=edges)
    stage = FiberConditionedStage(
        stage_id="stage",
        runtime=runtime,
        tower=tower,
        fine_tier=0,
        coarse_tier=1,
        frozen_behavior=behavior,
        path_fiber=path_fiber,
    )
    return stage, runtime, tower, start, goal, start_goal


def build_pointwise_stage_fixture() -> tuple[
    FiberConditionedStage,
    _TinyRuntime,
    PartitionTower,
    State,
    BaseEdge,
]:
    zero = state("0")
    one = state("1")
    two = state("2")
    contract = edge(zero, one, "contract")
    zero_to_two = edge(zero, two, "to2")
    one_to_two = edge(one, two, "to2")
    one_only = edge(one, two, "one_only")
    edges = (contract, zero_to_two, one_to_two, one_only)
    tower = PartitionTower(schema=DimensionwiseSchema(("contract", "unused")))
    tower.initialize(initial_states=(zero, one, two), initial_edges=edges, current_state=zero)
    behavior = FrozenQuotientBehavior.from_step(
        behavior_id="pointwise-frozen",
        coarse_tier=2,
        supported_fine_tier=1,
        source_cell=tower.current_state_cell(2, zero),
        target_cell=tower.current_state_cell(2, two),
    )
    path_fiber = PathFiber(
        fiber_id="pointwise-fiber",
        tower=tower,
        fine_tier=1,
        coarse_tier=2,
        frozen_behavior=behavior,
    )
    runtime = _TinyRuntime(tower=tower, start=zero, goal=two, edges=edges)
    stage = FiberConditionedStage(
        stage_id="pointwise-stage",
        runtime=runtime,
        tower=tower,
        fine_tier=1,
        coarse_tier=2,
        frozen_behavior=behavior,
        path_fiber=path_fiber,
    )
    return stage, runtime, tower, zero, one_only


def build_multi_lift_stage_fixture() -> tuple[
    FiberConditionedStage,
    _TinyRuntime,
    BaseEdge,
    BaseEdge,
]:
    start = state("start")
    goal = state("goal")
    left = state("left")
    right = state("right")
    first_finish = duplicate_identity_edge(
        start,
        goal,
        payload_suffix="first",
        identity="finish",
    )
    second_finish = duplicate_identity_edge(
        start,
        goal,
        payload_suffix="second",
        identity="finish",
    )
    contract = edge(left, right, "contract")
    edges = (first_finish, second_finish, contract)
    tower = PartitionTower(schema=DimensionwiseSchema(("contract",)))
    tower.initialize(
        initial_states=(start, goal, left, right),
        initial_edges=edges,
        current_state=start,
    )
    behavior = FrozenQuotientBehavior.from_step(
        behavior_id="multi-lift-frozen",
        coarse_tier=1,
        supported_fine_tier=0,
        source_cell=tower.current_state_cell(1, start),
        action_cell=tower.action_cell_for_edge(1, first_finish),
        target_cell=tower.current_state_cell(1, goal),
    )
    path_fiber = PathFiber(
        fiber_id="multi-lift-fiber",
        tower=tower,
        fine_tier=0,
        coarse_tier=1,
        frozen_behavior=behavior,
    )
    runtime = _TinyRuntime(tower=tower, start=start, goal=goal, edges=edges)
    stage = FiberConditionedStage(
        stage_id="multi-lift-stage",
        runtime=runtime,
        tower=tower,
        fine_tier=0,
        coarse_tier=1,
        frozen_behavior=behavior,
        path_fiber=path_fiber,
    )
    return stage, runtime, first_finish, second_finish


def test_stage_reset_returns_context_and_fiber_mask() -> None:
    stage, _runtime, _tower, _start, _goal, _bad = build_stage_fixture()

    action_input = stage.reset(seed=0)

    assert action_input.stage_context == stage.stage_context
    assert action_input.action_mask == (True, True, False)
    assert action_input.diagnostics["fiber_action_vocabulary"]


def test_current_input_is_stable_before_stepping() -> None:
    stage, _runtime, _tower, _start, _goal, _bad = build_stage_fixture()
    initial_input = stage.reset(seed=0)

    current_input = stage.current_input()

    assert current_input.runtime_snapshot.current_base_state == (
        initial_input.runtime_snapshot.current_base_state
    )
    assert current_input.action_mask == initial_input.action_mask
    assert current_input.stage_context == initial_input.stage_context


def test_stage_step_emits_training_transition_for_admissible_action() -> None:
    stage, runtime, _tower, _start, _goal, _bad = build_stage_fixture()
    source_input = stage.reset(seed=0)

    transition = stage.step(ActionDecision(chosen_action=0))

    assert isinstance(transition, TrainingTransition)
    assert transition.source_input == source_input
    assert transition.stage_context == stage.stage_context
    assert transition.projected_coarse_step == stage.frozen_behavior.current_step
    assert transition.fiber_departure is None
    assert transition.reward == 1.0
    assert runtime.step_count == 1


def test_stage_step_diagnoses_inadmissible_action_without_stepping() -> None:
    stage, runtime, _tower, start, _goal, _bad = build_stage_fixture()
    stage.reset(seed=0)

    transition = stage.step(ActionDecision(chosen_action=2))

    assert transition.fiber_departure is not None
    assert transition.fiber_departure.reason is FiberDepartureReason.PROJECTED_TARGET_MISMATCH
    assert transition.reward == 0.0
    assert transition.bootstrap_reason == "fiber_departure"
    assert runtime.step_count == 0
    assert runtime.state == start


def test_stage_does_not_step_non_current_source_representative() -> None:
    stage, runtime, tower, zero, one_only = build_pointwise_stage_fixture()
    action_input = stage.reset(seed=0)
    vocabulary = action_input.diagnostics["fiber_action_vocabulary"]
    one_only_cell = tower.action_cell_for_edge(1, one_only)

    assert one_only_cell is not None
    assert isinstance(vocabulary, tuple)
    chosen_index = vocabulary.index(one_only_cell)
    transition = stage.step(ActionDecision(chosen_action=chosen_index))

    assert transition.fiber_departure is not None
    assert transition.fiber_departure.reason is FiberDepartureReason.NO_LIFT_CANDIDATE
    assert transition.reward == 0.0
    assert runtime.step_count == 0
    assert runtime.state == zero


def test_default_lift_selector_chooses_first_candidate() -> None:
    stage, _runtime, first_finish, _second_finish = build_multi_lift_stage_fixture()
    stage.reset(seed=0)

    transition = stage.step(ActionDecision(chosen_action=0))

    assert transition.diagnostics["realized_edge"] == first_finish
    assert transition.diagnostics["lift_candidate_count"] == 2
    assert transition.diagnostics["selected_lift_index"] == 0
    assert (
        transition.diagnostics["lift_selector"]
        == deterministic_first_lift_selector.__name__
    )


def test_custom_lift_selector_can_choose_non_first_candidate() -> None:
    stage, _runtime, _first_finish, second_finish = build_multi_lift_stage_fixture()

    def select_second(
        lift_candidates: tuple[BaseEdge, ...],
        _source_input: object,
        _action_cell: object,
    ) -> BaseEdge:
        return lift_candidates[1]

    stage.lift_selector = select_second
    stage.reset(seed=0)

    transition = stage.step(ActionDecision(chosen_action=0))

    assert transition.diagnostics["realized_edge"] == second_finish
    assert transition.diagnostics["selected_lift_index"] == 1
    assert transition.diagnostics["lift_selector"] == "select_second"


def test_invalid_lift_selector_output_fails() -> None:
    stage, _runtime, _first_finish, _second_finish = build_multi_lift_stage_fixture()
    outside_edge = edge(state("outside"), state("elsewhere"), "outside")

    def select_outside(
        _lift_candidates: tuple[BaseEdge, ...],
        _source_input: object,
        _action_cell: object,
    ) -> BaseEdge:
        return outside_edge

    stage.lift_selector = select_outside
    stage.reset(seed=0)

    try:
        stage.step(ActionDecision(chosen_action=0))
    except ValueError as exc:
        assert "outside the available lift candidates" in str(exc)
    else:
        raise AssertionError("expected invalid lift selector to fail")


def test_frozen_behavior_remains_unchanged_after_step() -> None:
    stage, _runtime, _tower, _start, _goal, _bad = build_stage_fixture()
    frozen_behavior = stage.frozen_behavior
    stage.reset(seed=0)

    stage.step(ActionDecision(chosen_action=0))

    assert stage.frozen_behavior == frozen_behavior


def test_tiny_direct_stage_loop_can_use_tabular_learner() -> None:
    stage, _runtime, _tower, _start, _goal, _bad = build_stage_fixture()
    learner = TabularQLearner(action_count=3, epsilon=0.0, seed=0)
    current_input = stage.reset(seed=0)

    decision = learner.act(current_input)
    transition = stage.step(decision)
    learner.observe(transition)
    summary = learner.update()

    assert summary.updated
    assert learner.replay == [transition]
