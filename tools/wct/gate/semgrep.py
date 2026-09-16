"""Alcance verificable de G-SAST-SEMGREP (addenda de frontera) — fachada.

Partición fachada (TEST-007): el inventario exigible y la normalización de
rutas viven en semgrep_scope, la validación tipada del JSON en
semgrep_schema y la clasificación cerrada en semgrep_verdict; aquí quedan
el comando, la topología Git, la política de alcance y el gate que los
compone. Los imports públicos no cambian: SemgrepScopeError,
required_sources, Verdict y classify se re-exportan para runner y tests.

Política de herramienta ausente vigente: Semgrep ausente es SKIP visible.
Orden de clasificación: preflight de topología (absorción por ancestro es
ERROR), configuración de alcance, ejecución del instrumento y veredicto.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import time
from typing import Any

from tools.wct.config import ConfigError, load_yaml
from tools.wct.gate.semgrep_scope import SemgrepScopeError, required_sources
from tools.wct.gate.semgrep_verdict import Verdict, classify
from tools.wct.model import GateResult, Status

GATE_ID = "G-SAST-SEMGREP"
COMMAND = (
    "semgrep",
    "--quiet",
    "--error",
    "--severity",
    "ERROR",
    "--config",
    "governance/semgrep",
    "--json",
)

__all__ = [
    "COMMAND",
    "GATE_ID",
    "SemgrepScopeError",
    "Verdict",
    "classify",
    "gate_sast_semgrep",
    "required_sources",
]


def _topology(root: Path) -> None:
    """ERROR si Git descubre un toplevel distinto de la raíz (absorción por ancestro)."""
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return
    toplevel = Path(completed.stdout.strip()).resolve()
    if toplevel != root.resolve():
        raise SemgrepScopeError(f"candidate root absorbed by foreign Git ancestor: {toplevel}")


def _policy(root: Path) -> dict[str, Any]:
    """Policy de alcance; la configuración ilegible hace el alcance indeterminable."""
    try:
        return load_yaml(root / "governance" / "policy.yaml")
    except ConfigError as exc:
        raise SemgrepScopeError(f"governance/policy.yaml ilegible: {exc}") from exc


def gate_sast_semgrep(root: Path) -> GateResult:
    """G-SAST-SEMGREP: Semgrep con alcance exigible verificable (addenda de frontera)."""
    started = time.monotonic()
    if shutil.which("semgrep") is None:
        return GateResult(GATE_ID, Status.SKIP, "herramienta ausente: semgrep")
    try:
        _topology(root)
        required = required_sources(root, _policy(root))
        completed = subprocess.run(
            list(COMMAND), cwd=root, text=True, capture_output=True, check=False
        )
        verdict = classify(required, completed.stdout, completed.returncode)
    except (SemgrepScopeError, OSError) as exc:
        return GateResult(GATE_ID, Status.ERROR, str(exc), int((time.monotonic() - started) * 1000))
    return GateResult(
        GATE_ID,
        verdict.status,
        verdict.summary,
        int((time.monotonic() - started) * 1000),
        list(verdict.details),
        " ".join(COMMAND),
    )
