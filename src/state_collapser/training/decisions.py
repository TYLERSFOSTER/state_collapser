"""Action-decision surface for training-facing code."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ActionDecision:
    """Typed package-facing action-decision object."""

    chosen_action: object | None = None
    action_probabilities: Mapping[object, float] | None = None
    action_logits: Mapping[object, float] | None = None
    action_values: Mapping[object, float] | None = None
    value_estimate: float | None = None
    diagnostics: Mapping[str, object] = field(default_factory=dict)


__all__ = ["ActionDecision"]
