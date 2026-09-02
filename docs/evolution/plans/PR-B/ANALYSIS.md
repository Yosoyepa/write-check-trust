# ANALYSIS — PR-B: evidencia e inventario

## 1. Sitios verificados en `ee17288` (hardcoded con equivalente declarado)

| Sitio (archivo:línea) | Literal | Clave declarada en thresholds.yaml |
|---|---|---|
| `tools/wct/gate/runner.py:402` | `--max-crap 6` | `crap.changed_max: 6` |
| `tools/wct/gate/runner.py:159` | `--fail-under 90` (diff-cover) | `coverage.diff_min: 90` |
| `tools/wct/gate/runner.py:374` | `--min-confidence 80` | `dead_code.vulture_min_confidence: 80` |
| `tools/wct/gate/runner.py:408+` | xenon `B`,`A`,`A` | `complexity.xenon_max_absolute: B` / `xenon_max_modules: A` / `xenon_max_average: A` |
| `tools/wct/dry/tpl.py:19-20` | `MIN_LINES=4`, `MIN_NODES=20` | `dry.min_lines: 4`, `dry.min_nodes: 20` |

Riesgo concreto que este cableado elimina: cambiar `crap.changed_max` en el
YAML (con bless, como manda su cabecera) no cambia hoy ningún gate. El archivo
instruye un procedimiento que no tiene efecto — peor que no existir.

## 2. Constantes runtime SIN clave declarada (4)

| Sitio | Literal | Clave nueva propuesta |
|---|---|---|
| `tools/wct/dry/tpl.py:18` | `DEFAULT_TEMPLATE_THRESHOLD = 0.90` | `dry.template_threshold: 0.90` |
| `tools/wct/dry/analyzer.py:125` | `review_threshold = 0.95` | `dry.review_threshold: 0.95` |
| `tools/wct/lcom/engine.py:16` | `MIN_METHODS = 3` | `lcom.min_methods: 3` |
| `tools/wct/lcom/engine.py:17` | `LCOM_THRESHOLD = 2` | `lcom.threshold: 2` |

## 3. Inventario de claves declaradas SIN consumidor (insumo Horizonte 0)

Verificado contra `ee17288`; se lista completo para la decisión de
activar/deprecar/retirar que el roadmap asigna al Horizonte 0 — PR-B NO las
toca:

- **policy.yaml**: `project.*` (name, language, secondary_languages,
  python_requires, package_manager), `lint_profile`, `paths.features`,
  `paths.build`, `paths.generated`, `architecture.unsuitable_for_test`.
- **thresholds.yaml**: `crap.profiles` (ver ADR-B-01 §alternativas),
  `coverage.branch`, `coverage.total_is_ratchet` (semántica ya implementada de
  hecho en A2; la clave sigue sin lector — candidata a consumirse en el doctor
  de conformidad o retirarse), `complexity.max_cc_per_function`,
  `mutation.{max_workers, differential, max_survivors_changed,
  timeout_per_mutant, engine}`, `acceptance.*`, `introvert.*`, `debt.*`,
  `dead_code.*` (salvo min_confidence), `dependencies.*`, `docs.*`,
  `budgets_seconds.*`, `dry.coverage_matrix_guard`.

## 4. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Gates externos se vuelven dinámicos → complejidad nueva en runner.py (500 LOC exactos tras A2) | La construcción de comandos vive en `checks.py` (patrón A2); runner.py solo registra y ejecuta. Si G-SIZE salta de nuevo, partición TEST-007 — el backlog ya trae la extracción del módulo de gates subprocess |
| YAML corrupto/clave faltante en runtime | El loader es la única fuente; clave ausente → el gate falla declarando la clave esperada (mismo contrato que G-COV-TOTAL con su baseline en A2: nunca corre con valor por defecto silencioso) |
| Comportamiento cambia por error de cableado (p.ej. leer otra clave) | Los tests asertan el round-trip: fixture YAML con valor DISTINTO al actual → el comando lo refleja; y con los valores reales → comandos idénticos a los de hoy (regresión) |
| thresholds.yaml editado (4 claves nuevas) | ADR-B-02 con diff exacto + tu aprobación del plan + bless; las claves nuevas replican los valores actuales de los literales: cero cambio de comportamiento |
| doctor muestra estado viejo | La sección de doctor lee thresholds.yaml en vivo, sin lista estática |

## 5. Predicciones falsables

- Los comandos de G-CRAP/G-COV-DIFF/G-DEAD/G-CC/G-DRY-TPL son byte-idénticos a
  los actuales con el YAML vigente (regresión) y cambian si el fixture YAML
  cambia (efecto).
- Suite, tiers fast/commit/pr, red team y aceptación: sin cambios de estado
  (solo G-META-1 rojo por governance+tools sin bless).
- `wct doctor` muestra la sección de conformidad con ≥9 claves → gate.
