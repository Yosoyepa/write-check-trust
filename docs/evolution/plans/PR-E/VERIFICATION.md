# VERIFICATION — PR-E: DoD de merge y secuencia humana

> Autorización: delegación de arquitecto vigente (PR-D, reconfirmada
> 2026-09-05 "mantenemos ritmo hasta mi bless").

## Definition of done (merge)

1. DoD-F1..F3 completos (mapeo criterio→evidencia en cada handoff).
2. Matriz completa con salida real + presupuesto de runtime.
3. PR abierto enlazando el plan; bless humano pendiente.

## Matriz de verificación

| Verificación | Comando | Criterio |
|---|---|---|
| Suite | `uv run pytest -q` | 286 base + nuevos, 0 failed |
| Red team | `uv run wct selftest redteam` (mutmut presente) | 30/30 · 13 engine · 12 tool · 4 hook · **1 heuristic** · 0 SKIP |
| Red team sin mutmut | which falseado (test existente del arnés) | casos mutmut → SKIP visibles |
| Presupuesto runtime | 3 corridas del selftest | ≤ +15s sobre ~5s |
| Tier full | `uv run wct gate --tier full` | G-MUT PASS dentro del tier; rojos solo G-META-1 (pre-bless) + G-DRY-TPL (deuda registrada: NO — la baseline ya es 17, debe PASS) — ver predicciones |
| Tier fast / commit / pr | idem | 7/7 · 19+G-META-1 · 24+G-META-1+G-HOOKS-WIRED |
| Ratchet | `uv run wct ratchet check` | todos se mantienen |
| Aceptación | `accept parse` + `ir-dry` features nuevos | EXIT=0 |
| Lint dual | ruff con `--config` (+ desnudo si DoD-F3 fix) | limpios |
| Colección | `pytest --collect-only -q` | sin errores |

## Predicciones falsables

- El desglose del red team imprime `1 heuristic (declarado)` — un solo
  residuo en toda la suite adversarial.
- G-MUT dentro del tier full agrega ≈2s (1.9s medidos sobre main).
- Si la matriz exit-code revela runner-roto → 0, el handoff de E1 lo
  trae con salida real y el PR lo declara — el caso NO se fuerza a verde.
- El cache de mutmut (`mutants/`, `.mutmut-cache`) no aparece en
  `git status` del repo del runner tras el selftest.

## Secuencia humana (bless único)

```bash
git checkout fix/mutation-real
uv run wct mutate update-manifest --approved-by "yosoyepa" \
  --reason "aprobado en PR #N: PR-E mutacion real — redime F2-a/F2-b/F5-b y G-MUT entra al tier full (plan docs/evolution/plans/PR-E)"
git add -A && git commit -m "chore: bless PR-E real mutation (PR #N)" && git push
```

(Recuerda: si en el futuro el bless lleva varios comandos que escriben
rutas protegidas, el bless va SIEMPRE de último — lección PR #32.)

## Post-merge

- Red team: 29/30 productivos, 1 residuo declarado (F4-b).
- Horizonte 1 + calificación del instrumento cerrados; el backlog queda
  con: deduplicación de plantillas (17), F4-b, mutación diferencial del
  harness (condiciones en ADR-E-01), G-MUT en pr (diferido).
