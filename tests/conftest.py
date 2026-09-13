from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import os
from pathlib import Path
import shutil

import pytest
import yaml

GIT_ENV = ("GIT_CEILING_DIRECTORIES", "GIT_DIR", "GIT_WORK_TREE")


@contextmanager
def git_isolated(tmp_path: Path) -> Iterator[dict[str, str | None]]:
    """Limita el descubrimiento Git del proceso al temporal de la prueba (FI1).

    Dentro del contexto el techo Git es el temporal y no hay GIT_DIR ni
    GIT_WORK_TREE heredados: un directorio sin repositorio bajo el temporal
    no descubre repositorios ancestro, y un repositorio propio creado
    dentro del temporal sigue descubriéndose como raíz. Al salir restaura
    los tres valores exactamente como estaban y entrega la instantánea
    guardada para que el test observe la restauración.
    """
    saved = {name: os.environ.get(name) for name in GIT_ENV}
    os.environ["GIT_CEILING_DIRECTORIES"] = str(tmp_path)
    for name in ("GIT_DIR", "GIT_WORK_TREE"):
        os.environ.pop(name, None)
    try:
        yield saved
    finally:
        for name, value in saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


@pytest.fixture(autouse=True)
def git_isolation(tmp_path: Path) -> Iterator[None]:
    """Cada prueba corre con el descubrimiento Git limitado a su temporal."""
    with git_isolated(tmp_path):
        yield


@pytest.fixture
def project_factory(tmp_path: Path) -> object:
    template = Path(__file__).parents[1]

    def create(*, package: str = "example") -> Path:
        root = tmp_path / package
        root.mkdir()
        governance = root / "governance"
        governance.mkdir()
        shutil.copy(template / "governance/policy.yaml", governance / "policy.yaml")
        shutil.copy(template / "governance/thresholds.yaml", governance / "thresholds.yaml")
        shutil.copytree(template / "governance/baselines", governance / "baselines")
        shutil.copytree(template / "governance/rules", governance / "rules")
        policy = yaml.safe_load((governance / "policy.yaml").read_text(encoding="utf-8"))
        policy["architecture"]["root_package"] = package
        policy["providers"] = []
        (governance / "policy.yaml").write_text(
            yaml.safe_dump(policy, sort_keys=False), encoding="utf-8"
        )
        for directory in ("src", "tests", "features"):
            (root / directory).mkdir()
        return root

    return create
