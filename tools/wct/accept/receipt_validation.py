"""Pure receipt shape, identity and semantic disposition validation."""

from typing import Any

_KEYS = {"schema_version", "attempt_id", "ir_sha256", "exit", "cases", "errors"}


def _identity(document: Any, attempt_id: str, ir_sha256: str, exit_code: int) -> None:
    if type(document) is not dict or document.keys() != _KEYS:
        raise ValueError("receipt keys")
    for key, expected in (
        ("schema_version", 1),
        ("attempt_id", attempt_id),
        ("ir_sha256", ir_sha256),
        ("exit", exit_code),
    ):
        if type(document[key]) is not type(expected) or document[key] != expected:
            raise ValueError(f"receipt identity/type: {key}")


def _case(case: Any) -> tuple[int, str]:
    if type(case) is not dict or case.keys() != {"scenario", "status"}:
        raise ValueError("case keys")
    if type(case["scenario"]) is not int:
        raise ValueError("case index/duplicate")
    return case["scenario"], case["status"]


def _cases(cases: Any, scenario_count: int) -> list[str]:
    if type(cases) is not list:
        raise ValueError("cases must be a list")
    seen: set[int] = set()
    statuses = []
    for case in cases:
        index, status = _case(case)
        if index in seen:
            raise ValueError("case index/duplicate")
        seen.add(index)
        statuses.append(status)
    if seen != set(range(scenario_count)):
        raise ValueError("case inventory")
    return statuses


def _statuses(statuses: list[str]) -> None:
    if any(
        type(value) is not str or value not in {"pass", "mismatch", "error"} for value in statuses
    ):
        raise ValueError("case status")


def _errors(errors: Any) -> None:
    if type(errors) is not list or any(type(value) is not str or not value for value in errors):
        raise ValueError("errors must contain nonempty strings")
    if errors:
        raise ValueError("runner errors")


def _exit_status(code: int, statuses: list[str]) -> tuple[str, str]:
    if code == 0 and all(value == "pass" for value in statuses):
        return "pass", "all scenarios passed"
    if code == 1 and "mismatch" in statuses:
        return "mismatch", "semantic mismatch"
    raise ValueError("receipt exit/status contradiction")


def _disposition(document: dict[str, Any], scenario_count: int) -> tuple[str, str]:
    statuses = _cases(document["cases"], scenario_count)
    _statuses(statuses)
    _errors(document["errors"])
    if "error" in statuses:
        raise ValueError("runner errors")
    return _exit_status(document["exit"], statuses)
