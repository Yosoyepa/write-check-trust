"""Inventarios, propiedades y comparaciones de identidad (SH-P03a/1 §7).

Los items previos son selected + deselected por multiconjunto; ningún
silencio elimina un item. Cada finding apunta al evento causante; las
ausencias quedan con offset None. Las identidades se calculan
exclusivamente con ``compare_identities`` de P01, por keywords, sin
deduplicar antes.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from tools.wct.evidence.identities import IdentityComparison, compare_identities
from tools.wct.evidence.pytest_types import ProtocolFinding

PROPERTY_FINDING_CODES = frozenset(
    {
        "unauthorized_deselection",
        "unauthorized_selection",
        "property_marker_changed",
        "missing_property",
        "unexpected_property",
        "duplicate_property",
    }
)
NON_BLOCKING_CODES = PROPERTY_FINDING_CODES | {
    "selection_mismatch",
    "unexpected_test",
}


@dataclass(frozen=True)
class ExecutionInventory:
    """Inventario en orden observado de una ejecución, con duplicados."""

    items: tuple[tuple[str, bool, int], ...]
    selected: tuple[tuple[str, int], ...]
    deselected: tuple[tuple[str, bool, int], ...]
    collection_end_offset: int | None


def _finding(
    code: str, execution_id: str, nodeid: str | None, offset: int | None
) -> ProtocolFinding:
    return ProtocolFinding(
        code=code, execution_id=execution_id, nodeid=nodeid, phase=None, offset=offset
    )


def selection_findings(
    inventory: ExecutionInventory, execution_id: str
) -> tuple[ProtocolFinding, ...]:
    """Items previos = selected + deselected por multiconjunto."""
    covered: Counter[str] = Counter(nodeid for nodeid, _offset in inventory.selected)
    covered.update(nodeid for nodeid, _flag, _offset in inventory.deselected)
    if Counter(nodeid for nodeid, _flag, _offset in inventory.items) == covered:
        return ()
    return (_finding("selection_mismatch", execution_id, None, inventory.collection_end_offset),)


def _deselection_findings(
    inventory: ExecutionInventory,
    execution_id: str,
    property_ids: tuple[str, ...],
    item_flags: dict[str, bool],
) -> list[ProtocolFinding]:
    """Cada deselección: marcador coherente, propiedad autorizada y única."""
    findings: list[ProtocolFinding] = []
    for deselected in inventory.deselected:
        findings.extend(_deselection_rule(execution_id, property_ids, item_flags, deselected))
    findings.extend(_duplicate_findings(inventory, execution_id))
    return findings


def _deselection_rule(
    execution_id: str,
    property_ids: tuple[str, ...],
    item_flags: dict[str, bool],
    deselected: tuple[str, bool, int],
) -> list[ProtocolFinding]:
    """Marcador coherente con el item y propiedad autorizada."""
    nodeid, flag, offset = deselected
    found: list[ProtocolFinding] = []
    if nodeid in item_flags and item_flags[nodeid] != flag:
        found.append(_finding("property_marker_changed", execution_id, nodeid, offset))
    if not flag:
        found.append(_finding("unauthorized_deselection", execution_id, nodeid, offset))
    elif nodeid not in property_ids:
        found.append(_finding("unexpected_property", execution_id, nodeid, offset))
    return found


def _duplicate_findings(inventory: ExecutionInventory, execution_id: str) -> list[ProtocolFinding]:
    """Nodeids deseleccionados más de una vez son duplicate_property."""
    counts: Counter[str] = Counter(nodeid for nodeid, _flag, _offset in inventory.deselected)
    return [
        _finding("duplicate_property", execution_id, nodeid, None)
        for nodeid, total in counts.items()
        if total > 1
    ]


def property_findings(
    inventory: ExecutionInventory, execution_id: str, property_ids: tuple[str, ...]
) -> tuple[ProtocolFinding, ...]:
    """Reglas de property del §7: marcadores, autorización y obligaciones."""
    findings: list[ProtocolFinding] = []
    item_flags: dict[str, bool] = {}
    for nodeid, flag, _offset in inventory.items:
        item_flags.setdefault(nodeid, flag)
    findings.extend(_deselection_findings(inventory, execution_id, property_ids, item_flags))
    for nodeid, offset in inventory.selected:
        if item_flags.get(nodeid) is True:
            findings.append(_finding("unauthorized_selection", execution_id, nodeid, offset))
    deselected_ids = {nodeid for nodeid, _flag, _offset in inventory.deselected}
    findings.extend(_missing_findings(execution_id, property_ids, deselected_ids))
    return tuple(findings)


def _missing_findings(
    execution_id: str, property_ids: tuple[str, ...], deselected_ids: set[str]
) -> list[ProtocolFinding]:
    """Propiedad declarada sin deselección es missing_property."""
    return [
        _finding("missing_property", execution_id, identity, None)
        for identity in property_ids
        if identity not in deselected_ids
    ]


def identity_comparisons(
    expected: tuple[str, ...],
    collection_selected: tuple[str, ...],
    producer_selected: tuple[str, ...],
    producer_terminals: tuple[str, ...],
) -> tuple[IdentityComparison, IdentityComparison]:
    """Preflight y final según §7; P01 conserva su propio catálogo y orden."""
    preflight = compare_identities(
        expected=expected, collected=collection_selected, executed=producer_selected
    )
    final = compare_identities(
        expected=expected, collected=producer_selected, executed=producer_terminals
    )
    return preflight, final
