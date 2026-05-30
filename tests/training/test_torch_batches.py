"""Tests for the optional Torch tensor boundary."""

from __future__ import annotations

import pytest

from state_collapser.training import (
    LinearizationConfig,
    LinearizationState,
    LinearizedActionSelectionInput,
    LinearizedTrainingTransition,
    NumericBackend,
    TensorDeviceKind,
)
from state_collapser.training.torch import TorchDecisionBatch, TorchTransitionBatch


def _config(device_kind: TensorDeviceKind = TensorDeviceKind.CPU) -> LinearizationConfig:
    """Return an enabled Torch config for decision/transition batch tests."""

    return LinearizationConfig(
        linearization_state=LinearizationState.PRESENT_ENABLED,
        numeric_backend=NumericBackend.TORCH,
        device_kind=device_kind,
        max_action_count=3,
    )


def _record() -> LinearizedActionSelectionInput:
    """Return a fixed-width linearized record with metadata sidecar content."""

    return LinearizedActionSelectionInput(
        observation_features=(1.0, 2.0),
        current_base_state_id=0,
        tower_position_ids=(0, 1),
        tower_depth=2,
        active_tier=0,
        fine_tier=0,
        coarse_tier=1,
        action_mask=(True, False, True),
        action_count=3,
        stage_id=0,
        fiber_id=0,
        frozen_behavior_id=0,
        frozen_behavior_version=0,
        fiber_departure_reason_id=None,
        metadata={"sidecar": "kept"},
    )


@pytest.mark.requires_torch
def test_torch_decision_batch_preserves_masks_and_metadata() -> None:
    """Convert decision records without losing masks or sidecar metadata."""

    torch = pytest.importorskip("torch")

    batch = TorchDecisionBatch.from_linearized([_record()], config=_config())

    assert tuple(batch.observations.shape) == (1, 2)
    assert batch.action_mask.dtype == torch.bool
    assert batch.action_mask.tolist() == [[True, False, True]]
    assert batch.metadata == ({"sidecar": "kept"},)


@pytest.mark.requires_torch
def test_torch_transition_batch_converts_transition_fields() -> None:
    """Convert transition records into tensors and preserve bootstrap fields."""

    pytest.importorskip("torch")

    record = _record()
    transition = LinearizedTrainingTransition(
        source=record,
        target=record,
        chosen_action=2,
        reward=1.5,
        terminated=False,
        truncated=True,
        bootstrap_allowed=False,
        bootstrap_reason_id=1,
        metadata={"transition": "sidecar"},
    )

    batch = TorchTransitionBatch.from_linearized([transition], config=_config())

    assert batch.actions.tolist() == [2]
    assert batch.rewards.tolist() == [1.5]
    assert batch.terminated.tolist() == [False]
    assert batch.truncated.tolist() == [True]
    assert batch.bootstrap_allowed.tolist() == [False]
    assert batch.metadata == ({"transition": "sidecar"},)


@pytest.mark.requires_torch
def test_cuda_config_requires_cuda_availability() -> None:
    """Require CUDA configs to fail explicitly when CUDA is unavailable."""

    torch = pytest.importorskip("torch")

    if torch.cuda.is_available():
        batch = TorchDecisionBatch.from_linearized(
            [_record()],
            config=_config(TensorDeviceKind.CUDA),
        )
        assert batch.observations.device.type == "cuda"
    else:
        with pytest.raises(RuntimeError, match="CUDA"):
            TorchDecisionBatch.from_linearized(
                [_record()],
                config=_config(TensorDeviceKind.CUDA),
            )
