"""Discrete articulated-loop environment for package evaluation."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import gymnasium
import numpy as np


@dataclass(frozen=True, slots=True)
class ArticulatedLoopState:
    """Immutable internal state for ArticulatedLoopEnv."""

    d1: int
    d2: int
    d3: int
    brace_mode: int
    coupler_slack: int


@dataclass(frozen=True, slots=True)
class PrimitiveTransitionResult:
    """Detailed one-step transition metadata for ArticulatedLoopEnv."""

    candidate_state: ArticulatedLoopState
    next_state: ArticulatedLoopState
    candidate_valid: bool
    valid_transition: bool
    invalid_move: bool
    valid_self_transition: bool


DIRECTION_COUNT = 4
BRACE_MODE_COUNT = 2
COUPLER_SLACK_COUNT = 3
MAX_STEPS = 30
ACTION_COUNT = 9
START_STATE = ArticulatedLoopState(0, 1, 3, 0, 2)
CANDIDATE_GOAL_STATE = ArticulatedLoopState(0, 2, 1, 1, 0)


def encode_observation(state: ArticulatedLoopState) -> np.ndarray:
    """Encode an internal state into the canonical observation array."""

    return np.asarray(
        [state.d1, state.d2, state.d3, state.brace_mode, state.coupler_slack],
        dtype=np.int64,
    )


def decode_observation(values: Iterable[int]) -> ArticulatedLoopState:
    """Decode an observation-like iterable into an internal state."""

    d1, d2, d3, brace_mode, coupler_slack = tuple(int(value) for value in values)
    return ArticulatedLoopState(
        d1=d1,
        d2=d2,
        d3=d3,
        brace_mode=brace_mode,
        coupler_slack=coupler_slack,
    )


def direction_vector(direction: int) -> tuple[int, int]:
    """Return the unit vector corresponding to one direction bin."""

    if direction == 0:
        return (1, 0)
    if direction == 1:
        return (0, 1)
    if direction == 2:
        return (-1, 0)
    if direction == 3:
        return (0, -1)
    raise ValueError(f"Unsupported direction: {direction}")


def brace_target(brace_mode: int) -> tuple[int, int]:
    """Return the required loop-closure target for one brace mode."""

    if brace_mode == 0:
        return (1, 0)
    if brace_mode == 1:
        return (0, 1)
    raise ValueError(f"Unsupported brace_mode: {brace_mode}")


def endpoint_sum(state: ArticulatedLoopState) -> tuple[int, int]:
    """Return the endpoint vector sum induced by the three link directions."""

    vectors = [direction_vector(direction) for direction in (state.d1, state.d2, state.d3)]
    return (sum(vector[0] for vector in vectors), sum(vector[1] for vector in vectors))


def closure_mismatch(state: ArticulatedLoopState) -> int:
    """Return the Manhattan mismatch between endpoint sum and brace target."""

    endpoint_x, endpoint_y = endpoint_sum(state)
    target_x, target_y = brace_target(state.brace_mode)
    return abs(endpoint_x - target_x) + abs(endpoint_y - target_y)


def is_valid_state(state: ArticulatedLoopState) -> bool:
    """Return whether a state satisfies the discrete loop-closure rule."""

    if not all(0 <= direction < DIRECTION_COUNT for direction in (state.d1, state.d2, state.d3)):
        return False
    if not 0 <= state.brace_mode < BRACE_MODE_COUNT:
        return False
    if not 0 <= state.coupler_slack < COUPLER_SLACK_COUNT:
        return False
    return closure_mismatch(state) <= state.coupler_slack


def has_valid_start_state() -> bool:
    """Return whether the configured start state is valid."""

    return is_valid_state(START_STATE)


def has_valid_goal_state() -> bool:
    """Return whether the configured goal state is valid."""

    return is_valid_state(CANDIDATE_GOAL_STATE)


def propose_primitive_action(state: ArticulatedLoopState, action: int) -> ArticulatedLoopState:
    """Return the candidate state produced by one primitive action proposal."""

    if action == 0:
        return ArticulatedLoopState(
            (state.d1 + 1) % 4, state.d2, state.d3, state.brace_mode, state.coupler_slack
        )
    if action == 1:
        return ArticulatedLoopState(
            (state.d1 - 1) % 4, state.d2, state.d3, state.brace_mode, state.coupler_slack
        )
    if action == 2:
        return ArticulatedLoopState(
            state.d1, (state.d2 + 1) % 4, state.d3, state.brace_mode, state.coupler_slack
        )
    if action == 3:
        return ArticulatedLoopState(
            state.d1, (state.d2 - 1) % 4, state.d3, state.brace_mode, state.coupler_slack
        )
    if action == 4:
        return ArticulatedLoopState(
            state.d1, state.d2, (state.d3 + 1) % 4, state.brace_mode, state.coupler_slack
        )
    if action == 5:
        return ArticulatedLoopState(
            state.d1, state.d2, (state.d3 - 1) % 4, state.brace_mode, state.coupler_slack
        )
    if action == 6:
        return ArticulatedLoopState(
            state.d1, state.d2, state.d3, 1 - state.brace_mode, state.coupler_slack
        )
    if action == 7:
        return ArticulatedLoopState(
            state.d1,
            state.d2,
            state.d3,
            state.brace_mode,
            min(state.coupler_slack + 1, COUPLER_SLACK_COUNT - 1),
        )
    if action == 8:
        return ArticulatedLoopState(
            state.d1,
            state.d2,
            state.d3,
            state.brace_mode,
            max(state.coupler_slack - 1, 0),
        )
    raise ValueError(f"Unsupported action: {action}")


def primitive_transition(state: ArticulatedLoopState, action: int) -> PrimitiveTransitionResult:
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


def is_goal_state(state: ArticulatedLoopState) -> bool:
    """Return whether a state matches the configured goal."""

    return state == CANDIDATE_GOAL_STATE


def transition_reward(
    state: ArticulatedLoopState,
    action: int,
    next_state: ArticulatedLoopState,
) -> float:
    """Return the reward for one primitive transition."""

    result = primitive_transition(state, action)
    if result.invalid_move:
        return -2.0
    if is_goal_state(next_state):
        return 20.0
    return -1.0


def transition_terminated(state: ArticulatedLoopState) -> bool:
    """Return whether an episode should terminate at the given state."""

    return is_goal_state(state)


def transition_truncated(step_count: int, terminated: bool) -> bool:
    """Return whether an episode should truncate at the current step count."""

    return (not terminated) and step_count >= MAX_STEPS


def all_candidate_states() -> tuple[ArticulatedLoopState, ...]:
    """Return the full ambient discrete candidate state set."""

    states: list[ArticulatedLoopState] = []
    for d1 in range(DIRECTION_COUNT):
        for d2 in range(DIRECTION_COUNT):
                for d3 in range(DIRECTION_COUNT):
                    for brace_mode in range(BRACE_MODE_COUNT):
                        for coupler_slack in range(COUPLER_SLACK_COUNT):
                            states.append(
                                ArticulatedLoopState(
                                    d1,
                                    d2,
                                    d3,
                                    brace_mode,
                                    coupler_slack,
                                )
                            )
    return tuple(states)


def all_valid_states() -> tuple[ArticulatedLoopState, ...]:
    """Return the valid hidden-state subset."""

    return tuple(state for state in all_candidate_states() if is_valid_state(state))


def valid_outgoing_transitions(
    state: ArticulatedLoopState,
) -> tuple[tuple[int, ArticulatedLoopState], ...]:
    """Return valid primitive outgoing transitions from one state."""

    transitions: list[tuple[int, ArticulatedLoopState]] = []
    for action in range(ACTION_COUNT):
        result = primitive_transition(state, action)
        if result.invalid_move:
            continue
        transitions.append((action, result.next_state))
    return tuple(transitions)


class ArticulatedLoopEnv(gymnasium.Env[np.ndarray, int]):
    """Gymnasium-compatible discrete articulated-loop environment."""

    metadata = {"render_modes": []}

    def __init__(self) -> None:
        """Initialize spaces, start state, and episode step counter."""

        super().__init__()
        self.action_space = gymnasium.spaces.Discrete(ACTION_COUNT)
        self.observation_space = gymnasium.spaces.MultiDiscrete([4, 4, 4, 2, 3])
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
        """Apply one articulated-loop action and return Gymnasium outputs."""

        if isinstance(action, bool) or not self.action_space.contains(action):
            raise ValueError(f"Unsupported action index: {action}")

        action_index = int(action)
        result = primitive_transition(self.state, action_index)
        self.state = result.next_state
        self.step_count += 1
        reward_source = result.candidate_state if result.invalid_move else self.state
        reward = transition_reward(reward_source, action_index, self.state)
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
    "ArticulatedLoopEnv",
    "ArticulatedLoopState",
    "COUPLER_SLACK_COUNT",
    "CANDIDATE_GOAL_STATE",
    "MAX_STEPS",
    "PrimitiveTransitionResult",
    "START_STATE",
    "all_candidate_states",
    "all_valid_states",
    "brace_target",
    "closure_mismatch",
    "decode_observation",
    "direction_vector",
    "encode_observation",
    "endpoint_sum",
    "has_valid_goal_state",
    "has_valid_start_state",
    "is_goal_state",
    "is_valid_state",
    "primitive_transition",
    "propose_primitive_action",
    "transition_reward",
    "transition_terminated",
    "transition_truncated",
    "valid_outgoing_transitions",
]
