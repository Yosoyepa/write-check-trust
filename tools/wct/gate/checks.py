"""Gates puros de analyzer: sin subprocess, sin dependencias del registro.

Viven separados de runner.py (partición fachada, TEST-007): runner conserva
el registro, los tiers, los gates que disparan procesos y los que los tests
parchean por ruta de módulo.
"""

from __future__ import annotations

from pathlib import Path
import time

from tools.wct.accept.pipeline import ir_dry, parse_feature
from tools.wct.archmetrics.analyzer import analyze as analyze_architecture
from tools.wct.cognitive.engine import scan as scan_cognitive
from tools.wct.dry.analyzer import analyze as analyze_dry
from tools.wct.integrity.engine import violations as integrity_violations
from tools.wct.introvert.analyzer import analyze as analyze_tests
from tools.wct.model import GateResult, Status
from tools.wct.ratchet.engine import (
    baseline,
    compare,
    debt_findings,
    ignores_count,
    ignores_findings,
    suppression_count,
    suppression_findings,
)
from tools.wct.rules.engine import drift
from tools.wct.size.engine import oversized as size_oversized


def _result(gate_id: str, started: float, findings: list[str], ok: str) -> GateResult:
    status = Status.FAIL if findings else Status.PASS
    return GateResult(
        gate_id,
        status,
        findings[0] if findings else ok,
        int((time.monotonic() - started) * 1000),
        findings[:50],
    )


def gate_meta_integrity(root: Path) -> GateResult:
    started = time.monotonic()
    return _result(
        "G-META-1",
        started,
        integrity_violations(root),
        "configuración protegida coincide con integrity.lock",
    )


def gate_rules_drift(root: Path) -> GateResult:
    started = time.monotonic()
    findings = [f"regla generada ausente o divergente: {p.relative_to(root)}" for p in drift(root)]
    return _result("G-RULES-DRIFT", started, findings, "copias por proveedor sincronizadas")


def gate_suppressions(root: Path) -> GateResult:
    started = time.monotonic()
    findings = suppression_findings(root) + ignores_findings(root)
    current = suppression_count(root)
    base = baseline(root, "suppressions")
    if not compare(current, base):
        findings.append(f"ratchet: {current} > baseline {base['value']}")
    ignored = ignores_count(root)
    ignores_base = baseline(root, "per-file-ignores")
    if not compare(ignored, ignores_base):
        findings.append(f"ratchet per-file-ignores: {ignored} > baseline {ignores_base['value']}")
    return _result("G-SUPPRESS", started, findings, "sin erosión por supresiones")


def gate_debt(root: Path) -> GateResult:
    started = time.monotonic()
    findings = debt_findings(root)
    base = baseline(root, "debt-markers")
    if not compare(len(findings), base):
        findings.append(f"ratchet: {len(findings)} > baseline {base['value']}")
    return _result("G-DEBT", started, findings, "deuda diferida trazable")


def gate_archmetrics(root: Path) -> GateResult:
    started = time.monotonic()
    report = analyze_architecture(root)
    findings = list(report["violations"])
    zones = [item for item in report["metrics"] if item["zone"] != "healthy"]
    if not compare(len(zones), baseline(root, "archmetrics-zones")):
        findings.extend(
            f"{item['package']}: zone={item['zone']} D={item['distance']:.3f}" for item in zones
        )
    return _result(
        "G-ARCHMETRICS",
        started,
        findings,
        "dependency graph y métricas A/I/D saludables",
    )


def gate_dry(root: Path) -> GateResult:
    started = time.monotonic()
    report = analyze_dry(root)
    findings = list(report["errors"])
    for item in report["candidates"]:
        if item["ai_actionability"] == "EXTRACT":
            findings.append(
                f"{item['left']['file']}:{item['left']['start']} ~ "
                f"{item['right']['file']}:{item['right']['start']} "
                f"score={item['score']} pressure={item['extraction_pressure']}"
            )
    return _result("G-DRY", started, findings, "sin duplicación estructural accionable")


def gate_introvert(root: Path) -> GateResult:
    started = time.monotonic()
    report = analyze_tests(root)
    current = int(report["counts"].get("introverted", 0))
    base = baseline(root, "introverted-tests")
    findings = [
        f"{item['file']}:{item['line']}: {item['test']}: {item['reason']}"
        for item in report["tests"]
        if item["verdict"] == "introverted"
    ]
    if compare(current, base):
        findings = []
    return _result("G-INTROVERT", started, findings, "honestidad de tests no retrocede")


def gate_accept(root: Path) -> GateResult:
    started = time.monotonic()
    findings: list[str] = []
    for path in sorted((root / "features").glob("*.feature")):
        try:
            report = ir_dry(parse_feature(path))
            findings.extend(
                f"{path.relative_to(root)}:{item['line']}: {item['kind']}: {item['message']}"
                for item in report["findings"]
            )
        except ValueError as exc:
            findings.append(str(exc))
    return _result("G-ACCEPT", started, findings, "Gherkin parseable y sin repetición estructural")


def gate_size(root: Path) -> GateResult:
    started = time.monotonic()
    report = size_oversized(root)
    base = baseline(root, "file-size")
    allowed = {str(name) for name in base["files"]}
    findings = [
        f"{item['file']}: {item['loc']} LOC > límite {report['limit']}"
        for item in report["files"]
        if item["file"] not in allowed
    ]
    if not compare(len(report["files"]), base):
        findings.append(f"ratchet: {len(report['files'])} > baseline {base['value']}")
    return _result("G-SIZE", started, findings, "archivos dentro del presupuesto de líneas")


def gate_cognitive(root: Path) -> GateResult:
    started = time.monotonic()
    report = scan_cognitive(root)
    findings = [
        f"{item['file']}:{item['line']}: {item['function']}: "
        f"cognitiva {item['score']} > {report['limit']}"
        for item in report["functions"]
    ]
    return _result("G-COGNITIVE", started, findings, "anidamiento dentro del umbral cognitivo")
