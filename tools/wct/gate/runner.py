from __future__ import annotations

from collections.abc import Callable
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from tools.wct.accept.pipeline import ir_dry, parse_feature
from tools.wct.archmetrics.analyzer import analyze as analyze_architecture
from tools.wct.config import load_config
from tools.wct.dry.analyzer import analyze as analyze_dry
from tools.wct.integrity.engine import violations as integrity_violations
from tools.wct.introvert.analyzer import analyze as analyze_tests
from tools.wct.model import GateResult, Status
from tools.wct.mutate.engine import scan as scan_mutations
from tools.wct.ratchet.engine import (
    baseline,
    compare,
    debt_findings,
    ignores_count,
    ignores_findings,
    suppression_count,
    suppression_findings,
)
from tools.wct.rules.engine import drift, rule_documents
from tools.wct.util.git import remote_base

Gate = Callable[[Path], GateResult]


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


def external(gate_id: str, command: list[str], *, optional: bool = False) -> Gate:
    def run(root: Path) -> GateResult:
        started = time.monotonic()
        executable = command[0]
        if shutil.which(executable) is None:
            status = Status.SKIP if optional else Status.ERROR
            return GateResult(
                gate_id,
                status,
                f"herramienta ausente: {executable}",
                int((time.monotonic() - started) * 1000),
                command=" ".join(command),
            )
        completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        output = (completed.stdout + "\n" + completed.stderr).strip()
        status = Status.PASS if completed.returncode == 0 else Status.FAIL
        summary = (
            "ok"
            if status is Status.PASS
            else (output.splitlines()[-1] if output else f"exit {completed.returncode}")
        )
        return GateResult(
            gate_id,
            status,
            summary,
            int((time.monotonic() - started) * 1000),
            output.splitlines()[-50:],
            " ".join(command),
        )

    return run


def gate_coverage_diff(root: Path) -> GateResult:
    """Hard diff-cover: coverage >= 90% on changed lines, CI-faithful base.

    The pilot's phase 25 shipped a 17/17 local run that CI rejected on
    diff-cover: the gate existed but no tier ran it. Here it blocks (ERROR,
    not SKIP) because its tier's whole promise is local parity with CI.
    Requires G-COV-TOTAL to have produced build/coverage/lcov.info first
    (tier ordering guarantees it).
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
    command = [
        "diff-cover",
        "build/coverage/lcov.info",
        "--compare-branch",
        base,
        "--fail-under",
        "90",
        "--include-untracked",
    ]
    completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    output = (completed.stdout + "\n" + completed.stderr).strip()
    status = Status.PASS if completed.returncode == 0 else Status.FAIL
    summary = "ok" if status is Status.PASS else (output.splitlines()[-1] if output else "exit 1")
    return GateResult(
        "G-COV-DIFF",
        status,
        summary,
        int((time.monotonic() - started) * 1000),
        output.splitlines()[-50:],
        " ".join(command),
    )


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
    baseline = root / ".secrets.baseline"
    if not baseline.is_file():
        return set()
    document = json.loads(baseline.read_text(encoding="utf-8"))
    return {
        (filename, str(item.get("hashed_secret", "")))
        for filename, items in document.get("results", {}).items()
        for item in items
    }


def gate_secrets(root: Path) -> GateResult:
    started = time.monotonic()
    if shutil.which("detect-secrets") is None:
        return GateResult("G-SECRET", Status.ERROR, "herramienta ausente: detect-secrets")
    paths = [
        "src",
        "tools",
        "governance",
        ".claude",
        "skills",
        "plugins",
        ".github",
        "pyproject.toml",
        ".pre-commit-config.yaml",
    ]
    # governance/generated/ contiene artefactos regenerados por las propias
    # herramientas (p. ej. fingerprints sha256 del manifiesto de mutación):
    # hex de alta entropía por diseño, no secretos. Auditarlos en el baseline
    # sería fricción en cada regeneración.
    completed = subprocess.run(
        [
            "detect-secrets",
            "scan",
            "--slim",
            "--exclude-files",
            "^governance/generated/",
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


def alias(gate_id: str, target: Gate) -> Gate:
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

    return run


REGISTRY: dict[str, Gate] = {
    "G-META-1": gate_meta_integrity,
    "G-META-2": gate_meta_rules,
    "G-RULES-DRIFT": gate_rules_drift,
    "G-SUPPRESS": gate_suppressions,
    "G-DEBT": gate_debt,
    "G-LINT": external("G-LINT", ["ruff", "check", "--config", "governance/lint/ruff.toml", "."]),
    "G-FMT": external(
        "G-FMT",
        ["ruff", "format", "--config", "governance/lint/ruff.toml", "--check", "."],
    ),
    "G-TYPE": external("G-TYPE", ["mypy", "tools/wct", "src"]),
    "G-TEST": external("G-TEST", ["pytest", "-q", "tests/unit", "tests/integration"]),
    "G-ARCH": external("G-ARCH", ["lint-imports"]),
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
    ),
    "G-DEAD": external("G-DEAD", ["vulture", "src", "tools/wct", "--min-confidence", "80"]),
    "G-SAST-BANDIT": external("G-SAST-BANDIT", ["bandit", "-q", "-r", "src"]),
    "G-SAST-SEMGREP": external(
        "G-SAST-SEMGREP",
        [
            "semgrep",
            "--quiet",
            "--error",
            "--severity",
            "ERROR",
            "--config",
            "governance/semgrep",
        ],
        optional=True,
    ),
    "G-AUDIT": gate_audit,
    "G-ARCHMETRICS": gate_archmetrics,
    "G-DRY": gate_dry,
    "G-INTROVERT": gate_introvert,
    "G-MUT-SITES": gate_mutation_sites,
    "G-ACCEPT": gate_accept,
    "G-CRAP": external(
        "G-CRAP",
        ["crap4py", "src", "--lcov", "build/coverage/lcov.info", "--max-crap", "6"],
        optional=True,
    ),
    "G-CC": external(
        "G-CC",
        [
            "xenon",
            "--max-absolute",
            "B",
            "--max-modules",
            "A",
            "--max-average",
            "A",
            "src",
        ],
        optional=True,
    ),
    "G-COV-TOTAL": external(
        "G-COV-TOTAL",
        [
            "pytest",
            "--cov",
            "--cov-branch",
            "--cov-report=lcov:build/coverage/lcov.info",
            "-q",
        ],
    ),
    "G-COV-DIFF": gate_coverage_diff,
    "G-DOC": external("G-DOC", ["interrogate", "src", "--fail-under", "34"], optional=True),
    "G-SECRET": gate_secrets,
    "G-PROP": external("G-PROP", ["pytest", "-q", "tests/property"]),
    "G-TEST-RANDOM": external(
        "G-TEST-RANDOM", ["pytest", "-q", "--randomly-seed=last"], optional=True
    ),
    # --exit-code 1: sin esa bandera jscpd sale 0 aunque encuentre clones
    # (verificado empíricamente) y el gate sería vacío. El presupuesto de
    # detección (min-tokens, threshold) vive en .jscpd.json del repo.
    "G-DRY-TOK": external(
        "G-DRY-TOK", ["jscpd", "src", "tools", "--exit-code", "1"], optional=True
    ),
    "G-SBOM": external(
        "G-SBOM",
        ["cyclonedx-py", "environment", "--output-file", "build/sbom.json"],
        optional=True,
    ),
    "G-COMMIT-MSG": external(
        "G-COMMIT-MSG",
        ["cz", "check", "--commit-msg-file", ".git/COMMIT_EDITMSG"],
        optional=True,
    ),
    "G-MUT": external("G-MUT", ["mutmut", "run"], optional=True),
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
    "commit": [
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
    ],
    "full": [
        "G-META-1",
        "G-META-2",
        "G-RULES-DRIFT",
        "G-SUPPRESS",
        "G-DEBT",
        "G-LINT",
        "G-FMT",
        "G-TYPE",
        "G-TEST",
        "G-COV-TOTAL",
        "G-CRAP",
        "G-CC",
        "G-ARCH",
        "G-ARCHMETRICS",
        "G-DEPS",
        "G-DEAD",
        "G-DRY",
        "G-INTROVERT",
        "G-MUT-SITES",
        "G-ACCEPT",
        "G-SAST-BANDIT",
        "G-SAST-SEMGREP",
        "G-SECRET",
        "G-AUDIT",
        "G-SBOM",
        "G-DOC",
        "G-REDTEAM",
    ],
    # Espejo local de quality.yml en PRs: todo lo que CI exige de una PR,
    # ejecutable con un solo comando antes de pushear.
    "pr": [
        *[
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
        ],
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
