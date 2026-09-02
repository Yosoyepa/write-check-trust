# SPEC-A2-01 — Scope y baseline de cobertura

ADRs: [A2-01](../decisions/ADR-A2-01-mecanismo-de-aplicacion.md),
[A2-02](../decisions/ADR-A2-02-rebaseline-humano.md) · Escenarios:
[GHERKIN-A2.md](../GHERKIN-A2.md).

## Paso 0 — Investigación previa del coder (leer ANTES de codear)

1. Semántica exacta de `--cov-fail-under` con `--cov-branch` en coverage.py:
   confirmar que el total comparado es el de la línea TOTAL del reporte term
   (statements+branches). Documentar en el handoff con la salida de una
   corrida de prueba.
2. Estructura del lcov producido (LF/LH/BRF/BRH por archivo): escribir el
   parse y su fórmula de total; validar contra la línea TOTAL oficial del
   mismo run en este repo (deben coincidir; si difieren por redondeo,
   documentar y alinear la fórmula ANTES de seguir).
3. Semántica de `wct ratchet record` actual (engine.py): qué escribe, con qué
   campos, y si re-escribe todos los baselines (confirmar el riesgo del
   ANALYSIS §3).

## Cambios

### 1. `pyproject.toml` (protegido → bless del PR)

```toml
[tool.coverage.run]
source = ["src", "tools/wct"]   # era ["src/example"]
```

`omit` sin cambios.

### 2. `tools/wct/gate/runner.py` — G-COV-TOTAL dinámico

- Reemplazar la entrada estática por una función `gate_coverage_total(root)`
  (patrón de `gate_coverage_diff`): lee el baseline
  `governance/baselines/coverage-total.json` (usar el loader de config ya
  importado en checks.py; NO parsear YAML a mano en runner) y construye:

```python
command = [
    "pytest",
    "--cov",
    "--cov-branch",
    "--cov-report=lcov:build/coverage/lcov.info",
    "--cov-fail-under",
    str(baseline_value),
    "-q",
    "-m",
    "not property",
]
```

- Baseline ausente o ilegible: el gate **debe** declararlo y fallar (no
  silently sin piso — es exactamente el defecto que este PR corrige); el
  mensaje indica el archivo esperado.
- Mover la lógica a `gate/checks.py` si el house-style lo pide (gate_* viven
  ahí); runner.py solo registra. Elegir la sede consistente con
  `gate_coverage_diff`.

### 3. `tools/wct/ratchet/measure.py` — medición por artefacto

- `coverage_total(root) -> float | None`: parsea `build/coverage/lcov.info`;
  `None` si no existe (patrón `docstring-coverage`).
- `measurements()` añade `"coverage-total": ...` solo si no es None (clave
  presente solo con dato — igual que docstrings).

### 4. `tools/wct/ratchet/engine.py` (+ cli.py si hace falta) — `record --metric`

- `record(root, approved_by, reason, metric=None)`: con `metric`, escribe solo
  el baseline de esa métrica; sin `metric`, comportamiento actual.
- Para `coverage-total`, el valor sale de una corrida
  `pytest --cov --cov-branch --cov-report=term -q -m "not property"` parseando
  la línea TOTAL (autoritativo — ADR-A2-01 §3). El subproceso corre SOLO en
  record, jamás en measurements().
- CLI: `wct ratchet record [--metric NOMBRE] --approved-by ... --reason ...`
  (argparse, default None).
- Validación: metric desconocido → error listando las métricas válidas.

### 5. Docs factuales

- `docs/gates.md`: G-COV-TOTAL ahora cita `--cov-fail-under` desde baseline;
  G-PROP sin cambios.
- `docs/README.md`/runbook si describen el baseline de cobertura: actualizar
  la mención (semilla → real, con el comando de re-baseline).

## Tests TDD (rojo primero; nombres propuestos)

1. `tests/unit/test_gate_coverage_total.py::test_command_includes_fail_under_from_baseline`
   — con baseline fixture 85.0, la invocación contiene
   `["--cov-fail-under", "85.0"]` y `-m not property`.
2. `...::test_missing_baseline_fails_loudly` — sin archivo de baseline: FAIL
   con mensaje que nombra la ruta esperada (no SKIP, no PASS).
3. `...::test_gate_passes_at_floor` — con fake_run de exit 0 (patrono
   `test_gate_commands.py` de A1): PASS.
4. `tests/unit/test_ratchet_coverage.py::test_measurement_parses_lcov` —
   lcov fixture con LF/LH/BRF/BRH conocidos → valor exacto esperado.
5. `...::test_measurement_none_without_artifact` — sin lcov: measurements()
   no incluye la clave (o la omite como docstrings — consistente con §3).
6. `...::test_lcov_parse_agrees_with_term_total` — acuerdo parse↔TOTAL
   oficial (usa un lcov y un term reales del repo si pesa poco, si no un
   fixture con ambos outputs congelados).
7. `tests/unit/test_ratchet_record.py::test_record_single_metric_writes_only_that_baseline`
   — fixture con 2 baselines; `record(metric=...)` escribe uno y no toca el
   otro (compara contenido de archivos).
8. `...::test_record_unknown_metric_lists_valid_metrics` — error accionable.
9. `tests/unit/test_coverage_scope.py::test_coverage_source_includes_harness`
   — lee pyproject: `source` contiene `src` y `tools/wct` (tomllib, patrón
   `test_mutation_selection.py` de A1).

## No hacer

- No tocar `[tool.mutmut]` (scope de mutación = PR propio).
- No correr pytest dentro de `measurements()`.
- No editar el archivo de baseline a mano (la secuencia humana de ADR-A2-02
  lo registra con `ratchet record`).
- No "pintar" el 73: si la medición real difiere de lo predicho, se reporta
  y se usa el número medido.

## Commits

`feat(gate): G-COV-TOTAL aplica el baseline como piso` ·
`feat(ratchet): coverage-total medido del artefacto lcov` ·
`feat(ratchet): record por métrica` · `chore(coverage): el harness entra al scope`
(+ docs en el commit que corresponda).
