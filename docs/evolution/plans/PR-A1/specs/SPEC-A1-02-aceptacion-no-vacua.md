# SPEC-A1-02 — Veredicto no vacío en aceptación por mutación

ADR: [ADR-A1-02](../decisions/ADR-A1-02-aceptacion-no-vacua.md) ·
Escenarios: `wct-accept-nonvacuous` en [GHERKIN-A1.md](../GHERKIN-A1.md).

## Paso 0 — Censo de vacuidad del corpus actual (obligatorio, antes de codear)

1. `uv run wct accept parse` — confirmar que todo parsea.
2. Para cada feature en `features/`: listar escenarios con conteo de Examples
   (script desechable en `build/tmp/` con pytest-bdd/gherkin parser o lectura
   del IR de `accept/pipeline.py` — NO editar el manifiesto a mano, TEST-009:
   solo lectura).
3. Emitir la tabla escenario × examples en el handoff.
4. **Si hay escenarios sin Examples**: parametrizarlos en el mismo PR según
   TEST-010 (features/ es ruta libre). Si alguno no puede parametrizarse sin
   rediseño, NO endulzar el veredicto: escalar en el handoff con la propuesta.

## Cambios

### 1. `tools/wct/cli.py` (veredicto, ~líneas 311-313)

```python
# antes
return bool(report["survived"])
# después (ajustar a la estructura real de report que exponga el conteo)
if not report["results"]:
    print(
        "wct: 0 mutaciones ejecutadas: el escenario no parametriza "
        "campos variables; agrega Examples (TEST-010)"
    )
    return True  # fallo
return bool(report["survived"])
```

- El coder inspecciona `run_mutations` y usa la clave real (`results`,
  `killed`+`survived`, u otra): el TEST debe asertir la semántica (0
  ejecutadas → fallo), no el nombre de la clave.
- El mensaje sale por stderr o stdout según la convención de errores del CLI.

### 2. Reporte de vacuidad por escenario (WARN)

- En la ruta que imprime el reporte de aceptación (localizar dónde se
  resume; si no existe sección de warnings, añadirla mínima junto al resumen
  existente): listar escenarios sin `examples` como
  `WARN: escenario "<nombre>" sin Examples — vacuidad potencial (TEST-010)`.
- No bloquea por sí solo (ADR-A1-02: WARN por escenario, FAIL agregado).

## Tests TDD

1. `tests/unit/test_accept_verdict.py::test_zero_mutations_fails`
   — IR cuyo escenario no tiene examples → la función de veredicto (o la
   ruta de CLI testable) retorna fallo y el mensaje cita TEST-010.
2. `...::test_survivors_still_fail` — IR con examples y sobrevivientes →
   fallo (regresión: semántica anterior intacta).
3. `...::test_clean_scenario_passes` — IR con examples, 0 sobrevivientes →
   éxito (no romper el caso sano).
4. `...::test_vacuous_scenario_listed_as_warning`
   — feature mixto (1 escenario con Examples, 1 sin) → el reporte lista el
   vacuo como WARN y el veredicto NO falla solo por él (el agregado tiene
   mutaciones del otro escenario).

## No hacer

- No tocar `accept/pipeline.py::mutations()` (el motor sigue igual; la
  semántica cambia en el veredicto).
- No editar `governance/acceptance-manifest.json` ni manifests generados.
- No introducir claves nuevas de thresholds.yaml.

## Commit

`fix(accept): la mutación de aceptación no aprueba con cero mutaciones (TEST-010)`
(+ commit aparte `feat(features): parametriza escenarios sin Examples` si el
censo del paso 0 encontró vacíos).
