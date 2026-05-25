"""Compatibility readouts from partition towers to quotient tier views."""

from __future__ import annotations

from typing import TYPE_CHECKING

from state_collapser.quotient.tier_view import QuotientTierView

if TYPE_CHECKING:
    from state_collapser.tower.partition.tower import PartitionTower


def to_quotient_tier_views(partition_tower: PartitionTower) -> tuple[QuotientTierView, ...]:
    """Build compatibility quotient-tier views from partition tower data."""

    registry = partition_tower.registry
    positions = (
        ()
        if partition_tower.last_update_result is None
        else partition_tower.last_update_result.current_position_by_tier
    )
    tiers: list[QuotientTierView] = []
    for tier_index, state_layer in enumerate(partition_tower.state_layers):
        tier_view = QuotientTierView(tier=tier_index)
        for state_id in registry.state_ids:
            state = registry.state_for_id(state_id)
            state_cell_id = state_layer.cell_of(state_id)
            tier_view.projection.set_state_projection(state, state_cell_id)
            tier_view.cosets.add_node_member(state_cell_id, state)

        action_layer = partition_tower.action_layers[tier_index]
        active_collection_ids = {
            action_layer.outgoing_collection(state_cell_id)
            for state_cell_id in state_layer.all_cell_ids()
        }
        for collection_id in sorted(active_collection_ids):
            action_cell_ids = action_layer.action_cells_for_collection(collection_id)
            for action_cell_id in action_cell_ids:
                quotient_edge = ("partition-action-cell", tier_index, action_cell_id)
                for edge_id in action_layer.edge_ids_for_action_cell(action_cell_id):
                    edge = registry.edge_for_id(edge_id)
                    tier_view.projection.set_edge_projection(edge, quotient_edge)
                    tier_view.cosets.add_edge_member(quotient_edge, edge)
                    tier_view.add_outgoing_knowledge(tier_index, quotient_edge)
            # Keep a collection-level breadcrumb for empty outgoing collections.
            if not action_cell_ids:
                tier_view.add_outgoing_knowledge(
                    tier_index,
                    ("partition-action-collection", tier_index, collection_id),
                )

        if tier_index < len(positions):
            tier_view.set_current_position(positions[tier_index])
        tiers.append(tier_view)
    return tuple(tiers)


__all__ = ["to_quotient_tier_views"]
