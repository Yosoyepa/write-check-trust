"""Registro de gates, tiers y orquestación (fachada TEST-007).

Los gates puros de analizador viven en checks.py y la metadata de
capacidades en capabilities.py; aquí quedan el registro compuesto, los
gates que disparan procesos externos y los que los tests parchean por
ruta de módulo. Los atributos shutil y subprocess se conservan como
superficie de parche (tests/unit vía rutas tools.wct.gate.runner.*).
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import time

from tools.wct.config import load_config
from tools.wct.gate.capabilities import declares
from tools.wct.gate.checks import _result, coverage_diff_command
from tools.wct.gate.exec import _captured
from tools.wct.gate.mutation import gate_mutation
from tools.wct.gate.registry_derived import derived
from tools.wct.gate.registry_process import REGISTRY as _PROCESS_REGISTRY
from tools.wct.gate.registry_static import REGISTRY as _STATIC_REGISTRY
from tools.wct.gate.runner_audit import gate_audit
from tools.wct.gate.runner_docstrings import gate_docstrings
from tools.wct.gate.runner_secrets import SECRET_PATHS, _audited_secrets, gate_secrets
from tools.wct.gate.runner_support import Gate, alias, dynamic, external
from tools.wct.gate.semgrep import gate_sast_semgrep
from tools.wct.gate.tier_map import _COMMIT_GATES, TIERS
from tools.wct.model import GateResult, Status
from tools.wct.mutate.engine import scan as scan_mutations
from tools.wct.rules.engine import rule_documents
from tools.wct.util.git import remote_base


def gate_meta_rules(root: Path) -> GateResult:
    started = time.monotonic()
    known = set(REGISTRY) | {"human"}
    findings: list[str] = []
    for document in rule_documents(root):
        for rule in document.get("rules", []):
            checks = rule.get("verified_by")
            if not checks:
                findings.append(f"{rule.get('id', '?')}: falta verified_by")
                continue
            unknown = sorted(set(checks) - known)
            if unknown:
                findings.append(f"{rule['id']}: gates desconocidos: {', '.join(unknown)}")
    return _result(
        "G-META-2",
        started,
        findings,
        "todas las reglas nombran verificadores conocidos",
    )


MANIFEST_DIAGNOSTICS = {
    "legacy": (
        "manifiesto schema 1: toda función cuenta como cambiada; "
        "regenera con 'wct mutate update-manifest'"
    ),
    "missing": (
        "manifiesto ausente: toda función cuenta como cambiada; "
        "genera con 'wct mutate update-manifest'"
    ),
}


def gate_coverage_diff(root: Path) -> GateResult:
    """Hard diff-cover sobre las líneas cambiadas, con base fiel a CI.

    El piso nace de thresholds.yaml (coverage.diff_min, ADR-B-01): clave
    ausente → FAIL nombrándola, nunca un default silencioso. Bloquea como
    ERROR (no SKIP) porque su tier promete paridad local con CI, y sin rama
    base no hay diff que auditar. Requiere que G-COV-TOTAL haya producido
    build/coverage/lcov.info primero (el orden del tier lo garantiza).
    """
    started = time.monotonic()
    if shutil.which("diff-cover") is None:
        return GateResult("G-COV-DIFF", Status.ERROR, "herramienta ausente: diff-cover")
    base = remote_base(root)
    if base is None:
        return GateResult(
            "G-COV-DIFF",
            Status.ERROR,
            "sin rama base resoluble: no encontré origin/main ni main",
        )
    command = coverage_diff_command(root, base)
    if command is None:
        return GateResult(
            "G-COV-DIFF",
            Status.FAIL,
            "clave ausente o ilegible: coverage.diff_min",
        )
    status, summary, output = _captured(root, command)
    return GateResult(
        "G-COV-DIFF",
        status,
        summary,
        int((time.monotonic() - started) * 1000),
        output.splitlines()[-50:],
        " ".join(command),
    )


def gate_mutation_sites(root: Path) -> GateResult:
    started = time.monotonic()
    report = scan_mutations(root)
    # TEST-007 aplica a archivos CAMBIADOS: un archivo legacy sobre el límite
    # solo bloquea si el diff tocó alguna de sus funciones (manifiesto
    # diferencial en governance/generated/mutation-manifest.json). Un archivo
    # nuevo sobre el límite tiene todas sus funciones "cambiadas" y bloquea.
    findings = [
        f"{item['file']}: excede max_sites_per_file con funciones cambiadas"
        for item in report["files"]
        if item["over_limit"] and item["changed_functions"]
    ]
    diagnostic = MANIFEST_DIAGNOSTICS.get(report.get("manifest") or "")
    if findings and diagnostic:
        findings.insert(0, diagnostic)
    return _result("G-MUT-SITES", started, findings, "archivos dentro del presupuesto de mutación")


def run_tier(root: Path, tier: str) -> list[GateResult]:
    _root, policy, _thresholds = load_config(root)
    required = policy.get("environment_required", {}).get(tier, [])
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        return [
            GateResult(
                "G-ENV",
                Status.ERROR,
                f"variables de entorno ausentes para el tier {tier}: {', '.join(missing)}",
            )
        ]
    disabled = set(policy.get("gates", {}).get("disabled", []))
    results: list[GateResult] = []
    for gate_id in TIERS[tier]:
        if gate_id in disabled:
            results.append(GateResult(gate_id, Status.SKIP, "desactivado por policy.yaml"))
        else:
            try:
                results.append(REGISTRY[gate_id](root))
            except Exception as exc:  # fail closed: harness errors are blocking
                results.append(
                    GateResult(
                        gate_id,
                        Status.ERROR,
                        f"guard crash: {type(exc).__name__}: {exc}",
                    )
                )
    return results


REGISTRY: dict[str, Gate] = {**_STATIC_REGISTRY, **_PROCESS_REGISTRY}
REGISTRY.update(derived(REGISTRY))
# Entradas de gates residentes en la fachada: los tests los parchean por
# nombre en este módulo (remote_base/scan_mutations/REGISTRY), de modo que
# componerse aquí evita que los submódulos importen hacia arriba (cero ciclos).
REGISTRY["G-META-2"] = gate_meta_rules
REGISTRY["G-MUT-SITES"] = declares(gate_mutation_sites, scope=("src",))
REGISTRY["G-COV-DIFF"] = declares(gate_coverage_diff, tools=("diff-cover",))


__all__ = [
    "MANIFEST_DIAGNOSTICS",
    "REGISTRY",
    "SECRET_PATHS",
    "TIERS",
    "_COMMIT_GATES",
    "Gate",
    "_audited_secrets",
    "alias",
    "dynamic",
    "external",
    "gate_audit",
    "gate_coverage_diff",
    "gate_docstrings",
    "gate_meta_rules",
    "gate_mutation",
    "gate_mutation_sites",
    "gate_sast_semgrep",
    "gate_secrets",
    "run_tier",
    "subprocess",
]
