"""Validate campaign identity and accounting before issuing an acceptance verdict."""

from typing import Any

from tools.wct.accept.mutation_cases import mutations
from tools.wct.accept.verdict_validation import _baseline, _count, _result


def _accounting(ir: dict[str, Any], report: dict[str, Any]) -> None:
    inventory = [
        {key: value for key, value in item.items() if key != "ir"} for item in mutations(ir)
    ]
    results = _inventory(report, len(inventory))
    for index, (item, expected) in enumerate(zip(results, inventory, strict=True)):
        _result(item, expected, index)
    _counters(report, results)


def _inventory(report: dict[str, Any], size: int) -> list[dict[str, Any]]:
    if not _count(report.get("planned")) or report["planned"] != size:
        raise ValueError("planned inventory")
    results = report.get("results")
    if type(results) is not list or len(results) != size:
        raise ValueError("results inventory")
    return results


def _counters(report: dict[str, Any], results: list[dict[str, Any]]) -> None:
    for counter, status in (
        ("killed", "killed"),
        ("survived", "survived"),
        ("errors", "error"),
        ("not_run", "not_run"),
    ):
        observed = sum(item["status"] == status for item in results)
        if not _count(report.get(counter)) or report[counter] != observed:
            raise ValueError(f"counter mismatch: {counter}")


def accept_verdict(ir: dict[str, Any], report: dict[str, Any]) -> tuple[bool, list[str]]:
    """Fail closed on legacy, inconsistent, vacuous or incomplete campaigns."""
    vacuous = [scenario["name"] for scenario in ir["scenarios"] if not scenario["examples"]]
    report["vacuous"] = vacuous
    try:
        baseline = _baseline(report)
        _accounting(ir, report)
    except (ValueError, TypeError, KeyError) as error:
        return True, [f"invalid campaign: {error}"]
    return _outcome(baseline, report, vacuous)


def _outcome(
    baseline: dict[str, Any], report: dict[str, Any], vacuous: list[str]
) -> tuple[bool, list[str]]:
    if baseline["status"] != "pass":
        return True, [f"baseline {baseline['status']}: {baseline['reason']}"]
    if report["planned"] == 0:
        return True, [
            "0 mutaciones ejecutadas: TEST-010 exige Examples",
            f"escenarios sin Examples: {', '.join(vacuous)}",
        ]
    failed = report["killed"] != report["planned"]
    return failed, ["campaign has survived/error/not_run results"] if failed else []
