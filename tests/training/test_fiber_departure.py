"""Tests for path-fiber departure diagnostics."""

from __future__ import annotations

from state_collapser.training import (
    FiberDeparture,
    FiberDepartureReason,
    FiberStageContext,
)


def test_fiber_departure_reasons_are_stable_and_readable() -> None:
    assert FiberDepartureReason.ACTION_NOT_IN_FIBER.value == "ACTION_NOT_IN_FIBER"
    assert FiberDepartureReason.PROJECTED_TARGET_MISMATCH.value == (
        "PROJECTED_TARGET_MISMATCH"
    )
    assert FiberDepartureReason.NO_LIFT_CANDIDATE.value == "NO_LIFT_CANDIDATE"
    assert FiberDepartureReason.STALE_TOWER_CONTEXT.value == "STALE_TOWER_CONTEXT"
    assert FiberDepartureReason.UNKNOWN_STATE_CELL.value == "UNKNOWN_STATE_CELL"
    assert FiberDepartureReason.UNKNOWN_ACTION_CELL.value == "UNKNOWN_ACTION_CELL"
    assert FiberDepartureReason.ILLEGAL_ACTION_INDEX.value == "ILLEGAL_ACTION_INDEX"
    assert FiberDepartureReason.UNSPECIFIED.value == "UNSPECIFIED"


def test_fiber_departure_defaults_diagnostics_safely() -> None:
    left = FiberDeparture(reason=FiberDepartureReason.UNSPECIFIED)
    right = FiberDeparture(reason=FiberDepartureReason.UNSPECIFIED)

    assert left.diagnostics == {}
    assert right.diagnostics == {}
    assert left.diagnostics is not right.diagnostics


def test_fiber_departure_preserves_payloads() -> None:
    context = FiberStageContext(
        stage_id="stage",
        fiber_id="fiber",
        fine_tier=0,
        coarse_tier=1,
        frozen_behavior_id="frozen",
        frozen_behavior_version="v1",
    )
    departure = FiberDeparture(
        reason=FiberDepartureReason.ACTION_NOT_IN_FIBER,
        stage_context=context,
        expected="expected",
        actual="actual",
        attempted="attempted",
        diagnostics={"why": "test"},
    )

    assert departure.stage_context == context
    assert departure.expected == "expected"
    assert departure.actual == "actual"
    assert departure.attempted == "attempted"
    assert departure.diagnostics == {"why": "test"}
