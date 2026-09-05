# SPEC-G1a-1 — Coder: recepción y clasificación del inventario del motor

**Sustituye íntegramente al SPEC-G1-1 original** (REVIEW-G1 D1: no ejecutar
el original sin reconciliar; su `fresh=False` y su borrado de `.meta`
quedan anulados por ADR-G1-02). Estado: **AUTORIZADO** — aprobación humana
de yosoyepa, 2026-09-05 (Gherkin §G1a + ADR-G1-01/03; 02/04 por dirección).
Frontera EXACTA:

```
tools/wct/mutate/verdict.py         (nuevo: adaptador run→results--all→clasificación; retorna GateResult)
tools/wct/gate/mutation.py          (delega en el adaptador; fachada y exports intactos)
tools/wct/mutate/engine.py          (run: delta 0 informativo; delta >0 → adaptador, exit semántico)
tools/wct/cli.py                    (imprimir diagnóstico del CLI: estado/fase/conteos/identidades)
tests/unit/test_gate_mutation.py    (EXTENDER el control sano de PR-E; no duplicarlo)
tests/unit/test_mutation_verdict.py (nuevo: clasificación y precedencia)
tests/unit/test_mutation_cli.py     (nuevo: CLI por subprocess sobre micro-repo)
features/wct-mutation-verdict-001.feature (verbatim de GHERKIN-G1.md §G1a, tras aprobación)
docs/evolution/plans/G1/EVIDENCE.md (añadir las corridas de verificación del coder)
```

PROHIBIDO: `governance/**`, `pyproject.toml` (source_paths/selección),
`quality/redteam/**` (F2-a/b, F5-b intactos), `gate/exec.py` (timeout → G3),
borrar o escribir `mutants/**` (ADR-G1-02: la política de repetición es
G1b), selección de mutantes por subconjunto (H0), cualquier claim de
frescura/causa en mensajes del código (eso es G1b).

## Paso 0 — Contratos

1. ANALYSIS §1-§4 y ADR-G1-01/03 (la tabla de clasificación y precedencia
   es la única verdad; cualquier conflicto con este SPEC, manda el ADR y
   lo reportas).
2. NO re-ejecutes las sondas de EVIDENCE.md (P1–P8, D3): son evidencia
   preservada. Las corridas que TU escribas viven en tus tests y se
   registran al final en EVIDENCE.md.
3. `tests/unit/test_gate_mutation.py:57` — el control sano de PR-E que
   debes EXTENDER (afirmar además el inventario: N killed citado), nunca
   duplicar (RG01).
4. Idioma y tono de los mensajes: fase + causa declarada (tabla ADR-G1-01),
   sin atribuir "defecto de producto" al run-fail.

## Paso 1 — TDD (rojo contra mutation.py actual)

| Test | Rojo esperado hoy | Requisito |
|---|---|---|
| `test_clean_tree_cites_inventory` (extiende el sano de PR-E) | PASS sin inventario citado | RG01 |
| `test_timeout_states_are_instrument_error` (fixture countdown real, patrón sonda P8) | PASS falso → ERROR | M04a/RG03 parcial |
| `test_injected_nonterminal_states_error` (inyecta exits 2/34 en meta del fixture — etiqueta la inyección en el docstring) | PASS falso → ERROR | M04b |
| `test_results_failure_after_healthy_run_is_error` (doble de proceso EXPLÍCITO: responses del results con exit 1 tras run sano; etiquetado) | PASS falso → ERROR fase results | RG02 |
| `test_mixed_survived_and_timeout_error_preserves_findings` (survived + timeout: ERROR y las identidades survived siguen en details) | PASS falso | RG03 |
| `test_duplicate_identity_and_unknown_line_error` (inventario con ID duplicado y estado fuera de vocabulario) | PASS falso → ERROR | RG04 |
| `test_empty_inventory_is_error` (inventario legible vacío) | PASS falso → ERROR | M02 borde |
| `test_classification_table` (paramétrico 10 estados: status + summary; align con ADR-G1-01) | — | M04 |
| `test_run_failure_blocks_without_product_label` (run interrumpido: FAIL con "ejecución no completada", SIN "defecto") | FAIL con otro texto | D2 |
| `test_cli_subprocess_delta_reports_ids` (subprocess `wct mutate run` en micro-repo SIN manifiesto — toda función cuenta como cambiada; sobrevivientes → exit 1 + identidades impresas) | exit 0 de mutmut o sin IDs | RG09 |
| `test_cli_delta_zero_informs_without_quality_claim` | — | RG08 |

Dobles SOLO donde la tabla los etiqueta (RG02/M04b): los controles con
motor real (timeout, sano, sobrevivientes) NUNCA se sustituyen por dobles.

## Paso 2 — Implementación mínima

Adaptador (ADR-G1-03): secuencia run → `results --all true` → clasificación
por tabla con precedencia ERROR>FAIL conservando identidades; retorna
GateResult; diagnóstico con fase, conteos, estado por clase y versión
`mutmut --version` registrada (la llamada extra es aceptable; medir su
costo en la verificación). Gate y CLI según ADR-G1-01/03. CLI imprime
`estado:`/`fase:`/`identidades:` (formato estable, sin prometer parsing).

## Paso 3 — Verificación (reporta salida real; sin pipes para exit codes)

```bash
uv run pytest -q                      # suite completa; registrar duración base vs nueva (RG12 exploratorio)
uv run pytest --collect-only -q
uv run wct accept parse features/wct-mutation-verdict-001.feature
uv run wct accept ir-dry features/wct-mutation-verdict-001.feature
uv run wct selftest redteam           # 30/30 · 13 · 13 · 4 · 0 · 0 SIN CAMBIOS
uv run wct gate --tier fast           # 7/7
uv run wct gate --tier commit         # SOLO G-META-1 rojo esperado
ruff format --config governance/lint/ruff.toml <frontera>
ruff check --config governance/lint/ruff.toml --fix <frontera>
```

Presupuesto exploratorio (muestra pequeña, declarada como tal): ≥3
correcciones de (a) suite base vs nueva, (b) `wct gate --tier full` antes/
después — mediana y rango; el presupuesto DEFINITIVO de G1b lo mide y
aprueba el humano (RG12).

## No hacer

- NO borres/modifiques `mutants/**` ni corras `mutmut run '*'` (G1b).
- NO toques el manifiesto/lock del repo; el fixture CLI usa manifiesto
  AUSENTE (scan marca todo como cambiado).
- NO cites este SPEC si contradice un ADR: manda el ADR y repórtalo.
- NO push, NO PR, NO bless/update-manifest/ratchet record; no `pytest -k`
  como evidencia.
