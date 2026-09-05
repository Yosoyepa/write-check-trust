# PR-F — Definition of Done

## Unidad de feature

- [ ] F4-b migra de `cases.yaml` (heurístico) a `cases-tool.yaml`
      (`gate-tool`, `tool: diff-cover`) con builder git en `fixtures_tools.py`.
- [ ] `uv run wct selftest redteam` reporta
      `30/30 · 13 gate-engine · 13 gate-tool · 4 hook · 0 heuristic (declarados) · 0 SKIP`.
- [ ] El checker `testless` no existe en `redteam.py` (ni función ni entrada
      en `_CHECKERS`); los casos hook siguen pasando por `_reject_verdict`.
- [ ] `features/wct-redteam-residual-001.feature` es el ratchet cero-residuos
      de GHERKIN-F.md, verbatim.

## Unidad de tests

- [ ] `test_union_declares_zero_heuristics` existe, falló primero (rojo
      contra F4-b heurístico) y pasa tras la conversión.
- [ ] `test_tool_case_catches_planted_defect[F4-b]` pasa con diff-cover
      presente (aserción sobre `GateResult.status is FAIL` del gate
      productivo — TEST-003).
- [ ] R1/X5/X6 re-enfocados a checkers reales; suite completa en verde;
      `pytest --collect-only -q` limpio (TEST-011).
- [ ] `uv run wct mutate`: cero sobrevivientes en el delta (TEST-002).

## Unidad de commit

- [ ] `docs: PR-F dossier — redención de F4-b` (arquitecto; rutas libres).
- [ ] `feat(redteam): F4-b corre gate-tool con fixture git; queda cero
      residuos` (coder; byline `By coder.`; TDD visible en el diff).

## Unidad de revisión (arquitecto)

- [ ] El builder planta gobernanza con `diff_min: 90` (réplica productiva,
      con comentario de procedencia) y NO toca `governance/**`.
- [ ] El commit base usa identidad y `commit.gpgsign=false` explícitos
      (portable a cualquier máquina/CI).
- [ ] La víctima queda UNTRACKED (la receta A medida en la sonda).
- [ ] Matriz de VERIFICATION.md corrida con salida real.

## Unidad de merge

- [ ] CI verde (incluye `commit-gates` con G-META-1 bendecido por el humano).
- [ ] Bless humano único: `wct mutate update-manifest --approved-by
      "yosoyepa" --reason "aprobado en PR #N: redención F4-b, red team sin
      residuos"` (regenera manifiesto + lock atómicamente), luego commit y
      push del bless.
- [ ] Squash merge, rama borrada, main verificado post-merge (pytest +
      redteam + fast + commit + ratchets).
