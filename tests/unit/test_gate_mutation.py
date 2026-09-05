"""G-MUT verifica cero sobrevivientes, no solo que mutmut corra (TEST-002).

Hasta PR-E el gate era el comando ``mutmut run`` desnudo, y su exit code no
distingue sobrevivientes (matriz del paso 0.1: sale 0 con el árbol limpio Y
con mutantes vivos). El ruling del arquitecto lo cierra: la función de gate
corre mutmut y FALLA listando cada mutante sobreviviente — TEST-002
("cero mutantes sobrevivientes, Verified by: G-MUT") por fin verificado.
"""

from __future__ import annotations

from pathlib import Path
import shutil

import pytest

from tools.wct.gate.runner import REGISTRY, gate_mutation
from tools.wct.model import Status
from tools.wct.selftest.fixtures_tools import BUILDERS

requires_mutmut = pytest.mark.skipif(
    shutil.which("mutmut") is None, reason="requiere mutmut (grupo quality)"
)


@requires_mutmut
def test_survivors_fail_the_gate_and_are_listed(tmp_path: Path) -> None:
    """El mutante del camino no ejercido sobrevive y el gate lo nombra.

    El fixture (b) del paso 0.1: ``total([]) == 0`` pasa, pero los mutantes
    de ``sum(items) * 1.0`` sobreviven. Con el gate de comando este árbol
    daba PASS (el hallazgo); con la función debe dar FAIL con cada
    sobreviviente en los detalles.
    """
    result = gate_mutation(BUILDERS["F2-b"](tmp_path))

    assert result.status is Status.FAIL
    assert "sobrevivientes" in result.summary
    assert result.details, "el FAIL debe listar los mutantes sobrevivientes"
    assert all(line.endswith(": survived") for line in result.details)


@requires_mutmut
def test_weak_test_survivors_fail_the_gate(tmp_path: Path) -> None:
    """F5-b: un test débil deja mutantes vivos de otra clase que F2-b.

    Cobertura parcial de ramas — solo el camino intermedio de ``clamp`` se
    ejercita, y los mutantes de las comparaciones sobreviven.
    """
    result = gate_mutation(BUILDERS["F5-b"](tmp_path))

    assert result.status is Status.FAIL
    assert result.details


@requires_mutmut
def test_clean_tree_passes_with_zero_survivors(tmp_path: Path) -> None:
    """Árbol donde todo mutante muere: PASS con el resumen del contrato."""
    root = tmp_path
    (root / "pyproject.toml").write_text(
        '[project]\nname = "victim"\nversion = "0.0.0"\n\n[tool.mutmut]\n'
        'source_paths = ["src"]\n'
        'pytest_add_cli_args_test_selection = ["tests/test_calc.py"]\n',
        encoding="utf-8",
    )
    (root / "src" / "victim").mkdir(parents=True)
    (root / "src" / "victim" / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / "victim" / "calc.py").write_text(
        "def add(a, b):\n    return a + b\n", encoding="utf-8"
    )
    (root / "tests").mkdir()
    (root / "tests" / "test_calc.py").write_text(
        "from victim.calc import add\n\n"
        "def test_add():\n    assert add(2, 3) == 5\n    assert add(-1, 1) == 0\n",
        encoding="utf-8",
    )

    result = gate_mutation(root)

    assert result.status is Status.PASS
    assert result.summary == "cero mutantes sobrevivientes"


@requires_mutmut
def test_run_that_cannot_execute_fails_the_gate(tmp_path: Path) -> None:
    """Producción sin tests: la corrida misma aborta y el gate FALLA.

    `mutmut run` sale 1 cuando no puede colectar stats (matriz del paso
    0.1); el gate traduce ese aborto en FAIL con el diagnóstico.
    """
    result = gate_mutation(BUILDERS["F2-a"](tmp_path))

    assert result.status is Status.FAIL
    assert result.details, "el FAIL debe llevar el diagnóstico de mutmut"


def test_absent_mutmut_keeps_optional_skip_semantics(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutmut ausente → SKIP visible: la semántica optional del gate original."""
    monkeypatch.setattr(
        "tools.wct.gate.runner.shutil.which",
        lambda executable: None if executable == "mutmut" else executable,
    )

    result = REGISTRY["G-MUT"](tmp_path)

    assert result.status is Status.SKIP
    assert result.summary == "herramienta ausente: mutmut"
