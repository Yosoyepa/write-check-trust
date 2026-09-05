"""Ruff desnudo extiende el perfil del repo (ADR-D-03): el footgun, cazado.

Repro del handoff de PR-C: `ruff check tools/wct/gate/checks.py` (archivo
intacto de main, limpio bajo el perfil del repo) reportaba I001 falso sin
`--config`: ruff aplicaba otro ruleset con orden de imports mutuamente
excluyente. Todo agente que corría ruff desnudo recibía hallazgos falsos
o formateaba con settings ajenos.
"""

from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from tools.wct.config import find_root

TARGET = "tools/wct/gate/checks.py"
PROFILE = "governance/lint/ruff.toml"


def _ruff_check(repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    """Corre ``ruff check`` sobre el archivo del repro desde ``repo``."""
    return subprocess.run(
        ["ruff", "check", *extra, TARGET],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.mark.integration
def test_bare_ruff_check_uses_repo_profile() -> None:
    """`ruff check` SIN --config pasa sobre un archivo limpio del repo.

    pyproject.toml lleva ``[tool.ruff] extend`` apuntando al perfil viviente:
    el comando desnudo hereda el mismo ruleset que el autoritativo.
    """
    repo = find_root()

    completed = _ruff_check(repo)

    assert completed.returncode == 0, completed.stdout + completed.stderr


@pytest.mark.integration
def test_explicit_config_ruff_check_still_passes() -> None:
    """No-regresión: el comando autoritativo con --config sigue pasando (G-LINT)."""
    repo = find_root()

    completed = _ruff_check(repo, "--config", PROFILE)

    assert completed.returncode == 0, completed.stdout + completed.stderr
