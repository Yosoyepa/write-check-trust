"""Casos gate-tool del red team: el gate productivo caza el defecto plantado.

PR-C, SPEC-C-01 tests 6-7 (DoD-F2). Cada parámetro planta el defecto de su
caso con el builder de ``fixtures_tools``, invoca la FUNCIÓN de gate
productiva (``REGISTRY[gate]`` de tools/wct/gate/runner.py) sobre el
fixture aislado y exige que el gate lo rechace: la aserción traza al
GateResult del gate, no al andamiaje (TEST-003). El skip por herramienta
ausente es honesto: nombra la herramienta y NO cuenta como verde del caso
(DoD-F2.2, ADR-C-01 §4). Con las herramientas del grupo quality presentes,
los 9 casos deben pasar de verdad — un caso que no pase se reporta en
rojo con su salida, no se marca xfail (ADR-C-01 §5).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import shutil
from typing import Any

import pytest
import yaml

from tools.wct.gate.runner import REGISTRY
from tools.wct.model import Status
from tools.wct.selftest import redteam
from tools.wct.selftest.fixtures_tools import BUILDERS, IMPORT_LINTER, SEMGREP_RULES

REPO_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = REPO_ROOT / "quality" / "redteam" / "cases-tool.yaml"


def _load_cases() -> dict[str, dict[str, Any]]:
    document = yaml.safe_load(CASES_PATH.read_text(encoding="utf-8"))
    return {str(case["id"]): case for case in document["cases"]}


CASES = _load_cases()


@pytest.mark.parametrize("case_id", sorted(CASES))
def test_tool_case_catches_planted_defect(case_id: str, tmp_path: Path) -> None:
    """El gate productivo rechaza el fixture con el defecto plantado."""
    case = CASES[case_id]
    tool = str(case["tool"])
    if shutil.which(tool) is None:
        pytest.skip(f"herramienta ausente: {tool}")
    root = BUILDERS[case_id](tmp_path)
    result = REGISTRY[str(case["gate"])](root)
    assert result.status is Status.FAIL, f"{case_id}: {result.summary}"


def test_embedded_replicas_match_production() -> None:
    """Las réplicas embebidas no divergen de los archivos productivos.

    Los fixtures de G-ARCH y G-SAST-SEMGREP califican el instrumento solo
    si replican BYTE a byte la configuración que esos gates leen en
    producción; una divergencia silenciosa mediría un instrumento viejo.
    """
    production_rules = (REPO_ROOT / "governance" / "semgrep" / "wct-architecture.yaml").read_text(
        encoding="utf-8"
    )
    production_contracts = (REPO_ROOT / ".importlinter").read_text(encoding="utf-8")
    assert production_rules == SEMGREP_RULES
    assert production_contracts == IMPORT_LINTER


def _harness_dispatcher(module: Any) -> Callable[..., Any] | None:
    """Detecta el despachador por arnés de R1 sin acoplar al nombre exacto.

    El runner actual (pre-merge de PR-C) no expone ningún símbolo cuyo
    nombre mencione dispatch/harness; el despachador por ``harness`` de
    ADR-C-01 §1 sí. Guard de capacidad pactado con el arquitecto: hasta el
    merge este test queda en skip explícito y nombrado.
    """
    for name, member in vars(module).items():
        if ("dispatch" in name or "harness" in name) and callable(member):
            return member
    return None


def test_absent_tool_reports_visible_skip(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Herramienta ausente → SKIP visible con la herramienta nombrada.

    Ejercita el despachador por arnés de R1 contra la unión post-merge: un
    repo-fixture con cases-tool.yaml y ``which`` falseado para ocultar
    vulture. Los casos de esa herramienta deben ir a la lista de skips
    nombrándola, sin engrosar failures ni rechazados (ADR-C-01 §4).
    """
    if _harness_dispatcher(redteam) is None:
        pytest.skip("requiere el dispatcher de R1 (post-merge)")
    root = tmp_path / "repo"
    (root / "quality" / "redteam").mkdir(parents=True)
    shutil.copy(CASES_PATH, root / "quality" / "redteam" / "cases-tool.yaml")
    real_which = shutil.which
    monkeypatch.setattr(
        shutil, "which", lambda name: None if name == "vulture" else real_which(name)
    )
    _count, failures = redteam.run(root)
    captured = capsys.readouterr()
    assert "vulture" in captured.out + captured.err
    vulture_cases = {"F1-b", "F11-a", "F11-b"}
    assert not any(any(case_id in failure for case_id in vulture_cases) for failure in failures)
