from collections.abc import Callable
import json
from pathlib import Path

import pytest

from tools.wct.cli import main
from tools.wct.ratchet.measure import record

REASON = "re-baseline por cambio de scope en PR #30"

TERM_REPORT = """\
Name                             Stmts   Miss Branch BrPart  Cover
TOTAL                               61      1      6      1    97%
"""


def _baseline_contents(root: Path) -> dict[str, str]:
    directory = root / "governance/baselines"
    return {
        path.name: path.read_text(encoding="utf-8") for path in sorted(directory.glob("*.json"))
    }


class _FakeCompleted:
    def __init__(self, stdout: str, returncode: int) -> None:
        self.stdout = stdout
        self.stderr = ""
        self.returncode = returncode


def test_record_single_metric_writes_only_that_baseline(
    project_factory: Callable[..., Path],
) -> None:
    """`record --metric` re-estampa SU baseline; los demás quedan intactos."""
    root = project_factory()
    before = _baseline_contents(root)

    written = record(root, "mantenedor", REASON, metric="suppressions")

    assert [path.name for path in written] == ["suppressions.json"]
    after = _baseline_contents(root)
    changed = {name for name, text in before.items() if text != after[name]}
    assert changed == {"suppressions.json"}
    document = json.loads(after["suppressions.json"])
    assert document["recorded_by"] == "mantenedor"
    assert document["commit"] is None  # el fixture vive fuera de git
    log = (root / "governance/ratchet-log.md").read_text(encoding="utf-8")
    assert REASON in log
    assert "- Metrics: suppressions" in log


def test_record_unknown_metric_lists_valid_metrics(
    project_factory: Callable[..., Path],
) -> None:
    root = project_factory()

    with pytest.raises(ValueError, match="coverage-total") as error:
        record(root, "mantenedor", REASON, metric="metrica-inventada")

    assert "suppressions" in str(error.value)


def test_record_without_metric_still_rewrites_every_baseline(
    project_factory: Callable[..., Path],
) -> None:
    """Sin --metric se preserva la semántica actual: re-estampa todas las medidas."""
    root = project_factory()

    written = record(root, "mantenedor", REASON)

    assert {path.name for path in written} == {
        "suppressions.json",
        "debt-markers.json",
        "introverted-tests.json",
        "archmetrics-zones.json",
        "per-file-ignores.json",
        "file-size.json",
        "lcom-classes.json",
        "dry-template-clusters.json",
    }
    log = (root / "governance/ratchet-log.md").read_text(encoding="utf-8")
    assert "- Metrics:" not in log


def test_record_coverage_total_uses_one_authoritative_suite_run(
    project_factory: Callable[..., Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """coverage-total se registra del TOTAL oficial de UNA corrida de la suite."""
    root = project_factory()
    before = _baseline_contents(root)
    commands: list[list[str]] = []

    def fake_run(command: list[str], **_kwargs: object) -> _FakeCompleted:
        commands.append(list(command))
        return _FakeCompleted(TERM_REPORT, returncode=0)

    monkeypatch.setattr("tools.wct.ratchet.measure.subprocess.run", fake_run)

    record(root, "mantenedor", REASON, metric="coverage-total")

    # measurements() ya lanza su interrogate: lo que debe ser UNO es el run
    # de pytest de la fuente autoritativa.
    suite_runs = [command for command in commands if "pytest" in command]
    assert len(suite_runs) == 1
    assert suite_runs[0][1:] == [
        "-m",
        "pytest",
        "--cov",
        "--cov-branch",
        "--cov-report=term",
        "-q",
        "-m",
        "not property",
    ]
    after = _baseline_contents(root)
    changed = {name for name, text in before.items() if text != after[name]}
    assert changed == {"coverage-total.json"}
    assert json.loads(after["coverage-total.json"])["value"] == 97.0


def test_record_coverage_total_requires_the_term_total_line(
    project_factory: Callable[..., Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Una corrida sin línea TOTAL no registra nada: falla declarando la causa."""
    root = project_factory()
    before = _baseline_contents(root)

    def fake_run(_command: list[str], **_kwargs: object) -> _FakeCompleted:
        return _FakeCompleted("1 failed in 0.1s", returncode=1)

    monkeypatch.setattr("tools.wct.ratchet.measure.subprocess.run", fake_run)

    with pytest.raises(ValueError, match="TOTAL"):
        record(root, "mantenedor", REASON, metric="coverage-total")

    assert before == _baseline_contents(root)


def test_cli_record_forwards_metric(
    project_factory: Callable[..., Path],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = project_factory()
    monkeypatch.setenv("WCT_PROJECT_ROOT", str(root))

    exit_code = main(
        [
            "ratchet",
            "record",
            "--metric",
            "suppressions",
            "--approved-by",
            "mantenedor",
            "--reason",
            REASON,
        ]
    )

    assert exit_code == 0
    assert "suppressions.json" in capsys.readouterr().out
