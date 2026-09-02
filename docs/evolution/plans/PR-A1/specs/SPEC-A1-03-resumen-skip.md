# SPEC-A1-03 — Resumen de gates con contadores separados

ADR: [ADR-A1-03](../decisions/ADR-A1-03-honestidad-skip.md) ·
Escenarios: `wct-skip-honesty` en [GHERKIN-A1.md](../GHERKIN-A1.md).

## Cambios

### 1. `tools/wct/report/render.py` (~líneas 19-20)

Reemplazar el agregado único:

```python
# antes
passed = sum(not result.blocking for result in results)
lines.append(f"\n{passed}/{len(results)} gates no bloqueantes")
# después (formato indicativo; mantener tres contadores distinguibles)
counts = {"PASS": 0, "SKIP": 0, "FAIL": 0}  # FAIL absorbe ERROR según model.Status
for result in results:
    ...
lines.append(f"\n{len(results)} gates: {p} PASS · {s} SKIP · {f} FAIL/ERROR")
```

- Usar `model.Status` como fuente de verdad de los estados (no
  `result.blocking`): PASS exacto, SKIP exacto, resto agrupado.
- La tabla por fila no se toca (ya muestra STATUS por gate).

### 2. Consumidores

- Buscar tests que asertan sobre la línea anterior (`grep -rn "no bloqueantes"
  tests/`) y actualizarlos; añadir los nuevos de abajo.
- `docs/` y `README.md`: actualizar SOLO donde el formato citado quede
  factualmente incorrecto tras el cambio (ej.: catálogos que muestren la línea
  de ejemplo).

## Tests TDD

En `tests/unit/test_render.py` (o el archivo que ya testeé render):

1. `test_summary_separates_pass_skip_fail`
   — resultados 1 PASS + 1 SKIP + 1 FAIL → la línea de resumen contiene los
   tres contadores con valores correctos (1, 1, 1) y NO contiene la cadena
   `3/3` ni `2/3 gates no bloqueantes`.
2. `test_summary_all_pass`
   — 7 PASS, 0 SKIP, 0 FAIL → `7 gates: 7 PASS · 0 SKIP · 0 FAIL/ERROR`
   (o equivalente del formato elegido).
3. `test_summary_with_only_skip_does_not_claim_full_pass`
   — 1 SKIP y nada más → el resumen no afirma verificación completa
   (regresión del defecto original: SKIP≠PASS en el agregado).
4. `test_skip_still_non_blocking`
   — sanity del modelo (si ya existe, no duplicar): solo SKIP → no bloquea.
   Documenta que A1 no cambia semántica.

## No hacer

- No modificar `tools/wct/gate/model.py` (`blocking`, `Status`).
- No añadir tratamiento por tier (perfil local/completo = Horizonte 0).
- No elevar motivos de SKIP al agregado (O-001 / Report V2).

## Commit

`fix(report): el resumen separa PASS de SKIP (no bloqueante ≠ verificado)`
