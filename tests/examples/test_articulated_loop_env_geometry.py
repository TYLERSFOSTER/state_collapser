from __future__ import annotations

from state_collapser.examples.articulated_loop_env import (
    ArticulatedLoopState,
    brace_target,
    direction_vector,
    endpoint_sum,
)


def test_direction_vector_matches_cardinal_bins() -> None:
    assert direction_vector(0) == (1, 0)
    assert direction_vector(1) == (0, 1)
    assert direction_vector(2) == (-1, 0)
    assert direction_vector(3) == (0, -1)


def test_brace_target_depends_on_brace_mode() -> None:
    assert brace_target(0) == (1, 0)
    assert brace_target(1) == (0, 1)


def test_endpoint_sum_matches_discrete_link_directions() -> None:
    state = ArticulatedLoopState(0, 1, 3, 0, 2)
    assert endpoint_sum(state) == (1, 0)
