"""Tests for tensorization config, reports, and import boundaries."""

from __future__ import annotations

import pytest

import state_collapser.training.linearization as linearization
from state_collapser.training import (
    LinearizationConfig,
    LinearizationState,
    NumericBackend,
    TensorDeviceKind,
    build_linearization_report,
)


def test_linearization_mode_values_are_stable() -> None:
    """Lock enum spellings used by benchmark labels and artifact manifests."""

    assert LinearizationState.ABSENT.value == "ABSENT"
    assert LinearizationState.PRESENT_DISABLED.value == "PRESENT_DISABLED"
    assert LinearizationState.PRESENT_ENABLED.value == "PRESENT_ENABLED"
    assert NumericBackend.NONE.value == "NONE"
    assert NumericBackend.NUMPY.value == "NUMPY"
    assert NumericBackend.TORCH.value == "TORCH"
    assert TensorDeviceKind.NONE.value == "NONE"
    assert TensorDeviceKind.CPU.value == "CPU"
    assert TensorDeviceKind.CUDA.value == "CUDA"


def test_config_serializes_and_derives_benchmark_labels() -> None:
    """Require configs to round-trip while preserving derived benchmark labels."""

    config = LinearizationConfig(
        linearization_state=LinearizationState.PRESENT_DISABLED,
        numeric_backend=NumericBackend.NUMPY,
        device_kind=TensorDeviceKind.NONE,
        max_action_count=4,
        strict=True,
    )

    data = config.to_dict()
    rebuilt = LinearizationConfig.from_dict(data)

    assert data["derived_benchmark_label"] == "tensor_available_disabled"
    assert rebuilt == config


def test_config_rejects_inconsistent_modes() -> None:
    """Reject mode combinations that would blur numeric and device boundaries."""

    with pytest.raises(ValueError, match="ABSENT"):
        LinearizationConfig(
            linearization_state=LinearizationState.ABSENT,
            numeric_backend=NumericBackend.NUMPY,
            device_kind=TensorDeviceKind.NONE,
        )

    with pytest.raises(ValueError, match="CUDA"):
        LinearizationConfig(
            linearization_state=LinearizationState.PRESENT_ENABLED,
            numeric_backend=NumericBackend.NUMPY,
            device_kind=TensorDeviceKind.CUDA,
        )

    with pytest.raises(ValueError, match="PRESENT_ENABLED"):
        LinearizationConfig(
            linearization_state=LinearizationState.PRESENT_ENABLED,
            numeric_backend=NumericBackend.NONE,
            device_kind=TensorDeviceKind.NONE,
        )


def test_report_serializes_artifact_safe_mode_data() -> None:
    """Require reports to expose benchmark-safe metadata without tensor records."""

    config = LinearizationConfig(
        linearization_state=LinearizationState.PRESENT_DISABLED,
        numeric_backend=NumericBackend.TORCH,
        device_kind=TensorDeviceKind.CPU,
        max_tower_depth=3,
        max_action_count=5,
    )

    report = build_linearization_report(config=config)
    data = report.to_dict()

    assert data["benchmark_label"] == "tensor_available_disabled"
    assert data["enabled"] is False
    assert "torch_available" in data
    assert "numpy_available" in data
    assert data["conversion_count"] == 0


def test_backend_independent_module_does_not_bind_torch_symbol() -> None:
    """Keep the linearization module free of eager Torch imports."""

    assert "torch" not in vars(linearization)
