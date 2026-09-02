# VERIFICATION — PR-A1: definition of done y contrato del coder

## Definition of done

1. Escenarios de [GHERKIN-A1.md](GHERKIN-A1.md) aprobados por humano y
   aterrizados en `features/`.
2. Censo del paso 0 de SPEC-A1-02 (escenario × Examples) incluido en el
   handoff; vacíos parametrizados o escalados.
3. Tests TDD de los tres specs en verde, escritos antes que su implementación.
4. Matriz de verificación completa con **salida real pegada** (PROC-012).
5. Tres commits convencionales (más el de features si hubo parametrización).
6. PR abierto con cuerpo que enlaza este plan; sin push a main; sin bless.

## Matriz de verificación (salida real obligatoria en el handoff)

| Verificación | Comando | Criterio de aprobación |
|---|---|---|
| Suite completa | `uv run pytest -q` | 180+ passed, 0 failed (los tests nuevos suman) |
| Tier rápido | `uv run wct gate --tier fast` | 7 PASS · 0 SKIP · 0 FAIL |
| Tier commit | `uv run wct gate --tier commit` | verde; el resumen YA debe mostrar contadores separados (dogfooding inmediato del fix 3) |
| Aceptación parsea | `uv run wct accept parse` | sin errores |
| Red team | `uv run wct selftest redteam` | 30/30 |
| G-PROP intacto | `uv run pytest -q tests/property` | el property test corre y pasa |
| Exclusión efectiva | `uv run pytest --cov=src --cov=tools/wct --cov-branch -q -m "not property" 2>&1 \| tail -3` | TOTAL 73 % (idéntico al medido: el fix no mueve el número — ANALYSIS §2) |
| Sin consumidores rotos | `grep -rn "no bloqueantes" tests/ tools/ docs/ README.md` | solo restos intencionales; docs actualizados donde cite el formato viejo |

## Predicciones falsables (si algo no coincide, el handoff lo declara)

- Cobertura total: 73 % antes y después de A1 (scope sin cambio).
- Colección bajo `-m "not property"`: 179 tests (el property sale).
- El resumen del tier commit mostrará sus SKIP (si los hay en el entorno)
  separados por primera vez — evidencia visual del fix en la propia corrida.

## Contrato del coder (lecciones de fases 22–24 del piloto)

- Declara TODA desviación del spec en el handoff, aunque sea benigna.
- Al tocar archivos legacy: `uv run ruff format --config governance/lint/ruff.toml`.
- Si un gate falla por algo fuera de alcance: dejarlo rojo y reportarlo con
  salida — no "arreglarlo" tocando governance ni saltándose checks (SEC-006).
- Temporales en `./build/tmp/`, nunca `/tmp` (PROC-007).
- No correr bless/ratchet/update-manifest (bloqueados para agentes de todos
  modos); no pushear; no crear el PR final si el verificador arquitecto no
  revisó el diff antes.

## Paso humano único tras la verificación

```bash
git checkout fix/instrument-honesty-p0a   # rama recreada bajo este plan
uv run wct mutate update-manifest --approved-by "yosoyepa" \
  --reason "aprobado en PR #N: PR-A1 honestidad del reporte (plan docs/evolution/plans/PR-A1)"
git add -A && git commit -m "chore: bless PR-A1 instrument honesty (PR #N)" && git push
```

Cubre las rutas protegidas tocadas: `pyproject.toml` y `tools/wct/**`.
CI verde → squash merge → verificación post-merge en main
(`gate --tier commit` + lectura del nuevo resumen).

## Post-merge inmediato (dispara PR-A2)

- Registrar el baseline real bajo la semántica de A1:
  `uv run wct ratchet record --approved-by "yosoyepa" --reason "re-baseline
  por cambio de scope en PR #N2: 100 era src/example (61 stmts); real con
  src+tools/wct = 73 %"` — decisión humana documentada en el plan de A2.
