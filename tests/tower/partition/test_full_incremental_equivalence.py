"""Full-build versus incremental equivalence tests for partition towers."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.ids import StateCellId
from state_collapser.tower.partition.schema import (
    ContractionSchema,
    DimensionwiseSchema,
    DiscoveryOrderChunkSchema,
    LabelBlockSchema,
    NoContractionSchema,
)
from state_collapser.tower.partition.tower import PartitionTower


@dataclass(frozen=True, slots=True)
class DeltaBatch:
    states: tuple[State, ...]
    edges: tuple[BaseEdge, ...]


@dataclass(frozen=True, slots=True)
class EquivalenceFixture:
    states: tuple[State, ...]
    edges: tuple[BaseEdge, ...]
    batches: tuple[DeltaBatch, ...]
    schema: ContractionSchema
    current_state: State


def state(name: str) -> State:
    return State(payload=(name,), identity=name)


def edge(source: State, target: State, label: object = "x") -> BaseEdge:
    return BaseEdge(
        source=source,
        action=PrimitiveAction(
            payload=("move", label),
            identity=("move", label),
            labels=(label,),
        ),
        target=target,
    )


def unlabeled_edge(source: State, target: State, identity: object) -> BaseEdge:
    return BaseEdge(
        source=source,
        action=PrimitiveAction(payload=("move", identity), identity=("move", identity)),
        target=target,
    )


def test_two_state_one_edge_full_and_incremental_are_equivalent() -> None:
    start = state("start")
    goal = state("goal")
    first_edge = edge(start, goal, "x")
    fixture = EquivalenceFixture(
        states=(start, goal),
        edges=(first_edge,),
        batches=(DeltaBatch(states=(goal,), edges=(first_edge,)),),
        schema=DimensionwiseSchema(("x",)),
        current_state=goal,
    )

    assert_partition_towers_equivalent(fixture)


def test_three_state_path_full_and_incremental_are_equivalent() -> None:
    start = state("start")
    middle = state("middle")
    goal = state("goal")
    first_edge = edge(start, middle, "x")
    second_edge = edge(middle, goal, "x")
    fixture = EquivalenceFixture(
        states=(start, middle, goal),
        edges=(first_edge, second_edge),
        batches=(
            DeltaBatch(states=(middle,), edges=(first_edge,)),
            DeltaBatch(states=(goal,), edges=(second_edge,)),
        ),
        schema=DimensionwiseSchema(("x",)),
        current_state=goal,
    )

    assert_partition_towers_equivalent(fixture)


def test_square_dimension_labels_full_and_incremental_are_equivalent() -> None:
    origin = state("origin")
    east = state("east")
    north = state("north")
    northeast = state("northeast")
    east_edge = edge(origin, east, "x")
    north_edge = edge(origin, north, "y")
    east_to_northeast = edge(east, northeast, "y")
    north_to_northeast = edge(north, northeast, "x")
    fixture = EquivalenceFixture(
        states=(origin, east, north, northeast),
        edges=(east_edge, north_edge, east_to_northeast, north_to_northeast),
        batches=(
            DeltaBatch(states=(east,), edges=(east_edge,)),
            DeltaBatch(states=(north,), edges=(north_edge,)),
            DeltaBatch(states=(northeast,), edges=(east_to_northeast, north_to_northeast)),
        ),
        schema=DimensionwiseSchema(("x", "y")),
        current_state=northeast,
    )

    assert_partition_towers_equivalent(fixture)


def test_internal_edge_fixture_full_and_incremental_are_equivalent() -> None:
    start = state("start")
    middle = state("middle")
    goal = state("goal")
    contracted = edge(start, middle, "x")
    live = edge(start, goal, "z")
    fixture = EquivalenceFixture(
        states=(start, middle, goal),
        edges=(contracted, live),
        batches=(
            DeltaBatch(states=(middle,), edges=(contracted,)),
            DeltaBatch(states=(goal,), edges=(live,)),
        ),
        schema=DimensionwiseSchema(("x",)),
        current_state=start,
    )

    assert_partition_towers_equivalent(fixture)


def test_unlabeled_discovery_order_full_and_incremental_are_equivalent() -> None:
    start = state("start")
    first = state("first")
    second = state("second")
    first_edge = unlabeled_edge(start, first, "first")
    second_edge = unlabeled_edge(first, second, "second")
    fixture = EquivalenceFixture(
        states=(start, first, second),
        edges=(first_edge, second_edge),
        batches=(
            DeltaBatch(states=(first,), edges=(first_edge,)),
            DeltaBatch(states=(second,), edges=(second_edge,)),
        ),
        schema=DiscoveryOrderChunkSchema(chunk_size=1),
        current_state=second,
    )

    assert_partition_towers_equivalent(fixture)


def test_schema_block_order_changes_tier_structure() -> None:
    start = state("start")
    via_x = state("via-x")
    via_y = state("via-y")
    x_edge = edge(start, via_x, "x")
    y_edge = edge(start, via_y, "y")
    xy_tower = build_full_tower(
        states=(start, via_x, via_y),
        edges=(x_edge, y_edge),
        schema=LabelBlockSchema.from_labels(("x", "y")),
        current_state=start,
    )
    yx_tower = build_full_tower(
        states=(start, via_x, via_y),
        edges=(x_edge, y_edge),
        schema=LabelBlockSchema.from_labels(("y", "x")),
        current_state=start,
    )

    assert normalized_state_partitions(xy_tower)[1] != normalized_state_partitions(
        yx_tower
    )[1]
    assert normalized_state_partitions(xy_tower)[-1] == normalized_state_partitions(
        yx_tower
    )[-1]


def test_no_contraction_fixture_compares_outgoing_data_only() -> None:
    start = state("start")
    goal = state("goal")
    first_edge = edge(start, goal, "free")
    fixture = EquivalenceFixture(
        states=(start, goal),
        edges=(first_edge,),
        batches=(DeltaBatch(states=(goal,), edges=(first_edge,)),),
        schema=NoContractionSchema(),
        current_state=start,
    )

    assert_partition_towers_equivalent(fixture)


def assert_partition_towers_equivalent(fixture: EquivalenceFixture) -> None:
    full_tower = build_full_tower(
        states=fixture.states,
        edges=fixture.edges,
        schema=fixture.schema,
        current_state=fixture.current_state,
    )
    incremental_tower = build_incremental_tower(fixture)

    assert normalized_state_partitions(full_tower) == normalized_state_partitions(
        incremental_tower
    )
    assert normalized_outgoing_collections(full_tower) == normalized_outgoing_collections(
        incremental_tower
    )
    assert normalized_internal_edges(full_tower) == normalized_internal_edges(
        incremental_tower
    )
    assert normalized_schema_assignments(full_tower) == normalized_schema_assignments(
        incremental_tower
    )
    assert normalized_current_positions(full_tower) == normalized_current_positions(
        incremental_tower
    )
    assert normalized_readouts(full_tower) == normalized_readouts(incremental_tower)


def build_full_tower(
    *,
    states: Iterable[State],
    edges: Iterable[BaseEdge],
    schema: ContractionSchema,
    current_state: State,
) -> PartitionTower:
    tower = PartitionTower(schema=schema)
    tower.initialize(
        initial_states=states,
        initial_edges=edges,
        current_state=current_state,
    )
    return tower


def build_incremental_tower(fixture: EquivalenceFixture) -> PartitionTower:
    tower = PartitionTower(schema=fixture.schema)
    tower.initialize(
        initial_states=(fixture.states[0],),
        initial_edges=(),
        current_state=fixture.states[0],
    )
    current_state = fixture.states[0]
    for batch in fixture.batches:
        if batch.states:
            current_state = batch.states[-1]
        tower.update_with_delta(
            delta_states=batch.states,
            delta_edges=batch.edges,
            current_state=current_state,
        )
    tower.update_with_delta(
        delta_states=(),
        delta_edges=(),
        current_state=fixture.current_state,
    )
    return tower


def normalized_state_partitions(
    tower: PartitionTower,
) -> tuple[tuple[tuple[object, ...], ...], ...]:
    return tuple(
        tuple(
            sorted(
                tuple(state_identity(tower.registry.state_for_id(state_id)) for state_id in cell)
                for cell in layer.members_by_cell_id.values()
            )
        )
        for layer in tower.state_layers
    )


def normalized_outgoing_collections(
    tower: PartitionTower,
) -> tuple[tuple[tuple[tuple[object, ...], tuple[tuple[object, object, object], ...]], ...], ...]:
    normalized_tiers = []
    for tier, state_layer in enumerate(tower.state_layers):
        action_layer = tower.action_layers[tier]
        normalized_collections = []
        for state_cell_id in state_layer.all_cell_ids():
            collection_id = action_layer.outgoing_collection(state_cell_id)
            normalized_collections.append(
                (
                    normalized_state_cell(tower, state_layer, state_cell_id),
                    tuple(
                        edge_identity(tower.registry.edge_for_id(edge_id))
                        for edge_id in action_layer.edge_ids_for_collection(collection_id)
                    ),
                )
            )
        normalized_tiers.append(tuple(sorted(normalized_collections)))
    return tuple(normalized_tiers)


def normalized_internal_edges(
    tower: PartitionTower,
) -> tuple[tuple[tuple[tuple[object, ...], tuple[tuple[object, object, object], ...]], ...], ...]:
    normalized_tiers = []
    for tier, state_layer in enumerate(tower.state_layers):
        action_layer = tower.action_layers[tier]
        normalized_cells = []
        for state_cell_id in state_layer.all_cell_ids():
            internal_edges = tuple(
                edge_identity(tower.registry.edge_for_id(edge_id))
                for edge_id in action_layer.internal_edge_ids(state_cell_id)
            )
            if internal_edges:
                normalized_cells.append(
                    (normalized_state_cell(tower, state_layer, state_cell_id), internal_edges)
                )
        normalized_tiers.append(tuple(sorted(normalized_cells)))
    return tuple(normalized_tiers)


def normalized_schema_assignments(
    tower: PartitionTower,
) -> tuple[tuple[tuple[object, object, object], object | None], ...]:
    return tuple(
        sorted(
            (
                edge_identity(tower.registry.edge_for_id(edge_id)),
                None if block_id is None else block_id.value,
            )
            for edge_id, block_id in (
                tower.schema_assignment_store.assignment_by_edge_id.items()
            )
        )
    )


def normalized_current_positions(tower: PartitionTower) -> tuple[tuple[object, ...] | None, ...]:
    if tower.last_update_result is None:
        return ()
    positions = []
    for tier, position in enumerate(tower.last_update_result.current_position_by_tier):
        if position is None:
            positions.append(None)
        else:
            positions.append(normalized_state_cell(tower, tower.state_layers[tier], position))
    return tuple(positions)


def normalized_readouts(
    tower: PartitionTower,
) -> tuple[
    tuple[
        tuple[tuple[object, tuple[object, ...]], ...],
        tuple[tuple[tuple[object, object, object], tuple[object, ...]], ...],
        tuple[object, ...] | None,
    ],
    ...,
]:
    normalized = []
    for tier_view in tower.to_quotient_tier_views():
        node_members = tuple(
            sorted(
                tuple(sorted(state_identity(state) for state in members))
                for members in tier_view.cosets.quotient_node_members.values()
            )
        )
        edge_members = tuple(
            sorted(
                tuple(sorted(edge_identity(member) for member in members))
                for members in tier_view.cosets.quotient_edge_members.values()
            )
        )
        current_position = None
        if tier_view.current_position is not None:
            current_position = tuple(
                sorted(
                    state_identity(state)
                    for state in tier_view.cosets.node_members(tier_view.current_position)
                )
            )
        normalized.append((node_members, edge_members, current_position))
    return tuple(normalized)


def normalized_state_cell(
    tower: PartitionTower,
    state_layer,
    state_cell_id: StateCellId,
) -> tuple[object, ...]:
    return tuple(
        state_identity(tower.registry.state_for_id(state_id))
        for state_id in state_layer.members(state_cell_id)
    )


def state_identity(state: State) -> object:
    return state.canonical_identity


def edge_identity(edge: BaseEdge) -> tuple[object, object, object]:
    return (
        edge.source.canonical_identity,
        edge.action.canonical_identity,
        edge.target.canonical_identity,
    )
