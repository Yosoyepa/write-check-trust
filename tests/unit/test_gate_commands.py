"""Invocaciones pytest de los gates: el aislamiento property es contractual (TEST-008)."""

from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from tools.wct.gate.runner import REGISTRY
from tools.wct.model import Status


@pytest.fixture
def _green_external(monkeypatch: pytest.MonkeyPatch) -> None:
    """Gates externos sin salir del proceso: herramienta presente, salida exitosa."""

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr("tools.wct.gate.runner.shutil.which", lambda _: "/usr/bin/pytest")
    monkeypatch.setattr("tools.wct.gate.runner.subprocess.run", fake_run)


def _invocation(command: str | None) -> list[str]:
    return (command or "").split()


def _excludes_property(command: list[str]) -> bool:
    """La bandera -m recibe el valor como dos argv: 'not' y 'property'."""
    index = command.index("-m")
    return command[index + 1 : index + 3] == ["not", "property"]


@pytest.mark.usefixtures("_green_external")
def test_gcov_total_excludes_property_tests(tmp_path: Path) -> None:
    """La cobertura total no puede contar líneas cubiertas por property tests."""
    result = REGISTRY["G-COV-TOTAL"](tmp_path)

    command = _invocation(result.command)
    assert result.status is Status.PASS
    assert _excludes_property(command)


@pytest.mark.usefixtures("_green_external")
def test_gtest_excludes_property_tests(tmp_path: Path) -> None:
    """La verificación normal excluye por marker, no por accidente de rutas."""
    result = REGISTRY["G-TEST"](tmp_path)

    command = _invocation(result.command)
    assert result.status is Status.PASS
    assert _excludes_property(command)


@pytest.mark.usefixtures("_green_external")
def test_gprop_runs_property_without_filter(tmp_path: Path) -> None:
    """El gate dedicado ejecuta tests/property sin deselección por marker."""
    result = REGISTRY["G-PROP"](tmp_path)

    command = _invocation(result.command)
    assert result.status is Status.PASS
    assert "tests/property" in command
    assert "-m" not in command
