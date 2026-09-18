"""Estructura de la lista de eventos: offsets, seq y relaciones (§2/§4)."""

from typing import cast

from tools.wct.evidence.pytest_observation_event import _validate_event
from tools.wct.evidence.pytest_observation_inventory import _validate_inventory_cap
from tools.wct.evidence.pytest_payloads import ExecutionStart, NodeDeclaration
from tools.wct.evidence.pytest_sequence import MAX_DECLARATIONS
from tools.wct.evidence.pytest_types import JournalEvent, JournalObservation, ObservationError
from tools.wct.evidence.pytest_wire_framing import canonical_header


def _validate_events(observation: JournalObservation) -> None:
    """Tipos, clases, offsets y secuencias contiguas desde la cabecera."""
    header_length = len(canonical_header(observation.run_id, observation.executions))
    if not observation.events:
        if observation.consumed_bytes not in (0, header_length):
            raise ObservationError("invalid_observation", "consumed_bytes")
        return
    _validate_event_stream(observation, header_length)
    if observation.events[-1].end_offset != observation.consumed_bytes:
        raise ObservationError("invalid_observation", "consumed_bytes")


def _validate_event_stream(observation: JournalObservation, header_length: int) -> None:
    """Cada evento encadena seq/offset y respeta relaciones e inventarios."""
    expected_start = header_length
    local_next: dict[str, int] = {}
    declared: list[str] = []
    inventories: dict[tuple[str, str], int] = {}
    for index, event in enumerate(observation.events):
        _validate_event(index, event, observation)
        _validate_relations(index, event, declared, observation)
        _validate_inventory_cap(index, event, inventories)
        if event.seq != index + 1:
            raise ObservationError("invalid_observation", f"events[{index}].seq")
        if event.origin != "supervisor":
            _advance_local(index, event, local_next)
        if event.offset != expected_start:
            raise ObservationError("invalid_observation", f"events[{index}].offset")
        expected_start = event.end_offset


def _advance_local(index: int, event: JournalEvent, local_next: dict[str, int]) -> None:
    """El worker encadena su local_seq por ejecución."""
    following = local_next.get(event.execution_id, 1)
    if event.local_seq != following:
        raise ObservationError("invalid_observation", f"events[{index}].local_seq")
    local_next[event.execution_id] = following + 1


def _validate_relations(
    index: int, event: JournalEvent, declared: list[str], observation: JournalObservation
) -> None:
    """Relaciones que el decoder garantiza: tabla de nodos e identidad de arranque.

    Los índices declarados son contiguos desde 0 con strings únicos, todo
    nodeid referido resuelve a una declaración anterior, y el execution_start
    conserva role/digests de su cabecera.
    """
    payload = event.payload
    if type(payload) is NodeDeclaration:
        _declare_node(index, payload, declared)
        return
    nodeid = getattr(payload, "nodeid", None)
    if nodeid is not None and nodeid not in declared:
        raise ObservationError("invalid_observation", f"events[{index}].payload.nodeid")
    if event.kind == "execution_start":
        _validate_start_identity(index, event, observation)


def _declare_node(index: int, payload: NodeDeclaration, declared: list[str]) -> None:
    """Índices contiguos desde 0 y strings únicos hasta el tope."""
    if payload.index != len(declared):
        raise ObservationError("invalid_observation", f"events[{index}].payload.index")
    if len(declared) >= MAX_DECLARATIONS:
        raise ObservationError("invalid_observation", f"events[{index}].payload.index")
    if payload.nodeid in declared:
        raise ObservationError("invalid_observation", f"events[{index}].payload.nodeid")
    declared.append(payload.nodeid)


def _validate_start_identity(
    index: int, event: JournalEvent, observation: JournalObservation
) -> None:
    """Role y digests del arranque provienen inequívocamente de su cabecera."""
    start = cast(ExecutionStart, event.payload)
    expected = next(
        item for item in observation.executions if item.execution_id == event.execution_id
    )
    if start.role != expected.role:
        raise ObservationError("invalid_observation", f"events[{index}].payload.role")
    if (start.input_sha256, start.context_sha256, start.recipe_sha256) != (
        expected.input_sha256,
        expected.context_sha256,
        expected.recipe_sha256,
    ):
        raise ObservationError("invalid_observation", f"events[{index}].payload.input_sha256")
