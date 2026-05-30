"""Tower-runtime integration layer for RlCounterpointEnv."""

from __future__ import annotations

from collections.abc import Hashable, Iterable
from dataclasses import dataclass
from typing import cast

from state_collapser.contract.policy import ContractionPolicy
from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.examples.rl_counterpoint_v3.env import (
    RlCounterpointEnv,
    RlCounterpointGraphSpec,
    RlCounterpointState,
    action_index_to_step_delta,
    all_valid_states,
    primitive_transition,
    transition_reward,
)
from state_collapser.graph.hidden_graph import HiddenGraph
from state_collapser.tower.partition.schema import ContractionSchema, DimensionwiseSchema
from state_collapser.tower.runtime import TowerRuntime
from state_collapser.tower.snapshot import LiveRuntimeView


@dataclass(frozen=True, slots=True)
class RlCounterpointEnvRuntimeReset:
    """Combined environment and tower snapshot returned from reset."""

    observation: object
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


@dataclass(frozen=True, slots=True)
class RlCounterpointEnvRuntimeStep:
    """Combined environment and tower snapshot returned from one step."""

    observation: object
    reward: float
    terminated: bool
    truncated: bool
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


def rl_counterpoint_state_to_core_state(state: RlCounterpointState) -> State:
    """Translate a counterpoint environment state into a core graph state."""

    return State(payload=state, identity=("rl-counterpoint-v3-state", state))


def action_index_to_primitive_action(action: int) -> PrimitiveAction:
    """Translate a counterpoint action index into a primitive action."""

    return PrimitiveAction(
        payload=("rl-counterpoint-v3-action", int(action)),
        identity=f"rl-counterpoint-v3-action:{int(action)}",
    )


def primitive_action_to_action_index(action: PrimitiveAction) -> int:
    """Translate a primitive action back into a counterpoint action index."""

    payload = cast(tuple[str, int], action.payload)
    tag, index = payload
    if tag != "rl-counterpoint-v3-action":
        raise ValueError(f"Unsupported primitive action payload: {action.payload!r}")
    return index


def rl_counterpoint_edge_labels(
    source: RlCounterpointState,
    action_index: int,
    target: RlCounterpointState,
    spec: RlCounterpointGraphSpec,
) -> tuple[Hashable, ...]:
    """Return neutral motion-family labels for one counterpoint edge."""

    del source, target
    step_delta = action_index_to_step_delta(action_index, spec=spec)
    moving_deltas = tuple(delta for delta in step_delta if delta != 0)
    labels: list[Hashable] = [
        "rl-counterpoint-v3-transition",
        "rl-counterpoint-v3-beat-advance",
    ]
    if step_delta[0] != 0:
        labels.append("rl-counterpoint-v3-bass-motion")
    if step_delta[1] != 0:
        labels.append("rl-counterpoint-v3-inner-motion")
    if step_delta[2] != 0:
        labels.append("rl-counterpoint-v3-upper-motion")
    if moving_deltas:
        labels.append("rl-counterpoint-v3-any-voice-motion")
    if moving_deltas and all(abs(delta) <= 1 for delta in moving_deltas):
        labels.append("rl-counterpoint-v3-stepwise-motion")
    if any(abs(delta) > 1 for delta in moving_deltas):
        labels.append("rl-counterpoint-v3-leap-motion")

    signs = tuple(1 if delta > 0 else -1 for delta in moving_deltas)
    if len(signs) == 1:
        labels.append("rl-counterpoint-v3-oblique-motion")
    elif signs and all(sign == signs[0] for sign in signs):
        labels.append("rl-counterpoint-v3-parallel-direction-motion")
    elif len(set(signs)) > 1:
        labels.append("rl-counterpoint-v3-contrary-direction-motion")
    return tuple(labels)


class RlCounterpointHiddenGraph(HiddenGraph):
    """Hidden-graph binding for counterpoint transition semantics."""

    def __init__(self, spec: RlCounterpointGraphSpec) -> None:
        """Cache the graph spec, valid states, and action count."""

        self.spec = spec
        self._valid_states = frozenset(all_valid_states(spec))
        self._action_count = (2 * self.spec.max_step_size + 1) ** 3 - 1

    def is_valid_state(self, state: State) -> bool:
        """Return whether a core state wraps a valid counterpoint state."""

        payload = state.payload
        return isinstance(payload, RlCounterpointState) and payload in self._valid_states

    def is_valid_action(self, action: PrimitiveAction) -> bool:
        """Return whether a primitive action wraps a valid action index."""

        try:
            index = primitive_action_to_action_index(action)
        except ValueError:
            return False
        return 0 <= index < len(self._action_space_indices)

    @property
    def _action_space_indices(self) -> range:
        """Return valid primitive action indices for internal validation."""

        return range(self.action_count)

    @property
    def action_count(self) -> int:
        """Return the number of nonzero step-delta actions."""

        return self._action_count

    def apply_action(self, state: State, action: PrimitiveAction) -> State | None:
        """Apply one primitive action through the counterpoint transition model."""

        payload = state.payload
        if not isinstance(payload, RlCounterpointState):
            return None
        index = primitive_action_to_action_index(action)
        transition = primitive_transition(payload, index, spec=self.spec)
        return rl_counterpoint_state_to_core_state(transition.next_state)

    def is_valid_edge(self, edge: BaseEdge) -> bool:
        """Return whether an edge matches the deterministic transition model."""

        return self.apply_action(edge.source, edge.action) == edge.target

    def out_actions(self, state: State) -> Iterable[PrimitiveAction]:
        """Return all primitive actions available from a valid state."""

        return tuple(
            action_index_to_primitive_action(index)
            for index in self._action_space_indices
        )

    def out_neighbors(self, state: State) -> Iterable[State]:
        """Return all deterministic successor states from a state."""

        return tuple(
            target
            for index in self._action_space_indices
            if (
                target := self.apply_action(
                    state,
                    action_index_to_primitive_action(index),
                )
            )
            is not None
        )

    def out_edges(self, state: State) -> Iterable[BaseEdge]:
        """Return all deterministic outgoing base edges from a state."""

        edges: list[BaseEdge] = []
        for index in self._action_space_indices:
            action = action_index_to_primitive_action(index)
            target = self.apply_action(state, action)
            if target is None:
                continue
            source_payload = state.payload
            target_payload = target.payload
            if not isinstance(source_payload, RlCounterpointState) or not isinstance(
                target_payload, RlCounterpointState
            ):
                continue
            edges.append(
                BaseEdge(
                    source=state,
                    action=action,
                    target=target,
                    labels=rl_counterpoint_edge_labels(
                        source_payload,
                        index,
                        target_payload,
                        self.spec,
                    ),
                )
            )
        return tuple(edges)


def default_rl_counterpoint_v3_schema() -> ContractionSchema:
    """Return the default smoke schema for RlCounterpointEnv."""

    return DimensionwiseSchema(("rl-counterpoint-v3-transition",))


def semantic_rl_counterpoint_v3_schema() -> ContractionSchema:
    """Return a voice-motion schema for RlCounterpointEnv."""

    return DimensionwiseSchema(
        (
            "rl-counterpoint-v3-bass-motion",
            "rl-counterpoint-v3-inner-motion",
            "rl-counterpoint-v3-upper-motion",
            "rl-counterpoint-v3-contrary-direction-motion",
            "rl-counterpoint-v3-oblique-motion",
            "rl-counterpoint-v3-parallel-direction-motion",
        )
    )


class RlCounterpointEnvRuntime:
    """Couple `RlCounterpointEnv` to `TowerRuntime` for examples and tests."""

    def __init__(
        self,
        env: RlCounterpointEnv,
        contraction_policy: ContractionPolicy | None = None,
        contraction_schema: ContractionSchema | None = None,
    ) -> None:
        """Create the environment runtime and its package tower runtime."""

        self.env = env
        self.hidden_graph = RlCounterpointHiddenGraph(env.graph_spec)
        self._tower_runtime = TowerRuntime(
            hidden_graph=self.hidden_graph,
            contraction_policy=contraction_policy,
            contraction_schema=default_rl_counterpoint_v3_schema()
            if contraction_schema is None
            else contraction_schema,
            reward_function=self._reward_from_edge,
        )

    def _reward_from_edge(self, edge: BaseEdge) -> float:
        source_payload = edge.source.payload
        target_payload = edge.target.payload
        if not isinstance(source_payload, RlCounterpointState) or not isinstance(
            target_payload, RlCounterpointState
        ):
            raise ValueError(
                "RlCounterpointEnvRuntime reward mapping requires RlCounterpointState payloads."
            )
        action_index = primitive_action_to_action_index(edge.action)
        return transition_reward(
            source_payload,
            action_index,
            target_payload,
            history=(source_payload,),
            spec=self.env.graph_spec,
        ).reward

    @property
    def quotient_tiers(self) -> tuple[object, ...]:
        """Return compatibility quotient-tier readouts from the tower runtime."""

        return self._tower_runtime.quotient_tiers

    @property
    def tower_runtime(self) -> TowerRuntime:
        """Return the underlying package-owned tower runtime."""

        return self._tower_runtime

    def reset(
        self, *, seed: int | None = None, options: dict[str, object] | None = None
    ) -> RlCounterpointEnvRuntimeReset:
        """Reset the environment and initialize the tower at the start state."""

        observation, info = self.env.reset(seed=seed, options=options)
        initial_core_state = rl_counterpoint_state_to_core_state(self.env.state)
        runtime_snapshot = self._tower_runtime.reset(initial_state=initial_core_state)
        return RlCounterpointEnvRuntimeReset(
            observation=observation,
            info=info,
            runtime_snapshot=runtime_snapshot,
        )

    def step(self, action: int) -> RlCounterpointEnvRuntimeStep:
        """Step the environment and update the tower with the realized action."""

        observation, reward, terminated, truncated, info = self.env.step(action)
        runtime_snapshot = self._tower_runtime.step(action_index_to_primitive_action(action))
        return RlCounterpointEnvRuntimeStep(
            observation=observation,
            reward=reward,
            terminated=terminated,
            truncated=truncated,
            info=info,
            runtime_snapshot=runtime_snapshot,
        )


__all__ = [
    "RlCounterpointEnvRuntime",
    "RlCounterpointEnvRuntimeReset",
    "RlCounterpointEnvRuntimeStep",
    "RlCounterpointHiddenGraph",
    "action_index_to_primitive_action",
    "default_rl_counterpoint_v3_schema",
    "primitive_action_to_action_index",
    "rl_counterpoint_edge_labels",
    "rl_counterpoint_state_to_core_state",
    "semantic_rl_counterpoint_v3_schema",
]
