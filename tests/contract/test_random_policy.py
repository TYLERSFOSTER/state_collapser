"""Tests for the seeded-random contraction policy."""

from __future__ import annotations

from state_collapser.contract.policy import SeededRandomContractionPolicy
from state_collapser.core.action import PrimitiveAction
from state_collapser.core.annotations import NodeAnnotationStore
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.graph.local_star import LocalStar


def build_local_star() -> LocalStar:
    source = State(payload=("source",), identity="s1")
    targets = tuple(State(payload=(f"target-{i}",), identity=f"s{i}") for i in range(3))
    actions = tuple(PrimitiveAction(payload=(f"step-{i}",), identity=f"a{i}") for i in range(3))
    edges = tuple(
        BaseEdge(source=source, action=actions[i], target=targets[i], labels=(str(i),))
        for i in range(3)
    )
    return LocalStar(
        center=source,
        outgoing_edges=edges,
        outgoing_neighbors=targets,
        annotations=NodeAnnotationStore(),
    )


def test_deterministic_output_under_fixed_seed() -> None:
    star = build_local_star()
    policy = SeededRandomContractionPolicy(seed=7, sample_size=2)

    selection_a = policy.select(star)
    selection_b = policy.select(star)

    assert selection_a == selection_b


def test_output_is_subset_of_local_star() -> None:
    star = build_local_star()
    policy = SeededRandomContractionPolicy(seed=7, sample_size=2)

    selection = policy.select(star)

    assert set(selection.edges).issubset(set(star.outgoing_edges))


def test_no_mutation_performed_by_policy_itself() -> None:
    star = build_local_star()
    original_edges = star.outgoing_edges
    original_neighbors = star.outgoing_neighbors
    policy = SeededRandomContractionPolicy(seed=7, sample_size=2)

    policy.select(star)

    assert star.outgoing_edges == original_edges
    assert star.outgoing_neighbors == original_neighbors
