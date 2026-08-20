from collections.abc import Callable
import json
from pathlib import Path

import pytest

from tools.wct.mutate.engine import function_hashes, mutation_sites, scan, update_manifest


def test_mutation_scan_counts_behavioral_sites(tmp_path: Path) -> None:
    source = tmp_path / "sample.py"
    source.write_text(
        """def choose(value):
    if value > 3 and value < 9:
        return value + 1
    return 0
""",
        encoding="utf-8",
    )

    assert mutation_sites(source) >= 6
    assert len(function_hashes(source, tmp_path)) == 1


def test_function_identity_survives_line_shift(tmp_path: Path) -> None:
    """Adding an import above must not invalidate every function below it."""
    source = tmp_path / "sample.py"
    source.write_text("def keep():\n    return 1\n", encoding="utf-8")
    before = function_hashes(source, tmp_path)
    source.write_text("# padding\n# padding\n\ndef keep():\n    return 1\n", encoding="utf-8")

    assert function_hashes(source, tmp_path) == before


def test_function_body_change_invalidates_fingerprint(tmp_path: Path) -> None:
    source = tmp_path / "sample.py"
    source.write_text("def keep():\n    return 1\n", encoding="utf-8")
    before = function_hashes(source, tmp_path)
    source.write_text("def keep():\n    return 2\n", encoding="utf-8")
    after = function_hashes(source, tmp_path)

    assert set(after) == set(before)
    assert after != before


def test_same_method_name_in_different_classes_keeps_distinct_identity(
    tmp_path: Path,
) -> None:
    source = tmp_path / "sample.py"
    source.write_text(
        "class Alpha:\n    def run(self):\n        return 1\n"
        "class Beta:\n    def run(self):\n        return 2\n",
        encoding="utf-8",
    )

    keys = set(function_hashes(source, tmp_path))

    assert keys == {"sample.py::Alpha.run", "sample.py::Beta.run"}


def test_scan_treats_legacy_manifest_as_pending_migration(
    project_factory: Callable[..., Path],
) -> None:
    """A schema-1 manifest (lineno keys) matches nothing.

    Everything counts as changed until `update-manifest` migrates it. Red,
    not silent.
    """
    root = project_factory()
    (root / "src/code.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    manifest = root / "governance/generated/mutation-manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps({"schema_version": 1, "functions": {"src/code.py::value:1": "dead"}}),
        encoding="utf-8",
    )

    report = scan(root)

    assert report["changed_functions"] == 1


def test_update_manifest_without_approval_leaves_lock_alone(
    project_factory: Callable[..., Path],
) -> None:
    root = project_factory()
    (root / "src/code.py").write_text("def value():\n    return 1\n", encoding="utf-8")

    path = update_manifest(root)

    assert json.loads(path.read_text(encoding="utf-8"))["schema_version"] == 2
    assert not (root / "governance/integrity.lock").exists()


def test_update_manifest_with_approval_regenerates_lock_and_logs(
    project_factory: Callable[..., Path],
) -> None:
    root = project_factory()
    (root / "src/code.py").write_text("def value():\n    return 1\n", encoding="utf-8")

    update_manifest(root, approved_by="mantenedor", reason="aprobado en PR #70")

    assert (root / "governance/integrity.lock").is_file()
    log = (root / "governance/integrity-log.md").read_text(encoding="utf-8")
    assert "PR #70" in log


def test_update_manifest_rejects_partial_approval(
    project_factory: Callable[..., Path],
) -> None:
    root = project_factory()
    with pytest.raises(ValueError, match="juntos"):
        update_manifest(root, approved_by="mantenedor")
