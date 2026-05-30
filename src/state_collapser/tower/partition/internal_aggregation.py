"""Internal-edge aggregation surface for partition towers.

Internal edges are base edges that became loops inside a coarsened state cell.
They are not exposed as ordinary outgoing actions, but callers may still want a
summary of their reward/value contribution for diagnostics or residual learning.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum


class InternalAggregationName(StrEnum):
    """Supported aggregation modes for internal-edge numeric values."""

    SUM = "sum"
    MEAN = "mean"
    MAX = "max"


@dataclass(frozen=True, slots=True)
class InternalAggregationResult:
    """Aggregated value and count for internal-edge numeric data."""

    name: InternalAggregationName
    value: float | None
    count: int


@dataclass(frozen=True, slots=True)
class InternalEdgeAggregator:
    """Configuration for summarizing values carried by internal edges."""

    name: InternalAggregationName = InternalAggregationName.SUM

    @classmethod
    def sum(cls) -> InternalEdgeAggregator:
        """Aggregate internal values by summation."""

        return cls(InternalAggregationName.SUM)

    @classmethod
    def mean(cls) -> InternalEdgeAggregator:
        """Aggregate internal values by arithmetic mean."""

        return cls(InternalAggregationName.MEAN)

    @classmethod
    def max(cls) -> InternalEdgeAggregator:
        """Aggregate internal values by maximum."""

        return cls(InternalAggregationName.MAX)


def aggregate_internal_values(
    values: Iterable[float],
    aggregator: InternalEdgeAggregator | None = None,
) -> InternalAggregationResult:
    """Aggregate internal-edge numeric values under the configured mode."""

    resolved = InternalEdgeAggregator.sum() if aggregator is None else aggregator
    value_tuple = tuple(float(value) for value in values)
    if resolved.name is InternalAggregationName.SUM:
        return InternalAggregationResult(
            name=resolved.name,
            value=sum(value_tuple),
            count=len(value_tuple),
        )
    if not value_tuple:
        return InternalAggregationResult(name=resolved.name, value=None, count=0)
    if resolved.name is InternalAggregationName.MEAN:
        return InternalAggregationResult(
            name=resolved.name,
            value=sum(value_tuple) / len(value_tuple),
            count=len(value_tuple),
        )
    if resolved.name is InternalAggregationName.MAX:
        return InternalAggregationResult(
            name=resolved.name,
            value=max(value_tuple),
            count=len(value_tuple),
        )
    raise ValueError(f"Unsupported internal aggregation mode: {resolved.name}")


__all__ = [
    "InternalAggregationName",
    "InternalAggregationResult",
    "InternalEdgeAggregator",
    "aggregate_internal_values",
]
