"""Tests for the core State type."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from state_collapser.core.state import State


def test_state_equality_for_identical_payloads() -> None:
    state_a = State(payload=("region", 1), identity="s1")
    state_b = State(payload=("region", 1), identity="s1")

    assert state_a == state_b


def test_state_inequality_for_distinct_payloads() -> None:
    state_a = State(payload=("region", 1), identity="s1")
    state_b = State(payload=("region", 2), identity="s2")

    assert state_a != state_b


def test_state_hash_is_stable_for_equal_instances() -> None:
    state_a = State(payload=("region", 1), identity="s1")
    state_b = State(payload=("region", 1), identity="s1")

    assert hash(state_a) == hash(state_b)


def test_state_is_immutable() -> None:
    state = State(payload=("region", 1), identity="s1")

    with pytest.raises(FrozenInstanceError):
        state.payload = ("region", 9)
