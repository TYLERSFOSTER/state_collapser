"""Quotient-tier-view contract surface."""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass, field

from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.quotient.cosets import CosetStore
from state_collapser.quotient.projection import ProjectionMap


@dataclass(slots=True)
class QuotientTierView:
    """Combined projection/coset view for one quotient tier."""

    tier: int
    projection: ProjectionMap = field(default_factory=ProjectionMap)
    cosets: CosetStore = field(default_factory=CosetStore)
    outgoing_knowledge_by_tier: dict[int, set[Hashable]] = field(default_factory=dict)
    current_position: Hashable | None = None

    def add_outgoing_knowledge(self, tier: int, knowledge: Hashable) -> None:
        """Record outgoing-edge knowledge at a particular quotient tier."""

        self.outgoing_knowledge_by_tier.setdefault(tier, set()).add(knowledge)

    def outgoing_edge_knowledge_exact(self, tier: int) -> frozenset[Hashable]:
        """Return outgoing-edge knowledge stored exactly at one tier."""

        return frozenset(self.outgoing_knowledge_by_tier.get(tier, set()))

    def outgoing_edge_knowledge_upto(self, tier: int) -> frozenset[Hashable]:
        """Return outgoing-edge knowledge accumulated across all tiers <= tier."""

        cumulative: set[Hashable] = set()
        for known_tier, knowledge in self.outgoing_knowledge_by_tier.items():
            if known_tier <= tier:
                cumulative.update(knowledge)
        return frozenset(cumulative)

    def set_current_position(self, position: Hashable | None) -> None:
        """Record the current position identifier for this tier."""

        self.current_position = position

    def same_coset(self, left: State, right: State) -> bool:
        """Return whether two base states project to the same quotient node."""

        left_id = self.projection.project_state(left)
        right_id = self.projection.project_state(right)
        return left_id is not None and left_id == right_id

    def projected_edge_is_trivial(self, edge: BaseEdge) -> bool:
        """Return whether a base edge projects to a loop/trivial edge at this tier."""

        source_id = self.projection.project_state(edge.source)
        target_id = self.projection.project_state(edge.target)
        return source_id is None or target_id is None or source_id == target_id

    def is_point(self) -> bool:
        """Return whether this quotient tier has collapsed to a single node."""

        return len(self.cosets.quotient_node_members) <= 1


__all__ = ["QuotientTierView"]
