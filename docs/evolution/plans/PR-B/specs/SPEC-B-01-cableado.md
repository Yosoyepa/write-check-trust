# SPEC-B-01 — Cableado configuración → runtime

ADRs: [B-01](../decisions/ADR-B-01-umbrales-declarados-a-runtime.md),
[B-02](../decisions/ADR-B-02-nuevas-claves-y-doctor.md) · Escenarios:
[GHERKIN-B.md](../GHERKIN-B.md).

## Paso 0 — Verificación previa del coder (documentar en handoff)

1. Confirmar las claves exactas y valores actuales en governance/thresholds.yaml
   para: `crap.changed_max`, `coverage.diff_min`,
   `dead_code.vulture_min_confidence`, `complexity.xenon_max_{absolute,modules,average}`,
   `dry.min_lines`, `dry.min_nodes` (el ANALYSIS fue verificado en `ee17288`).
2. Leer `gate_coverage_diff` y `gate_coverage_total` (patrones dinámicos A2) y
   el house-style de `checks.py` (dónde viven las construcciones).
3. Capturar los comandos ACTUALES de G-CRAP, G-COV-DIFF, G-DEAD, G-CC y la
   invocación de G-DRY-TPL (salida de un `wct gate --tier pr` o invocación
   directa REGISTRY) — son los fixtures de regresión byte-idéntica.

## Cambios

### 1. `governance/thresholds.yaml` (protegido; autorizado por este plan)

Aplicar el diff EXACTO de ADR-B-02 §1 (4 claves nuevas con comentarios de
procedencia). Sin tocar ningún valor existente.

### 2. `tools/wct/gate/checks.py` — constructores dinámicos

Funciones constructoras (patrón `coverage_total_command` de A2), una por gate,
cada una leyendo su clave vía `load_config` y fallando con la clave nombrada
si falta/ilegible:

- `crap_command(root)` → `["crap4py", "src", "--lcov", "build/coverage/lcov.info", "--max-crap", str(th["crap"]["changed_max"])]`
- `coverage_diff_command(root)` → el comando actual de gate_coverage_diff con `--fail-under str(th["coverage"]["diff_min"])`
- `dead_code_command(root)` → `["vulture", "src", "tools/wct", "--min-confidence", str(th["dead_code"]["vulture_min_confidence"])]`
- `cognitive_command(root)` (G-CC/xenon) → flags actuales con los tres valores de `complexity.xenon_max_*`
- `dry_tpl_params(root)` → dict con `min_lines`/`min_nodes`/`template_threshold` desde `dry.*` (para el gate G-DRY-TPL y/o `wct dry --normalized` según Consumidor actual — paso 0.3 define la frontera exacta: si G-DRY-TPL es función dinámica que llama al engine, los params se inyectan ahí. **La frontera de reparto entre coders la congela [DoD.md](../DoD.md): la inyección dry va por el engine (parámetros con default desde config), NO por checks.py** — así W1 y W2 quedan disjuntos)

### 3. `tools/wct/gate/runner.py` — registro

Reemplazar las entradas `external()` estáticas de G-CRAP, G-DEAD, G-CC y la
construcción interna de gate_coverage_diff por las funciones dinámicas que
usan los constructores. runner.py NO crece (los constructores viven en
checks.py); si G-SIME… G-SIZE salta, aplicar partición TEST-007 como en A2.

### 4. `tools/wct/dry/tpl.py`, `tools/wct/dry/analyzer.py`, `tools/wct/lcom/engine.py`

- Los literales `DEFAULT_TEMPLATE_THRESHOLD`, `MIN_LINES`, `MIN_NODES`,
  `review_threshold`, `MIN_METHODS`, `LCOM_THRESHOLD` mueren.
- Cada módulo resuelve su valor desde `load_config` con el contrato de
  clave-ausente-falla (KeyError→ValueError con la clave nombrada) o recibe el
  valor como parámetro requerido desde el caller (elige la forma más
  consistente con el house-style de cada módulo y declárala en el handoff).
- OJO: `wct lcom --json` y `wct dry --normalized` (CLIs standalone) también
  consumen estos valores — el cableado debe cubrirlos (mismo loader).

### 5. `tools/wct/doctor/` — sección de conformidad

Sección advisory "Umbrales declarados → gates": lee thresholds.yaml EN VIVO y
lista las 11 claves cableadas (5 existentes + 4 nuevas + las 2 de xenon extra
si se listan por flag) con valor y gate consumidor. Sin lista estática de
valores; la única tabla estática permitida es el MAPA clave→gate (rotaría solo
si se cablea una clave nueva — aceptable y documentado).

### 6. Docs factuales

- `docs/gates.md`: los verificadores citados de G-CRAP/G-DEAD/G-CC/G-COV-DIFF
  pasan a describir la fuente (thresholds.yaml → flag).
- `docs/runbook.md`: si documenta cómo subir un umbral, conectar con el flujo
  real (editar thresholds.yaml + bless).

## Tests TDD (rojo primero; nombres propuestos)

1. `tests/unit/test_gate_config_wiring.py::test_gate_commands_match_current_literals`
   — con el YAML REAL del repo: los comandos construidos de G-CRAP, G-DEAD,
   G-CC y G-COV-DIFF son idénticos a los capturados en paso 0.3 (regresión
   byte-idéntica).
2. `...::test_yaml_change_flows_into_command` — fixture repo (project_factory)
   con `crap.changed_max: 9` → `--max-crap 9` (el camino no contiene "6").
3. `...::test_missing_key_fails_naming_it` — fixture sin `coverage.diff_min`
   → G-COV-DIFF FAIL cuyo summary nombra `coverage.diff_min`.
4. `tests/unit/test_dry_config.py::test_template_threshold_declared_and_consumed`
   — `dry.template_threshold` existe en el YAML, y `analyze_template` usa ese
   valor (fixture con 0.5 detecta/unifica según semántica actual — asertir
   contra comportamiento observable, no contra el atributo).
5. `tests/unit/test_lcom_config.py::test_lcom_thresholds_declared_and_consumed`
   — ídem con `lcom.min_methods`/`lcom.threshold` (una clase fixture de 2
   métodos no se evalúa; LCOM4 2 con threshold 2 cuenta).
6. `tests/unit/test_doctor_conformance.py::test_doctor_lists_wired_thresholds`
   — la salida de doctor contiene la sección con ≥11 pares clave→gate y los
   valores del YAML vigente.
7. `...::test_doctor_section_reads_live_yaml` — fixture con valor distinto →
   doctor refleja el valor del fixture (no estático).

## No hacer

- No consumir `crap.profiles` (ADR-B-01 alternativa rechazada).
- No tocar `mutation.*` operativos, `budgets_seconds`, policy.yaml huérfanas.
- No cambiar NINGÚN valor existente de thresholds.yaml (solo las 4 adiciones).
- No añadir defaults silenciosos: clave ausente = gate rojo con nombre.

## Commits

`feat(gate): los gates consumen los umbrales declarados` ·
`feat(config): cuatro constantes runtime se declaran en thresholds.yaml` ·
`feat(doctor): sección de conformidad declarado→runtime` (+ docs donde toquen).
