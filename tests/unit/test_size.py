from collections.abc import Callable
from pathlib import Path

from tools.wct.gate.runner import REGISTRY, TIERS
from tools.wct.model import Status
from tools.wct.size.engine import file_loc, oversized


def test_file_loc_counts_only_real_code(tmp_path: Path) -> None:
    source = tmp_path / "mixed.py"
    source.write_text(
        '"""Docstring counts: it is content."""\n'
        "\n"
        "# comment-only line\n"
        "value = 1  # trailing comment, still code\n"
        "text = (\n"
        '    "multi-line "\n'
        '    "string"\n'
        ")\n",
        encoding="utf-8",
    )

    assert file_loc(source) == 6


def test_file_loc_of_pure_comments_is_zero(tmp_path: Path) -> None:
    source = tmp_path / "only_comments.py"
    source.write_text("# one\n# two\n\n# three\n", encoding="utf-8")

    assert file_loc(source) == 0


def _oversized(root: Path, relative: str, loc: int) -> Path:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(f"line_{index} = {index}" for index in range(loc)), encoding="utf-8"
    )
    return target


def test_oversized_reports_files_over_limit(project_factory: Callable[..., Path]) -> None:
    root = project_factory()
    _oversized(root, "src/big.py", 520)
    (root / "src/small.py").write_text("value = 1\n", encoding="utf-8")

    report = oversized(root)

    assert report["limit"] == 500
    assert [item["file"] for item in report["files"]] == ["src/big.py"]


def test_gate_fails_on_new_oversized_file(project_factory: Callable[..., Path]) -> None:
    root = project_factory()
    _oversized(root, "src/big.py", 640)

    result = REGISTRY["G-SIZE"](root)

    assert result.status is Status.FAIL
    assert "src/big.py" in result.summary


def test_gate_ratchets_the_count_of_oversized_files(
    project_factory: Callable[..., Path],
) -> None:
    root = project_factory()
    _oversized(root, "src/big.py", 640)
    _oversized(root, "src/other.py", 600)

    result = REGISTRY["G-SIZE"](root)

    assert result.status is Status.FAIL
    assert any("ratchet" in finding for finding in result.details)


def test_baseline_entry_passes_while_ratchet_holds(project_factory: Callable[..., Path]) -> None:
    root = project_factory()
    _oversized(root, "tools/wct/gate/runner.py", 593)

    result = REGISTRY["G-SIZE"](root)

    assert result.status is Status.PASS


def test_size_gate_is_in_commit_pr_and_full_tiers() -> None:
    assert "G-SIZE" in TIERS["commit"]
    assert "G-SIZE" in TIERS["pr"]
    assert "G-SIZE" in TIERS["full"]
    assert "G-SIZE" not in TIERS["fast"]
