"""Diagnostics for partition-tower updates."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TowerUpdateDiagnostics:
    """Counters describing one partition-tower update.

    Diagnostics are intentionally simple manifest-friendly counters. They are
    meant to support benchmarks and sanity checks without exposing mutable tower
    internals as part of the public API.
    """

    discovered_state_count: int = 0
    discovered_edge_count: int = 0
    delta_state_count: int = 0
    delta_edge_count: int = 0
    schema_assignment_count: int = 0
    state_cell_merge_count: int = 0
    action_collection_merge_count: int = 0
    internal_edge_count: int = 0
    dirty_collection_count: int = 0
    compat_readout_rebuild_count: int = 0
    full_rebuild_validation_count: int = 0
    internal_aggregation_name: str = "sum"


__all__ = ["TowerUpdateDiagnostics"]
