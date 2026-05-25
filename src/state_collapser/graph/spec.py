"""Graph specification contract surface."""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GraphSpec:
    """Immutable environment-specific graph-spec contract."""

    name: str
    rules: tuple[tuple[str, Hashable], ...] = ()
    metadata: tuple[tuple[str, Hashable], ...] = ()


__all__ = ["GraphSpec"]
