"""Pure campaign result and baseline schema checks."""

from typing import Any


def _count(value: Any) -> bool:
    return type(value) is int and value >= 0


def _identity(item: Any, expected: dict[str, Any], index: int) -> None:
    if type(item) is not dict:
        raise ValueError("result must be an object")
    for key, value in {"id": index, **expected}.items():
        if type(item.get(key)) is not type(value) or item[key] != value:
            raise ValueError(f"result identity: {index}/{key}")


def _result(item: Any, expected: dict[str, Any], index: int) -> None:
    _identity(item, expected, index)
    status = item.get("status")
    if status not in ("killed", "survived", "error", "not_run"):
        raise ValueError("result status")
    if type(item.get("reason")) is not str or not item["reason"]:
        raise ValueError("result reason")
    _exit(status, item.get("exit"))


def _exit(status: str, code: Any) -> None:
    if code is not None and type(code) is not int:
        raise ValueError("result exit type")
    required = {"killed": 1, "survived": 0, "not_run": None}
    if status in required and code != required[status]:
        raise ValueError("result exit/status")


def _header(report: dict[str, Any]) -> None:
    if type(report.get("schema_version")) is not int or report["schema_version"] != 1:
        raise ValueError("unsupported campaign schema")
    if type(report.get("evidence_dir")) is not str or not report["evidence_dir"]:
        raise ValueError("missing evidence directory")


def _baseline(report: dict[str, Any]) -> dict[str, Any]:
    _header(report)
    baseline = report.get("baseline")
    if type(baseline) is not dict or baseline.get("status") not in ("pass", "mismatch", "invalid"):
        raise ValueError("missing/invalid baseline")
    _baseline_exit(baseline)
    if type(baseline.get("reason")) is not str or not baseline["reason"]:
        raise ValueError("baseline reason")
    return baseline


def _baseline_exit(baseline: dict[str, Any]) -> None:
    code = baseline.get("exit")
    if code is not None and type(code) is not int:
        raise ValueError("baseline exit/status")
    if baseline["status"] == "invalid":
        return
    if code != {"pass": 0, "mismatch": 1}[baseline["status"]]:
        raise ValueError("baseline exit/status")
