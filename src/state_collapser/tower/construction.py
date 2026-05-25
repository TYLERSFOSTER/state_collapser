"""Legacy full-rebuild dynamic tower construction helpers.

The partition tower is the normal runtime authority. This module remains as a
legacy/validation path for tests and compatibility checks that need the older
full-reconstruction behavior.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from math import ceil

from state_collapser.contract.policy import ContractionPolicy
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.graph.explored_graph import ExploredGraph
from state_collapser.graph.vista_graph import VistaGraph
from state_collapser.quotient.tier_view import QuotientTierView


@dataclass(frozen=True, slots=True)
class TierContractionRecord:
    """Tier-local contraction bookkeeping for one tower-construction pass."""

    tier_index: int
    eligible_base_edges: tuple[BaseEdge, ...]
    selected_base_edges: tuple[BaseEdge, ...]
    retired_base_edges: tuple[BaseEdge, ...]


@dataclass(frozen=True, slots=True)
class TowerConstructionResult:
    """Result of one package-owned tower construction/update pass."""

    ordered_tiers: tuple[QuotientTierView, ...]
    tier_contraction_records: tuple[TierContractionRecord, ...]
    stopping_reason: str


def _base_node_id(state: State) -> tuple[object, ...]:
    return ("state", state.canonical_identity)


def _base_edge_id(edge: BaseEdge) -> tuple[object, ...]:
    return (
        "edge",
        edge.source.canonical_identity,
        edge.action.canonical_identity,
        edge.target.canonical_identity,
    )


def _stable_edge_key(edge: BaseEdge) -> tuple[str, str, str]:
    return (
        repr(edge.source.canonical_identity),
        repr(edge.action.canonical_identity),
        repr(edge.target.canonical_identity),
    )


def _visible_base_edges(
    explored_graph: ExploredGraph,
    vista_graph: VistaGraph,
) -> tuple[BaseEdge, ...]:
    ordered: dict[BaseEdge, None] = {}
    for state in explored_graph.visited_states():
        for edge in vista_graph.vista_edges(state):
            ordered.setdefault(edge, None)
    return tuple(ordered.keys())


def _visible_base_states(
    base_edges: Iterable[BaseEdge],
    explored_graph: ExploredGraph,
) -> tuple[State, ...]:
    ordered: dict[State, None] = {}
    for state in explored_graph.visited_states():
        ordered.setdefault(state, None)
    for edge in base_edges:
        ordered.setdefault(edge.source, None)
        ordered.setdefault(edge.target, None)
    return tuple(ordered.keys())


def _eligible_base_edges(
    *,
    base_edges: tuple[BaseEdge, ...],
    current_tier: QuotientTierView,
    contraction_policy: ContractionPolicy | None,
) -> tuple[BaseEdge, ...]:
    if contraction_policy is None:
        return ()
    return tuple(
        edge
        for edge in sorted(base_edges, key=_stable_edge_key)
        if not projected_edge_is_trivial(current_tier, edge)
    )


def _selected_subfamily(
    eligible_base_edges: tuple[BaseEdge, ...],
) -> tuple[BaseEdge, ...]:
    if not eligible_base_edges:
        return ()
    budget = max(1, ceil(len(eligible_base_edges) * 0.2))
    return eligible_base_edges[:budget]


def build_dynamic_tower(
    *,
    explored_graph: ExploredGraph,
    vista_graph: VistaGraph,
    current_base_state: State | None,
    contraction_policy: ContractionPolicy | None,
) -> TowerConstructionResult:
    """Build a legacy full-reconstruction tower from explored/vista graph layers."""

    base_edges = _visible_base_edges(explored_graph, vista_graph)
    base_states = _visible_base_states(base_edges, explored_graph)

    tiers: list[QuotientTierView] = []
    tier_records: list[TierContractionRecord] = []
    tier0 = QuotientTierView(tier=0)
    for state in base_states:
        node_id = _base_node_id(state)
        tier0.projection.set_state_projection(state, node_id)
        tier0.cosets.add_node_member(node_id, state)
    for edge in base_edges:
        edge_id = _base_edge_id(edge)
        tier0.projection.set_edge_projection(edge, edge_id)
        tier0.cosets.add_edge_member(edge_id, edge)
        tier0.add_outgoing_knowledge(0, edge_id)
    if current_base_state is not None:
        tier0.set_current_position(tier0.projection.project_state(current_base_state))
    tiers.append(tier0)

    current_tier = tier0
    tier_index = 1
    stopping_reason = "no_visible_edges"
    while True:
        next_tier, record, reason = _build_next_tier(
            tier_index=tier_index,
            current_tier=current_tier,
            base_edges=base_edges,
            base_states=base_states,
            current_base_state=current_base_state,
            contraction_policy=contraction_policy,
        )
        tier_records.append(record)
        if next_tier is None:
            stopping_reason = reason
            break
        tiers.append(next_tier)
        current_tier = next_tier
        tier_index += 1

    return TowerConstructionResult(
        ordered_tiers=tuple(tiers),
        tier_contraction_records=tuple(tier_records),
        stopping_reason=stopping_reason,
    )


def _build_next_tier(
    *,
    tier_index: int,
    current_tier: QuotientTierView,
    base_edges: tuple[BaseEdge, ...],
    base_states: tuple[State, ...],
    current_base_state: State | None,
    contraction_policy: ContractionPolicy | None,
) -> tuple[QuotientTierView | None, TierContractionRecord, str]:
    eligible_base_edges = _eligible_base_edges(
        base_edges=base_edges,
        current_tier=current_tier,
        contraction_policy=contraction_policy,
    )
    if not eligible_base_edges:
        return (
            None,
            TierContractionRecord(
                tier_index=current_tier.tier,
                eligible_base_edges=(),
                selected_base_edges=(),
                retired_base_edges=(),
            ),
            "no_nontrivial_remainder",
        )

    selected_base_edges = _selected_subfamily(eligible_base_edges)
    if not selected_base_edges:
        return (
            None,
            TierContractionRecord(
                tier_index=current_tier.tier,
                eligible_base_edges=eligible_base_edges,
                selected_base_edges=(),
                retired_base_edges=(),
            ),
            "empty_selection_budget",
        )

    selected_pairs: set[tuple[object, object]] = set()
    for edge in selected_base_edges:
        source_id = current_tier.projection.project_state(edge.source)
        target_id = current_tier.projection.project_state(edge.target)
        if source_id is None or target_id is None or source_id == target_id:
            continue
        ordered = tuple(sorted((source_id, target_id), key=repr))
        selected_pairs.add((ordered[0], ordered[1]))

    if not selected_pairs:
        return (
            None,
            TierContractionRecord(
                tier_index=current_tier.tier,
                eligible_base_edges=eligible_base_edges,
                selected_base_edges=selected_base_edges,
                retired_base_edges=selected_base_edges,
            ),
            "selected_family_became_trivial",
        )

    components = _connected_components(selected_pairs, current_tier)
    next_tier = QuotientTierView(tier=tier_index)
    for state in base_states:
        prior_id = current_tier.projection.project_state(state)
        if prior_id is None:
            continue
        component_id = components.get(prior_id, _singleton_component(prior_id))
        quotient_node = ("tier-node", tier_index, component_id)
        next_tier.projection.set_state_projection(state, quotient_node)
        next_tier.cosets.add_node_member(quotient_node, state)

    for edge in base_edges:
        source_node = next_tier.projection.project_state(edge.source)
        target_node = next_tier.projection.project_state(edge.target)
        if source_node is None or target_node is None or source_node == target_node:
            continue
        quotient_edge = (
            "tier-edge",
            tier_index,
            source_node,
            edge.action.canonical_identity,
            target_node,
        )
        next_tier.projection.set_edge_projection(edge, quotient_edge)
        next_tier.cosets.add_edge_member(quotient_edge, edge)
        next_tier.add_outgoing_knowledge(tier_index, quotient_edge)

    if current_base_state is not None:
        next_tier.set_current_position(next_tier.projection.project_state(current_base_state))

    retired_base_edges = tuple(
        edge for edge in selected_base_edges if projected_edge_is_trivial(next_tier, edge)
    )
    return (
        next_tier,
        TierContractionRecord(
            tier_index=current_tier.tier,
            eligible_base_edges=eligible_base_edges,
            selected_base_edges=selected_base_edges,
            retired_base_edges=retired_base_edges,
        ),
        "built_next_tier",
    )


def _singleton_component(node_id: object) -> frozenset[object]:
    return frozenset({node_id})


def _connected_components(
    edges: set[tuple[object, object]],
    current_tier: QuotientTierView,
) -> dict[object, frozenset[object]]:
    adjacency: dict[object, set[object]] = {}
    for left, right in edges:
        adjacency.setdefault(left, set()).add(right)
        adjacency.setdefault(right, set()).add(left)
    for quotient_node in current_tier.cosets.quotient_node_members:
        adjacency.setdefault(quotient_node, set())

    seen: set[object] = set()
    components: dict[object, frozenset[object]] = {}
    for node in adjacency:
        if node in seen:
            continue
        queue: deque[object] = deque([node])
        component: set[object] = set()
        while queue:
            current = queue.popleft()
            if current in seen:
                continue
            seen.add(current)
            component.add(current)
            queue.extend(adjacency[current] - seen)
        frozen = frozenset(component)
        for member in component:
            components[member] = frozen
    return components


def tier_is_point(tier: QuotientTierView) -> bool:
    """Return whether a tier has collapsed to a single quotient node."""

    return len(tier.cosets.quotient_node_members) <= 1


def projected_edge_is_trivial(tier: QuotientTierView, edge: BaseEdge) -> bool:
    """Return whether the projected image of a base edge is trivial at this tier."""

    source_id = tier.projection.project_state(edge.source)
    target_id = tier.projection.project_state(edge.target)
    return source_id is None or target_id is None or source_id == target_id


def tower_is_fully_propagated(
    tiers: tuple[QuotientTierView, ...],
    current_base_state: State | None,
) -> bool:
    """Return whether every tier has a current position for the current base state."""

    if current_base_state is None:
        return True
    return all(
        tier.projection.project_state(current_base_state) == tier.current_position
        for tier in tiers
    )


__all__ = [
    "TierContractionRecord",
    "TowerConstructionResult",
    "build_dynamic_tower",
    "projected_edge_is_trivial",
    "tier_is_point",
    "tower_is_fully_propagated",
]
