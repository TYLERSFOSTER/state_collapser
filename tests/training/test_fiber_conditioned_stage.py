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
