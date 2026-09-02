"""Gates de comando externo: la invocación nace de thresholds.yaml (PR-B, ADR-B-01)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import subprocess

import pytest
import yaml

from tools.wct.gate.runner import REGISTRY
from tools.wct.model import Status

REPO = Path(__file__).resolve().parents[2]

# Captura PRE (SPEC-B-01 paso 0.3, ee17288): con el YAML vigente los comandos
# cableados deben seguir siendo byte-idénticos. La fuente cambia; el comando, no.
WIRED_LITERALS = {
    "G-CRAP": "crap4py src --lcov build/coverage/lcov.info --max-crap 6",
    "G-COV-DIFF": (
        "diff-cover build/coverage/lcov.info --compare-branch origin/main "
        "--fail-under 90 --include-untracked"
    ),
    "G-DEAD": "vulture src tools/wct --min-confidence 80",
    "G-CC": "xenon --max-absolute B --max-modules A --max-average A src",
}


def _fake_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """Herramientas presentes y corridas exitosas sin salir del proceso."""

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr(
        "tools.wct.gate.runner.shutil.which", lambda executable: f"/usr/bin/{executable}"
    )
    monkeypatch.setattr("tools.wct.gate.runner.subprocess.run", fake_run)
    monkeypatch.setattr("tools.wct.gate.runner.remote_base", lambda _root: "origin/main")


def _declare(root: Path, key: str, value: object) -> None:
    """Reescribe una clave de thresholds.yaml del fixture."""
    path = root / "governance/thresholds.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    section, _, name = key.partition(".")
    document[section][name] = value
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")


def _undeclare(root: Path, key: str) -> None:
    """Elimina una clave (o toda su sección si no hay subclave) del YAML."""
    path = root / "governance/thresholds.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    section, _, name = key.partition(".")
    if name:
        del document[section][name]
    else:
        del document[section]
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")


def test_gate_commands_match_current_literals(monkeypatch: pytest.MonkeyPatch) -> None:
    """Con el YAML real del repo, cada comando cableado es el literal de antes."""
    _fake_tools(monkeypatch)

    commands = {gate_id: REGISTRY[gate_id](REPO) for gate_id in WIRED_LITERALS}

    for gate_id, literal in WIRED_LITERALS.items():
        assert commands[gate_id].status is Status.PASS, gate_id
        assert commands[gate_id].command == literal, gate_id


def test_yaml_change_flows_into_command(
    project_factory: Callable[..., Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """crap.changed_max declarado en 9 llega como --max-crap 9: el YAML manda."""
    _fake_tools(monkeypatch)
    root = project_factory()
    _declare(root, "crap.changed_max", 9)

    result = REGISTRY["G-CRAP"](root)

    assert result.status is Status.PASS
    assert result.command == "crap4py src --lcov build/coverage/lcov.info --max-crap 9"
    assert "6" not in (result.command or "")


@pytest.mark.parametrize(
    ("gate_id", "key"),
    [
        ("G-CRAP", "crap.changed_max"),
        ("G-COV-DIFF", "coverage.diff_min"),
        ("G-DEAD", "dead_code.vulture_min_confidence"),
        ("G-CC", "complexity"),
    ],
)
def test_missing_key_fails_naming_it(
    project_factory: Callable[..., Path], monkeypatch: pytest.MonkeyPatch, gate_id: str, key: str
) -> None:
    """Clave ausente → FAIL nombrándola; nunca corre con un default silencioso."""
    _fake_tools(monkeypatch)
    root = project_factory()
    _undeclare(root, key)

    result = REGISTRY[gate_id](root)

    assert result.status is Status.FAIL, gate_id
    assert key in result.summary, gate_id


def test_missing_tool_keeps_optional_contract(
    project_factory: Callable[..., Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """El cableado preserva qué es obligatorio: G-DEAD ERROR; G-CRAP/G-CC SKIP."""
    monkeypatch.setattr("tools.wct.gate.runner.shutil.which", lambda _executable: None)
    root = project_factory()

    verdicts = {gate_id: REGISTRY[gate_id](root) for gate_id in ("G-DEAD", "G-CRAP", "G-CC")}

    assert verdicts["G-DEAD"].status is Status.ERROR
    assert verdicts["G-CRAP"].status is Status.SKIP
    assert verdicts["G-CC"].status is Status.SKIP


def test_unreadable_config_fails_naming_the_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sin governance/ legible el gate es FAIL nombrando la clave, no un crash."""
    _fake_tools(monkeypatch)

    result = REGISTRY["G-CRAP"](tmp_path)

    assert result.status is Status.FAIL
    assert "crap.changed_max" in result.summary
