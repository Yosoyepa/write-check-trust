"""Cabecera completa, canónica y coincidente con los argumentos (§4)."""

from tools.wct.evidence.pytest_limits import (
    _DIGEST_RE,
    _EVENT_VECTOR_FIELDS,
    _RUN_ID_RE,
    HEADER_KEYS,
    RECORD_TYPE,
    SCHEMA_VERSION,
)
from tools.wct.evidence.pytest_sequence import _Job
from tools.wct.evidence.pytest_types import ExecutionExpectation
from tools.wct.evidence.pytest_wire_framing import _DefectError, _parse_line


def _bad_execution(wire: object, literal: list[str]) -> str | None:
    """Estructura inválida es invalid_field; identidad ajena es foreign."""
    if type(wire) is not list or len(wire) != _EVENT_VECTOR_FIELDS:
        return "invalid_field"
    if _bad_wire_strings(wire):
        return "invalid_field"
    return None if wire == literal else "foreign_reference"


def _bad_wire_strings(wire: list[object]) -> bool:
    """Todo elemento es str y los tres digests son lowerhex64."""
    for item in wire:
        if type(item) is not str:
            return True
    for digest in wire[2:5]:
        if type(digest) is not str or _DIGEST_RE.fullmatch(digest) is None:
            return True
    return False


def _match_executions(wire_execs: object, executions: tuple[ExecutionExpectation, ...]) -> None:
    """Cada entrada del wire coincide, en orden, con la expectativa."""
    if type(wire_execs) is not list or len(wire_execs) != len(executions):
        raise _DefectError("invalid_field")
    for wire, expected in zip(wire_execs, executions, strict=True):
        literal = [
            expected.execution_id,
            expected.role,
            expected.input_sha256,
            expected.context_sha256,
            expected.recipe_sha256,
        ]
        verdict = _bad_execution(wire, literal)
        if verdict is not None:
            raise _DefectError(verdict)


def _decode_header(raw: bytes, job: _Job) -> None:
    """Cabecera completa, canónica y coincidente con los argumentos."""
    value = _parse_line(raw)
    if type(value) is not dict:
        raise _DefectError("invalid_field")
    _header_keys(set(value))
    _header_scalars(value)
    _header_run(value["run_id"], job.run_id)
    _match_executions(value["executions"], job.executions)


def _header_keys(keys: set[str]) -> None:
    """Sin campos desconocidos y con todos los requeridos."""
    if not keys <= HEADER_KEYS:
        raise _DefectError("unknown_field")
    if keys != HEADER_KEYS:
        raise _DefectError("invalid_field")


def _header_scalars(value: dict[str, object]) -> None:
    """schema_version del esquema vigente y record_type del contrato."""
    version = value["schema_version"]
    if type(version) is not int:
        raise _DefectError("invalid_field")
    if version != SCHEMA_VERSION:
        raise _DefectError("unknown_schema")
    record = value["record_type"]
    if type(record) is not str:
        raise _DefectError("invalid_field")
    if record != RECORD_TYPE:
        raise _DefectError("unknown_schema")


def _header_run(wire_run: object, run_id: str) -> None:
    """run_id del wire es lowerhex32 y coincide con la expectativa."""
    if type(wire_run) is not str or _RUN_ID_RE.fullmatch(wire_run) is None:
        raise _DefectError("invalid_field")
    if wire_run != run_id:
        raise _DefectError("foreign_reference")
