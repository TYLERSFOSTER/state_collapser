"""Discrete dual-arm manipulation environment for package evaluation."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import gymnasium
import numpy as np


@dataclass(frozen=True, slots=True)
class DualArmManipulationState:
    """Immutable internal state for DualArmManipulationEnv."""

    obj_x: int
    obj_y: int
    obj_theta: int
    left_mode: int
    right_mode: int
    left_reach: int
    right_reach: int


@dataclass(frozen=True, slots=True)
class PrimitiveTransitionResult:
    """Detailed one-step transition metadata for DualArmManipulationEnv."""

    candidate_state: DualArmManipulationState
    next_state: DualArmManipulationState
    candidate_valid: bool
    valid_transition: bool
    invalid_move: bool
    valid_self_transition: bool


GRID_SIZE = 3
THETA_COUNT = 2
ARM_MODE_COUNT = 3
REACH_COUNT = 3
MAX_STEPS = 32
ACTION_COUNT = 11

LEFT_BASE = (0, 1)
RIGHT_BASE = (2, 1)

START_STATE = DualArmManipulationState(1, 1, 0, 1, 1, 1, 1)
CANDIDATE_GOAL_STATE = DualArmManipulationState(2, 1, 1, 1, 2, 2, 1)


def encode_observation(state: DualArmManipulationState) -> np.ndarray:
    """Encode one internal state into the canonical observation array."""

    return np.asarray(
        [
            state.obj_x,
            state.obj_y,
            state.obj_theta,
            state.left_mode,
            state.right_mode,
            state.left_reach,
            state.right_reach,
        ],
        dtype=np.int64,
    )


def decode_observation(values: Iterable[int]) -> DualArmManipulationState:
    """Decode an observation-like iterable into an internal state."""

    obj_x, obj_y, obj_theta, left_mode, right_mode, left_reach, right_reach = (
        int(value) for value in values
    )
    return DualArmManipulationState(
        obj_x=obj_x,
        obj_y=obj_y,
        obj_theta=obj_theta,
        left_mode=left_mode,
        right_mode=right_mode,
        left_reach=left_reach,
        right_reach=right_reach,
    )


def manhattan_distance(point_a: tuple[int, int], point_b: tuple[int, int]) -> int:
    """Return the Manhattan distance between two workspace points."""

    return abs(point_a[0] - point_b[0]) + abs(point_a[1] - point_b[1])


def arm_can_contact_object(state: DualArmManipulationState, *, left_arm: bool) -> bool:
    """Return whether one arm can contact the current object pose."""

    base = LEFT_BASE if left_arm else RIGHT_BASE
    reach = state.left_reach if left_arm else state.right_reach
    return manhattan_distance(base, (state.obj_x, state.obj_y)) <= reach + 1


def active_support_count(state: DualArmManipulationState) -> int:
    """Return how many arms are currently active on the object."""

    return int(state.left_mode != 0) + int(state.right_mode != 0)


def has_required_side_support(state: DualArmManipulationState) -> bool:
    """Return whether object placement is compatible with side-specific support."""

    if state.obj_x == 0:
        return state.left_mode != 0
    if state.obj_x == 2:
        return state.right_mode != 0
    return True


def is_valid_state(state: DualArmManipulationState) -> bool:
    """Return whether a state satisfies the dual-arm coordination rules."""

    if not 0 <= state.obj_x < GRID_SIZE or not 0 <= state.obj_y < GRID_SIZE:
        return False
    if not 0 <= state.obj_theta < THETA_COUNT:
        return False
    if not 0 <= state.left_mode < ARM_MODE_COUNT or not 0 <= state.right_mode < ARM_MODE_COUNT:
        return False
    if not 0 <= state.left_reach < REACH_COUNT or not 0 <= state.right_reach < REACH_COUNT:
        return False

    if state.left_mode != 0 and not arm_can_contact_object(state, left_arm=True):
        return False
    if state.right_mode != 0 and not arm_can_contact_object(state, left_arm=False):
        return False

    support_count = active_support_count(state)
    if support_count == 0:
        return False
    if not has_required_side_support(state):
        return False
    if state.obj_y == 2 and support_count < 2:
        return False
    if state.obj_theta == 1 and support_count < 2:
        return False
    if state.obj_theta == 1 and state.left_mode != 2 and state.right_mode != 2:
        return False
    return True


def has_valid_start_state() -> bool:
    """Return whether the configured start state is valid."""

    return is_valid_state(START_STATE)


def has_valid_goal_state() -> bool:
    """Return whether the configured goal state is valid."""

    return is_valid_state(CANDIDATE_GOAL_STATE)


def propose_primitive_action(
    state: DualArmManipulationState, action: int
) -> DualArmManipulationState:
    """Return the candidate state produced by one primitive action proposal."""

    if action == 0:
        return DualArmManipulationState(
            obj_x=min(state.obj_x + 1, GRID_SIZE - 1),
            obj_y=state.obj_y,
            obj_theta=state.obj_theta,
            left_mode=state.left_mode,
            right_mode=state.right_mode,
            left_reach=state.left_reach,
            right_reach=state.right_reach,
        )
    if action == 1:
        return DualArmManipulationState(
            obj_x=max(state.obj_x - 1, 0),
            obj_y=state.obj_y,
            obj_theta=state.obj_theta,
            left_mode=state.left_mode,
            right_mode=state.right_mode,
            left_reach=state.left_reach,
            right_reach=state.right_reach,
        )
    if action == 2:
        return DualArmManipulationState(
            obj_x=state.obj_x,
            obj_y=min(state.obj_y + 1, GRID_SIZE - 1),
            obj_theta=state.obj_theta,
            left_mode=state.left_mode,
            right_mode=state.right_mode,
            left_reach=state.left_reach,
            right_reach=state.right_reach,
        )
    if action == 3:
        return DualArmManipulationState(
            obj_x=state.obj_x,
            obj_y=max(state.obj_y - 1, 0),
            obj_theta=state.obj_theta,
            left_mode=state.left_mode,
            right_mode=state.right_mode,
            left_reach=state.left_reach,
            right_reach=state.right_reach,
        )
    if action == 4:
        return DualArmManipulationState(
            obj_x=state.obj_x,
            obj_y=state.obj_y,
            obj_theta=1 - state.obj_theta,
            left_mode=state.left_mode,
            right_mode=state.right_mode,
            left_reach=state.left_reach,
            right_reach=state.right_reach,
        )
    if action == 5:
        return DualArmManipulationState(
            obj_x=state.obj_x,
            obj_y=state.obj_y,
            obj_theta=state.obj_theta,
            left_mode=(state.left_mode + 1) % ARM_MODE_COUNT,
            right_mode=state.right_mode,
            left_reach=state.left_reach,
            right_reach=state.right_reach,
        )
    if action == 6:
        return DualArmManipulationState(
            obj_x=state.obj_x,
            obj_y=state.obj_y,
            obj_theta=state.obj_theta,
            left_mode=state.left_mode,
            right_mode=(state.right_mode + 1) % ARM_MODE_COUNT,
            left_reach=state.left_reach,
            right_reach=state.right_reach,
        )
    if action == 7:
        return DualArmManipulationState(
            obj_x=state.obj_x,
            obj_y=state.obj_y,
            obj_theta=state.obj_theta,
            left_mode=state.left_mode,
            right_mode=state.right_mode,
            left_reach=min(state.left_reach + 1, REACH_COUNT - 1),
            right_reach=state.right_reach,
        )
    if action == 8:
        return DualArmManipulationState(
            obj_x=state.obj_x,
            obj_y=state.obj_y,
            obj_theta=state.obj_theta,
            left_mode=state.left_mode,
            right_mode=state.right_mode,
            left_reach=max(state.left_reach - 1, 0),
            right_reach=state.right_reach,
        )
    if action == 9:
        return DualArmManipulationState(
            obj_x=state.obj_x,
            obj_y=state.obj_y,
            obj_theta=state.obj_theta,
            left_mode=state.left_mode,
            right_mode=state.right_mode,
            left_reach=state.left_reach,
            right_reach=min(state.right_reach + 1, REACH_COUNT - 1),
        )
    if action == 10:
        return DualArmManipulationState(
            obj_x=state.obj_x,
            obj_y=state.obj_y,
            obj_theta=state.obj_theta,
            left_mode=state.left_mode,
            right_mode=state.right_mode,
            left_reach=state.left_reach,
            right_reach=max(state.right_reach - 1, 0),
        )
    raise ValueError(f"Unsupported action: {action}")


def primitive_transition(
    state: DualArmManipulationState, action: int
) -> PrimitiveTransitionResult:
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


def is_goal_state(state: DualArmManipulationState) -> bool:
    """Return whether a state matches the configured goal."""

    return state == CANDIDATE_GOAL_STATE


def transition_reward(
    state: DualArmManipulationState,
    action: int,
    next_state: DualArmManipulationState,
) -> float:
    """Return the reward for one primitive transition."""

    result = primitive_transition(state, action)
    if result.invalid_move:
        return -2.0
    if is_goal_state(next_state):
        return 20.0
    return -1.0


def transition_terminated(state: DualArmManipulationState) -> bool:
    """Return whether an episode should terminate at the given state."""

    return is_goal_state(state)


def transition_truncated(step_count: int, terminated: bool) -> bool:
    """Return whether an episode should truncate at the current step count."""

    return (not terminated) and step_count >= MAX_STEPS


def all_candidate_states() -> tuple[DualArmManipulationState, ...]:
    """Return the full ambient discrete candidate state set."""

    states: list[DualArmManipulationState] = []
    for obj_x in range(GRID_SIZE):
        for obj_y in range(GRID_SIZE):
            for obj_theta in range(THETA_COUNT):
                for left_mode in range(ARM_MODE_COUNT):
                    for right_mode in range(ARM_MODE_COUNT):
                        for left_reach in range(REACH_COUNT):
                            for right_reach in range(REACH_COUNT):
                                states.append(
                                    DualArmManipulationState(
                                        obj_x=obj_x,
                                        obj_y=obj_y,
                                        obj_theta=obj_theta,
                                        left_mode=left_mode,
                                        right_mode=right_mode,
                                        left_reach=left_reach,
                                        right_reach=right_reach,
                                    )
                                )
    return tuple(states)


def all_valid_states() -> tuple[DualArmManipulationState, ...]:
    """Return the valid hidden-state subset."""

    return tuple(state for state in all_candidate_states() if is_valid_state(state))


def valid_outgoing_transitions(
    state: DualArmManipulationState,
) -> tuple[tuple[int, DualArmManipulationState], ...]:
    """Return valid primitive outgoing transitions from one state."""

    transitions: list[tuple[int, DualArmManipulationState]] = []
    for action in range(ACTION_COUNT):
        result = primitive_transition(state, action)
        if result.invalid_move:
            continue
        transitions.append((action, result.next_state))
    return tuple(transitions)


class DualArmManipulationEnv(gymnasium.Env[np.ndarray, int]):
    """Gymnasium-compatible discrete dual-arm manipulation environment."""

    metadata = {"render_modes": []}

    def __init__(self) -> None:
        super().__init__()
        self.action_space = gymnasium.spaces.Discrete(ACTION_COUNT)
        self.observation_space = gymnasium.spaces.MultiDiscrete([3, 3, 2, 3, 3, 3, 3])
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
    "ARM_MODE_COUNT",
    "CANDIDATE_GOAL_STATE",
    "DualArmManipulationEnv",
    "DualArmManipulationState",
    "GRID_SIZE",
    "LEFT_BASE",
    "MAX_STEPS",
    "PrimitiveTransitionResult",
    "REACH_COUNT",
    "RIGHT_BASE",
    "START_STATE",
    "THETA_COUNT",
    "active_support_count",
    "all_candidate_states",
    "all_valid_states",
    "arm_can_contact_object",
    "decode_observation",
    "encode_observation",
    "has_required_side_support",
    "has_valid_goal_state",
    "has_valid_start_state",
    "is_goal_state",
    "is_valid_state",
    "manhattan_distance",
    "primitive_transition",
    "propose_primitive_action",
    "transition_reward",
    "transition_terminated",
    "transition_truncated",
    "valid_outgoing_transitions",
]
