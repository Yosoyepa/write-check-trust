# VERIFICATION — PR-B: definition of done y secuencia humana

> El DoD de nivel merge vive aquí; el DoD por feature, workstream, commit y
> revisión vive en [DoD.md](DoD.md) — son complementarios y ambos obligatorios.

## Definition of done

1. Escenarios de [GHERKIN-B.md](GHERKIN-B.md) aprobados y aterrizados en
   `features/`.
2. Paso 0 documentado (claves confirmadas, comandos actuales capturados).
3. Tests TDD (7 nombrados en el spec) en verde, rojo-primero.
4. Matriz completa con salida real (PROC-012) + "Propuestas al arquitecto".
5. Commits convencionales con byline `By coder.`
6. PR abierto enlazando este plan.

## Matriz de verificación

| Verificación | Comando | Criterio |
|---|---|---|
| Suite | `uv run pytest -q` | 212 base + nuevos, 0 failed |
| Tier fast | `uv run wct gate --tier fast` | 7 PASS (doctor no corre aquí) |
| Tier commit | `uv run wct gate --tier commit` | solo G-META-1 FAIL (thresholds.yaml + tools/wct sin bless) |
| Tier pr | `uv run wct gate --tier pr` | 26 PASS · 0 SKIP tras bless (G-CRAP/G-DEAD/G-CC/G-COV-DIFF verdes con comandos cableados) |
| Comandos idénticos | diff entre paso 0.3 y post-cableado | byte-idéntico por gate |
| doctor | `uv run wct doctor` | sección "Umbrales declarados → gates" con ≥11 pares en vivo |
| Aceptación / red team | `wct accept parse` / `selftest redteam` | EXIT=0 / 30/30 |
| LCOM/DRY standalone | `wct lcom --json` / `wct dry --normalized` | sin cambios de salida con valores vigentes |

## Predicciones falsables

- Ningún comando de gate cambia con el YAML vigente (regresión byte-idéntica).
- El conteo del ratchet `dry-template-clusters` y `lcom-classes` NO cambia
  (mismos valores, otra fuente) — si cambia, el cableado alteró semántica:
  parar y reportar.
- `wct doctor` antes del PR no tiene la sección; después la tiene con los
  valores del YAML real.
- G-SIZE: runner.py no crece (constructores en checks.py); si checks.py
  supera 500, partición TEST-007 en el mismo PR.

## Secuencia humana (un solo paso: bless)

```bash
git checkout fix/config-runtime-conformance
uv run wct mutate update-manifest --approved-by "yosoyepa" \
  --reason "aprobado en PR #N: PR-B conformidad config→runtime (plan docs/evolution/plans/PR-B)"
git add -A && git commit -m "chore: bless PR-B config-runtime conformance (PR #N)" && git push
```

(Sin `ratchet record`: PR-B no cambia ninguna métrica — los valores son los
mismos, solo cambia la fuente. El diff de thresholds.yaml está autorizado por
la aprobación de este plan; ADR-B-02 §1 lo congela.)

## Post-merge inmediato

- Cambiar un umbral cableado pasa a requerir bless (G-META-1 sobre
  thresholds.yaml) Y tiene efecto real: la gobernanza recupera autoridad.
- El inventario de huérfanas del ANALYSIS queda listo para la decisión del
  Horizonte 0 (activar/deprecar/retirar).
