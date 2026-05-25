"""Focused tests for training continuation semantics."""

from state_collapser.training import (
    BootstrapSemantics,
    default_bootstrap_allowed,
    default_bootstrap_reason,
)


def test_default_bootstrap_semantics_terminal_never_bootstraps() -> None:
    semantics = BootstrapSemantics()

    assert not default_bootstrap_allowed(
        terminated=True,
        truncated=False,
        semantics=semantics,
    )
    assert (
        default_bootstrap_reason(terminated=True, truncated=False, semantics=semantics)
        == "terminated"
    )


def test_default_bootstrap_semantics_truncation_bootstraps_by_default() -> None:
    semantics = BootstrapSemantics()

    assert default_bootstrap_allowed(
        terminated=False,
        truncated=True,
        semantics=semantics,
    )
    assert (
        default_bootstrap_reason(terminated=False, truncated=True, semantics=semantics)
        == "truncated_bootstrap"
    )


def test_default_bootstrap_semantics_truncation_can_disable_bootstrap() -> None:
    semantics = BootstrapSemantics(bootstrap_on_truncation=False)

    assert not default_bootstrap_allowed(
        terminated=False,
        truncated=True,
        semantics=semantics,
    )
    assert (
        default_bootstrap_reason(terminated=False, truncated=True, semantics=semantics)
        == "truncated_no_bootstrap"
    )


def test_default_bootstrap_semantics_continuing_transition_bootstraps() -> None:
    semantics = BootstrapSemantics()

    assert default_bootstrap_allowed(
        terminated=False,
        truncated=False,
        semantics=semantics,
    )
    assert (
        default_bootstrap_reason(terminated=False, truncated=False, semantics=semantics)
        == "continuing"
    )
