"""Arnés gate-engine del red team: builders + motor productivo + despachador.

Cada caso siembra su defecto en un tmpdir aislado y el MOTOR productivo que su
gate usa debe cazarlo (ADR-C-01 §1/§5). La aserción traza al reporte del motor,
no al andamiaje del despachador.
"""

from __future__ import annotations

from collections.abc import Callable
import importlib
from pathlib import Path
import shutil
import sys
import types
from typing import Any

import pytest
import yaml

from tools.wct.gate.runner import REGISTRY
from tools.wct.model import GateResult, Status
from tools.wct.selftest import redteam
from tools.wct.selftest.fixtures_engine import BUILDERS

REPOSITORY = Path(__file__).resolve().parents[2]
ENGINE_CASES = {
    str(case["id"]): case
    for case in yaml.safe_load(
        (REPOSITORY / "quality/redteam/cases-engine.yaml").read_text(encoding="utf-8")
    )["cases"]
}

DUMMY_POLICY = "schema_version: 1\npaths:\n  protected: [governance/**]\n"
DUMMY_THRESHOLDS = "schema_version: 1\n"
DUMMY_ENGINE = (
    "calls = []\n"
    "\n"
    "\n"
    "def report(root):\n"
    "    calls.append(root)\n"
    '    return {"hits": 1}\n'
    "\n"
    "\n"
    "def miss(root):\n"
    '    return {"hits": 0}\n'
)
DISPATCH_CASES = """\
schema_version: 1
cases:
  - id: E1
    failure_mode: F1
    gate: G-DRY
    harness: gate-engine
    engine: dummy_engine.report
    expect: "hits>=1"
  - id: T1
    failure_mode: F1
    gate: G-DEAD
    harness: gate-tool
    tool: absent-tool
  - id: H1
    failure_mode: F1
    gate: G-META-1
    harness: hook
    checker: protected-write
    payload: "governance/thresholds.yaml"
  - id: R1
    failure_mode: F1
    gate: G-MUT
    harness: heuristic
    checker: testless
    payload: "production=true;tests=false"
"""
ISOLATION_CASES = """\
schema_version: 1
cases:
  - id: E1
    failure_mode: F1
    gate: G-DRY
    harness: gate-engine
    engine: dummy_engine.report
    expect: "hits>=1"
  - id: E2
    failure_mode: F1
    gate: G-DRY
    harness: gate-engine
    engine: dummy_engine.report
    expect: "hits>=1"
"""
TOOL_PRESENT_CASES = """\
schema_version: 1
cases:
  - id: T1
    failure_mode: F1
    gate: G-DEAD
    harness: gate-tool
    tool: vulture
"""
MALFORMED_CASES = """\
schema_version: 1
cases:
  - id: X1
    failure_mode: F14
    gate: G-DRY
    harness: gate-engine
    engine: dummy_engine.report
    expect: "hits>=1"
  - id: X2
    failure_mode: F14
    gate: G-DRY
    harness: gate-engine
    engine: no.such.module.fn
    expect: ">=1"
  - id: X3
    failure_mode: F14
    gate: G-DRY
    harness: gate-engine
    engine: dummy_engine.miss
    expect: "hits>=1"
  - id: X4
    failure_mode: F14
    gate: G-NOPE
    harness: hook
    checker: forbidden-command
    payload: "git push --no-verify"
  - id: X5
    failure_mode: F14
    harness: mesa
    gate: G-MUT
    checker: testless
    payload: "x"
  - id: X6
    failure_mode: F14
    gate: G-MUT
    harness: heuristic
    checker: testless
    payload: "production=false"
"""
PAIR_CASES = """\
schema_version: 1
cases:
  - id: A1
    failure_mode: F14
    gate: G-HOOKS-WIRED
    harness: hook
    checker: forbidden-command
    payload: "git push --no-verify"
  - id: A2
    failure_mode: F14
    gate: G-HOOKS-WIRED
    harness: hook
    checker: forbidden-command
    payload: "git commit --no-verify"
"""
LONE_CASE = """\
schema_version: 1
cases:
  - id: A1
    failure_mode: F14
    gate: G-HOOKS-WIRED
    harness: hook
    checker: forbidden-command
    payload: "git push --no-verify"
"""
EMPTY_CASES = "schema_version: 1\ncases: []\n"


def _engine(dotted: str) -> Callable[[Path], Any]:
    module, _, attribute = dotted.rpartition(".")
    return getattr(importlib.import_module(module), attribute)


def _dummy_root(tmp_path: Path, cases: str = DISPATCH_CASES) -> Path:
    (tmp_path / "governance").mkdir()
    (tmp_path / "governance" / "policy.yaml").write_text(DUMMY_POLICY, encoding="utf-8")
    (tmp_path / "governance" / "thresholds.yaml").write_text(DUMMY_THRESHOLDS, encoding="utf-8")
    (tmp_path / "quality" / "redteam").mkdir(parents=True)
    (tmp_path / "quality" / "redteam" / "cases.yaml").write_text(cases, encoding="utf-8")
    (tmp_path / "dummy_engine.py").write_text(DUMMY_ENGINE, encoding="utf-8")
    return tmp_path


def _case_root(tmp_path: Path, files: dict[str, str]) -> Path:
    directory = tmp_path / "quality" / "redteam"
    directory.mkdir(parents=True)
    for name, content in files.items():
        (directory / name).write_text(content, encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize("case_id", sorted(ENGINE_CASES))
def test_engine_case_catches_planted_defect(case_id: str, tmp_path: Path) -> None:
    case = ENGINE_CASES[case_id]
    engine = _engine(str(case["engine"]))
    report = engine(BUILDERS[case_id](tmp_path))
    assert redteam.meets(report, str(case["expect"]))


def test_runner_dispatches_by_harness(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _dummy_root(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setitem(BUILDERS, "E1", lambda directory: directory)
    monkeypatch.setattr(shutil, "which", lambda _tool: None)

    count, failures = redteam.run(root)

    dummy = importlib.import_module("dummy_engine")
    assert count == 3
    assert failures == []
    assert len(dummy.calls) == 1
    assert dummy.calls[0].is_relative_to(root / "build" / "tmp")


def test_mode_invariant_on_union(tmp_path: Path) -> None:
    pair_alone = redteam.run(_case_root(tmp_path / "pair", {"cases.yaml": PAIR_CASES}))
    assert pair_alone[1] == []

    split = _case_root(
        tmp_path / "split",
        {"cases.yaml": LONE_CASE, "cases-engine.yaml": LONE_CASE},
    )
    assert redteam.run(split)[1] == []

    lone = redteam.run(_case_root(tmp_path / "lone", {"cases.yaml": LONE_CASE}))
    assert lone[1] == []

    complete = _case_root(
        tmp_path / "complete",
        {"cases.yaml": LONE_CASE, "cases-engine.yaml": EMPTY_CASES, "cases-tool.yaml": EMPTY_CASES},
    )
    _, failures = redteam.run(complete)
    assert "F14: requiere al menos dos casos" in failures


def test_summary_counts_by_harness(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _dummy_root(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setitem(BUILDERS, "E1", lambda directory: directory)
    monkeypatch.setattr(shutil, "which", lambda _tool: None)

    count, failures = redteam.run(root)

    output = capsys.readouterr().out
    assert count == 3
    assert failures == []
    assert "cargados cases.yaml; ausentes: cases-engine.yaml, cases-tool.yaml" in output
    assert "red team SKIP: T1: herramienta ausente: absent-tool" in output
    assert (
        "3/3 rechazados · 1 gate-engine · 0 gate-tool · 1 hook · "
        "1 heuristic (declarados) · 1 SKIP" in output
    )


def test_isolated_tmpdirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _dummy_root(tmp_path, ISOLATION_CASES)
    monkeypatch.syspath_prepend(str(tmp_path))
    roots: list[Path] = []

    def record(directory: Path) -> Path:
        roots.append(directory)
        return directory

    monkeypatch.setitem(BUILDERS, "E1", record)
    monkeypatch.setitem(BUILDERS, "E2", record)

    count, failures = redteam.run(root)

    assert len(roots) == 2
    assert roots[0] != roots[1]
    assert count == 2
    assert failures == []


@pytest.mark.parametrize(
    ("report", "expect", "expected"),
    [
        ({"hits": 1}, "hits>=1", True),
        ({"hits": 0}, "hits>=1", False),
        ({"counts": {"introverted": 2}}, "counts.introverted>=1", True),
        ({"candidates": [{"score": 1.0}]}, "candidates>=1", True),
        ({"candidates": []}, "candidates>=1", False),
        (1, ">=1", True),
        ({"hits": 1}, "hits>=2", False),
        ({"hits": 1}, "hits", False),
    ],
)
def test_meets_evaluates_catch_conditions(report: Any, expect: str, expected: bool) -> None:
    assert redteam.meets(report, expect) is expected


def test_gate_tool_case_catches_when_gate_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _dummy_root(tmp_path, TOOL_PRESENT_CASES)
    monkeypatch.setitem(BUILDERS, "T1", lambda directory: directory)
    monkeypatch.setattr(shutil, "which", lambda _tool: "/usr/bin/true")

    def fake_gate(_fixture: Path) -> GateResult:
        return GateResult("G-DEAD", Status.FAIL, "dead code found")

    monkeypatch.setitem(REGISTRY, "G-DEAD", fake_gate)

    count, failures = redteam.run(root)

    assert count == 1
    assert failures == []


def test_gate_tool_fixture_lives_outside_the_repo_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """El fixture tool vive fuera del árbol del repo.

    Semgrep/detect-secrets enumeran archivos vía git: un fixture untracked
    dentro del repo les es invisible (addendum R1).
    """
    root = _dummy_root(tmp_path, TOOL_PRESENT_CASES)
    fixtures: list[Path] = []

    def record(directory: Path) -> Path:
        fixtures.append(directory)
        return directory

    monkeypatch.setitem(BUILDERS, "T1", record)
    monkeypatch.setattr(shutil, "which", lambda _tool: "/usr/bin/true")
    monkeypatch.setitem(
        REGISTRY, "G-DEAD", lambda _fixture: GateResult("G-DEAD", Status.FAIL, "dead code")
    )

    count, failures = redteam.run(root)

    assert count == 1
    assert failures == []
    assert not fixtures[0].is_relative_to(root)


def test_dispatch_reports_malformed_cases(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _dummy_root(tmp_path, MALFORMED_CASES)
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setitem(BUILDERS, "X2", lambda directory: directory)
    monkeypatch.setitem(BUILDERS, "X3", lambda directory: directory)

    count, failures = redteam.run(root)

    assert count == 6
    assert "X1: sin builder" in " ".join(failures)
    assert "X2: ModuleNotFoundError" in " ".join(failures)
    assert "X3: el motor no reportó el defecto (hits>=1)" in " ".join(failures)
    assert "X4: gate inexistente G-NOPE" in " ".join(failures)
    assert "X5: arnés desconocido mesa" in " ".join(failures)
    assert "X6: dejó de ser rechazado por G-MUT" in " ".join(failures)


def test_tool_builders_merge_when_module_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = types.ModuleType("tools.wct.selftest.fixtures_tools")
    fake.BUILDERS = {"F1-b": lambda directory: directory}
    monkeypatch.setitem(sys.modules, "tools.wct.selftest.fixtures_tools", fake)

    merged = redteam._builders()

    assert "F1-a" in merged
    assert merged["F1-b"] is fake.BUILDERS["F1-b"]


def test_run_without_case_files_fails(tmp_path: Path) -> None:
    count, failures = redteam.run(tmp_path)

    assert count == 0
    assert "sin archivos de casos" in " ".join(failures)
