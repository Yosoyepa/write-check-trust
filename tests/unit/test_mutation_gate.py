"""Tests for the differential behavior of G-MUT-SITES (TEST-007)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.wct.gate.runner import gate_mutation_sites
from tools.wct.model import Status


def test_legacy_file_over_limit_without_changed_functions_does_not_block(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """TEST-007 covers CHANGED files.

    A legacy file over the site budget that the diff did not touch must not
    block the gate.
    """
    report = {
        "files": [
            {
                "file": "src/legacy/http.py",
                "sites": 150,
                "over_limit": True,
                "changed_functions": [],
            }
        ],
        "over_limit": ["src/legacy/http.py"],
    }
    monkeypatch.setattr("tools.wct.gate.runner.scan_mutations", lambda _root: report)

    result = gate_mutation_sites(tmp_path)

    assert result.status is Status.PASS


def test_file_over_limit_with_changed_functions_blocks(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    report = {
        "files": [
            {
                "file": "src/mine/worker.py",
                "sites": 150,
                "over_limit": True,
                "changed_functions": ["src/mine/worker.py::run"],
            }
        ],
        "over_limit": ["src/mine/worker.py"],
    }
    monkeypatch.setattr("tools.wct.gate.runner.scan_mutations", lambda _root: report)

    result = gate_mutation_sites(tmp_path)

    assert result.status is Status.FAIL
    assert "src/mine/worker.py" in result.summary


@pytest.mark.parametrize(
    ("changed", "expected"),
    [([], Status.PASS), (["src/a.py::f"], Status.FAIL)],
)
def test_blocking_depends_on_changed_functions(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    changed: list[str],
    expected: Status,
) -> None:
    monkeypatch.setattr(
        "tools.wct.gate.runner.scan_mutations",
        lambda _root: {
            "files": [
                {"file": "src/a.py", "sites": 101, "over_limit": True, "changed_functions": changed}
            ],
            "over_limit": ["src/a.py"],
        },
    )

    assert gate_mutation_sites(tmp_path).status is expected
