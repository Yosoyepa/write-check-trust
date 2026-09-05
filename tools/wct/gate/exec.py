"""Ejecución capturada de comandos de gate (partición fachada, TEST-007).

``_captured`` la usan los gates que disparan procesos desde sus módulos
(runner, mutation): una sola definición, sin ciclos de import.
"""

from __future__ import annotations

from pathlib import Path
import subprocess

from tools.wct.model import Status


def _captured(root: Path, command: list[str]) -> tuple[Status, str, str]:
    """Ejecuta un comando del gate y resume: status, summary, salida completa."""
    completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    output = (completed.stdout + "\n" + completed.stderr).strip()
    status = Status.PASS if completed.returncode == 0 else Status.FAIL
    summary = (
        "ok"
        if status is Status.PASS
        else (output.splitlines()[-1] if output else f"exit {completed.returncode}")
    )
    return status, summary, output
