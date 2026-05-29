"""Tests for backend-independent linearized input and transition records."""

from __future__ import annotations

import pytest

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
    EncodingRegistry,
    FiberDeparture,
    FiberDepartureReason,
    FiberStageContext,
    LinearizationConfig,
    LinearizationState,
    NumericBackend,
    TensorDeviceKind,
    TrainingTransition,
    build_action_selection_input,
    linearize_action_selection_input,
    linearize_training_transition,
)


def _state(name: str) -> State:
    return State(payload=(name,), identity=name)


def _edge(source: State, target: State, label: str) -> BaseEdge:
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


class _HiddenGraph:
    def __init__(self, edges: tuple[BaseEdge, ...]) -> None:
        self.edges = edges


def _fixture() -> tuple[PartitionTower, State, tuple[object, ...], LiveRuntimeView]:
    start = _state("start")
    left = _state("left")
    right = _state("right")
    edges = (
        _edge(start, left, "choose"),
        _edge(start, right, "choose"),
        _edge(left, right, "contract"),
    )
    tower = PartitionTower(schema=DimensionwiseSchema(("contract",)))
    tower.initialize(
        initial_states=(start, left, right),
        initial_edges=edges,
        current_state=start,
    )
    hidden_graph = _HiddenGraph(edges)
    explored_graph = ExploredGraph()
    snapshot = LiveRuntimeView(
        current_base_state=start,
        explored_graph=explored_graph,
        vista_graph=VistaGraph(hidden_graph, explored_graph),
        ordered_quotient_tiers=(),
        current_position_at_every_tier=tower.current_position_at_every_tier(start),
        current_step_reward=None,
        cumulative_path_reward=PathRewardSummary(step_rewards=(), total=0.0),
        quotient_tier_reward_summaries=(),
        active_control_tier=0,
        partition_tower_view=tower,
    )
    action_vocabulary = tower.outgoing_action_cells(0, tower.current_state_cell(0, start))
    return tower, start, action_vocabulary, snapshot


def _config(*, strict: bool = True) -> LinearizationConfig:
    return LinearizationConfig(
        linearization_state=LinearizationState.PRESENT_ENABLED,
        numeric_backend=NumericBackend.TORCH,
        device_kind=TensorDeviceKind.CPU,
        max_tower_depth=4,
        max_action_count=4,
        strict=strict,
    )


def test_linearizes_action_selection_input_with_masks_and_stage_context() -> None:
    tower, _start, action_vocabulary, snapshot = _fixture()
    registry = EncodingRegistry.from_tower(tower)
    context = FiberStageContext(
        stage_id="stage",
        fiber_id="fiber",
        fine_tier=0,
        coarse_tier=1,
        frozen_behavior_id="frozen",
        frozen_behavior_version=0,
    )
    action_input = build_action_selection_input(
        observation=(1, 2.5, True),
        runtime_snapshot=snapshot,
        action_mask=(True, False),
        stage_context=context,
        diagnostics={"fiber_action_vocabulary": action_vocabulary},
    )

    linearized = linearize_action_selection_input(
        action_input,
        config=_config(),
        registry=registry,
    )

    assert linearized.observation_features == (1.0, 2.5, 1.0)
    assert linearized.action_mask == (True, False, False, False)
    assert linearized.action_count == 4
    assert len(linearized.tower_position_ids) == 4
    assert linearized.fine_tier == 0
    assert linearized.coarse_tier == 1
    assert linearized.stage_id == 0
    assert linearized.metadata["action_vocabulary_ids"]


def test_unsupported_observation_fails_strict_and_sidecars_non_strict() -> None:
    tower, _start, _action_vocabulary, snapshot = _fixture()
    registry = EncodingRegistry.from_tower(tower)
    action_input = build_action_selection_input(
        observation={"not": "first-scope"},
        runtime_snapshot=snapshot,
        action_mask=(True,),
    )

    with pytest.raises(ValueError, match="Unsupported observation"):
        linearize_action_selection_input(action_input, config=_config(), registry=registry)

    linearized = linearize_action_selection_input(
        action_input,
        config=_config(strict=False),
        registry=registry,
    )

    assert linearized.observation_features == ()
    assert "observation" in linearized.metadata


def test_linearizes_training_transition_and_resolves_action_cell_index() -> None:
    tower, _start, action_vocabulary, snapshot = _fixture()
    registry = EncodingRegistry.from_tower(tower)
    action_input = build_action_selection_input(
        observation=(0.0,),
        runtime_snapshot=snapshot,
        action_mask=(True, True),
        diagnostics={"fiber_action_vocabulary": action_vocabulary},
    )
    transition = TrainingTransition(
        source_input=action_input,
        chosen_action=action_vocabulary[1],
        reward=3.0,
        target_input=action_input,
        terminated=False,
        truncated=False,
        bootstrap_allowed=True,
        bootstrap_reason="continuing",
        fiber_departure=FiberDeparture(reason=FiberDepartureReason.NO_LIFT_CANDIDATE),
    )

    linearized = linearize_training_transition(
        transition,
        config=_config(),
        registry=registry,
    )

    assert linearized.chosen_action == 1
    assert linearized.reward == 3.0
    assert linearized.bootstrap_allowed
    assert linearized.bootstrap_reason_id == 0
