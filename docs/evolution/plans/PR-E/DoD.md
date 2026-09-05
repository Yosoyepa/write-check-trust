# DoD — PR-E: Definitions of Done por unidad de aceptación

## Reparto entre coders (frontera disjunta)

- **Coder-E1 — redenciones**: `quality/redteam/cases.yaml`,
  `quality/redteam/cases-tool.yaml`,
  `tools/wct/selftest/fixtures_tools.py`,
  `tools/wct/selftest/redteam.py` (solo reconocedores muertos),
  `tests/unit/test_redteam_tools.py`.
- **Coder-E2 — tier y ruff**: `tools/wct/gate/runner.py` (solo TIERS),
  `docs/STATUS.md`, `pyproject.toml` y/o `governance/lint/ruff.toml`
  (SOLO si el root-cause lo exige, fix ≤5 líneas), tests del tier y de
  ruff, addendum ADR-D-03 si hay fix.
- El arquitecto aterriza features/, dossier e índice; addendum ADR-C-02.

## DoD-F1 — las 3 redenciones (E1)

1. Matriz exit-code medida SIN pipes (paso 0.1) documentada en handoff;
   hallazgo runner-roto reportado si aplica (y NO maquillado).
2. Los 3 casos cazan con corridas reales de mutmut sobre fixtures (tests
   parametrizados ×12 en verde con quality; rojo primero documentado).
3. Receta de fixture documentada; nada del cache de mutmut escapa al
   árbol del repo del runner.
4. `cases.yaml` queda con 4 hook + F4-b; `_reject` pierde `hardcoded` y
   `survivor`; `testless` sobrevive (F4-b).
5. Desglose final: `30/30 · 13 gate-engine · 12 gate-tool · 4 hook ·
   1 heuristic (declarado) · 0 SKIP` con mutmut presente.

## DoD-F2 — G-MUT en full (E2)

1. `G-MUT in TIERS["full"]` fijado por test (y en ningún otro tier).
2. Runtime medido frío y con cache (handoff); delta del tier full
   reportado (esperado ≈ +2s).
3. STATUS.md actualizado (34 gates en full).

## DoD-F3 — ruff desnudo árbol (E2, condicional)

1. Root-cause documentado con salida de `--show-settings` (handoff).
2. Si fix quirúrgico: ruff desnudo sobre el árbol → 0 hallazgos (test
   rojo-primero: hoy 622) + addendum fechado en ADR-D-03.
3. Si estructural: hallazgo documentado, sin forcear nada.

## DoD por commit / revisión / merge

- **Commit**: conventional + byline `By coder.` + hooks sin
  `--no-verify` + suite verde en intermedios.
- **Revisión de arquitecto**: diffs completos; DoD-F1..F3 verificados
  independientemente; el hallazgo exit-code (si existe) adjudicado con
  razón escrita antes del merge.
- **Merge**: matriz de VERIFICATION.md con salida real + presupuesto de
  runtime del selfteam ≤ +15s + G-META-1 como único rojo pre-bless.
