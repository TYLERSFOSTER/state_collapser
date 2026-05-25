"""Tower-runtime integration layer for DualArmManipulationEnv."""

from __future__ import annotations

from collections.abc import Hashable, Iterable
from dataclasses import dataclass
from typing import cast

from state_collapser.contract.policy import ContractionPolicy
from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.examples.dual_arm_manipulation_env.env import (
    ACTION_COUNT,
    DualArmManipulationEnv,
    DualArmManipulationState,
    primitive_transition,
    transition_reward,
)
from state_collapser.graph.hidden_graph import HiddenGraph
from state_collapser.tower.partition.schema import ContractionSchema, DimensionwiseSchema
from state_collapser.tower.runtime import TowerRuntime
from state_collapser.tower.snapshot import LiveRuntimeView


@dataclass(frozen=True, slots=True)
class DualArmManipulationEnvRuntimeReset:
    """Combined env/runtime result for adapter reset."""

    observation: object
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


@dataclass(frozen=True, slots=True)
class DualArmManipulationEnvRuntimeStep:
    """Combined env/runtime result for adapter step."""

    observation: object
    reward: float
    terminated: bool
    truncated: bool
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


def dual_arm_state_to_core_state(state: DualArmManipulationState) -> State:
    """Translate env state into the package core state surface."""

    return State(payload=state, identity=("dual-arm-state", state))


def action_index_to_primitive_action(action: int) -> PrimitiveAction:
    """Translate a discrete env action index into a core primitive action."""

    return PrimitiveAction(
        payload=("dual-arm-action", int(action)),
        identity=f"dual-arm-action:{int(action)}",
    )


def primitive_action_to_action_index(action: PrimitiveAction) -> int:
    """Translate a core primitive action back into a discrete env action index."""

    payload = cast(tuple[str, int], action.payload)
    tag, index = payload
    if tag != "dual-arm-action":
        raise ValueError(f"Unsupported primitive action payload: {action.payload!r}")
    return index


def dual_arm_edge_labels(action_index: int) -> tuple[Hashable, ...]:
    """Return auditable schema labels for one dual-arm action family."""

    labels: list[Hashable] = ["dual-arm-transition"]
    if action_index in (0, 1):
        labels.extend(("dual-arm-object-x-motion", "dual-arm-object-motion"))
    elif action_index in (2, 3):
        labels.extend(("dual-arm-object-y-motion", "dual-arm-object-motion"))
    elif action_index == 4:
        labels.extend(("dual-arm-object-orientation-motion", "dual-arm-object-motion"))
    elif action_index == 5:
        labels.extend(
            (
                "dual-arm-left-mode-motion",
                "dual-arm-left-arm-motion",
                "dual-arm-coordination-motion",
            )
        )
    elif action_index == 6:
        labels.extend(
            (
                "dual-arm-right-mode-motion",
                "dual-arm-right-arm-motion",
                "dual-arm-coordination-motion",
            )
        )
    elif action_index in (7, 8):
        labels.extend(
            (
                "dual-arm-left-reach-motion",
                "dual-arm-left-arm-motion",
                "dual-arm-coordination-motion",
            )
        )
    elif action_index in (9, 10):
        labels.extend(
            (
                "dual-arm-right-reach-motion",
                "dual-arm-right-arm-motion",
                "dual-arm-coordination-motion",
            )
        )
    return tuple(labels)


class DualArmManipulationHiddenGraph(HiddenGraph):
    """Hidden-graph binding for DualArmManipulationEnv semantics."""

    def is_valid_state(self, state: State) -> bool:
        payload = state.payload
        return isinstance(payload, DualArmManipulationState)

    def is_valid_action(self, action: PrimitiveAction) -> bool:
        try:
            index = primitive_action_to_action_index(action)
        except ValueError:
            return False
        return 0 <= index < ACTION_COUNT

    def apply_action(self, state: State, action: PrimitiveAction) -> State | None:
        payload = state.payload
        if not isinstance(payload, DualArmManipulationState):
            return None
        index = primitive_action_to_action_index(action)
        transition = primitive_transition(payload, index)
        return dual_arm_state_to_core_state(transition.next_state)

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
                    labels=dual_arm_edge_labels(index),
                )
            )
        return tuple(edges)


def default_dual_arm_schema() -> ContractionSchema:
    """Return the default smoke schema for DualArmManipulationEnv."""

    return DimensionwiseSchema(("dual-arm-transition",))


def semantic_dual_arm_schema() -> ContractionSchema:
    """Return an object/arm coordination schema for DualArmManipulationEnv."""

    return DimensionwiseSchema(
        (
            "dual-arm-coordination-motion",
            "dual-arm-object-motion",
            "dual-arm-left-arm-motion",
            "dual-arm-right-arm-motion",
        )
    )


class DualArmManipulationEnvRuntime:
    """Package-facing env runtime that couples the env to TowerRuntime."""

    def __init__(
        self,
        env: DualArmManipulationEnv,
        contraction_policy: ContractionPolicy | None = None,
        contraction_schema: ContractionSchema | None = None,
    ) -> None:
        self.env = env
        self.hidden_graph = DualArmManipulationHiddenGraph()
        self._tower_runtime = TowerRuntime(
            hidden_graph=self.hidden_graph,
            contraction_policy=contraction_policy,
            contraction_schema=default_dual_arm_schema()
            if contraction_schema is None
            else contraction_schema,
            reward_function=self._reward_from_edge,
        )

    def _reward_from_edge(self, edge: BaseEdge) -> float:
        source_payload = edge.source.payload
        target_payload = edge.target.payload
        if not isinstance(source_payload, DualArmManipulationState) or not isinstance(
            target_payload, DualArmManipulationState
        ):
            raise ValueError(
                "DualArmManipulationEnvRuntime requires DualArmManipulationState payloads."
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
    ) -> DualArmManipulationEnvRuntimeReset:
        observation, info = self.env.reset(seed=seed, options=options)
        initial_core_state = dual_arm_state_to_core_state(self.env.state)
        runtime_snapshot = self._tower_runtime.reset(initial_state=initial_core_state)
        return DualArmManipulationEnvRuntimeReset(
            observation=observation,
            info=info,
            runtime_snapshot=runtime_snapshot,
        )

    def step(self, action: int) -> DualArmManipulationEnvRuntimeStep:
        observation, reward, terminated, truncated, info = self.env.step(action)
        runtime_snapshot = self._tower_runtime.step(action_index_to_primitive_action(action))
        return DualArmManipulationEnvRuntimeStep(
            observation=observation,
            reward=reward,
            terminated=terminated,
            truncated=truncated,
            info=info,
            runtime_snapshot=runtime_snapshot,
        )


__all__ = [
    "DualArmManipulationEnvRuntime",
    "DualArmManipulationEnvRuntimeReset",
    "DualArmManipulationEnvRuntimeStep",
    "DualArmManipulationHiddenGraph",
    "action_index_to_primitive_action",
    "default_dual_arm_schema",
    "dual_arm_edge_labels",
    "dual_arm_state_to_core_state",
    "primitive_action_to_action_index",
    "semantic_dual_arm_schema",
]
