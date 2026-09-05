# SPEC-C-01 — Conversión del red team a ejecución productiva

ADRs: [C-01](../decisions/ADR-C-01-modelo-de-ejecucion.md),
[C-02](../decisions/ADR-C-02-residuos-declarados.md) · Escenarios:
[GHERKIN-C.md](../GHERKIN-C.md).

## Paso 0 — Verificación previa (ambos coders, documentar en handoff)

1. **R1**: para cada motor engine (dry.analyzer, introvert.analyzer,
   ratchet.engine.suppression_count, mutate.engine.mutation_sites,
   archmetrics cycle/metrics): leer su firma y qué estructura/config espera
   (¿lee policy.yaml? ¿requiere src/example layout?); elegir el fixture
   mínimo por caso y documentarlo.
2. **R1**: capturar salida actual de `wct selftest redteam` (baseline de
   runtime y conteos).
3. **R2**: para cada gate-tool: identificar la función productiva a invocar
   (REGISTRY[gate] o la función interna que referencia) y su contrato de
   entrada (root con qué estructura mínima); documentar por caso.

## Cambios — R1 (framework + 10 engine)

### 1. `tools/wct/selftest/redteam.py` (reescritura del runner)

- Despachador por `harness` (ADR-C-01 §1). Carga los tres YAML (unión) y
  tolera archivos ausentes. Invariario de modos sobre la unión.
- `heuristic` mantiene `_reject` actual (solo con los 4 casos residuales:
  testless/hardcoded/survivor — los reconocedores de los convertidos mueren).
- Resumen por arnés + SKIP visibles con herramienta ausente (ADR-C-01 §4).
- `run(root)` conserva la firma `(count, failures)` que usa `cli.py` — el
  CLI no cambia.

### 2. `tools/wct/selftest/fixtures_engine.py` (nuevo)

Builders por caso (id → función(tmp_path) → root del fixture con el defecto
plantado), según la tabla ANALYSIS §2. El archivo de >100 sitios de F5-a se
genera programáticamente (determinista).

### 3. `quality/redteam/cases-engine.yaml` (nuevo)

Los 10 casos con `harness: gate-engine`, `engine:` (ruta importable),
`expect:` (condición de caza, p.ej. `candidates>=1`), y el resto de campos
actuales. `payload` muere en estos casos (el fixture ES el payload).

### 4. `quality/redteam/cases.yaml` (cirugía, solo R1)

Quedan 8 casos: 4 hook (`harness: hook`, sin cambios de fondo) + 4
residuales (`harness: heuristic` + comentario de razón de ADR-C-02). Los 22
líneas convertidas se eliminan.

## Cambios — R2 (12 tool)

### 5. `tools/wct/selftest/fixtures_tools.py` (nuevo)

Builders por caso (tabla ANALYSIS §2 gate-tool): árboles mínimos por caso
(p.ej. domain/x.py importando sqlalchemy para F8-a).

### 6. `quality/redteam/cases-tool.yaml` (nuevo)

12 casos con `harness: gate-tool`, `gate:` (existente), `expect:` (FAIL o
findings no vacíos según el gate), `tool:` (herramienta requerida).

### 7. SKIP honesto en el runner — coordinado

La LÓGICA de SKIP la escribe R1 en el runner (herramienta ausente → caso a
lista de skips, no a failures ni a rechazados). R2 solo declara `tool:` por
caso. R2 verifica el comportamiento con la herramienta DESINSTALADA vía
PATH manipulado (monkeypatch de shutil.which en tests; no desinstalar nada
del entorno real).

## Tests TDD (rojo primero)

**R1** (`tests/unit/test_redteam_engine.py`):
1. `test_engine_case_catches_planted_defect[F1-a]`… parametrizado ×10: cada
   builder planta su defecto y el motor productivo lo reporta (la aserción
   traza al motor, no al despachador).
2. `test_runner_dispatches_by_harness` — caso engine→engine invocado, caso
   hook→pre_tool_use, caso heuristic→_reject (con dummies en tmp).
3. `test_mode_invariant_on_union` — archivos parciales respetan ≥2 por modo
   sobre la unión; un archivo ausente no rompe.
4. `test_summary_counts_by_harness` — salida con conteos separados y skips
   listados.
5. `test_isolated_tmpdirs` — dos casos no comparten root.

**R2** (`tests/unit/test_redteam_tools.py`):
6. `test_tool_case_catches_planted_defect[...]` parametrizado ×12 — SOLO
   ejecutable si la herramienta está presente: `pytest.importorskip`-style
   por herramienta (o skipif shutil.which) — el skip del TEST es honesto y
   no cuenta como verde del caso.
7. `test_absent_tool_reports_visible_skip` — con which() falseado: el caso
   va a skips con la herramienta nombrada; failures y rechazados no crecen.

## No hacer

- No convertir los 4 residuos (ADR-C-02).
- No añadir casos nuevos ni tocar F14/F15 más allá del relabeling.
- No paralelizar la ejecución (runtime medido primero; si duele, PR propio).
- No tocar governance/** ni pyproject.toml.
- Si un motor productivo NO caza el defecto plantado (falso negativo real):
  dejar el caso en rojo, reportarlo en el handoff con la salida — NO ajustar
  el fixture hasta que pase (ADR-C-01 §5). El arquitecto decide: defecto del
  motor → issue; expectativa irreal → ajuste documentado como propuesta.

## Commits

R1: `feat(selftest): red team ejecuta engines productivos sobre fixtures` ·
`refactor(selftest): cases.yaml queda con hook+residuos declarados`
R2: `feat(selftest): 12 casos cazan con las funciones de gate reales`
