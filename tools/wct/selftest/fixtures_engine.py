"""Fixtures del arnés gate-engine: cada builder planta UN defecto en un tmpdir.

ADR-C-01 §2: un caso, un tmpdir. El builder recibe el directorio privado del
caso y retorna la raíz del fixture que el motor productivo va a analizar. La
configuración governance/ replicada aquí es la mínima que cada motor consume
vía ``load_config`` (verificado en el paso 0 de SPEC-C-01).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

Builder = Callable[[Path], Path]

PACKAGE = "example"
LAYERS = ("entrypoints", "adapters", "application", "domain")

POLICY = """\
schema_version: 1
paths:
  source: [src]
  tests: [tests]
architecture:
  root_package: example
  layers: [entrypoints, adapters, application, domain]
  forbidden_external: {}
"""
THRESHOLDS_DRY = """\
schema_version: 1
dry:
  threshold: 0.82
  min_lines: 3
  min_nodes: 10
  review_threshold: 0.95
  extraction:
    min_shared_forms: 3
    max_variable_points: 4
    helper_cost: 1.0
    min_pressure: 0.5
"""
THRESHOLDS_MUTATION = """\
schema_version: 1
mutation:
  max_sites_per_file: 100
"""
THRESHOLDS_ARCHITECTURE = """\
schema_version: 1
architecture:
  healthy_threshold: 0.3
  cycle_allowlist: []
"""
THRESHOLDS_MINIMAL = "schema_version: 1\n"

DUPLICATED = """\
def pack_light(first: int, second: int) -> int:
    total = first + second
    scaled = total * 2
    return scaled


def pack_heavy(third: int, fourth: int) -> int:
    combined = third + fourth
    doubled = combined * 2
    return doubled
"""
PURE_ASSERTION = "def test_arithmetic() -> None:\n    assert 2 + 2 == 4\n"
MOCK_ONLY = (
    "from example.gateways import client\n"
    "\n"
    "\n"
    "def test_save_delegates() -> None:\n"
    "    client.save.assert_called_once()\n"
)


def _governance(root: Path, thresholds: str) -> Path:
    """Escribe la policy y thresholds mínimos que ``load_config`` exige."""
    directory = root / "governance"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "policy.yaml").write_text(POLICY, encoding="utf-8")
    (directory / "thresholds.yaml").write_text(thresholds, encoding="utf-8")
    return root


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _layer_tree(root: Path) -> None:
    """Réplica mínima del layout de capas que archmetrics recorre."""
    for layer in LAYERS:
        _write(root, f"src/{PACKAGE}/{layer}/__init__.py", "")
    _write(root, f"src/{PACKAGE}/__init__.py", "")


def _suppression_fixture(tmp_path: Path, suppressed_line: str) -> Path:
    root = _governance(tmp_path, THRESHOLDS_MINIMAL)
    _write(root, "src/module.py", suppressed_line)
    return root


def _oversized_source(functions: int) -> str:
    """``(value + i) * i`` aporta 4 sitios por función: 30 funciones = 120 > 100."""
    return "".join(
        f"def step_{index}(value: int) -> int:\n    return (value + {index}) * {index}\n\n"
        for index in range(functions)
    )


def _duplicate_pair(tmp_path: Path) -> Path:
    """F1-a: dos funciones estructuralmente idénticas para dry.analyzer."""
    root = _governance(tmp_path, THRESHOLDS_DRY)
    _write(root, "src/warehouse.py", DUPLICATED)
    return root


def _pure_assertion_test(tmp_path: Path) -> Path:
    """F3-a: test que aserta constantes sin trazar al SUT."""
    root = _governance(tmp_path, THRESHOLDS_MINIMAL)
    _write(root, "tests/test_arithmetic.py", PURE_ASSERTION)
    return root


def _mock_only_test(tmp_path: Path) -> Path:
    """F3-b: test mock-only; verifica la llamada, no el resultado del SUT."""
    root = _governance(tmp_path, THRESHOLDS_MINIMAL)
    _write(root, "tests/test_save.py", MOCK_ONLY)
    return root


def _unjustified_pragma(tmp_path: Path) -> Path:
    """F4-a: supresión de cobertura sin regla ni justificación."""
    return _suppression_fixture(tmp_path, "value = compute()  # pragma: no cover\n")


def _oversized_mutation_file(tmp_path: Path) -> Path:
    """F5-a: archivo generado programáticamente con >100 sitios de mutación."""
    root = _governance(tmp_path, THRESHOLDS_MUTATION)
    _write(root, "src/generated_batch.py", _oversized_source(30))
    return root


def _upward_import_tree(tmp_path: Path) -> Path:
    """F6-b: application importa desde entrypoints (Dependency Rule hacia arriba)."""
    root = _governance(tmp_path, THRESHOLDS_ARCHITECTURE)
    _layer_tree(root)
    _write(root, f"src/{PACKAGE}/entrypoints/cli.py", "def main() -> int:\n    return 0\n")
    _write(
        root,
        f"src/{PACKAGE}/application/services.py",
        f"from {PACKAGE}.entrypoints.cli import main\n\n\ndef run() -> int:\n    return main()\n",
    )
    return root


def _two_module_cycle(tmp_path: Path) -> Path:
    """F7-a: ciclo de imports entre 2 módulos hermanos."""
    root = _governance(tmp_path, THRESHOLDS_ARCHITECTURE)
    _layer_tree(root)
    _write(root, f"src/{PACKAGE}/domain/alpha.py", f"import {PACKAGE}.domain.beta\n")
    _write(root, f"src/{PACKAGE}/domain/beta.py", f"import {PACKAGE}.domain.alpha\n")
    return root


def _three_module_cycle(tmp_path: Path) -> Path:
    """F7-b: ciclo de imports entre 3 módulos hermanos."""
    root = _governance(tmp_path, THRESHOLDS_ARCHITECTURE)
    _layer_tree(root)
    _write(root, f"src/{PACKAGE}/domain/alpha.py", f"import {PACKAGE}.domain.beta\n")
    _write(root, f"src/{PACKAGE}/domain/beta.py", f"import {PACKAGE}.domain.gamma\n")
    _write(root, f"src/{PACKAGE}/domain/gamma.py", f"import {PACKAGE}.domain.alpha\n")
    return root


def _unjustified_noqa(tmp_path: Path) -> Path:
    """F13-a: noqa sin código de regla ni justificación."""
    return _suppression_fixture(tmp_path, "value = compute()  # noqa\n")


def _unjustified_type_ignore(tmp_path: Path) -> Path:
    """F13-b: type: ignore sin código de regla ni justificación."""
    return _suppression_fixture(tmp_path, "value = compute()  # type: ignore\n")


BUILDERS: dict[str, Builder] = {
    "F1-a": _duplicate_pair,
    "F3-a": _pure_assertion_test,
    "F3-b": _mock_only_test,
    "F4-a": _unjustified_pragma,
    "F5-a": _oversized_mutation_file,
    "F6-b": _upward_import_tree,
    "F7-a": _two_module_cycle,
    "F7-b": _three_module_cycle,
    "F13-a": _unjustified_noqa,
    "F13-b": _unjustified_type_ignore,
}
