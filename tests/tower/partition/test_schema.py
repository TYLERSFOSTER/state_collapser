"""Tests for contraction schemas."""

from __future__ import annotations

import pytest

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.base_registry import BaseGraphRegistry
from state_collapser.tower.partition.ids import SchemaBlockId
from state_collapser.tower.partition.schema import (
    DimensionwiseSchema,
    DiscoveryOrderChunkSchema,
    LabelBlockSchema,
    NoContractionSchema,
    SchemaAssignmentStore,
    SeededRandomRateSchema,
)


def make_edge(
    name: str,
    *,
    edge_labels: tuple[object, ...] = (),
    action_labels: tuple[object, ...] = (),
) -> BaseEdge:
    source = State(payload=("source", name), identity=("source", name))
    target = State(payload=("target", name), identity=("target", name))
    action = PrimitiveAction(
        payload=("action", name),
        identity=("action", name),
        labels=action_labels,
    )
    return BaseEdge(source=source, action=action, target=target, labels=edge_labels)


def test_no_contraction_schema_schedules_nothing() -> None:
    registry = BaseGraphRegistry()
    edge_id = registry.register_edge(make_edge("a", edge_labels=("x",)))
    store = SchemaAssignmentStore(NoContractionSchema())

    assignment = store.assign_edge(edge_id, registry)

    assert assignment.block_id is None
    assert store.ordered_blocks() == ()
    assert tuple(store.unscheduled_edge_ids) == (edge_id,)


def test_label_schema_assigns_first_matching_declared_block() -> None:
    registry = BaseGraphRegistry()
    edge_id = registry.register_edge(make_edge("a", edge_labels=("y",), action_labels=("x",)))
    schema = LabelBlockSchema.from_labels(("x", "y"))

    assert schema.assign_edge(edge_id, registry) == SchemaBlockId("x")
    assert schema.ordered_blocks() == (SchemaBlockId("x"), SchemaBlockId("y"))


def test_label_schema_supports_ordered_mapping() -> None:
    registry = BaseGraphRegistry()
    edge_id = registry.register_edge(make_edge("a", edge_labels=("voice:bass",)))
    schema = LabelBlockSchema.from_mapping({"voice:bass": "bass-block"})

    assert schema.assign_edge(edge_id, registry) == SchemaBlockId("bass-block")


def test_dimensionwise_schema_preserves_declared_order() -> None:
    registry = BaseGraphRegistry()
    x_edge = registry.register_edge(make_edge("x", action_labels=("x",)))
    z_edge = registry.register_edge(make_edge("z", action_labels=("z",)))
    schema = DimensionwiseSchema(("x", "y", "z"))

    assert schema.ordered_blocks() == (
        SchemaBlockId("x"),
        SchemaBlockId("y"),
        SchemaBlockId("z"),
    )
    assert schema.assign_edge(x_edge, registry) == SchemaBlockId("x")
    assert schema.assign_edge(z_edge, registry) == SchemaBlockId("z")


def test_assignment_store_persists_old_assignments() -> None:
    registry = BaseGraphRegistry()
    edge_id = registry.register_edge(make_edge("a", action_labels=("x",)))
    store = SchemaAssignmentStore(DimensionwiseSchema(("x",)))

    first = store.assign_edge(edge_id, registry)
    second = store.assign_edge(edge_id, registry)

    assert second == first
    assert store.edges_in_block(SchemaBlockId("x")) == (edge_id,)


def test_seeded_random_schema_is_stable_for_existing_assignments() -> None:
    registry = BaseGraphRegistry()
    first = registry.register_edge(make_edge("a"))
    store = SchemaAssignmentStore(SeededRandomRateSchema(seed=7, block_count=4))
    first_assignment = store.assign_edge(first, registry)

    registry.register_edge(make_edge("b"))
    second_first_assignment = store.assign_edge(first, registry)

    assert second_first_assignment == first_assignment


def test_seeded_random_schema_repeats_for_same_seed_and_discovery_order() -> None:
    left_registry = BaseGraphRegistry()
    right_registry = BaseGraphRegistry()
    left_edge = left_registry.register_edge(make_edge("a"))
    right_edge = right_registry.register_edge(make_edge("a"))
    left_store = SchemaAssignmentStore(SeededRandomRateSchema(seed=11, block_count=5))
    right_store = SchemaAssignmentStore(SeededRandomRateSchema(seed=11, block_count=5))

    assert left_store.assign_edge(left_edge, left_registry).block_id == right_store.assign_edge(
        right_edge,
        right_registry,
    ).block_id


def test_discovery_order_chunk_schema_assigns_expected_blocks() -> None:
    registry = BaseGraphRegistry()
    edge_ids = tuple(registry.register_edge(make_edge(str(index))) for index in range(5))
    schema = DiscoveryOrderChunkSchema(chunk_size=2)

    assert schema.assign_edge(edge_ids[0], registry) == SchemaBlockId(("chunk", 0))
    assert schema.assign_edge(edge_ids[1], registry) == SchemaBlockId(("chunk", 0))
    assert schema.assign_edge(edge_ids[2], registry) == SchemaBlockId(("chunk", 1))
    assert schema.assign_edge(edge_ids[4], registry) == SchemaBlockId(("chunk", 2))


def test_schema_config_rejects_invalid_sizes() -> None:
    with pytest.raises(ValueError):
        SeededRandomRateSchema(seed=1, block_count=0)

    with pytest.raises(ValueError):
        DiscoveryOrderChunkSchema(chunk_size=0)
