"""Tests for `wct adopt` lifecycle: lock, check, sync."""

from __future__ import annotations

from collections.abc import Callable
import json
from pathlib import Path
import subprocess

import pytest

from tools.wct.adopt.lifecycle import check, lock, render_check, render_sync, sync
from tools.wct.cli import main


def make_upstream_repo(
    path: Path, remote_url: str = "https://github.com/example/upstream.git"
) -> Path:
    """Create a minimal git repo simulating an upstream source."""
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "coder@example.com"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Coder"], cwd=path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "remote", "add", "origin", remote_url], cwd=path, check=True, capture_output=True
    )
    (path / "tools/wct").mkdir(parents=True, exist_ok=True)
    (path / "tools/wct/engine.py").write_text("def run(): pass\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "feat: initial upstream"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    return path


def test_lock_writes_json_with_correct_hash_and_url(tmp_path: Path) -> None:
    source = make_upstream_repo(tmp_path / "upstream")
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=source, capture_output=True, text=True, check=True
    ).stdout.strip()
    adopter = tmp_path / "adopter"
    adopter.mkdir()

    result = lock(adopter, source, paths=["tools/wct"])

    lock_file = adopter / ".wct-upstream.json"
    assert lock_file.is_file()
    data = json.loads(lock_file.read_text(encoding="utf-8"))
    assert data["upstream"] == "https://github.com/example/upstream.git"
    assert data["commit"] == head_sha
    assert data["paths"] == ["tools/wct"]
    assert "locked_at" in data
    assert result["lock"] == data
    assert result["path"] == str(lock_file)


def test_lock_without_git_in_source_raises_error(tmp_path: Path) -> None:
    non_git_source = tmp_path / "not-a-repo"
    non_git_source.mkdir()
    adopter = tmp_path / "adopter"
    adopter.mkdir()

    with pytest.raises(ValueError, match="repositorio git"):
        lock(adopter, non_git_source)


def test_lock_duplicate_without_force_fails_and_with_force_overwrites(
    tmp_path: Path,
) -> None:
    source = make_upstream_repo(tmp_path / "upstream")
    adopter = tmp_path / "adopter"
    adopter.mkdir()

    lock(adopter, source, paths=["tools/wct"])

    with pytest.raises(ValueError, match="--force"):
        lock(adopter, source, paths=["tools/wct"], force=False)

    result = lock(adopter, source, paths=["tools/wct"], force=True)
    assert (adopter / ".wct-upstream.json").is_file()
    assert result["lock"]["paths"] == ["tools/wct"]


def test_lock_nonexistent_paths_in_source_raises_error(tmp_path: Path) -> None:
    source = make_upstream_repo(tmp_path / "upstream")
    adopter = tmp_path / "adopter"
    adopter.mkdir()

    with pytest.raises(ValueError, match="no existe en source"):
        lock(adopter, source, paths=["nonexistent/dir"])


def test_lock_cli_invocation(
    project_factory: Callable[..., Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = make_upstream_repo(tmp_path / "upstream")
    adopter = project_factory(package="adopter")
    monkeypatch.setenv("WCT_PROJECT_ROOT", str(adopter))

    exit_code = main(["adopt", "lock", "--source", str(source)])
    assert exit_code == 0
    captured = capsys.readouterr().out
    assert ".wct-upstream.json" in captured
    assert (adopter / ".wct-upstream.json").is_file()


def test_check_classifies_drift_behind_and_conflict_candidates(tmp_path: Path) -> None:
    source = make_upstream_repo(tmp_path / "upstream")
    (source / "tools/wct/solo.py").write_text("solo upstream\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=source, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "add solo"], cwd=source, check=True, capture_output=True)

    adopter = tmp_path / "adopter"
    adopter.mkdir()
    lock(adopter, source, paths=["tools/wct"])

    (adopter / "tools/wct").mkdir(parents=True)
    (adopter / "tools/wct/engine.py").write_text("def run(): local_custom()\n", encoding="utf-8")
    (adopter / "tools/wct/local_only.py").write_text("local only\n", encoding="utf-8")

    (source / "tools/wct/engine.py").write_text("def run(): upstream_v2()\n", encoding="utf-8")
    (source / "tools/wct/new_upstream.py").write_text("new upstream\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=source, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "upstream v2"], cwd=source, check=True, capture_output=True
    )

    report = check(adopter, source, ref="HEAD")

    assert "tools/wct/engine.py" in report["drift"]["diverged"]
    assert "tools/wct/local_only.py" in report["drift"]["solo-local"]
    assert "tools/wct/solo.py" in report["drift"]["solo-upstream"]

    behind_paths = [item["path"] for item in report["behind"]]
    assert "tools/wct/engine.py" in behind_paths
    assert "tools/wct/new_upstream.py" in behind_paths

    assert report["conflict_candidates"] == ["tools/wct/engine.py"]

    rendered = render_check(report)
    assert "tools/wct/engine.py" in rendered
    assert "DRIFT" in rendered
    assert "BEHIND" in rendered


def test_check_identical_file_not_in_conflict_candidates(tmp_path: Path) -> None:
    source = make_upstream_repo(tmp_path / "upstream")
    adopter = tmp_path / "adopter"
    adopter.mkdir()
    lock(adopter, source, paths=["tools/wct"])

    (adopter / "tools/wct").mkdir(parents=True)
    (adopter / "tools/wct/engine.py").write_text("def run(): pass\n", encoding="utf-8")

    (source / "tools/wct/engine.py").write_text("def run(): pass_v2\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=source, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "commit B"], cwd=source, check=True, capture_output=True)

    report = check(adopter, source, ref="HEAD")
    assert "tools/wct/engine.py" in report["drift"]["identical"]
    assert report["conflict_candidates"] == []


def test_check_missing_lock_raises_error(tmp_path: Path) -> None:
    source = make_upstream_repo(tmp_path / "upstream")
    adopter = tmp_path / "adopter"
    adopter.mkdir()

    with pytest.raises(ValueError, match=r"falta \.wct-upstream\.json"):
        check(adopter, source)


def test_check_nonexistent_ref_raises_error(tmp_path: Path) -> None:
    source = make_upstream_repo(tmp_path / "upstream")
    adopter = tmp_path / "adopter"
    adopter.mkdir()
    lock(adopter, source, paths=["tools/wct"])

    with pytest.raises(ValueError, match="ref 'nonexistent'"):
        check(adopter, source, ref="nonexistent")


def test_check_cli_json(
    project_factory: Callable[..., Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = make_upstream_repo(tmp_path / "upstream")
    adopter = project_factory(package="adopter")
    monkeypatch.setenv("WCT_PROJECT_ROOT", str(adopter))

    main(["adopt", "lock", "--source", str(source)])
    capsys.readouterr()

    exit_code = main(["adopt", "check", "--source", str(source), "--json"])
    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert "drift" in data
    assert "behind" in data
    assert "conflict_candidates" in data


def test_sync_generates_patch_matching_git_diff(tmp_path: Path) -> None:
    source = make_upstream_repo(tmp_path / "upstream")
    adopter = tmp_path / "adopter"
    adopter.mkdir()
    lock_result = lock(adopter, source, paths=["tools/wct"])
    commit_a = lock_result["lock"]["commit"]

    (source / "tools/wct/engine.py").write_text("def run(): upstream_v2\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=source, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "commit B"], cwd=source, check=True, capture_output=True)

    expected_diff = subprocess.run(
        ["git", "diff", commit_a, "HEAD", "--", "tools/wct"],
        cwd=source,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    out_file = adopter / "build/tmp/wct-sync.patch"
    report = sync(adopter, source, ref="HEAD", out=out_file)

    assert out_file.is_file()
    assert out_file.read_text(encoding="utf-8") == expected_diff
    assert report["patch_path"] == str(out_file)
    assert report["changed_files_count"] == 1
    assert report["conflict_candidates"] == []


def test_sync_lists_conflict_candidates_first_with_warning(tmp_path: Path) -> None:
    source = make_upstream_repo(tmp_path / "upstream")
    adopter = tmp_path / "adopter"
    adopter.mkdir()
    lock(adopter, source, paths=["tools/wct"])

    # Local vendor diverged
    (adopter / "tools/wct").mkdir(parents=True)
    (adopter / "tools/wct/engine.py").write_text("def run(): diverged_local\n", encoding="utf-8")

    # Upstream commit B modifies engine.py and adds other.py
    (source / "tools/wct/engine.py").write_text("def run(): upstream_v2\n", encoding="utf-8")
    (source / "tools/wct/other.py").write_text("other\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=source, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "commit B"], cwd=source, check=True, capture_output=True)

    out_file = adopter / "build/tmp/wct-sync.patch"
    report = sync(adopter, source, ref="HEAD", out=out_file)

    assert report["conflict_candidates"] == ["tools/wct/engine.py"]
    assert report["changed_files_count"] == 2

    rendered = render_sync(report)
    warning_text = "revisar a mano: divergencia local + cambio upstream"
    assert warning_text in rendered
    # Warning and conflict candidates appear before the patch path and summary
    assert rendered.find(warning_text) < rendered.find("Patch generado en:")


def test_sync_does_not_modify_any_files_outside_build(tmp_path: Path) -> None:
    source = make_upstream_repo(tmp_path / "upstream")
    adopter = tmp_path / "adopter"
    adopter.mkdir()
    (adopter / "src").mkdir()
    (adopter / "src/app.py").write_text("print('app')\n", encoding="utf-8")
    (adopter / "tools/wct").mkdir(parents=True)
    (adopter / "tools/wct/engine.py").write_text("def run(): local\n", encoding="utf-8")
    lock(adopter, source, paths=["tools/wct"])

    (source / "tools/wct/engine.py").write_text("def run(): v2\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=source, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "commit B"], cwd=source, check=True, capture_output=True)

    def snapshot(root: Path) -> dict[str, bytes]:
        return {
            p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*")
            if p.is_file() and p.relative_to(root).parts[0] != "build"
        }

    before = snapshot(adopter)
    sync(adopter, source, ref="HEAD", out=adopter / "build/tmp/wct-sync.patch")
    after = snapshot(adopter)

    assert before == after


def test_sync_missing_lock_raises_error(tmp_path: Path) -> None:
    source = make_upstream_repo(tmp_path / "upstream")
    adopter = tmp_path / "adopter"
    adopter.mkdir()

    with pytest.raises(ValueError, match=r"falta \.wct-upstream\.json"):
        sync(adopter, source, ref="HEAD")


def test_sync_cli_json(
    project_factory: Callable[..., Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = make_upstream_repo(tmp_path / "upstream")
    adopter = project_factory(package="adopter")
    monkeypatch.setenv("WCT_PROJECT_ROOT", str(adopter))

    main(["adopt", "lock", "--source", str(source)])
    capsys.readouterr()

    exit_code = main(["adopt", "sync", "--source", str(source), "--ref", "HEAD", "--json"])
    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert "patch_path" in data
    assert "changed_files_count" in data
    assert "conflict_candidates" in data
