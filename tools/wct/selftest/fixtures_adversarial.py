"""Fixtures adversariales del red team y de mutación."""

from __future__ import annotations

from pathlib import Path

from tools.wct.selftest.fixtures_git import _git_base, _git_track
from tools.wct.selftest.fixtures_governance import (
    MUTMUT_PYPROJECT,
    Builder,
    _arch_tree,
    _aws_secret_value,
    _plant,
    _private_key_block,
    mutmut_pyproject,
)

_ORM_TYPES_REGEX = (
    "(?i).*(Row|RowProxy|ResultProxy|Session|Query|Model|"
    "Response|Request|Cursor|Connection|DataFrame).*"
)

_CREDENTIAL_NAME_REGEX = (
    "(?i).*(password|passwd|secret|token|api_key|apikey|private_key|access_key|client_secret).*"
)

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

DEPS_PYPROJECT = (
    '[project]\nname = "victim"\nversion = "0.0.0"\nrequires-python = ">=3.11"\ndependencies = []\n'
)

SECRET_PATHS = {
    "src/example/__init__.py": "",
    "tools/wct/__init__.py": "",
    "pyproject.toml": "[project]\nname = 'victim'\n",
    ".pre-commit-config.yaml": "repos: []\n",
}


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
    El fixture es su propia raíz Git (addenda de frontera): bajo el techo
    del temporal, Semgrep descubre el proyecto propio y escanea la fuente
    plantada en vez de salir con cero targets por el ignore de un ancestro.
    Declara la gobernanza que el alcance exigible de G-SAST-SEMGREP lee.
    """
    root = _plant(
        tmp_path,
        {
            "governance/policy.yaml": "schema_version: 1\npaths:\n  source: [src]\n",
            "governance/thresholds.yaml": "schema_version: 1\n",
            "governance/semgrep/wct-architecture.yaml": SEMGREP_RULES,
            "src/victim/domain/io.py": 'import subprocess\n\nsubprocess.run(["ls"])\n',
        },
    )
    return _git_track(root)


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


def f2_a(tmp_path: Path) -> Path:
    """F2-a: producción real y NINGÚN test — nada ejercita los mutantes.

    Con un árbol sin tests, pytest colecciona nada (exit 5) y mutmut aborta
    en la colecta de stats con exit 1 ANTES de emitir un solo veredicto: el
    gate productivo se niega a aprobar producción sin tests. Medido contra
    mutmut 3.7.0 sin pipes (matriz del paso 0.1 de PR-E): todos-cazados →
    exit 0; sobrevivientes → exit 0 (hallazgo, bloquea F2-b/F5-b); sin
    tests → exit 1.
    """
    return _plant(
        tmp_path,
        {
            "pyproject.toml": MUTMUT_PYPROJECT,
            "src/victim/__init__.py": "",
            "src/victim/calc.py": (
                "def add(a, b):\n    return a + b\n\n\ndef mul(a, b):\n    return a * b\n"
            ),
        },
    )


def _mutation_adversary(*, module: str, code: str, test_path: str, test_code: str) -> Builder:
    """Builder de fixture de mutación: pyproject + un módulo + su test (receta 0.2).

    Fábrica en vez de builders gemelos: dos funciones ``_plant(tmp_path,
    {...})`` con cuatro entradas son el clon de plantilla exacto que
    G-DRY-TPL rastrea, y sus pares legados ya consumen la baseline (17)
    que solo puede bajar. Los imports del test son totalmente calificados
    y el pyproject del fixture declara su ``[tool.mutmut]`` con la
    selección — la convención medida en el paso 0.2 de PR-E.
    """

    def plant(tmp_path: Path) -> Path:
        return _plant(
            tmp_path,
            {
                "pyproject.toml": mutmut_pyproject(test_path),
                "src/victim/__init__.py": "",
                f"src/victim/{module}.py": code,
                test_path: test_code,
            },
        )

    return plant


F2_BILLING_ADVERSARY = _mutation_adversary(
    module="billing",
    code="def total(items):\n    return sum(items) * 1.0\n",
    test_path="tests/test_billing.py",
    test_code="from victim.billing import total\n\n"
    "def test_total_empty():\n    assert total([]) == 0\n",
)

F5_CLAMP_ADVERSARY = _mutation_adversary(
    module="clamp",
    code=(
        "def clamp(value, low, high):\n"
        "    if value < low:\n        return low\n"
        "    if value > high:\n        return high\n"
        "    return value\n"
    ),
    test_path="tests/test_clamp.py",
    test_code="from victim.clamp import clamp\n\n"
    "def test_middle_passes_through():\n    assert clamp(5, 0, 10) == 5\n",
)


def f4_b(tmp_path: Path) -> Path:
    """F4-b: producción nueva sin un solo test — el diff corre con 0%.

    Adversario (ADR-F-01): ``src/victim/ops.py`` recién escrito y UNTRACKED
    — producción nueva, cero tests — y ``build/coverage/lcov.info``
    sembrado con ``DA:n,0`` (cero ejecuciones), el artefacto que
    G-COV-TOTAL produciría si la suite no ejercita el archivo. Receta
    medida por la sonda del paso 0 (build/tmp/probe_f4b.py, variante A):
    el gate productivo corre diff-cover --include-untracked contra
    ``main`` y reprueba con ``Coverage: 0%``.
    """
    return _plant(
        _git_base(tmp_path),
        {
            "src/victim/ops.py": "def add(a, b):\n    return a + b\n",
            "build/coverage/lcov.info": (
                "TN:\nSF:src/victim/ops.py\nDA:1,0\nDA:2,0\nend_of_record\n"
            ),
        },
    )
