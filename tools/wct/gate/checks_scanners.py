"""Gates analizadores: archmetrics, DRY, introvertidos, aceptación y tamaño."""

from __future__ import annotations

from pathlib import Path
import time

from tools.wct.accept.pipeline import ir_dry, parse_feature
from tools.wct.archmetrics.analyzer import analyze as analyze_architecture
from tools.wct.dry.analyzer import analyze as analyze_dry
from tools.wct.gate.checks_debt import _result
from tools.wct.introvert.analyzer import analyze as analyze_tests
from tools.wct.model import GateResult
from tools.wct.ratchet.engine import baseline, compare
from tools.wct.size.engine import oversized as size_oversized


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
