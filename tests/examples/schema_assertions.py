"""Shared assertions for schema-enabled example runtime tests."""

from __future__ import annotations

from typing import Any

from state_collapser.tower.snapshot import LiveRuntimeView


def _last_tower_update_result(runtime: object) -> Any | None:
    """Return the latest partition update result exposed by an example runtime."""

    tower_runtime = getattr(runtime, "tower_runtime", None)
    if tower_runtime is None:
        return None
    return getattr(tower_runtime, "last_tower_update_result", None)


def latest_schema_assignment_count(runtime: object) -> int:
    """Return the number of schema assignments in the latest tower update."""

    result = _last_tower_update_result(runtime)
    if result is None:
        return 0
    return len(getattr(result, "schema_assignments", ()))


def scheduled_assignment_count(runtime: object) -> int:
    """Return the number of scheduled schema assignments in the latest update."""

    result = _last_tower_update_result(runtime)
    if result is None:
        return 0
    return sum(
        1
        for assignment in getattr(result, "schema_assignments", ())
        if getattr(assignment, "block_id", None) is not None
    )


def snapshot_has_nontrivial_tower(snapshot: LiveRuntimeView) -> bool:
    """Return whether a snapshot exposes at least one non-base tier position."""

    return len(snapshot.current_position_at_every_tier) >= 2


def assert_runtime_scheduled_schema_assignments(runtime: object) -> None:
    """Assert that the latest runtime update scheduled at least one edge."""

    assert scheduled_assignment_count(runtime) > 0


def assert_snapshot_has_nontrivial_tower(snapshot: LiveRuntimeView) -> None:
    """Assert that a snapshot exposes a nontrivial tower position list."""

    assert snapshot_has_nontrivial_tower(snapshot)
