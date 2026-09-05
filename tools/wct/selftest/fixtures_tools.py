"""Fixtures adversariales de los casos gate-tool del red team (PR-C, ADR-C-01 §2).

Cada builder planta el defecto de su caso en un árbol mínimo que replica la
estructura que la función de gate productiva REALMENTE lee. Contratos
verificados en el paso 0.3 contra ``tools/wct/gate/runner.py`` y
``checks.py`` (no adivinados; cada uno fue corrido con las herramientas del
grupo quality antes de escribir este archivo):

- G-DEAD (``dynamic`` → vulture): exige ``governance/policy.yaml`` y
  ``governance/thresholds.yaml`` (ambos con ``schema_version: 1``) con la
  clave ``dead_code.vulture_min_confidence`` — aquí se replica el valor
  productivo (80) — y los caminos ``src/`` y ``tools/wct/`` del comando.
- G-ARCH (``external`` → ``lint-imports``): lee ``.importlinter`` del root
  (réplica verbatim del productivo) y resuelve ``root_package = example``
  porque import-linter inserta el cwd en ``sys.path[0]``: el árbol vive en
  ``<root>/example/`` y sombra al paquete editable del venv.
- G-SAST-SEMGREP (``external`` → semgrep): lee ``governance/semgrep`` del
  root (réplica verbatim de sus reglas) y escanea el cwd. semgrep limita el
  escaneo a archivos trackeados por git, así que el fixture debe vivir
  FUERA de cualquier repo git (``tmp_path`` de pytest lo garantiza).
- G-DEPS (``external`` → deptry): exige ``pyproject.toml`` en el root y los
  caminos ``src/`` y ``tools/`` del comando.
- G-SECRET (``gate_secrets`` → detect-secrets): pasa una lista fija de
  caminos; los directorios se enumeran vía ``git ls-files``, así que el
  fixture lleva su propio ``git init`` + ``git add``.

Los valores con forma de credencial se ensamblan en runtime (nunca como
literal contiguo en este archivo) para que G-SECRET del propio repositorio
no falle sobre su herramienta de calificación.
"""

from __future__ import annotations

from collections.abc import Callable
import hashlib
from pathlib import Path
import subprocess

Builder = Callable[[Path], Path]

# Réplica del valor productivo de governance/thresholds.yaml. Es parte del
# instrumento que se califica: cambiarlo aquí maquillaría el hallazgo F1-b.
VULTURE_MIN_CONFIDENCE = 80

# Réplica verbatim del .importlinter productivo (contratos de capas; sin
# contratos forbidden_external ni include_external_packages — verificado en
# el paso 0.3: ningún código genera .importlinter desde policy.yaml).
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

# Las dos regex largas del ruleset se ensamblan por partes para que ninguna
# línea de este archivo pase E501; el YAML que se planta es byte-idéntico al
# productivo (verificado por tests de igualdad contra governance/semgrep).
_ORM_TYPES_REGEX = (
    "(?i).*(Row|RowProxy|ResultProxy|Session|Query|Model|"
    "Response|Request|Cursor|Connection|DataFrame).*"
)
_CREDENTIAL_NAME_REGEX = (
    "(?i).*(password|passwd|secret|token|api_key|apikey|private_key|access_key|client_secret).*"
)

# Réplica verbatim de governance/semgrep/wct-architecture.yaml (ruleset que
# G-SAST-SEMGREP pasa con --config governance/semgrep).
SEMGREP_RULES = """\
# governance/semgrep/wct-architecture.yaml
#
# Reglas semgrep propias del harness. Cubren lo que import-linter NO puede ver:
# import-linter razona sobre el GRAFO de imports; estas reglas razonan sobre el
# USO de tipos y valores dentro del archivo.
#
# Ejecutadas por G-SAST-SEMGREP. Requieren `semgrep` instalado (opcional: si
# falta, el gate reporta SKIPPED y aparece como no cubierto en `wct report`).

rules:
  # ARCH-004 — filtración de tipos de infraestructura por los límites.
  # import-linter no lo atrapa cuando el tipo entra por un `TYPE_CHECKING` o
  # cuando se retorna un objeto sin anotarlo.
  - id: wct-orm-row-leaked-from-application
    languages: [python]
    severity: ERROR
    message: >
      ARCH-004: este módulo de `application/` retorna o expone un objeto de
      ORM/framework. Convierte a un tipo del dominio antes de cruzar el límite.
    paths:
      include:
        - "src/*/application/**"
    patterns:
      - pattern-either:
          - pattern: |
              def $F(...) -> $T: ...
          - pattern: |
              async def $F(...) -> $T: ...
      - metavariable-regex:
          metavariable: $T
          regex: '__ORM_TYPES_REGEX__'

  # ARCH-002 reforzado: import dinámico que esquiva el análisis estático.
  - id: wct-dynamic-import-in-core
    languages: [python]
    severity: ERROR
    message: >
      ARCH-002: import dinámico en el core. `importlib.import_module` y
      `__import__` son invisibles para import-linter, así que aquí equivalen a
      esquivar el gate de arquitectura.
    paths:
      include:
        - "src/*/domain/**"
        - "src/*/application/**"
    pattern-either:
      - pattern: importlib.import_module(...)
      - pattern: __import__(...)

  # ARCH-002 — IO directo desde el core.
  - id: wct-io-in-domain
    languages: [python]
    severity: ERROR
    message: >
      ARCH-002: IO directo en `domain/`. El dominio no lee archivos, no abre
      sockets y no toca el reloj del sistema: recibe esos valores como
      argumentos, lo que además lo hace testeable sin mocks.
    paths:
      include:
        - "src/*/domain/**"
    pattern-either:
      - pattern: open(...)
      - pattern: pathlib.Path(...).read_text(...)
      - pattern: pathlib.Path(...).write_text(...)
      - pattern: os.environ
      - pattern: os.getenv(...)
      - pattern: socket.$ANY(...)
      - pattern: subprocess.$ANY(...)

  # SEC-001 refuerzo: secreto con forma de placeholder realista. detect-secrets
  # usa entropía y falla con constantes de forma reconocible.
  - id: wct-hardcoded-credential-shape
    languages: [python]
    severity: ERROR
    message: >
      SEC-001: credencial embebida en el código. Léela de una variable de
      entorno en la capa de entrypoints, incluso si este valor es de ejemplo:
      un secreto committeado queda en el historial para siempre.
    patterns:
      - pattern: $VAR = "..."
      - metavariable-regex:
          metavariable: $VAR
          regex: '__CREDENTIAL_NAME_REGEX__'

  # TEST-003 — el caso Python del test introvertido. Es un pre-filtro rápido;
  # el análisis real lo hace `wct introvert` (G-INTROVERT).
  - id: wct-mock-only-assertion
    languages: [python]
    severity: WARNING
    message: >
      TEST-003: este test asevera únicamente sobre el mock. Añade una aserción
      sobre el valor que retorna el SUT, o el test verifica su propio
      andamiaje. Confirma con `wct introvert`.
    paths:
      include:
        - "tests/**"
    patterns:
      - pattern-either:
          - pattern: $M.assert_called_once(...)
          - pattern: $M.assert_called_once_with(...)
          - pattern: $M.assert_called_with(...)
          - pattern: $M.assert_awaited_once(...)
          - pattern: $M.assert_awaited_once_with(...)
""".replace("__ORM_TYPES_REGEX__", _ORM_TYPES_REGEX).replace(
    "__CREDENTIAL_NAME_REGEX__", _CREDENTIAL_NAME_REGEX
)

# pyproject mínimo que deptry exige en el root del fixture (G-DEPS).
DEPS_PYPROJECT = (
    '[project]\nname = "victim"\nversion = "0.0.0"\nrequires-python = ">=3.11"\ndependencies = []\n'
)

# Camino base que gate_secrets pasa a detect-secrets (todos deben existir).
SECRET_PATHS = {
    "src/example/__init__.py": "",
    "tools/wct/__init__.py": "",
    "pyproject.toml": "[project]\nname = 'victim'\n",
    ".pre-commit-config.yaml": "repos: []\n",
}


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


def _git_track(root: Path) -> Path:
    """Trackea el fixture: detect-secrets enumera directorios vía ``git ls-files``."""
    for command in (("git", "init", "-q"), ("git", "add", "-A")):
        subprocess.run(command, cwd=root, check=True, capture_output=True)
    return root


def f1_b(tmp_path: Path) -> Path:
    """F1-b: import estándar muerto, residuo de un helper generado.

    Adversario re-declarado por adjudicación del arquitecto: una FUNCIÓN
    muerta es confianza 60 en vulture y el umbral productivo (80) la deja
    pasar; un import sin uso es confianza 90 y sí es cazado.
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


def f6_a(tmp_path: Path) -> Path:
    """F6-a: domain importa adapters (Dependency Rule rota hacia afuera)."""
    return _plant(
        tmp_path,
        _arch_tree({"example/domain/leak.py": "from example.adapters import db\n"}),
    )


def f9_a(tmp_path: Path) -> Path:
    """F9-a: domain EJECUTA subprocess (IO directo en el core).

    Re-declarado por adjudicación: el catcher productivo es la regla
    semgrep ``wct-io-in-domain`` (patrón ``subprocess.$ANY(...)`` con
    include ``src/*/domain/**``) — import-linter no ve módulos externos.
    """
    return _plant(
        tmp_path,
        {
            "governance/semgrep/wct-architecture.yaml": SEMGREP_RULES,
            "src/victim/domain/io.py": 'import subprocess\n\nsubprocess.run(["ls"])\n',
        },
    )


def f10_a(tmp_path: Path) -> Path:
    """F10-a: import de un SDK que el pyproject del fixture no declara."""
    return _plant(
        tmp_path,
        {
            "pyproject.toml": DEPS_PYPROJECT,
            "src/example/__init__.py": "",
            "src/example/tenants.py": "import imaginary_sdk\n",
            "tools/__init__.py": "",
        },
    )


def f10_b(tmp_path: Path) -> Path:
    """F10-b: import disponible solo de forma transitiva, sin declaración."""
    return _plant(
        tmp_path,
        {
            "pyproject.toml": DEPS_PYPROJECT,
            "src/example/__init__.py": "",
            "src/example/tenants.py": "from transitive_only import api\n",
            "tools/__init__.py": "",
        },
    )


def f12_a(tmp_path: Path) -> Path:
    """F12-a: clave de acceso AWS comitteada en ``src``."""
    root = _plant(
        tmp_path,
        {
            **SECRET_PATHS,
            "src/example/settings.py": f'AWS_SECRET_ACCESS_KEY = "{_aws_secret_value()}"\n',
        },
    )
    return _git_track(root)


def f12_b(tmp_path: Path) -> Path:
    """F12-b: llave privada PEM comitteada en ``src``."""
    root = _plant(
        tmp_path,
        {
            **SECRET_PATHS,
            "src/example/identity.py": f'PEM = """{_private_key_block()}"""\n',
        },
    )
    return _git_track(root)


BUILDERS: dict[str, Builder] = {
    "F1-b": f1_b,
    "F6-a": f6_a,
    "F9-a": f9_a,
    "F10-a": f10_a,
    "F10-b": f10_b,
    "F11-a": f11_a,
    "F12-a": f12_a,
    "F12-b": f12_b,
}
