from __future__ import annotations

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from state_collapser.examples.plate_support_env import (
    PlateSupportState,
    encode_observation,
    ordered_socket_world_positions,
    rotate_local_point,
    socket_world_position,
)


def test_plate_support_state_is_frozen_and_hashable() -> None:
    state = PlateSupportState(2, 2, 0, 1, 1, 1)

    assert isinstance(hash(state), int)

    with pytest.raises(FrozenInstanceError):
        state.x_idx = 3  # type: ignore[misc]


@pytest.mark.parametrize(
    ("theta_idx", "point", "expected"),
    (
        (0, (1, 2), (1, 2)),
        (1, (1, 2), (-2, 1)),
        (2, (1, 2), (-1, -2)),
        (3, (1, 2), (2, -1)),
    ),
)
def test_rotate_local_point_matches_spec(
    theta_idx: int,
    point: tuple[int, int],
    expected: tuple[int, int],
) -> None:
    assert rotate_local_point(theta_idx, point) == expected


def test_socket_world_position_combines_translation_and_rotation() -> None:
    center = (2, 3)
    local_socket = (-1, 0)

    assert socket_world_position(center, 0, local_socket) == (1, 3)
    assert socket_world_position(center, 1, local_socket) == (2, 2)
    assert socket_world_position(center, 2, local_socket) == (3, 3)
    assert socket_world_position(center, 3, local_socket) == (2, 4)


def test_ordered_socket_world_positions_align_with_left_mid_right() -> None:
    state = PlateSupportState(2, 3, 1, 1, 1, 1)

    assert ordered_socket_world_positions(state) == ((2, 2), (2, 3), (2, 4))


def test_encode_observation_returns_int64_shape_6() -> None:
    obs = encode_observation(PlateSupportState(2, 3, 1, 2, 1, 2))

    assert isinstance(obs, np.ndarray)
    assert obs.shape == (6,)
    assert obs.dtype == np.int64
    assert obs.tolist() == [2, 3, 1, 2, 1, 2]
