# ANALYSIS — PR-A2: evidencia y datos de diseño

## 1. Evidencia (re-verificada en `b7eda55`)

- `[tool.coverage.run] source = ["src/example"]` (pyproject.toml:60-63): 61
  statements medidos de 2 509 reales del harness (`tools/wct` = 4 077 LOC).
- `governance/baselines/coverage-total.json`: `value: 100.0`,
  `recorded_by: "seed"`, `commit: null` — sembrado, nunca medido.
- `grep coverage-total tools/wct/` → 0 consumidores. G-COV-TOTAL
  (runner.py:387-397) corre pytest sin `--cov-fail-under`: su verde es "los
  tests pasaron", no "la cobertura está sobre el piso".
- `ratchet/measure.py::measurements()` (líneas 45-64): 9 métricas,
  coverage-total ausente. `check()` compara solo lo que measurements() produce.
- El CLI expone `wct ratchet {check,record}` **sin** selección por métrica:
  un record hoy re-escribiría TODOS los baselines (riesgo de re-stamp
  masivo — ver §3).

## 2. Datos de diseño (decisivos, medidos esta sesión)

| Dato | Valor | Implicación |
|---|---|---|
| G-DEBT (tier **fast**) usa `ratchet.engine` | checks.py:22-77 | `measurements()` vive en el camino rápido: la medición nueva **no puede** lanzar pytest (subprocess de segundos en cada gate fast) |
| Precedente de métrica opcional | `docstring-coverage` → `None` si interrogate falta, y `check()` la salta | La abstención declarada cuando falta el artefacto tiene patrón establecido |
| G-COV-TOTAL produce `build/coverage/lcov.info` en cada corrida | runner.py:394 | El artefacto ya existe: la medición puede parsearlo sin subprocess |
| pytest-cov soporta `--cov-fail-under` | behavior documentado de coverage.py | La aplicación del piso es un flag del comando, no lógica nueva |
| Mutación diferencial con selección de tests fija en pyproject | `[tool.mutmut]` | Extender mutación al harness = rediseño de selección (fuera de A2) |

## 3. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| **Discrepancia gate↔ratchet**: `--cov-fail-under` usa el total de coverage.py; una medición lcov-parseada podría calcular distinto | Test de acuerdo: fixture donde ambas fuentes se comparan (SPEC §T6); `record` usa SIEMPRE el TOTAL de `--cov-report=term` (autoritativo por construcción), el parse lcov solo para check() |
| **Record masivo**: `ratchet record` sin filtro re-estampa los 9 baselines | A2 añade `--metric` (default: comportamiento actual preservado); la secuencia humana usa `--metric coverage-total` |
| **Árbol rojo por scope**: aplicar fail-under 100 con total real 73 | Secuencia ADR-A2-02: record del 73 ANTES del merge; el gate lee el baseline re-registrado |
| **Artefacto stale en check()**: lcov viejo produce número viejo | La medición se abstiene si el artefacto no existe (patrón docstrings); el gate SIEMPRE corre pytest fresco — el piso se aplica sobre medición fresca siempre |
| **Runtime del gate**: `--cov-fail-under` no añade tiempo (mismo run) | N/A |
| **Adoptantes**: el scope del template es el del template | Documentado en el spec: un adoptante ajusta `source` a su repo; el mecanismo (fail-under desde baseline) es lo que se hereda |

## 4. Predicciones falsables de A2

- Tras el cambio, `G-COV-TOTAL` en el repo mide TOTAL = 73 % (2509 stmts,
  598 miss — bajo `-m "not property"`; ±2 stmts por código nuevo de A2).
- Con baseline 73: verde. Con baseline simulado 74 en un fixture: rojo
  (test del gate).
- `wct ratchet check` reporta `coverage-total: actual=73, baseline=73` PASS.
- El tier fast no cambia de duración apreciable (medición por artefacto,
  sin subprocess nuevo).
- Red team y accept parse: sin cambios (no se tocan superficies suyas).
