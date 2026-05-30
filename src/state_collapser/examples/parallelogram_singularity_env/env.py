"""Discrete parallelogram-singularity environment for package evaluation."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import gymnasium
import numpy as np


@dataclass(frozen=True, slots=True)
class ParallelogramState:
    """Immutable internal state for ParallelogramSingularityEnv."""

    left_angle: int
    right_angle: int
    span: int
    alignment_mode: int


@dataclass(frozen=True, slots=True)
class PrimitiveTransitionResult:
    """Detailed one-step transition metadata for ParallelogramSingularityEnv."""

    candidate_state: ParallelogramState
    next_state: ParallelogramState
    candidate_valid: bool
    valid_transition: bool
    invalid_move: bool
    valid_self_transition: bool


ANGLE_COUNT = 4
SPAN_COUNT = 3
ALIGNMENT_MODE_COUNT = 2
MAX_STEPS = 24
ACTION_COUNT = 7

START_STATE = ParallelogramState(0, 0, 0, 0)
CANDIDATE_GOAL_STATE = ParallelogramState(0, 2, 2, 1)


def encode_observation(state: ParallelogramState) -> np.ndarray:
    """Encode one internal state into the canonical observation array."""

    return np.asarray(
        [state.left_angle, state.right_angle, state.span, state.alignment_mode],
        dtype=np.int64,
    )


def decode_observation(values: Iterable[int]) -> ParallelogramState:
    """Decode an observation-like iterable into an internal state."""

    left_angle, right_angle, span, alignment_mode = (int(value) for value in values)
    return ParallelogramState(
        left_angle=left_angle,
        right_angle=right_angle,
        span=span,
        alignment_mode=alignment_mode,
    )


def cyclic_angle_gap(left_angle: int, right_angle: int) -> int:
    """Return the minimum cyclic angle gap between two angle bins."""

    raw_gap = abs(left_angle - right_angle) % ANGLE_COUNT
    return min(raw_gap, ANGLE_COUNT - raw_gap)


def is_singular_state(state: ParallelogramState) -> bool:
    """Return whether the state lies in one of the singular span regimes."""

    return state.span in (0, SPAN_COUNT - 1)


def is_valid_state(state: ParallelogramState) -> bool:
    """Return whether a state satisfies the linkage consistency rules."""

    if not 0 <= state.left_angle < ANGLE_COUNT or not 0 <= state.right_angle < ANGLE_COUNT:
        return False
    if not 0 <= state.span < SPAN_COUNT:
        return False
    if not 0 <= state.alignment_mode < ALIGNMENT_MODE_COUNT:
        return False

    gap = cyclic_angle_gap(state.left_angle, state.right_angle)
    if state.span == 0:
        return gap == 0 and state.alignment_mode == 0
    if state.span == 1:
        if state.alignment_mode == 0:
            return gap in (0, 1)
        return gap == 1
    return gap == 2 and state.alignment_mode == 1


def has_valid_start_state() -> bool:
    """Return whether the configured start state is valid."""

    return is_valid_state(START_STATE)


def has_valid_goal_state() -> bool:
    """Return whether the configured goal state is valid."""

    return is_valid_state(CANDIDATE_GOAL_STATE)


def propose_primitive_action(state: ParallelogramState, action: int) -> ParallelogramState:
    """Return the candidate state produced by one primitive action proposal."""

    if action == 0:
        return ParallelogramState(
            (state.left_angle + 1) % ANGLE_COUNT,
            state.right_angle,
            state.span,
            state.alignment_mode,
        )
    if action == 1:
        return ParallelogramState(
            (state.left_angle - 1) % ANGLE_COUNT,
            state.right_angle,
            state.span,
            state.alignment_mode,
        )
    if action == 2:
        return ParallelogramState(
            state.left_angle,
            (state.right_angle + 1) % ANGLE_COUNT,
            state.span,
            state.alignment_mode,
        )
    if action == 3:
        return ParallelogramState(
            state.left_angle,
            (state.right_angle - 1) % ANGLE_COUNT,
            state.span,
            state.alignment_mode,
        )
    if action == 4:
        return ParallelogramState(
            state.left_angle,
            state.right_angle,
            min(state.span + 1, SPAN_COUNT - 1),
            state.alignment_mode,
        )
    if action == 5:
        return ParallelogramState(
            state.left_angle,
            state.right_angle,
            max(state.span - 1, 0),
            state.alignment_mode,
        )
    if action == 6:
        return ParallelogramState(
            state.left_angle,
            state.right_angle,
            state.span,
            1 - state.alignment_mode,
        )
    raise ValueError(f"Unsupported action: {action}")


def primitive_transition(state: ParallelogramState, action: int) -> PrimitiveTransitionResult:
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


def is_goal_state(state: ParallelogramState) -> bool:
    """Return whether a state matches the configured goal."""

    return state == CANDIDATE_GOAL_STATE


def transition_reward(
    state: ParallelogramState, action: int, next_state: ParallelogramState
) -> float:
    """Return the reward for one primitive transition."""

    result = primitive_transition(state, action)
    if result.invalid_move:
        return -2.0
    if is_goal_state(next_state):
        return 20.0
    return -1.0


def transition_terminated(state: ParallelogramState) -> bool:
    """Return whether an episode should terminate at the given state."""

    return is_goal_state(state)


def transition_truncated(step_count: int, terminated: bool) -> bool:
    """Return whether an episode should truncate at the current step count."""

    return (not terminated) and step_count >= MAX_STEPS


def all_candidate_states() -> tuple[ParallelogramState, ...]:
    """Return the full ambient discrete candidate state set."""

    states: list[ParallelogramState] = []
    for left_angle in range(ANGLE_COUNT):
        for right_angle in range(ANGLE_COUNT):
            for span in range(SPAN_COUNT):
                for alignment_mode in range(ALIGNMENT_MODE_COUNT):
                    states.append(ParallelogramState(left_angle, right_angle, span, alignment_mode))
    return tuple(states)


def all_valid_states() -> tuple[ParallelogramState, ...]:
    """Return the valid hidden-state subset."""

    return tuple(state for state in all_candidate_states() if is_valid_state(state))


def valid_outgoing_transitions(
    state: ParallelogramState,
) -> tuple[tuple[int, ParallelogramState], ...]:
    """Return valid primitive outgoing transitions from one state."""

    transitions: list[tuple[int, ParallelogramState]] = []
    for action in range(ACTION_COUNT):
        result = primitive_transition(state, action)
        if result.invalid_move:
            continue
        transitions.append((action, result.next_state))
    return tuple(transitions)


class ParallelogramSingularityEnv(gymnasium.Env[np.ndarray, int]):
    """Gymnasium-compatible discrete parallelogram singularity environment."""

    metadata = {"render_modes": []}

    def __init__(self) -> None:
        """Initialize spaces, start state, and episode step counter."""

        super().__init__()
        self.action_space = gymnasium.spaces.Discrete(ACTION_COUNT)
        self.observation_space = gymnasium.spaces.MultiDiscrete([4, 4, 3, 2])
        self.state = START_STATE
        self.step_count = 0

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, object] | None = None,
    ) -> tuple[np.ndarray, dict[str, object]]:
        """Reset to the fixed start state and return observation metadata."""

        super().reset(seed=seed)
        del options
        self.state = START_STATE
        self.step_count = 0
        return encode_observation(self.state), {"state": self.state}

    def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict[str, object]]:
        """Apply one parallelogram action and return Gymnasium outputs."""

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
    "ALIGNMENT_MODE_COUNT",
    "ANGLE_COUNT",
    "CANDIDATE_GOAL_STATE",
    "MAX_STEPS",
    "ParallelogramSingularityEnv",
    "ParallelogramState",
    "PrimitiveTransitionResult",
    "SPAN_COUNT",
    "START_STATE",
    "all_candidate_states",
    "all_valid_states",
    "cyclic_angle_gap",
    "decode_observation",
    "encode_observation",
    "has_valid_goal_state",
    "has_valid_start_state",
    "is_goal_state",
    "is_singular_state",
    "is_valid_state",
    "primitive_transition",
    "propose_primitive_action",
    "transition_reward",
    "transition_terminated",
    "transition_truncated",
    "valid_outgoing_transitions",
]
