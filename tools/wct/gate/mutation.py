"""G-MUT: mutación real con veredicto del inventario completo (G1a).

Partición fachada (TEST-007): ``gate_mutation`` dispara subprocess, así que
su casa canónica es el área de runner — pero runner.py estaba a 491 LOC y
STYLE-011 (500) no admite el crecimiento. Vive aquí y runner.py la
re-exporta; los imports públicos no cambian.

La clasificación vive en ``tools/wct/mutate/verdict.py`` (ADR-G1-03): un
contrato de veredicto, dos consumidores — este gate y el CLI ``wct mutate
run`` — para que nunca vuelvan a divergir (hallazgo F02).
"""

from __future__ import annotations

from pathlib import Path
import shutil

from tools.wct.model import GateResult, Status
from tools.wct.mutate.verdict import mutation_verdict


def gate_mutation(root: Path) -> GateResult:
    """Clasifica todo el inventario del motor de mutación (tabla ADR-G1-01).

    Delega en el adaptador ``mutation_verdict`` (run → ``results --all
    true`` → clasificación con precedencia ERROR>FAIL): PASS limitado
    cuando el motor reporta todo su inventario como killed; FAIL con las
    identidades de survived/no tests y para la corrida que no completa
    ("ejecución no completada", sin atribuir defecto de producto); ERROR
    para evidencia inválida (fases results/inventario/clasificación) y
    estados fuera del contrato de certificación WCT.

    Args:
        root: raíz del árbol a mutar; su ``[tool.mutmut]`` define el alcance.

    Returns:
        SKIP si mutmut no está instalado (semántica optional de PR-E,
        ``mutation.py:43``); si no, el GateResult del adaptador con fase,
        conteos, identidades y versión del motor en el diagnóstico.
    """
    if shutil.which("mutmut") is None:
        return GateResult("G-MUT", Status.SKIP, "herramienta ausente: mutmut")
    return mutation_verdict(root)
