"""Tests for annotation-store and payload objects."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.annotations import NodeAnnotationStore, VistaPayload
from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State


def test_annotation_store_stores_labels_and_notes() -> None:
    store = NodeAnnotationStore()

    store.add_label("seen")
    store.add_note("color", "blue")

    assert store.labels == frozenset({"seen"})
    assert store.notes == {"color": "blue"}


def test_annotation_store_receives_push_and_pull_payloads() -> None:
    store = NodeAnnotationStore()
    payload = VistaPayload(labels=("forward",))

    store.receive_pushed_payload(payload)
    store.receive_pulled_payload(payload)

    assert store.pushed_payloads == (payload,)
    assert store.pulled_payloads == (payload,)


def test_annotation_store_exact_tier_query() -> None:
    store = NodeAnnotationStore()

    store.add_outgoing_knowledge(0, "edge-a")
    store.add_outgoing_knowledge(1, "edge-b")

    assert store.outgoing_knowledge_exact(1) == frozenset({"edge-b"})


def test_annotation_store_cumulative_upto_query() -> None:
    store = NodeAnnotationStore()

    store.add_outgoing_knowledge(0, "edge-a")
    store.add_outgoing_knowledge(1, "edge-b")
    store.add_outgoing_knowledge(2, "edge-c")

    assert store.outgoing_knowledge_upto(1) == frozenset({"edge-a", "edge-b"})


def test_vista_payload_contents_preserved() -> None:
    source = State(payload=("source",), identity="s1")
    target = State(payload=("target",), identity="s2")
    action = PrimitiveAction(payload=("step",), identity="a1")
    edge = BaseEdge(source=source, action=action, target=target, labels=("boundary",))

    payload = VistaPayload(
        outgoing_edges=(edge,),
        reachable_targets=(target,),
        labels=("forward",),
        contraction_marks=("c0",),
        coset_marks=("q0",),
    )

    assert payload.outgoing_edges == (edge,)
    assert payload.reachable_targets == (target,)
    assert payload.contraction_marks == ("c0",)
    assert payload.coset_marks == ("q0",)


def test_vista_payload_labels_preserved() -> None:
    payload = VistaPayload(labels=("forward", "safe"))

    assert payload.labels == ("forward", "safe")
