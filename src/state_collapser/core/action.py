"""Core primitive-action contract surface."""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PrimitiveAction:
    """Immutable primitive action for hidden-graph and runtime layers."""

    payload: Hashable
    identity: Hashable | None = None
    labels: tuple[Hashable, ...] = ()

    @property
    def canonical_identity(self) -> Hashable:
        """Return the stable identity used to talk about this action."""

        return self.payload if self.identity is None else self.identity


__all__ = ["PrimitiveAction"]
