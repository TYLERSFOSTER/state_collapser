"""Tests for quotient reward aggregation."""

from __future__ import annotations

from state_collapser.core.action import PrimitiveAction
from state_collapser.core.edges import BaseEdge
from state_collapser.core.rewards import summarize_quotient_rewards
from state_collapser.core.state import State


def test_quotient_mean_reward_computation() -> None:
    summary = summarize_quotient_rewards((1.0, 3.0, 5.0))

    assert summary.mean_reward == 3.0


def test_exclusion_of_internal_collapsed_edges() -> None:
    state_a = State(payload=("a",), identity="s1")
    state_b = State(payload=("b",), identity="s2")
    state_c = State(payload=("c",), identity="s3")
    action = PrimitiveAction(payload=("step",), identity="a1")
    internal_edge = BaseEdge(source=state_a, action=action, target=state_b, labels=("internal",))
    boundary_edge = BaseEdge(source=state_b, action=action, target=state_c, labels=("boundary",))
    reward_by_edge = {
        internal_edge: 9.0,
        boundary_edge: 3.0,
    }

    boundary_contributors = tuple(
        reward for edge, reward in reward_by_edge.items() if "boundary" in edge.labels
    )
    summary = summarize_quotient_rewards(boundary_contributors)

    assert summary.contributing_rewards == (3.0,)
    assert 9.0 not in summary.contributing_rewards


def test_correct_use_of_boundary_crossing_contributors() -> None:
    summary = summarize_quotient_rewards((2.0, 4.0))

    assert summary.contributing_rewards == (2.0, 4.0)
    assert summary.mean_reward == 3.0
