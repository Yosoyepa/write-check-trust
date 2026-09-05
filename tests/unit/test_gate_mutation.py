"""G-MUT clasifica todo el inventario del motor (G1a, ADR-G1-01).

PR-E hizo real el veredicto de sobrevivientes; G1a lo completa: el gate
deriva su veredicto de la secuencia run → ``results --all true`` → tabla de
ADR-G1-01 con precedencia ERROR>FAIL conservando identidades. Los controles
con motor REAL (sano, timeout, inyección en meta, corrida rota) viven aquí;
la clasificación pura en ``test_mutation_verdict.py`` y el CLI por
subprocess en ``test_mutation_cli.py``.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess

import pytest

from tools.wct.gate.runner import REGISTRY, gate_mutation
from tools.wct.model import Status
from tools.wct.selftest.fixtures_tools import BUILDERS, mutmut_pyproject

requires_mutmut = pytest.mark.skipif(
    shutil.which("mutmut") is None, reason="requiere mutmut (grupo quality)"
)


def _plant_victim(root: Path, module: str, code: str, test_path: str, test_code: str) -> Path:
    """Escribe un fixture de mutación mínimo: pyproject + módulo + su test."""
    (root / "pyproject.toml").write_text(mutmut_pyproject(test_path), encoding="utf-8")
    (root / "src" / "victim").mkdir(parents=True)
    (root / "src" / "victim" / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / "victim" / f"{module}.py").write_text(code, encoding="utf-8")
    (root / "tests").mkdir()
    (root / "tests" / test_path.removeprefix("tests/")).write_text(test_code, encoding="utf-8")
    return root


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
    identities = [line for line in result.details if line.startswith("identidades:")]
    assert identities, "el FAIL debe listar los mutantes sobrevivientes"
    assert all(line.endswith(": survived") for line in identities)


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
def test_clean_tree_cites_inventory(tmp_path: Path) -> None:
    """Control sano de PR-E, AMPLIADO (RG01): PASS cita el inventario N/N killed.

    Extiende ``test_clean_tree_passes_with_zero_survivors`` de PR-E — mismo
    árbol, misma expectativa de PASS — y añade la afirmación de inventario:
    el claim PASS es LIMITADO ("el motor reportó todo su inventario como
    killed", ADR-G1-01 nota 1), así que el resumen cita N/N y el diagnóstico
    lleva fase, conteos, versión del motor y la salvedad del claim.
    """
    root = _plant_victim(
        tmp_path,
        module="calc",
        code="def add(a, b):\n    return a + b\n",
        test_path="tests/test_calc.py",
        test_code=(
            "from victim.calc import add\n\n"
            "def test_add():\n    assert add(2, 3) == 5\n    assert add(-1, 1) == 0\n"
        ),
    )

    result = gate_mutation(root)

    assert result.status is Status.PASS
    assert "clasificación del motor" in result.summary
    assert re.search(r": (\d+)/\1 killed", result.summary), "el PASS debe citar el inventario"
    assert any(line.startswith("fase: ") for line in result.details)
    assert any(line.startswith("conteos: killed=") for line in result.details)
    assert any(line.startswith("motor: mutmut ") for line in result.details)


@requires_mutmut
def test_run_that_cannot_execute_fails_the_gate(tmp_path: Path) -> None:
    """Producción sin tests: la corrida misma aborta y el gate FALLA.

    `mutmut run` sale 1 cuando no puede colectar stats (matriz del paso
    0.1); el gate traduce ese aborto en FAIL con el diagnóstico.
    """
    result = gate_mutation(BUILDERS["F2-a"](tmp_path))

    assert result.status is Status.FAIL
    assert result.details, "el FAIL debe llevar el diagnóstico de mutmut"


@requires_mutmut
def test_untested_mutants_fail_the_gate(tmp_path: Path) -> None:
    """Mutante "no tests" (🫥): ningún test detecta ese cambio (TEST-002 estricto).

    La corrida completa bien (add sí tiene tests), pero los mutantes de
    ``mul`` quedan "no tests": un escape equivalente a un sobreviviente —
    el gate debe FALLAR nombrándolos igual que a los sobrevivientes.
    """
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
        "def add(a, b):\n    return a + b\n\n\ndef mul(a, b):\n    return a * b\n",
        encoding="utf-8",
    )
    (root / "tests").mkdir()
    (root / "tests" / "test_calc.py").write_text(
        "from victim.calc import add\n\ndef test_add():\n    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )

    result = gate_mutation(root)

    assert result.status is Status.FAIL
    assert "sin test asociado" in result.summary
    assert any(line.endswith(": no tests") for line in result.details)


@requires_mutmut
def test_survivors_and_untested_are_distinguished_in_one_summary(tmp_path: Path) -> None:
    """Sobrevivientes y sin-test juntos: un FAIL, summary que distingue ambos."""
    root = tmp_path
    (root / "pyproject.toml").write_text(
        '[project]\nname = "victim"\nversion = "0.0.0"\n\n[tool.mutmut]\n'
        'source_paths = ["src"]\n'
        'pytest_add_cli_args_test_selection = ["tests/test_billing.py"]\n',
        encoding="utf-8",
    )
    (root / "src" / "victim").mkdir(parents=True)
    (root / "src" / "victim" / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / "victim" / "billing.py").write_text(
        "def total(items):\n    return sum(items) * 1.0\n\n\ndef mul(a, b):\n    return a * b\n",
        encoding="utf-8",
    )
    (root / "tests").mkdir()
    (root / "tests" / "test_billing.py").write_text(
        "from victim.billing import total\n\ndef test_total_empty():\n    assert total([]) == 0\n",
        encoding="utf-8",
    )

    result = gate_mutation(root)

    assert result.status is Status.FAIL
    assert "mutantes sobrevivientes" in result.summary
    assert "sin test asociado" in result.summary
    assert any(line.endswith(": survived") for line in result.details)
    assert any(line.endswith(": no tests") for line in result.details)


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


@requires_mutmut
def test_timeout_states_are_instrument_error(tmp_path: Path) -> None:
    """Timeout REAL (patrón sonda P8): ERROR de instrumento, jamás PASS falso.

    ``n -= 1`` mutado a incremento produce un bucle infinito real: el motor
    lo reporta ``timeout`` y esa mutación tarda en caer (~15-20 s la fase de
    mutación completa). Antes de G1a este árbol daba PASS (la sonda P8 de
    EVIDENCE.md); con ADR-G1-01 el estado está fuera del contrato de
    certificación WCT → ERROR con la identidad del colgado.
    """
    root = _plant_victim(
        tmp_path,
        module="countdown",
        code="def countdown(n):\n    while n > 0:\n        n -= 1\n    return n\n",
        test_path="tests/test_countdown.py",
        test_code=(
            "from victim.countdown import countdown\n\n"
            "def test_countdown():\n    assert countdown(5) == 0\n"
        ),
    )

    result = gate_mutation(root)

    assert result.status is Status.ERROR
    assert "fuera del contrato de certificación WCT" in result.summary
    assert any(": timeout" in line for line in result.details)


@requires_mutmut
def test_injected_nonterminal_states_error(tmp_path: Path) -> None:
    """[M04b · INYECCIÓN declarada] exits 2/34 plantados en meta → ERROR, no PASS.

    Corrida sana real primero (que genere mutants/ y meta), luego se
    SOBRESCRIBEN exit_code_by_key en ``mutants/src/victim/calc.py.meta`` con
    los exits 2 (check was interrupted by user) y 34 (skipped) — la misma
    inyección de la sonda P7/B. ``mutmut run`` re-ejecutado respeta el cache
    (``__main__.py``: "let the result stand"), así que el gate lee los
    estados plantados. Es inyección controlada [I]: representa la respuesta
    del motor, no prueba su ocurrencia natural.
    """
    root = _plant_victim(
        tmp_path,
        module="calc",
        code="def add(a, b):\n    return a + b\n\n\ndef mul(a, b):\n    return a * b\n",
        test_path="tests/test_calc.py",
        test_code=(
            "from victim.calc import add, mul\n\n"
            "def test_add():\n    assert add(2, 3) == 5\n\n"
            "def test_mul():\n    assert mul(2, 3) == 6\n"
        ),
    )
    subprocess.run(["mutmut", "run"], cwd=root, check=True, capture_output=True)
    meta_path = root / "mutants" / "src" / "victim" / "calc.py.meta"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    keys = sorted(meta["exit_code_by_key"])
    meta["exit_code_by_key"][keys[0]] = 2
    meta["exit_code_by_key"][keys[1]] = 34
    meta_path.write_text(json.dumps(meta), encoding="utf-8")

    result = gate_mutation(root)

    assert result.status is Status.ERROR
    assert "fuera del contrato de certificación WCT" in result.summary
    joined = "\n".join(result.details)
    assert "check was interrupted by user" in joined
    assert "skipped" in joined


@requires_mutmut
def test_results_failure_after_healthy_run_is_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """[RG02 · DOBLE de proceso declarado] results exit 1 tras run sano → ERROR.

    La fase results del adaptador falla con un diagnostic real de proceso
    (exit 1); el run previo respondió sano (exit 0). El doble reemplaza
    SOLO la frontera de subprocess del adaptador (``_execute``) con esas
    respuestas explícitas — la secuencia de clasificación es la productiva.
    Ningún motor real corre aquí: el control sano/defectuoso con motor real
    vive en el resto de este archivo.
    """
    responses = {
        ("mutmut", "--version"): (0, "mutmut, version 3.7.0"),
        ("mutmut", "run"): (0, "Running mutation testing\n1/1  🎉 1  ⏰ 0  🙁 0"),
        ("mutmut", "results", "--all", "true"): (1, "TypeError: boom del results"),
    }

    def fake_execute(_root: Path, command: list[str]) -> tuple[int, str]:
        return responses[tuple(command)]

    monkeypatch.setattr("tools.wct.mutate.verdict._execute", fake_execute)

    result = gate_mutation(tmp_path)

    assert result.status is Status.ERROR
    assert "evidencia inválida (fase results)" in result.summary
    assert any("TypeError: boom del results" in line for line in result.details)


@requires_mutmut
def test_run_failure_blocks_without_product_label(tmp_path: Path) -> None:
    """Run interrumpido (F2-a): FAIL "ejecución no completada", sin etiqueta de producto (D2).

    La corrida misma aborta (exit 1 sin colecta de stats): es un FAIL de
    compatibilidad PR-E/redteam, NO un defecto de producto — el resumen no
    atribuye "defecto" y el diagnóstico lleva las últimas líneas del motor.
    """
    result = gate_mutation(BUILDERS["F2-a"](tmp_path))

    assert result.status is Status.FAIL
    assert "ejecución no completada" in result.summary
    assert "defecto" not in result.summary
    assert result.details, "el FAIL debe llevar el diagnóstico de mutmut"
