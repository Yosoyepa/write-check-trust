# SPEC-F-1 — Coder-F1: F4-b productivo, checker retirado, feature invertido

Rol: coder. Frontera EXACTA (nada fuera de esta lista):

```
tools/wct/selftest/fixtures_tools.py
tools/wct/selftest/redteam.py
quality/redteam/cases.yaml
quality/redteam/cases-tool.yaml
features/wct-redteam-residual-001.feature
tests/unit/test_redteam_engine.py
tests/unit/test_redteam_tools.py
```

## Paso 0 — Contratos (leer ANTES de escribir; verificados por el arquitecto)

1. `docs/evolution/plans/PR-F/ANALYSIS.md` — contrato completo del gate con
   file:line y la sonda medida.
2. `build/tmp/probe_f4b.py` — córrelo (`uv run python build/tmp/probe_f4b.py`):
   variante A (untracked) debe dar `FAIL · Coverage: 0%`. Esa receta es la
   que implementas, no otra.
3. Patrones a copiar: `_git_track` (`fixtures_tools.py:284`),
   `_vulture_governance` (`:246`) para la gobernanza mínima, builders
   existentes + `BUILDERS` (`:491`).
4. `tests/unit/test_redteam_tools.py:36-42` — el test parametrizado que
   ejercitará tu caso automáticamente.

## Paso 1 — TDD: tests PRIMERO (deben fallar en rojo antes de implementar)

1. `tests/unit/test_redteam_engine.py`: nueva
   `test_union_declares_zero_heuristics` — carga la unión real con
   `redteam._load_union(REPO_ROOT)` (REPO_ROOT ya existe en
   `test_redteam_tools.py:32`, cópialo) y afirma que NINGÚN caso tiene
   `harness == "heuristic"`. Hoy falla: F4-b aún lo declara.
2. `quality/redteam/cases-tool.yaml`: añade el caso (bloque, estilo de los
   existentes):

   ```yaml
   - id: F4-b
     failure_mode: F4
     harness: gate-tool
     gate: G-COV-DIFF
     tool: diff-cover
   ```

   Corre `uv run pytest tests/unit/test_redteam_tools.py -q` — F4-b falla
   con `KeyError: 'F4-b'` (sin builder). ESE es el rojo que quieres.
3. `tests/unit/test_redteam_engine.py`: re-enfoca R1, X5 y X6 de `checker:
   testless` a checkers reales (R1 → `forbidden-command` con payload
   `"git push --no-verify"` sobre G-HOOKS-WIRED; X5 conserva su propósito de
   arnés desconocido con cualquier checker; X6 → `heuristic` con
   `forbidden-command` y un payload que NO se bloquea, p. ej. `"ls"`, para
   conservar la expectativa "dejó de ser rechazado → fallo"). Ajusta solo
   lo que los renombres obliguen; no inventes casos nuevos.

## Paso 2 — Implementación mínima

1. `tools/wct/selftest/fixtures_tools.py`: builder `f4_b(tmp_path) -> Path`
   (docstring: adversario producción-nueva-sin-tests + receta de la sonda
   + referencia ADR-F-01). Contenido:
   - helper `_git_base(root)` (o inline): `git init -q -b main`,
     gobernanza (`governance/policy.yaml` = `schema_version: 1\n`;
     `governance/thresholds.yaml` = `schema_version: 1\ncoverage:\n  diff_min: 90\n`
     — replica el valor productivo de `thresholds.yaml:113` con comentario
     de procedencia, patrón `VULTURE_MIN_CONFIDENCE`),
     `git add -A`, commit con `-c user.email=wct@redteam -c
     user.name=wct-redteam -c commit.gpgsign=false` (identidad y firma
     explícitas: el builder debe funcionar en cualquier máquina/CI).
   - víctima `src/victim/ops.py` = `"def add(a, b):\n    return a + b\n"`
     (UNTRACKED — no la agregues al index).
   - `build/coverage/lcov.info` = `"TN:\nSF:src/victim/ops.py\nDA:1,0\nDA:2,0\nend_of_record\n"`.
   - entrada `"F4-b": f4_b` en `BUILDERS`.
   - actualiza el docstring de cabecera del módulo con el contrato G-COV-DIFF
     (una viñeta, patrón de las existentes).
2. `quality/redteam/cases.yaml`: elimina la línea de F4-b con su comentario;
   ajusta la cabecera del archivo: aquí viven los hooks, y una declaración
   heurística futura volvería a vivir aquí — remite al feature
   `wct-redteam-residual-001` (ahora ratchet cero).
3. `tools/wct/selftest/redteam.py`: elimina `_reject_testless` y la entrada
   `"testless"` de `_CHECKERS`; docstring: el bullet `heuristic` gana la
   línea "F4-b fue redimido en la PR-F (ADR-F-01) y corre como gate-tool;
   el feature wct-redteam-residual-001 fija el conteo en cero".
4. `features/wct-redteam-residual-001.feature`: reemplaza el contenido por
   el feature de `GHERKIN-F.md` (VERBATIM, incluidos los comentarios `#`).

## Paso 3 — Verificación (en orden; reporta salida real, sin pipes para exit codes)

```bash
uv run pytest -q                                   # suite completa en verde
uv run pytest --collect-only -q >/dev/null; echo "EXIT=$?"   # TEST-011
uv run wct selftest redteam          # 30/30 · 13 gate-engine · 13 gate-tool · 4 hook · 0 heuristic · 0 SKIP
uv run wct gate --tier fast          # 7/7 (G-META-1 no está en fast)
uv run wct accept parse              # feature nuevo parseable
uv run wct mutate                    # delta sin sobrevivientes (TEST-002)
ruff format --config governance/lint/ruff.toml tools tests
ruff check --config governance/lint/ruff.toml --fix tools tests
```

`wct gate --tier commit`: G-META-1 en rojo ESPERADO (toqué
`tools/wct/selftest/*`, rutas protegidas) — repórtalo así, no lo persigas.
Lo arregla el bless humano final.

## No hacer

- NO toques `governance/**` (ni thresholds ni baselines): la gobernanza del
  fixture se PLANTA en el tempdir, no se edita la productiva.
- NO corras `wct mutate update-manifest`, `wct ratchet record`,
  `wct integrity bless` (solo el humano; el hook te bloquea igual).
- NO hagas push, NO abras PR, NO commitees en main.
- NO uses pipes para capturar exit codes (`cmd | tail` te da el exit de
  tail): redirige a archivo y lee `$?`.
- NO dejes el builder sin `capture_output=True` en los subprocess (ruido en
  la salida del red team).
- Si un gate falla por algo que NO es G-META-1: para, reporta la salida
  real, no "arregles" tocando fuera de tu frontera.
