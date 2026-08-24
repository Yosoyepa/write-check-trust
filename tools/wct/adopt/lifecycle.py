"""Lifecycle engine for adopted vendor harness (lock, check, sync).

Follows the cruft/copier pattern: couples to an exact upstream commit SHA
rather than loose versions, detects drift, and prepares diff reviews.
DESIGN: PROPOSES, NEVER EXECUTES — no subcommand modifies vendor files.
"""

from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
import subprocess
from typing import Any

from tools.wct.util.git import run_git

LOCK_FILE_NAME = ".wct-upstream.json"
DEFAULT_PATCH_PATH = "build/tmp/wct-sync.patch"
RENAME_FIELD_COUNT = 2


def lock(
    root: Path,
    source: Path,
    paths: list[str] | None = None,
    *,
    force: bool = False,
) -> dict[str, Any]:
    """Lock vendor paths in `root` to the exact commit SHA of local `source` clone."""
    resolved_source = source.resolve()
    git_check = run_git(resolved_source, "rev-parse", "--git-dir", check=False)
    if git_check.returncode != 0:
        raise ValueError(f"source '{source}' no es un repositorio git válido")

    remote_res = run_git(resolved_source, "config", "--get", "remote.origin.url", check=False)
    origin_url = remote_res.stdout.strip()
    if not origin_url:
        raise ValueError(f"source '{source}' no tiene remote origin configurado")

    head_res = run_git(resolved_source, "rev-parse", "HEAD", check=False)
    commit_sha = head_res.stdout.strip()
    if not commit_sha:
        raise ValueError(f"source '{source}' no tiene commit HEAD válido")

    resolved_paths = list(paths) if paths else ["tools/wct"]
    for path_entry in resolved_paths:
        if not (resolved_source / path_entry).exists():
            raise ValueError(f"ruta '{path_entry}' no existe en source '{source}'")

    lock_file = root / LOCK_FILE_NAME
    if lock_file.exists() and not force:
        raise ValueError(".wct-upstream.json ya existe; usa --force para sobrescribir")

    lock_data = {
        "upstream": origin_url,
        "commit": commit_sha,
        "paths": resolved_paths,
        "locked_at": datetime.now(UTC).isoformat(),
    }
    lock_file.write_text(json.dumps(lock_data, indent=2) + "\n", encoding="utf-8")
    return {"path": str(lock_file.resolve()), "lock": lock_data}


def render_lock(report: dict[str, Any]) -> str:
    """Render lock report as human-readable and machine-readable text."""
    return f"{json.dumps(report['lock'], indent=2, ensure_ascii=False)}\n{report['path']}"


def _load_lock(root: Path) -> dict[str, Any]:
    lock_file = root / LOCK_FILE_NAME
    if not lock_file.is_file():
        raise ValueError("falta .wct-upstream.json; corre 'wct adopt lock' primero")
    try:
        data = json.loads(lock_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("formato inválido en .wct-upstream.json") from exc
    if not isinstance(data, dict):
        raise TypeError("formato inválido en .wct-upstream.json")
    return data


def _resolve_git_ref(source: Path, ref: str, label: str) -> str:
    res = run_git(source, "rev-parse", "--verify", f"{ref}^{{commit}}", check=False)
    if res.returncode != 0:
        raise ValueError(f"{label} '{ref}' no existe en source '{source}'")
    return res.stdout.strip()


_ARTIFACT_SUFFIXES = frozenset({".pyc", ".pyo"})


def _is_artifact(child: Path) -> bool:
    relative_parts = child.parts
    return (
        any(part == "__pycache__" for part in relative_parts) or child.suffix in _ARTIFACT_SUFFIXES
    )


def _collect_local_files(root: Path, paths: list[str]) -> set[str]:
    local_files: set[str] = set()
    for path_entry in paths:
        target = root / path_entry
        if target.is_file():
            local_files.add(path_entry)
        elif target.is_dir():
            for child in target.rglob("*"):
                if child.is_file() and not _is_artifact(child):
                    local_files.add(child.relative_to(root).as_posix())
    return local_files


def _collect_upstream_files(source: Path, commit: str, paths: list[str]) -> set[str]:
    res = run_git(source, "ls-tree", "-r", "--name-only", commit, "--", *paths, check=False)
    if res.returncode != 0:
        return set()
    return {line.strip() for line in res.stdout.splitlines() if line.strip()}


def _classify_drift(
    root: Path, source: Path, locked_commit: str, paths: list[str]
) -> dict[str, list[str]]:
    local_files = _collect_local_files(root, paths)
    upstream_files = _collect_upstream_files(source, locked_commit, paths)
    identical: list[str] = []
    diverged: list[str] = []
    solo_local: list[str] = []
    solo_upstream: list[str] = []

    for file_path in sorted(local_files | upstream_files):
        in_local = file_path in local_files
        in_upstream = file_path in upstream_files
        if in_local and not in_upstream:
            solo_local.append(file_path)
        elif in_upstream and not in_local:
            solo_upstream.append(file_path)
        else:
            local_bytes = (root / file_path).read_bytes()
            show = subprocess.run(
                ["git", "show", f"{locked_commit}:{file_path}"],
                cwd=source,
                capture_output=True,
                check=False,
            )
            if local_bytes == show.stdout:
                identical.append(file_path)
            else:
                diverged.append(file_path)

    return {
        "identical": identical,
        "diverged": diverged,
        "solo-local": solo_local,
        "solo-upstream": solo_upstream,
    }


def _compute_behind(
    source: Path, locked_commit: str, ref: str, paths: list[str]
) -> tuple[list[dict[str, str]], set[str]]:
    diff_res = run_git(
        source, "diff", "--name-status", locked_commit, ref, "--", *paths, check=False
    )
    behind: list[dict[str, str]] = []
    changed_paths: set[str] = set()
    for line in diff_res.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        file_path = parts[-1]
        behind.append({"path": file_path, "status": status})
        changed_paths.add(file_path)
        if len(parts) > RENAME_FIELD_COUNT:
            changed_paths.add(parts[1])
    return behind, changed_paths


def check(root: Path, source: Path, ref: str = "HEAD") -> dict[str, Any]:
    """Check drift, behind changes, and conflict candidates against upstream clone."""
    lock_data = _load_lock(root)
    locked_commit = str(lock_data.get("commit", ""))
    paths = list(lock_data.get("paths", ["tools/wct"]))

    resolved_source = source.resolve()
    git_check = run_git(resolved_source, "rev-parse", "--git-dir", check=False)
    if git_check.returncode != 0:
        raise ValueError(f"source '{source}' no es un repositorio git válido")

    _resolve_git_ref(resolved_source, locked_commit, "commit bloqueado")
    _resolve_git_ref(resolved_source, ref, "ref")

    drift = _classify_drift(root, resolved_source, locked_commit, paths)
    behind, changed_paths = _compute_behind(resolved_source, locked_commit, ref, paths)
    conflict_candidates = sorted(set(drift["diverged"]) & changed_paths)

    return {
        "locked_commit": locked_commit,
        "ref": ref,
        "paths": paths,
        "drift": drift,
        "behind": behind,
        "conflict_candidates": conflict_candidates,
    }


def render_check(report: dict[str, Any]) -> str:
    """Render check report as structured, human-readable text."""
    lines = [
        f"wct adopt check (locked: {report['locked_commit'][:10]}, ref: {report['ref']})",
        "=" * 60,
        "DRIFT (local vs upstream@locked):",
        f"  identical: {len(report['drift']['identical'])}",
        f"  diverged: {len(report['drift']['diverged'])}",
    ]
    for path in report["drift"]["diverged"]:
        lines.append(f"    - {path}")
    lines.append(f"  solo-local: {len(report['drift']['solo-local'])}")
    for path in report["drift"]["solo-local"]:
        lines.append(f"    - {path}")
    lines.append(f"  solo-upstream: {len(report['drift']['solo-upstream'])}")
    for path in report["drift"]["solo-upstream"]:
        lines.append(f"    - {path}")

    lines.append("")
    lines.append("BEHIND (upstream@locked vs upstream@ref):")
    lines.append(f"  cambios: {len(report['behind'])}")
    for item in report["behind"]:
        lines.append(f"    - [{item['status']}] {item['path']}")

    lines.append("")
    lines.append("CONFLICT CANDIDATES (diverged ∩ changed):")
    lines.append(f"  candidatos: {len(report['conflict_candidates'])}")
    for path in report["conflict_candidates"]:
        lines.append(f"    - {path} (revisar a mano: divergencia local + cambio upstream)")

    return "\n".join(lines)


def sync(
    root: Path,
    source: Path,
    ref: str,
    out: Path | None = None,
) -> dict[str, Any]:
    """Propose unified diff patch without modifying vendor files."""
    check_report = check(root, source, ref=ref)
    locked_commit = check_report["locked_commit"]
    paths = check_report["paths"]

    resolved_source = source.resolve()
    diff_res = run_git(resolved_source, "diff", locked_commit, ref, "--", *paths, check=False)
    patch_text = diff_res.stdout

    target_out = (root / out) if out else (root / DEFAULT_PATCH_PATH)
    target_out.parent.mkdir(parents=True, exist_ok=True)
    target_out.write_text(patch_text, encoding="utf-8")

    warning = (
        "revisar a mano: divergencia local + cambio upstream"
        if check_report["conflict_candidates"]
        else None
    )
    return {
        "locked_commit": locked_commit,
        "ref": ref,
        "patch_path": str(target_out),
        "changed_files_count": len(check_report["behind"]),
        "conflict_candidates": check_report["conflict_candidates"],
        "warning": warning,
    }


def render_sync(report: dict[str, Any]) -> str:
    """Render sync proposal summary."""
    lines: list[str] = []
    if report["conflict_candidates"]:
        lines.append("ADVERTENCIA: revisar a mano: divergencia local + cambio upstream")
        for candidate in report["conflict_candidates"]:
            lines.append(f"  - {candidate}")
        lines.append("")

    lines.append(f"Patch generado en: {report['patch_path']}")
    lines.append(
        f"Resumen: {report['changed_files_count']} archivos cambiados upstream, "
        f"{len(report['conflict_candidates'])} candidatos a conflicto"
    )
    return "\n".join(lines)
