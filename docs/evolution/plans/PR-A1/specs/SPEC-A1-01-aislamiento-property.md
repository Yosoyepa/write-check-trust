# SPEC-A1-01 — Aislamiento de property tests

ADR: [ADR-A1-01](../decisions/ADR-A1-01-aislamiento-property.md) ·
Escenarios: `wct-prop-isolation` en [GHERKIN-A1.md](../GHERKIN-A1.md).

## Paso 0 — Censo (sin código)

- Listar módulos bajo `tests/property/` y sus tests `@given` (hoy: 1 archivo,
  1 test; re-verificar).
- Confirmar con `grep -rn "pytest.mark.property" tests/` que no hay usos
  parciales que el cambio de módulo pudiera duplicar.

## Cambios

### 1. `tests/property/test_inventory_properties.py` (y todo módulo property)

Añadir a nivel de módulo (debajo de los imports):

```python
pytestmark = pytest.mark.property
```

Requisito: `import pytest` si no está. NO decorar test a test (ADR-A1-01 §1).

### 2. `tools/wct/gate/runner.py`

- G-COV-TOTAL (líneas ~387-395): la lista de argumentos de pytest añade
  `"-m", "not property"`.
- G-TEST (línea 328): misma adición en su lista de argumentos.
- G-PROP (línea 400): **sin cambios**.

### 3. `pyproject.toml`

- En `pytest_add_cli_args_test_selection` (líneas 82-88): retirar la entrada
  `"tests/property/test_inventory_properties.py"`. Sin otros cambios en el
  archivo.

## Tests TDD (escribir ANTES de cada implementación; deben fallar en rojo primero)

En `tests/unit/` (nombres propuestos; ajustar al estilo local):

1. `tests/unit/test_gate_commands.py::test_gcov_total_excludes_property_tests`
   — la invocación construida de G-COV-TOTAL contiene `["-m", "not property"]`.
   (Localizar cómo se testean hoy los comandos de gates externos; si existe
   helper de construcción de comando, asertir sobre él.)
2. `...::test_gtest_excludes_property_tests` — ídem para G-TEST.
3. `...::test_gprop_runs_property_without_filter` — la invocación de G-PROP
   NO contiene `-m` (el gate dedicado no filtra).
4. `tests/unit/test_property_isolation.py::test_property_modules_carry_marker`
   — para cada módulo en `tests/property/`: `module.pytestmark` contiene
   `pytest.mark.property` (import dinámico; si el costo de import es alto,
   asertir sobre el AST/fuente que existe `pytestmark` con el marker —
   elegir la forma que la suite ya use para contract-tests de fuente).
5. `tests/unit/test_mutation_selection.py::test_mutation_selection_excludes_property`
   — leer `pytest_add_cli_args_test_selection` (tomlllib sobre pyproject) y
   asertir que ninguna entrada está bajo `tests/property/`.

## No hacer

- No tocar `addopts`, `testpaths`, `markers`, `[tool.coverage]`,
  `[tool.mutmut].source_paths` (scope de mutación = PR-A2/out).
- No añadir infrastructure nueva de markers dinámicos.
- No excluir property de G-PROP.

## Commit

`fix(gate): aislamiento contractual de property tests (TEST-008)`
