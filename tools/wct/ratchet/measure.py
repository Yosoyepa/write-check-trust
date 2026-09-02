from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

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
LCOV_ARTIFACT = Path("build/coverage/lcov.info")
LCOV_COUNTER = re.compile(r"^(LF|LH|BRF|BRH):(\d+)$")
TERM_TOTAL = re.compile(r"^TOTAL\b.*?(\d+(?:\.\d+)?)%\s*$", re.MULTILINE)


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


def suite_coverage_total(root: Path) -> float:
    """Corre la suite UNA vez y devuelve el TOTAL oficial del reporte term.

    Solo `record` la usa: es la fuente autoritativa (la misma que
    --cov-fail-under), jamás la ruta de medición de `measurements()`.
    """
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--cov",
            "--cov-branch",
            "--cov-report=term",
            "-q",
            "-m",
            "not property",
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    match = TERM_TOTAL.search(completed.stdout)
    if match is None:
        raise ValueError("la corrida de cobertura no produjo línea TOTAL (¿falló pytest?)")
    return float(match.group(1))


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


def check(root: Path) -> list[str]:
    failures: list[str] = []
    for name, current in measurements(root).items():
        expected = baseline(root, name)
        if not compare(current, expected):
            failures.append(f"{name}: actual={current:g}, baseline={expected['value']}")
    return failures


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
