# PR-F — VERIFICATION

## Matriz (corría el arquitecto sobre la rama integrada; salida real reportada)

| Verificación | Predicción falsable | Comando |
|---|---|---|
| Suite completa | todos en verde; +2 tests netos (zero-heuristics + F4-b parametrizado) | `uv run pytest -q` |
| Colecta | 0 errores de colección | `uv run pytest --collect-only -q` |
| Red team | `30/30 · 13 gate-engine · 13 gate-tool · 4 hook · 0 heuristic (declarados) · 0 SKIP` | `uv run wct selftest redteam` |
| Tier fast | 7/7 | `uv run wct gate --tier fast` |
| Tier commit | G-META-1 rojo por diseño (rutas protegidas tocadas); resto verde | `uv run wct gate --tier commit` |
| Aceptación | parse limpio + ir-dry sin colisiones de forma (steps nuevos únicos) | `uv run wct accept parse` + `ir-dry` |
| Mutación delta | 0 sobrevivientes / 0 sin test | `uv run wct mutate` |
| Ruff | limpio | `ruff check --config governance/lint/ruff.toml` |

## Predicciones que refutarían el diseño

- Si `remote_base` no resolviera `main` en el fixture (p. ej. un cambio de
  orden en los candidatos), el gate daría ERROR y el caso quedaría en rojo
  con "sin rama base resoluble" — no un SKIP silencioso.
- Si diff-cover dejara de incluir untracked (cambio upstream del flag), el
  gate daría PASS con diff vacío → caso en rojo "el gate no cazó el
  defecto". ESE rojo es un hallazgo del instrumento, no un fixture que
  ajustar (ADR-C-01 §5).
- Si alguien re-declarara un heuristic en cases*.yaml,
  `test_union_declares_zero_heuristics` y el escenario del feature caen en
  rojo simultáneamente.

## Secuencia humana (tras CI verde de la PR)

1. `uv run wct mutate update-manifest --approved-by "yosoyepa" --reason "aprobado en PR #N: redención F4-b, red team sin residuos"`
2. `git add -A && git commit -m "chore: bless F4-b redemption (PR #N)" && git push`
3. Merge squash cuando CI vuelva a verde.

El paso 1 es el ÚNICO que escribe rutas protegidas (regenera manifiesto de
mutación + integrity lock atómicamente) — no hay orden trampa posible: es
un solo comando.
