"""G-DOC: cobertura de docstrings con interrogate."""

from __future__ import annotations

from pathlib import Path
import shutil
import time

from tools.wct.gate.exec import _captured
from tools.wct.model import GateResult, Status
from tools.wct.ratchet.engine import baseline


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
