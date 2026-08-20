"""Tests for WCT integrity classification of protected-path drift."""

from __future__ import annotations

from collections.abc import Callable
import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from tools.wct.integrity.engine import _classify, _protected, bless, review, write_lock


def test_classify_modified_file_is_violation() -> None:
    """A protected file whose hash changed is always a violation."""
    problems, warnings = _classify({"a.yml": "old"}, {"a.yml": "new"}, {"a.yml"})
    assert problems == ["modificado: a.yml"]
    assert warnings == []


def test_classify_new_protected_file_is_violation() -> None:
    """A new file under a protected route requires a bless."""
    problems, warnings = _classify({}, {"b.yml": "hash"}, {"b.yml"})
    assert problems == ["nuevo protegido: b.yml"]
    assert warnings == []


def test_classify_missing_tracked_file_is_violation() -> None:
    """A tracked protected file missing from disk is a real deletion."""
    problems, warnings = _classify({"c.yml": "hash"}, {}, {"c.yml"})
    assert problems == ["eliminado protegido: c.yml"]
    assert warnings == []


def test_classify_missing_untracked_file_is_warning() -> None:
    """Untracked protected paths cannot be attacked through a PR.

    They warn instead of failing (e.g. gitignored local skills).
    """
    problems, warnings = _classify({"skill/SKILL.md": "hash"}, {}, set())
    assert problems == []
    assert warnings == ["ausente no versionado (omitido): skill/SKILL.md"]


def test_classify_missing_fails_closed_without_git() -> None:
    """Without git tracking info every missing protected file stays a violation."""
    problems, warnings = _classify({"d.yml": "hash"}, {}, None)
    assert problems == ["eliminado protegido: d.yml"]
    assert warnings == []


def test_classify_in_sync() -> None:
    """No drift means no violations and no warnings."""
    problems, warnings = _classify({"e.yml": "h"}, {"e.yml": "h"}, {"e.yml"})
    assert problems == []
    assert warnings == []


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def test_review_warns_when_missing_protected_path_is_untracked(
    project_factory: Callable[..., Path],
) -> None:
    """A CI runner without locally-installed untracked skills must not fail."""
    root = project_factory()
    local = root / ".claude" / "settings.json"
    local.parent.mkdir(parents=True)
    local.write_text("{}", encoding="utf-8")
    _git(root, "init")
    _git(root, "add", "governance/policy.yaml")
    write_lock(root)
    local.unlink()

    problems, warnings = review(root)

    assert problems == []
    assert warnings == ["ausente no versionado (omitido): .claude/settings.json"]


def test_review_fails_when_missing_protected_path_is_tracked(
    project_factory: Callable[..., Path],
) -> None:
    """Deleting a versioned protected file is a real attack on the control plane."""
    root = project_factory()
    _git(root, "init")
    _git(root, "add", "governance/baselines/suppressions.json")
    write_lock(root)
    (root / "governance/baselines/suppressions.json").unlink()

    problems, warnings = review(root)

    assert problems == ["eliminado protegido: governance/baselines/suppressions.json"]
    assert warnings == []


def test_review_fails_closed_without_git(
    project_factory: Callable[..., Path],
) -> None:
    """No git information: a missing protected path stays a violation."""
    root = project_factory()
    write_lock(root)
    (root / "governance/baselines/suppressions.json").unlink()

    problems, warnings = review(root)

    assert problems == ["eliminado protegido: governance/baselines/suppressions.json"]
    assert warnings == []


def test_lock_hash_is_immune_to_eol_differences(
    project_factory: Callable[..., Path],
) -> None:
    """A CRLF checkout of the same content must not demand a re-bless."""
    root = project_factory()
    target = root / "governance/baselines/suppressions.json"
    original = target.read_bytes()
    write_lock(root)
    target.write_bytes(original.replace(b"\n", b"\r\n"))

    problems, warnings = review(root)

    assert problems == []
    assert warnings == []


def test_legacy_lock_without_algorithm_field_compares_raw_bytes(
    project_factory: Callable[..., Path],
) -> None:
    """Locks written before the EOL-normalized algorithm keep comparing raw."""
    root = project_factory()
    raw = {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in _protected(root)
    }
    (root / "governance/integrity.lock").write_text(
        json.dumps({"schema_version": 1, "commit": None, "files": raw}, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )

    problems, _warnings = review(root)

    assert problems == []


def test_bless_requires_approval_evidence_in_reason(
    project_factory: Callable[..., Path],
) -> None:
    """A bare prose reason is not enough: cite the PR or comment that approved."""
    root = project_factory()
    with pytest.raises(ValueError, match="evidencia"):
        bless(root, "cambio de umbral autorizado verbalmente", "mantenedor")

    bless(root, "aprobado en PR #66 por el mantenedor", "mantenedor")

    assert (root / "governance/integrity.lock").is_file()
    assert "PR #66" in (root / "governance/integrity-log.md").read_text(encoding="utf-8")
