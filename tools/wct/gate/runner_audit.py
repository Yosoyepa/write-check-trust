"""G-AUDIT: CVEs de dependencias con pip-audit."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from tools.wct.gate.checks import _result
from tools.wct.model import GateResult, Status


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
