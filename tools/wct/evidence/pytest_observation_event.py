"""Validación de un evento manual: clase exacta, identidad y offsets (§2)."""

from tools.wct.evidence.pytest_event_catalog import EVENT_CATALOG
from tools.wct.evidence.pytest_limits import LINE_MAX_BYTES
from tools.wct.evidence.pytest_payload_validate import validate_payload
from tools.wct.evidence.pytest_types import JournalEvent, JournalObservation, ObservationError

_CLASS_BY_KIND: dict[tuple[str, str], type] = {
    (origin, kind): cls for _code, origin, kind, cls in EVENT_CATALOG
}


def _validate_event(index: int, event: object, observation: JournalObservation) -> None:
    """Un evento manual: clase exacta, esquema de payload e identidad."""
    if type(event) is not JournalEvent:
        raise ObservationError("invalid_observation", f"events[{index}]")
    _validate_payload_class(index, event)
    try:
        validate_payload(event.payload)
    except ObservationError as error:
        raise ObservationError(error.code, f"events[{index}].payload.{error.field}") from None
    _validate_event_identity(index, event, observation)
    _validate_event_offsets(index, event, observation)


def _validate_payload_class(index: int, event: JournalEvent) -> None:
    """El par (origin, kind) existe en el catálogo y el payload es de su clase."""
    if type(event.origin) is not str or type(event.kind) is not str:
        raise ObservationError("invalid_observation", f"events[{index}].payload")
    expected_cls = _CLASS_BY_KIND.get((event.origin, event.kind))
    if expected_cls is None or type(event.payload) is not expected_cls:
        raise ObservationError("invalid_observation", f"events[{index}].payload")


def _validate_event_identity(
    index: int, event: JournalEvent, observation: JournalObservation
) -> None:
    """Seq positivo, ejecución conocida y local_seq coherente con el origen."""
    if type(event.seq) is not int or event.seq < 1:
        raise ObservationError("invalid_observation", f"events[{index}].seq")
    _validate_known_execution(index, event, observation)
    _validate_local_seq(index, event)


def _validate_known_execution(
    index: int, event: JournalEvent, observation: JournalObservation
) -> None:
    """execution_id existe entre las ejecuciones esperadas."""
    if type(event.execution_id) is not str or event.execution_id not in {
        item.execution_id for item in observation.executions
    }:
        raise ObservationError("invalid_observation", f"events[{index}].execution_id")


def _validate_local_seq(index: int, event: JournalEvent) -> None:
    """Supervisor sin local_seq; worker con local_seq positivo."""
    if event.origin == "supervisor":
        if event.local_seq is not None:
            raise ObservationError("invalid_observation", f"events[{index}].local_seq")
    elif type(event.local_seq) is not int or event.local_seq < 1:
        raise ObservationError("invalid_observation", f"events[{index}].local_seq")


def _validate_event_offsets(
    index: int, event: JournalEvent, observation: JournalObservation
) -> None:
    """Intervalo semiabierto dentro del consumo y de la línea máxima."""
    if type(event.offset) is not int or type(event.end_offset) is not int:
        raise ObservationError("invalid_observation", f"events[{index}].offset")
    if not 0 <= event.offset < event.end_offset <= observation.consumed_bytes:
        raise ObservationError("invalid_observation", f"events[{index}].offset")
    if not 1 <= event.end_offset - event.offset <= LINE_MAX_BYTES:
        raise ObservationError("invalid_observation", f"events[{index}].offset")
