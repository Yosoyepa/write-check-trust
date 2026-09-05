# ANALYSIS — PR-D: evidencia y factibilidad

## 1. Evidencia (verificada contra `87c562c`)

### O-006: capacidades ausentes y scopes

- `tools/wct/report/overview.py:24-32` — `wct report` ya clasifica reglas
  (automated/human_only/unknown) y expone `policy.gates.optional_tools`,
  pero NO dice qué gate requiere qué herramienta, ni si está presente en
  este entorno, ni qué scope escanea. Un auditor externo no puede derivar
  "qué significa full verde aquí" del report.
- `tools/wct/gate/runner.py:85-123` — `dynamic(gate_id, executable,
  builder, ...)` YA conoce el ejecutable que cada gate necesita (lo
  resuelve con `shutil.which` en su cierre, línea 102) y `external`
  (línea 121) delega en él. El dato existe; no está expuesto.
- `tools/wct/report/render.py:20-24` — el resumen cuenta SKIP aparte
  (ADR-A1-03) pero no dice qué SON: "7 PASS · 1 SKIP · 0 FAIL" no distingue
  "herramienta ausente" ni remite al perfil.
- Scopes: `G-DEAD` escanea `src tools/wct` (`checks.py:145`), `G-COV`
  cubre `src + tools/wct` (pyproject, PR-A2), `G-MUT` solo `src/example`
  (selección de mutación en pyproject), `G-INTROVERT` solo `tests/`. Cada
  gate lo sabe; ningún lugar lo declara. El criterio de salida
  "scopes explícitos" exige que el perfil los reporte desde una sola
  fuente.

### F11-b: sonda vulture@60 (2026-09-05, main)

`uv run vulture src tools/wct --min-confidence 60` → **exactamente 1
hallazgo** en todo el repo: `tools/wct/archmetrics/analyzer.py:24: unused
variable 'abstract_symbols' (60% confidence)`. Es un **falso positivo**:
campo del dataclass `PackageMetric` consumido vía `dataclasses.asdict()`
(analyzer.py:26-27) — reflexión que vulture no ve. Muerte real a
confianza 60: **cero**.

Coste de la redención: umbral 60 + whitelist de 1 entrada; los hallazgos
netos quedan en 0 y la baseline del ratchet dead-code NO cambia (no se
necesita `ratchet record`). Beneficio: la clase de adversarios
función/constante/atributo muerto (confianza 60) pasa a ser cazada — el
hueco que F11-b declaraba desde PR-C.

### ruff desnudo (footgun documentado por el coder de PR-C)

`pyproject.toml` NO tiene sección `[tool.ruff]`; `ruff check` sin
`--config governance/lint/ruff.toml` aplica otro ruleset. Repro del
handoff PR-C: `uv run ruff check tools/wct/gate/checks.py` (archivo intacto
desde main) reporta I001; el comando autoritativo del repo pasa limpio.
Cualquier agente que corra ruff desnudo recibe hallazgos falsos o
formatea con settings distintos.

### Artefacto de aceptación con ruta absoluta (bug que mordió en PR-C)

`tools/wct/accept/pipeline.py:139-156` — `generate()` embebe el IR como
JSON en `tests/acceptance/generated/test_acceptance.py`; el IR viene de
`parse_feature(feature)` con la ruta ABSOLUTA del feature
(`"source": "/home/.../features/example.feature"`). Durante PR-C, correr
el pipeline desde el worktree regeneró el artefacto con la ruta del
worktree y ensució el árbol (diff real observado: solo el campo `source`
cambiaba). El artefacto generado no es reproducible entre checkouts.

## 2. Factibilidad

| Cambio | Mecanismo | Riesgo |
|---|---|---|
| Capabilities en report | `dynamic()`/`external()` estampan `tools`/`scope` en el gate; `overview()` las agrega con presencia vía `shutil.which` y tiers vía `TIERS` | bajo — aditivo al JSON |
| Resumen honesto | `render.text_report` añade línea solo si `skipped > 0` | bajo — no cambia semántica de bloqueo |
| vulture 60+whitelist | `dead_code_command` añade `--whitelist` cuando `dead_code.whitelist` existe en thresholds (patrón PR-B: clave declarada); whitelist = 1 archivo python con el nombre del campo | medio-bajo — verificar hallazgos netos 0 |
| F11-b a gate-tool | fixture con thresholds propios (confianza 60) + constante muerta; patrón F1-b/F11-a de PR-C | bajo |
| ruff extend | `[tool.ruff] extend = "governance/lint/ruff.toml"` en pyproject | bajo — el comando con `--config` sigue idéntico |
| Artefacto relativo | `parse_feature` normaliza `source` a ruta relativa al root cuando es derivable; regenerar el artefacto con la herramienta | bajo — tests de estabilidad entre dos roots |

## 3. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| vulture@60 destapa hallazgos nuevos al tocar herramientas/archivos | la sonda ya midió main: 1 FP neto; la whitelist lo cubre; si aparecen más durante la PR son muerte REAL y se arregla, no se whitelist |
| Stamping de atributos en closures queda frágil | helper tipado `gate_info(gate)` con `getattr` documentado; tests fijan que todo gate de REGISTRY expone tools (los que tienen) |
| extender ruff desde pyproject cambia el comportamiento del comando con `--config` | no debe: `extend` solo aporta cuando NO se pasa `--config`; test de equivalencia |
| regenerar el artefacto de aceptación toca un archivo generated | regeneración SOLO vía `wct accept generate` (TEST-009); el diff debe mostrar únicamente la ruta relativa |

## 4. Rollback

Cuatro commits independientes (perfil, resumen, redenciones, artefacto);
cada uno revertible por separado. Sin cambios de umbrales más allá de
`dead_code.vulture_min_confidence` (80→60 documentado en ADR-D-02) y una
clave nueva `dead_code.whitelist`.

## 5. Hallazgo preexistente (destapado por la verificación de D2, 2026-09-05)

`wct ratchet check` sobre main limpio (`87c562c`): `dry-template-clusters:
actual=16, baseline=9` — la baseline se sembró el 2026-08-23 y los clones
de plantilla en `tools/wct` crecieron (β-1→PR-C) sin que nadie corriera
el tier full, único donde vive G-DRY-TPL (`runner.py:477`). Ningún tier de
CI lo ejecuta: el rojo era invisible. Disposición: registrar la realidad
con `ratchet record` humano en el bless de esta PR (razón citando la
deuda), archivar la deduplicación como PR propio, y esta PR añade el tier
full a su matriz de verificación para que no vuelva a esconderse.
