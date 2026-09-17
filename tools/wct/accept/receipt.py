"""Strict bounded receipts for cooperative acceptance runners."""

import json
import os
from pathlib import Path
import stat
from typing import Any

from tools.wct.accept.receipt_validation import _disposition, _identity

RECEIPT_LIMIT = 1024 * 1024


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate receipt key")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise ValueError(f"non-JSON constant: {value}")


def _read(path: Path) -> Any:
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("receipt is not regular")
        raw = stream.read(RECEIPT_LIMIT + 1)
    if len(raw) > RECEIPT_LIMIT:
        raise ValueError("receipt exceeds byte limit")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=_unique, parse_constant=_constant)


def validate_receipt(
    path: Path, *, attempt_id: str, ir_sha256: str, exit_code: int, scenario_count: int
) -> tuple[str, str]:
    """Return pass/mismatch only for complete, matching regular-file evidence."""
    try:
        document = _read(path)
        _identity(document, attempt_id, ir_sha256, exit_code)
        return _disposition(document, scenario_count)
    except (OSError, ValueError, TypeError, RecursionError) as error:
        return "invalid", f"invalid receipt: {error}"
