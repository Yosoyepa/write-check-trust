# ANALYSIS — PR-A1: evidencia, impacto, riesgo

Cada afirmación fue verificada contra `82d686d` en esta sesión con
subagentes de verificación independientes. Nada aquí proviene del dossier
sin re-verificación local.

## 1. Evidencia de los tres defectos

### 1.1 Property tests contaminan las métricas (TEST-008 incumplido)

- La regla exige aislarlos de coverage, mutación, CRAP y aceptación, y marcarlos
  con `@pytest.mark.property` (governance/rules/10-testing.yaml:97-108).
- El marker está declarado en `pyproject.toml:56` **sin ningún uso**: `grep` en
  `tests/` → 0 resultados. El único property test
  (`tests/property/test_inventory_properties.py`, 1 test `@given` de hypothesis)
  no está marcado.
- **Coverage**: G-COV-TOTAL (`tools/wct/gate/runner.py:387-395`) corre
  `pytest --cov --cov-branch --cov-report=lcov:... -q` y resuelve colección por
  `testpaths = ["tests"]` (`pyproject.toml:53`), que incluye `tests/property`.
  El `omit = ["tests/*"]` de coverage excluye los *archivos de test como fuente
  medida*, no su *ejecución*: sus líneas cubiertas en `src/example` sí cuentan.
- **Mutación**: `pytest_add_cli_args_test_selection` (`pyproject.toml:82-88`)
  incluye explícitamente `"tests/property/test_inventory_properties.py"` —
  mutmut corre property tests (con shrinking de hypothesis) por cada mutante:
  costo y no-aislamiento a la vez.
- **Ya aislado por ruta**: G-TEST (`runner.py:328`) corre
  `pytest -q tests/unit tests/integration` — property no corre ahí hoy, pero por
  accidente de rutas, no por contrato. G-PROP (`runner.py:400`) corre
  `pytest -q tests/property` (ejecución dedicada, correcta).

### 1.2 Aceptación aprueba vacíamente con cero mutaciones

- El veredicto es solo `return bool(report["survived"])`
  (`tools/wct/cli.py:311-313`).
- Las mutaciones se generan exclusivamente desde
  `scenario.get("examples", [])` (`tools/wct/accept/pipeline.py:172-194`): un
  feature cuyos escenarios no tienen Examples produce `killed=0, survived=0`
  → exit 0 (PASS) sin advertencia. Un "verde" que no verificó nada.
- Agravante: G-ACCEPT-MUT es `optional=True` (`runner.py:422`) — si el binario
  falta, además se SKIPea en tier pr. Doble superficie de falso verde.

### 1.3 El resumen fusiona PASS con SKIP

- `tools/wct/report/render.py:19-20`:
  `passed = sum(not result.blocking for ...)` → imprime
  `"{passed}/{len(results)} gates no bloqueantes"`. Como SKIP no bloquea
  (`model.py:28-30`), una corrida `28 PASS + 5 SKIP` se reporta idéntica a un
  full-pass `33/33`. La tabla por fila sí muestra la columna STATUS
  (`render.py:16-17`): el defecto está en el agregado, no en la fila.
- El tier full puede terminar verde con gates opcionales ausentes (G-CRAP,
  G-CC, G-DRY-TOK, G-SAST-SEMGREP, G-SBOM: `runner.py:476-486`); el propio
  corte del dossier observó `32 PASS, 1 SKIP` reportado como no-bloqueado.
- Radio de explosión del cambio de formato: `grep "no bloqueantes"` → solo el
  productor (`render.py:20`); **ningún test ni consumidor parsea esa línea hoy**.

## 2. Impacto cuantificado (medido esta sesión)

| Medición | Valor | Comando |
|---|---|---|
| Cobertura total, scope real (`src + tools/wct`), con property | **73 %** (2496 stmts, 604 miss) | `pytest --cov=src --cov=tools/wct --cov-branch -q` |
| Cobertura total, mismo scope, **sin** property | **73 %** (idéntico: 604 miss) | `pytest --ignore=tests/property --cov=... -q` |
| Tests en la suite | 180; sin property 179 | colección |
| Property tests existentes | 1 (`@given`, inventory) | `grep @given tests/property` |
| Consumidores del string de resumen | 0 (solo el productor) | `grep "no bloqueantes"` |

Conclusiones de la medición:

- **A1 no mueve el número de cobertura** (el property test cubre líneas ya
  cubiertas). El 73 % proviene del scope, no de property → A1 aterriza sin
  rojo y PR-A2 puede registrar su baseline bajo la semántica final de A1.
- El riesgo numérico del PR es ~nulo; el riesgo real es de **contrato**
  (ver §3).

## 3. Riesgos y mitigaciones

| Riesgo | Prob. | Mitigación en este plan |
|---|---|---|
| Escenarios existentes quedan vacuos al endurecer el veredicto | Media | Paso obligatorio del spec: enumerar escenarios del manifiesto de aceptación vs Examples ANTES de implementar; los vacíos se parametrizan en el mismo PR (TEST-010 ya lo exige) — ver SPEC-A1-02 paso 0 |
| `-m "not property"` filtra tests que alguien marque por error en tests/unit | Baja | G-TEST también recibe la bandera: el contrato pasa de incidental (rutas) a explícito (marker); tests TDD asertan ambas invocaciones |
| rotura de consumidores del formato de resumen | Baja (medido: 0 consumidores) | Tests del render actualizados en el mismo commit; búsqueda de consumidores repetida en verificación |
| Marker añadido sin exclusión efectiva (falsa sensación de aislamiento) | Baja | Los tests TDD aserten la *invocación construida*, no la presencia del marker aislado |
| Encarecimiento de G-PROP por cambios globales | Nula | G-PROP no recibe banderas de exclusión; tests lo cubren |

## 4. Rollback

Tres commits convencionales independientes (`fix(gate)`, `fix(accept)`,
`fix(report)`); cada uno revertible en solitario. Ningún cambio de
governance/**, ningún manifiesto editado a mano, ningún umbral movido. El
único artefacto compartido es `pyproject.toml` (selección mutmut + nada más),
protegido y cubierto por el bless del PR.

## 5. Trazabilidad

- Defecto 1 → regla TEST-008; oportunidad O-003 (coherencia de scope);
  ADR-A1-01; SPEC-A1-01; Gherkin `wct-prop-isolation`.
- Defecto 2 → regla TEST-010; oportunidad O-004 (aceptación no vacua);
  ADR-A1-02; SPEC-A1-02; Gherkin `wct-accept-nonvacuous`.
- Defecto 3 → oportunidad O-006 (completitud/perfiles, mitad de reporte);
  ADR-A1-03; SPEC-A1-03; Gherkin `wct-skip-honesty`.
- Secuencia: PR-A1 → PR-A2 (scope + baseline 73 % autorizado) → PR-B
  (config→runtime) → PR-C (red team productivo).
