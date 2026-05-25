"""Tower-runtime integration layer for PlateSupportEnv."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import cast

from state_collapser.contract.policy import ContractionPolicy, SeededRandomContractionPolicy
from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.examples.plate_support_env.env import (
    ACTION_COUNT,
    PlateSupportEnv,
    PlateSupportState,
    all_valid_states,
    encode_observation,
    primitive_transition,
    transition_reward,
    transition_terminated,
    transition_truncated,
)
from state_collapser.graph.hidden_graph import HiddenGraph
from state_collapser.tower.control import (
    ActiveTierController,
    ActiveTierState,
    FrozenLowerContext,
    TierControlConfig,
    TierLearner,
)
from state_collapser.tower.control.transition import ActiveTierTransition
from state_collapser.tower.partition.schema import ContractionSchema, DimensionwiseSchema
from state_collapser.tower.runtime import ExploitExploreTowerRuntime, TowerRuntime
from state_collapser.tower.snapshot import LiveRuntimeView


@dataclass(frozen=True, slots=True)
class PlateSupportEnvRuntimeReset:
    """Combined env/runtime result for adapter reset."""

    observation: object
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


@dataclass(frozen=True, slots=True)
class PlateSupportEnvRuntimeStep:
    """Combined env/runtime result for adapter step."""

    observation: object
    reward: float
    terminated: bool
    truncated: bool
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


@dataclass(frozen=True, slots=True)
class PlateSupportExploitExploreRuntimeReset:
    """Reset result for the exploit/explore runtime path."""

    observation: object
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView
    active_tier_state: ActiveTierState


@dataclass(frozen=True, slots=True)
class PlateSupportExploitExploreRuntimeStep:
    """One exploit/explore control-loop step result for PlateSupportEnv."""

    observation: object
    reward: float
    terminated: bool
    truncated: bool
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView
    active_tier_state: ActiveTierState
    control_action: str


def plate_support_state_to_core_state(state: PlateSupportState) -> State:
    """Translate env state into the package core state surface."""

    return State(payload=state, identity=("plate-support-state", state))


def action_index_to_primitive_action(action: int) -> PrimitiveAction:
    """Translate a discrete env action index into a core primitive action."""

    return PrimitiveAction(
        payload=("plate-support-action", int(action)),
        identity=f"plate-support-action:{int(action)}",
    )


def primitive_action_to_action_index(action: PrimitiveAction) -> int:
    """Translate a core primitive action back into a discrete env action index."""

    payload = cast(tuple[str, int], action.payload)
    tag, index = payload
    if tag != "plate-support-action":
        raise ValueError(f"Unsupported primitive action payload: {action.payload!r}")
    return index


def coarse_plate_support_position(state: PlateSupportState) -> tuple[object, ...]:
    """Return a coarse descriptive key for one env state."""

    support_pattern = tuple(int(extension > 0) for extension in (state.e1, state.e2, state.e3))
    return (
        "plate-support-coarse",
        state.x_idx // 2,
        state.y_idx // 2,
        state.theta_idx,
        support_pattern,
    )


def fine_plate_support_position(state: PlateSupportState) -> tuple[object, ...]:
    """Return a fine descriptive key for one env state."""

    return (
        "plate-support-fine",
        state.x_idx,
        state.y_idx,
        state.theta_idx,
        state.e1,
        state.e2,
        state.e3,
    )


class PlateSupportHiddenGraph(HiddenGraph):
    """Hidden-graph binding for PlateSupportEnv semantics."""

    def is_valid_state(self, state: State) -> bool:
        payload = state.payload
        return isinstance(payload, PlateSupportState) and payload in set(all_valid_states())

    def is_valid_action(self, action: PrimitiveAction) -> bool:
        try:
            index = primitive_action_to_action_index(action)
        except ValueError:
            return False
        return 0 <= index < ACTION_COUNT

    def apply_action(self, state: State, action: PrimitiveAction) -> State | None:
        state_payload = state.payload
        if not isinstance(state_payload, PlateSupportState):
            return None
        index = primitive_action_to_action_index(action)
        transition = primitive_transition(state_payload, index)
        return plate_support_state_to_core_state(transition.next_state)

    def is_valid_edge(self, edge: BaseEdge) -> bool:
        return self.apply_action(edge.source, edge.action) == edge.target

    def out_actions(self, state: State) -> Iterable[PrimitiveAction]:
        return tuple(action_index_to_primitive_action(index) for index in range(ACTION_COUNT))

    def out_neighbors(self, state: State) -> Iterable[State]:
        return tuple(
            target
            for index in range(ACTION_COUNT)
            if (target := self.apply_action(state, action_index_to_primitive_action(index)))
            is not None
        )

    def out_edges(self, state: State) -> Iterable[BaseEdge]:
        edges: list[BaseEdge] = []
        for index in range(ACTION_COUNT):
            action = action_index_to_primitive_action(index)
            target = self.apply_action(state, action)
            if target is None:
                continue
            edges.append(
                BaseEdge(
                    source=state,
                    action=action,
                    target=target,
                    labels=("plate-support-transition",),
                )
            )
        return tuple(edges)


def default_plate_support_schema() -> ContractionSchema:
    """Return the default smoke schema for PlateSupportEnv tower contraction."""

    return DimensionwiseSchema(("plate-support-transition",))


class PlateSupportEnvRuntime:
    """Package-facing env runtime that couples PlateSupportEnv to TowerRuntime."""

    def __init__(
        self,
        env: PlateSupportEnv,
        contraction_policy: ContractionPolicy | None = None,
        contraction_schema: ContractionSchema | None = None,
    ) -> None:
        self.env = env
        self.hidden_graph = PlateSupportHiddenGraph()
        self._tower_runtime = TowerRuntime(
            hidden_graph=self.hidden_graph,
            contraction_policy=contraction_policy,
            contraction_schema=default_plate_support_schema()
            if contraction_schema is None
            else contraction_schema,
            reward_function=self._reward_from_edge,
        )

    def _reward_from_edge(self, edge: BaseEdge) -> float:
        source_payload = edge.source.payload
        target_payload = edge.target.payload
        if not isinstance(source_payload, PlateSupportState) or not isinstance(
            target_payload, PlateSupportState
        ):
            raise ValueError(
                "PlateSupportEnvRuntime reward mapping requires PlateSupportState payloads."
            )
        action_index = primitive_action_to_action_index(edge.action)
        return transition_reward(source_payload, action_index, target_payload)

    @property
    def quotient_tiers(self) -> tuple[object, ...]:
        return self._tower_runtime.quotient_tiers

    @property
    def tower_runtime(self) -> TowerRuntime:
        return self._tower_runtime

    def reset(
        self, *, seed: int | None = None, options: dict[str, object] | None = None
    ) -> PlateSupportEnvRuntimeReset:
        observation, info = self.env.reset(seed=seed, options=options)
        initial_core_state = plate_support_state_to_core_state(self.env.state)
        runtime_snapshot = self._tower_runtime.reset(initial_state=initial_core_state)
        return PlateSupportEnvRuntimeReset(
            observation=observation,
            info=info,
            runtime_snapshot=runtime_snapshot,
        )

    def step(self, action: int) -> PlateSupportEnvRuntimeStep:
        observation, reward, terminated, truncated, info = self.env.step(action)
        runtime_snapshot = self._tower_runtime.step(action_index_to_primitive_action(action))
        return PlateSupportEnvRuntimeStep(
            observation=observation,
            reward=reward,
            terminated=terminated,
            truncated=truncated,
            info=info,
            runtime_snapshot=runtime_snapshot,
        )


class PlateSupportLiftResolveExecutor:
    """Lift/resolve executor for PlateSupportEnv exploit/explore control."""

    def __init__(self, runtime: PlateSupportEnvRuntime) -> None:
        self._runtime = runtime
        self.last_step_result: PlateSupportEnvRuntimeStep | None = None

    def execute(
        self,
        active_tier_state: ActiveTierState,
        action: object,
        *,
        frozen_context: FrozenLowerContext,
        mode: str,
    ) -> ActiveTierTransition:
        action_index = cast(int, action)
        source_state = active_tier_state.tier_state
        step_result = self._runtime.step(action_index)
        self.last_step_result = step_result
        positions = step_result.runtime_snapshot.current_position_at_every_tier
        target_state = (
            None
            if active_tier_state.active_tier >= len(positions)
            else positions[active_tier_state.active_tier]
        )
        return ActiveTierTransition(
            tier_index=active_tier_state.active_tier,
            source_state=source_state,
            action=action_index,
            target_state=target_state,
            aggregated_reward=step_result.reward,
            duration=1,
            context_version=frozen_context.version,
            representative_jump=("plate-support-rep-jump", mode, active_tier_state.active_tier),
            success=not step_result.info.get("invalid_move", False),
        )


class PlateSupportExploitExploreRuntime:
    """Exploit/explore runtime binding for PlateSupportEnv."""

    def __init__(
        self,
        env: PlateSupportEnv,
        *,
        tier_configs: dict[int, TierControlConfig] | None = None,
        contraction_policy: ContractionPolicy | None = None,
        learner: TierLearner | None = None,
    ) -> None:
        from state_collapser.examples.plate_support_env.training import PlateSupportTierLearner

        self.base_runtime = PlateSupportEnvRuntime(
            env=env,
            contraction_policy=(
                SeededRandomContractionPolicy(seed=0, sample_size=1)
                if contraction_policy is None
                else contraction_policy
            ),
        )
        self.env = env
        self.learner = PlateSupportTierLearner() if learner is None else learner
        self._control_runtime: ExploitExploreTowerRuntime | None = None
        self._executor = PlateSupportLiftResolveExecutor(self.base_runtime)
        self._last_runtime_snapshot: LiveRuntimeView | None = None
        self._base_tier_configs = (
            {
                0: TierControlConfig(epsilon=0.2, min_visit_count=2, training_interval=3),
                1: TierControlConfig(epsilon=0.2, min_visit_count=2, training_interval=3),
            }
            if tier_configs is None
            else tier_configs
        )

    def reset(
        self, *, seed: int | None = None, options: dict[str, object] | None = None
    ) -> PlateSupportExploitExploreRuntimeReset:
        base_reset = self.base_runtime.reset(seed=seed, options=options)
        self._last_runtime_snapshot = base_reset.runtime_snapshot
        positions = base_reset.runtime_snapshot.current_position_at_every_tier
        deepest_known_tier = len(positions) - 1
        tier_configs = self._resolved_tier_configs(deepest_known_tier)
        initial_state = ActiveTierState(
            active_tier=0,
            tier_state=None if not positions else positions[0],
            deepest_known_tier=deepest_known_tier,
        )
        frozen_contexts = self._build_frozen_contexts(positions)
        def move_down(state: ActiveTierState) -> ActiveTierState:
            if self._last_runtime_snapshot is None:
                return state
            current_positions = self._last_runtime_snapshot.current_position_at_every_tier
            next_tier = state.active_tier + 1
            next_state = next_tier < len(current_positions) and current_positions[next_tier] or None
            return state.descend(next_state=next_state)

        def move_up(state: ActiveTierState) -> ActiveTierState:
            if self._last_runtime_snapshot is None:
                return state
            current_positions = self._last_runtime_snapshot.current_position_at_every_tier
            next_tier = state.active_tier - 1
            next_state = (
                current_positions[next_tier]
                if 0 <= next_tier < len(current_positions)
                else None
            )
            return state.lift(next_state=next_state)

        self._control_runtime = ExploitExploreTowerRuntime(
            active_tier_state=initial_state,
            tier_configs=tier_configs,
            controller=ActiveTierController(),
            learner=self.learner,
            executor=self._executor,
            frozen_contexts=frozen_contexts,
            move_down=move_down,
            move_up=move_up,
        )
        snapshot = self._with_control_fields(
            base_reset.runtime_snapshot,
            active_tier=initial_state.active_tier,
            control_action=None,
        )
        return PlateSupportExploitExploreRuntimeReset(
            observation=base_reset.observation,
            info=base_reset.info,
            runtime_snapshot=snapshot,
            active_tier_state=initial_state,
        )

    def step(self) -> PlateSupportExploitExploreRuntimeStep:
        if self._control_runtime is None:
            raise ValueError("reset(...) must be called before step().")
        if self._last_runtime_snapshot is None:
            raise ValueError("Exploit/explore runtime requires a base runtime snapshot.")
        decision = self._control_runtime.step()
        base_snapshot = self._last_runtime_snapshot
        info: dict[str, object]
        reward = 0.0
        terminated = False
        truncated = False
        observation = encode_observation(self.env.state)
        if decision.transition is not None:
            if self._executor.last_step_result is None:
                raise ValueError("Executor did not retain the latest base runtime step.")
            base_snapshot = self._executor.last_step_result.runtime_snapshot
            self._last_runtime_snapshot = base_snapshot
            self._sync_control_runtime_with_snapshot(base_snapshot)
            reward = cast(ActiveTierTransition, decision.transition).aggregated_reward
            info = {"state": self.env.state}
            terminated = transition_terminated(self.env.state)
            truncated = transition_truncated(self.env.step_count, terminated)
        else:
            info = {"state": self.env.state}
            self._sync_control_runtime_with_snapshot(base_snapshot)
        snapshot = self._with_control_fields(
            base_snapshot,
            active_tier=decision.active_tier_state.active_tier,
            control_action=decision.decision.value,
        )
        return PlateSupportExploitExploreRuntimeStep(
            observation=observation,
            reward=reward,
            terminated=terminated,
            truncated=truncated,
            info=info,
            runtime_snapshot=snapshot,
            active_tier_state=decision.active_tier_state,
            control_action=decision.decision.value,
        )

    def _with_control_fields(
        self,
        snapshot: LiveRuntimeView,
        *,
        active_tier: int,
        control_action: str | None,
    ) -> LiveRuntimeView:
        return LiveRuntimeView(
            current_base_state=snapshot.current_base_state,
            explored_graph=snapshot.explored_graph,
            vista_graph=snapshot.vista_graph,
            ordered_quotient_tiers=snapshot.ordered_quotient_tiers,
            current_position_at_every_tier=snapshot.current_position_at_every_tier,
            current_step_reward=snapshot.current_step_reward,
            cumulative_path_reward=snapshot.cumulative_path_reward,
            quotient_tier_reward_summaries=snapshot.quotient_tier_reward_summaries,
            active_control_tier=active_tier,
            last_control_action=control_action,
            partition_tower_view=snapshot.partition_tower_view,
            tower_update_result=snapshot.tower_update_result,
        )

    def _build_frozen_contexts(
        self,
        positions: tuple[object | None, ...],
    ) -> dict[int, FrozenLowerContext]:
        contexts: dict[int, FrozenLowerContext] = {}
        for tier_index in range(len(positions)):
            supporting_tier = tier_index + 1 if tier_index + 1 < len(positions) else None
            representative = None if supporting_tier is None else positions[supporting_tier]
            contexts[tier_index] = FrozenLowerContext(
                supporting_tier=supporting_tier,
                representative_data=representative,
                version=0,
            )
        return contexts

    def _resolved_tier_configs(self, deepest_known_tier: int) -> dict[int, TierControlConfig]:
        if deepest_known_tier < 0:
            return {}
        configs: dict[int, TierControlConfig] = {}
        template = self._base_tier_configs[max(self._base_tier_configs)]
        for tier_index in range(deepest_known_tier + 1):
            configs[tier_index] = self._base_tier_configs.get(tier_index, template)
        return configs

    def _sync_control_runtime_with_snapshot(self, snapshot: LiveRuntimeView) -> None:
        if self._control_runtime is None:
            return
        positions = snapshot.current_position_at_every_tier
        deepest_known_tier = len(positions) - 1
        self._control_runtime._tier_configs = self._resolved_tier_configs(deepest_known_tier)
        self._control_runtime._frozen_contexts = self._build_frozen_contexts(positions)
        clamped_active_tier = (
            0
            if deepest_known_tier < 0
            else min(self._control_runtime.active_tier_state.active_tier, deepest_known_tier)
        )
        self._control_runtime._active_tier_state = ActiveTierState(
            active_tier=clamped_active_tier,
            tier_state=(
                None
                if clamped_active_tier >= len(positions)
                else positions[clamped_active_tier]
            ),
            deepest_known_tier=deepest_known_tier,
            context_version=self._control_runtime.active_tier_state.context_version,
            event_index=self._control_runtime.active_tier_state.event_index,
        )


__all__ = [
    "PlateSupportExploitExploreRuntime",
    "PlateSupportExploitExploreRuntimeReset",
    "PlateSupportExploitExploreRuntimeStep",
    "PlateSupportLiftResolveExecutor",
    "PlateSupportEnvRuntime",
    "PlateSupportEnvRuntimeReset",
    "PlateSupportEnvRuntimeStep",
    "PlateSupportHiddenGraph",
    "action_index_to_primitive_action",
    "default_plate_support_schema",
    "fine_plate_support_position",
    "plate_support_state_to_core_state",
    "primitive_action_to_action_index",
]
