"""Decodificación de una línea de evento con la precedencia del §4."""

from dataclasses import replace
import hashlib

from tools.wct.evidence.pytest_builders import _BUILDERS
from tools.wct.evidence.pytest_event_catalog import EVENT_CATALOG
from tools.wct.evidence.pytest_limits import _EVENT_VECTOR_FIELDS, SEQ_MAX
from tools.wct.evidence.pytest_payload_classes import CollectionReport, ExecutionStart
from tools.wct.evidence.pytest_payloads import NodeDeclaration
from tools.wct.evidence.pytest_sequence import (
    _check_inventory,
    _check_sequence,
    _DecodeState,
    _inventory_key,
    _Job,
    _register_declaration,
)
from tools.wct.evidence.pytest_types import (
    ExecutionExpectation,
    JournalEvent,
    JournalObservation,
    ProtocolFinding,
)
from tools.wct.evidence.pytest_wire_fields import WIRE_FIELDS
from tools.wct.evidence.pytest_wire_framing import _DefectError, _line_defect, _parse_line
from tools.wct.evidence.pytest_wire_values import _int_in


def _resolve_nodeid(state: _DecodeState, index: int) -> str:
    """Resuelve la referencia contra la tabla global; ajena es foreign."""
    if index >= len(state.declarations):
        raise _DefectError("foreign_reference")
    return state.declarations[index]


_CATALOG: dict[int, tuple[str, str, type]] = {
    code: (origin, kind, cls) for code, origin, kind, cls in EVENT_CATALOG
}


def _validated_vector(cls: type, values: object) -> dict[str, object]:
    """Arididad exacta del vector; el nodeid referido queda como índice."""
    names = WIRE_FIELDS[cls]
    if type(values) is not list or len(values) != len(names):
        raise _DefectError("invalid_field")
    fields = dict(zip(names, values, strict=True))
    if "nodeid" in fields and cls is not NodeDeclaration:
        fields["nodeid"] = _int_in(fields["nodeid"], 0, SEQ_MAX)
    return fields


def _build_payload(cls: type, fields: dict[str, object], state: _DecodeState) -> object:
    """Resuelve el nodeid contra la tabla y construye el payload frozen."""
    if "nodeid" in fields and cls is not NodeDeclaration:
        _resolve_field_nodeid(cls, fields, state)
    payload = _BUILDERS[cls](fields)
    if isinstance(payload, NodeDeclaration):
        _register_declaration(state, payload)
    return payload


def _resolve_field_nodeid(cls: type, fields: dict[str, object], state: _DecodeState) -> None:
    """El índice de nodeid resuelve contra la tabla; vacío solo en reports."""
    index = fields["nodeid"]
    if type(index) is not int:
        raise _DefectError("invalid_field")
    nodeid = _resolve_nodeid(state, index)
    if cls is not CollectionReport and nodeid == "":
        raise _DefectError("invalid_field")
    fields["nodeid"] = nodeid


def _decode_event(raw: bytes, offset: int, state: _DecodeState) -> JournalEvent:
    """Decodifica una línea de evento con la precedencia del §4."""
    value = _parse_line(raw)
    if type(value) is not list or len(value) != _EVENT_VECTOR_FIELDS:
        raise _DefectError("invalid_field")
    seq, ex_value, local, code, values = value
    if type(code) is not int or code not in _CATALOG:
        raise _DefectError("unknown_event")
    origin, kind, cls = _CATALOG[code]
    attributed = _attributed_execution(ex_value, state)
    fields = _validated_vector(cls, values)
    payload = _build_payload(cls, fields, state)
    ex = _execution_index(ex_value, state, attributed)
    payload = _reconstruct_refs(payload, state.executions[ex])
    _check_sequence(state, seq, local, origin, ex)
    _check_inventory(state, ex, _inventory_key(cls, payload))
    return JournalEvent(
        seq=seq,
        execution_id=state.executions[ex].execution_id,
        origin=origin,
        local_seq=local,
        kind=kind,
        payload=payload,
        offset=offset,
        end_offset=offset + len(raw),
    )


def _reconstruct_refs(payload: object, expected: ExecutionExpectation) -> object:
    """execution_start recupera role y digests de su única cabecera."""
    if not isinstance(payload, ExecutionStart):
        return payload
    return replace(
        payload,
        role=expected.role,
        input_sha256=expected.input_sha256,
        context_sha256=expected.context_sha256,
        recipe_sha256=expected.recipe_sha256,
    )


def _attributed_execution(ex_value: object, state: _DecodeState) -> str | None:
    """Ejecución atribuible a un defecto antes de validar el índice."""
    if type(ex_value) is int and 0 <= ex_value < len(state.executions):
        return state.executions[ex_value].execution_id
    return None


def _execution_index(ex_value: object, state: _DecodeState, attributed: str | None) -> int:
    """execution_index dentro de la cabecera; fuera de rango es foreign."""
    if type(ex_value) is not int:
        raise _DefectError("invalid_field", attributed)
    if ex_value < 0 or ex_value >= len(state.executions):
        raise _DefectError("foreign_reference", attributed)
    return ex_value


def _finish(
    job: _Job, events: list[JournalEvent], consumed: int, defect: _DefectError | None
) -> JournalObservation:
    """JournalObservation final con finding opcional y hash del sufijo."""
    findings: tuple[ProtocolFinding, ...] = ()
    if defect is not None:
        findings = (
            ProtocolFinding(
                code=defect.code,
                execution_id=defect.execution_id,
                nodeid=None,
                phase=None,
                offset=consumed,
            ),
        )
    tail = hashlib.sha256(job.data[consumed:]).hexdigest()
    return JournalObservation(
        run_id=job.run_id,
        executions=job.executions,
        events=tuple(events),
        findings=findings,
        consumed_bytes=consumed,
        tail_sha256=None if consumed == len(job.data) else tail,
        max_bytes=job.max_bytes,
    )


def _consume_line(
    state: _DecodeState, events: list[JournalEvent], data: bytes, offset: int
) -> tuple[_DefectError | None, int]:
    """Consume una línea; ante defecto devuelve código y offset conservado."""
    line_end = data.find(b"\n", offset)
    line = data[offset:] if line_end == -1 else data[offset : line_end + 1]
    defect = _line_defect(line, unterminated=line_end == -1)
    if defect is not None:
        return defect, offset
    try:
        events.append(_decode_event(line, offset, state))
    except _DefectError as caught:
        return caught, offset
    return None, line_end + 1
