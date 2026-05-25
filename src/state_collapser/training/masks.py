"""Action-mask helpers for training-facing code."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


def mask_from_info(info: Mapping[str, object]) -> tuple[bool, ...] | None:
    """Normalize ``info["action_mask"]`` into the package mask shape."""

    if "action_mask" not in info:
        return None
    raw_mask = info["action_mask"]
    if raw_mask is None:
        return None
    if isinstance(raw_mask, str | bytes):
        raise ValueError("action_mask must be an iterable of bool-like values.")
    if not isinstance(raw_mask, Iterable):
        raise ValueError("action_mask must be an iterable of bool-like values.")
    return tuple(bool(item) for item in raw_mask)


def legal_actions(mask: tuple[bool, ...] | None, action_count: int) -> tuple[int, ...]:
    """Return action indices allowed by ``mask`` under a fixed action count."""

    if action_count < 0:
        raise ValueError("action_count must be non-negative.")
    if mask is None:
        return tuple(range(action_count))
    return tuple(action for action, allowed in enumerate(mask[:action_count]) if allowed)


def action_is_legal(action: int, mask: tuple[bool, ...] | None) -> bool:
    """Return whether ``action`` is permitted by ``mask``."""

    if isinstance(action, bool) or not isinstance(action, int):
        return False
    if action < 0:
        return False
    if mask is None:
        return True
    return action < len(mask) and mask[action]


__all__ = ["action_is_legal", "legal_actions", "mask_from_info"]
