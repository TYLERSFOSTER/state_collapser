"""Tests for the core PrimitiveAction type."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from state_collapser.core.action import PrimitiveAction


def test_action_equality() -> None:
    action_a = PrimitiveAction(payload=("turn", 1), identity="a1", labels=("x",))
    action_b = PrimitiveAction(payload=("turn", 1), identity="a1", labels=("x",))

    assert action_a == action_b


def test_action_inequality() -> None:
    action_a = PrimitiveAction(payload=("turn", 1), identity="a1", labels=("x",))
    action_b = PrimitiveAction(payload=("turn", 2), identity="a2", labels=("y",))

    assert action_a != action_b


def test_action_hash_is_stable_for_equal_instances() -> None:
    action_a = PrimitiveAction(payload=("turn", 1), identity="a1", labels=("x",))
    action_b = PrimitiveAction(payload=("turn", 1), identity="a1", labels=("x",))

    assert hash(action_a) == hash(action_b)


def test_action_is_immutable() -> None:
    action = PrimitiveAction(payload=("turn", 1), identity="a1", labels=("x",))

    with pytest.raises(FrozenInstanceError):
        action.labels = ("z",)
