# SPEC-G3a-1 — Coder: G3a-1 (AUTORIZADA con ajustes obligatorios; SIN commit en este encargo)

Estado: **AUTORIZADA** (yosoyepa, 2026-09-05; encargo con 5 ajustes
obligatorios ya reconciliados en ADR-G3a-01/02/03/04 y GHERKIN-G3a).
**Entrega en el ÁRBOL DE TRABAJO: este encargo PROHÍBE commit/push/PR.**
G3a-2 (workflow) y G1b productivo quedan FUERA. Frontera EXACTA:

```
tools/wct/gate/runner.py            (membresía: G-INTROVERT → _COMMIT_GATES; retirar entrada de full)
tools/wct/ratchet/measure.py        (check(root, required=…) según ADR-G3a-02; inventario explícito)
tools/wct/cli.py                    (ratchet check --require …; validación de entrada; denominador)
tools/wct/introvert/analyzer.py     (SOLO docstring del módulo: limitación subprocess)
tests/unit/test_ratchet_check.py    (nuevo: contrato --require + regresión del escape)
tests/unit/test_gate_tiers.py       (membresía commit/pr/full sin duplicados)
tests/unit/test_mutation_cli.py     (doble clase de aserciones, ADR-G3a-04)
features/wct-premerge-verification-001.feature (verbatim de GHERKIN-G3a §aprobada)
```

PROHIBIDO: `.github/workflows/**`, `governance/**` (baselines incluidos),
`quality/redteam/**`, `pyproject.toml`, `mutants/**`, manifiestos, y
COMMIT/PUSH/PR/bless/update-manifest/ratchet record.

## Paso 0 — Contratos

1. ADR-G3a-01/02/03/04 (versión aceptada con ajustes) y GHERKIN-G3a.md —
   mandan sobre este SPEC en caso de conflicto; repórtalo si lo ves.
2. `ratchet/measure.py:118-149` — modo sin `--require` BYTE-compatible.
3. `G1/EVIDENCE.md` §addenda — los matices que este trabajo materializa.

## Paso 1 — TDD (rojo primero; documenta los rojos)

**Corrección pre-bless (hallazgos humanos, 2026-09-05) — tests NUEVOS que
hoy dan rojo y son la razón de esta revisión:**

0a. `test_require_does_not_silence_other_ratchets` — reproducción del
hallazgo 2: mismas mediciones con una métrica fuera de baseline
(introverted=1 vs 0) y `required=["suppressions"]` → el reporte exigible
**SIGUE conteniendo el fallo de introverted-tests**. Hoy: verde falso.
0b. `test_invalid_lcov_counters_block_in_require_mode` — reproducción del
hallazgo 1 (bloqueante): LCOV con `LH:2` sobre `LF:1` (200% imposible) →
`required=["coverage-total"]` bloquea con "medición inválida" nombrando el
defecto; variantes: `BRH>BRF`, totales en cero, y rango >100. El modo
tolerante NO cambia (byte-compat ya probada sigue verde).
0c. `test_coverage_producer_command_matches_gate_recipe` — el comando
productor de `_COVERAGE_TOTAL_COMMAND` contiene los tokens de la receta
productiva del gate (checks.py, incl. `-m`/`not property`) — importa el
builder productivo en el test y compara tokens.
0d. `test_green_denominator_n_of_n_with_multiple` — verde exigible
N-de-N con N≥2 (dos métricas medidas y en baseline → `medidas 2 de 2`).

**Corrección residual pre-bless (3º hallazgo humano, 2026-09-05) — test:**

0g. `test_incomplete_counters_block_without_traceback` — reproducción:
registro VÁLIDO que diluya el total (p. ej. LF:10/LH:5) + registro
INCOMPLETO (`LH:1` sin `LF`, o `BRH:1` sin `BRF`) → hoy `_record_defect`
lanza **KeyError** (la comparación usa `.get(..., 0)` pero el mensaje
accede `record['LF']`). El modo exigible debe devolver `medición inválida`
con causa y registro (`LH 1 sin LF en <SF>` / `BRH 1 sin BRF en <SF>`),
sin traceback. **No ampliar el contrato de completitud**: `LF` sin `LH`
sigue siendo VÁLIDO (0 cubiertas); el defecto es exclusivamente
cubiertas-sin-total. Tolerante intacto.

**Corrección final pre-bless (2º hallazgo humano, 2026-09-05) — tests:**

0e. `test_malformed_counters_block_in_require_mode` — reproducción: LCOV
con un registro válido al 100% + otro con `LF:-1`/`LH:-2` (hoy: la regex
`\d+` IGNORA esos renglones, el registro queda "vacío-coherente" y el
validador retorna None → verde). La vía exigible debe RECHAZAR renglones
con nombre de contador reconocido (`LF|LH|BRF|BRH:`) y valor que no sea
entero no-negativo → `medición inválida` nombrando el contador y el SF.
Variantes: `LF:1.5`, `LF:` vacío. Tolerante intacto (su parser histórico
no cambia: preservar su compatibilidad no obliga al validador nuevo a
ignorar esos errores).
0f. Fortalecer 0c con límites de argumento reales: el comando productor se
imprime shell-correcto — `-m "not property"` — y el test compara
`shlex.split(comando_mostrado)` contra la LISTA del builder productivo
(checks.py, sin el par `--cov-fail-under <piso>`), SIN aplanar con
`.split()` (que pierde justamente los límites de argumento que deben
verificarse).

**Consolidación (hallazgo humano):** las aserciones independientes viven
DENTRO de `test_cli_subprocess_delta_reports_ids` (exit 1 literal,
`estado: FAIL`, `fase: criterio`, `survived=` + cotejo adaptador) y
`test_cli_mutate_run_keeps_independent_contract` SE ELIMINA — una sola
ejecución del motor, no dos (ahorra ~7 s de suite).

**Regresión del escape (ADR-G3a-01, ajuste 4 del humano):**

1. `test_repo_introverted_ratchet_holds_baseline` — usa la MEDICIÓN y el
   BASELINE productivos: `measurements(REPO)["introverted-tests"]` contra
   `baseline(REPO, "introverted-tests")` con `compare` productivo. **PROHIBIDO
   un segundo umbral 0 hardcodeado** — si el humano sube el baseline con
   `ratchet record`, este test lo sigue (no invalida decisiones futuras).
2. `test_defective_control_introverted_detected` — fixture con UN test
   introverted y baseline propio en 0: `check()` productivo lo reporta
   (control defectuoso emparejado — especificidad).

**Contrato `--require` (ADR-G3a-02, ajuste 3):**

3. `test_require_rejects_empty_unknown_and_duplicated` — lista vacía,
   nombre desconocido y duplicado → error de uso con los nombres válidos.
4. `test_require_blocks_missing_naming_metric_and_command` — exigible
   ausente (coverage-total sin LCOV; docstring-coverage sin interrogate
   simulado por PATH sin la tool) → fallo nombrando métrica, causa y el
   comando que produce la medición.
5. `test_require_presence_is_not_threshold` — DOS fronteras: métrica
   presente y EN baseline → verde; presente y POR ENCIMA → rojo por
   umbral con texto distinto al de ausencia (compare productivo).
6. `test_require_all_uses_explicit_inventory` — `all` exige el inventario
   de código (incluidas las que hoy no se puedan medir en el entorno del
   test → bloqueo por ausencia, no éxito por omisión).
7. `test_require_publishes_names_and_denominator` — salida con nombres
   exigidos, medidos y `medidas N de M exigibles`.
8. `test_without_require_output_unchanged` — sin flag, salida idéntica
   (compara contra la del modo actual).

**Membresía (ajuste 1):**

9. `test_introvert_in_commit_and_pr_without_duplication` — G-INTROVERT en
   commit y en pr (hereda `_COMMIT_GATES`), SIN duplicar en full.

**Doble clase CLI (ajuste 2):**

10. `test_cli_mutate_run_keeps_independent_contract` — exit `1` literal,
    `estado: FAIL`, `fase: criterio`, `survived=` en conteos — CONSERVANDO
    el cotejo con `mutation_verdict` como comprobación adicional.

## Paso 2 — Implementación mínima (estado: corrección pre-bless sobre lo ya implementado)

Ya implementado y verificado (no lo rehagas): membresía de tiers,
inventario, validación de entrada, `_absent_failure`, denominador,
docstring del analyzer, feature verbatim, regresión y doble clase CLI.

Correcciones de ESTA revisión:

1. `check(root, required)` es **ADITIVO**: primero las comparaciones del
   modo tolerante sobre TODAS las métricas medidas (mismas líneas), luego
   las obligaciones de presencia/validez de las exigibles — sin líneas
   duplicadas (una métrica exigida y en rojo aparece UNA vez).
2. Validación de artefacto en la vía exigible: parseo por registro con
   coherencia (0≤LH≤LF, 0≤BRH≤BRF, LF+BRF>0) y rango [0,100] →
   `"<métrica>: medición inválida (<defecto>)"`, texto distinto de ausencia
   y umbral. `lcov_percent`/`coverage_total` actuales quedan INTACTOS para
   el modo tolerante (extrae la variante validada, no la mutes).
3. `_COVERAGE_TOTAL_COMMAND` alineado a la receta del gate (checks.py:73-82):
   añade `-q -m not property` (test 0c ancla la igualdad de tokens).
4. Consolida el test del CLI (elimina el duplicado; aserciones ambas
   clases en el original).

## Paso 3 — Verificación (salida real; sin pipes para exit codes; SIN commit)

```
uv run pytest -q
uv run pytest --collect-only -q
uv run wct accept parse features/wct-premerge-verification-001.feature
uv run wct accept ir-dry  features/wct-premerge-verification-001.feature
uv run wct selftest redteam           # 30/30 · 13 · 13 · 4 · 0 · 0 SIN CAMBIOS
uv run wct gate --tier fast           # 7/7
uv run wct gate --tier commit         # 21 gates: G-INTROVERT PASS + SOLO G-META-1 rojo (pre-bless, repórtalo así)
uv run wct ratchet check              # idéntico a hoy
uv run wct ratchet check --require all   # denominador; bloquea nombrando lo no medible
ruff format/check --config governance/lint/ruff.toml <frontera>
```

Coste (PRESUPUESTO.md): ≥3 reps de `--tier commit` post-cambio; el coste
de G-INTROVERT sale de su `duration_ms` en el reporte del gate —
decláralo como medido así.

## No hacer

- NO commitees, empujes ni abras PR (encargo explícito).
- NO toques baselines ni presentes un scan vacío como mutación del
  harness: reporta `wct mutate run` tal cual responda.
- NO agregues claims de frescura ni guard de mtime.
- NO cambies la lógica del analyzer ni el modo tolerante.
