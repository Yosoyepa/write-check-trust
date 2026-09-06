from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import NamedTuple, overload

from tools.wct.archmetrics.analyzer import analyze as analyze_architecture
from tools.wct.dry.tpl import analyze_template
from tools.wct.integrity.engine import require_approval_evidence
from tools.wct.introvert.analyzer import analyze as analyze_tests
from tools.wct.lcom.engine import scan as scan_lcom
from tools.wct.ratchet.engine import (
    baseline,
    compare,
    debt_findings,
    ignores_count,
    suppression_count,
)
from tools.wct.size.engine import oversized as size_oversized
from tools.wct.util.git import head_sha

MIN_APPROVER = 2
MIN_REASON = 12
# Procedencia por SHA corto: 40 hex trote G-SECRET (Hex High Entropy);
# 12 resuelven unívocamente y ningún registro futuro vuelve a tropezar.
COMMIT_PROVENANCE_CHARS = 12
PERCENT = re.compile(r"actual:\s*(\d+(?:\.\d+)?)%")
# Techo de un porcentaje: la vía exigible rechaza mediciones fuera de [0, 100].
PERCENT_MAX = 100.0
LCOV_ARTIFACT = Path("build/coverage/lcov.info")
LCOV_COUNTER = re.compile(r"^(LF|LH|BRF|BRH):(\d+)$")
# Renglón que RECLAMA ser contador (nombre reconocido) con valor que NO es
# entero no-negativo (vacío, negativo, decimal). El parser histórico
# (LCOV_COUNTER) lo ignora y esa tolerancia queda intacta; la vía exigible
# lo rechaza como medición inválida (ADR-G3a-02 §5).
LCOV_MALFORMED_COUNTER = re.compile(r"^(LF|LH|BRF|BRH):(?!\d+$).*$")
RECORD_COVERAGE_JSON = Path("build/tmp/coverage-record.json")

# Inventario exigible EXPLÍCITO (ADR-G3a-02 §2): lo que ``--require all``
# exige — las 8 métricas estáticas de measurements() más las dos que
# dependen de herramienta/artefacto. Es la lista de lo EXIGIBLE, no de lo
# medido: independiente de lo que una corrida particular logre medir.
# Orden estable = orden de measurements().
REQUIRED_INVENTORY: tuple[str, ...] = (
    "suppressions",
    "debt-markers",
    "introverted-tests",
    "archmetrics-zones",
    "per-file-ignores",
    "file-size",
    "lcom-classes",
    "dry-template-clusters",
    "docstring-coverage",
    "coverage-total",
)

# Comando que PRODUCE cada medición estática (ADR-G3a-02 §3): lo que el
# operador ejecuta para reproducirla. Las dos dependientes de herramienta o
# artefacto se resuelven con su causa exacta en _absent_failure.
_PRODUCE_COMMANDS: dict[str, str] = {
    "suppressions": "wct ratchet check",
    "debt-markers": "wct ratchet check",
    "introverted-tests": "wct introvert",
    "archmetrics-zones": "wct archmetrics",
    "per-file-ignores": "wct ratchet check",
    "file-size": "wct ratchet check",
    "lcom-classes": "wct lcom",
    "dry-template-clusters": "wct dry --normalized",
}
# Shell-correcto (0f): `-m "not property"` cita el marcador para que la
# shell no lo parta en dos argumentos; shlex.split reproduce los límites
# reales y ancla la igualdad con la receta del gate (checks.py).
_COVERAGE_TOTAL_COMMAND = (
    'pytest --cov --cov-branch --cov-report=lcov:build/coverage/lcov.info -q -m "not property"'
)


class RatchetReport(NamedTuple):
    """Resultado del modo exigible: bloqueos y resumen público.

    Attributes:
        failures: líneas de bloqueo (vacío = verde): TODAS las del modo
            tolerante (exigir es aditivo, ADR-G3a-02 §4) más las de exigibles
            ausentes o con medición inválida — textos distintos entre sí.
        summary: nombres exigidos, medidos y ``medidas N de M exigibles`` —
            un verde siempre dice qué midió (ADR-G3a-02 §6). Sin claims de
            frescura: la procedencia del artefacto es G3a-2, no este comando.
    """

    failures: list[str]
    summary: list[str]


def interrogate_percent(text: str) -> float | None:
    """Extrae el 'actual: N%' de la salida de interrogate."""
    match = PERCENT.search(text)
    return float(match.group(1)) if match else None


def docstring_coverage(root: Path) -> float | None:
    """Cobertura de docstrings medida por interrogate (None si la tool falta)."""
    if shutil.which("interrogate") is None:
        return None
    completed = subprocess.run(
        ["interrogate", "src"], cwd=root, text=True, capture_output=True, check=False
    )
    return interrogate_percent(completed.stdout + completed.stderr)


def lcov_percent(text: str) -> float | None:
    """Porcentaje total de un lcov: (LH+BRH)/(LF+BRF) sumando por archivo.

    Es la misma razón (statements y arcos de rama) con la que coverage.py
    calcula la línea TOTAL del reporte term, así que ambas fuentes coinciden
    salvo el redondeo a entero del reporte.
    """
    totals = {"LF": 0, "LH": 0, "BRF": 0, "BRH": 0}
    for line in text.splitlines():
        match = LCOV_COUNTER.match(line)
        if match:
            totals[match.group(1)] += int(match.group(2))
    measurable = totals["LF"] + totals["BRF"]
    return 100.0 * (totals["LH"] + totals["BRH"]) / measurable if measurable else None


def coverage_total(root: Path) -> float | None:
    """Cobertura total medida del artefacto lcov del gate (None si no existe)."""
    artifact = root / LCOV_ARTIFACT
    if not artifact.is_file():
        return None
    return lcov_percent(artifact.read_text(encoding="utf-8"))


def _lcov_records(text: str) -> list[dict[str, str | int]]:
    """Registros SF→end_of_record de un lcov, con contadores acumulados.

    Los contadores repetidos dentro de un registro se suman (misma semántica
    que ``lcov_percent``); los contadores fuera de todo registro agrupan en
    uno ``(sin SF)``. Los registros vacíos aportan cero y son coherentes.
    """
    records: list[dict[str, str | int]] = []
    current: dict[str, str | int] = {"SF": "(sin SF)"}
    for line in text.splitlines():
        counter = LCOV_COUNTER.match(line)
        if line.startswith("SF:"):
            records.append(current)
            current = {"SF": line.removeprefix("SF:").strip()}
        elif counter is not None:
            key = counter.group(1)
            current[key] = int(current.get(key, 0)) + int(counter.group(2))
        elif line.strip() == "end_of_record":
            records.append(current)
            current = {"SF": "(sin SF)"}
    records.append(current)
    return records


def _record_defect(record: dict[str, str | int]) -> str | None:
    """Defecto de coherencia de un registro (None si 0≤LH≤LF y 0≤BRH≤BRF).

    Cubiertas-sin-total (``LH`` sin ``LF``, ``BRH`` sin ``BRF``) nombra la
    clave ausente con los valores ya presentes (SPEC-G3a-1, test 0g) — el
    total ausente no es 0. ``LF`` sin ``LH`` sigue VÁLIDO: 0 cubiertas de N
    no amplía el contrato de completitud.
    """
    source = str(record.get("SF", "(sin SF)"))
    for hits, total in (("LH", "LF"), ("BRH", "BRF")):
        if int(record.get(hits, 0)) > int(record.get(total, 0)):
            if total in record:
                return f"{hits} {record[hits]} > {total} {record[total]} en {source}"
            return f"{hits} {record[hits]} sin {total} en {source}"
    return None


def _malformed_counter_defect(text: str) -> str | None:
    """Primer renglón de contador malformado, nombrando contador y SF.

    Sigue los ``SF:`` del artefacto con la misma agrupación que
    ``_lcov_records`` (contadores fuera de todo registro: ``(sin SF)``): un
    renglón cuyo prefijo es un contador reconocido con valor que no es
    entero no-negativo es un defecto de medición, no una línea a ignorar.
    """
    source = "(sin SF)"
    for line in text.splitlines():
        if line.startswith("SF:"):
            source = line.removeprefix("SF:").strip()
        elif LCOV_MALFORMED_COUNTER.match(line):
            return f"contador {line} en {source}"
        elif line.strip() == "end_of_record":
            source = "(sin SF)"
    return None


def _coherence_defect(records: list[dict[str, str | int]]) -> str | None:
    """Defecto de coherencia de los registros acumulados (None si son válidos).

    Totales medibles (LF+BRF>0), rango [0, 100] del resultado y coherencia
    por registro (0≤LH≤LF, 0≤BRH≤BRF).
    """
    totals = {"LF": 0, "LH": 0, "BRF": 0, "BRH": 0}
    for record in records:
        for counter in totals:
            totals[counter] += int(record.get(counter, 0))
    measurable = totals["LF"] + totals["BRF"]
    if measurable == 0:
        return "LF+BRF == 0 en todos los registros"
    percent = PERCENT_MAX * (totals["LH"] + totals["BRH"]) / measurable
    if not 0.0 <= percent <= PERCENT_MAX:
        return f"total {percent:g}% fuera de [0, 100]"
    for record in records:
        if defect := _record_defect(record):
            return defect
    return None


def _lcov_defect(text: str) -> str | None:
    """Primer defecto del ARTEFACTO lcov (None si produce una medición válida).

    Validación exclusiva de la vía exigible (ADR-G3a-02 §5): primero los
    contadores malformados (nombre reconocido, valor que no es entero
    no-negativo — el parser histórico los ignora), luego la coherencia de
    los registros. ``lcov_percent`` y ``coverage_total`` — el modo tolerante
    — quedan intactos: no heredan esta validación.
    """
    if malformed := _malformed_counter_defect(text):
        return malformed
    return _coherence_defect(_lcov_records(text))


def _coverage_artifact_defect(root: Path, names: Sequence[str]) -> str | None:
    """Defecto del artefacto de coverage cuando la métrica es exigible.

    None cuando coverage-total no se exige o el artefacto no existe (esa
    ausencia la reporta ``_absent_failure``).
    """
    if "coverage-total" not in names:
        return None
    artifact = root / LCOV_ARTIFACT
    if not artifact.is_file():
        return None
    return _lcov_defect(artifact.read_text(encoding="utf-8"))


def suite_coverage_total(root: Path) -> float:
    """Corre la suite UNA vez y devuelve el piso preciso del JSON de coverage.

    Solo `record` la usa. ``percent_covered`` es el mismo valor que
    ``--cov-fail-under`` compara internamente; se trunca a 2 decimales hacia
    abajo para que el piso registrado nunca supere la medición precisa (el
    display del reporte term redondea a entero y podía fijar pisos
    inalcanzables). Registra solo corridas verdes.
    """
    artifact = root / RECORD_COVERAGE_JSON
    artifact.unlink(missing_ok=True)
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--cov",
            "--cov-branch",
            f"--cov-report=json:{RECORD_COVERAGE_JSON}",
            "-q",
            "-m",
            "not property",
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ValueError(
            "la suite bajo cobertura no paso; un piso se registra solo de corrida verde"
        )
    try:
        totals = json.loads(artifact.read_text(encoding="utf-8"))["totals"]
        precise = float(totals["percent_covered"])
    except (OSError, KeyError, TypeError, ValueError) as error:
        raise ValueError("la corrida de cobertura no produjo percent_covered") from error
    return math.floor(precise * 100) / 100


def measurements(root: Path) -> dict[str, float]:
    """Métricas actuales del repo: sin subprocess de suite (tier fast)."""
    architecture = analyze_architecture(root)
    tests = analyze_tests(root)
    metrics = {
        "suppressions": float(suppression_count(root)),
        "debt-markers": float(len(debt_findings(root))),
        "introverted-tests": float(tests["counts"].get("introverted", 0)),
        "archmetrics-zones": float(
            sum(item["zone"] != "healthy" for item in architecture["metrics"])
        ),
        "per-file-ignores": float(ignores_count(root)),
        "file-size": float(len(size_oversized(root)["files"])),
        "lcom-classes": float(len(scan_lcom(root)["violators"])),
        "dry-template-clusters": float(len(analyze_template(root)["candidates"])),
    }
    docstrings = docstring_coverage(root)
    if docstrings is not None:
        metrics["docstring-coverage"] = docstrings
    coverage = coverage_total(root)
    if coverage is not None:
        metrics["coverage-total"] = coverage
    return metrics


def _over_baseline(root: Path, name: str, current: float) -> str | None:
    """Línea de fallo por umbral vía ``compare`` productivo; None si se mantiene."""
    expected = baseline(root, name)
    if compare(current, expected):
        return None
    return f"{name}: actual={current:g}, baseline={expected['value']}"


def _validated_required(required: Sequence[str]) -> list[str]:
    """Valida y expande ``required`` según ADR-G3a-02 §1.

    Args:
        required: nombres exigidos tal como los pasó el operador; el token
            ``all`` expande al inventario completo.

    Returns:
        Los nombres exigidos, en orden estable.

    Raises:
        ValueError: lista vacía, nombre desconocido, ``all`` combinado con
            otras métricas, o duplicados — nunca colapsados en silencio.
    """
    valid = f"{', '.join(REQUIRED_INVENTORY)} (o 'all')"
    # "token" como nombre tropezaría el detector S105 de bandit (comparado
    # con un literal): el nombre no es una credencial, pero renombrar es más
    # barato que una supresión con ratchet (STYLE-008).
    requested = [entry.strip() for entry in required]
    if not requested or any(not entry for entry in requested):
        raise ValueError(f"--require vacío; exigibles: {valid}")
    unknown = sorted(
        entry for entry in requested if entry != "all" and entry not in REQUIRED_INVENTORY
    )
    if unknown:
        raise ValueError(f"--require desconocido: {', '.join(unknown)}; exigibles: {valid}")
    if "all" in requested and len(requested) > 1:
        raise ValueError(f"'all' no se combina con otras métricas; exigibles: {valid}")
    names = list(REQUIRED_INVENTORY) if "all" in requested else requested
    duplicated = sorted({name for name in names if names.count(name) > 1})
    if duplicated:
        raise ValueError(f"--require duplicado: {', '.join(duplicated)}; exigibles: {valid}")
    return names


def _absent_failure(name: str) -> str:
    """Bloqueo por exigible sin medición: métrica, causa y comando (ADR-G3a-02 §3).

    La causa distingue artefacto faltante o herramienta ausente (un artefacto
    existente pero defectuoso es "medición inválida", no ausencia); el comando
    es el que produce la medición. Texto distinto al de umbral para que "no
    medida" nunca se lea como "por encima".
    """
    if name == "coverage-total":
        return (
            f"{name}: exigible no medida (no existe build/coverage/lcov.info); "
            f"produce la medición: {_COVERAGE_TOTAL_COMMAND}"
        )
    if name == "docstring-coverage":
        cause = (
            "interrogate no está instalado"
            if shutil.which("interrogate") is None
            else "interrogate sin 'actual: N%' medible en su salida"
        )
        return f"{name}: exigible no medida ({cause}); produce la medición: interrogate src"
    command = _PRODUCE_COMMANDS.get(name, "wct ratchet check")
    return (
        f"{name}: exigible no medida (análisis no disponible en esta corrida); "
        f"produce la medición: {command}"
    )


@overload
def check(root: Path, required: None = None) -> list[str]: ...
@overload
def check(root: Path, required: Sequence[str]) -> RatchetReport: ...


def check(root: Path, required: Sequence[str] | None = None) -> list[str] | RatchetReport:
    """Compara las métricas medidas contra sus baselines.

    Args:
        root: raíz del proyecto a medir.
        required: nombres del inventario exigible (o ``all``). None mantiene
            el modo tolerante actual: solo opina sobre lo medido.

    Returns:
        Sin ``required``, la lista de fallos de umbral del modo tolerante
        (contrato actual). Con ``required``, un :class:`RatchetReport` con
        TODAS las comparaciones del modo tolerante (exigir es ADITIVO:
        añade obligaciones, jamás filtra ni apaga rojos, ADR-G3a-02 §4) más
        las obligaciones de presencia/validez de las exigibles, sin líneas
        duplicadas, y el resumen ``medidas N de M exigibles`` — presencia y
        umbral, SIN claim de frescura del artefacto (la procedencia es G3a-2).

    Raises:
        ValueError: entrada ``required`` inválida (vacía, desconocida o
            duplicada), nombrando los nombres válidos.
    """
    if required is None:
        failures: list[str] = []
        for name, current in measurements(root).items():
            if line := _over_baseline(root, name, current):
                failures.append(line)
        return failures
    return _required_report(root, _validated_required(required))


def _required_report(root: Path, names: list[str]) -> RatchetReport:
    """Modo exigible: comparaciones tolerantes completas + obligaciones.

    Primero TODAS las comparaciones del modo tolerante (mismas líneas, sobre
    todas las métricas medidas), luego presencia de las exigibles — así una
    métrica exigida y en rojo aparece UNA vez. Una medición de coverage
    INVÁLIDA reemplaza su comparación de umbral: comparar un valor imposible
    contra el baseline no dice nada (ADR-G3a-02 §5).
    """
    metrics = measurements(root)
    defect = _coverage_artifact_defect(root, names)
    blocking: list[str] = []
    for name, current in metrics.items():
        if defect is not None and name == "coverage-total":
            continue
        if line := _over_baseline(root, name, current):
            blocking.append(line)
    for name in names:
        if defect is not None and name == "coverage-total":
            blocking.append(f"{name}: medición inválida ({defect})")
        elif name not in metrics:
            blocking.append(_absent_failure(name))
    measured = [name for name in names if name in metrics]
    summary = [
        f"exigidas: {', '.join(names)}",
        f"medidas: {', '.join(measured) if measured else '(ninguna)'}",
        f"medidas {len(measured)} de {len(names)} exigibles",
    ]
    return RatchetReport(blocking, summary)


def _record_targets(root: Path, metric: str | None) -> dict[str, float]:
    """Métricas que este registro debe re-estampar (todas, o solo `metric`)."""
    current = measurements(root)
    if metric is None:
        return current
    if metric == "coverage-total":
        return {metric: suite_coverage_total(root)}
    if metric in current:
        return {metric: current[metric]}
    raise ValueError(
        f"métrica desconocida: {metric}; válidas: {', '.join(sorted({*current, 'coverage-total'}))}"
    )


def record(root: Path, approved_by: str, reason: str, metric: str | None = None) -> list[Path]:
    """Re-registra baselines con rastro de aprobación; con `metric`, solo el suyo."""
    if len(approved_by.strip()) < MIN_APPROVER or len(reason.strip()) < MIN_REASON:
        raise ValueError("approved-by y reason >=12 caracteres son obligatorios")
    require_approval_evidence(reason)
    written: list[Path] = []
    head = head_sha(root)
    provenance = head[:COMMIT_PROVENANCE_CHARS] if head else None
    for name, current in _record_targets(root, metric).items():
        path = root / "governance/baselines" / f"{name}.json"
        document = baseline(root, name)
        document.update(
            {
                "value": current,
                "recorded_at": datetime.now(UTC).isoformat(),
                "recorded_by": approved_by,
                "commit": provenance,
            }
        )
        path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(path)
    with (root / "governance/ratchet-log.md").open("a", encoding="utf-8") as stream:
        stream.write(
            f"\n## {datetime.now(UTC).isoformat()}\n\n"
            f"- Approved by: {approved_by}\n- Reason: {reason}\n"
        )
        if metric is not None:
            stream.write(f"- Metrics: {metric}\n")
    return written
