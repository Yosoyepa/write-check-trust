"""CLI behavior of `wct integrity check` on missing protected paths."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import subprocess

import pytest

from tools.wct.cli import main
from tools.wct.integrity.engine import write_lock


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def test_integrity_check_prints_warning_and_exits_zero_for_untracked_absence(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    project_factory: Callable[..., Path],
) -> None:
    """Locally-installed untracked paths absent in a clean CI runner warn.

    A warning, not a permanent failure.
    """
    root = project_factory()
    local = root / ".claude" / "settings.json"
    local.parent.mkdir(parents=True)
    local.write_text("{}", encoding="utf-8")
    _git(root, "init")
    _git(root, "add", "governance/policy.yaml")
    write_lock(root)
    local.unlink()
    monkeypatch.setenv("WCT_PROJECT_ROOT", str(root))

    assert main(["integrity", "check"]) == 0

    captured = capsys.readouterr()
    assert "aviso: ausente no versionado (omitido): .claude/settings.json" in captured.out


def test_integrity_check_fails_for_tracked_absence(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    project_factory: Callable[..., Path],
) -> None:
    """A versioned protected file deleted from disk keeps blocking the gate."""
    root = project_factory()
    _git(root, "init")
    _git(root, "add", "governance/baselines/suppressions.json")
    write_lock(root)
    (root / "governance/baselines/suppressions.json").unlink()
    monkeypatch.setenv("WCT_PROJECT_ROOT", str(root))

    assert main(["integrity", "check"]) == 1

    captured = capsys.readouterr()
    assert "eliminado protegido: governance/baselines/suppressions.json" in captured.out
