"""Tests for quotient tier views."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.quotient.tier_view import QuotientTierView


def test_nested_cumulative_outgoing_edge_query_semantics() -> None:
    tier_view = QuotientTierView(tier=2)

    tier_view.add_outgoing_knowledge(0, "edge-a")
    tier_view.add_outgoing_knowledge(1, "edge-b")
    tier_view.add_outgoing_knowledge(2, "edge-c")

    assert tier_view.outgoing_edge_knowledge_exact(1) == frozenset({"edge-b"})
    assert tier_view.outgoing_edge_knowledge_upto(1) == frozenset({"edge-a", "edge-b"})


def test_current_tier_position_storage() -> None:
    tier_view = QuotientTierView(tier=2)

    tier_view.set_current_position("Q1")

    assert tier_view.current_position == "Q1"


def test_same_coset_and_triviality_queries() -> None:
    tier_view = QuotientTierView(tier=1)
    s1 = State(payload=("s1",), identity="s1")
    s2 = State(payload=("s2",), identity="s2")
    s3 = State(payload=("s3",), identity="s3")
    a = PrimitiveAction(payload=("step",), identity="a")
    edge = BaseEdge(source=s1, action=a, target=s2)

    tier_view.projection.set_state_projection(s1, "Q1")
    tier_view.projection.set_state_projection(s2, "Q1")
    tier_view.projection.set_state_projection(s3, "Q2")

    assert tier_view.same_coset(s1, s2) is True
    assert tier_view.same_coset(s1, s3) is False
    assert tier_view.projected_edge_is_trivial(edge) is True


def test_point_query() -> None:
    tier_view = QuotientTierView(tier=2)
    s1 = State(payload=("s1",), identity="s1")
    tier_view.projection.set_state_projection(s1, "Q1")
    tier_view.cosets.add_node_member("Q1", s1)

    assert tier_view.is_point() is True
