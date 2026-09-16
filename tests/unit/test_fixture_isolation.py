"""Aislamiento Git in-process: techo del temporal y restauración exacta (FI1).

Observa el mismo contexto que delega el fixture autouse, dentro del mismo
proceso de pytest: centinelas heredados de entorno, descubrimiento Git bajo
el temporal (observado a través del adaptador productivo tools.wct.util.git)
y restauración de los tres valores al salir.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

import pytest

from tests.conftest import GIT_ENV, git_isolated
from tools.wct.util.git import tracked_files

SENTINELS = {
    "GIT_CEILING_DIRECTORIES": "/outer/ceiling",
    "GIT_DIR": "/outer/git",
    "GIT_WORK_TREE": "/outer/worktree",
}


def _toplevel(cwd: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def test_contexto_aisla_y_restaura_los_sentinelas(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name, value in SENTINELS.items():
        monkeypatch.setenv(name, value)

    with git_isolated(tmp_path) as saved:
        assert os.environ["GIT_CEILING_DIRECTORIES"] == str(tmp_path)
        assert "GIT_DIR" not in os.environ
        assert "GIT_WORK_TREE" not in os.environ
        plain = tmp_path / "sin-repositorio"
        plain.mkdir()
        assert tracked_files(plain) is None
        own = tmp_path / "propio"
        own.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=own, check=True, capture_output=True)
        assert tracked_files(own) == set()

    for name, value in SENTINELS.items():
        assert os.environ[name] == value
    assert saved["GIT_DIR"] == "/outer/git"


def test_contexto_restaura_tambien_los_valores_ausentes(tmp_path: Path) -> None:
    entry = {name: os.environ.get(name) for name in GIT_ENV}
    plain = tmp_path / "sin-repositorio"
    plain.mkdir()

    with git_isolated(tmp_path) as saved:
        assert tracked_files(plain) is None

    for name, value in entry.items():
        assert os.environ.get(name) == value
    assert saved == entry
