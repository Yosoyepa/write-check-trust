"""Reconciliación pura de identidades de evidencia (SH-P01, sh-p01/1).

Compara tres inventarios de identidades opacas —expected, collected y
executed— sin confundir igualdad de conteos con igualdad de obligaciones.
Kernel interno: no corre pytest, no mide cobertura, no autentica entradas
y un ``match`` no afirma ejecución ni éxito de tests.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Literal

Inventory = Literal["expected", "collected", "executed"]
FindingCode = Literal[
    "empty_expected",
    "empty_identity",
    "duplicate_identity",
    "missing_identity",
    "unexpected_identity",
]
IdentityStatus = Literal["match", "mismatch", "empty", "invalid"]

_OBSERVED_INVENTORIES: tuple[Inventory, ...] = ("collected", "executed")

# Precedencia de sh-p01/1 §4, en orden: el primer código presente decide el
# estado; solo si ningún trigger aplica hay igualdad exacta y ``match``.
_STATUS_PRECEDENCE: tuple[tuple[frozenset[FindingCode], IdentityStatus], ...] = (
    (frozenset({"empty_identity", "duplicate_identity"}), "invalid"),
    (frozenset({"empty_expected"}), "empty"),
    (frozenset({"missing_identity", "unexpected_identity"}), "mismatch"),
)

__all__ = ["IdentityComparison", "IdentityFinding", "compare_identities"]


@dataclass(frozen=True)
class IdentityFinding:
    """Defecto u obligación puntual observada en un inventario.

    Attributes:
        inventory: inventario donde se observó el hallazgo.
        code: código cerrado del catálogo de ``sh-p01/1`` §4.
        identity: identidad afectada; ``None`` solo para ``empty_expected``.
    """

    inventory: Inventory
    code: FindingCode
    identity: str | None


@dataclass(frozen=True)
class IdentityComparison:
    """Resultado completo de reconciliar los tres inventarios.

    Attributes:
        status: decisión de precedencia de ``sh-p01/1`` §4; ``match``
            acredita igualdad de identidades, no ejecución ni éxito.
        findings: todos los hallazgos aplicables, en orden canónico.
    """

    status: IdentityStatus
    findings: tuple[IdentityFinding, ...]


def _validated(inventory: Inventory, items: object) -> tuple[str, ...]:
    """Exige una tupla de strings en la frontera pública de la API.

    Args:
        inventory: nombre del argumento validado, para el diagnóstico.
        items: valor recibido, sin confiar en su anotación.

    Returns:
        La tupla de entrada, ya validada.

    Raises:
        TypeError: si el contenedor no es una tupla o algún elemento no es
            un string. El texto no es contrato.
    """
    if not isinstance(items, tuple):
        raise TypeError(f"{inventory}: debe ser una tupla de strings")
    for item in items:
        if not isinstance(item, str):
            raise TypeError(f"{inventory}: cada identidad debe ser un string")
    return items


def _non_empty_counts(items: tuple[str, ...]) -> Counter[str]:
    """Multiconjunto de las identidades no vacías de un inventario.

    Args:
        items: entradas originales del inventario, sin deduplicar.

    Returns:
        El conteo por identidad; los vacíos se diagnostican aparte.
    """
    return Counter(item for item in items if item != "")


def _empty_findings(inventory: Inventory, items: tuple[str, ...]) -> list[IdentityFinding]:
    """Hallazgos por entradas vacías: uno por inventario, sin contar duplicados.

    Args:
        inventory: inventario bajo revisión.
        items: entradas originales del inventario.

    Returns:
        Una lista con ``empty_identity`` si hay algún string vacío.
    """
    if "" in items:
        return [IdentityFinding(inventory, "empty_identity", "")]
    return []


def _duplicate_findings(inventory: Inventory, counts: Counter[str]) -> list[IdentityFinding]:
    """Hallazgos por identidades no vacías repetidas, en orden lexicográfico.

    Args:
        inventory: inventario bajo revisión.
        counts: multiconjunto no vacío del inventario.

    Returns:
        Un hallazgo ``duplicate_identity`` por identidad repetida.
    """
    return [
        IdentityFinding(inventory, "duplicate_identity", identity)
        for identity, total in sorted(counts.items())
        if total > 1
    ]


def _gap_findings(
    inventory: Inventory, identities: set[str], code: FindingCode
) -> list[IdentityFinding]:
    """Hallazgos de un conjunto de identidades ausentes o de sobra.

    Args:
        inventory: inventario observado bajo revisión.
        identities: conjunto del gap ya calculado por el caller.
        code: ``missing_identity`` o ``unexpected_identity``.

    Returns:
        Un hallazgo por identidad, en orden lexicográfico.
    """
    return [IdentityFinding(inventory, code, identity) for identity in sorted(identities)]


def _observed_findings(
    inventory: Inventory, values: set[str], expected_values: set[str]
) -> list[IdentityFinding]:
    """Diferencias de un inventario observado frente a lo esperado no vacío.

    Args:
        inventory: inventario observado bajo revisión.
        values: strings no vacíos observados en el inventario.
        expected_values: strings no vacíos esperados.

    Returns:
        Los faltantes y luego los inesperados, cada grupo en orden
        lexicográfico; un ``executed`` presente no compensa un faltante
        de colección.
    """
    return [
        *_gap_findings(inventory, expected_values - values, "missing_identity"),
        *_gap_findings(inventory, values - expected_values, "unexpected_identity"),
    ]


def _inventory_findings(
    inventory: Inventory, items: tuple[str, ...], expected_values: set[str]
) -> list[IdentityFinding]:
    """Recolecta los hallazgos de un inventario, en su orden canónico.

    El multiconjunto original se retiene para detectar duplicados; las
    diferencias se calculan sobre los strings no vacíos.

    Args:
        inventory: inventario bajo revisión.
        items: entradas originales, sin deduplicar.
        expected_values: strings no vacíos esperados; solo afecta a los
            inventarios observados.

    Returns:
        Hallazgos ordenados por código del catálogo y, dentro de cada
        código, lexicográficamente por identidad.
    """
    counts = _non_empty_counts(items)
    findings = [*_empty_findings(inventory, items), *_duplicate_findings(inventory, counts)]
    if inventory in _OBSERVED_INVENTORIES:
        findings.extend(_observed_findings(inventory, set(counts), expected_values))
    return findings


def _resolved_status(findings: list[IdentityFinding]) -> IdentityStatus:
    """Aplica la precedencia de ``sh-p01/1`` §4 conservando todas las causas.

    Args:
        findings: hallazgos ya emitidos para los tres inventarios.

    Returns:
        El estado del primer trigger de ``_STATUS_PRECEDENCE`` presente;
        ``match`` solo cuando no hay hallazgo alguno, es decir, expected
        no vacío e igualdad exacta de los tres inventarios.
    """
    codes = {finding.code for finding in findings}
    for trigger, status in _STATUS_PRECEDENCE:
        if codes & trigger:
            return status
    return "match"


def compare_identities(
    *,
    expected: tuple[str, ...],
    collected: tuple[str, ...],
    executed: tuple[str, ...],
) -> IdentityComparison:
    """Reconcilia los tres inventarios conservando todas las causas.

    Igualdad exacta de strings Python: sin ``strip``, ni case-folding, ni
    normalización Unicode, ni extracción parcial del nodeid. Los argumentos
    defectuosos se rechazan en esta frontera antes de producir un reporte.

    Args:
        expected: obligaciones declaradas.
        collected: identidades recolectadas.
        executed: identidades reportadas como ejecutadas.

    Returns:
        El estado de precedencia y todos los hallazgos en orden canónico.

    Raises:
        TypeError: si algún argumento no es una tupla de strings.
    """
    inventories: tuple[tuple[Inventory, tuple[str, ...]], ...] = (
        ("expected", _validated("expected", expected)),
        ("collected", _validated("collected", collected)),
        ("executed", _validated("executed", executed)),
    )
    expected_values = {item for item in inventories[0][1] if item != ""}
    findings: list[IdentityFinding] = []
    if not expected_values:
        findings.append(IdentityFinding("expected", "empty_expected", None))
    for inventory, items in inventories:
        findings.extend(_inventory_findings(inventory, items, expected_values))
    return IdentityComparison(_resolved_status(findings), tuple(findings))
