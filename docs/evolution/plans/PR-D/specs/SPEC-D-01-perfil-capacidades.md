# SPEC-D-01 — Perfil de capacidades y resumen honesto (Coder-D1)

ADRs: [D-01](../decisions/ADR-D-01-perfil-derivado.md).
Escenarios: [GHERKIN-D.md](../GHERKIN-D.md) (wct-capability-profile-001).

## Paso 0 (documentar en handoff)

1. Para cada gate de REGISTRY con herramienta externa: verificar qué
   ejecutable resuelve y qué scope REAL escanea (lee el builder del
   comando — p. ej. `dead_code_command` escanea `src tools/wct`;
   G-INTROVERT analiza `policy.paths.tests`; G-COV lee la selección de
   pyproject). Documenta la tabla gate → tools → scope que vas a declarar.
2. Mapear cómo `overview()` consume `TIERS` y qué forma tiene la salida
   actual de `wct report` (JSON) — el perfil es aditivo.

## Cambios

### 1. `tools/wct/gate/runner.py` — metadatos en el constructor

- `dynamic()` estampa en el gate: `tools` (tupla con el ejecutable) y
  `scope` (parámetro nuevo, default `()`), junto con el `gate_id` que ya
  conoce. `external()` propaga igual (delega en dynamic).
- Helper tipado `gate_info(gate) -> GateInfo | None` que lee los
  metadatos estampados (dataconse `GateInfo: tools, scope`) — el stamping
  vive encapsulado ahí, sin getattr dispersos.
- En los sitios de construcción de REGISTRY, declara el `scope` verificado
  en el paso 0 para cada gate que escanea rutas (p. ej. G-DEAD
  `("src", "tools/wct")`, G-INTROVERT `("tests",)`, G-DEPS los caminos de
  su comando). Los gates sin archivos (G-META-*) no declaran scope.

### 2. `tools/wct/report/overview.py` — capabilities

- Sección nueva `"capabilities"` en el dict de `overview()`: por gate (en
  orden estable): `{gate, tools: [...], present: bool, scope: [...],
  tiers: [...]}` — `present` vía `shutil.which` EN TIEMPO DE REPORT;
  `tiers` derivado de `TIERS`. Gates sin herramienta externa:
  `tools: [], present: true`.
- La sección debe permitir a un auditor externo responder "si corro full
  aquí, ¿qué no se verifica y por qué".

### 3. `tools/wct/report/render.py` — resumen honesto

- `text_report`: cuando `skipped > 0`, línea adicional después del
  resumen: `capacidades no verificadas: {skipped} — wct report muestra
  herramientas ausentes`. `skipped == 0` → sin línea extra (salida de los
  tiers verdes NO cambia byte a byte — verifica con el test).

## Tests TDD (rojo primero) — `tests/unit/test_report_profile.py`

1. `test_every_gate_with_external_tool_exposes_it` — para todo REGISTRY:
   si el gate corre un ejecutable, `gate_info` devuelve tools con él.
2. `test_capabilities_report_tool_presence[F-*]` parametrizado — con
   `which` real o falseado: presente → `present: true`; ausente →
   `present: false` Y el gate aparece en la sección.
3. `test_capabilities_declare_scope` — los gates del paso 1 reportan el
   scope declarado (traza al constructor, no a una tabla duplicada).
4. `test_full_summary_declares_unverified_capabilities` — render con un
   resultado SKIP → la línea aparece; sin SKIPs → idéntico al render
   actual (regresión byte a byte).
5. `test_overview_capabilities_json_shape` — la sección es JSON
   serializable con la forma documentada (auditoría externa, O-001).

## No hacer

- No tocar `tools/wct/gate/checks.py`, `accept/`, `selftest/`,
  `pyproject.toml`, `governance/**` (frontera de D2 y del arquitecto).
- No convertir el perfil en gate bloqueante (informa, no bloquea).
- No declarar scopes en YAML/config (ADR-D-01 alternativa (a) rechazada).
- No cambiar la semántica de bloqueo de SKIP (ADR-A1-03 se mantiene).

## Commit

`feat(report): perfil de capacidades derivado y resumen honesto del tier`
— cuerpo explicando fuente única y O-006. Byline `By coder.`
