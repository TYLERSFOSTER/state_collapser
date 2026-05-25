"""Package smoke tests."""

from __future__ import annotations

import importlib.metadata
import tomllib
from pathlib import Path

import state_collapser


def test_package_exposes_version() -> None:
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text())
    assert state_collapser.__version__ == pyproject["project"]["version"]


def test_distribution_metadata_version_matches_package_version() -> None:
    assert importlib.metadata.version("state-collapser") == state_collapser.__version__


def test_pyproject_declares_gymnasium_and_torch_optional_dependencies() -> None:
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text())
    optional_dependencies = pyproject["project"]["optional-dependencies"]

    assert "gymnasium>=1.0.0" in optional_dependencies["rl"]
    assert "torch>=2.4.0" in optional_dependencies["ml"]
