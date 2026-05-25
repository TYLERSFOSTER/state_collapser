"""Tower-runtime contract surface."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from state_collapser.contract.policy import ContractionPolicy
from state_collapser.core.action import PrimitiveAction
from state_collapser.core.annotations import VistaPayload
from state_collapser.core.edges import BaseEdge
from state_collapser.core.rewards import (
    PathRewardSummary,
    StepReward,
    primitive_step_reward,
    summarize_path_rewards,
)
from state_collapser.core.state import State
from state_collapser.graph.explored_graph import ExploredGraph
from state_collapser.graph.hidden_graph import HiddenGraph
from state_collapser.graph.local_star import LocalStar
from state_collapser.graph.vista_graph import VistaGraph
from state_collapser.quotient.tier_view import QuotientTierView
from state_collapser.tower.construction import (
    TierContractionRecord,
    projected_edge_is_trivial,
    tier_is_point,
    tower_is_fully_propagated,
)
from state_collapser.tower.construction import (
    build_dynamic_tower as build_legacy_dynamic_tower,
)
from state_collapser.tower.control import (
    ActiveTierController,
    ActiveTierState,
    ControlAction,
    FrozenLowerContext,
    LearnerUpdateSummary,
    LiftResolveExecutor,
    TierControlConfig,
    TierControlMetrics,
    TierLearner,
    TierSignalState,
)
from state_collapser.tower.partition.loop_policy import LoopPolicy
from state_collapser.tower.partition.reward_aggregation import RewardAggregator
from state_collapser.tower.partition.schema import ContractionSchema, NoContractionSchema
from state_collapser.tower.partition.tower import PartitionTower
from state_collapser.tower.partition.update import TowerUpdateResult
from state_collapser.tower.snapshot import LiveRuntimeView


class TowerRuntime:
    """Package-owned coordinator for discovered graph, vista graph, and dynamic tower state."""

    def __init__(
        self,
        hidden_graph: HiddenGraph,
        quotient_tiers: tuple[QuotientTierView, ...] = (),
        contraction_policy: ContractionPolicy | None = None,
        reward_function: Callable[[BaseEdge], float] | None = None,
        tower_backend: str = "partition",
        contraction_schema: ContractionSchema | None = None,
        loop_policy: LoopPolicy | None = None,
        reward_aggregator: RewardAggregator | None = None,
        build_morphism: bool = False,
    ) -> None:
        """Initialize a tower runtime.

        The partition backend is the normal runtime path. The legacy dynamic
        builder remains available with ``tower_backend="legacy"`` for
        validation and compatibility checks.
        """

        if tower_backend not in {"partition", "legacy"}:
            raise ValueError("tower_backend must be either 'partition' or 'legacy'.")
        self._hidden_graph = hidden_graph
        self._seed_quotient_tiers = quotient_tiers
        self._quotient_tiers: tuple[QuotientTierView, ...] = quotient_tiers
        self._compatibility_quotient_tiers: tuple[QuotientTierView, ...] | None = (
            quotient_tiers if quotient_tiers else None
        )
        self._current_position_at_every_tier: tuple[object | None, ...] = ()
        self._contraction_policy = contraction_policy
        self._reward_function = reward_function
        self._tower_backend = tower_backend
        self._contraction_schema = (
            NoContractionSchema() if contraction_schema is None else contraction_schema
        )
        self._loop_policy = LoopPolicy.drop_internal() if loop_policy is None else loop_policy
        self._reward_aggregator = (
            RewardAggregator() if reward_aggregator is None else reward_aggregator
        )
        self._build_morphism = build_morphism
        self._partition_tower: PartitionTower | None = None
        self._last_tower_update_result: TowerUpdateResult | None = None
        self._explored_graph = ExploredGraph()
        self._vista_graph = VistaGraph(hidden_graph, self._explored_graph)
        self._step_rewards: list[StepReward] = []
        self._selected_base_edges: tuple[BaseEdge, ...] = ()
        self._tier_contraction_records: tuple[TierContractionRecord, ...] = ()
        self._tower_stopping_reason: str = "uninitialized"

    def reset(self, initial_state: State | None = None) -> LiveRuntimeView:
        """Reset runtime graph layers and return the initial snapshot."""

        self._explored_graph = ExploredGraph()
        self._vista_graph = VistaGraph(self._hidden_graph, self._explored_graph)
        self._step_rewards = []
        if initial_state is not None:
            self._explored_graph.add_state(initial_state)
            self._vista_graph.refresh_local_vista(initial_state)
        if self._tower_backend == "partition":
            self._reset_partition_tower(current_base_state=initial_state)
        else:
            self._refresh_dynamic_tower(current_base_state=initial_state)
        return LiveRuntimeView(
            current_base_state=self._explored_graph.current_state(),
            explored_graph=self._explored_graph,
            vista_graph=self._vista_graph,
            ordered_quotient_tiers=self._compatibility_quotient_tiers or (),
            current_position_at_every_tier=self._current_position_at_every_tier,
            current_step_reward=None,
            cumulative_path_reward=PathRewardSummary(step_rewards=(), total=0.0),
            quotient_tier_reward_summaries=(),
            partition_tower_view=self._partition_tower,
            tower_update_result=self._last_tower_update_result,
        )

    def step(self, action: PrimitiveAction) -> LiveRuntimeView:
        """Advance the runtime by one primitive action."""

        current_state = self._explored_graph.current_state()
        if current_state is None:
            raise ValueError(
                "TowerRuntime.step(...) requires a current base state; call reset(...) first."
            )

        next_state = self._hidden_graph.apply_action(current_state, action)
        if next_state is None:
            raise ValueError(
                "Hidden graph returned no successor for the requested primitive action."
            )

        edge = BaseEdge(source=current_state, action=action, target=next_state)
        self._explored_graph.add_edge(edge)
        self._vista_graph.refresh_local_vista(current_state)
        self._vista_graph.refresh_local_vista(next_state)

        if self._contraction_policy is not None:
            local_star = LocalStar(
                center=current_state,
                outgoing_edges=self._vista_graph.vista_edges(current_state),
                outgoing_neighbors=self._vista_graph.vista_neighbors(current_state),
                annotations=self._vista_graph.node_payload(current_state),
            )
            selection = self._contraction_policy.select(local_star)
            if selection.edges:
                payload = VistaPayload(
                    outgoing_edges=selection.edges,
                    reachable_targets=tuple(edge.target for edge in selection.edges),
                    labels=tuple(
                        label for selected_edge in selection.edges for label in selected_edge.labels
                    ),
                )
                self._vista_graph.push_message(current_state, next_state, payload)
                self._vista_graph.pull_message(current_state, next_state, payload)
        if self._tower_backend == "partition":
            self._update_partition_tower(
                current_base_state=next_state,
                refreshed_states=(current_state, next_state),
            )
        else:
            self._refresh_dynamic_tower(current_base_state=next_state)

        reward_value = 0.0 if self._reward_function is None else self._reward_function(edge)
        step_reward = primitive_step_reward(reward_value)
        self._step_rewards.append(step_reward)
        cumulative = summarize_path_rewards(tuple(self._step_rewards))
        return LiveRuntimeView(
            current_base_state=self._explored_graph.current_state(),
            explored_graph=self._explored_graph,
            vista_graph=self._vista_graph,
            ordered_quotient_tiers=self._compatibility_quotient_tiers or (),
            current_position_at_every_tier=self._current_position_at_every_tier,
            current_step_reward=step_reward,
            cumulative_path_reward=cumulative,
            quotient_tier_reward_summaries=(),
            partition_tower_view=self._partition_tower,
            tower_update_result=self._last_tower_update_result,
        )

    @property
    def quotient_tiers(self) -> tuple[QuotientTierView, ...]:
        """Return compatibility quotient-tier readouts, building them lazily."""

        return self.compatibility_quotient_tiers()

    def compatibility_quotient_tiers(self) -> tuple[QuotientTierView, ...]:
        """Build or return cached compatibility quotient-tier readouts."""

        if self._tower_backend != "partition":
            return self._quotient_tiers
        if self._partition_tower is None:
            return ()
        if self._compatibility_quotient_tiers is None:
            self._compatibility_quotient_tiers = (
                self._partition_tower.to_quotient_tier_views()
            )
        return self._compatibility_quotient_tiers

    @property
    def selected_base_edges(self) -> tuple[BaseEdge, ...]:
        return self._selected_base_edges

    @property
    def tier_contraction_records(self) -> tuple[TierContractionRecord, ...]:
        return self._tier_contraction_records

    @property
    def tower_stopping_reason(self) -> str:
        return self._tower_stopping_reason

    def current_deepest_tier(self) -> int | None:
        if self._tower_backend == "partition" and self._partition_tower is not None:
            if not self._partition_tower.state_layers:
                return None
            return len(self._partition_tower.state_layers) - 1
        if not self._quotient_tiers:
            return None
        return self._quotient_tiers[-1].tier

    def project_state_to_tier(self, state: State, tier_index: int) -> object | None:
        if self._tower_backend == "partition" and self._partition_tower is not None:
            return self._partition_tower.current_state_cell(tier_index, state)
        if tier_index < 0 or tier_index >= len(self._quotient_tiers):
            return None
        return self._quotient_tiers[tier_index].projection.project_state(state)

    def project_edge_to_tier(self, edge: BaseEdge, tier_index: int) -> object | None:
        if self._tower_backend == "partition" and self._partition_tower is not None:
            source = self._partition_tower.current_state_cell(tier_index, edge.source)
            target = self._partition_tower.current_state_cell(tier_index, edge.target)
            if source is None or target is None:
                return None
            return (source, edge.action, target)
        if tier_index < 0 or tier_index >= len(self._quotient_tiers):
            return None
        return self._quotient_tiers[tier_index].projection.project_edge(edge)

    def states_share_coset(self, left: State, right: State, tier_index: int) -> bool:
        if self._tower_backend == "partition" and self._partition_tower is not None:
            left_cell = self._partition_tower.current_state_cell(tier_index, left)
            right_cell = self._partition_tower.current_state_cell(tier_index, right)
            return left_cell is not None and left_cell == right_cell
        if tier_index < 0 or tier_index >= len(self._quotient_tiers):
            return False
        return self._quotient_tiers[tier_index].same_coset(left, right)

    def projected_edge_is_trivial_at_tier(self, edge: BaseEdge, tier_index: int) -> bool:
        if self._tower_backend == "partition" and self._partition_tower is not None:
            return self.states_share_coset(edge.source, edge.target, tier_index)
        if tier_index < 0 or tier_index >= len(self._quotient_tiers):
            return True
        return projected_edge_is_trivial(self._quotient_tiers[tier_index], edge)

    def tier_is_point(self, tier_index: int) -> bool:
        if self._tower_backend == "partition" and self._partition_tower is not None:
            if tier_index < 0 or tier_index >= len(self._partition_tower.state_layers):
                return False
            return len(self._partition_tower.state_layers[tier_index].all_cell_ids()) == 1
        if tier_index < 0 or tier_index >= len(self._quotient_tiers):
            return False
        return tier_is_point(self._quotient_tiers[tier_index])

    def tower_is_fully_propagated(self) -> bool:
        if self._tower_backend == "partition" and self._partition_tower is not None:
            deepest = self.current_deepest_tier()
            if deepest is None:
                return False
            return all(
                self.projected_edge_is_trivial_at_tier(edge, deepest)
                for edge in self._selected_base_edges
            )
        return tower_is_fully_propagated(
            self._quotient_tiers,
            self._explored_graph.current_state(),
        )

    @property
    def partition_tower(self) -> PartitionTower | None:
        return self._partition_tower

    @property
    def last_tower_update_result(self) -> TowerUpdateResult | None:
        return self._last_tower_update_result

    def _refresh_dynamic_tower(self, current_base_state: State | None) -> None:
        """Refresh the full current tower from explored/vista state."""

        if self._seed_quotient_tiers and self._contraction_policy is None:
            self._quotient_tiers = self._seed_quotient_tiers
            self._selected_base_edges = ()
            self._tier_contraction_records = ()
            self._tower_stopping_reason = "seeded_static_tiers"
            for tier in self._quotient_tiers:
                position = (
                    None
                    if current_base_state is None
                    else tier.projection.project_state(current_base_state)
                )
                tier.set_current_position(position)
            self._current_position_at_every_tier = tuple(
                tier.current_position for tier in self._quotient_tiers
            )
            self._compatibility_quotient_tiers = self._quotient_tiers
            return

        result = build_legacy_dynamic_tower(
            explored_graph=self._explored_graph,
            vista_graph=self._vista_graph,
            current_base_state=current_base_state,
            contraction_policy=self._contraction_policy,
        )
        self._quotient_tiers = result.ordered_tiers
        self._compatibility_quotient_tiers = self._quotient_tiers
        self._current_position_at_every_tier = tuple(
            tier.current_position for tier in self._quotient_tiers
        )
        self._tier_contraction_records = result.tier_contraction_records
        self._selected_base_edges = (
            ()
            if not result.tier_contraction_records
            else result.tier_contraction_records[0].selected_base_edges
        )
        self._tower_stopping_reason = result.stopping_reason

    def _reset_partition_tower(self, current_base_state: State | None) -> None:
        """Reset the partition backend from the currently visible graph."""

        states, edges = self._visible_base_graph()
        partition_tower = PartitionTower(
            schema=self._contraction_schema,
            loop_policy=self._loop_policy,
            reward_aggregator=self._reward_aggregator,
        )
        result = partition_tower.initialize(
            initial_states=states,
            initial_edges=edges,
            current_state=current_base_state,
        )
        self._partition_tower = partition_tower
        self._apply_partition_update_result(result)

    def _update_partition_tower(
        self,
        current_base_state: State | None,
        refreshed_states: tuple[State, ...] = (),
    ) -> None:
        """Apply visible graph deltas to the partition backend."""

        if self._partition_tower is None:
            self._reset_partition_tower(current_base_state=current_base_state)
            return

        states, edges = self._visible_base_graph_for_states(
            refreshed_states or (() if current_base_state is None else (current_base_state,))
        )
        delta_states = tuple(
            state
            for state in states
            if state not in self._partition_tower.registry.state_id_by_state
        )
        delta_edges = tuple(
            edge
            for edge in edges
            if edge not in self._partition_tower.registry.edge_id_by_edge
        )
        result = self._partition_tower.update_with_delta(
            delta_states=delta_states,
            delta_edges=delta_edges,
            current_state=current_base_state,
            build_morphism=self._build_morphism,
        )
        self._apply_partition_update_result(result)

    def _apply_partition_update_result(self, result: TowerUpdateResult) -> None:
        """Refresh runtime compatibility fields from a partition update."""

        if self._partition_tower is None:
            return
        self._last_tower_update_result = result
        self._compatibility_quotient_tiers = None
        self._quotient_tiers = ()
        self._current_position_at_every_tier = result.current_position_by_tier
        self._selected_base_edges = tuple(
            self._partition_tower.registry.edge_for_id(assignment.edge_id)
            for assignment in result.schema_assignments
            if assignment.block_id is not None
        )
        self._tier_contraction_records = ()
        self._tower_stopping_reason = (
            "partition_update" if result.changed else "partition_noop"
        )

    def _visible_base_graph(self) -> tuple[tuple[State, ...], tuple[BaseEdge, ...]]:
        """Return visible states and edges in stable runtime order."""

        ordered_edges: dict[BaseEdge, None] = {}
        for state in self._explored_graph.visited_states():
            for edge in self._vista_graph.vista_edges(state):
                ordered_edges.setdefault(edge, None)

        ordered_states: dict[State, None] = {}
        for state in self._explored_graph.visited_states():
            ordered_states.setdefault(state, None)
        for edge in ordered_edges:
            ordered_states.setdefault(edge.source, None)
            ordered_states.setdefault(edge.target, None)

        return tuple(ordered_states), tuple(ordered_edges)

    def _visible_base_graph_for_states(
        self,
        states: tuple[State, ...],
    ) -> tuple[tuple[State, ...], tuple[BaseEdge, ...]]:
        """Return visible graph data from a local set of refreshed states."""

        ordered_edges: dict[BaseEdge, None] = {}
        ordered_states: dict[State, None] = {}
        for state in states:
            ordered_states.setdefault(state, None)
            for edge in self._vista_graph.vista_edges(state):
                ordered_edges.setdefault(edge, None)
                ordered_states.setdefault(edge.source, None)
                ordered_states.setdefault(edge.target, None)
        return tuple(ordered_states), tuple(ordered_edges)


@dataclass(frozen=True, slots=True)
class ExploitExploreStepResult:
    """One control-loop result for exploit/explore runtime."""

    decision: ControlAction
    active_tier_state: ActiveTierState
    signal_state: TierSignalState
    learner_summary: LearnerUpdateSummary | None = None
    transition: object | None = None


class ExploitExploreTowerRuntime:
    """Single-active-tier exploit/explore controller runtime."""

    def __init__(
        self,
        *,
        active_tier_state: ActiveTierState,
        tier_configs: dict[int, TierControlConfig],
        controller: ActiveTierController,
        learner: TierLearner,
        executor: LiftResolveExecutor,
        frozen_contexts: dict[int, FrozenLowerContext],
        move_down: Callable[[ActiveTierState], ActiveTierState],
        move_up: Callable[[ActiveTierState], ActiveTierState],
    ) -> None:
        self._active_tier_state = active_tier_state
        self._tier_configs = tier_configs
        self._controller = controller
        self._learner = learner
        self._executor = executor
        self._frozen_contexts = frozen_contexts
        self._move_down = move_down
        self._move_up = move_up
        self._signals: dict[int, TierSignalState] = {}
        self._metrics = TierControlMetrics()

    @property
    def active_tier_state(self) -> ActiveTierState:
        return self._active_tier_state

    @property
    def metrics(self) -> TierControlMetrics:
        return self._metrics

    def signal_state(self, active_tier_state: ActiveTierState | None = None) -> TierSignalState:
        state = self._active_tier_state if active_tier_state is None else active_tier_state
        return self._signals.setdefault(state.active_tier, TierSignalState())

    def step(self) -> ExploitExploreStepResult:
        active_tier_state = self._active_tier_state
        signal = self.signal_state(active_tier_state)
        config = self._tier_configs[active_tier_state.active_tier]
        frozen_context = self._frozen_contexts.get(
            active_tier_state.active_tier,
            FrozenLowerContext(supporting_tier=None),
        )
        decision = self._controller.decide(
            active_tier_state,
            signal,
            config,
            signals_by_tier=self._signals,
            tier_configs=self._tier_configs,
            frozen_context=frozen_context,
            training_due=self._learner.should_train(active_tier_state.event_index),
        )

        learner_summary: LearnerUpdateSummary | None = None
        transition: object | None = None
        if decision.action is ControlAction.LIFT:
            self._active_tier_state = self._move_up(active_tier_state)
        elif decision.action is ControlAction.DESCEND:
            self._active_tier_state = self._move_down(active_tier_state)
        elif decision.action is ControlAction.TRAIN:
            learner_summary = self._learner.train(frozen_context=frozen_context)
            signal.record_td_error(learner_summary.td_error)
            signal.record_outcome(success=learner_summary.success)
            if learner_summary.reward_residual is not None:
                signal.record_reward_residual(learner_summary.reward_residual)
            self._active_tier_state = active_tier_state.advance_event()
        else:
            mode = "explore" if decision.action is ControlAction.EXPLORE else "exploit"
            action = self._learner.behavior_action(active_tier_state.tier_state, mode=mode)
            transition = self._executor.execute(
                active_tier_state,
                action,
                frozen_context=frozen_context,
                mode=mode,
            )
            learner_summary = self._learner.observe(
                transition,
                frozen_context=frozen_context,
            )
            signal.record_visit()
            signal.record_td_error(learner_summary.td_error)
            signal.record_outcome(success=learner_summary.success)
            if learner_summary.reward_residual is not None:
                signal.record_reward_residual(learner_summary.reward_residual)
            target_state = getattr(transition, "target_state", None)
            self._active_tier_state = active_tier_state.advance_event(next_state=target_state)

        self._metrics.record(
            active_tier=self._active_tier_state.active_tier,
            action=decision.action,
        )
        return ExploitExploreStepResult(
            decision=decision.action,
            active_tier_state=self._active_tier_state,
            signal_state=signal,
            learner_summary=learner_summary,
            transition=transition,
        )


__all__ = ["ExploitExploreStepResult", "ExploitExploreTowerRuntime", "TowerRuntime"]
