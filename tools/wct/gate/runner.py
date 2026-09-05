"""Registro de gates, tiers y orquestación.

Partición fachada (TEST-007): los gates puros de analyzer viven en
checks.py y la metadata de capacidades en capabilities.py; aquí quedan el
registro, los gates que disparan procesos externos y los que los tests
parchean por ruta de módulo.
"""

from __future__ import annotations

from collections.abc import Callable
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from tools.wct.config import load_config
from tools.wct.gate.capabilities import GateInfo, declares, gate_info, stamped
from tools.wct.gate.checks import (
    COVERAGE_TOTAL_BASELINE,
    _result,
    cognitive_command,
    coverage_diff_command,
    coverage_total_command,
    crap_command,
    dead_code_command,
    gate_accept,
    gate_archmetrics,
    gate_cognitive,
    gate_debt,
    gate_dry,
    gate_dry_tpl,
    gate_introvert,
    gate_lcom,
    gate_meta_integrity,
    gate_rules_drift,
    gate_size,
    gate_suppressions,
    gate_wire,
)
from tools.wct.gate.exec import _captured
from tools.wct.gate.mutation import gate_mutation
from tools.wct.model import GateResult, Status
from tools.wct.mutate.engine import scan as scan_mutations
from tools.wct.ratchet.engine import baseline
from tools.wct.rules.engine import rule_documents
from tools.wct.util.git import remote_base

Gate = Callable[[Path], GateResult]


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


def dynamic(
    gate_id: str,
    executable: str,
    builder: Callable[[Path], list[str] | None],
    key: str = "",
    *,
    optional: bool = False,
) -> Gate:
    """Gate cuyo comando resuelve builder(root) — estático o desde thresholds.yaml.

    Ciclo de vida: herramienta ausente → ERROR (o SKIP si es optional);
    builder None → FAIL nombrando la clave declarada, nunca un default
    silencioso (ADR-B-01 §3); y la corrida del proceso externo.

    Estampa GateInfo con el ejecutable que YA conoce: la herramienta vive
    donde se resuelve, no en una tabla paralela (ADR-D-01).
    """

    def run(root: Path) -> GateResult:
        started = time.monotonic()
        if shutil.which(executable) is None:
            status = Status.SKIP if optional else Status.ERROR
            return GateResult(gate_id, status, f"herramienta ausente: {executable}")
        command = builder(root)
        if command is None:
            return GateResult(gate_id, Status.FAIL, f"clave ausente o ilegible: {key}")
        status, summary, output = _captured(root, command)
        return GateResult(
            gate_id,
            status,
            summary,
            int((time.monotonic() - started) * 1000),
            output.splitlines()[-50:],
            " ".join(command),
        )

    return stamped(run, GateInfo((executable,)))


def external(
    gate_id: str, command: list[str], *, optional: bool = False, scope: tuple[str, ...] = ()
) -> Gate:
    """Gate de comando estático: la invocación no depende de thresholds.yaml."""
    return declares(
        dynamic(gate_id, command[0], lambda _root: command, optional=optional), scope=scope
    )


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


def gate_audit(root: Path) -> GateResult:
    """Audit only deployable dependencies exported from the locked graph."""
    started = time.monotonic()
    for executable in ("uv", "pip-audit"):
        if shutil.which(executable) is None:
            return GateResult("G-AUDIT", Status.ERROR, f"herramienta ausente: {executable}")
    exported = subprocess.run(
        [
            "uv",
            "export",
            "--frozen",
            "--no-dev",
            "--no-emit-project",
            "--no-hashes",
            "--format",
            "requirements.txt",
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if exported.returncode:
        return _result("G-AUDIT", started, [exported.stderr.strip()], "")
    with tempfile.TemporaryDirectory(prefix="wct-audit-") as directory:
        requirements = Path(directory) / "requirements.txt"
        requirements.write_text(exported.stdout, encoding="utf-8")
        audited = subprocess.run(
            ["pip-audit", "--requirement", str(requirements)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
    output = (audited.stdout + "\n" + audited.stderr).strip()
    findings = output.splitlines() if audited.returncode else []
    return _result("G-AUDIT", started, findings, "dependencias desplegables sin CVEs conocidas")


def _audited_secrets(root: Path) -> set[tuple[str, str]]:
    """Read-only set of (filename, hashed_secret) already triaged by a human.

    The baseline is NOT passed as --baseline to detect-secrets: that flag
    REWRITES the file (it refreshes generated_at on every run), and the
    baseline lives on a G-META-1 protected route, so the gate must never
    dirty it.
    """
    secrets_baseline = root / ".secrets.baseline"
    if not secrets_baseline.is_file():
        return set()
    document = json.loads(secrets_baseline.read_text(encoding="utf-8"))
    return {
        (filename, str(item.get("hashed_secret", "")))
        for filename, items in document.get("results", {}).items()
        for item in items
    }


# Rutas que G-SECRET escanea (runner) y declara como scope (REGISTRY):
# una sola definición para que el comando y el perfil no diverjan.
SECRET_PATHS = (
    "src",
    "tools",
    "governance",
    ".claude",
    "skills",
    "plugins",
    ".github",
    "pyproject.toml",
    ".pre-commit-config.yaml",
)


def gate_secrets(root: Path) -> GateResult:
    started = time.monotonic()
    if shutil.which("detect-secrets") is None:
        return GateResult("G-SECRET", Status.ERROR, "herramienta ausente: detect-secrets")
    paths = list(SECRET_PATHS)
    # governance/generated/ y governance/baselines/ contienen artefactos
    # regenerados por las propias herramientas: fingerprints sha256 del
    # manifiesto de mutación los primeros, SHAs cortos de procedencia que
    # escribe ``wct ratchet record`` los segundos. Ambos son hex de alta
    # entropía por diseño, no secretos; auditarlos en el baseline sería
    # fricción en cada regeneración. Incidente PR #32: el SHA de 12 chars
    # de dry-template-clusters.json cruzó el límite 3.0 de HexHighEntropy
    # por azar de entropía (el de coverage-total no) — re-acortar el SHA
    # sería churn que reaparece al azar, no una garantía.
    completed = subprocess.run(
        [
            "detect-secrets",
            "scan",
            "--slim",
            "--exclude-files",
            "^(governance/generated|governance/baselines)/",
            *paths,
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        return _result("G-SECRET", started, [completed.stderr.strip()], "")
    # Con todos los hallazgos auditados en el baseline, detect-secrets emite
    # stdout vacío (exit 0): eso significa "sin hallazgos", no un error.
    raw = completed.stdout.strip()
    document = json.loads(raw) if raw else {}
    results = document.get("results", {})
    audited = _audited_secrets(root)
    findings = [
        # --slim omite line_number; se reporta "?" cuando no está disponible.
        f"{filename}:{item.get('line_number', '?')}: posible {item['type']}"
        for filename, items in results.items()
        for item in items
        if (filename, str(item.get("hashed_secret", ""))) not in audited
    ]
    return _result("G-SECRET", started, findings, "sin secretos nuevos")


def gate_docstrings(root: Path) -> GateResult:
    """El piso vive en la baseline de ratchet (docstring-coverage), no en el comando."""
    started = time.monotonic()
    if shutil.which("interrogate") is None:
        return GateResult("G-DOC", Status.SKIP, "herramienta ausente: interrogate")
    floor = int(float(baseline(root, "docstring-coverage")["value"]))
    command = ["interrogate", "src", "--fail-under", str(floor)]
    status, summary, output = _captured(root, command)
    return GateResult(
        "G-DOC",
        status,
        summary,
        int((time.monotonic() - started) * 1000),
        output.splitlines()[-50:],
        " ".join(command),
    )


def alias(gate_id: str, target: Gate) -> Gate:
    """Envuelve un gate bajo otro id, heredando su capacidad declarada."""

    def run(root: Path) -> GateResult:
        result = target(root)
        return GateResult(
            gate_id,
            result.status,
            result.summary,
            result.duration_ms,
            result.details,
            result.command,
        )

    marked = gate_info(target)
    return stamped(run, marked) if marked else run


# Scopes verificados contra los comandos/analizadores reales (SPEC-D-01 paso 0):
# los external/dynamic citan los args de rutas de su comando; los analizadores
# puros citan las policy.paths que su motor recorre. Gates de configuración
# (G-META-*), drift de reglas y orquestadores sin rutas propias (G-SBOM,
# G-COMMIT-MSG, G-AUDIT, G-COV-DIFF, G-ACCEPT-MUT, G-REDTEAM, G-HOOKS-WIRED)
# no declaran scope.
REGISTRY: dict[str, Gate] = {
    "G-META-1": gate_meta_integrity,
    "G-META-2": gate_meta_rules,
    "G-RULES-DRIFT": gate_rules_drift,
    "G-SUPPRESS": declares(gate_suppressions, scope=("src", "tests")),
    "G-DEBT": declares(gate_debt, scope=("src", "tests")),
    "G-LINT": external(
        "G-LINT",
        ["ruff", "check", "--config", "governance/lint/ruff.toml", "."],
        scope=(".",),
    ),
    "G-FMT": external(
        "G-FMT",
        ["ruff", "format", "--config", "governance/lint/ruff.toml", "--check", "."],
        scope=(".",),
    ),
    "G-TYPE": external("G-TYPE", ["mypy", "tools/wct", "src"], scope=("tools/wct", "src")),
    "G-TEST": external(
        "G-TEST",
        ["pytest", "-q", "tests/unit", "tests/integration", "-m", "not property"],
        scope=("tests/unit", "tests/integration"),
    ),
    "G-ARCH": external("G-ARCH", ["lint-imports"], scope=("src/example",)),
    "G-DEPS": external(
        "G-DEPS",
        [
            "deptry",
            "src",
            "tools",
            "--known-first-party",
            "example",
            "--known-first-party",
            "tools",
        ],
        scope=("src", "tools"),
    ),
    "G-DEAD": declares(
        dynamic("G-DEAD", "vulture", dead_code_command, "dead_code.vulture_min_confidence"),
        scope=("src", "tools/wct"),
    ),
    "G-SAST-BANDIT": external("G-SAST-BANDIT", ["bandit", "-q", "-r", "src"], scope=("src",)),
    "G-SAST-SEMGREP": external(
        "G-SAST-SEMGREP",
        ["semgrep", "--quiet", "--error", "--severity", "ERROR", "--config", "governance/semgrep"],
        optional=True,
        scope=(".",),
    ),
    "G-AUDIT": declares(gate_audit, tools=("uv", "pip-audit")),
    "G-ARCHMETRICS": declares(gate_archmetrics, scope=("src/example",)),
    "G-DRY": declares(gate_dry, scope=("src",)),
    "G-DRY-TPL": declares(gate_dry_tpl, scope=("src", "tools")),
    "G-INTROVERT": declares(gate_introvert, scope=("tests",)),
    "G-MUT-SITES": declares(gate_mutation_sites, scope=("src",)),
    "G-ACCEPT": declares(gate_accept, scope=("features",)),
    "G-SIZE": declares(gate_size, scope=("src", "tools")),
    "G-COGNITIVE": declares(gate_cognitive, scope=("src",)),
    "G-LCOM": declares(gate_lcom, scope=("src", "tools")),
    "G-WIRE": declares(gate_wire, scope=("src/example/domain", "src/example/application")),
    "G-CRAP": declares(
        dynamic("G-CRAP", "crap4py", crap_command, "crap.changed_max", optional=True),
        scope=("src",),
    ),
    "G-CC": declares(
        dynamic("G-CC", "xenon", cognitive_command, "complexity.xenon_max_*", optional=True),
        scope=("src",),
    ),
    "G-COV-TOTAL": declares(
        dynamic("G-COV-TOTAL", "pytest", coverage_total_command, COVERAGE_TOTAL_BASELINE),
        scope=("src", "tools/wct"),
    ),
    "G-COV-DIFF": declares(gate_coverage_diff, tools=("diff-cover",)),
    "G-DOC": declares(gate_docstrings, tools=("interrogate",), scope=("src",)),
    "G-SECRET": declares(gate_secrets, tools=("detect-secrets",), scope=SECRET_PATHS),
    "G-PROP": external("G-PROP", ["pytest", "-q", "tests/property"], scope=("tests/property",)),
    "G-TEST-RANDOM": external(
        "G-TEST-RANDOM", ["pytest", "-q", "--randomly-seed=last"], optional=True, scope=("tests",)
    ),
    # --exit-code 1: sin esa bandera jscpd sale 0 aunque encuentre clones
    # (verificado empíricamente) y el gate sería vacío. CON la bandera es
    # tolerancia cero: cualquier clon a 70+ tokens falla (el "threshold" de
    # .jscpd.json solo afecta el reporte, no el exit — también verificado).
    "G-DRY-TOK": external(
        "G-DRY-TOK",
        ["jscpd", "src", "tools", "--exit-code", "1"],
        optional=True,
        scope=("src", "tools"),
    ),
    "G-SBOM": external(
        "G-SBOM", ["cyclonedx-py", "environment", "--output-file", "build/sbom.json"], optional=True
    ),
    "G-COMMIT-MSG": external(
        "G-COMMIT-MSG", ["cz", "check", "--commit-msg-file", ".git/COMMIT_EDITMSG"], optional=True
    ),
    "G-MUT": declares(gate_mutation, tools=("mutmut",), scope=("src/example",)),
    "G-ACCEPT-MUT": external("G-ACCEPT-MUT", ["wct", "accept", "mutate"], optional=True),
    "G-REDTEAM": external("G-REDTEAM", ["wct", "selftest", "redteam"]),
}

REGISTRY.update(
    {
        "G-ARCH-CYCLE": alias("G-ARCH-CYCLE", gate_archmetrics),
        "G-CVE": alias("G-CVE", REGISTRY["G-AUDIT"]),
        "G-HOOKS-WIRED": external("G-HOOKS-WIRED", ["wct", "doctor"], optional=False),
        "G-IMPORT-ORDER": alias("G-IMPORT-ORDER", REGISTRY["G-LINT"]),
        "G-RULES-SYNC": alias("G-RULES-SYNC", gate_rules_drift),
        "G-SAST": alias("G-SAST", REGISTRY["G-SAST-BANDIT"]),
        "G-TEST-FAST": alias("G-TEST-FAST", REGISTRY["G-TEST"]),
        "G-TODO": alias("G-TODO", gate_debt),
    }
)

_COMMIT_GATES = [
    "G-META-1",
    "G-META-2",
    "G-RULES-DRIFT",
    "G-SUPPRESS",
    "G-DEBT",
    "G-LINT",
    "G-FMT",
    "G-TYPE",
    "G-TEST",
    "G-ARCH",
    "G-ARCHMETRICS",
    "G-DEPS",
    "G-DEAD",
    "G-SAST-BANDIT",
    "G-SECRET",
    "G-MUT-SITES",
    "G-ACCEPT",
    "G-SIZE",
    "G-COGNITIVE",
    "G-WIRE",
]

TIERS: dict[str, list[str]] = {
    "fast": [
        "G-META-2",
        "G-RULES-DRIFT",
        "G-SUPPRESS",
        "G-DEBT",
        "G-LINT",
        "G-FMT",
        "G-TYPE",
    ],
    "commit": list(_COMMIT_GATES),
    "full": [
        *_COMMIT_GATES,
        "G-COV-TOTAL",
        "G-MUT",
        "G-CRAP",
        "G-CC",
        "G-DRY",
        "G-DRY-TOK",
        "G-DRY-TPL",
        "G-INTROVERT",
        "G-LCOM",
        "G-SAST-SEMGREP",
        "G-AUDIT",
        "G-SBOM",
        "G-DOC",
        "G-REDTEAM",
    ],
    # Espejo local de quality.yml en PRs: todo lo que CI exige de una PR,
    # ejecutable con un solo comando antes de pushear.
    "pr": [
        *_COMMIT_GATES,
        "G-HOOKS-WIRED",
        "G-COV-TOTAL",
        "G-COV-DIFF",
        "G-PROP",
        "G-ACCEPT-MUT",
        "G-REDTEAM",
    ],
}


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
