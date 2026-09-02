# VERIFICATION — PR-A2: definition of done y secuencia humana

## Definition of done

1. Escenarios de [GHERKIN-A2.md](GHERKIN-A2.md) aprobados y aterrizados en
   `features/` (prosa como comentarios, escenarios literales).
2. Paso 0 del spec investigado y documentado (semántica fail-under, acuerdo
   lcov↔term, semántica actual de record).
3. Tests TDD (9 nombrados en el spec) en verde, rojo-primero.
4. Matriz completa con salida real (PROC-012) + sección "Propuestas al
   arquitecto".
5. Commits convencionales con byline `By coder.`
6. PR abierto enlazando este plan.

## Matriz de verificación

| Verificación | Comando | Criterio |
|---|---|---|
| Suite | `uv run pytest -q` | 195 + nuevos, 0 failed |
| Tier fast | `uv run wct gate --tier fast` | 7 PASS · duración sin regresión apreciable (medición por artefacto) |
| Tier commit | `uv run wct gate --tier commit` | solo G-META-1 FAIL (pyproject + tools/wct sin bless) — **y G-COV-TOTAL PASS con fail-under activo y TOTAL 73 % visible** |
| Ratchet | `uv run wct ratchet check` | `coverage-total` PASS contra baseline registrado (73) |
| Aceptación | `uv run wct accept parse` | EXIT=0 |
| Red team | `uv run wct selftest redteam` | 30/30 |
| Cobertura real | salida del propio G-COV-TOTAL | TOTAL 73 % sobre ~2 5xx statements (±2 por código nuevo) |
| Registro por métrica | demo en el handoff | `record --metric` toca solo su baseline (evidencia con fixture, nunca sobre los baselines reales del repo) |

## Predicciones falsables

- TOTAL 73 % (2509 stmts ±2, ~598 miss ±2) bajo `-m "not property"`.
- Tier fast no sube de ~0.9 s a algo apreciable (parse lcov < 10 ms).
- `ratchet check` antes del re-baseline humano: `coverage-total: actual=73,
  baseline=100` **FAIL** — este rojo es la evidencia del defecto y se resuelve
  con la secuencia humana, no tocando código.

## Secuencia humana completa (tus dos comandos, en orden)

```bash
git checkout fix/self-coverage-baseline
# 1) registra el punto de partida real (ADR-A2-02):
uv run wct ratchet record --metric coverage-total \
  --approved-by "yosoyepa" \
  --reason "re-baseline por cambio de scope en PR #N: 100 era src/example (61 stmts, seed); real con src+tools/wct = 73 %"
# 2) bless del PR (cierra G-META-1 + manifiesto de mutación):
uv run wct mutate update-manifest --approved-by "yosoyepa" \
  --reason "aprobado en PR #N: PR-A2 scope+baseline de cobertura (plan docs/evolution/plans/PR-A2)"
git add -A && git commit -m "chore: bless PR-A2 self-coverage baseline (PR #N)" && git push
```

Tras tu push: CI verde → squash merge → verificación post-merge en main
(`gate --tier commit` con G-COV-TOTAL aplicando el piso y `ratchet check`
verde).

## Post-merge inmediato

- Primer PR futuro que baje cobertura total bajo 73 rompe el gate: el ratchet
  vive. Subirlo es `ratchet record --metric coverage-total` con valor mayor +
  razón.
- Nota para adoptantes en el handoff del PR: cada repo registra SU baseline
  con el mismo comando; el 73 es el del template.
