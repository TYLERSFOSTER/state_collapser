"""Tests for the toy Gymnasium-style adapter."""

from __future__ import annotations

from state_collapser.adapters.gymnasium import RobotConstraintRuntimeAdapter
from state_collapser.core.action import PrimitiveAction


def test_gymnasium_style_reset_output() -> None:
    adapter = RobotConstraintRuntimeAdapter()

    observation, info = adapter.reset()

    assert observation is not None
    assert "runtime_snapshot" in info


def test_gymnasium_style_step_output() -> None:
    adapter = RobotConstraintRuntimeAdapter()
    adapter.reset()

    observation, reward, terminated, truncated, info = adapter.step(
        PrimitiveAction(payload=("move", "right"), identity="action:right")
    )

    assert observation is not None
    assert reward == 1.0
    assert terminated is False
    assert truncated is False
    assert "runtime_snapshot" in info


def test_preservation_of_runtime_metadata_in_adapter_visible_structures() -> None:
    adapter = RobotConstraintRuntimeAdapter()
    _, info = adapter.reset()

    snapshot = info["runtime_snapshot"]

    assert snapshot.current_base_state is not None
    assert snapshot.explored_graph.current_path()
