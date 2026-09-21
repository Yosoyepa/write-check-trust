"""Predicados de tipos exactos para payloads de observaciones manuales (§2)."""

from collections.abc import Callable
from datetime import datetime
from typing import TypeGuard

from tools.wct.evidence.pytest_limits import (
    _DIGEST_RE,
    _UTC_RE,
    C0_LIMIT,
    DEL_CHAR,
    SEQ_MAX,
    STRING_MAX_BYTES,
)
from tools.wct.evidence.pytest_types import XfailObservation


def _clean_string(value: str) -> bool:
    """UTF-8 estricto ≤4096 bytes, sin surrogate/C0/DEL (§2)."""
    try:
        size = len(value.encode("utf-8"))
    except UnicodeEncodeError:
        return False
    return size <= STRING_MAX_BYTES and all(
        ord(char) >= C0_LIMIT and ord(char) != DEL_CHAR for char in value
    )


def _is_bool(value: object) -> bool:
    return type(value) is bool


def _is_u(value: object) -> bool:
    return type(value) is int and 0 <= value <= SEQ_MAX


def _is_digest(value: object) -> bool:
    return type(value) is str and _DIGEST_RE.fullmatch(value) is not None


def _is_text(value: object) -> TypeGuard[str]:
    return type(value) is str and value != "" and _clean_string(value)


def _is_broad_text(value: object) -> bool:
    """S con vacío permitido: nodo raíz y collect_report."""
    return type(value) is str and _clean_string(value)


def _is_argv(value: object) -> bool:
    return type(value) is tuple and len(value) > 0 and all(_is_text(item) for item in value)


def _is_cwd(value: object) -> bool:
    if not _is_text(value):
        return False
    parts = value.split("/")
    return value.startswith("/") and "." not in parts and ".." not in parts


def _is_utc(value: object) -> bool:
    if type(value) is not str or _UTC_RE.fullmatch(value) is None:
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError:
        return False
    return True


def _is_xfail(value: object) -> bool:
    return value is None or (
        type(value) is XfailObservation
        and type(value.run) is bool
        and type(value.strict) is bool
        and type(value.raises_present) is bool
    )


def _within(low: int, high: int) -> Callable[[object], bool]:
    return lambda value: type(value) is int and low <= value <= high


def _optional(check: Callable[[object], bool]) -> Callable[[object], bool]:
    return lambda value: value is None or check(value)


def _member_of(options: tuple[str, ...]) -> Callable[[object], bool]:
    return lambda value: type(value) is str and value in options
