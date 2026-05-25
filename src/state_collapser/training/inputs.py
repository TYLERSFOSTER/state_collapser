"""Decision-input surface for training-facing code."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from state_collapser.tower.snapshot import LiveRuntimeView

from .fibers import FiberDeparture, FiberStageContext


def tower_position_key(snapshot: LiveRuntimeView) -> tuple[object | None, ...]:
    """Return the canonical tower-position tuple for one runtime snapshot."""

    return tuple(snapshot.current_position_at_every_tier)


@dataclass(frozen=True, slots=True)
class ActionSelectionInput:
    """Typed package-facing input object for action selection."""

    observation: object
    current_base_state: object | None
    runtime_snapshot: LiveRuntimeView
    tower_position_key: tuple[object | None, ...]
    action_mask: tuple[bool, ...] | None = None
    history_window: tuple[object, ...] = ()
    active_tier_state: object | None = None
    frozen_lower_context: object | None = None
    stage_context: FiberStageContext | None = None
    fiber_departure: FiberDeparture | None = None
    diagnostics: Mapping[str, object] = field(default_factory=dict)


def build_action_selection_input(
    *,
    observation: object,
    runtime_snapshot: LiveRuntimeView,
    action_mask: tuple[bool, ...] | None = None,
    history_window: tuple[object, ...] = (),
    active_tier_state: object | None = None,
    frozen_lower_context: object | None = None,
    stage_context: FiberStageContext | None = None,
    fiber_departure: FiberDeparture | None = None,
    diagnostics: Mapping[str, object] | None = None,
) -> ActionSelectionInput:
    """Build the canonical action-selection input from one runtime snapshot."""

    resolved_active_tier_state = active_tier_state
    if resolved_active_tier_state is None:
        active_tier = runtime_snapshot.active_control_tier
        if active_tier is not None and 0 <= active_tier < len(
            runtime_snapshot.current_position_at_every_tier
        ):
            resolved_active_tier_state = runtime_snapshot.current_position_at_every_tier[
                active_tier
            ]

    return ActionSelectionInput(
        observation=observation,
        current_base_state=runtime_snapshot.current_base_state,
        runtime_snapshot=runtime_snapshot,
        tower_position_key=tower_position_key(runtime_snapshot),
        action_mask=action_mask,
        history_window=history_window,
        active_tier_state=resolved_active_tier_state,
        frozen_lower_context=frozen_lower_context,
        stage_context=stage_context,
        fiber_departure=fiber_departure,
        diagnostics={} if diagnostics is None else diagnostics,
    )


__all__ = [
    "ActionSelectionInput",
    "build_action_selection_input",
    "tower_position_key",
]
