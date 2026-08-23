from collections.abc import Callable
from pathlib import Path
import subprocess

import pytest

from tools.wct.gate.runner import REGISTRY
from tools.wct.model import Status
from tools.wct.ratchet.measure import docstring_coverage, interrogate_percent

SAMPLE_OUTPUT = "RESULT: FAILED (minimum: 80.0%, actual: 34.8%)\n"


def test_percent_parser_reads_actual() -> None:
    assert interrogate_percent(SAMPLE_OUTPUT) == 34.8
    assert interrogate_percent("sin coincidencia") is None


def test_coverage_none_without_interrogate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("tools.wct.ratchet.measure.shutil.which", lambda _: None)

    assert docstring_coverage(tmp_path) is None


def test_coverage_parsed_from_interrogate_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr("tools.wct.ratchet.measure.shutil.which", lambda _: "/usr/bin/interrogate")
    monkeypatch.setattr(
        "tools.wct.ratchet.measure.subprocess.run",
        lambda _cmd, **_kw: subprocess.CompletedProcess(_cmd, 0, stdout=SAMPLE_OUTPUT, stderr=""),
    )

    assert docstring_coverage(tmp_path) == 34.8


def test_gate_reads_floor_from_ratchet_baseline(
    project_factory: Callable[..., Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, object] = {}

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, stdout="RESULT: ok", stderr="")

    root = project_factory()
    monkeypatch.setattr("tools.wct.gate.runner.shutil.which", lambda _: "/usr/bin/interrogate")
    monkeypatch.setattr("tools.wct.gate.runner.subprocess.run", fake_run)

    result = REGISTRY["G-DOC"](root)

    assert result.status is Status.PASS
    command = captured["command"]
    assert command[command.index("--fail-under") + 1] == "34"


def test_gate_fails_on_returncode(
    project_factory: Callable[..., Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = project_factory()
    monkeypatch.setattr("tools.wct.gate.runner.shutil.which", lambda _: "/usr/bin/interrogate")
    monkeypatch.setattr(
        "tools.wct.gate.runner.subprocess.run",
        lambda command, **_kw: subprocess.CompletedProcess(
            command, 1, stdout=SAMPLE_OUTPUT, stderr=""
        ),
    )

    result = REGISTRY["G-DOC"](root)

    assert result.status is Status.FAIL
    assert "34.8" in result.summary


def test_gate_skips_when_interrogate_missing(
    project_factory: Callable[..., Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = project_factory()
    monkeypatch.setattr("tools.wct.gate.runner.shutil.which", lambda _: None)

    result = REGISTRY["G-DOC"](root)

    assert result.status is Status.SKIP
