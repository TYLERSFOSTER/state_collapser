"""Tests for shared fiber-stage context vocabulary."""

from __future__ import annotations

import pytest

from state_collapser.training import FiberStageContext


def test_fiber_stage_context_accepts_adjacent_tiers() -> None:
    context = FiberStageContext(
        stage_id="stage",
        fiber_id="fiber",
        fine_tier=0,
        coarse_tier=1,
        frozen_behavior_id="frozen",
        frozen_behavior_version=3,
    )

    assert context.stage_id == "stage"
    assert context.fiber_id == "fiber"
    assert context.fine_tier == 0
    assert context.coarse_tier == 1
    assert context.frozen_behavior_id == "frozen"
    assert context.frozen_behavior_version == 3


def test_fiber_stage_context_rejects_non_adjacent_tiers() -> None:
    with pytest.raises(ValueError, match="coarse_tier == fine_tier"):
        FiberStageContext(
            stage_id="stage",
            fiber_id="fiber",
            fine_tier=0,
            coarse_tier=2,
            frozen_behavior_id="frozen",
            frozen_behavior_version=0,
        )
