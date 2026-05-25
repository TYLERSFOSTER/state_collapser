"""Discrete cable-parallel environment for package evaluation."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import gymnasium
import numpy as np


@dataclass(frozen=True, slots=True)
class CableParallelState:
    """Immutable internal state for CableParallelEnv."""

    x_idx: int
    y_idx: int
    theta_idx: int
    c1: int
    c2: int
    c3: int


@dataclass(frozen=True, slots=True)
class PrimitiveTransitionResult:
    """Detailed one-step transition metadata for CableParallelEnv."""

    candidate_state: CableParallelState
    next_state: CableParallelState
    candidate_valid: bool
    valid_transition: bool
    invalid_move: bool
    valid_self_transition: bool


GRID_SIZE = 3
THETA_COUNT = 2
TENSION_COUNT = 3
MAX_STEPS = 32
ACTION_COUNT = 11

ANCHOR_1 = (0, 2)
ANCHOR_2 = (2, 2)
ANCHOR_3 = (1, 0)

START_STATE = CableParallelState(1, 1, 0, 2, 2, 1)
CANDIDATE_GOAL_STATE = CableParallelState(1, 2, 1, 0, 0, 2)


def encode_observation(state: CableParallelState) -> np.ndarray:
    """Encode one internal state into the canonical observation array."""

    return np.asarray(
        [state.x_idx, state.y_idx, state.theta_idx, state.c1, state.c2, state.c3],
        dtype=np.int64,
    )


def decode_observation(values: Iterable[int]) -> CableParallelState:
    """Decode an observation-like iterable into an internal state."""

    x_idx, y_idx, theta_idx, c1, c2, c3 = (int(value) for value in values)
    return CableParallelState(
        x_idx=x_idx,
        y_idx=y_idx,
        theta_idx=theta_idx,
        c1=c1,
        c2=c2,
        c3=c3,
    )


def manhattan_distance(point_a: tuple[int, int], point_b: tuple[int, int]) -> int:
    """Return the Manhattan distance between two discrete points."""

    return abs(point_a[0] - point_b[0]) + abs(point_a[1] - point_b[1])


def required_tensions(state: CableParallelState) -> tuple[int, int, int]:
    """Return the required cable tensions for the current platform pose."""

    position = (state.x_idx, state.y_idx)
    top_left = min(2, manhattan_distance(position, ANCHOR_1))
    top_right = min(2, manhattan_distance(position, ANCHOR_2))
    bottom = min(2, manhattan_distance(position, ANCHOR_3))
    if state.theta_idx == 1:
        top_left = max(0, top_left - 1)
        top_right = max(0, top_right - 1)
        bottom = min(2, bottom + 1)
    return (top_left, top_right, bottom)


def support_count(state: CableParallelState) -> int:
    """Return how many cables currently meet or exceed required tension."""

    req1, req2, req3 = required_tensions(state)
    return int(state.c1 >= req1) + int(state.c2 >= req2) + int(state.c3 >= req3)


def is_valid_state(state: CableParallelState) -> bool:
    """Return whether a state satisfies the cable-feasibility rules."""

    if not 0 <= state.x_idx < GRID_SIZE or not 0 <= state.y_idx < GRID_SIZE:
        return False
    if not 0 <= state.theta_idx < THETA_COUNT:
        return False
    if not all(0 <= tension < TENSION_COUNT for tension in (state.c1, state.c2, state.c3)):
        return False

    req1, req2, req3 = required_tensions(state)
    if abs(state.c1 - req1) > 1 or abs(state.c2 - req2) > 1 or abs(state.c3 - req3) > 1:
        return False
    if support_count(state) < 2:
        return False
    if state.y_idx == 2 and not (state.c1 >= req1 and state.c2 >= req2):
        return False
    if state.x_idx == 0 and not (state.c1 >= req1 and state.c3 >= req3):
        return False
    if state.x_idx == 2 and not (state.c2 >= req2 and state.c3 >= req3):
        return False
    return True


def has_valid_start_state() -> bool:
    """Return whether the configured start state is valid."""

    return is_valid_state(START_STATE)


def has_valid_goal_state() -> bool:
    """Return whether the configured goal state is valid."""

    return is_valid_state(CANDIDATE_GOAL_STATE)


def propose_primitive_action(state: CableParallelState, action: int) -> CableParallelState:
    """Return the candidate state produced by one primitive action proposal."""

    if action == 0:
        return CableParallelState(
            min(state.x_idx + 1, GRID_SIZE - 1),
            state.y_idx,
            state.theta_idx,
            state.c1,
            state.c2,
            state.c3,
        )
    if action == 1:
        return CableParallelState(
            max(state.x_idx - 1, 0),
            state.y_idx,
            state.theta_idx,
            state.c1,
            state.c2,
            state.c3,
        )
    if action == 2:
        return CableParallelState(
            state.x_idx,
            min(state.y_idx + 1, GRID_SIZE - 1),
            state.theta_idx,
            state.c1,
            state.c2,
            state.c3,
        )
    if action == 3:
        return CableParallelState(
            state.x_idx,
            max(state.y_idx - 1, 0),
            state.theta_idx,
            state.c1,
            state.c2,
            state.c3,
        )
    if action == 4:
        return CableParallelState(
            state.x_idx,
            state.y_idx,
            1 - state.theta_idx,
            state.c1,
            state.c2,
            state.c3,
        )
    if action == 5:
        return CableParallelState(
            state.x_idx,
            state.y_idx,
            state.theta_idx,
            min(state.c1 + 1, TENSION_COUNT - 1),
            state.c2,
            state.c3,
        )
    if action == 6:
        return CableParallelState(
            state.x_idx,
            state.y_idx,
            state.theta_idx,
            max(state.c1 - 1, 0),
            state.c2,
            state.c3,
        )
    if action == 7:
        return CableParallelState(
            state.x_idx,
            state.y_idx,
            state.theta_idx,
            state.c1,
            min(state.c2 + 1, TENSION_COUNT - 1),
            state.c3,
        )
    if action == 8:
        return CableParallelState(
            state.x_idx,
            state.y_idx,
            state.theta_idx,
            state.c1,
            max(state.c2 - 1, 0),
            state.c3,
        )
    if action == 9:
        return CableParallelState(
            state.x_idx,
            state.y_idx,
            state.theta_idx,
            state.c1,
            state.c2,
            min(state.c3 + 1, TENSION_COUNT - 1),
        )
    if action == 10:
        return CableParallelState(
            state.x_idx,
            state.y_idx,
            state.theta_idx,
            state.c1,
            state.c2,
            max(state.c3 - 1, 0),
        )
    raise ValueError(f"Unsupported action: {action}")


def primitive_transition(state: CableParallelState, action: int) -> PrimitiveTransitionResult:
    """Apply one primitive action under the env validity rule."""

    candidate = propose_primitive_action(state, action)
    candidate_valid = is_valid_state(candidate)
    next_state = candidate if candidate_valid else state
    valid_self_transition = candidate_valid and next_state == state
    return PrimitiveTransitionResult(
        candidate_state=candidate,
        next_state=next_state,
        candidate_valid=candidate_valid,
        valid_transition=candidate_valid and next_state != state,
        invalid_move=not candidate_valid,
        valid_self_transition=valid_self_transition,
    )


def is_goal_state(state: CableParallelState) -> bool:
    """Return whether a state matches the configured goal."""

    return state == CANDIDATE_GOAL_STATE


def transition_reward(
    state: CableParallelState,
    action: int,
    next_state: CableParallelState,
) -> float:
    """Return the reward for one primitive transition."""

    result = primitive_transition(state, action)
    if result.invalid_move:
        return -2.0
    if is_goal_state(next_state):
        return 20.0
    return -1.0


def transition_terminated(state: CableParallelState) -> bool:
    """Return whether an episode should terminate at the given state."""

    return is_goal_state(state)


def transition_truncated(step_count: int, terminated: bool) -> bool:
    """Return whether an episode should truncate at the current step count."""

    return (not terminated) and step_count >= MAX_STEPS


def all_candidate_states() -> tuple[CableParallelState, ...]:
    """Return the full ambient discrete candidate state set."""

    states: list[CableParallelState] = []
    for x_idx in range(GRID_SIZE):
        for y_idx in range(GRID_SIZE):
            for theta_idx in range(THETA_COUNT):
                for c1 in range(TENSION_COUNT):
                    for c2 in range(TENSION_COUNT):
                        for c3 in range(TENSION_COUNT):
                            states.append(CableParallelState(x_idx, y_idx, theta_idx, c1, c2, c3))
    return tuple(states)


def all_valid_states() -> tuple[CableParallelState, ...]:
    """Return the valid hidden-state subset."""

    return tuple(state for state in all_candidate_states() if is_valid_state(state))


def valid_outgoing_transitions(
    state: CableParallelState,
) -> tuple[tuple[int, CableParallelState], ...]:
    """Return valid primitive outgoing transitions from one state."""

    transitions: list[tuple[int, CableParallelState]] = []
    for action in range(ACTION_COUNT):
        result = primitive_transition(state, action)
        if result.invalid_move:
            continue
        transitions.append((action, result.next_state))
    return tuple(transitions)


class CableParallelEnv(gymnasium.Env[np.ndarray, int]):
    """Gymnasium-compatible discrete cable-parallel environment."""

    metadata = {"render_modes": []}

    def __init__(self) -> None:
        super().__init__()
        self.action_space = gymnasium.spaces.Discrete(ACTION_COUNT)
        self.observation_space = gymnasium.spaces.MultiDiscrete([3, 3, 2, 3, 3, 3])
        self.state = START_STATE
        self.step_count = 0

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, object] | None = None,
    ) -> tuple[np.ndarray, dict[str, object]]:
        super().reset(seed=seed)
        del options
        self.state = START_STATE
        self.step_count = 0
        return encode_observation(self.state), {"state": self.state}

    def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict[str, object]]:
        if isinstance(action, bool) or not self.action_space.contains(action):
            raise ValueError(f"Unsupported action index: {action}")

        action_index = int(action)
        prior_state = self.state
        result = primitive_transition(self.state, action_index)
        self.state = result.next_state
        self.step_count += 1
        reward = transition_reward(prior_state, action_index, self.state)
        terminated = transition_terminated(self.state)
        truncated = transition_truncated(self.step_count, terminated)
        return (
            encode_observation(self.state),
            reward,
            terminated,
            truncated,
            {"state": self.state, "invalid_move": result.invalid_move},
        )


__all__ = [
    "ACTION_COUNT",
    "ANCHOR_1",
    "ANCHOR_2",
    "ANCHOR_3",
    "CANDIDATE_GOAL_STATE",
    "CableParallelEnv",
    "CableParallelState",
    "GRID_SIZE",
    "MAX_STEPS",
    "PrimitiveTransitionResult",
    "START_STATE",
    "TENSION_COUNT",
    "THETA_COUNT",
    "all_candidate_states",
    "all_valid_states",
    "decode_observation",
    "encode_observation",
    "has_valid_goal_state",
    "has_valid_start_state",
    "is_goal_state",
    "is_valid_state",
    "manhattan_distance",
    "primitive_transition",
    "propose_primitive_action",
    "required_tensions",
    "support_count",
    "transition_reward",
    "transition_terminated",
    "transition_truncated",
    "valid_outgoing_transitions",
]
