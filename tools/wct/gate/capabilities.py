"""Metadata de capacidades de los gates (ADR-D-01, O-006).

Partición fachada (TEST-007): runner.py conserva el registro y los gates;
aquí vive el stamping/lectura de la capacidad que cada gate declara donde
se construye — tools externas y rutas que escanea. Nadie duplica el dato:
dynamic/external derivan las tools del ejecutable que ya resuelven, y los
sitios de construcción de REGISTRY declaran el scope verificado.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from tools.wct.model import GateResult


@dataclass(frozen=True)
class GateInfo:
    """Capacidad de un gate declarada donde se construye (ADR-D-01).

    tools: ejecutables externos que resuelve el gate; vacía para los
    analizadores puros del repo. scope: rutas del proyecto que escanea;
    vacía para gates de configuración u orquestadores sin rutas propias.
    """

    tools: tuple[str, ...] = ()
    scope: tuple[str, ...] = ()


def stamped(gate: Callable[[Path], GateResult], info: GateInfo) -> Callable[[Path], GateResult]:
    """Adjunta los metadatos al objeto gate: el stamping vive solo aquí."""
    vars(gate)["_gate_info"] = info
    return gate


def gate_info(gate: Callable[[Path], GateResult]) -> GateInfo | None:
    """Lee la capacidad estampada por el constructor; None si no declara."""
    marked = getattr(gate, "_gate_info", None)
    return marked if isinstance(marked, GateInfo) else None


def declares(
    gate: Callable[[Path], GateResult],
    *,
    tools: tuple[str, ...] = (),
    scope: tuple[str, ...] = (),
) -> Callable[[Path], GateResult]:
    """Declara capacidad en el sitio de construcción del gate (ADR-D-01).

    Las tools se SUMAN a las que el constructor ya estampó (dynamic y
    external las derivan de su ejecutable); el scope se declara aquí porque
    las rutas reales las conoce el sitio que registra el gate.
    """
    marked = gate_info(gate)
    known = marked.tools if marked else ()
    return stamped(gate, GateInfo(known + tools, scope))
