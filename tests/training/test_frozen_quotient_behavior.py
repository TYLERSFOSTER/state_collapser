"""Tests for frozen quotient behavior surfaces."""

from __future__ import annotations

import pytest

from state_collapser.training import FrozenQuotientBehavior, FrozenQuotientStep


def test_frozen_quotient_step_preserves_concrete_values() -> None:
    step = FrozenQuotientStep(
        coarse_tier=2,
        source_cell="source",
        action_cell="action",
        target_cell="target",
        metadata={"kind": "test"},
    )

    assert step.coarse_tier == 2
    assert step.source_cell == "source"
    assert step.action_cell == "action"
    assert step.target_cell == "target"
    assert step.metadata == {"kind": "test"}


def test_frozen_quotient_step_metadata_defaults_safely() -> None:
    left = FrozenQuotientStep(coarse_tier=1, source_cell="source")
    right = FrozenQuotientStep(coarse_tier=1, source_cell="source")

    assert left.metadata == {}
    assert right.metadata == {}
    assert left.metadata is not right.metadata


def test_frozen_quotient_behavior_accepts_adjacent_tiers() -> None:
    step = FrozenQuotientStep(
        coarse_tier=1,
        source_cell="source",
        action_cell="action",
        target_cell="target",
    )
    behavior = FrozenQuotientBehavior(
        behavior_id="behavior",
        coarse_tier=1,
        supported_fine_tier=0,
        current_step=step,
        path_prefix=("source", "target"),
        action_prefix=("action",),
        metadata={"owner": "test"},
    )

    assert behavior.current_step == step
    assert behavior.path_prefix == ("source", "target")
    assert behavior.action_prefix == ("action",)
    assert behavior.metadata == {"owner": "test"}


def test_frozen_quotient_behavior_rejects_non_adjacent_tiers() -> None:
    with pytest.raises(ValueError, match="coarse_tier == supported_fine_tier"):
        FrozenQuotientBehavior(
            behavior_id="behavior",
            coarse_tier=2,
            supported_fine_tier=0,
        )


def test_frozen_quotient_behavior_rejects_mismatched_step_tier() -> None:
    with pytest.raises(ValueError, match="current_step.coarse_tier"):
        FrozenQuotientBehavior(
            behavior_id="behavior",
            coarse_tier=1,
            supported_fine_tier=0,
            current_step=FrozenQuotientStep(coarse_tier=2, source_cell="source"),
        )


def test_frozen_quotient_behavior_from_step_keeps_tier_direction_explicit() -> None:
    behavior = FrozenQuotientBehavior.from_step(
        behavior_id="behavior",
        coarse_tier=1,
        supported_fine_tier=0,
        source_cell="source",
        action_cell="action",
        target_cell="target",
        version="v1",
    )

    assert behavior.coarse_tier == 1
    assert behavior.supported_fine_tier == 0
    assert behavior.current_step == FrozenQuotientStep(
        coarse_tier=1,
        source_cell="source",
        action_cell="action",
        target_cell="target",
    )
    assert behavior.path_prefix == ("source", "target")
    assert behavior.action_prefix == ("action",)
    assert behavior.version == "v1"
