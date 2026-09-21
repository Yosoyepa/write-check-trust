"""Coercers escalares del wire: enteros, strings, digests y enums (§3)."""

from tools.wct.evidence.pytest_limits import _DIGEST_RE, SEQ_MAX, STRING_MAX_BYTES
from tools.wct.evidence.pytest_wire_framing import _DefectError


def _int_in(value: object, low: int, high: int) -> int:
    """Entero exacto (bool excluido) dentro de [low, high]."""
    if type(value) is not int or value < low or value > high:
        raise _DefectError("invalid_field")
    return value


def _u(value: object) -> int:
    """U del contrato: entero 0..2**63-1, bool excluido."""
    return _int_in(value, 0, SEQ_MAX)


def _s(value: object, *, min_len: int = 0) -> str:
    """String ≤4096 bytes con mínimo de longitud; sin normalización."""
    if type(value) is not str:
        raise _DefectError("invalid_field")
    size = len(value.encode("utf-8"))
    if not min_len <= size <= STRING_MAX_BYTES:
        raise _DefectError("invalid_field")
    return value


def _opt_s(value: object) -> str | None:
    """String no vacío o None."""
    return None if value is None else _s(value, min_len=1)


def _h(value: object) -> str:
    """Digest lowerhex64."""
    if type(value) is not str or _DIGEST_RE.fullmatch(value) is None:
        raise _DefectError("invalid_field")
    return value


def _opt_h(value: object) -> str | None:
    """Digest lowerhex64 o None."""
    return None if value is None else _h(value)


def _enum(value: object, options: tuple[str, ...]) -> str:
    """Índice entero sin bool sobre una tabla cerrada de strings."""
    return options[_int_in(value, 0, len(options) - 1)]


def _member(value: object, options: tuple[str, ...]) -> str:
    """String literal dentro de un conjunto cerrado (termination, defecto)."""
    if type(value) is not str or value not in options:
        raise _DefectError("invalid_field")
    return value


def _b(value: object) -> bool:
    """Bool exacto: un 0/1 o un entero no sustituyen a true/false."""
    if type(value) is not bool:
        raise _DefectError("invalid_field")
    return value
