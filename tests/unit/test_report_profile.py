"""Perfil de capacidades derivado del constructor del gate (ADR-D-01, O-006).

La fuente única es el sitio de construcción: dynamic/external derivan las
tools del ejecutable que ya resuelven; el scope se declara donde el gate se
registra. Estos tests fijan que ningún gate "de herramienta" quede sin
metadata y que el report agregue presencia real, scope y tiers.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.wct.gate.capabilities import gate_info
from tools.wct.gate.runner import REGISTRY, TIERS
from tools.wct.model import GateResult, Status
from tools.wct.report.overview import overview
from tools.wct.report.render import text_report

REPO = Path(__file__).resolve().parents[2]

# Gates que ejecutan un proceso externo y el ejecutable que cada uno resuelve
# (paso 0: verificado contra el comando que arma cada constructor en
# tools/wct/gate/runner.py y los builders de tools/wct/gate/checks.py).
EXTERNAL_TOOLS = {
    "G-LINT": ("ruff",),
    "G-FMT": ("ruff",),
    "G-TYPE": ("mypy",),
    "G-TEST": ("pytest",),
    "G-ARCH": ("lint-imports",),
    "G-DEPS": ("deptry",),
    "G-DEAD": ("vulture",),
    "G-SAST-BANDIT": ("bandit",),
    "G-SAST-SEMGREP": ("semgrep",),
    "G-AUDIT": ("uv", "pip-audit"),
    "G-CRAP": ("crap4py",),
    "G-CC": ("xenon",),
    "G-COV-TOTAL": ("pytest",),
    "G-COV-DIFF": ("diff-cover",),
    "G-DOC": ("interrogate",),
    "G-SECRET": ("detect-secrets",),
    "G-PROP": ("pytest",),
    "G-TEST-RANDOM": ("pytest",),
    "G-DRY-TOK": ("jscpd",),
    "G-SBOM": ("cyclonedx-py",),
    "G-COMMIT-MSG": ("cz",),
    "G-MUT": ("mutmut",),
    "G-ACCEPT-MUT": ("wct",),
    "G-REDTEAM": ("wct",),
    "G-HOOKS-WIRED": ("wct",),
    # Aliases: heredan la capacidad del gate que envuelven.
    "G-CVE": ("uv", "pip-audit"),
    "G-SAST": ("bandit",),
    "G-IMPORT-ORDER": ("ruff",),
    "G-TEST-FAST": ("pytest",),
}

# Scope verificado en el paso 0 contra el comando o analizador real de cada
# gate: args de rutas del comando, o las policy.paths que el motor recorre.
DECLARED_SCOPES = {
    "G-LINT": (".",),
    "G-FMT": (".",),
    "G-TYPE": ("tools/wct", "src"),
    "G-TEST": ("tests/unit", "tests/integration"),
    "G-ARCH": ("src/example",),
    "G-DEPS": ("src", "tools"),
    "G-DEAD": ("src", "tools/wct"),
    "G-SAST-BANDIT": ("src",),
    "G-SAST-SEMGREP": (".",),
    "G-SUPPRESS": ("src", "tests"),
    "G-DEBT": ("src", "tests"),
    "G-ARCHMETRICS": ("src/example",),
    "G-DRY": ("src",),
    "G-DRY-TPL": ("src", "tools"),
    "G-DRY-TOK": ("src", "tools"),
    "G-INTROVERT": ("tests",),
    "G-MUT-SITES": ("src",),
    "G-MUT": ("src/example",),
    "G-ACCEPT": ("features",),
    "G-SIZE": ("src", "tools"),
    "G-COGNITIVE": ("src",),
    "G-LCOM": ("src", "tools"),
    "G-WIRE": ("src/example/domain", "src/example/application"),
    "G-CRAP": ("src",),
    "G-CC": ("src",),
    "G-COV-TOTAL": ("src", "tools/wct"),
    "G-DOC": ("src",),
    "G-SECRET": (
        "src",
        "tools",
        "governance",
        ".claude",
        "skills",
        "plugins",
        ".github",
        "pyproject.toml",
        ".pre-commit-config.yaml",
    ),
    "G-PROP": ("tests/property",),
    "G-TEST-RANDOM": ("tests",),
}


def _entries() -> dict[str, dict[str, object]]:
    """Sección capabilities indexada por gate, desde el overview real."""
    section = overview(REPO)["capabilities"]
    return {str(item["gate"]): item for item in section}


def _results(statuses: list[Status]) -> list[GateResult]:
    return [
        GateResult(f"G-{index:02d}", status, "resumen de prueba")
        for index, status in enumerate(statuses)
    ]


def test_every_gate_with_external_tool_exposes_it() -> None:
    """Ningún gate que corre un ejecutable queda sin metadata (DoD-F1.1)."""
    for gate_id, expected in EXTERNAL_TOOLS.items():
        info = gate_info(REGISTRY[gate_id])
        assert info is not None, f"{gate_id} corre un ejecutable y no declara tools"
        assert info.tools == expected, gate_id


def test_gates_without_external_tool_expose_no_tools() -> None:
    """Los gates puros no declaran herramientas: el perfil no inventa capacidad."""
    tool_gates = set(EXTERNAL_TOOLS)
    for gate_id, gate in REGISTRY.items():
        if gate_id in tool_gates:
            continue
        info = gate_info(gate)
        assert info is None or info.tools == (), gate_id


@pytest.mark.parametrize(
    ("gate_id", "tool"),
    [
        ("G-DEAD", "vulture"),
        ("G-SAST-SEMGREP", "semgrep"),
        ("G-DOC", "interrogate"),
    ],
    ids=["F-DEAD", "F-SEMGREP", "F-DOC"],
)
def test_capabilities_report_tool_presence(
    gate_id: str, tool: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Present refleja which en tiempo de report, y el gate sigue en la sección."""
    monkeypatch.setattr(
        "tools.wct.report.overview.shutil.which", lambda executable: f"/usr/bin/{executable}"
    )
    assert _entries()[gate_id] == {
        "gate": gate_id,
        "tools": [tool],
        "present": True,
        "scope": list(DECLARED_SCOPES[gate_id]),
        "tiers": [tier for tier, gates in TIERS.items() if gate_id in gates],
    }

    monkeypatch.setattr("tools.wct.report.overview.shutil.which", lambda _executable: None)
    absent = _entries()[gate_id]
    assert absent["present"] is False
    assert absent["tools"] == [tool]


def test_capabilities_presence_with_real_which() -> None:
    """Sin falsear nada, pytest está presente: lo está ejecutando este test."""
    assert _entries()["G-TEST"]["present"] is True


def test_presence_requires_every_tool_of_the_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """G-AUDIT necesita uv Y pip-audit: una sola ausente basta para present=false."""
    monkeypatch.setattr(
        "tools.wct.report.overview.shutil.which",
        lambda executable: "/usr/bin/uv" if executable == "uv" else None,
    )
    assert _entries()["G-AUDIT"]["present"] is False


def test_gates_without_tool_are_present_by_definition() -> None:
    """Gates sin herramienta externa: tools vacías y present=true."""
    entry = _entries()["G-INTROVERT"]
    assert entry["tools"] == []
    assert entry["present"] is True


def test_capabilities_declare_scope() -> None:
    """El scope se lee del constructor vía gate_info: no hay tabla duplicada."""
    for gate_id, expected in DECLARED_SCOPES.items():
        info = gate_info(REGISTRY[gate_id])
        assert info is not None, f"{gate_id} escanea rutas y no declara scope"
        assert info.scope == expected, gate_id
        assert _entries()[gate_id]["scope"] == list(expected), gate_id


def test_full_summary_declares_unverified_capabilities() -> None:
    """Con SKIPs, línea tras el resumen que declara la capacidad no verificada."""
    report = text_report(_results([Status.PASS, Status.SKIP, Status.FAIL]))

    lines = report.splitlines()
    summary_index = next(index for index, line in enumerate(lines) if line.endswith("FAIL/ERROR"))
    assert lines[summary_index + 1] == (
        "capacidades no verificadas: 1 — wct report muestra herramientas ausentes"
    )


def test_summary_without_skips_is_byte_identical() -> None:
    """Regresión: sin SKIPs la salida es byte-idéntica a la previa a PR-D."""
    report = text_report(_results([Status.PASS, Status.PASS, Status.PASS]))

    assert report == (
        "GATE  STATUS  MS      SUMMARY\n"
        "G-00  PASS    0       resumen de prueba\n"
        "G-01  PASS    0       resumen de prueba\n"
        "G-02  PASS    0       resumen de prueba\n"
        "\n"
        "3 gates: 3 PASS · 0 SKIP · 0 FAIL/ERROR"
    )


def test_overview_capabilities_json_shape() -> None:
    """Sección JSON-serializable, forma documentada, todo gate en orden estable."""
    document = json.loads(json.dumps(overview(REPO), ensure_ascii=False))

    capabilities = document["capabilities"]
    assert [item["gate"] for item in capabilities] == list(REGISTRY)
    for item in capabilities:
        assert set(item) == {"gate", "tools", "present", "scope", "tiers"}
        assert isinstance(item["tools"], list)
        assert isinstance(item["present"], bool)
        assert isinstance(item["scope"], list)
        expected_tiers = [tier for tier, gates in TIERS.items() if item["gate"] in gates]
        assert item["tiers"] == expected_tiers, item["gate"]
