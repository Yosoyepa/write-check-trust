"""Bucle de decodificación del journal y superficie estable del módulo (§4).

El framing vive en ``pytest_wire_framing``; los coercers en
``pytest_wire_values``/``pytest_wire_composites``; los builders en
``pytest_builders``; secuencias e inventarios en ``pytest_sequence``;
cabecera y líneas de evento en ``pytest_decode_header``/
``pytest_decode_events``; y la validación de payloads manuales en
``pytest_payload_validate``.
"""

from tools.wct.evidence.pytest_decode_events import _consume_line, _finish
from tools.wct.evidence.pytest_decode_header import _decode_header
from tools.wct.evidence.pytest_event_catalog import EVENT_CATALOG
from tools.wct.evidence.pytest_limits import (
    C0_LIMIT,
    DECODER_FINDING_CODES,
    DEL_CHAR,
    LINE_MAX_BYTES,
    MAX_DEPTH,
    MAX_JOURNAL_BYTES,
    MIN_JOURNAL_BYTES,
    SEQ_MAX,
    STRING_MAX_BYTES,
)
from tools.wct.evidence.pytest_payload_validate import validate_payload
from tools.wct.evidence.pytest_sequence import _DecodeState, _Job
from tools.wct.evidence.pytest_types import ExecutionExpectation, JournalEvent, JournalObservation
from tools.wct.evidence.pytest_wire_framing import _DefectError, _line_defect, canonical_header


def decode_journal(
    data: bytes, *, run_id: str, executions: tuple[ExecutionExpectation, ...], max_bytes: int
) -> JournalObservation:
    """Decodifica el prefijo válido; al primer defecto conserva y para."""
    job = _Job(data=data, run_id=run_id, executions=executions, max_bytes=max_bytes)
    events: list[JournalEvent] = []
    state = _DecodeState(executions)
    if not data:
        return _finish(job, events, 0, None)
    consumed, defect = _consume_header(data, job)
    offset = consumed
    while defect is None and offset < len(data):
        defect, consumed = _consume_line(state, events, data, offset)
        offset = consumed
    return _finish(job, events, consumed, defect)


def _consume_header(data: bytes, job: _Job) -> tuple[int, _DefectError | None]:
    """Consume la cabecera; ante defecto el consumo queda en 0."""
    header_end = data.find(b"\n")
    if header_end == -1:
        return 0, _line_defect(data, unterminated=True)
    if header_end + 1 > LINE_MAX_BYTES:
        return 0, _DefectError("limit_exceeded")
    try:
        _decode_header(data[:header_end], job)
    except _DefectError as caught:
        return 0, caught
    return header_end + 1, None


__all__ = [
    "C0_LIMIT",
    "DECODER_FINDING_CODES",
    "DEL_CHAR",
    "EVENT_CATALOG",
    "LINE_MAX_BYTES",
    "MAX_DEPTH",
    "MAX_JOURNAL_BYTES",
    "MIN_JOURNAL_BYTES",
    "SEQ_MAX",
    "STRING_MAX_BYTES",
    "ExecutionExpectation",
    "_DecodeState",
    "_DefectError",
    "_consume_line",
    "_decode_header",
    "_line_defect",
    "canonical_header",
    "validate_payload",
]
