"""Adaptador de veredicto del motor de mutación (G1a, ADR-G1-01/03).

Un contrato, dos consumidores observables: ``gate_mutation`` (G-MUT) y el
CLI ``wct mutate run`` derivan su veredicto de la MISMA secuencia —
``mutmut run`` → ``mutmut results --all true`` → clasificación por la tabla
de ADR-G1-01 con precedencia ERROR>FAIL conservando identidades. El
adaptador retorna el ``GateResult`` existente (no existe un tipo Verdict
paralelo): status/summary/details expresan fase, conteos e identidades.

El claim de PASS es LIMITADO por diseño (ADR-G1-01 nota 1): "el motor
reportó todo su inventario como killed" — sin causa (exit 1 y 3 colapsan a
killed) ni pertenencia a esta corrida; esa acreditación es G1b.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import subprocess
import time

from tools.wct.model import GateResult, Status

GATE_ID = "G-MUT"

# Vocabulario de mutmut 3.7.0 (__main__.py:82-104): 10 estados — 1 aprobado,
# 2 defectuosos, 7 fuera del contrato de certificación WCT (ADR-G1-01).
PASS_STATES = frozenset({"killed"})
FAIL_STATES = frozenset({"survived", "no tests"})
CONTRACT_ERROR_STATES = frozenset(
    {
        "timeout",
        "suspicious",
        "not checked",
        "check was interrupted by user",
        "segfault",
        "skipped",
        "caught by type check",
    }
)
VOCABULARY = PASS_STATES | FAIL_STATES | CONTRACT_ERROR_STATES

FAIL_LABELS = {"survived": "mutantes sobrevivientes", "no tests": "sin test asociado"}

DIAGNOSTIC_TAIL = 50
CLAIM_LIMIT = "claim limitado: reporte del motor, sin causa ni frescura (G1b)"
SEQUENCE = "mutmut run && mutmut results --all true"


def _execute(root: Path, command: list[str]) -> tuple[int, str]:
    """Corre un comando del motor y retorna (exit code, salida combinada).

    Es la única frontera de subprocess del adaptador: los dobles declarados
    de los tests (RG02) se inyectan aquí, nunca en la clasificación.
    """
    completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    return completed.returncode, (completed.stdout + "\n" + completed.stderr).strip()


def _engine_version(root: Path) -> str:
    """Versión del motor para el diagnóstico (llamada extra aceptada por ADR-G1-03)."""
    _code, output = _execute(root, ["mutmut", "--version"])
    first_line = output.splitlines()[0] if output else ""
    return first_line.split()[-1] if first_line else "desconocida"


def _counts_line(counts: Counter[str]) -> str:
    """Renglon estable de conteos por estado, orden alfabético."""
    return "conteos: " + ", ".join(f"{state}={counts[state]}" for state in sorted(counts))


def _identity_lines(entries: dict[str, str]) -> list[str]:
    """Identidades de los hallazgos (todo estado que no sea killed), una por renglón."""
    return [
        f"identidades: {identity}: {state}"
        for identity, state in entries.items()
        if state not in PASS_STATES
    ]


def _parse(output: str) -> tuple[dict[str, str], list[str]]:
    """Parsea el inventario de ``results --all true``: entradas y problemas.

    Cada renglón legible es ``<identidad>: <estado>``. Identidad duplicada,
    estado fuera de vocabulario o renglón truncado son evidencia inválida
    (fase clasificación), no datos que ignorar en silencio.
    """
    entries: dict[str, str] = {}
    problems: list[str] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        identity, separator, state = line.partition(": ")
        if not separator or not identity or not state:
            problems.append(f"renglón desconocido: {line}")
        elif identity in entries:
            problems.append(f"identidad duplicada: {identity}")
        elif state not in VOCABULARY:
            problems.append(f"estado fuera de vocabulario: {line}")
        else:
            entries[identity] = state
    return entries, problems


def _invalid_rows_result(problems: list[str]) -> GateResult:
    """ERROR de fase clasificación: renglones que no se pueden contar (RG04)."""
    summary = f"evidencia inválida (fase clasificación): {len(problems)} renglones inválidos"
    return GateResult(GATE_ID, Status.ERROR, summary, details=["fase: clasificación", *problems])


def _empty_inventory_result() -> GateResult:
    """ERROR de fase inventario: legible pero sin mutantes donde se exige trabajo (M02)."""
    return GateResult(
        GATE_ID,
        Status.ERROR,
        "no acreditado (fase inventario): inventario vacío (0 mutantes)",
        details=["fase: inventario", "conteos: 0 mutantes"],
    )


def _measured_result(entries: dict[str, str]) -> GateResult:
    """Veredicto sobre un inventario legible y no vacío, con precedencia ERROR>FAIL."""
    counts = Counter(entries.values())
    error_states = sorted(state for state in counts if state in CONTRACT_ERROR_STATES)
    if error_states:
        labels = " + ".join(f"{counts[state]} {state}" for state in error_states)
        return GateResult(
            GATE_ID,
            Status.ERROR,
            f"fuera del contrato de certificación WCT: {labels}",
            details=["fase: certificación", _counts_line(counts), *_identity_lines(entries)],
        )
    fail_states = sorted(state for state in counts if state in FAIL_STATES)
    if fail_states:
        labels = " + ".join(f"{counts[state]} {FAIL_LABELS[state]}" for state in fail_states)
        return GateResult(
            GATE_ID,
            Status.FAIL,
            f"criterio de mutación incumplido: {labels}",
            details=["fase: criterio", _counts_line(counts), *_identity_lines(entries)],
        )
    return GateResult(
        GATE_ID,
        Status.PASS,
        f"clasificación del motor: {counts['killed']}/{len(entries)} killed",
        details=["fase: certificación", _counts_line(counts), CLAIM_LIMIT],
    )


def classify_inventory(output: str) -> GateResult:
    """Clasifica el inventario completo del motor según la tabla de ADR-G1-01.

    Args:
        output: stdout de ``mutmut results --all true`` (una ``<identidad>:
            <estado>`` por renglón).

    Returns:
        GateResult con la causa declarada por el ADR y details estables
        (``fase:``/``conteos:``/``identidades:``): ERROR por renglones
        inválidos, inventario vacío o estados fuera del contrato (con las
        identidades de FAIL conservadas); FAIL para survived/no tests con
        cada mutante nombrado; PASS limitado cuando todo el inventario es
        killed, citando N/N.
    """
    entries, problems = _parse(output)
    if problems:
        return _invalid_rows_result(problems)
    if not entries:
        return _empty_inventory_result()
    return _measured_result(entries)


def mutation_verdict(root: Path) -> GateResult:
    """Corre la secuencia del motor y clasifica su inventario completo.

    Args:
        root: raíz del árbol a medir; su ``[tool.mutmut]`` define el alcance.

    Returns:
        El veredicto de ADR-G1-01: run interrumpido → FAIL "ejecución no
        completada" (compatibilidad PR-E, sin atribuir defecto de producto);
        results fallido → ERROR fase results; el resto, lo que dicte
        ``classify_inventory``. Todo diagnóstico lleva fase y versión del
        motor; la precedencia es ERROR>FAIL conservando identidades.
    """
    started = time.monotonic()
    version = _engine_version(root)
    motor = f"motor: mutmut {version}"

    run_code, run_output = _execute(root, ["mutmut", "run"])
    if run_code != 0:
        return GateResult(
            GATE_ID,
            Status.FAIL,
            "ejecución no completada",
            int((time.monotonic() - started) * 1000),
            ["fase: run", motor, *run_output.splitlines()[-DIAGNOSTIC_TAIL:]],
            "mutmut run",
        )

    results_code, results_output = _execute(root, ["mutmut", "results", "--all", "true"])
    if results_code != 0:
        last = results_output.splitlines()[-1] if results_output else f"exit {results_code}"
        return GateResult(
            GATE_ID,
            Status.ERROR,
            f"evidencia inválida (fase results): {last}",
            int((time.monotonic() - started) * 1000),
            ["fase: results", motor, *results_output.splitlines()[-DIAGNOSTIC_TAIL:]],
            SEQUENCE,
        )

    verdict = classify_inventory(results_output)
    return GateResult(
        GATE_ID,
        verdict.status,
        verdict.summary,
        int((time.monotonic() - started) * 1000),
        [*verdict.details, motor],
        SEQUENCE,
    )


def render_verdict(result: GateResult) -> str:
    """Diagnóstico legible y estable del CLI: ``estado:`` más las líneas del veredicto.

    ADR-G1-03 §4: las líneas ``estado:``/``fase:``/``identidades:`` son
    salida nueva pero contractual — mantenerlas estables sin prometer
    parsing más allá de ellas.
    """
    return "\n".join([f"estado: {result.status.value}", *result.details])
