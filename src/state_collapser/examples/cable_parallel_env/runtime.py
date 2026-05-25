"""Tower-runtime integration layer for CableParallelEnv."""

from __future__ import annotations

from collections.abc import Hashable, Iterable
from dataclasses import dataclass
from typing import cast

from state_collapser.contract.policy import ContractionPolicy
from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.examples.cable_parallel_env.env import (
    ACTION_COUNT,
    CableParallelEnv,
    CableParallelState,
    primitive_transition,
    transition_reward,
)
from state_collapser.graph.hidden_graph import HiddenGraph
from state_collapser.tower.partition.schema import ContractionSchema, DimensionwiseSchema
from state_collapser.tower.runtime import TowerRuntime
from state_collapser.tower.snapshot import LiveRuntimeView


@dataclass(frozen=True, slots=True)
class CableParallelEnvRuntimeReset:
    observation: object
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


@dataclass(frozen=True, slots=True)
class CableParallelEnvRuntimeStep:
    observation: object
    reward: float
    terminated: bool
    truncated: bool
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


def cable_parallel_state_to_core_state(state: CableParallelState) -> State:
    """Translate env state into the package core state surface."""

    return State(payload=state, identity=("cable-parallel-state", state))


def action_index_to_primitive_action(action: int) -> PrimitiveAction:
    """Translate a discrete env action index into a core primitive action."""

    return PrimitiveAction(
        payload=("cable-parallel-action", int(action)),
        identity=f"cable-parallel-action:{int(action)}",
    )


def primitive_action_to_action_index(action: PrimitiveAction) -> int:
    """Translate a core primitive action back into a discrete env action index."""

    payload = cast(tuple[str, int], action.payload)
    tag, index = payload
    if tag != "cable-parallel-action":
        raise ValueError(f"Unsupported primitive action payload: {action.payload!r}")
    return index


def cable_parallel_edge_labels(action_index: int) -> tuple[Hashable, ...]:
    """Return auditable schema labels for one cable-parallel action family."""

    labels: list[Hashable] = ["cable-parallel-transition"]
    if action_index in (0, 1):
        labels.extend(("cable-parallel-x-motion", "cable-parallel-platform-motion"))
    elif action_index in (2, 3):
        labels.extend(("cable-parallel-y-motion", "cable-parallel-platform-motion"))
    elif action_index == 4:
        labels.extend(
            ("cable-parallel-orientation-motion", "cable-parallel-platform-motion")
        )
    elif action_index in (5, 6):
        labels.extend(("cable-parallel-cable-1-tension", "cable-parallel-tension-motion"))
    elif action_index in (7, 8):
        labels.extend(("cable-parallel-cable-2-tension", "cable-parallel-tension-motion"))
    elif action_index in (9, 10):
        labels.extend(("cable-parallel-cable-3-tension", "cable-parallel-tension-motion"))
    return tuple(labels)


class CableParallelHiddenGraph(HiddenGraph):
    """Hidden-graph binding for CableParallelEnv semantics."""

    def is_valid_state(self, state: State) -> bool:
        return isinstance(state.payload, CableParallelState)

    def is_valid_action(self, action: PrimitiveAction) -> bool:
        try:
            index = primitive_action_to_action_index(action)
        except ValueError:
            return False
        return 0 <= index < ACTION_COUNT

    def apply_action(self, state: State, action: PrimitiveAction) -> State | None:
        payload = state.payload
        if not isinstance(payload, CableParallelState):
            return None
        index = primitive_action_to_action_index(action)
        transition = primitive_transition(payload, index)
        return cable_parallel_state_to_core_state(transition.next_state)

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
                    labels=cable_parallel_edge_labels(index),
                )
            )
        return tuple(edges)


def default_cable_parallel_schema() -> ContractionSchema:
    """Return the default smoke schema for CableParallelEnv."""

    return DimensionwiseSchema(("cable-parallel-transition",))


def semantic_cable_parallel_schema() -> ContractionSchema:
    """Return a pose/tension-aware schema for CableParallelEnv."""

    return DimensionwiseSchema(
        (
            "cable-parallel-tension-motion",
            "cable-parallel-platform-motion",
            "cable-parallel-orientation-motion",
            "cable-parallel-cable-1-tension",
            "cable-parallel-cable-2-tension",
            "cable-parallel-cable-3-tension",
        )
    )


class CableParallelEnvRuntime:
    """Package-facing env runtime that couples the env to TowerRuntime."""

    def __init__(
        self,
        env: CableParallelEnv,
        contraction_policy: ContractionPolicy | None = None,
        contraction_schema: ContractionSchema | None = None,
    ) -> None:
        self.env = env
        self.hidden_graph = CableParallelHiddenGraph()
        self._tower_runtime = TowerRuntime(
            hidden_graph=self.hidden_graph,
            contraction_policy=contraction_policy,
            contraction_schema=default_cable_parallel_schema()
            if contraction_schema is None
            else contraction_schema,
            reward_function=self._reward_from_edge,
        )

    def _reward_from_edge(self, edge: BaseEdge) -> float:
        source_payload = edge.source.payload
        target_payload = edge.target.payload
        if not isinstance(source_payload, CableParallelState) or not isinstance(
            target_payload, CableParallelState
        ):
            raise ValueError("CableParallelEnvRuntime requires CableParallelState payloads.")
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
    ) -> CableParallelEnvRuntimeReset:
        observation, info = self.env.reset(seed=seed, options=options)
        initial_core_state = cable_parallel_state_to_core_state(self.env.state)
        runtime_snapshot = self._tower_runtime.reset(initial_state=initial_core_state)
        return CableParallelEnvRuntimeReset(
            observation=observation,
            info=info,
            runtime_snapshot=runtime_snapshot,
        )

    def step(self, action: int) -> CableParallelEnvRuntimeStep:
        observation, reward, terminated, truncated, info = self.env.step(action)
        runtime_snapshot = self._tower_runtime.step(action_index_to_primitive_action(action))
        return CableParallelEnvRuntimeStep(
            observation=observation,
            reward=reward,
            terminated=terminated,
            truncated=truncated,
            info=info,
            runtime_snapshot=runtime_snapshot,
        )


__all__ = [
    "CableParallelEnvRuntime",
    "CableParallelEnvRuntimeReset",
    "CableParallelEnvRuntimeStep",
    "CableParallelHiddenGraph",
    "action_index_to_primitive_action",
    "cable_parallel_edge_labels",
    "cable_parallel_state_to_core_state",
    "default_cable_parallel_schema",
    "primitive_action_to_action_index",
    "semantic_cable_parallel_schema",
]
