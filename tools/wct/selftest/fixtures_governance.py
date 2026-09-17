"""Fixtures de gobernanza plantada: pyproject, vulture, arch y secretos."""

from __future__ import annotations

from collections.abc import Callable
import hashlib
from pathlib import Path

Builder = Callable[[Path], Path]

MUTMUT_PYPROJECT = (
    '[project]\nname = "victim"\nversion = "0.0.0"\n\n[tool.mutmut]\nsource_paths = ["src"]\n'
)

VULTURE_MIN_CONFIDENCE = 60

IMPORT_LINTER = """\
[importlinter]
root_package = example

[importlinter:contract:domain-independence]
name = Domain has no project dependencies
type = forbidden
source_modules = example.domain
forbidden_modules =
    example.application
    example.adapters
    example.entrypoints

[importlinter:contract:application-independence]
name = Application does not depend on outer layers
type = forbidden
source_modules = example.application
forbidden_modules =
    example.adapters
    example.entrypoints

[importlinter:contract:adapter-independence]
name = Adapters do not depend on entrypoints
type = forbidden
source_modules = example.adapters
forbidden_modules = example.entrypoints

[importlinter:contract:layer-independence]
name = Architectural layers are acyclic siblings
type = acyclic_siblings
ancestors = example
"""


def mutmut_pyproject(selection: str) -> str:
    """Pyproject del fixture de mutación con selección de tests (receta 0.2)."""
    return f'{MUTMUT_PYPROJECT[:-1]}\npytest_add_cli_args_test_selection = ["{selection}"]\n'


def _plant(root: Path, files: dict[str, str]) -> Path:
    """Escribe ``files`` (ruta relativa → contenido) bajo ``root`` y retorna root."""
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return root


def _vulture_governance(extra: dict[str, str]) -> dict[str, str]:
    """Gobernanza mínima que ``dead_code_command`` lee, con el valor productivo."""
    replica = {
        "governance/policy.yaml": "schema_version: 1\n",
        "governance/thresholds.yaml": (
            f"schema_version: 1\ndead_code:\n  vulture_min_confidence: {VULTURE_MIN_CONFIDENCE}\n"
        ),
        "tools/wct/__init__.py": "",
    }
    return {**replica, **extra}


def _arch_tree(extra: dict[str, str]) -> dict[str, str]:
    """Árbol de capas mínimo con el ``.importlinter`` productivo replicado."""
    tree = {
        ".importlinter": IMPORT_LINTER,
        "example/__init__.py": "",
        "example/domain/__init__.py": "",
        "example/adapters/__init__.py": "",
        "example/adapters/db.py": "CONNECTED = True\n",
        "example/application/__init__.py": "",
        "example/entrypoints/__init__.py": "",
    }
    return {**tree, **extra}


def _aws_secret_value() -> str:
    """Valor de 40 caracteres con forma de clave AWS, sin literal contiguo aquí."""
    return hashlib.sha256(b"wct-redteam-f12a").hexdigest()[:40]


def _private_key_block() -> str:
    """Bloque PEM ensamblado por partes (un literal dispararía G-SECRET aquí)."""
    header = "-----BEGIN " + "PRIVATE KEY" + "-----"
    footer = "-----END " + "PRIVATE KEY" + "-----"
    return f"{header}\nMIIBCgKCAQEA relleno del adversario\n{footer}\n"


def f1_b(tmp_path: Path) -> Path:
    """F1-b: import estándar muerto, residuo de un helper generado.

    Adversario re-declarado por adjudicación del arquitecto: una FUNCIÓN
    muerta es confianza 60 en vulture; un import sin uso es confianza 90 y
    queda cazado con margen sobre cualquier umbral declarado.
    """
    return _plant(
        tmp_path,
        _vulture_governance(
            {
                "src/example/__init__.py": "",
                "src/example/generated.py": "import json\n",
            }
        ),
    )
