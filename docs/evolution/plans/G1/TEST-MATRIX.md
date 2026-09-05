# G1 — Matriz de tests: M (POST-PR36) + RG (REVIEW-G1) por incremento

Estado por requisito: **plan** (especificado, sin código) · **continuo**
(ya cubierto por suite/redteam existentes) · **bloqueado** (requiere gates
de SPEC-G1b-1). Nada abajo está "implementado" ni "medido" por este
dossier; la evidencia existente está tipificada en EVIDENCE.md.

## Requisitos RG (REVIEW-G1 §matriz adicional obligatoria)

| ID | Caso | Incremento | Evidencia actual | Prueba |
|---|---|---|---|---|
| RG01 | control sano de PR-E sigue PASS y se AMPLÍA con inventario | G1a | [continuo] `test_clean_tree_passes_with_zero_survivors` (test_gate_mutation.py:57) | `test_clean_tree_cites_inventory` (extensión) |
| RG02 | results-error tras run sano → ERROR por la fase real (doble EXPLÍCITO) | G1a | [I]+[O] P4a/b standalone; secuencia completa NO demostrada | `test_results_failure_after_healthy_run_is_error` |
| RG03 | killed+timeout+survived → ERROR prioritario sin perder FAIL | G1a | [O] P8 (timeout real); mezcla con survived por doble etiquetado | `test_mixed_survived_and_timeout_error_preserves_findings` |
| RG04 | línea desconocida/ID duplicado/truncado → diagnóstico, no PASS | G1a | diseño (nadie lo produce hoy) | `test_duplicate_identity_and_unknown_line_error` |
| RG05 | exit bruto 1 vs 3, ambos "killed" | **G1b** | [L] colapso en __main__.py:82-104 | bloqueado (ADR-G1-04) |
| RG06 | meta parcial perdido entre fases → divergencia detectada | **G1b** | [L] load tolera FileNotFoundError (data.py:112) | bloqueado (denominador independiente) |
| RG07 | tests debilitados (mismo código) → evaluación refleja tests actuales | **G1b** | [O] P5bis (falla hoy) + [O] D3 (la repetición lo resuelve) | bloqueado con G1b |
| RG08 | delta cero → mensaje explícito, sin claim | G1a | [L] engine.py:173-175 | `test_cli_delta_zero_informs_without_quality_claim` |
| RG09 | CLI por subprocess con delta: exit 1 + diagnóstico/IDs | G1a | [plan] fixture micro-repo sin manifiesto | `test_cli_subprocess_delta_reports_ids` |
| RG10 | tool ausente → SKIP (sin cambio); versión no soportada → error versionado | G1a (SKIP) / **G1b** (versión) | [continuo] SKIP mutation.py:43 | G1a: conservado; G1b: bloqueado |
| RG11 | concurrencia/symlink → no borrar ni mezclar datos de terceros | **G1b** | sin diseño ejecutado | bloqueado (ADR-G1-02 §concurrencia) |
| RG12 | frío/caliente emparejado → costo y re-ejecutados medidos | **G1b** (exploratorio en G1a) | 1.8 vs 1.9 s RETIRADO como evidencia (no emparejado) | plan de medición en SPEC-G1a-1 paso 3 |
| RG13 | cambio solo tests/config/asociación → sin evidencia ajena | **G1b** | [O] D3 parcial (re-ejecuta bajo tests actuales) | bloqueado (incl. stats/caches) |

## Requisitos M (POST-PR36 PLAN) — estado tras reconciliación

| ID | Estado | Nota |
|---|---|---|
| M01a run fallido → FAIL con fase | G1a | causa "ejecución no completada", sin etiqueta producto (D2) |
| M01b results fallido → ERROR fase results | G1a | = RG02 |
| M02 todos killed + results vacío → PASS con inventario | G1a | PASS **limitado** (claim); = RG01 ampliado |
| M03 survived/no tests → FAIL con identidades | [continuo] | PR-E + redteam F2-b/F5-b; G1a lo preserva |
| M04 timeout/desconocidos/no ejecutados → no PASS | G1a | = RG03/RG04 |
| M05 artefacto de otra revisión → invalidar/recalcular | **G1b** | política de repetición (ADR-G1-02) |
| M06 selección por función cambiada | **H0** | fuera del incremento |
| M07 tests debilitados sin cambio de fuente | **G1b** | = RG07/RG13 |
| M08 import/constante/borrado/rename | **H0** | fuera del incremento |
| M09 CLI/gate misma corrida | G1a | cuando MIDEN; delta cero informativo (RG08) |
| M10 delta vacío informativo | G1a | = RG08 |

## Controles sanos/defectuosos emparejados (R01)

El PAR existe desde PR-E: sano (RG01, PASS esperado) frente a defectuosos
(survived/no-tests, FAIL esperado — continuo). G1a añade el tercer vértice
que faltaba: **estados de instrumento** (timeout real → ERROR), de modo
que un gate que rechazara todo, otro que aprobara todo y otro que ignorara
estados cada uno falla en al menos un control.

## Fuera de G1 (guardas)

Selección/mapping (M06/M08, H0) · scope tools (H1) · timeout de subprocess
gate-level (G3) · #35 (el Gherkin usa comentarios) · dedup · G2 (aceptación
causal) — sin mezclar.
