"""Tier composition contracts: the pr tier mirrors what PR CI runs."""

from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from tools.wct.cli import parser
from tools.wct.gate.runner import TIERS, gate_coverage_diff
from tools.wct.model import Status


def test_pr_tier_extends_commit_and_adds_pr_ci_gates() -> None:
    extra = set(TIERS["pr"]) - set(TIERS["commit"])

    assert set(TIERS["commit"]).issubset(set(TIERS["pr"]))
    assert extra == {
        "G-HOOKS-WIRED",
        "G-COV-TOTAL",
        "G-COV-DIFF",
        "G-PROP",
        "G-ACCEPT-MUT",
        "G-REDTEAM",
    }


def test_pr_tier_generates_coverage_before_diff() -> None:
    """diff-cover consumes build/coverage/lcov.info: the producer runs first."""
    gates = TIERS["pr"]

    assert gates.index("G-COV-TOTAL") < gates.index("G-COV-DIFF")


def test_full_tier_enforces_docstrings() -> None:
    assert "G-DOC" in TIERS["full"]


def test_full_tier_runs_token_duplication_after_structural() -> None:
    """G-DRY-TOK sin tier = CI instala jscpd y nunca lo usa (hueco real v0.3.0)."""
    assert "G-DRY-TOK" in TIERS["full"]
    assert TIERS["full"].index("G-DRY") < TIERS["full"].index("G-DRY-TOK")


def test_cli_accepts_pr_tier() -> None:
    args = parser().parse_args(["gate", "--tier", "pr"])

    assert args.tier == "pr"


def test_missing_diff_cover_is_error_not_skip(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The pr tier promises CI parity: a missing tool must block, not skip."""
    monkeypatch.setattr("tools.wct.gate.runner.shutil.which", lambda _: None)

    result = gate_coverage_diff(tmp_path)

    assert result.status is Status.ERROR
    assert "diff-cover" in result.summary


def test_unresolvable_base_is_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("tools.wct.gate.runner.shutil.which", lambda _: "/usr/bin/diff-cover")

    class Missing:
        returncode = 1

    def always_missing(_root: Path, *_args: str, **_kwargs: bool) -> Missing:
        return Missing()

    monkeypatch.setattr("tools.wct.util.git.run_git", always_missing)

    result = gate_coverage_diff(tmp_path)

    assert result.status is Status.ERROR
    assert "base" in result.summary


def test_command_uses_resolved_base_and_includes_untracked(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict[str, object] = {}
    # El piso --fail-under nace de thresholds.yaml (ADR-B-01): el fixture
    # declara coverage.diff_min para que el comando pueda construirse.
    governance = tmp_path / "governance"
    governance.mkdir()
    (governance / "policy.yaml").write_text("schema_version: 1\n", encoding="utf-8")
    (governance / "thresholds.yaml").write_text(
        "schema_version: 1\ncoverage:\n  diff_min: 90\n", encoding="utf-8"
    )
    monkeypatch.setattr("tools.wct.gate.runner.shutil.which", lambda _: "/usr/bin/diff-cover")

    class Present:
        returncode = 0

    def always_present(_root: Path, *_args: str, **_kwargs: bool) -> Present:
        return Present()

    monkeypatch.setattr("tools.wct.util.git.run_git", always_present)

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr("tools.wct.gate.runner.subprocess.run", fake_run)

    result = gate_coverage_diff(tmp_path)

    assert result.status is Status.PASS
    command = captured["command"]
    assert "--include-untracked" in command
    assert "--fail-under" in command
    assert "90" in command
    assert "--compare-branch" in command
    assert command[command.index("--compare-branch") + 1] == "origin/main"
