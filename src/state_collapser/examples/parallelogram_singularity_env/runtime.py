"""Tower-runtime integration layer for ParallelogramSingularityEnv."""

from __future__ import annotations

from collections.abc import Hashable, Iterable
from dataclasses import dataclass
from typing import cast

from state_collapser.contract.policy import ContractionPolicy
from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.examples.parallelogram_singularity_env.env import (
    ACTION_COUNT,
    ParallelogramSingularityEnv,
    ParallelogramState,
    is_singular_state,
    primitive_transition,
    transition_reward,
)
from state_collapser.graph.hidden_graph import HiddenGraph
from state_collapser.tower.partition.schema import ContractionSchema, DimensionwiseSchema
from state_collapser.tower.runtime import TowerRuntime
from state_collapser.tower.snapshot import LiveRuntimeView


@dataclass(frozen=True, slots=True)
class ParallelogramEnvRuntimeReset:
    observation: object
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


@dataclass(frozen=True, slots=True)
class ParallelogramEnvRuntimeStep:
    observation: object
    reward: float
    terminated: bool
    truncated: bool
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


def parallelogram_state_to_core_state(state: ParallelogramState) -> State:
    """Translate env state into the package core state surface."""

    return State(payload=state, identity=("parallelogram-state", state))


def action_index_to_primitive_action(action: int) -> PrimitiveAction:
    """Translate a discrete env action index into a core primitive action."""

    return PrimitiveAction(
        payload=("parallelogram-action", int(action)),
        identity=f"parallelogram-action:{int(action)}",
    )


def primitive_action_to_action_index(action: PrimitiveAction) -> int:
    """Translate a core primitive action back into a discrete env action index."""

    payload = cast(tuple[str, int], action.payload)
    tag, index = payload
    if tag != "parallelogram-action":
        raise ValueError(f"Unsupported primitive action payload: {action.payload!r}")
    return index


def parallelogram_edge_labels(
    source: ParallelogramState,
    action_index: int,
    target: ParallelogramState,
) -> tuple[Hashable, ...]:
    """Return auditable schema labels for one parallelogram transition."""

    labels: list[Hashable] = ["parallelogram-transition"]
    if action_index in (0, 1):
        labels.append("parallelogram-left-angle")
    elif action_index in (2, 3):
        labels.append("parallelogram-right-angle")
    elif action_index in (4, 5):
        labels.append("parallelogram-span")
    elif action_index == 6:
        labels.append("parallelogram-alignment-mode")

    source_is_singular = is_singular_state(source)
    target_is_singular = is_singular_state(target)
    if source_is_singular:
        labels.append("parallelogram-singular-source")
    if target_is_singular:
        labels.append("parallelogram-singular-target")
    if not source_is_singular and target_is_singular:
        labels.append("parallelogram-enters-singular-regime")
    if source_is_singular and not target_is_singular:
        labels.append("parallelogram-leaves-singular-regime")
    return tuple(labels)


class ParallelogramHiddenGraph(HiddenGraph):
    """Hidden-graph binding for ParallelogramSingularityEnv semantics."""

    def is_valid_state(self, state: State) -> bool:
        return isinstance(state.payload, ParallelogramState)

    def is_valid_action(self, action: PrimitiveAction) -> bool:
        try:
            index = primitive_action_to_action_index(action)
        except ValueError:
            return False
        return 0 <= index < ACTION_COUNT

    def apply_action(self, state: State, action: PrimitiveAction) -> State | None:
        payload = state.payload
        if not isinstance(payload, ParallelogramState):
            return None
        index = primitive_action_to_action_index(action)
        transition = primitive_transition(payload, index)
        return parallelogram_state_to_core_state(transition.next_state)

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
            source_payload = state.payload
            target_payload = target.payload
            if not isinstance(source_payload, ParallelogramState) or not isinstance(
                target_payload, ParallelogramState
            ):
                continue
            edges.append(
                BaseEdge(
                    source=state,
                    action=action,
                    target=target,
                    labels=parallelogram_edge_labels(source_payload, index, target_payload),
                )
            )
        return tuple(edges)


def default_parallelogram_schema() -> ContractionSchema:
    """Return the default smoke schema for ParallelogramSingularityEnv."""

    return DimensionwiseSchema(("parallelogram-transition",))


def semantic_parallelogram_schema() -> ContractionSchema:
    """Return a singularity-aware schema for ParallelogramSingularityEnv."""

    return DimensionwiseSchema(
        (
            "parallelogram-enters-singular-regime",
            "parallelogram-leaves-singular-regime",
            "parallelogram-span",
            "parallelogram-alignment-mode",
            "parallelogram-left-angle",
            "parallelogram-right-angle",
        )
    )


class ParallelogramSingularityEnvRuntime:
    """Package-facing env runtime that couples the env to TowerRuntime."""

    def __init__(
        self,
        env: ParallelogramSingularityEnv,
        contraction_policy: ContractionPolicy | None = None,
        contraction_schema: ContractionSchema | None = None,
    ) -> None:
        self.env = env
        self.hidden_graph = ParallelogramHiddenGraph()
        self._tower_runtime = TowerRuntime(
            hidden_graph=self.hidden_graph,
            contraction_policy=contraction_policy,
            contraction_schema=default_parallelogram_schema()
            if contraction_schema is None
            else contraction_schema,
            reward_function=self._reward_from_edge,
        )

    def _reward_from_edge(self, edge: BaseEdge) -> float:
        source_payload = edge.source.payload
        target_payload = edge.target.payload
        if not isinstance(source_payload, ParallelogramState) or not isinstance(
            target_payload, ParallelogramState
        ):
            raise ValueError(
                "ParallelogramSingularityEnvRuntime requires ParallelogramState payloads."
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
    ) -> ParallelogramEnvRuntimeReset:
        observation, info = self.env.reset(seed=seed, options=options)
        initial_core_state = parallelogram_state_to_core_state(self.env.state)
        runtime_snapshot = self._tower_runtime.reset(initial_state=initial_core_state)
        return ParallelogramEnvRuntimeReset(
            observation=observation,
            info=info,
            runtime_snapshot=runtime_snapshot,
        )

    def step(self, action: int) -> ParallelogramEnvRuntimeStep:
        observation, reward, terminated, truncated, info = self.env.step(action)
        runtime_snapshot = self._tower_runtime.step(action_index_to_primitive_action(action))
        return ParallelogramEnvRuntimeStep(
            observation=observation,
            reward=reward,
            terminated=terminated,
            truncated=truncated,
            info=info,
            runtime_snapshot=runtime_snapshot,
        )


__all__ = [
    "ParallelogramEnvRuntimeReset",
    "ParallelogramEnvRuntimeStep",
    "ParallelogramHiddenGraph",
    "ParallelogramSingularityEnvRuntime",
    "action_index_to_primitive_action",
    "default_parallelogram_schema",
    "parallelogram_edge_labels",
    "parallelogram_state_to_core_state",
    "primitive_action_to_action_index",
    "semantic_parallelogram_schema",
]
