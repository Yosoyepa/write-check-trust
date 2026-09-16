"""Trampolines de construcción de entradas del registro y el tipo Gate."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import shutil
import time

from tools.wct.gate.capabilities import GateInfo, declares, gate_info, stamped
from tools.wct.gate.exec import _captured
from tools.wct.model import GateResult, Status

Gate = Callable[[Path], GateResult]


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
