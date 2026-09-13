"""AC1 verdict independently validates identity, counts and baseline causality."""

import copy
from pathlib import Path

import pytest

from tools.wct.accept.pipeline import accept_verdict, parse_feature


def _ir(tmp_path: Path):
    path = tmp_path / "one.feature"
    path.write_text("Feature: F\nScenario Outline: S\nGiven v <x>\nExamples:\n| x |\n| 2 |\n")
    return parse_feature(path)


def _report():
    return {
        "schema_version": 1,
        "baseline": {"status": "pass", "exit": 0, "reason": "all scenarios passed"},
        "results": [
            {
                "id": 0,
                "scenario": "S",
                "row": 0,
                "field": "x",
                "from": "2",
                "to": "0",
                "status": "killed",
                "exit": 1,
                "reason": "semantic mismatch",
            }
        ],
        "planned": 1,
        "killed": 1,
        "survived": 0,
        "errors": 0,
        "not_run": 0,
        "evidence_dir": "build/tmp/independent-literal",
    }


def test_complete_literal_report_passes(tmp_path: Path) -> None:
    assert accept_verdict(_ir(tmp_path), _report()) == (False, [])


def test_historical_false_green_is_rejected(tmp_path: Path) -> None:
    failed, messages = accept_verdict(
        _ir(tmp_path), {"results": [{"status": "killed"}], "killed": 1, "survived": 0}
    )
    assert failed
    assert messages == ["invalid campaign: unsupported campaign schema"]


@pytest.mark.parametrize(
    ("field", "value", "cause"),
    [
        ("schema_version", True, ("schema",)),
        ("schema_version", 2, ("schema",)),
        ("planned", True, ("planned", "inventory")),
        ("planned", 2, ("planned", "inventory")),
        ("killed", 0, ("counter", "killed")),
        ("survived", 1, ("counter", "survived")),
        ("errors", -1, ("counter", "errors")),
        ("not_run", False, ("counter", "not_run")),
        ("results", [], ("results", "inventory")),
        ("baseline", None, ("baseline",)),
        ("evidence_dir", "", ("evidence", "directory")),
    ],
)
def test_report_corruption_blocks(tmp_path: Path, field, value, cause) -> None:
    report = _report()
    report[field] = value
    failed, messages = accept_verdict(_ir(tmp_path), report)
    assert failed
    assert len(messages) == 1
    assert all(word in messages[0].lower() for word in cause)


@pytest.mark.parametrize(
    ("field", "value", "cause"),
    [
        ("id", True, ("identity", "id")),
        ("id", 1, ("identity", "id")),
        ("row", 1, ("identity", "row")),
        ("scenario", "other", ("identity", "scenario")),
        ("field", "wrong", ("identity", "field")),
        ("from", "3", ("identity", "from")),
        ("to", "1", ("identity", "to")),
        ("status", "unknown", ("result", "status")),
        ("exit", 0, ("result", "exit", "status")),
        ("exit", True, ("result", "exit", "type")),
        ("reason", "", ("result", "reason")),
    ],
)
def test_result_identity_corruption_blocks(tmp_path: Path, field, value, cause) -> None:
    report = _report()
    report["results"][0][field] = value
    failed, messages = accept_verdict(_ir(tmp_path), report)
    assert failed
    assert len(messages) == 1
    assert all(word in messages[0].lower() for word in cause)


def test_survivor_is_retained_and_blocks(tmp_path: Path) -> None:
    report = _report()
    report.update(killed=0, survived=1)
    report["results"][0].update(status="survived", exit=0)
    assert accept_verdict(_ir(tmp_path), report)[0]


def test_baseline_failure_preserves_cause(tmp_path: Path) -> None:
    report = _report()
    report["baseline"].update(status="invalid", exit=2, reason="collection failed")
    report.update(killed=0, not_run=1)
    report["results"][0].update(status="not_run", exit=None)
    assert accept_verdict(_ir(tmp_path), report) == (True, ["baseline invalid: collection failed"])


@pytest.mark.parametrize(
    ("status", "exit_code"),
    [("mismatch", 0), ("mismatch", None), ("mismatch", True), ("invalid", False), ("invalid", "1")],
)
def test_malformed_failed_baseline_is_not_a_valid_disposition(tmp_path: Path, status, exit_code):
    report = _report()
    report["baseline"].update(status=status, exit=exit_code)
    report.update(killed=0, not_run=1)
    report["results"][0].update(status="not_run", exit=None)
    assert accept_verdict(_ir(tmp_path), report) == (
        True,
        ["invalid campaign: baseline exit/status"],
    )


def test_zero_mutations_has_vacuous_warning(tmp_path: Path) -> None:
    ir = _ir(tmp_path)
    ir["scenarios"][0]["examples"] = []
    report = _report()
    report.update(results=[], planned=0, killed=0)
    failed, messages = accept_verdict(ir, report)
    assert failed
    assert "TEST-010" in messages[0]
    assert report["vacuous"] == ["S"]


def test_duplicate_results_do_not_hide_inventory(tmp_path: Path) -> None:
    report = _report()
    report["results"].append(copy.deepcopy(report["results"][0]))
    report.update(planned=2, killed=2)
    assert accept_verdict(_ir(tmp_path), report)[0]


def test_results_requires_list_even_when_tuple_inventory_matches(tmp_path: Path) -> None:
    report = _report()
    report["results"] = tuple(report["results"])
    failed, messages = accept_verdict(_ir(tmp_path), report)
    assert failed
    assert "results inventory" in messages[0].lower()


@pytest.mark.parametrize("reason", ["", 1, True, ["reported"], None])
def test_baseline_reason_is_nonempty_text(tmp_path: Path, reason) -> None:
    report = _report()
    report["baseline"]["reason"] = reason
    failed, messages = accept_verdict(_ir(tmp_path), report)
    assert failed
    assert "baseline reason" in messages[0].lower()


@pytest.mark.parametrize(
    ("status", "code", "counter"),
    [
        ("survived", 0, "survived"),
        ("error", 2, "errors"),
        ("error", None, "errors"),
        ("error", -9, "errors"),
    ],
)
def test_valid_residual_is_not_misreported_as_invalid_instrument(
    tmp_path: Path, status, code, counter
) -> None:
    report = _report()
    report.update(killed=0)
    report[counter] = 1
    report["results"][0].update(status=status, exit=code)
    failed, messages = accept_verdict(_ir(tmp_path), report)
    assert failed
    assert len(messages) == 1
    assert "invalid" not in messages[0].lower()
    assert status in messages[0].lower()


@pytest.mark.parametrize(
    ("status", "code", "counter"),
    [
        ("survived", 1, "survived"),
        ("survived", None, "survived"),
        ("not_run", 0, "not_run"),
        ("not_run", 1, "not_run"),
    ],
)
def test_residual_exit_contradiction_is_instrument_invalid(
    tmp_path: Path, status, code, counter
) -> None:
    report = _report()
    if status == "not_run":
        report["baseline"].update(status="invalid", exit=2, reason="collection failed")
    report.update(killed=0)
    report[counter] = 1
    report["results"][0].update(status=status, exit=code)
    failed, messages = accept_verdict(_ir(tmp_path), report)
    assert failed
    assert "invalid campaign" in messages[0].lower()
    assert "exit/status" in messages[0].lower()


@pytest.mark.parametrize("code", [1, 2])
def test_baseline_mismatch_requires_exit_one_and_preserves_cause(tmp_path: Path, code) -> None:
    report = _report()
    report["baseline"].update(status="mismatch", exit=code, reason="observed units disagree")
    report.update(killed=0, not_run=1)
    report["results"][0].update(status="not_run", exit=None)
    failed, messages = accept_verdict(_ir(tmp_path), report)
    assert failed
    expected = (
        "baseline mismatch: observed units disagree"
        if code == 1
        else "invalid campaign: baseline exit/status"
    )
    assert messages == [expected]


def test_non_object_result_names_the_shape_defect(tmp_path: Path) -> None:
    report = _report()
    report["results"] = [None]
    failed, messages = accept_verdict(_ir(tmp_path), report)
    assert failed
    assert all(word in messages[0].lower() for word in ("result", "object"))
