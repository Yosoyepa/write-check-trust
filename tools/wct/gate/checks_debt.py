"""Comandos de deuda: cobertura, CRAP, código muerto, supresiones y metas."""

from __future__ import annotations

from pathlib import Path
import time
from typing import Any

from tools.wct.config import ConfigError, load_config
from tools.wct.integrity.engine import violations as integrity_violations
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
    clave — el gate nunca corre con un valor por defecto silencioso. Un
    root explícito sin gobernanza propia no asciende: leer los umbrales de
    un ancestro declararía configuración ajena como propia (FI1).
    """
    if not (root / "governance" / "policy.yaml").is_file():
        return None
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


COVERAGE_TOTAL_BASELINE = "governance/baselines/coverage-total.json"
