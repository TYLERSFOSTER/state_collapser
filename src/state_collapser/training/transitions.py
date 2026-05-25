"""Transition surface for training-facing code."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from state_collapser.tower.snapshot import LiveRuntimeView

from .fibers import FiberDeparture, FiberStageContext
from .inputs import ActionSelectionInput, tower_position_key


@dataclass(frozen=True, slots=True)
class RuntimeSnapshotSummary:
    """Small structural summary extracted from a runtime snapshot."""

    current_base_state: object | None
    tower_depth: int
    tower_position_key: tuple[object | None, ...]
    active_control_tier: int | None
    last_control_action: str | None


def summarize_runtime_snapshot(snapshot: LiveRuntimeView) -> RuntimeSnapshotSummary:
    """Build the canonical structural summary for one runtime snapshot."""

    return RuntimeSnapshotSummary(
        current_base_state=snapshot.current_base_state,
        tower_depth=len(snapshot.current_position_at_every_tier),
        tower_position_key=tower_position_key(snapshot),
        active_control_tier=snapshot.active_control_tier,
        last_control_action=snapshot.last_control_action,
    )


@dataclass(frozen=True, slots=True)
class TrainingTransition:
    """Typed package-facing transition handoff object."""

    source_input: ActionSelectionInput
    chosen_action: object
    reward: float
    target_input: ActionSelectionInput
    terminated: bool
    truncated: bool
    bootstrap_allowed: bool
    diagnostics: Mapping[str, object] = field(default_factory=dict)
    bootstrap_input: ActionSelectionInput | None = None
    bootstrap_reason: str = "unspecified"
    runtime_snapshot_summary: RuntimeSnapshotSummary | None = None
    tower_position_key: tuple[object | None, ...] | None = None
    active_tier: int | None = None
    frozen_context_version: int | str | None = None
    stage_context: FiberStageContext | None = None
    projected_coarse_step: object | None = None
    fiber_departure: FiberDeparture | None = None


__all__ = [
    "RuntimeSnapshotSummary",
    "TrainingTransition",
    "summarize_runtime_snapshot",
]
