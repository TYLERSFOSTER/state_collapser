"""Three-voice counterpoint environment for state_collapser evaluation."""

from __future__ import annotations

import random
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from functools import cache

import gymnasium
import numpy as np

DEFAULT_ALLOWED_ADJACENT_INTERVALS_MOD_12 = frozenset({3, 4, 5, 7, 8, 9})
DEFAULT_ALLOWED_OUTER_INTERVALS_MOD_12 = frozenset({3, 4, 5, 7, 8, 9})
DEFAULT_ALLOWED_ROOT_INTERVALS_FROM_TONIC_MOD_12 = frozenset({0, 3, 4, 5, 7, 8, 9})
DEFAULT_FORBIDDEN_PARALLEL_INTERVAL_CLASSES = frozenset({0, 7})
DEFAULT_TERMINAL_OUTER_INTERVAL_CLASSES = frozenset({7})
DEFAULT_TERMINAL_INNER_INTERVALS_FROM_BASS_MOD_12 = frozenset({3, 4})


StepDelta = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class RlCounterpointState:
    """Immutable graph state for the first three-voice counterpoint example."""

    bass_pitch: int
    inner_pitch: int
    upper_pitch: int
    beat_index: int


@dataclass(frozen=True, slots=True)
class RlCounterpointGraphSpec:
    """Small explicit graph contract for the first counterpoint example."""

    tonic_pitch_class: int = 0
    pitch_min: int = 48
    pitch_max: int = 79
    measure_size: int = 4
    max_steps: int = 16
    max_step_size: int = 2
    allowed_adjacent_intervals_mod_12: frozenset[int] = field(
        default_factory=lambda: DEFAULT_ALLOWED_ADJACENT_INTERVALS_MOD_12
    )
    allowed_outer_intervals_mod_12: frozenset[int] = field(
        default_factory=lambda: DEFAULT_ALLOWED_OUTER_INTERVALS_MOD_12
    )
    allowed_root_intervals_from_tonic_mod_12: frozenset[int] = field(
        default_factory=lambda: DEFAULT_ALLOWED_ROOT_INTERVALS_FROM_TONIC_MOD_12
    )
    forbidden_parallel_interval_classes: frozenset[int] = field(
        default_factory=lambda: DEFAULT_FORBIDDEN_PARALLEL_INTERVAL_CLASSES
    )
    max_outer_span: int = 15
    require_strict_voice_order: bool = True

    def __post_init__(self) -> None:
        if self.pitch_min > self.pitch_max:
            raise ValueError("pitch_min must be <= pitch_max")
        if self.measure_size < 1:
            raise ValueError("measure_size must be at least 1")
        if self.max_steps < 1:
            raise ValueError("max_steps must be at least 1")
        if self.max_step_size < 1:
            raise ValueError("max_step_size must be at least 1")
        if self.max_outer_span < 1:
            raise ValueError("max_outer_span must be at least 1")
        if not self.allowed_adjacent_intervals_mod_12:
            raise ValueError("allowed_adjacent_intervals_mod_12 must not be empty")
        if not self.allowed_outer_intervals_mod_12:
            raise ValueError("allowed_outer_intervals_mod_12 must not be empty")
        if not self.allowed_root_intervals_from_tonic_mod_12:
            raise ValueError("allowed_root_intervals_from_tonic_mod_12 must not be empty")
        if not all(0 <= value <= 11 for value in self.allowed_adjacent_intervals_mod_12):
            raise ValueError("allowed_adjacent_intervals_mod_12 must lie in [0, 11]")
        if not all(0 <= value <= 11 for value in self.allowed_outer_intervals_mod_12):
            raise ValueError("allowed_outer_intervals_mod_12 must lie in [0, 11]")
        if not all(0 <= value <= 11 for value in self.allowed_root_intervals_from_tonic_mod_12):
            raise ValueError("allowed_root_intervals_from_tonic_mod_12 must lie in [0, 11]")
        if not all(0 <= value <= 11 for value in self.forbidden_parallel_interval_classes):
            raise ValueError("forbidden_parallel_interval_classes must lie in [0, 11]")

    @property
    def allowed_root_pitch_classes(self) -> frozenset[int]:
        return frozenset(
            (self.tonic_pitch_class + interval) % 12
            for interval in self.allowed_root_intervals_from_tonic_mod_12
        )


@dataclass(frozen=True, slots=True)
class PrimitiveTransitionResult:
    """Detailed one-step transition metadata for RlCounterpointEnv."""

    candidate_state: RlCounterpointState
    next_state: RlCounterpointState
    candidate_valid: bool
    valid_transition: bool
    invalid_move: bool
    valid_self_transition: bool


@dataclass(frozen=True, slots=True)
class RewardContext:
    """Explicit reward context for one transition."""

    step_index: int
    max_steps: int
    measure_size: int
    source_state: RlCounterpointState
    target_state: RlCounterpointState
    action: StepDelta
    history: tuple[RlCounterpointState, ...]
    is_final_step: bool
    is_terminal_step: bool


@dataclass(frozen=True, slots=True)
class RewardResult:
    """Structured reward output for one transition."""

    reward: float
    terminal_success: bool = False
    hard_violation: bool = False
    diagnostics: Mapping[str, object] = field(default_factory=dict)


DEFAULT_GRAPH_SPEC = RlCounterpointGraphSpec()
MAX_STEPS = DEFAULT_GRAPH_SPEC.max_steps


def pitch_class(pitch: int) -> int:
    """Return the pitch class modulo 12."""

    return pitch % 12


def adjacent_intervals(state: RlCounterpointState) -> tuple[int, int]:
    """Return the adjacent vertical intervals."""

    return (
        state.inner_pitch - state.bass_pitch,
        state.upper_pitch - state.inner_pitch,
    )


def outer_interval(state: RlCounterpointState) -> int:
    """Return the bass-to-upper interval."""

    return state.upper_pitch - state.bass_pitch


def encode_observation(state: RlCounterpointState) -> np.ndarray:
    """Encode one internal state into the canonical observation array."""

    return np.asarray(
        [state.bass_pitch, state.inner_pitch, state.upper_pitch, state.beat_index],
        dtype=np.int64,
    )


def decode_observation(values: Iterable[int]) -> RlCounterpointState:
    """Decode an observation-like iterable into an internal state."""

    bass_pitch, inner_pitch, upper_pitch, beat_index = tuple(int(value) for value in values)
    return RlCounterpointState(
        bass_pitch=bass_pitch,
        inner_pitch=inner_pitch,
        upper_pitch=upper_pitch,
        beat_index=beat_index,
    )


@cache
def step_delta_action_space(max_step_size: int) -> tuple[StepDelta, ...]:
    """Return the bounded nonzero three-voice step-delta lattice."""

    if max_step_size < 1:
        raise ValueError("max_step_size must be at least 1")
    actions: list[StepDelta] = []
    for bass_delta in range(-max_step_size, max_step_size + 1):
        for inner_delta in range(-max_step_size, max_step_size + 1):
            for upper_delta in range(-max_step_size, max_step_size + 1):
                delta = (bass_delta, inner_delta, upper_delta)
                if delta != (0, 0, 0):
                    actions.append(delta)
    return tuple(actions)


ACTION_SPACE = step_delta_action_space(DEFAULT_GRAPH_SPEC.max_step_size)
ACTION_COUNT = len(ACTION_SPACE)


def action_index_to_step_delta(
    action: int,
    *,
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> StepDelta:
    """Decode one discrete action index into a StepDelta."""

    action_space = step_delta_action_space(spec.max_step_size)
    if not 0 <= action < len(action_space):
        raise ValueError(f"Unsupported action index: {action}")
    return action_space[action]


def step_delta_to_action_index(
    step_delta: StepDelta,
    *,
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> int:
    """Encode one StepDelta into its discrete action index."""

    action_space = step_delta_action_space(spec.max_step_size)
    try:
        return action_space.index(step_delta)
    except ValueError as exc:
        raise ValueError(f"Unsupported step delta: {step_delta!r}") from exc


def propose_primitive_action(
    state: RlCounterpointState,
    action: int,
    *,
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> RlCounterpointState:
    """Return the candidate state produced by one primitive action proposal."""

    bass_delta, inner_delta, upper_delta = action_index_to_step_delta(action, spec=spec)
    return RlCounterpointState(
        bass_pitch=state.bass_pitch + bass_delta,
        inner_pitch=state.inner_pitch + inner_delta,
        upper_pitch=state.upper_pitch + upper_delta,
        beat_index=(state.beat_index + 1) % spec.measure_size,
    )


def is_terminal_beat(state: RlCounterpointState, *, spec: RlCounterpointGraphSpec) -> bool:
    """Return whether the state lies in the first terminal beat regime."""

    return state.beat_index == spec.measure_size - 1


def has_valid_beat_index(state: RlCounterpointState, spec: RlCounterpointGraphSpec) -> bool:
    """Return whether the beat index lies inside the measure."""

    return 0 <= state.beat_index < spec.measure_size


def is_in_pitch_range(state: RlCounterpointState, spec: RlCounterpointGraphSpec) -> bool:
    """Return whether all pitches lie inside the configured band."""

    return all(
        spec.pitch_min <= pitch <= spec.pitch_max
        for pitch in (state.bass_pitch, state.inner_pitch, state.upper_pitch)
    )


def has_strict_voice_order(state: RlCounterpointState) -> bool:
    """Return whether the voices remain strictly ordered."""

    return state.bass_pitch < state.inner_pitch < state.upper_pitch


def has_valid_adjacent_intervals(state: RlCounterpointState, spec: RlCounterpointGraphSpec) -> bool:
    """Return whether the adjacent vertical intervals are permitted."""

    return all(
        interval > 0 and interval % 12 in spec.allowed_adjacent_intervals_mod_12
        for interval in adjacent_intervals(state)
    )


def has_valid_outer_interval(state: RlCounterpointState, spec: RlCounterpointGraphSpec) -> bool:
    """Return whether the outer interval is permitted."""

    interval = outer_interval(state)
    return interval > 0 and interval <= spec.max_outer_span and (
        interval % 12 in spec.allowed_outer_intervals_mod_12
    )


def has_valid_root_pitch_class(state: RlCounterpointState, spec: RlCounterpointGraphSpec) -> bool:
    """Return whether the bass pitch class lies in the allowed root family."""

    return pitch_class(state.bass_pitch) in spec.allowed_root_pitch_classes


def is_valid_state(
    state: RlCounterpointState,
    *,
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> bool:
    """Return whether a state lies in the hidden valid node set."""

    if not has_valid_beat_index(state, spec):
        return False
    if not is_in_pitch_range(state, spec):
        return False
    if spec.require_strict_voice_order and not has_strict_voice_order(state):
        return False
    if not has_valid_adjacent_intervals(state, spec):
        return False
    if not has_valid_outer_interval(state, spec):
        return False
    return has_valid_root_pitch_class(state, spec)


def voice_motion(step_delta: StepDelta) -> tuple[int, int, int]:
    """Return the signed motion tuple itself for naming symmetry."""

    return step_delta


def is_parallel_perfect_outer_motion(
    source: RlCounterpointState,
    target: RlCounterpointState,
    *,
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> bool:
    """Return whether the outer voices form forbidden parallel perfect motion."""

    source_outer_class = outer_interval(source) % 12
    target_outer_class = outer_interval(target) % 12
    if (
        source_outer_class not in spec.forbidden_parallel_interval_classes
        or target_outer_class not in spec.forbidden_parallel_interval_classes
    ):
        return False

    bass_motion = target.bass_pitch - source.bass_pitch
    upper_motion = target.upper_pitch - source.upper_pitch
    if bass_motion == 0 or upper_motion == 0:
        return False
    return (bass_motion > 0) == (upper_motion > 0)


def is_valid_step_delta_action(
    source: RlCounterpointState,
    step_delta: StepDelta,
    *,
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> bool:
    """Return whether a step delta decodes to a valid hidden edge."""

    if step_delta == (0, 0, 0):
        return False
    if any(abs(delta) > spec.max_step_size for delta in step_delta):
        return False

    target = RlCounterpointState(
        bass_pitch=source.bass_pitch + step_delta[0],
        inner_pitch=source.inner_pitch + step_delta[1],
        upper_pitch=source.upper_pitch + step_delta[2],
        beat_index=(source.beat_index + 1) % spec.measure_size,
    )
    if not is_valid_state(source, spec=spec) or not is_valid_state(target, spec=spec):
        return False
    if is_parallel_perfect_outer_motion(source, target, spec=spec):
        return False
    return True


def primitive_transition(
    state: RlCounterpointState,
    action: int,
    *,
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> PrimitiveTransitionResult:
    """Apply one primitive action under the env legality rule."""

    candidate = propose_primitive_action(state, action, spec=spec)
    step_delta = action_index_to_step_delta(action, spec=spec)
    candidate_valid = is_valid_step_delta_action(state, step_delta, spec=spec)
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


def is_terminal_configuration(
    state: RlCounterpointState,
    *,
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> bool:
    """Return whether a state satisfies the first three-voice cadence target."""

    if not is_valid_state(state, spec=spec):
        return False
    if not is_terminal_beat(state, spec=spec):
        return False
    if pitch_class(state.bass_pitch) != spec.tonic_pitch_class:
        return False
    if outer_interval(state) % 12 not in DEFAULT_TERMINAL_OUTER_INTERVAL_CLASSES:
        return False
    inner_from_bass = (state.inner_pitch - state.bass_pitch) % 12
    return inner_from_bass in DEFAULT_TERMINAL_INNER_INTERVALS_FROM_BASS_MOD_12


def is_goal_state(
    state: RlCounterpointState,
    *,
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> bool:
    """Return whether a state matches the first terminal success condition."""

    return is_terminal_configuration(state, spec=spec)


def reward_context(
    *,
    step_index: int,
    source_state: RlCounterpointState,
    target_state: RlCounterpointState,
    action: StepDelta,
    history: tuple[RlCounterpointState, ...],
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> RewardContext:
    """Build the structured reward context for one transition."""

    return RewardContext(
        step_index=step_index,
        max_steps=spec.max_steps,
        measure_size=spec.measure_size,
        source_state=source_state,
        target_state=target_state,
        action=action,
        history=history,
        is_final_step=(step_index + 1) >= spec.max_steps,
        is_terminal_step=is_terminal_configuration(target_state, spec=spec),
    )


def evaluate_reward(context: RewardContext) -> RewardResult:
    """Score one transition using the first narrow reward surface."""

    target = context.target_state
    source = context.source_state
    step_delta = context.action
    diagnostics: dict[str, object] = {}

    reward = -0.1
    diagnostics["step_cost"] = -0.1

    target_adjacent = adjacent_intervals(target)
    target_outer_class = outer_interval(target) % 12
    target_inner_from_bass = (target.inner_pitch - target.bass_pitch) % 12

    consonance_bonus = 0.0
    if target_adjacent[0] % 12 in {3, 4, 5}:
        consonance_bonus += 0.05
    if target_adjacent[1] % 12 in {3, 4, 5}:
        consonance_bonus += 0.05
    if target_outer_class in {3, 4, 7}:
        consonance_bonus += 0.05
    reward += consonance_bonus
    diagnostics["consonance_bonus"] = consonance_bonus

    downbeat_bonus = 0.0
    if target.beat_index == 0 and target_outer_class in {7} and target_inner_from_bass in {3, 4}:
        downbeat_bonus = 0.15
    reward += downbeat_bonus
    diagnostics["downbeat_bonus"] = downbeat_bonus

    smoothness_penalty = -0.02 * max(sum(abs(delta) for delta in step_delta) - 1, 0)
    reward += smoothness_penalty
    diagnostics["smoothness_penalty"] = smoothness_penalty

    terminal_success = context.is_terminal_step
    terminal_bonus = 8.0 if terminal_success else 0.0
    reward += terminal_bonus
    diagnostics["terminal_bonus"] = terminal_bonus

    diagnostics["target_outer_interval_class"] = target_outer_class
    diagnostics["target_inner_from_bass_mod_12"] = target_inner_from_bass
    diagnostics["source_outer_interval_class"] = outer_interval(source) % 12

    return RewardResult(
        reward=reward,
        terminal_success=terminal_success,
        hard_violation=False,
        diagnostics=diagnostics,
    )


def transition_reward(
    state: RlCounterpointState,
    action: int,
    next_state: RlCounterpointState,
    *,
    step_index: int = 0,
    history: tuple[RlCounterpointState, ...] = (),
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> RewardResult:
    """Return the structured reward result for one primitive transition."""

    result = primitive_transition(state, action, spec=spec)
    if result.invalid_move:
        return RewardResult(
            reward=-1.0,
            terminal_success=False,
            hard_violation=True,
            diagnostics={"invalid_move": True},
        )

    context = reward_context(
        step_index=step_index,
        source_state=state,
        target_state=next_state,
        action=action_index_to_step_delta(action, spec=spec),
        history=history,
        spec=spec,
    )
    return evaluate_reward(context)


def transition_terminated(
    state: RlCounterpointState,
    *,
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> bool:
    """Return whether an episode should terminate at the given state."""

    return is_goal_state(state, spec=spec)


def transition_truncated(
    step_count: int,
    terminated: bool,
    *,
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> bool:
    """Return whether an episode should truncate at the current step count."""

    return (not terminated) and step_count >= spec.max_steps


@cache
def all_candidate_states(
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> tuple[RlCounterpointState, ...]:
    """Return the full ambient discrete candidate state set."""

    states: list[RlCounterpointState] = []
    for bass_pitch in range(spec.pitch_min, spec.pitch_max + 1):
        for inner_pitch in range(spec.pitch_min, spec.pitch_max + 1):
            for upper_pitch in range(spec.pitch_min, spec.pitch_max + 1):
                for beat_index in range(spec.measure_size):
                    states.append(
                        RlCounterpointState(
                            bass_pitch=bass_pitch,
                            inner_pitch=inner_pitch,
                            upper_pitch=upper_pitch,
                            beat_index=beat_index,
                        )
                    )
    return tuple(states)


@cache
def all_valid_states(
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> tuple[RlCounterpointState, ...]:
    """Return the valid hidden-state subset."""

    return tuple(state for state in all_candidate_states(spec) if is_valid_state(state, spec=spec))


@cache
def all_goal_states(
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> tuple[RlCounterpointState, ...]:
    """Return the valid terminal target subset."""

    return tuple(state for state in all_valid_states(spec) if is_goal_state(state, spec=spec))


def valid_outgoing_transitions(
    state: RlCounterpointState,
    *,
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> tuple[tuple[int, RlCounterpointState], ...]:
    """Return valid primitive outgoing transitions from one state."""

    outgoing: list[tuple[int, RlCounterpointState]] = []
    for action in range(len(step_delta_action_space(spec.max_step_size))):
        result = primitive_transition(state, action, spec=spec)
        if result.valid_transition:
            outgoing.append((action, result.next_state))
    return tuple(outgoing)


@cache
def curated_start_states(
    spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC,
) -> tuple[RlCounterpointState, ...]:
    """Return the curated valid nonterminal start-state subset."""

    return tuple(
        state
        for state in all_valid_states(spec)
        if state.beat_index == 0
        and not is_goal_state(state, spec=spec)
        and bool(valid_outgoing_transitions(state, spec=spec))
    )


def has_valid_start_state(spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC) -> bool:
    """Return whether the configured first-scope start-state subset is nonempty."""

    return bool(curated_start_states(spec))


def has_valid_goal_state(spec: RlCounterpointGraphSpec = DEFAULT_GRAPH_SPEC) -> bool:
    """Return whether the configured first-scope terminal subset is nonempty."""

    return bool(all_goal_states(spec))


START_STATE = curated_start_states(DEFAULT_GRAPH_SPEC)[0]
CANDIDATE_GOAL_STATE = all_goal_states(DEFAULT_GRAPH_SPEC)[0]


class RlCounterpointEnv(gymnasium.Env[np.ndarray, int]):
    """Small Gymnasium-style env for the first three-voice counterpoint problem."""

    metadata = {"render_modes": []}

    def __init__(
        self,
        graph_spec: RlCounterpointGraphSpec | None = None,
        *,
        invalid_action_penalty: float = -1.0,
    ) -> None:
        super().__init__()
        self.graph_spec = DEFAULT_GRAPH_SPEC if graph_spec is None else graph_spec
        self.invalid_action_penalty = invalid_action_penalty
        self._action_space_values = step_delta_action_space(self.graph_spec.max_step_size)
        self.action_space = gymnasium.spaces.Discrete(len(self._action_space_values))
        self.observation_space = gymnasium.spaces.Box(
            low=np.asarray(
                [
                    self.graph_spec.pitch_min,
                    self.graph_spec.pitch_min,
                    self.graph_spec.pitch_min,
                    0,
                ],
                dtype=np.int64,
            ),
            high=np.asarray(
                [
                    self.graph_spec.pitch_max,
                    self.graph_spec.pitch_max,
                    self.graph_spec.pitch_max,
                    self.graph_spec.measure_size - 1,
                ],
                dtype=np.int64,
            ),
            dtype=np.int64,
        )
        self._rng = random.Random(0)
        self._state = (
            START_STATE
            if self.graph_spec == DEFAULT_GRAPH_SPEC
            else curated_start_states(self.graph_spec)[0]
        )
        self._step_index = 0
        self._history: tuple[RlCounterpointState, ...] = (self._state,)

        if not curated_start_states(self.graph_spec):
            raise ValueError("graph must contain at least one curated valid start state")
        if not all_goal_states(self.graph_spec):
            raise ValueError("graph must contain at least one valid terminal goal state")

    @property
    def state(self) -> RlCounterpointState:
        return self._state

    @property
    def step_index(self) -> int:
        return self._step_index

    @property
    def history(self) -> tuple[RlCounterpointState, ...]:
        return self._history

    @property
    def step_deltas(self) -> tuple[StepDelta, ...]:
        return self._action_space_values

    @property
    def action_count(self) -> int:
        return len(self._action_space_values)

    def _action_mask(self, state: RlCounterpointState) -> tuple[bool, ...]:
        return tuple(
            primitive_transition(state, action, spec=self.graph_spec).valid_transition
            for action in range(self.action_count)
        )

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, object] | None = None,
    ) -> tuple[np.ndarray, dict[str, object]]:
        del options
        if seed is not None:
            self._rng.seed(seed)
        self._state = self._rng.choice(curated_start_states(self.graph_spec))
        self._step_index = 0
        self._history = (self._state,)
        return encode_observation(self._state), self._info_for_state(self._state)

    def step(
        self,
        action: int,
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, object]]:
        if isinstance(action, bool) or not self.action_space.contains(action):
            raise ValueError(f"Unsupported action index: {action}")

        action_index = int(action)
        source = self._state
        transition = primitive_transition(source, action_index, spec=self.graph_spec)
        if transition.invalid_move:
            self._step_index += 1
            self._history = (*self._history, source)
            truncated = transition_truncated(
                self._step_index,
                False,
                spec=self.graph_spec,
            )
            info = self._info_for_state(
                source,
                source_state=source,
                candidate_state=transition.candidate_state,
                action=action_index,
                valid_action=False,
                reward_diagnostics={"invalid_move": True},
            )
            return (
                encode_observation(source),
                self.invalid_action_penalty,
                False,
                truncated,
                info,
            )

        reward_result = transition_reward(
            source,
            action_index,
            transition.next_state,
            step_index=self._step_index,
            history=self._history,
            spec=self.graph_spec,
        )
        self._state = transition.next_state
        self._step_index += 1
        self._history = (*self._history, self._state)
        terminated = reward_result.terminal_success
        truncated = transition_truncated(
            self._step_index,
            terminated,
            spec=self.graph_spec,
        )
        info = self._info_for_state(
            self._state,
            source_state=source,
            candidate_state=transition.candidate_state,
            action=action_index,
            valid_action=True,
            reward_diagnostics=dict(reward_result.diagnostics),
            hard_violation=reward_result.hard_violation,
            is_terminal_success=reward_result.terminal_success,
        )
        return (
            encode_observation(self._state),
            reward_result.reward,
            terminated,
            truncated,
            info,
        )

    def _info_for_state(
        self,
        state: RlCounterpointState,
        **extra: object,
    ) -> dict[str, object]:
        action_mask = self._action_mask(state)
        return {
            "state": state,
            "step_index": self._step_index,
            "measure_size": self.graph_spec.measure_size,
            "history": self._history,
            "action_mask": action_mask,
            "action_space": self._action_space_values,
            "has_legal_actions": any(action_mask),
            **extra,
        }


__all__ = [
    "ACTION_COUNT",
    "ACTION_SPACE",
    "CANDIDATE_GOAL_STATE",
    "DEFAULT_GRAPH_SPEC",
    "MAX_STEPS",
    "PrimitiveTransitionResult",
    "RewardContext",
    "RewardResult",
    "RlCounterpointEnv",
    "RlCounterpointGraphSpec",
    "RlCounterpointState",
    "START_STATE",
    "StepDelta",
    "action_index_to_step_delta",
    "adjacent_intervals",
    "all_candidate_states",
    "all_goal_states",
    "all_valid_states",
    "curated_start_states",
    "decode_observation",
    "encode_observation",
    "evaluate_reward",
    "has_valid_goal_state",
    "has_valid_start_state",
    "has_valid_root_pitch_class",
    "has_valid_outer_interval",
    "has_valid_adjacent_intervals",
    "has_valid_beat_index",
    "has_strict_voice_order",
    "is_goal_state",
    "is_in_pitch_range",
    "is_parallel_perfect_outer_motion",
    "is_terminal_beat",
    "is_terminal_configuration",
    "is_valid_state",
    "is_valid_step_delta_action",
    "outer_interval",
    "pitch_class",
    "primitive_transition",
    "propose_primitive_action",
    "reward_context",
    "step_delta_action_space",
    "step_delta_to_action_index",
    "transition_reward",
    "transition_terminated",
    "transition_truncated",
    "valid_outgoing_transitions",
    "voice_motion",
]
