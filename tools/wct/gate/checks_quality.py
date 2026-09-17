"""Complejidad cognitiva y gates de calidad estructural."""

from __future__ import annotations

from pathlib import Path
import time

from tools.wct.cognitive.engine import scan as scan_cognitive
from tools.wct.dry.tpl import analyze_template
from tools.wct.gate.checks_debt import _declared, _result
from tools.wct.lcom.engine import scan as scan_lcom
from tools.wct.model import GateResult
from tools.wct.ratchet.engine import baseline, compare
from tools.wct.wire.engine import scan as scan_wire

XENON_FLAGS = ("--max-absolute", "--max-modules", "--max-average")

XENON_KEYS = ("xenon_max_absolute", "xenon_max_modules", "xenon_max_average")


def cognitive_command(root: Path) -> list[str] | None:
    """Invocación de xenon con los grados declarados (complexity.xenon_max_*)."""
    complexity = _declared(root, "complexity")
    command = ["xenon"]
    try:
        for flag, name in zip(XENON_FLAGS, XENON_KEYS, strict=True):
            grade = complexity[name]
            if grade is None:
                return None
            command.append(flag)
            command.append(str(grade))
    except (KeyError, TypeError):
        return None
    command.append("src")
    return command


def gate_cognitive(root: Path) -> GateResult:
    started = time.monotonic()
    report = scan_cognitive(root)
    findings = [
        f"{item['file']}:{item['line']}: {item['function']}: "
        f"cognitiva {item['score']} > {report['limit']}"
        for item in report["functions"]
    ]
    return _result("G-COGNITIVE", started, findings, "anidamiento dentro del umbral cognitivo")


def gate_wire(root: Path) -> GateResult:
    started = time.monotonic()
    report = scan_wire(root)
    findings = [
        f"{item['file']}:{item['line']}: {item['symbol']} ({item['origin']}): {item['rule']}"
        for item in report["findings"]
    ]
    return _result(
        "G-WIRE", started, findings, "inyección de dependencias limpia en domain y application"
    )


def gate_lcom(root: Path) -> GateResult:
    started = time.monotonic()
    report = scan_lcom(root)
    violators = report["violators"]
    base = baseline(root, "lcom-classes")
    findings = [
        f"{item['file']}:{item['line']}: {item['class']}: LCOM4={item['lcom4']} >= 2"
        for item in violators
    ]
    if not compare(len(violators), base):
        findings.append(f"ratchet: {len(violators)} > baseline {base['value']}")
    return _result("G-LCOM", started, findings, "cohesión de clases LCOM4 saludable")


def gate_dry_tpl(root: Path) -> GateResult:
    started = time.monotonic()
    report = analyze_template(root)
    candidates = report["candidates"]
    base = baseline(root, "dry-template-clusters")
    findings = list(report["errors"])
    if not compare(len(candidates), base):
        for item in candidates:
            findings.append(
                f"{item['left']['file']}:{item['left']['start']} ~ "
                f"{item['right']['file']}:{item['right']['start']} "
                f"score={item['score']}"
            )
        findings.append(f"ratchet: {len(candidates)} > baseline {base['value']}")
    return _result("G-DRY-TPL", started, findings, "sin clones de plantilla sobre la baseline")
