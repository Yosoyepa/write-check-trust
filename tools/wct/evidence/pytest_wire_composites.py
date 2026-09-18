"""Campos compuestos del wire: argv, cwd, utc, excepción y xfail (§3)."""

from datetime import datetime

from tools.wct.evidence.pytest_limits import _UTC_RE, _XFAIL_FIELDS
from tools.wct.evidence.pytest_types import XfailObservation
from tools.wct.evidence.pytest_wire_framing import _DefectError
from tools.wct.evidence.pytest_wire_values import _b, _s


def _argv(value: object) -> tuple[str, ...]:
    """Argv no vacío de strings no vacíos; se conserva como tupla."""
    if type(value) is not list or not value:
        raise _DefectError("invalid_field")
    return tuple(_s(item, min_len=1) for item in value)


def _cwd(value: object) -> str:
    """Cwd absoluto POSIX sin componentes . o .."""
    text = _s(value, min_len=1)
    parts = text.split("/")
    if not text.startswith("/") or "." in parts or ".." in parts:
        raise _DefectError("invalid_field")
    return text


def _utc(value: object) -> str:
    """Marca UTC con formato exacto y fecha/hora válidas, sin leer reloj."""
    text = _s(value, min_len=1)
    if _UTC_RE.fullmatch(text) is None:
        raise _DefectError("invalid_field")
    try:
        datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError as exc:
        raise _DefectError("invalid_field") from exc
    return text


def _exception_type(present: object, name: object) -> str | None:
    """Coherencia exception_present/exception_type del §3."""
    if _b(present):
        return _s(name, min_len=1)
    if name is not None:
        raise _DefectError("invalid_field")
    return None


def _xfail(value: object) -> XfailObservation | None:
    """Null o array exacto [run, strict, raises_present] de bools."""
    if value is None:
        return None
    if type(value) is not list or len(value) != _XFAIL_FIELDS:
        raise _DefectError("invalid_field")
    return XfailObservation(run=_b(value[0]), strict=_b(value[1]), raises_present=_b(value[2]))
