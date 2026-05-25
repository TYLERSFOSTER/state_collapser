"""Tests for internal-edge aggregation surfaces."""

from __future__ import annotations

from state_collapser.tower.partition import (
    InternalAggregationName,
    InternalEdgeAggregator,
    PartitionTower,
    aggregate_internal_values,
)


def test_internal_aggregation_supports_sum_mean_and_max() -> None:
    values = (1.0, 2.0, 5.0)

    assert aggregate_internal_values(values, InternalEdgeAggregator.sum()).value == 8.0
    assert aggregate_internal_values(values, InternalEdgeAggregator.mean()).value == 8.0 / 3.0
    assert aggregate_internal_values(values, InternalEdgeAggregator.max()).value == 5.0


def test_internal_aggregation_empty_values_are_explicit() -> None:
    assert aggregate_internal_values((), InternalEdgeAggregator.sum()).value == 0.0
    assert aggregate_internal_values((), InternalEdgeAggregator.mean()).value is None
    assert aggregate_internal_values((), InternalEdgeAggregator.max()).value is None


def test_partition_tower_retains_internal_edge_aggregator_config() -> None:
    tower = PartitionTower(internal_edge_aggregator=InternalEdgeAggregator.max())

    assert tower.internal_edge_aggregator.name is InternalAggregationName.MAX


def test_partition_tower_diagnostics_expose_internal_aggregator_name() -> None:
    tower = PartitionTower(internal_edge_aggregator=InternalEdgeAggregator.max())
    result = tower.initialize(initial_states=(), initial_edges=(), current_state=None)

    assert result.diagnostics.internal_aggregation_name == "max"
