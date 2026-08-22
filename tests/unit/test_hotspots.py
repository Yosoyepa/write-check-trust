from collections.abc import Callable
import json
from pathlib import Path
import subprocess

import pytest

from tools.wct.cli import main
from tools.wct.hotspots.engine import churn_from_log, report

NUMSTAT_SAMPLE = """10\t2\tsrc/complex.py
3\t1\tsrc/flat.py
-\t-\tassets/logo.png
7\t7\tsrc/{old_name => complex}.py
5\t0\tsrc/complex.py
"""


def test_churn_accumulates_per_file() -> None:
    churn = churn_from_log(NUMSTAT_SAMPLE)

    assert churn["src/complex.py"] == 31
    assert churn["src/flat.py"] == 4


def test_churn_skips_binaries_and_resolves_renames() -> None:
    churn = churn_from_log(NUMSTAT_SAMPLE)

    assert "assets/logo.png" not in churn
    assert "src/old_name" not in churn


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=test@test", *args],
        cwd=root,
        check=True,
        capture_output=True,
    )


def _commit(root: Path, name: str, content: str) -> None:
    (root / name).parent.mkdir(parents=True, exist_ok=True)
    (root / name).write_text(content, encoding="utf-8")
    _git(root, "add", name)
    _git(root, "commit", "-m", f"touch {name}")


NESTED = (
    "def deep(a):\n"
    "    if a > 0:\n"
    "        if a > 1:\n"
    "            if a > 2:\n"
    "                if a > 3:\n"
    "                    if a > 4:\n"
    "                        if a > 5:\n"
    "                            return 1\n"
    "    return 0\n"
)
FLAT = "def flat(a):\n    if a:\n        return 1\n    return 0\n"


def test_report_ranks_churn_times_complexity(
    project_factory: Callable[..., Path],
) -> None:
    root = project_factory()
    _git(root, "init", "-q")
    _commit(root, "src/deep.py", NESTED)
    _commit(root, "src/deep.py", NESTED + "# segunda vuelta\n")
    _commit(root, "src/flat.py", FLAT)

    result = report(root)

    assert result["days"] == 90
    top = result["files"]
    assert top[0]["file"] == "src/deep.py"
    assert top[0]["churn"] > top[1]["churn"]
    assert top[0]["complexity"] == 21
    assert top[0]["hotspot"] == top[0]["churn"] * top[0]["complexity"]


def test_report_respects_top_limit(project_factory: Callable[..., Path]) -> None:
    root = project_factory()
    _git(root, "init", "-q")
    _commit(root, "src/deep.py", NESTED)
    _commit(root, "src/flat.py", FLAT)

    assert len(report(root, top=1)["files"]) == 1


def test_hotspots_cli_is_advisory_exit_zero(
    project_factory: Callable[..., Path],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = project_factory()
    _git(root, "init", "-q")
    _commit(root, "src/deep.py", NESTED)
    monkeypatch.setenv("WCT_PROJECT_ROOT", str(root))

    assert main(["hotspots", "--json", "--top", "3"]) == 0
    document = json.loads(capsys.readouterr().out)
    assert document["files"][0]["file"] == "src/deep.py"
