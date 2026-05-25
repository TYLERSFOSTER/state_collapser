"""Discrete plate-support environment for env_001 package evaluation."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import gymnasium
import numpy as np


@dataclass(frozen=True, slots=True)
class PlateSupportState:
    """Immutable internal state record for PlateSupportEnv."""

    x_idx: int
    y_idx: int
    theta_idx: int
    e1: int
    e2: int
    e3: int


@dataclass(frozen=True, slots=True)
class PrimitiveTransitionResult:
    """Detailed one-step transition metadata for PlateSupportEnv."""

    candidate_state: PlateSupportState
    next_state: PlateSupportState
    candidate_valid: bool
    valid_transition: bool
    invalid_move: bool
    valid_self_transition: bool


WORKSPACE_WIDTH = 5
WORKSPACE_HEIGHT = 5
SUPPORT_SOCKETS_LOCAL = ((-1, 0), (0, 0), (1, 0))
ARM_BASE_COORDINATES = ((1, 2), (2, 2), (3, 2))
START_STATE = PlateSupportState(2, 2, 0, 1, 1, 1)
CANDIDATE_GOAL_STATE = PlateSupportState(1, 1, 1, 2, 2, 2)
MAX_STEPS = 50
ACTION_COUNT = 12


def encode_observation(state: PlateSupportState) -> np.ndarray:
    """Encode an internal state into the canonical observation array."""

    return np.asarray(
        [state.x_idx, state.y_idx, state.theta_idx, state.e1, state.e2, state.e3],
        dtype=np.int64,
    )


def decode_observation(values: Iterable[int]) -> PlateSupportState:
    """Decode an observation-like iterable into an internal state."""

    x_idx, y_idx, theta_idx, e1, e2, e3 = tuple(int(value) for value in values)
    return PlateSupportState(
        x_idx=x_idx,
        y_idx=y_idx,
        theta_idx=theta_idx,
        e1=e1,
        e2=e2,
        e3=e3,
    )


def rotate_local_point(theta_idx: int, point: tuple[int, int]) -> tuple[int, int]:
    """Rotate a local support point by a quarter-turn orientation index."""

    u, v = point
    if theta_idx == 0:
        return (u, v)
    if theta_idx == 1:
        return (-v, u)
    if theta_idx == 2:
        return (-u, -v)
    if theta_idx == 3:
        return (v, -u)
    raise ValueError(f"Unsupported theta_idx: {theta_idx}")


def socket_world_position(
    center: tuple[int, int],
    theta_idx: int,
    local_socket: tuple[int, int],
) -> tuple[int, int]:
    """Compute one support-socket world position from center and orientation."""

    x_idx, y_idx = center
    du, dv = rotate_local_point(theta_idx, local_socket)
    return (x_idx + du, y_idx + dv)


def ordered_socket_world_positions(
    state: PlateSupportState,
) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    """Return socket world coordinates aligned with arms 1, 2, and 3."""

    center = (state.x_idx, state.y_idx)
    left, mid, right = SUPPORT_SOCKETS_LOCAL
    return (
        socket_world_position(center, state.theta_idx, left),
        socket_world_position(center, state.theta_idx, mid),
        socket_world_position(center, state.theta_idx, right),
    )


def plate_center_in_bounds(state: PlateSupportState) -> bool:
    """Return whether the plate center lies inside the workspace grid."""

    return 0 <= state.x_idx < WORKSPACE_WIDTH and 0 <= state.y_idx < WORKSPACE_HEIGHT


def all_sockets_in_bounds(state: PlateSupportState) -> bool:
    """Return whether all support sockets remain inside the workspace grid."""

    return all(
        0 <= x_idx < WORKSPACE_WIDTH and 0 <= y_idx < WORKSPACE_HEIGHT
        for x_idx, y_idx in ordered_socket_world_positions(state)
    )


def engaged_arm_reachability(state: PlateSupportState) -> tuple[bool, bool, bool]:
    """Return per-arm reachability under the fixed arm-to-socket assignment."""

    extensions = (state.e1, state.e2, state.e3)
    sockets = ordered_socket_world_positions(state)
    reachability: list[bool] = []
    for extension, socket, base in zip(extensions, sockets, ARM_BASE_COORDINATES, strict=True):
        if extension == 0:
            reachability.append(False)
            continue
        distance = abs(socket[0] - base[0]) + abs(socket[1] - base[1])
        reachability.append(distance <= extension)
    return tuple(reachability)  # type: ignore[return-value]


def has_minimum_engaged_supports(state: PlateSupportState) -> bool:
    """Return whether at least two arms are engaged."""

    return sum(extension > 0 for extension in (state.e1, state.e2, state.e3)) >= 2


def has_stable_support_pattern(state: PlateSupportState) -> bool:
    """Return whether the reachable support pattern satisfies the env stability rule."""

    left_ok, mid_ok, right_ok = engaged_arm_reachability(state)
    return (left_ok and right_ok) or (left_ok and mid_ok and right_ok)


def is_valid_state(state: PlateSupportState) -> bool:
    """Return whether a state satisfies the full env validity predicate."""

    return (
        plate_center_in_bounds(state)
        and all_sockets_in_bounds(state)
        and has_minimum_engaged_supports(state)
        and has_stable_support_pattern(state)
        and all(
            (extension == 0) or reachable
            for extension, reachable in zip(
                (state.e1, state.e2, state.e3),
                engaged_arm_reachability(state),
                strict=True,
            )
        )
    )


def has_valid_start_state() -> bool:
    """Return whether the configured start state satisfies env validity."""

    return is_valid_state(START_STATE)


def has_valid_goal_state() -> bool:
    """Return whether the configured candidate goal state satisfies env validity."""

    return is_valid_state(CANDIDATE_GOAL_STATE)


def goal_differs_from_start() -> bool:
    """Return whether the configured goal is distinct from the start state."""

    return CANDIDATE_GOAL_STATE != START_STATE


def goal_changes_plate_pose() -> bool:
    """Return whether the configured goal changes plate position or orientation."""

    return (
        CANDIDATE_GOAL_STATE.x_idx,
        CANDIDATE_GOAL_STATE.y_idx,
        CANDIDATE_GOAL_STATE.theta_idx,
    ) != (
        START_STATE.x_idx,
        START_STATE.y_idx,
        START_STATE.theta_idx,
    )


def goal_changes_support_configuration() -> bool:
    """Return whether the configured goal changes arm support configuration."""

    return (CANDIDATE_GOAL_STATE.e1, CANDIDATE_GOAL_STATE.e2, CANDIDATE_GOAL_STATE.e3) != (
        START_STATE.e1,
        START_STATE.e2,
        START_STATE.e3,
    )


def propose_primitive_action(state: PlateSupportState, action: int) -> PlateSupportState:
    """Return the candidate state produced by one primitive action proposal."""

    if action == 0:
        return PlateSupportState(
            state.x_idx + 1, state.y_idx, state.theta_idx, state.e1, state.e2, state.e3
        )
    if action == 1:
        return PlateSupportState(
            state.x_idx - 1, state.y_idx, state.theta_idx, state.e1, state.e2, state.e3
        )
    if action == 2:
        return PlateSupportState(
            state.x_idx, state.y_idx + 1, state.theta_idx, state.e1, state.e2, state.e3
        )
    if action == 3:
        return PlateSupportState(
            state.x_idx, state.y_idx - 1, state.theta_idx, state.e1, state.e2, state.e3
        )
    if action == 4:
        return PlateSupportState(
            state.x_idx, state.y_idx, (state.theta_idx + 1) % 4, state.e1, state.e2, state.e3
        )
    if action == 5:
        return PlateSupportState(
            state.x_idx, state.y_idx, (state.theta_idx - 1) % 4, state.e1, state.e2, state.e3
        )
    if action == 6:
        return PlateSupportState(
            state.x_idx, state.y_idx, state.theta_idx, min(state.e1 + 1, 2), state.e2, state.e3
        )
    if action == 7:
        return PlateSupportState(
            state.x_idx, state.y_idx, state.theta_idx, max(state.e1 - 1, 0), state.e2, state.e3
        )
    if action == 8:
        return PlateSupportState(
            state.x_idx, state.y_idx, state.theta_idx, state.e1, min(state.e2 + 1, 2), state.e3
        )
    if action == 9:
        return PlateSupportState(
            state.x_idx, state.y_idx, state.theta_idx, state.e1, max(state.e2 - 1, 0), state.e3
        )
    if action == 10:
        return PlateSupportState(
            state.x_idx, state.y_idx, state.theta_idx, state.e1, state.e2, min(state.e3 + 1, 2)
        )
    if action == 11:
        return PlateSupportState(
            state.x_idx, state.y_idx, state.theta_idx, state.e1, state.e2, max(state.e3 - 1, 0)
        )
    raise ValueError(f"Unsupported action index: {action}")


def primitive_action_result(state: PlateSupportState, action: int) -> PlateSupportState:
    """Return the actual one-step env result for a primitive action."""

    candidate = propose_primitive_action(state, action)
    if is_valid_state(candidate):
        return candidate
    return state


def primitive_transition(
    state: PlateSupportState,
    action: int,
) -> PrimitiveTransitionResult:
    """Return detailed one-step env transition metadata."""

    candidate = propose_primitive_action(state, action)
    candidate_valid = is_valid_state(candidate)
    if candidate_valid:
        return PrimitiveTransitionResult(
            candidate_state=candidate,
            next_state=candidate,
            candidate_valid=True,
            valid_transition=True,
            invalid_move=False,
            valid_self_transition=candidate == state,
        )
    return PrimitiveTransitionResult(
        candidate_state=candidate,
        next_state=state,
        candidate_valid=False,
        valid_transition=False,
        invalid_move=True,
        valid_self_transition=False,
    )


def goal_is_one_primitive_action_from_start() -> bool:
    """Return whether the configured goal is reachable from start in one env step."""

    return any(
        primitive_transition(START_STATE, action).next_state == CANDIDATE_GOAL_STATE
        for action in range(ACTION_COUNT)
    )


def is_goal_state(state: PlateSupportState) -> bool:
    """Return whether a state is the configured goal state."""

    return state == CANDIDATE_GOAL_STATE


def transition_reward(
    state: PlateSupportState,
    action: int,
    next_state: PlateSupportState,
) -> float:
    """Return the one-step local reward for a primitive transition."""

    # Reward is intentionally local to the primitive transition (s, a, s').
    _ = state
    _ = action
    if is_goal_state(next_state):
        return 100.0
    if next_state == state:
        return -3.0
    return -1.0


def transition_terminated(next_state: PlateSupportState) -> bool:
    """Return whether the transition reaches the configured goal."""

    return is_goal_state(next_state)


def transition_truncated(step_count: int, terminated: bool) -> bool:
    """Return whether the episode should truncate at the step budget."""

    return (step_count >= MAX_STEPS) and not terminated


def all_candidate_states() -> tuple[PlateSupportState, ...]:
    """Enumerate the ambient finite discrete state space before validity filtering."""

    states: list[PlateSupportState] = []
    for x_idx in range(WORKSPACE_WIDTH):
        for y_idx in range(WORKSPACE_HEIGHT):
            for theta_idx in range(4):
                for e1 in range(3):
                    for e2 in range(3):
                        for e3 in range(3):
                            states.append(PlateSupportState(x_idx, y_idx, theta_idx, e1, e2, e3))
    return tuple(states)


def all_valid_states() -> tuple[PlateSupportState, ...]:
    """Enumerate all valid states in the env's hidden feasible graph."""

    return tuple(state for state in all_candidate_states() if is_valid_state(state))


def valid_outgoing_transitions(
    state: PlateSupportState,
) -> tuple[tuple[int, PlateSupportState], ...]:
    """Enumerate valid non-self-loop outgoing primitive transitions from a state."""

    outgoing: list[tuple[int, PlateSupportState]] = []
    for action in range(ACTION_COUNT):
        transition = primitive_transition(state, action)
        if transition.valid_transition and transition.next_state != state:
            outgoing.append((action, transition.next_state))
    return tuple(outgoing)


class PlateSupportEnv(gymnasium.Env[np.ndarray, int]):
    """Discrete constrained plate-support Gymnasium environment for env_001."""

    metadata = {"render_modes": [None, "ansi"]}

    def __init__(self, render_mode: str | None = None) -> None:
        self.render_mode = render_mode
        self.action_space = gymnasium.spaces.Discrete(ACTION_COUNT)
        self.observation_space = gymnasium.spaces.MultiDiscrete([5, 5, 4, 3, 3, 3])
        self.state = START_STATE
        self.goal_state = CANDIDATE_GOAL_STATE
        self.step_count = 0

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, object] | None = None,
    ) -> tuple[np.ndarray, dict[str, object]]:
        super().reset(seed=seed)
        _ = options
        self.state = START_STATE
        self.step_count = 0
        return encode_observation(self.state), {
            "state": self.state,
            "goal_state": self.goal_state,
        }

    def step(
        self,
        action: int,
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, object]]:
        if isinstance(action, bool) or not self.action_space.contains(action):
            raise ValueError(f"Unsupported action index: {action}")

        action_index = int(action)
        previous_state = self.state
        transition = primitive_transition(previous_state, action_index)
        self.step_count += 1
        self.state = transition.next_state
        terminated = transition_terminated(self.state)
        truncated = transition_truncated(self.step_count, terminated)
        reward = transition_reward(previous_state, action_index, self.state)
        return (
            encode_observation(self.state),
            reward,
            terminated,
            truncated,
            {
                "state": self.state,
                "valid_transition": transition.valid_transition,
                "invalid_move": transition.invalid_move,
                "goal_reached": terminated,
            },
        )

    def render(self) -> str | None:
        if self.render_mode is None:
            return None
        if self.render_mode == "ansi":
            return (
                "PlateSupportState("
                f"x={self.state.x_idx}, "
                f"y={self.state.y_idx}, "
                f"theta={self.state.theta_idx}, "
                f"e=({self.state.e1},{self.state.e2},{self.state.e3}), "
                f"valid={is_valid_state(self.state)})"
            )
        raise ValueError(f"Unsupported render mode: {self.render_mode}")
