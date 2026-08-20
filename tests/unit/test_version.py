"""Tests for the single-source version convention (B6)."""

from __future__ import annotations

import importlib
import importlib.metadata
from pathlib import Path
import tomllib

import pytest

import example
from example import __version__ as example_version
import tools.wct
from tools.wct import __version__ as wct_version

REPO = Path(__file__).parents[2]


def _pyproject_version() -> str:
    document = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    return str(document["project"]["version"])


def test_package_versions_derive_from_pyproject() -> None:
    """A release bump in pyproject.toml must reach every __version__.

    Two sources drifted once and CI caught it only by luck.
    """
    assert wct_version == _pyproject_version()
    assert example_version == _pyproject_version()


def test_uninstalled_package_falls_back_to_local_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An uninstalled checkout reports 0.0.0+local instead of crashing."""

    def _missing(name: str) -> str:
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", _missing)
    try:
        assert importlib.reload(example).__version__ == "0.0.0+local"
        assert importlib.reload(tools.wct).__version__ == "0.0.0+local"
    finally:
        monkeypatch.undo()
        importlib.reload(example)
        importlib.reload(tools.wct)
