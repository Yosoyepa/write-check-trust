# ADR-A2-01 — Mecanismo de aplicación del baseline: fail-under en el gate + medición por artefacto

Estado: propuesto (se ejecuta al aprobarse GHERKIN-A2.md).
Contexto: [ANALYSIS.md §2](../ANALYSIS.md) · prior art en
[PR-A1 RESEARCH R2](../PR-A1/RESEARCH.md) (dogfooding de cobertura).

## Contexto

El baseline existe, declara "cobertura de rama del repo completo", y no lo
consume nadie. Dos problemas independientes: **aplicar el piso** (que un
total bajo el baseline bloquee) y **medir para el ratchet** (que
`measurements()`/`record`/`check` vean la métrica). G-DEBT está en el tier
fast y llama al motor de ratchets: la medición no puede costar segundos.

## Decisión

1. **Aplicación**: G-COV-TOTAL deja de ser `external()` estático y pasa a
   función dinámica (patrón `gate_coverage_diff`): lee
   `governance/baselines/coverage-total.json` y construye el comando pytest
   añadiendo `--cov-fail-under=<value>`. El piso se aplica sobre la corrida
   fresca del gate — sin números cacheados en la ruta de bloqueo.
2. **Medición para el ratchet**: `measurements()` gana `coverage-total`
   parseando `build/coverage/lcov.info` (LF/LH/BRF/BRH) **si existe**; si no,
   `None` y `check()` la salta (patrón `docstring-coverage`). Sin subprocess:
   el tier fast no se encarece.
3. **Registro autoritativo**: `ratchet record --metric coverage-total` corre
   la suite una vez y lee `percent_covered` **del reporte JSON** de
   coverage.py — el mismo valor preciso que `--cov-fail-under` compara
   internamente — truncado a 2 decimales hacia abajo: gate y ratchet no
   pueden discrepar por construcción, y el piso nunca supera la medición.
   *(Corrección 2026-09-02: la versión original leía la línea TOTAL del
   reporte term, cuyo display redondea a entero — el primer registro real
   midió 74.51 preciso como "75" y fijó un piso inalcanzable. Hallazgo del
   propio flujo de A2 durante el re-baseline.)*
4. **`--metric` opcional en record** (default: todos, comportamiento
   actual): permite re-baselinear UNA métrica sin re-estampar las otras 9.

## Alternativas consideradas

- **(a) Medición que corre pytest en `measurements()`**: rechazada — G-DEBT
  (fast tier) llama measurements(); añadir segundos a cada gate rápido rompe
  el propósito del anillo rápido. El interrogate de docstrings ya es el límite
  aceptable de costo en esa ruta.
- **(b) Solo fail-under, sin métrica en el ratchet**: rechazada — el baseline
  quedaría aplicado pero inauditable: `ratchet check` seguiría sin conocer la
  métrica y `record` no podría subirla nunca. Piso sin escalera.
- **(c) Parse lcov también para record**: rechazada — ahorra un run de pytest
  en un comando raro y humano, a cambio de abrir la puerta a la discrepancia
  de redondeo entre parse y total oficial. El registro debe ser autoritativo.
- **(d) Umbral fijo en thresholds.yaml en vez del baseline**: rechazada —
  duplicaría la fuente de verdad; el baseline versionado con commit/owner ES
  el ratchet del repo; añadirle un gemelo en otro YAML crea el mismo defecto
  de config-huérfana que PR-B está cazando.

## Consecuencias

- El 100 % decorativo muere: a partir de A2, bajar la cobertura total bajo el
  baseline bloquea el commit.
- El tier fast no cambia de costo (parse de un archivo pequeño).
- G-COV-TOTAL gana lógica (lectura de baseline + construcción dinámica):
  cubierta por tests TDD de comando y de fail-red; CRAP bajo por diseño
  (función pequeña).
- `pyproject.toml` y `tools/wct/**` son rutas protegidas → bless único del PR
  (secuencia completa en VERIFICATION.md).
