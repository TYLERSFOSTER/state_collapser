"""Tests for the label-based contraction policy."""

from __future__ import annotations

from state_collapser.contract.policy import LabelContractionPolicy
from state_collapser.core.action import PrimitiveAction
from state_collapser.core.annotations import NodeAnnotationStore
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.graph.local_star import LocalStar


def build_local_star() -> tuple[LocalStar, BaseEdge, BaseEdge]:
    source = State(payload=("source",), identity="s1")
    target_a = State(payload=("target-a",), identity="s2")
    target_b = State(payload=("target-b",), identity="s3")
    action_a = PrimitiveAction(payload=("step-a",), identity="a1", labels=("forward",))
    action_b = PrimitiveAction(payload=("step-b",), identity="a2", labels=("lateral",))
    edge_a = BaseEdge(source=source, action=action_a, target=target_a, labels=("blue",))
    edge_b = BaseEdge(source=source, action=action_b, target=target_b, labels=("red",))
    star = LocalStar(
        center=source,
        outgoing_edges=(edge_a, edge_b),
        outgoing_neighbors=(target_a, target_b),
        annotations=NodeAnnotationStore(),
    )
    return star, edge_a, edge_b


def test_correct_edges_selected_by_label() -> None:
    star, edge_a, _ = build_local_star()
    policy = LabelContractionPolicy(labels=frozenset({"blue"}))

    selection = policy.select(star)

    assert selection.edges == (edge_a,)


def test_only_requested_labels_selected() -> None:
    star, edge_a, edge_b = build_local_star()
    policy = LabelContractionPolicy(labels=frozenset({"red"}))

    selection = policy.select(star)

    assert selection.edges == (edge_b,)
    assert edge_a not in selection.edges


def test_no_tower_mutation_performed_by_policy_itself() -> None:
    star, edge_a, edge_b = build_local_star()
    original_edges = star.outgoing_edges
    original_neighbors = star.outgoing_neighbors
    policy = LabelContractionPolicy(labels=frozenset({"blue", "red"}))

    selection = policy.select(star)

    assert selection.edges == (edge_a, edge_b)
    assert star.outgoing_edges == original_edges
    assert star.outgoing_neighbors == original_neighbors
