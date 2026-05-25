"""Path-fiber surfaces for fiber-conditioned training."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum

from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.ids import ActionCellId, StateCellId
from state_collapser.tower.partition.tower import PartitionTower

from .frozen import FrozenQuotientBehavior, FrozenQuotientStep


@dataclass(frozen=True, slots=True)
class FiberStageContext:
    """Stable metadata identifying one fiber-conditioned training stage."""

    stage_id: str
    fiber_id: str
    fine_tier: int
    coarse_tier: int
    frozen_behavior_id: str
    frozen_behavior_version: int | str

    def __post_init__(self) -> None:
        if self.coarse_tier != self.fine_tier + 1:
            raise ValueError(
                "FiberStageContext first-scope use requires "
                "coarse_tier == fine_tier + 1."
            )


class FiberDepartureReason(StrEnum):
    """Stable diagnostic reasons for leaving or failing to enter a path fiber."""

    ACTION_NOT_IN_FIBER = "ACTION_NOT_IN_FIBER"
    PROJECTED_TARGET_MISMATCH = "PROJECTED_TARGET_MISMATCH"
    NO_LIFT_CANDIDATE = "NO_LIFT_CANDIDATE"
    STALE_TOWER_CONTEXT = "STALE_TOWER_CONTEXT"
    UNKNOWN_STATE_CELL = "UNKNOWN_STATE_CELL"
    UNKNOWN_ACTION_CELL = "UNKNOWN_ACTION_CELL"
    ILLEGAL_ACTION_INDEX = "ILLEGAL_ACTION_INDEX"
    UNSPECIFIED = "UNSPECIFIED"


@dataclass(frozen=True, slots=True)
class FiberDeparture:
    """Diagnostic payload for an attempted action outside the active path fiber."""

    reason: FiberDepartureReason
    stage_context: FiberStageContext | None = None
    expected: object | None = None
    actual: object | None = None
    attempted: object | None = None
    diagnostics: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "diagnostics", dict(self.diagnostics))


@dataclass(frozen=True, slots=True)
class FiberStateCells:
    """Fine/coarse state-cell pair for one total state."""

    total_state: State
    fine_state_cell: StateCellId
    coarse_state_cell: StateCellId


@dataclass(frozen=True, slots=True)
class PathFiber:
    """Path fiber over a frozen adjacent coarse-tier behavior."""

    fiber_id: str
    tower: PartitionTower
    fine_tier: int
    coarse_tier: int
    frozen_behavior: FrozenQuotientBehavior
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.coarse_tier != self.fine_tier + 1:
            raise ValueError("PathFiber requires coarse_tier == fine_tier + 1.")
        if self.frozen_behavior.coarse_tier != self.coarse_tier:
            raise ValueError("PathFiber coarse_tier must match the frozen behavior.")
        if self.frozen_behavior.supported_fine_tier != self.fine_tier:
            raise ValueError("PathFiber fine_tier must match the frozen behavior.")
        object.__setattr__(self, "metadata", dict(self.metadata))

    def stage_context(self, stage_id: str) -> FiberStageContext:
        """Build a stage context for this fiber and a caller-owned stage id."""

        return FiberStageContext(
            stage_id=stage_id,
            fiber_id=self.fiber_id,
            fine_tier=self.fine_tier,
            coarse_tier=self.coarse_tier,
            frozen_behavior_id=self.frozen_behavior.behavior_id,
            frozen_behavior_version=self.frozen_behavior.version,
        )

    def resolve_state_cells(
        self,
        total_state: State,
        *,
        stage_context: FiberStageContext | None = None,
    ) -> FiberStateCells | FiberDeparture:
        """Resolve fine and coarse state cells for a total state."""

        fine_state_cell = self.tower.current_state_cell(self.fine_tier, total_state)
        coarse_state_cell = self.tower.current_state_cell(self.coarse_tier, total_state)
        if fine_state_cell is None or coarse_state_cell is None:
            return FiberDeparture(
                reason=FiberDepartureReason.UNKNOWN_STATE_CELL,
                stage_context=stage_context,
                expected={"fine_tier": self.fine_tier, "coarse_tier": self.coarse_tier},
                actual={
                    "fine_state_cell": fine_state_cell,
                    "coarse_state_cell": coarse_state_cell,
                },
                attempted=total_state,
            )
        return FiberStateCells(
            total_state=total_state,
            fine_state_cell=fine_state_cell,
            coarse_state_cell=coarse_state_cell,
        )

    def current_fine_state_cell(self, total_state: State) -> StateCellId | None:
        """Return the fine state cell containing a total state."""

        return self.tower.current_state_cell(self.fine_tier, total_state)

    def current_coarse_state_cell(self, total_state: State) -> StateCellId | None:
        """Return the coarse state cell containing a total state."""

        return self.tower.current_state_cell(self.coarse_tier, total_state)

    def action_vocabulary(self, total_state: State) -> tuple[ActionCellId, ...]:
        """Return the finite fine-stage action vocabulary at the current state."""

        fine_state_cell = self.current_fine_state_cell(total_state)
        if fine_state_cell is None:
            return ()
        return self.tower.outgoing_action_cells(self.fine_tier, fine_state_cell)

    def admissible_action_cells(self, total_state: State) -> tuple[ActionCellId, ...]:
        """Return fine action cells compatible with the frozen coarse step."""

        frozen_step = self.frozen_behavior.current_step
        if frozen_step is None:
            return ()
        state_cells = self.resolve_state_cells(total_state)
        if isinstance(state_cells, FiberDeparture):
            return ()
        if state_cells.coarse_state_cell != frozen_step.source_cell:
            return ()

        admissible: list[ActionCellId] = []
        for fine_action_cell in self.action_vocabulary(total_state):
            if any(
                self._edge_matches_frozen_step(edge, frozen_step)
                for edge in self.tower.action_cell_members(self.fine_tier, fine_action_cell)
            ):
                admissible.append(fine_action_cell)
        return tuple(admissible)

    def action_mask(
        self,
        total_state: State,
        *,
        action_vocabulary: Sequence[ActionCellId] | None = None,
    ) -> tuple[bool, ...] | None:
        """Return a mask over a finite fine-stage action vocabulary."""

        vocabulary = (
            tuple(action_vocabulary)
            if action_vocabulary is not None
            else self.action_vocabulary(total_state)
        )
        if not vocabulary and self.current_fine_state_cell(total_state) is None:
            return None
        admissible = set(self.admissible_action_cells(total_state))
        return tuple(action_cell in admissible for action_cell in vocabulary)

    def lift_candidates(
        self,
        total_state: State,
        action_cell: ActionCellId,
    ) -> tuple[BaseEdge, ...]:
        """Return deterministic primitive representatives for a fiber action cell."""

        if action_cell not in set(self.admissible_action_cells(total_state)):
            return ()
        return self.tower.lift_candidates(self.fine_tier, action_cell, total_state)

    def diagnose_departure(
        self,
        total_state: State,
        action_cell: ActionCellId,
        *,
        stage_context: FiberStageContext | None = None,
    ) -> FiberDeparture | None:
        """Diagnose why an action cell is not currently fiber-admissible."""

        state_cells = self.resolve_state_cells(total_state, stage_context=stage_context)
        if isinstance(state_cells, FiberDeparture):
            return state_cells

        vocabulary = self.action_vocabulary(total_state)
        if action_cell not in vocabulary:
            return FiberDeparture(
                reason=FiberDepartureReason.UNKNOWN_ACTION_CELL,
                stage_context=stage_context,
                expected=vocabulary,
                attempted=action_cell,
            )

        admissible = self.admissible_action_cells(total_state)
        if action_cell not in admissible:
            reason = self._departure_reason_for_known_action_cell(action_cell)
            return FiberDeparture(
                reason=reason,
                stage_context=stage_context,
                expected=self.frozen_behavior.current_step,
                actual=tuple(
                    self._project_edge_to_coarse_step(edge)
                    for edge in self.tower.action_cell_members(self.fine_tier, action_cell)
                ),
                attempted=action_cell,
            )

        if not self.lift_candidates(total_state, action_cell):
            return FiberDeparture(
                reason=FiberDepartureReason.NO_LIFT_CANDIDATE,
                stage_context=stage_context,
                expected=admissible,
                attempted=action_cell,
            )

        return None

    def _edge_matches_frozen_step(
        self,
        edge: BaseEdge,
        frozen_step: FrozenQuotientStep,
    ) -> bool:
        projected = self._project_edge_to_coarse_step(edge)
        if projected is None:
            return False
        if projected.source_cell != frozen_step.source_cell:
            return False
        if frozen_step.action_cell is not None and projected.action_cell != frozen_step.action_cell:
            return False
        return not (
            frozen_step.target_cell is not None
            and projected.target_cell != frozen_step.target_cell
        )

    def _departure_reason_for_known_action_cell(
        self,
        action_cell: ActionCellId,
    ) -> FiberDepartureReason:
        frozen_step = self.frozen_behavior.current_step
        if frozen_step is None:
            return FiberDepartureReason.ACTION_NOT_IN_FIBER
        projected_steps = tuple(
            self._project_edge_to_coarse_step(edge)
            for edge in self.tower.action_cell_members(self.fine_tier, action_cell)
        )
        if (
            frozen_step.target_cell is not None
            and projected_steps
            and all(
                projected_step is None or projected_step.target_cell != frozen_step.target_cell
                for projected_step in projected_steps
            )
        ):
            return FiberDepartureReason.PROJECTED_TARGET_MISMATCH
        return FiberDepartureReason.ACTION_NOT_IN_FIBER

    def _project_edge_to_coarse_step(
        self,
        edge: BaseEdge,
    ) -> FrozenQuotientStep | None:
        source_cell = self.tower.current_state_cell(self.coarse_tier, edge.source)
        target_cell = self.tower.current_state_cell(self.coarse_tier, edge.target)
        action_cell = self.tower.action_cell_for_edge(self.coarse_tier, edge)
        if source_cell is None or target_cell is None:
            return None
        return FrozenQuotientStep(
            coarse_tier=self.coarse_tier,
            source_cell=source_cell,
            action_cell=action_cell,
            target_cell=target_cell,
        )


__all__ = [
    "FiberDeparture",
    "FiberDepartureReason",
    "FiberStageContext",
    "PathFiber",
]
