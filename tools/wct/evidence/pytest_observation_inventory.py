"""Tope de inventarios por ejecución y fase en observaciones manuales (§2)."""

from tools.wct.evidence.pytest_sequence import MAX_INVENTORY_ENTRIES
from tools.wct.evidence.pytest_types import JournalEvent, ObservationError

_INVENTORY_KINDS = frozenset({"item", "deselected", "selected", "test_start", "test_end"})


def _validate_inventory_cap(
    index: int, event: JournalEvent, inventories: dict[tuple[str, str], int]
) -> None:
    """Los inventarios por ejecución —y por fase— respetan el tope de §2.

    El decoder descarta la línea que excede 10 000 entradas; una observación
    manual que la contenga no puede ser su salida y se rechaza entera.
    """
    kind = event.kind
    if kind in _INVENTORY_KINDS:
        key = kind
    elif kind in ("phase_make", "phase_log"):
        key = f"{kind}:{getattr(event.payload, 'phase', '')}"
    else:
        return
    slot = (event.execution_id, key)
    count = inventories.get(slot, 0) + 1
    if count > MAX_INVENTORY_ENTRIES:
        raise ObservationError("invalid_observation", f"events[{index}]")
    inventories[slot] = count
