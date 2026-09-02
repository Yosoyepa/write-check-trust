"""G-COV-TOTAL aplica el baseline de coverage-total como piso (PR-A2, ADR-A2-01)."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from tools.wct.gate.runner import REGISTRY
from tools.wct.model import Status

BASELINE_PATH = "governance/baselines/coverage-total.json"


def _write_baseline(root: Path, value: float) -> None:
    """Baseline mínima: el gate solo consume el campo value."""
    target = root / BASELINE_PATH
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps({"value": value}), encoding="utf-8")


def _patch_run(monkeypatch: pytest.MonkeyPatch, returncode: int, stdout: str) -> None:
    """Herramienta pytest presente y corrida falsa con el exit code dado."""

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr="")

    monkeypatch.setattr("tools.wct.gate.runner.shutil.which", lambda _: "/usr/bin/pytest")
    monkeypatch.setattr("tools.wct.gate.runner.subprocess.run", fake_run)


def test_command_includes_fail_under_from_baseline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """El piso sale del baseline registrado: --cov-fail-under sobre medición fresca."""
    _write_baseline(tmp_path, 85.0)
    _patch_run(monkeypatch, 0, "Required test coverage of 85% reached.")

    result = REGISTRY["G-COV-TOTAL"](tmp_path)

    command = (result.command or "").split()
    assert command[command.index("--cov-fail-under") + 1] == "85.0"
    marker = command.index("-m")
    assert command[marker + 1 : marker + 3] == ["not", "property"]


def test_missing_baseline_fails_loudly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Sin baseline el gate es FAIL nombrando la ruta: nunca sin piso en silencio."""
    _patch_run(monkeypatch, 0, "ok")

    result = REGISTRY["G-COV-TOTAL"](tmp_path)

    assert result.status is Status.FAIL
    assert BASELINE_PATH in result.summary


def test_gate_passes_at_floor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Corrida exitosa con el piso aplicado: PASS."""
    _write_baseline(tmp_path, 85.0)
    _patch_run(monkeypatch, 0, "Required test coverage of 85% reached.")

    result = REGISTRY["G-COV-TOTAL"](tmp_path)

    assert result.status is Status.PASS


def test_gate_fails_below_floor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Total 84 bajo piso 85: pytest-cov sale 1 y el veredicto del gate bloquea."""
    _write_baseline(tmp_path, 85.0)
    _patch_run(
        monkeypatch,
        1,
        "FAIL Required test coverage of 85% not reached. Total coverage: 84.30%",
    )

    result = REGISTRY["G-COV-TOTAL"](tmp_path)

    assert result.status is Status.FAIL
