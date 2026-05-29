"""Tiny Torch smoke model for the tensor boundary."""

from __future__ import annotations

import pytest

from state_collapser.training import (
    LinearizationConfig,
    LinearizationState,
    LinearizedActionSelectionInput,
    NumericBackend,
    TensorDeviceKind,
)
from state_collapser.training.torch import TorchDecisionBatch, action_decision_from_logits


@pytest.mark.requires_torch
def test_tiny_torch_model_outputs_action_decision_compatible_result() -> None:
    torch = pytest.importorskip("torch")

    class _TinyPolicy(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.linear = torch.nn.Linear(2, 3)

        def forward(self, batch: TorchDecisionBatch) -> object:
            return self.linear(batch.observations)

    config = LinearizationConfig(
        linearization_state=LinearizationState.PRESENT_ENABLED,
        numeric_backend=NumericBackend.TORCH,
        device_kind=TensorDeviceKind.CPU,
        max_action_count=3,
    )
    record = LinearizedActionSelectionInput(
        observation_features=(1.0, 0.5),
        current_base_state_id=0,
        tower_position_ids=(0,),
        tower_depth=1,
        active_tier=0,
        fine_tier=0,
        coarse_tier=1,
        action_mask=(False, True, False),
        action_count=3,
        stage_id=0,
        fiber_id=0,
        frozen_behavior_id=0,
        frozen_behavior_version=0,
        fiber_departure_reason_id=None,
        metadata={},
    )

    batch = TorchDecisionBatch.from_linearized([record], config=config)
    model = _TinyPolicy()
    logits = model(batch)
    decision = action_decision_from_logits(logits, batch)

    assert decision.chosen_action == 1
