import json
from pathlib import Path
import subprocess

import pytest

from tools.wct.gate.runner import REGISTRY
from tools.wct.model import Status

REPO = Path(__file__).resolve().parents[2]


def test_gate_makes_jscpd_fail_on_clones(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Sin --exit-code, jscpd sale 0 aunque encuentre clones: el gate sería vacío."""

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 1, stdout="Found 2 clones.", stderr="")

    monkeypatch.setattr("tools.wct.gate.runner.shutil.which", lambda _: "/usr/bin/jscpd")
    monkeypatch.setattr("tools.wct.gate.runner.subprocess.run", fake_run)

    result = REGISTRY["G-DRY-TOK"](tmp_path)
    config = json.loads((REPO / ".jscpd.json").read_text(encoding="utf-8"))

    assert result.status is Status.FAIL
    assert "--exit-code" in result.command.split()
    assert result.command.split()[result.command.split().index("--exit-code") + 1] == "1"
    assert config["min-tokens"] >= 70
    assert 0 < config["threshold"] <= 5


def test_gate_passes_when_clean(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout="Found 0 clones.", stderr="")

    monkeypatch.setattr("tools.wct.gate.runner.shutil.which", lambda _: "/usr/bin/jscpd")
    monkeypatch.setattr("tools.wct.gate.runner.subprocess.run", fake_run)

    result = REGISTRY["G-DRY-TOK"](tmp_path)

    assert result.status is Status.PASS
