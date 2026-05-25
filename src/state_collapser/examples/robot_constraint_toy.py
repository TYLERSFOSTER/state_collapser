"""Robot-constraint toy environment contract surface."""

from __future__ import annotations

import copy
from dataclasses import dataclass, replace
from typing import cast

from state_collapser.contract.policy import ContractionPolicy
from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.graph.spec import GraphSpec
from state_collapser.tower.runtime import TowerRuntime
from state_collapser.tower.snapshot import LiveRuntimeView


@dataclass(frozen=True, slots=True)
class ConstraintRegion:
    """Region-specific local labeling metadata."""

    name: str
    labels: tuple[str, ...]


class RobotConstraintToy:
    """Small discretized robot-constraint environment with partially labeled regions."""

    def __init__(self) -> None:
        self.width = 4
        self.height = 3
        self._blocked = {(1, 1)}
        self._start = (0, 0)
        self._goal = (3, 2)
        self._regions = {
            (0, 2): ConstraintRegion("hinge-band", ("hinge",)),
            (2, 2): ConstraintRegion("elbow-window", ("elbow", "safe")),
        }
        self._actions = {
            "left": (-1, 0),
            "right": (1, 0),
            "down": (0, -1),
            "up": (0, 1),
        }

    @property
    def start_state(self) -> State:
        """Return the initial inspectable local state."""

        return self.state_at(*self._start)

    @property
    def goal_state(self) -> State:
        """Return the goal inspectable local state."""

        return self.state_at(*self._goal)

    def state_at(self, x: int, y: int) -> State:
        """Construct an inspectable local state from a grid position."""

        return State(payload=("joint-grid", x, y), identity=f"state:{x}:{y}")

    def coordinates(self, state: State) -> tuple[int, int]:
        """Decode a local state into grid coordinates."""

        payload = cast(tuple[str, int, int], state.payload)
        _, x, y = payload
        return x, y

    def valid_states(self) -> tuple[State, ...]:
        """Enumerate all valid local states in the constrained grid."""

        states: list[State] = []
        for x in range(self.width):
            for y in range(self.height):
                if (x, y) not in self._blocked:
                    states.append(self.state_at(x, y))
        return tuple(states)

    def valid_actions(self) -> tuple[PrimitiveAction, ...]:
        """Return the primitive transitions available in the toy environment."""

        return tuple(
            PrimitiveAction(payload=("move", name), identity=f"action:{name}")
            for name in self._actions
        )

    def region_labels(self, state: State) -> tuple[str, ...]:
        """Return region-specific labels where the current state is annotated."""

        coords = self.coordinates(state)
        region = self._regions.get(coords)
        return () if region is None else region.labels

    def transition(self, state: State, action: PrimitiveAction) -> State | None:
        """Apply one primitive transition under the hidden constraint geometry."""

        payload = cast(tuple[str, str], action.payload)
        _, action_name = payload
        dx, dy = self._actions[action_name]
        x, y = self.coordinates(state)
        next_coords = (x + dx, y + dy)
        if not (0 <= next_coords[0] < self.width and 0 <= next_coords[1] < self.height):
            return None
        if next_coords in self._blocked:
            return None
        return self.state_at(*next_coords)

    def graph_spec(self) -> GraphSpec:
        """Return the graph-spec contract for the toy environment."""

        return GraphSpec(
            name="robot-constraint-toy",
            rules=(
                ("width", self.width),
                ("height", self.height),
                ("blocked-count", len(self._blocked)),
            ),
            metadata=(("goal", self._goal),),
        )


class RobotConstraintHiddenGraph:
    """Hidden-graph binding for the robot-constraint toy environment."""

    def __init__(self, environment: RobotConstraintToy) -> None:
        self.environment = environment
        self.spec = environment.graph_spec()

    def is_valid_state(self, state: State) -> bool:
        return state in set(self.environment.valid_states())

    def is_valid_action(self, action: PrimitiveAction) -> bool:
        return action in set(self.environment.valid_actions())

    def apply_action(self, state: State, action: PrimitiveAction) -> State | None:
        return self.environment.transition(state, action)

    def is_valid_edge(self, edge: BaseEdge) -> bool:
        return self.apply_action(edge.source, edge.action) == edge.target

    def out_actions(self, state: State) -> tuple[PrimitiveAction, ...]:
        return tuple(
            action
            for action in self.environment.valid_actions()
            if self.apply_action(state, action) is not None
        )

    def out_neighbors(self, state: State) -> tuple[State, ...]:
        return tuple(
            target
            for action in self.out_actions(state)
            if (target := self.apply_action(state, action)) is not None
        )

    def out_edges(self, state: State) -> tuple[BaseEdge, ...]:
        return tuple(
            BaseEdge(
                source=state,
                action=action,
                target=target,
                labels=self.environment.region_labels(target),
            )
            for action in self.out_actions(state)
            if (target := self.apply_action(state, action)) is not None
        )


def run_robot_constraint_vertical_slice(
    actions: tuple[PrimitiveAction, ...],
    contraction_policy: ContractionPolicy | None = None,
    include_compatibility_readouts: bool = False,
) -> tuple[LiveRuntimeView, ...]:
    """Run an end-to-end tower runtime path through the toy environment."""

    environment = RobotConstraintToy()
    hidden_graph = RobotConstraintHiddenGraph(environment)
    runtime = TowerRuntime(
        hidden_graph=hidden_graph,
        contraction_policy=contraction_policy,
        reward_function=lambda edge: 1.0,
    )
    reset_view = runtime.reset(initial_state=environment.start_state)
    if include_compatibility_readouts:
        reset_view = replace(
            reset_view,
            ordered_quotient_tiers=runtime.compatibility_quotient_tiers(),
        )
    snapshots = [copy.deepcopy(reset_view)]
    for action in actions:
        step_view = runtime.step(action)
        if include_compatibility_readouts:
            step_view = replace(
                step_view,
                ordered_quotient_tiers=runtime.compatibility_quotient_tiers(),
            )
        snapshots.append(copy.deepcopy(step_view))
    return tuple(snapshots)


__all__ = [
    "RobotConstraintHiddenGraph",
    "RobotConstraintToy",
    "run_robot_constraint_vertical_slice",
]
