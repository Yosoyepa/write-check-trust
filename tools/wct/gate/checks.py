"""Gates puros de analyzer: sin subprocess, sin dependencias del registro.

Viven separados de runner.py (partición fachada, TEST-007): runner conserva
el registro, los tiers, los gates que disparan procesos y los que los tests
parchean por ruta de módulo.
"""

from __future__ import annotations

from pathlib import Path
import time
from typing import Any

from tools.wct.accept.pipeline import ir_dry, parse_feature
from tools.wct.archmetrics.analyzer import analyze as analyze_architecture
from tools.wct.cognitive.engine import scan as scan_cognitive
from tools.wct.config import ConfigError, load_config
from tools.wct.dry.analyzer import analyze as analyze_dry
from tools.wct.dry.tpl import analyze_template
from tools.wct.integrity.engine import violations as integrity_violations
from tools.wct.introvert.analyzer import analyze as analyze_tests
from tools.wct.lcom.engine import scan as scan_lcom
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
from tools.wct.wire.engine import scan as scan_wire


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


COVERAGE_TOTAL_BASELINE = "governance/baselines/coverage-total.json"


def coverage_total_command(root: Path) -> list[str] | None:
    """Invocación de pytest con el piso del baseline de coverage-total.

    None cuando el baseline falta o es ilegible: el caller lo declara como
    FAIL nombrando la ruta, nunca corre sin piso (ADR-A2-01).
    """
    try:
        floor = float(baseline(root, "coverage-total")["value"])
    except (OSError, TypeError, KeyError, ValueError):
        return None
    return [
        "pytest",
        "--cov",
        "--cov-branch",
        "--cov-report=lcov:build/coverage/lcov.info",
        "--cov-fail-under",
        str(floor),
        "-q",
        "-m",
        "not property",
    ]


def _declared(root: Path, *path: str) -> Any:
    """Valor declarado en thresholds.yaml; None si falta o es ilegible.

    Contrato ADR-B-01 §3: el caller declara el None como FAIL nombrando la
    clave — el gate nunca corre con un valor por defecto silencioso.
    """
    try:
        _project, _policy, thresholds = load_config(root)
        value: Any = thresholds
        for key in path:
            value = value[key]
    except (ConfigError, KeyError, TypeError):
        return None
    return value


def crap_command(root: Path) -> list[str] | None:
    """Invocación de crap4py con el umbral declarado (crap.changed_max).

    None cuando la clave falta o es ilegible: el caller lo declara como
    FAIL nombrando la clave (contrato ADR-B-01 §3).
    """
    max_crap = _declared(root, "crap", "changed_max")
    if max_crap is None:
        return None
    return [
        "crap4py",
        "src",
        "--lcov",
        "build/coverage/lcov.info",
        "--max-crap",
        str(max_crap),
    ]


def coverage_diff_command(root: Path, base: str) -> list[str] | None:
    """Invocación de diff-cover con el piso declarado (coverage.diff_min).

    `base` es la rama contra la que CI compara (remote_base la resuelve);
    None cuando la clave falta o es ilegible, con el contrato de crap_command.
    """
    diff_min = _declared(root, "coverage", "diff_min")
    if diff_min is None:
        return None
    return [
        "diff-cover",
        "build/coverage/lcov.info",
        "--compare-branch",
        base,
        "--fail-under",
        str(diff_min),
        "--include-untracked",
    ]


def dead_code_command(root: Path) -> list[str] | None:
    """Invocación de vulture con la confianza y whitelist declaradas.

    La whitelist (``dead_code.whitelist``, ADR-D-02) viaja SOLO cuando la
    clave existe en thresholds.yaml (patrón PR-B: clave ausente → sin ella,
    sin default silencioso). Se pasa como path posicional porque vulture
    2.16 no tiene flag ``--whitelist``: los nombres referenciados en un
    archivo escaneado cuentan como usados. La ruta es relativa al root
    porque el gate corre con ``cwd=root``.
    """
    confidence = _declared(root, "dead_code", "vulture_min_confidence")
    if confidence is None:
        return None
    command = ["vulture", "src", "tools/wct"]
    whitelist = _declared(root, "dead_code", "whitelist")
    if whitelist is not None:
        command.append(str(whitelist))
    command += ["--min-confidence", str(confidence)]
    return command


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
