"""Validación de argumentos públicos del API (SH-P03a/1 §2)."""

import re
from typing import cast

from tools.wct.evidence.pytest_limits import (
    C0_LIMIT,
    DEL_CHAR,
    MAX_JOURNAL_BYTES,
    MIN_JOURNAL_BYTES,
    STRING_MAX_BYTES,
)
from tools.wct.evidence.pytest_payloads import ROLES
from tools.wct.evidence.pytest_types import ExecutionExpectation, ObservationError

_RUN_ID_RE = re.compile(r"^[0-9a-f]{32}$")

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")

_EXPECTED_EXECUTIONS = (("collection-1", "collection"), ("producer-1", "producer"))

_MAX_EXPECTED_ENTRIES = 10_000
_EXECUTION_COUNT = 2


def _typed_str(value: object, field: str) -> str:
    """Exige str exacto en la frontera pública."""
    if type(value) is not str:
        raise TypeError(f"{field}: debe ser un string")
    return value


def _validate_run_id(run_id: object) -> str:
    """run_id lowerhex32; tipo malo es TypeError, valor malo es invalid_reference."""
    text = _typed_str(run_id, "run_id")
    if _RUN_ID_RE.fullmatch(text) is None:
        raise ObservationError("invalid_reference", "run_id")
    return text


def _validate_max_bytes(max_bytes: object) -> int:
    """max_bytes int exacto en 1..2MiB; sin default."""
    if type(max_bytes) is not int:
        raise TypeError("max_bytes: debe ser un int exacto, no bool")
    if not MIN_JOURNAL_BYTES <= max_bytes <= MAX_JOURNAL_BYTES:
        raise ObservationError("invalid_reference", "max_bytes")
    return max_bytes


def _validate_expectation(position: int, item: ExecutionExpectation, code: str) -> None:
    """Identidad y digests de una expectativa contra la tabla del §2."""
    expected_id, expected_role = _EXPECTED_EXECUTIONS[position]
    if item.execution_id != expected_id:
        raise ObservationError(code, f"executions[{position}].execution_id")
    if item.role != expected_role or item.role not in ROLES:
        raise ObservationError(code, f"executions[{position}].role")
    _validate_digests(position, item, code)


def _validate_digests(position: int, item: ExecutionExpectation, code: str) -> None:
    """Los tres digests son strings lowerhex64."""
    for name in ("input_sha256", "context_sha256", "recipe_sha256"):
        digest = getattr(item, name)
        if type(digest) is not str or _DIGEST_RE.fullmatch(digest) is None:
            raise ObservationError(code, f"executions[{position}].{name}")


def _validate_executions(executions: object) -> tuple[ExecutionExpectation, ...]:
    """Dos expectativas en orden con identidades y digests revisados."""
    if type(executions) is not tuple:
        raise TypeError("executions: debe ser una tupla de ExecutionExpectation")
    if len(executions) != _EXECUTION_COUNT or any(
        type(item) is not ExecutionExpectation for item in executions
    ):
        raise TypeError("executions: deben ser exactamente dos ExecutionExpectation")
    for position, item in enumerate(executions):
        _validate_expectation(position, item, "invalid_expectations")
    return executions


def _identity_args(values: tuple[object, ...], name: str) -> tuple[str, ...]:
    """Tupla de strings válidos, sin duplicados y bajo el tope del contrato."""
    if type(values) is not tuple:
        raise TypeError(f"{name}: debe ser una tupla de strings")
    for item in values:
        _identity_item(item, name)
    if len(values) > _MAX_EXPECTED_ENTRIES:
        raise ObservationError("limit_exceeded", name)
    if len(set(values)) != len(values):
        raise ObservationError("invalid_reference", name)
    return cast(tuple[str, ...], values)


def _identity_item(item: object, name: str) -> None:
    """Cada identidad es string UTF-8 corto y sin caracteres de control."""
    if type(item) is not str:
        raise TypeError(f"{name}: cada identidad debe ser un string")
    if _identity_size(item, name) > STRING_MAX_BYTES:
        raise ObservationError("invalid_reference", name)
    if any(ord(char) < C0_LIMIT or ord(char) == DEL_CHAR for char in item):
        raise ObservationError("invalid_reference", name)


def _identity_size(item: str, name: str) -> int:
    """Tamaño UTF-8; encoding inválido es invalid_reference."""
    try:
        return len(item.encode("utf-8"))
    except UnicodeEncodeError:
        raise ObservationError("invalid_reference", name) from None
