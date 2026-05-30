"""Core annotation contract surface."""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass

from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State


class NodeAnnotationStore:
    """Node- and tier-indexed runtime annotation store."""

    def __init__(self) -> None:
        """Initialize empty label, note, payload, and outgoing-knowledge stores."""

        self._labels: set[Hashable] = set()
        self._notes: dict[Hashable, Hashable] = {}
        self._pushed_payloads: list[VistaPayload] = []
        self._pulled_payloads: list[VistaPayload] = []
        self._outgoing_knowledge_by_tier: dict[int, set[Hashable]] = {}

    def add_label(self, label: Hashable) -> None:
        """Record a local label for this node."""

        self._labels.add(label)

    def add_note(self, key: Hashable, value: Hashable) -> None:
        """Record a local note for this node."""

        self._notes[key] = value

    def receive_pushed_payload(self, payload: VistaPayload) -> None:
        """Record payload received by push propagation."""

        self._pushed_payloads.append(payload)

    def receive_pulled_payload(self, payload: VistaPayload) -> None:
        """Record payload received by pull propagation."""

        self._pulled_payloads.append(payload)

    def add_outgoing_knowledge(self, tier: int, knowledge: Hashable) -> None:
        """Record outgoing-edge possibility knowledge at a tier."""

        self._outgoing_knowledge_by_tier.setdefault(tier, set()).add(knowledge)

    def outgoing_knowledge_exact(self, tier: int) -> frozenset[Hashable]:
        """Return outgoing knowledge recorded exactly at one tier."""

        return frozenset(self._outgoing_knowledge_by_tier.get(tier, set()))

    def outgoing_knowledge_upto(self, tier: int) -> frozenset[Hashable]:
        """Return outgoing knowledge accumulated across all tiers <= tier."""

        cumulative: set[Hashable] = set()
        for known_tier, knowledge in self._outgoing_knowledge_by_tier.items():
            if known_tier <= tier:
                cumulative.update(knowledge)
        return frozenset(cumulative)

    @property
    def labels(self) -> frozenset[Hashable]:
        """Return the local labels recorded at this node."""

        return frozenset(self._labels)

    @property
    def notes(self) -> dict[Hashable, Hashable]:
        """Return a copy of the local note mapping."""

        return dict(self._notes)

    @property
    def pushed_payloads(self) -> tuple[VistaPayload, ...]:
        """Return received push payloads in receipt order."""

        return tuple(self._pushed_payloads)

    @property
    def pulled_payloads(self) -> tuple[VistaPayload, ...]:
        """Return received pull payloads in receipt order."""

        return tuple(self._pulled_payloads)


@dataclass(frozen=True, slots=True)
class VistaPayload:
    """Outgoing-edge possibility payload used for push/pull propagation."""

    outgoing_edges: tuple[BaseEdge, ...] = ()
    reachable_targets: tuple[State, ...] = ()
    labels: tuple[Hashable, ...] = ()
    contraction_marks: tuple[Hashable, ...] = ()
    coset_marks: tuple[Hashable, ...] = ()


__all__ = ["NodeAnnotationStore", "VistaPayload"]
