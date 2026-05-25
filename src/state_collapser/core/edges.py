"""Core edge contract surface."""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.state import State


@dataclass(frozen=True, slots=True)
class BaseEdge:
    """Immutable base edge connecting two states by one primitive action."""

    source: State
    action: PrimitiveAction
    target: State
    labels: tuple[Hashable, ...] = ()


__all__ = ["BaseEdge"]
