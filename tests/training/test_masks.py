"""Focused tests for training action-mask helpers."""

from __future__ import annotations

import pytest

from state_collapser.training import action_is_legal, legal_actions, mask_from_info


def test_mask_from_info_returns_none_when_missing_or_none() -> None:
    assert mask_from_info({}) is None
    assert mask_from_info({"action_mask": None}) is None


def test_mask_from_info_normalizes_iterables_without_truth_value_checks() -> None:
    assert mask_from_info({"action_mask": [1, 0, True, False]}) == (
        True,
        False,
        True,
        False,
    )
    assert mask_from_info({"action_mask": (value for value in (0, 1))}) == (
        False,
        True,
    )


def test_mask_from_info_rejects_non_iterable_and_string_masks() -> None:
    with pytest.raises(ValueError):
        mask_from_info({"action_mask": 1})
    with pytest.raises(ValueError):
        mask_from_info({"action_mask": "101"})


def test_legal_actions_treats_none_as_all_actions_and_empty_as_none() -> None:
    assert legal_actions(None, 4) == (0, 1, 2, 3)
    assert legal_actions((), 4) == ()
    assert legal_actions((True, False, True), 4) == (0, 2)
    assert legal_actions((True, True, True), 2) == (0, 1)


def test_legal_actions_rejects_negative_action_count() -> None:
    with pytest.raises(ValueError):
        legal_actions(None, -1)


def test_action_is_legal_respects_bounds_masks_and_types() -> None:
    assert action_is_legal(3, None)
    assert not action_is_legal(-1, None)
    assert action_is_legal(0, (True, False))
    assert not action_is_legal(1, (True, False))
    assert not action_is_legal(2, (True, False))
    assert not action_is_legal(True, (True, False))
    assert not action_is_legal(1.0, (True, False))  # type: ignore[arg-type]
