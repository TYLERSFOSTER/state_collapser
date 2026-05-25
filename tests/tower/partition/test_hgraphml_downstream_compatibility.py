"""HGraphML-shaped compatibility tests for partition-tower readout.

These tests do not import HGraphML. They protect the upstream
`state_collapser` surfaces that HGraphML needs: full-graph tower construction,
state-cell fibers, registered fine edges, and coarse endpoint recovery by tier.
"""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition import LabelBlockSchema, PartitionTower
from state_collapser.tower.partition.ids import StateCellId
from state_collapser.tower.partition.tower import build_partition_tower_full


def _state(index: int) -> State:
    return State(payload=("node", index), identity=("node", index))


def _edge(index: int, source: State, target: State, label: str) -> BaseEdge:
    return BaseEdge(
        source=source,
        action=PrimitiveAction(
            payload=("edge", index),
            identity=("edge", index),
            labels=(label,),
        ),
        target=target,
        labels=(label,),
    )


def _node_fibers_by_tier(
    tower: PartitionTower,
    states: tuple[State, ...],
) -> tuple[tuple[tuple[int, ...], ...], ...]:
    index_by_state = {state: index for index, state in enumerate(states)}
    fibers_by_tier: list[tuple[tuple[int, ...], ...]] = []

    for state_layer in tower.state_layers:
        tier_fibers: list[tuple[int, ...]] = []
        for state_cell_id in state_layer.all_cell_ids():
            tier_fibers.append(
                tuple(
                    sorted(
                        index_by_state[tower.registry.state_for_id(state_id)]
                        for state_id in state_layer.members(state_cell_id)
                    )
                )
            )
        fibers_by_tier.append(tuple(sorted(tier_fibers)))

    return tuple(fibers_by_tier)


def _edge_fibers_by_coarse_endpoints(
    tower: PartitionTower,
    tier: int,
    states: tuple[State, ...],
    edges: tuple[BaseEdge, ...],
) -> dict[tuple[tuple[int, ...], tuple[int, ...]], tuple[int, ...]]:
    index_by_state = {state: index for index, state in enumerate(states)}
    index_by_edge = {edge: index for index, edge in enumerate(edges)}
    state_layer = tower.state_layers[tier]
    cell_fibers: dict[StateCellId, tuple[int, ...]] = {
        state_cell_id: tuple(
            sorted(
                index_by_state[tower.registry.state_for_id(state_id)]
                for state_id in state_layer.members(state_cell_id)
            )
        )
        for state_cell_id in state_layer.all_cell_ids()
    }
    grouped: dict[tuple[tuple[int, ...], tuple[int, ...]], list[int]] = {}

    for edge_id in tower.registry.edge_ids:
        source_cell = state_layer.cell_of(tower.registry.source_state_id(edge_id))
        target_cell = state_layer.cell_of(tower.registry.target_state_id(edge_id))
        coarse_endpoint = (cell_fibers[source_cell], cell_fibers[target_cell])
        grouped.setdefault(coarse_endpoint, []).append(
            index_by_edge[tower.registry.edge_for_id(edge_id)]
        )

    return {
        coarse_endpoint: tuple(sorted(edge_indices))
        for coarse_endpoint, edge_indices in grouped.items()
    }


def test_hgraphml_style_full_graph_readout_recovers_node_and_edge_fibers() -> None:
    """Protect the downstream graph-ML adapter's expected readout pattern."""

    states = tuple(_state(index) for index in range(4))
    edges = (
        _edge(0, states[0], states[1], "collapse"),
        _edge(1, states[1], states[2], "collapse"),
        _edge(2, states[2], states[3], "message"),
        _edge(3, states[0], states[3], "message"),
    )

    tower = build_partition_tower_full(
        states=states,
        edges=edges,
        current_state=None,
        schema=LabelBlockSchema.from_labels(("collapse",)),
    )

    assert len(tower.state_layers) == 2
    assert _node_fibers_by_tier(tower, states) == (
        ((0,), (1,), (2,), (3,)),
        ((0, 1, 2), (3,)),
    )

    for tier in range(len(tower.state_layers)):
        node_fibers = _node_fibers_by_tier(tower, states)[tier]
        assert sorted(index for fiber in node_fibers for index in fiber) == [0, 1, 2, 3]

        edge_fibers = _edge_fibers_by_coarse_endpoints(tower, tier, states, edges)
        assert sorted(index for fiber in edge_fibers.values() for index in fiber) == [
            0,
            1,
            2,
            3,
        ]

        for state_cell_id in tower.state_layers[tier].all_cell_ids():
            collection_id = tower.action_layers[tier].outgoing_collection(state_cell_id)
            action_cell_ids = tower.action_layers[tier].action_cells_for_collection(
                collection_id,
            )
            assert isinstance(action_cell_ids, tuple)

    assert _edge_fibers_by_coarse_endpoints(tower, 1, states, edges) == {
        ((0, 1, 2), (0, 1, 2)): (0, 1),
        ((0, 1, 2), (3,)): (2, 3),
    }
