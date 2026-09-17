"""G-SECRET: auditoría de secretos con detect-secrets."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import time

from tools.wct.gate.checks import _result
from tools.wct.model import GateResult, Status

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
