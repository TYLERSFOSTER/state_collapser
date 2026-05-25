"""Internal-edge aggregation surface for partition towers."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum


class InternalAggregationName(StrEnum):
    """Supported internal/pre-image aggregation modes."""

    SUM = "sum"
    MEAN = "mean"
    MAX = "max"


@dataclass(frozen=True, slots=True)
class InternalAggregationResult:
    """Result of aggregating internal-edge numeric values."""

    name: InternalAggregationName
    value: float | None
    count: int


@dataclass(frozen=True, slots=True)
class InternalEdgeAggregator:
    """Configuration for internal-edge aggregation."""

    name: InternalAggregationName = InternalAggregationName.SUM

    @classmethod
    def sum(cls) -> InternalEdgeAggregator:
        return cls(InternalAggregationName.SUM)

    @classmethod
    def mean(cls) -> InternalEdgeAggregator:
        return cls(InternalAggregationName.MEAN)

    @classmethod
    def max(cls) -> InternalEdgeAggregator:
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
