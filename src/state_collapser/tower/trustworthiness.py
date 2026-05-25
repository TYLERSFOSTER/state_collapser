"""Trustworthiness-policy contract surface."""

from __future__ import annotations

from typing import Protocol

from state_collapser.tower.snapshot import LiveRuntimeView


class TrustworthinessPolicy(Protocol):
    """Extension-point protocol for future trustworthiness heuristics."""

    def is_trustworthy(self, snapshot: LiveRuntimeView, tier: int) -> bool:
        """Return whether the requested tier is trustworthy for the given snapshot."""


__all__ = ["TrustworthinessPolicy"]
