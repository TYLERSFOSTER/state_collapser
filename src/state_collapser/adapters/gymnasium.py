"""Gymnasium adapter and wrapper surfaces."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Mapping
from dataclasses import dataclass
from typing import Protocol

from state_collapser.contract.policy import ContractionPolicy
from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.examples.robot_constraint_toy import (
    RobotConstraintHiddenGraph,
    RobotConstraintToy,
)
from state_collapser.graph.explored_graph import ExploredGraph
from state_collapser.tower.runtime import TowerRuntime

StateKeyHook = Callable[[object, Mapping[str, object]], Hashable]
ActionKeyHook = Callable[[object, object, Mapping[str, object]], Hashable]
ActionMaskHook = Callable[[Mapping[str, object], object], tuple[bool, ...] | None]
EdgeLabelerHook = Callable[
    [Hashable, Hashable, Hashable, Mapping[str, object]],
    tuple[Hashable, ...],
]


class GymnasiumLike(Protocol):
    """Minimal Gymnasium-like environment surface consumed by the wrapper."""

    @property
    def action_space(self) -> object: ...

    @property
    def observation_space(self) -> object: ...

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, object] | None = None,
    ) -> tuple[object, Mapping[str, object]]: ...

    def step(self, action: object) -> tuple[object, float, bool, bool, Mapping[str, object]]: ...


@dataclass(frozen=True, slots=True)
class StateCollapserGymHooks:
    """Explicit hooks for interpreting a Gymnasium env structurally."""

    state_key: StateKeyHook
    action_key: ActionKeyHook
    edge_labeler: EdgeLabelerHook = lambda source, action, target, info: ()
    action_mask: ActionMaskHook | None = None


class RobotConstraintRuntimeAdapter:
    """Toy robot adapter exposing the package runtime through Gymnasium-style methods."""

    def __init__(self, contraction_policy: ContractionPolicy | None = None) -> None:
        self.environment = RobotConstraintToy()
        self.hidden_graph = RobotConstraintHiddenGraph(self.environment)
        self.runtime = TowerRuntime(
            hidden_graph=self.hidden_graph,
            contraction_policy=contraction_policy,
            reward_function=lambda edge: 1.0,
        )

    def reset(self) -> tuple[object, dict[str, object]]:
        """Reset the runtime and return Gymnasium-style `(observation, info)`."""

        snapshot = self.runtime.reset(initial_state=self.environment.start_state)
        return snapshot.current_base_state, {"runtime_snapshot": snapshot}

    def step(
        self,
        action: PrimitiveAction,
    ) -> tuple[object, float, bool, bool, dict[str, object]]:
        """Advance one step and return Gymnasium-style step outputs."""

        snapshot = self.runtime.step(action)
        observation = snapshot.current_base_state
        reward = 0.0 if snapshot.current_step_reward is None else snapshot.current_step_reward.value
        terminated = observation == self.environment.goal_state
        truncated = False
        return observation, reward, terminated, truncated, {"runtime_snapshot": snapshot}


class StateCollapserGymWrapper:
    """Hook-based wrapper for recording realized Gymnasium transitions."""

    def __init__(self, env: GymnasiumLike, hooks: StateCollapserGymHooks) -> None:
        self.env = env
        self.hooks = hooks
        self.explored_graph = ExploredGraph()
        self._current_state: State | None = None
        self._current_observation: object | None = None
        self._current_info: dict[str, object] = {}

    @property
    def action_space(self) -> object:
        return self.env.action_space

    @property
    def observation_space(self) -> object:
        return self.env.observation_space

    @property
    def observed_edges(self) -> tuple[BaseEdge, ...]:
        return self.explored_graph.visited_edges()

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, object] | None = None,
    ) -> tuple[object, dict[str, object]]:
        """Reset the wrapped env and initialize the observed state graph."""

        observation, raw_info = self.env.reset(seed=seed, options=options)
        info = dict(raw_info)
        state_key = self.hooks.state_key(observation, info)
        state = State(payload=state_key, identity=state_key)
        self.explored_graph = ExploredGraph()
        self.explored_graph.add_state(state)
        self._current_state = state
        self._current_observation = observation
        self._current_info = info
        self._attach_mask(info)
        self._attach_metadata(
            info,
            source_key=None,
            action_key=None,
            target_key=state_key,
            edge_labels=(),
        )
        return observation, info

    def step(self, action: object) -> tuple[object, float, bool, bool, dict[str, object]]:
        """Delegate one env step and record the realized transition only."""

        if self._current_state is None:
            raise ValueError("reset(...) must be called before step(...).")
        source_state = self._current_state
        source_key = source_state.canonical_identity
        action_key = self.hooks.action_key(
            action,
            self._current_observation,
            self._current_info,
        )
        observation, reward, terminated, truncated, raw_info = self.env.step(action)
        info = dict(raw_info)
        target_key = self.hooks.state_key(observation, info)
        labels = self.hooks.edge_labeler(source_key, action_key, target_key, info)
        target_state = State(payload=target_key, identity=target_key)
        primitive_action = PrimitiveAction(
            payload=action_key,
            identity=action_key,
            labels=labels,
        )
        edge = BaseEdge(
            source=source_state,
            action=primitive_action,
            target=target_state,
            labels=labels,
        )
        self.explored_graph.add_edge(edge)
        self._current_state = target_state
        self._current_observation = observation
        self._current_info = info
        self._attach_mask(info)
        self._attach_metadata(
            info,
            source_key=source_key,
            action_key=action_key,
            target_key=target_key,
            edge_labels=labels,
        )
        return observation, float(reward), bool(terminated), bool(truncated), info

    def _attach_mask(self, info: dict[str, object]) -> None:
        if self.hooks.action_mask is None:
            return
        mask = self.hooks.action_mask(info, self.env)
        if mask is not None:
            info["action_mask"] = tuple(mask)

    def _attach_metadata(
        self,
        info: dict[str, object],
        *,
        source_key: object | None,
        action_key: object | None,
        target_key: object,
        edge_labels: tuple[Hashable, ...],
    ) -> None:
        info["state_collapser"] = {
            "mode": "opaque_realized_transitions",
            "source_state_key": source_key,
            "action_key": action_key,
            "target_state_key": target_key,
            "edge_labels": edge_labels,
            "observed_state_count": len(self.explored_graph.visited_states()),
            "observed_edge_count": len(self.explored_graph.visited_edges()),
            "explored_graph": self.explored_graph,
        }


__all__ = [
    "RobotConstraintRuntimeAdapter",
    "StateCollapserGymHooks",
    "StateCollapserGymWrapper",
]
