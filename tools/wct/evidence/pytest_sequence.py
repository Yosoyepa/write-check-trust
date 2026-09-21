"""Estado del decoder, secuencias globales/locales e inventarios (§4)."""

from dataclasses import dataclass, field

from tools.wct.evidence.pytest_limits import SEQ_MAX
from tools.wct.evidence.pytest_payload_classes import ORIGIN_SUPERVISOR, NodeDeclaration
from tools.wct.evidence.pytest_payloads import (
    CollectedItem,
    DeselectedItem,
    PhaseLog,
    PhaseMake,
    SelectedItem,
    TestEnd,
    TestStart,
)
from tools.wct.evidence.pytest_types import ExecutionExpectation
from tools.wct.evidence.pytest_wire_framing import _DefectError

MAX_DECLARATIONS = 20_000

MAX_INVENTORY_ENTRIES = 10_000

_CAPPED: dict[type, str] = {
    CollectedItem: "item",
    DeselectedItem: "deselected",
    SelectedItem: "selected",
    TestStart: "test_start",
    TestEnd: "test_end",
}


@dataclass(frozen=True)
class _Job:
    """Entrada ya validada del decoder, agrupada para helpers de 4 args."""

    data: bytes
    run_id: str
    executions: tuple[ExecutionExpectation, ...]
    max_bytes: int


@dataclass
class _DecodeState:
    """Estado mutable del decoder: contadores y tabla global de nodeids."""

    executions: tuple[ExecutionExpectation, ...]
    expected_seq: int = 1
    local_next: dict[int, int] = field(default_factory=dict)
    inventory: dict[tuple[int, str], int] = field(default_factory=dict)
    declarations: list[str] = field(default_factory=list)
    declared: set[str] = field(default_factory=set)


def _register_declaration(state: _DecodeState, payload: NodeDeclaration) -> None:
    """Índices contiguos desde 0 y strings únicos; tope de declaraciones."""
    if payload.index != len(state.declarations):
        raise _DefectError("invalid_field")
    if payload.nodeid in state.declared:
        raise _DefectError("invalid_field")
    if len(state.declarations) >= MAX_DECLARATIONS:
        raise _DefectError("limit_exceeded")
    state.declarations.append(payload.nodeid)
    state.declared.add(payload.nodeid)


def _check_sequence(state: _DecodeState, seq: object, local: object, origin: str, ex: int) -> None:
    """Seq global contiguo desde 1; local_seq por ejecución pytest."""
    if type(seq) is not int or seq < 1 or seq > SEQ_MAX:
        raise _DefectError("invalid_field")
    if seq != state.expected_seq:
        raise _DefectError("sequence_error")
    if origin == ORIGIN_SUPERVISOR:
        _reject_supervisor_local(local)
        state.expected_seq = seq + 1
        return
    _advance_local(state, seq, local, ex)


def _reject_supervisor_local(local: object) -> None:
    """El supervisor no declara local_seq."""
    if local is not None:
        raise _DefectError("sequence_error")


def _advance_local(state: _DecodeState, seq: int, local: object, ex: int) -> None:
    """El worker valida y avanza su contador local junto al global."""
    if local is None:
        raise _DefectError("sequence_error")
    if type(local) is not int or local < 1 or local > SEQ_MAX:
        raise _DefectError("invalid_field")
    if local != state.local_next.get(ex, 1):
        raise _DefectError("sequence_error")
    state.local_next[ex] = local + 1
    state.expected_seq = seq + 1


def _inventory_key(cls: type, payload: object) -> str | None:
    """Clave con tope por ejecución; fases cuentan separadas por nombre."""
    if cls in _CAPPED:
        return _CAPPED[cls]
    if cls is PhaseMake or cls is PhaseLog:
        phase = str(getattr(payload, "phase", ""))
        return f"{cls.__name__}:{phase}"
    return None


def _check_inventory(state: _DecodeState, ex: int, key: str | None) -> None:
    """Tope por inventario y ejecución; el +1 descarta el evento."""
    if key is None:
        return
    count = state.inventory.get((ex, key), 0) + 1
    if count > MAX_INVENTORY_ENTRIES:
        raise _DefectError("limit_exceeded")
    state.inventory[(ex, key)] = count
