"""Contraction-policy contract surface."""

from __future__ import annotations

import random
from collections.abc import Hashable
from dataclasses import dataclass
from typing import Protocol

from state_collapser.contract.selection import EdgeSelection
from state_collapser.graph.local_star import LocalStar


class ContractionPolicy(Protocol):
    """Protocol for local-star edge-family selection policies."""

    def select(self, local_star: LocalStar) -> EdgeSelection:
        """Return the edge selection induced by the local-star view."""


@dataclass(frozen=True, slots=True)
class LabelContractionPolicy:
    """Select outgoing edges whose labels satisfy a requested predicate set."""

    labels: frozenset[Hashable]

    def select(self, local_star: LocalStar) -> EdgeSelection:
        """Select outgoing edges whose edge/action labels match this policy."""

        selected = tuple(
            edge
            for edge in local_star.outgoing_edges
            if self.labels.intersection(edge.labels) or self.labels.intersection(edge.action.labels)
        )
        return EdgeSelection(edges=selected)


@dataclass(frozen=True, slots=True)
class SeededRandomContractionPolicy:
    """Select a deterministic random subset of local-star outgoing edges."""

    seed: int
    sample_size: int = 1

    def select(self, local_star: LocalStar) -> EdgeSelection:
        """Select a seeded random subset of outgoing local-star edges."""

        edges = list(local_star.outgoing_edges)
        if not edges:
            return EdgeSelection()
        rng = random.Random(self.seed)
        size = min(self.sample_size, len(edges))
        selected = tuple(rng.sample(edges, size))
        return EdgeSelection(edges=selected)


__all__ = [
    "ContractionPolicy",
    "LabelContractionPolicy",
    "SeededRandomContractionPolicy",
]
