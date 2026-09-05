"""G-MUT: mutación real con veredicto de sobrevivientes (ruling PR-E).

Partición fachada (TEST-007): ``gate_mutation`` dispara subprocess, así que
su casa canónica es el área de runner — pero runner.py estaba a 491 LOC y
STYLE-011 (500) no admite el crecimiento. Vive aquí y runner.py la
re-exporta; los imports públicos no cambian.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import time

from tools.wct.gate.exec import _captured
from tools.wct.model import GateResult, Status


def gate_mutation(root: Path) -> GateResult:
    """Corre mutmut y FALLA si algún mutante sobrevive (TEST-002).

    El exit code de ``mutmut run`` (3.7.0) no distingue sobrevivientes:
    sale 0 con el árbol limpio Y con mutantes vivos, y solo sale 1 cuando
    la corrida misma no puede ejecutarse (matriz del paso 0.1 de PR-E). El
    veredicto por eso se toma de ``mutmut results``, que lista cada mutante
    con su estado: cualquier ``: survived`` es un hallazgo que falla el
    gate; la corrida rota falla con su diagnóstico.

    Args:
        root: raíz del árbol a mutar; su ``[tool.mutmut]`` define el alcance.

    Returns:
        SKIP si mutmut no está instalado (semántica optional original);
        FAIL si la corrida aborta o si sobrevive algún mutante — con la
        lista de sobrevivientes en ``details``; PASS con resumen "cero
        mutantes sobrevivientes" en caso contrario.
    """
    started = time.monotonic()
    if shutil.which("mutmut") is None:
        return GateResult("G-MUT", Status.SKIP, "herramienta ausente: mutmut")
    run_status, run_summary, run_output = _captured(root, ["mutmut", "run"])
    if run_status is Status.FAIL:
        return GateResult(
            "G-MUT",
            Status.FAIL,
            run_summary,
            int((time.monotonic() - started) * 1000),
            run_output.splitlines()[-50:],
            "mutmut run",
        )
    _results_status, _results_summary, results_output = _captured(root, ["mutmut", "results"])
    survivors = [
        line.strip() for line in results_output.splitlines() if line.rstrip().endswith(": survived")
    ]
    if survivors:
        return GateResult(
            "G-MUT",
            Status.FAIL,
            f"{len(survivors)} mutantes sobrevivientes",
            int((time.monotonic() - started) * 1000),
            survivors,
            "mutmut run && mutmut results",
        )
    return GateResult(
        "G-MUT",
        Status.PASS,
        "cero mutantes sobrevivientes",
        int((time.monotonic() - started) * 1000),
        command="mutmut run && mutmut results",
    )
