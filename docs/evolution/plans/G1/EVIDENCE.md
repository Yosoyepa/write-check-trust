# G1 — Registro durable de evidencia (REVIEW-G1 §10)

Todo hallazgo se atribuye por TIPO: **[O] observación** de proceso real sin
intervención · **[I] inyección** controlada en un artefacto real (válida
para representación/respuesta; no prueba ocurrencia natural) · **[L] lectura
de fuente** · **[INF] inferencia** a partir de medidos, con la cadena citada.
Los fixtures bajo `build/tmp/` son efímeros: este registro conserva comandos,
versiones y salidas clave para revisión sin reejecutar.

## Entorno

- mutmut **3.7.0** (`.venv/lib/python3.12/site-packages/mutmut/`,
  `__main__.py`, `mutation/data.py`); Python 3.12.13 (uv).
  Las citas de línea se refieren a ESA instalación; un hash de fuente no se
  registró en el turno original — reproducibilidad por versión declarada.
- Repo en `0f80122`; sondas corridas con `uv run python` (venv activo).

## Sondas y atribución

| Sonda | Comando | Tipo | Salida clave |
|---|---|---|---|
| P1 sano | `mutmut run` + `mutmut results` + `results --all true` | [O] | run exit 0; results **vacío** exit 0 (vacío válido); `--all true` lista `victim.calc.x_add__mutmut_1: killed` |
| P2 defectuoso | ídem, fixture billing/lonely | [O] | run exit **0** con 2 `survived` + 3 `no tests` en results |
| P3 cero mutables | ídem | [O] | run exit **1** "Stopping early… test case for any mutant" (guard del motor) |
| P4a meta corrupto | escribir JSON inválido → `mutmut results` | [I] en artefacto + [O] de la fase results **standalone** | exit 1, JSONDecodeError. **No es la secuencia completa del gate** (REVIEW-G1 §2) |
| P4b meta ilegible | chmod 000 → results | [I] + [O] standalone | exit 1, PermissionError |
| P4c metas borrados | unlink → results | [I] + [O] standalone | exit **0** y salida VACÍA (pérdida silenciosa) |
| P5bis caché | debilitar aserciones conservando llamadas → `mutmut run` | [O] (secuencia completa, gate real) | run exit 0 "0.00 mutations/second"; results vacío; **gate PASS** — falso verde E2E |
| P6bis selección | `mutmut run <nombre>` / patrón sin coincidencia | [O] | seleccionado re-ejecuta ("Mutant results / 🎉 …"); sin coincidencia → AssertionError exit 1 |
| P7/B vocabulario | plantar exits 2 y 34 en meta → results + gate | [I] (representación) | results imprime `check was interrupted by user`, `skipped`; **gate PASS** |
| P8 timeout | `n -= 1` → bucle infinito real | [O] (secuencia completa) | run exit 0 (17 s); results 2 `: timeout`; **gate PASS** — falso verde E2E |
| D3 frescura | debilitar aserciones conservando llamadas → `mutmut run '*'` literal | [O] (fixture único `build/tmp/g1a-freshness/`) | 28.06 mutations/second (re-ejecutó); results: ambos `survived` — la repetición pública derrota la herencia SIN borrar metas |
| Repo main | mtimes de `mutants/src/example/*.meta` (09:10) + G-MUT 1.8 s | [O] | reutilización de resultados REPORTADA; **validez con tests actuales NO acreditada** (REVIEW-G1 §3) |

## Correcciones fácticas incorporadas (vs primer dossier G1)

1. PR-E YA tiene control sano real: `test_clean_tree_passes_with_zero_survivors`
   (`tests/unit/test_gate_mutation.py:57`). G1a lo EXTIENDE (inventario),
   no lo duplica.
2. Herramienta ausente → `Status.SKIP` (`gate/mutation.py:43`) — no ERROR.
3. La tabla de estados son 1 aprobado (killed), 2 defectuosos (survived,
   no tests) y 7 fuera del contrato de certificación — no "ocho fallos".
4. El costo CI no es nulo: `gate_mutation` se ejecuta en CI vía
   `tests/unit/{test_gate_mutation,test_mutation_gate,test_gate_mut_tier,
   test_redteam_engine,test_report_profile}.py` y los casos redteam
   F2-a/F2-b/F5-b (`quality/redteam/cases-tool.yaml`). El fixture timeout
   real suma a suite, coverage y redteam.
5. exit 1 y exit 3 colapsan a `killed` (`__main__.py:82-104`): el inventario
   textual NO conserva causa (límite del claim G1a; G1b lo ataca).

## Escape post-merge de G1a (arquitecto, 2026-09-05) — registro honesto

`wct ratchet check` en main tras fusionar PR #37: **`introverted-tests:
actual=1, baseline=0`** — `test_cli_subprocess_delta_reports_ids` salió
"introverted" (sus aserciones sobre la salida del subprocess no trazan a
un import del SUT, regla de `introvert/analyzer.py:97-112`).

Causa raíz, doble:

1. **G-INTROVERT vive solo en el tier full** (`gate/runner.py:506`) — ni
   el workflow de CI (commit-gates) ni la matriz pre-merge de G1a lo
   ejecutan: el patrón F05 de POST-PR36 (CI ≠ contratos locales), ahora
   con un caso propio.
2. **`wct ratchet check` faltó en mi matriz de verificación pre-merge de
   la PR #37** (estuvo en la de #36). El escape es del arquitecto, no del
   coder: su SPEC no lo listaba.

Arreglo (PR inmediata, tests-only, sin bless — sin rutas protegidas): el
test del CLI coteja la salida del subprocess contra el veredicto del SUT
calculado in-process (`mutation_verdict` + `EXIT_CODES` importados del
SUT) — aserción MÁS fuerte que la original: fija que el CLI expone
exactamente lo que el adaptador dicta (exit según tabla, líneas
`identidades:` del veredicto). El baseline del ratchet NO se toca
(PROC-008). Corrección de proceso: `wct ratchet check` entra a la matriz
de verificación estándar de cada PR desde ahora.

## Delimitación de roles (REVIEW-G1 §10, final)

El rol **specifier** no ejecuta mutación (`.claude/agents/specifier.md`).
Las sondas de este dossier fueron ejecutadas como **arquitecto de
diseño** con autorización diagnóstica explícita del prompt de REVIEW-G1
("evalúa primero repetición pública…"); los fixtures históricos
`build/tmp/g1probe/` NO se recrearon ni modificaron (preservados como
evidencia; REVIEW-G1 los leyó en modo lectura). Directorio único nuevo:
`build/tmp/g1a-freshness/`.

## Verificación del coder (2026-09-05)

Implementación de G1a (commit de implementación, rama
`fix/g1a-mutation-verdict`): adaptador `tools/wct/mutate/verdict.py`
+ delegación en `gate/mutation.py` + `engine.run` con exit semántico +
diagnóstico del CLI. Entorno idéntico al de arriba (mutmut 3.7.0, Python
3.12.13/uv). Todas las corridas sobre fixtures en `tmp_path` de pytest; el
`mutants/**` del repo NO se tocó (política de repetición = G1b). Salidas
íntegras en `build/tmp/g1a-*.txt` (efímeras; aquí las clave).

### TDD — rojo observado antes de implementar [O]

- `test_mutation_verdict.py`: `ModuleNotFoundError: No module named
  'tools.wct.mutate.verdict'` (clasificación inexistente).
- `test_clean_tree_cites_inventory`: `AssertionError: assert 'clasificación
  del motor' in 'cero mutantes sobrevivientes'` — PASS sin inventario citado
  (RG01).
- `test_timeout_states_are_instrument_error` y
  `test_injected_nonterminal_states_error`: `assert <Status.PASS: 'PASS'> is
  <Status.ERROR: 'ERROR'>` — el PASS falso de P8/P7-B, ahora rojo (RG03/M04b).
- `test_run_failure_blocks_without_product_label`: `assert 'ejecución no
  completada' in 'failed to collect stats. runner returned 5'` — FAIL con
  otro texto (D2).
- `test_cli_subprocess_delta_reports_ids`: `assert 0 == 1` — el CLI heredaba
  el exit 0 de `mutmut run` con sobrevivientes y no imprimía identidades
  (RG09).
- `test_cli_delta_zero_informs_without_quality_claim`: ROJO pese a que la
  tabla del SPEC lo predecía "—" — el mensaje viejo era "No hay funciones
  cambiadas respecto al manifest." y el contrato RG08 ("sin trabajo
  diferencial") es nuevo. Desviación reportada en el handoff.

### Batería de verificación (salida real) [O]

- `uv run pytest -q` → `319 passed` ×3 (ver presupuesto abajo).
- `uv run pytest --collect-only -q` → `319 tests collected in 0.39s`.
- `uv run wct accept parse features/wct-mutation-verdict-001.feature` →
  exit 0, IR schema_version 1 (feature intacta).
- `uv run wct accept ir-dry features/wct-mutation-verdict-001.feature` →
  `{"findings": [], "count": 0}` exit 0.
- `uv run wct selftest redteam` → `30/30 rechazados · 13 gate-engine · 13
  gate-tool · 4 hook · 0 heuristic (declarados) · 0 SKIP` — SIN CAMBIOS
  (F2-a/F2-b/F5-b siguen cazados: FAIL preservado por ADR-G1-01 fila 9).
- `uv run wct gate --tier fast` → `7 gates: 7 PASS · 0 SKIP · 0 FAIL/ERROR`.
- `uv run wct gate --tier commit` → `20 gates: 19 PASS · 0 SKIP · 1
  FAIL/ERROR`; el único rojo es `G-META-1 FAIL — modificado:
  tools/wct/cli.py` (esperado por diseño: la frontera toca `tools/wct/**`
  y el bless es humano).
- `ruff format`/`ruff check --fix` (`--config governance/lint/ruff.toml`)
  sobre la frontera → `7 files left unchanged` / `All checks passed!`.

### Presupuesto exploratorio RG12 (muestra pequeña, declarada como tal)

- Suite base (pre-cambio): 300 passed en **44.89 / 46.65 / 47.44 s**
  (mediana 46.65, rango 2.55).
- Suite nueva: 319 passed en **82.04 / 86.50 / 87.32 s** (mediana 86.50,
  rango 5.28). Delta mediana ≈ **+40 s**, dominado por el control timeout
  REAL: `test_timeout_states_are_instrument_error` 18.66 s (patrón P8),
  `test_injected_nonterminal_states_error` 5.81 s (dos pasadas del motor:
  corrida sana + cache), `test_cli_subprocess_delta_reports_ids` 3.95 s
  (subprocess `uv run` real).
- Costo de la llamada extra `mutmut --version` [O]: 0.66 s bajo `uv run`
  (salida `mutmut, version 3.7.0`), 1 llamada por veredicto medido.
- `wct gate --tier full` antes/después: **NO medido** — G-MUT en full
  ejecutaría `mutmut run` sobre el repo y re-escribiría `mutants/**`,
  bloqueado por ADR-G1-02 (política de repetición = G1b). El presupuesto
  DEFINITIVO sigue siendo medición y aprobación humana en G1b.
