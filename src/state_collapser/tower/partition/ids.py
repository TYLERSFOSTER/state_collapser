"""Typed identifiers for the partition-tower runtime.

The partition tower uses explicit id types so state ids, edge ids, and cell ids
cannot be accidentally mixed while the runtime is being refactored.
"""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, order=True)
class StateId:
    """Stable registry-local identifier for one discovered base state."""

    value: int


@dataclass(frozen=True, slots=True, order=True)
class EdgeId:
    """Stable registry-local identifier for one discovered base edge."""

    value: int


@dataclass(frozen=True, slots=True, order=True)
class ActionId:
    """Stable registry-local identifier for one primitive action identity."""

    value: int


@dataclass(frozen=True, slots=True, order=True)
class TierIndex:
    """Typed tower tier index for APIs that should not accept raw integers."""

    value: int


@dataclass(frozen=True, slots=True)
class SchemaBlockId:
    """Identifier for one ordered block in a contraction schema."""

    value: Hashable


@dataclass(frozen=True, slots=True, order=True)
class StateCellId:
    """Identifier for one historical state partition cell at one tier."""

    tier: int
    ordinal: int


@dataclass(frozen=True, slots=True, order=True)
class ActionCollectionId:
    """Identifier for one outgoing-action collection at one tier."""

    tier: int
    ordinal: int


@dataclass(frozen=True, slots=True, order=True)
class ActionCellId:
    """Identifier for one decision-level action cell at one tier."""

    tier: int
    ordinal: int


class IdAllocator:
    """Monotone integer allocator for one registry-local id namespace."""

    def __init__(self) -> None:
        """Start allocation at zero for a fresh id namespace."""

        self._next_value = 0

    def next(self) -> int:
        """Return the next integer and advance the namespace counter."""

        value = self._next_value
        self._next_value += 1
        return value


__all__ = [
    "ActionCellId",
    "ActionCollectionId",
    "ActionId",
    "EdgeId",
    "IdAllocator",
    "SchemaBlockId",
    "StateCellId",
    "StateId",
    "TierIndex",
]
