"""Direct fiber-conditioned stage surface."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Protocol

from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.ids import ActionCellId
from state_collapser.tower.partition.tower import PartitionTower
from state_collapser.tower.snapshot import LiveRuntimeView

from .continuation import (
    BootstrapSemantics,
    default_bootstrap_allowed,
    default_bootstrap_reason,
)
from .decisions import ActionDecision
from .fibers import (
    FiberDeparture,
    FiberDepartureReason,
    FiberStageContext,
    PathFiber,
)
from .frozen import FrozenQuotientBehavior
from .inputs import ActionSelectionInput, build_action_selection_input
from .transitions import TrainingTransition, summarize_runtime_snapshot


class StageRuntimeResetLike(Protocol):
    """Reset result surface consumed by `FiberConditionedStage`."""

    observation: object
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


class StageRuntimeStepLike(Protocol):
    """Step result surface consumed by `FiberConditionedStage`."""

    observation: object
    reward: float
    terminated: bool
    truncated: bool
    info: dict[str, object]
    runtime_snapshot: LiveRuntimeView


class StageRuntimeLike(Protocol):
    """Runtime surface consumed by `FiberConditionedStage`."""

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, object] | None = None,
    ) -> StageRuntimeResetLike:
        """Reset the stage runtime and return reset/snapshot data."""
        ...

    def step(self, action: object) -> StageRuntimeStepLike:
        """Advance one action and return step/snapshot data."""
        ...


@dataclass(frozen=True, slots=True)
class FiberStageStepResult:
    """Narrow structured result for one fiber-conditioned stage step."""

    transition: TrainingTransition
    next_input: ActionSelectionInput
    action_cell: ActionCellId | None
    realized_edge: BaseEdge | None = None
    departure: FiberDeparture | None = None


@dataclass(slots=True)
class FiberConditionedStage:
    """Package-native stage conditioned on frozen quotient behavior."""

    stage_id: str
    runtime: StageRuntimeLike
    tower: PartitionTower
    fine_tier: int
    coarse_tier: int
    frozen_behavior: FrozenQuotientBehavior
    path_fiber: PathFiber
    action_resolver: Callable[[BaseEdge], object] | None = None
    bootstrap_semantics: BootstrapSemantics = field(default_factory=BootstrapSemantics)
    metadata: Mapping[str, object] = field(default_factory=dict)
    _current_input: ActionSelectionInput | None = field(default=None, init=False, repr=False)
    _action_vocabulary: tuple[ActionCellId, ...] = field(default=(), init=False, repr=False)

    def __post_init__(self) -> None:
        """Validate stage/fiber/frozen-behavior alignment and copy metadata."""

        if self.coarse_tier != self.fine_tier + 1:
            raise ValueError("FiberConditionedStage requires coarse_tier == fine_tier + 1.")
        if self.path_fiber.tower is not self.tower:
            raise ValueError("FiberConditionedStage path_fiber must reference the same tower.")
        if self.path_fiber.fine_tier != self.fine_tier:
            raise ValueError("FiberConditionedStage fine_tier must match its path_fiber.")
        if self.path_fiber.coarse_tier != self.coarse_tier:
            raise ValueError("FiberConditionedStage coarse_tier must match its path_fiber.")
        if self.path_fiber.frozen_behavior != self.frozen_behavior:
            raise ValueError("FiberConditionedStage frozen behavior must match its path_fiber.")
        self.metadata = dict(self.metadata)

    @property
    def stage_context(self) -> FiberStageContext:
        """Return the current immutable context descriptor for this stage."""

        return self.path_fiber.stage_context(self.stage_id)

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, object] | None = None,
        reset_result: StageRuntimeResetLike | None = None,
    ) -> ActionSelectionInput:
        """Reset or bind the underlying runtime and return the first stage input."""

        result = (
            self.runtime.reset(seed=seed, options=options)
            if reset_result is None
            else reset_result
        )
        current_input = self._build_input(
            observation=result.observation,
            runtime_snapshot=result.runtime_snapshot,
            diagnostics=result.info,
        )
        self._current_input = current_input
        return current_input

    def current_input(self) -> ActionSelectionInput:
        """Return the current stage input without advancing the runtime."""

        if self._current_input is None:
            raise ValueError("FiberConditionedStage.current_input() requires reset first.")
        snapshot = self._current_input.runtime_snapshot
        current_input = self._build_input(
            observation=self._current_input.observation,
            runtime_snapshot=snapshot,
            diagnostics=self._current_input.diagnostics,
        )
        self._current_input = current_input
        return current_input

    def step(self, decision: ActionDecision) -> TrainingTransition:
        """Resolve and step one fiber-admissible action decision."""

        source_input = self.current_input()
        action_cell, departure = self._resolve_decision(decision)
        if departure is not None or action_cell is None:
            transition = self._diagnostic_transition(
                source_input=source_input,
                chosen_action=decision.chosen_action,
                departure=departure
                or FiberDeparture(
                    reason=FiberDepartureReason.UNSPECIFIED,
                    stage_context=self.stage_context,
                    attempted=decision.chosen_action,
                ),
            )
            self._current_input = transition.target_input
            return transition

        lift_candidates = self.path_fiber.lift_candidates(
            self._current_total_state(source_input),
            action_cell,
        )
        if not lift_candidates:
            transition = self._diagnostic_transition(
                source_input=source_input,
                chosen_action=decision.chosen_action,
                departure=FiberDeparture(
                    reason=FiberDepartureReason.NO_LIFT_CANDIDATE,
                    stage_context=self.stage_context,
                    expected=action_cell,
                    attempted=decision.chosen_action,
                ),
            )
            self._current_input = transition.target_input
            return transition

        realized_edge = lift_candidates[0]
        runtime_action = (
            realized_edge.action
            if self.action_resolver is None
            else self.action_resolver(realized_edge)
        )
        step_result = self.runtime.step(runtime_action)
        next_input = self._build_input(
            observation=step_result.observation,
            runtime_snapshot=step_result.runtime_snapshot,
            diagnostics=step_result.info,
        )
        transition_diagnostics: dict[str, object] = dict(step_result.info)
        transition_diagnostics.update(decision.diagnostics)
        transition_diagnostics["fiber_action_cell"] = action_cell
        transition_diagnostics["realized_edge"] = realized_edge
        bootstrap_allowed = default_bootstrap_allowed(
            terminated=step_result.terminated,
            truncated=step_result.truncated,
            semantics=self.bootstrap_semantics,
        )
        transition = TrainingTransition(
            source_input=source_input,
            chosen_action=decision.chosen_action,
            reward=step_result.reward,
            target_input=next_input,
            terminated=step_result.terminated,
            truncated=step_result.truncated,
            bootstrap_allowed=bootstrap_allowed,
            diagnostics=transition_diagnostics,
            bootstrap_input=next_input,
            bootstrap_reason=default_bootstrap_reason(
                terminated=step_result.terminated,
                truncated=step_result.truncated,
                semantics=self.bootstrap_semantics,
            ),
            runtime_snapshot_summary=summarize_runtime_snapshot(step_result.runtime_snapshot),
            tower_position_key=next_input.tower_position_key,
            active_tier=step_result.runtime_snapshot.active_control_tier,
            stage_context=self.stage_context,
            projected_coarse_step=self.frozen_behavior.current_step,
        )
        self._current_input = next_input
        return transition

    def _build_input(
        self,
        *,
        observation: object,
        runtime_snapshot: LiveRuntimeView,
        diagnostics: Mapping[str, object],
        fiber_departure: FiberDeparture | None = None,
    ) -> ActionSelectionInput:
        current_state = runtime_snapshot.current_base_state
        action_vocabulary: tuple[ActionCellId, ...] = ()
        action_mask: tuple[bool, ...] | None = None
        if isinstance(current_state, State):
            action_vocabulary = self.path_fiber.action_vocabulary(current_state)
            action_mask = self.path_fiber.action_mask(
                current_state,
                action_vocabulary=action_vocabulary,
            )
        self._action_vocabulary = action_vocabulary
        merged_diagnostics: dict[str, object] = dict(diagnostics)
        merged_diagnostics["fiber_action_vocabulary"] = action_vocabulary
        return build_action_selection_input(
            observation=observation,
            runtime_snapshot=runtime_snapshot,
            action_mask=action_mask,
            diagnostics=merged_diagnostics,
            stage_context=self.stage_context,
            fiber_departure=fiber_departure,
        )

    def _resolve_decision(
        self,
        decision: ActionDecision,
    ) -> tuple[ActionCellId | None, FiberDeparture | None]:
        chosen_action = decision.chosen_action
        if isinstance(chosen_action, int):
            if chosen_action < 0 or chosen_action >= len(self._action_vocabulary):
                return None, FiberDeparture(
                    reason=FiberDepartureReason.ILLEGAL_ACTION_INDEX,
                    stage_context=self.stage_context,
                    expected=tuple(range(len(self._action_vocabulary))),
                    attempted=chosen_action,
                )
            action_cell = self._action_vocabulary[chosen_action]
        elif isinstance(chosen_action, ActionCellId):
            action_cell = chosen_action
        else:
            return None, FiberDeparture(
                reason=FiberDepartureReason.UNKNOWN_ACTION_CELL,
                stage_context=self.stage_context,
                expected=self._action_vocabulary,
                attempted=chosen_action,
            )

        current_state = self._current_total_state(self.current_input())
        departure = self.path_fiber.diagnose_departure(
            current_state,
            action_cell,
            stage_context=self.stage_context,
        )
        return action_cell, departure

    def _diagnostic_transition(
        self,
        *,
        source_input: ActionSelectionInput,
        chosen_action: object,
        departure: FiberDeparture,
    ) -> TrainingTransition:
        target_input = self._build_input(
            observation=source_input.observation,
            runtime_snapshot=source_input.runtime_snapshot,
            diagnostics=source_input.diagnostics,
            fiber_departure=departure,
        )
        return TrainingTransition(
            source_input=source_input,
            chosen_action=chosen_action,
            reward=0.0,
            target_input=target_input,
            terminated=False,
            truncated=False,
            bootstrap_allowed=False,
            diagnostics={
                "fiber_departure_reason": departure.reason.value,
                "fiber_departure": departure,
            },
            bootstrap_input=target_input,
            bootstrap_reason="fiber_departure",
            runtime_snapshot_summary=summarize_runtime_snapshot(
                source_input.runtime_snapshot
            ),
            tower_position_key=source_input.tower_position_key,
            active_tier=source_input.runtime_snapshot.active_control_tier,
            stage_context=self.stage_context,
            projected_coarse_step=self.frozen_behavior.current_step,
            fiber_departure=departure,
        )

    def _current_total_state(self, action_input: ActionSelectionInput) -> State:
        current_state = action_input.runtime_snapshot.current_base_state
        if not isinstance(current_state, State):
            raise ValueError("FiberConditionedStage requires core State current states.")
        return current_state


__all__ = [
    "FiberConditionedStage",
    "FiberStageStepResult",
    "StageRuntimeLike",
    "StageRuntimeResetLike",
    "StageRuntimeStepLike",
]
