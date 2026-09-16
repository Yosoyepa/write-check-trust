"""Fixtures de raíces Git y umbral de cobertura diff."""

from __future__ import annotations

from pathlib import Path
import subprocess

from tools.wct.selftest.fixtures_governance import _plant, _vulture_governance

COVERAGE_DIFF_MIN = 90


def _git_track(root: Path) -> Path:
    """Trackea el fixture: detect-secrets enumera directorios vía ``git ls-files``."""
    for command in (("git", "init", "-q"), ("git", "add", "-A")):
        subprocess.run(command, cwd=root, check=True, capture_output=True)
    return root


def _git_base(root: Path) -> Path:
    """Planta la gobernanza mínima y la commitea: ``main`` resuelve en rev-parse.

    El commit base es innegociable (ADR-F-01): sin él ``remote_base`` no
    encuentra rama y G-COV-DIFF reporta ERROR en vez de FAIL. Identidad y
    ``commit.gpgsign=false`` van explícitos en el comando para que el
    builder funcione en cualquier máquina/CI sin configuración de git.
    """
    _plant(
        root,
        {
            "governance/policy.yaml": "schema_version: 1\n",
            "governance/thresholds.yaml": (
                f"schema_version: 1\ncoverage:\n  diff_min: {COVERAGE_DIFF_MIN}\n"
            ),
        },
    )
    for command in (
        ("git", "init", "-q", "-b", "main"),
        ("git", "add", "-A"),
        (
            "git",
            "-c",
            "user.email=wct@redteam",
            "-c",
            "user.name=wct-redteam",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-q",
            "-m",
            "base",
        ),
    ):
        subprocess.run(command, cwd=root, check=True, capture_output=True)
    return root


def f11_a(tmp_path: Path) -> Path:
    """F11-a: from-import muerto que nadie referencia."""
    return _plant(
        tmp_path,
        _vulture_governance(
            {
                "src/example/__init__.py": "",
                "src/example/legacy.py": "from os import path\n",
            }
        ),
    )


def f11_b(tmp_path: Path) -> Path:
    """F11-b: constante muerta a confianza 60 — la clase redimida (ADR-D-02).

    El umbral productivo bajó de 80 a 60: la muerte función/constante/
    atributo (confianza 60 de vulture) ya no escapa al gate. La gobernanza
    del fixture replica ese umbral y planta la constante muerta.
    """
    return _plant(
        tmp_path,
        _vulture_governance(
            {
                "src/example/__init__.py": "",
                "src/example/legacy.py": "UNUSED_CONSTANT = 7\n",
            }
        ),
    )
