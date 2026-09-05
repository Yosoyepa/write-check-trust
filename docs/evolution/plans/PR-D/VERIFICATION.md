# VERIFICATION — PR-D: DoD de merge y secuencia humana

> DoD por unidad en [DoD.md](DoD.md). Autorización: delegación de
> arquitecto del 2026-09-05 ("toma la decisión… te doy autoría… sigue
> autónomamente hasta que necesites mi bless").

## Definition of done (merge)

1. DoD-F1..F4 completos (mapeo criterio→evidencia en cada handoff).
2. Matriz completa con salida real.
3. PR abierto enlazando el plan; bless humano pendiente.

## Matriz de verificación

| Verificación | Comando | Criterio |
|---|---|---|
| Suite | `uv run pytest -q` | 268 base + nuevos, 0 failed |
| Red team | `uv run wct selftest redteam` | 30/30 · 13 engine · 9 tool · 4 hook · 4 heuristic · 0 SKIP |
| vulture neto | `uv run vulture src tools/wct governance/lint/vulture_whitelist.py --min-confidence 60` (whitelist como path posicional — vulture 2.16 no tiene flag) | 0 hallazgos, exit 0 |
| Ratchet | `uv run wct ratchet check` | solo `dry-template-clusters` (hallazgo preexistente, ver ANALYSIS §5): registro humano en el bless |
| Report | `uv run wct report` | sección `capabilities` con presencia/scope/tiers |
| Tier fast | `uv run wct gate --tier fast` | 7/7 |
| Tier commit | `uv run wct gate --tier commit` | solo G-META-1 rojo (pre-bless) |
| Tier pr | `uv run wct gate --tier pr` | G-META-1 + G-HOOKS-WIRED (mismo lock) y NADA más |
| Aceptación | `uv run wct accept parse` + `ir-dry` de los 4 features | EXIT=0 |
| Colección | `uv run pytest --collect-only -q` | sin errores |
| Lint dual | ruff con y sin `--config` | ambos limpios |
| Runtime | delta del tier fast vs main | sin regresión (>+1s = hallazgo) |
| Tier full | `uv run wct gate --tier full` | G-META-1/G-HOOKS-WIRED (bless) + G-DRY-TPL (hallazgo preexistente §5) y NADA más |

## Predicciones falsables

- `wct report` desde un entorno sin quality group lista las herramientas
  de G-DEAD/G-ARCH/G-SAST-SEMGREP/G-DEPS/G-SECRET con `present: false` —
  y con el grupo instalado, `present: true`.
- vulture@60+whitelist: 0 hallazgos. Si aparece otro FP durante la PR, es
  evidencia nueva y va al handoff — NO a la whitelist por defecto.
- El diff del artefacto regenerado contiene exactamente un cambio de
  campo (`source` absoluto → relativo).
- La salida de `wct gate --tier fast` en un entorno sin SKIPs es
  byte-idéntica a la de main (regresión del render).

## Secuencia humana (bless único)

```bash
git checkout fix/capability-profiles
uv run wct mutate update-manifest --approved-by "yosoyepa" \
  --reason "aprobado en PR #N: PR-D perfiles y completitud + redenciones (plan docs/evolution/plans/PR-D)"
uv run wct ratchet record --approved-by "yosoyepa" --metric dry-template-clusters \
  --reason "aprobado en PR #N: registra 17 clusters (deuda preexistente 16 en main desde 2026-08-23 + 2 de fixtures PR-D - 1 disuelto por la particion de runner.py); deduplicacion archivada como PR propio"
git add -A && git commit -m "chore: bless PR-D capability profiles (PR #N)" && git push
```

Cubre las rutas protegidas: tools/wct/**, governance/thresholds.yaml,
governance/lint/** (whitelist nueva), pyproject.toml,
quality/redteam/**, tests/acceptance/generated/** (regenerado).

## Post-merge

- Horizonte 1 cerrado de verdad: reporte honesto (A1), self-measurement
  (A2), config con autoridad (B), adversarios reales (C), capacidades y
  scopes explícitos (D).
- PR-E siguiente: mutación del harness — redime F2-a/F2-b/F5-b.
