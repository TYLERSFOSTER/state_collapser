"""Continuation and bootstrap semantics for training transitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BootstrapSemantics:
    """Configuration for target bootstrap behavior."""

    bootstrap_on_truncation: bool = True


def default_bootstrap_allowed(
    *,
    terminated: bool,
    truncated: bool,
    semantics: BootstrapSemantics,
) -> bool:
    """Return whether a transition should bootstrap under default semantics."""

    if terminated:
        return False
    if truncated:
        return semantics.bootstrap_on_truncation
    return True


def default_bootstrap_reason(
    *,
    terminated: bool,
    truncated: bool,
    semantics: BootstrapSemantics,
) -> str:
    """Return the canonical diagnostic reason for default bootstrap behavior."""

    if terminated:
        return "terminated"
    if truncated and semantics.bootstrap_on_truncation:
        return "truncated_bootstrap"
    if truncated:
        return "truncated_no_bootstrap"
    return "continuing"


__all__ = [
    "BootstrapSemantics",
    "default_bootstrap_allowed",
    "default_bootstrap_reason",
]
