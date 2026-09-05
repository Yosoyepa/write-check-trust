"""CLI de mutación por subprocess del entrypoint real (RG09, ADR-G1-03 §4).

``wct mutate run`` se ejercita como lo usa un humano — subprocess de
``uv run wct mutate run`` sobre un micro-repo fixture — nunca llamando a
``engine.run`` en proceso. Los fixtures viven en tmp_path con su PROPIA
gobernanza mínima: sin manifiesto el scan marca toda función como cambiada
(``engine.py`` scan); el manifiesto del fixture de delta cero se genera con
la herramienta permitida DENTRO del tempdir (``update_manifest``), nunca
editando el ``governance/`` protegido del repo.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import pytest

from tools.wct.mutate.engine import update_manifest

REPO_ROOT = Path(__file__).resolve().parents[2]

requires_mutmut = pytest.mark.skipif(
    shutil.which("mutmut") is None, reason="requiere mutmut (grupo quality)"
)

MICRO_POLICY = "schema_version: 1\npaths:\n  source: [src]\n"
MICRO_THRESHOLDS = "schema_version: 1\nmutation:\n  max_sites_per_file: 100\n"


def _micro_repo(root: Path, module: str, code: str, test_path: str, test_code: str) -> Path:
    """Planta el micro-repo: gobernanza mínima + pyproject + módulo + test."""
    (root / "governance").mkdir()
    (root / "governance" / "policy.yaml").write_text(MICRO_POLICY, encoding="utf-8")
    (root / "governance" / "thresholds.yaml").write_text(MICRO_THRESHOLDS, encoding="utf-8")
    (root / "pyproject.toml").write_text(
        '[project]\nname = "victim"\nversion = "0.0.0"\n\n[tool.mutmut]\n'
        'source_paths = ["src"]\n'
        f'pytest_add_cli_args_test_selection = ["{test_path}"]\n',
        encoding="utf-8",
    )
    (root / "src" / "victim").mkdir(parents=True)
    (root / "src" / "victim" / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / "victim" / f"{module}.py").write_text(code, encoding="utf-8")
    (root / "tests").mkdir()
    (root / "tests" / test_path.removeprefix("tests/")).write_text(test_code, encoding="utf-8")
    return root


def _wct_mutate_run(root: Path) -> subprocess.CompletedProcess[str]:
    """Subprocess del entrypoint real: ``uv run wct mutate run`` sobre el fixture."""
    return subprocess.run(
        ["uv", "run", "--project", str(REPO_ROOT), "wct", "mutate", "run"],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=300,
        check=False,
    )


@requires_mutmut
def test_cli_subprocess_delta_reports_ids(tmp_path: Path) -> None:
    """Sin manifiesto + sobrevivientes: exit 1 e identidades impresas (RG09).

    Micro-repo SIN manifiesto (scan marca toda función como cambiada) con el
    adversario F2-b: el test solo asienta el camino vacío y los mutantes de
    ``sum(items) * 1.0`` sobreviven. El CLI mide con la MISMA política del
    gate (ADR-G1-03): FAIL → exit 1 e ``identidades:`` con cada sobreviviente.
    """
    root = _micro_repo(
        tmp_path,
        module="billing",
        code="def total(items):\n    return sum(items) * 1.0\n",
        test_path="tests/test_billing.py",
        test_code=(
            "from victim.billing import total\n\n"
            "def test_total_empty():\n    assert total([]) == 0\n"
        ),
    )

    completed = _wct_mutate_run(root)
    output = completed.stdout + completed.stderr

    assert completed.returncode == 1, output
    assert "estado: FAIL" in output
    assert "fase: criterio" in output
    assert "conteos: " in output
    assert "survived=" in output
    assert "identidades:" in output
    assert ": survived" in output
    assert "motor: mutmut " in output


def test_cli_delta_zero_informs_without_quality_claim(tmp_path: Path) -> None:
    """Delta cero: informativo exit 0, sin presentar una medición de calidad (RG08).

    El manifiesto del fixture se genera DENTRO del tempdir (autorizado por
    ADR-G1-03 §4) para que ninguna función cuente como cambiada: el CLI
    informa la ausencia de trabajo diferencial y NO imprime veredicto ni
    conteos — no es una medición.
    """
    root = _micro_repo(
        tmp_path,
        module="calc",
        code="def add(a, b):\n    return a + b\n",
        test_path="tests/test_calc.py",
        test_code="from victim.calc import add\n\ndef test_add():\n    assert add(2, 3) == 5\n",
    )
    update_manifest(root)

    completed = _wct_mutate_run(root)
    output = completed.stdout + completed.stderr

    assert completed.returncode == 0, output
    assert "sin trabajo diferencial" in output
    assert "killed" not in output
    assert "estado:" not in output
