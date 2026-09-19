"""JSON canónico, framing por línea y defectos de framing (§3-§4)."""

import json

from tools.wct.evidence.pytest_limits import (
    C0_LIMIT,
    DEL_CHAR,
    LINE_MAX_BYTES,
    MAX_DEPTH,
    RECORD_TYPE,
    SCHEMA_VERSION,
)
from tools.wct.evidence.pytest_types import ExecutionExpectation


class _DefectError(Exception):
    """Defecto interno de línea con código del catálogo y ejecución opcional."""

    def __init__(self, code: str, execution_id: str | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.execution_id = execution_id


def canonical_bytes(value: object) -> bytes:
    """Serialización canónica: claves ordenadas, sin espacios, UTF-8."""
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    ).encode("utf-8")


def canonical_header(run_id: str, executions: tuple[ExecutionExpectation, ...]) -> bytes:
    """Cabecera canónica reconstruible desde run_id y expectativas."""
    header = {
        "schema_version": SCHEMA_VERSION,
        "record_type": RECORD_TYPE,
        "run_id": run_id,
        "executions": [
            [
                item.execution_id,
                item.role,
                item.input_sha256,
                item.context_sha256,
                item.recipe_sha256,
            ]
            for item in executions
        ],
    }
    return canonical_bytes(header) + b"\n"


def _depth(value: object) -> int:
    """Profundidad de contenedores: el objeto o arreglo exterior cuenta 1."""
    if isinstance(value, dict):
        children: tuple[object, ...] = tuple(value.values())
    elif isinstance(value, list):
        children = tuple(value)
    else:
        return 0
    return 1 + max((_depth(child) for child in children), default=0)


def _loads(text: str) -> object:
    """JSON estricto: sin claves duplicadas, floats, NaN/Infinity ni >8 niveles."""

    def pairs(entries: list[tuple[str, object]]) -> dict[str, object]:
        unique = dict(entries)
        if len(unique) != len(entries):
            raise _DefectError("invalid_json")
        return unique

    def reject_float(_raw: str) -> float:
        raise _DefectError("invalid_json")

    def reject_constant(_name: str) -> float:
        raise _DefectError("invalid_json")

    try:
        value = json.loads(
            text,
            object_pairs_hook=pairs,
            parse_float=reject_float,
            parse_constant=reject_constant,
        )
    except _DefectError:
        raise
    except (ValueError, RecursionError) as exc:
        raise _DefectError("invalid_json") from exc
    try:
        depth = _depth(value)
    except RecursionError as exc:
        raise _DefectError("invalid_json") from exc
    if depth > MAX_DEPTH:
        raise _DefectError("invalid_json")
    return value


def _check_strings(value: object) -> None:
    """Cero surrogates/C0/DEL dentro de valores string del documento."""
    if isinstance(value, dict):
        for item in value.values():
            _check_strings(item)
    elif isinstance(value, list):
        for item in value:
            _check_strings(item)
    elif isinstance(value, str):
        _reject_control_chars(value)


def _reject_control_chars(value: str) -> None:
    """Surrogates/C0/DEL dentro de un string es invalid_encoding."""
    if any(ord(char) < C0_LIMIT or ord(char) == DEL_CHAR for char in value):
        raise _DefectError("invalid_encoding")


def _parse_line(raw: bytes) -> object:
    """UTF-8 estricto, JSON estricto, canonicidad y contenido de strings."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _DefectError("invalid_encoding") from exc
    value = _loads(text)
    try:
        encoded = canonical_bytes(value)
    except UnicodeEncodeError as exc:
        raise _DefectError("invalid_encoding") from exc
    if encoded != (raw[:-1] if raw.endswith(b"\n") else raw):
        raise _DefectError("noncanonical_json")
    _check_strings(value)
    return value


def _line_defect(line: bytes, *, unterminated: bool) -> _DefectError | None:
    """Precedencia del §4 dentro de la línea: límite, UTF-8 y LF."""
    if len(line) > LINE_MAX_BYTES:
        return _DefectError("limit_exceeded")
    try:
        line.decode("utf-8")
    except UnicodeDecodeError:
        return _DefectError("invalid_encoding")
    return _DefectError("truncated_line") if unterminated else None
