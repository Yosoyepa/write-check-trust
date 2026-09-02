# DoD — PR-B: Definitions of Done por unidad de aceptación

El DoD de PR (nivel merge) vive en [VERIFICATION.md](VERIFICATION.md). Este
documento define el DoD de cada unidad que el arquitecto acepta o refuta:
por feature Gherkin, por workstream de coder, por commit y por revisión.
Un workstream no se acepta parcialmente: si un criterio falla, el handoff lo
declara en rojo con su salida y el workstream queda **no aceptado**.

## Reparto entre coders (frontera de archivos, disjunta)

- **Coder-W1 — gates de comando externo**: `tools/wct/gate/checks.py`,
  `tools/wct/gate/runner.py`, `tests/unit/test_gate_config_wiring.py`,
  `features/wct-config-wiring-001.feature`. Cablea crap.changed_max,
  coverage.diff_min, vulture, xenon (4 claves, 6 flags).
- **Coder-W2 — engines + doctor + YAML**: `governance/thresholds.yaml`,
  `tools/wct/dry/tpl.py`, `tools/wct/dry/analyzer.py`,
  `tools/wct/lcom/engine.py`, `tools/wct/doctor/**`,
  `tests/unit/test_dry_config.py`, `tests/unit/test_lcom_config.py`,
  `tests/unit/test_doctor_conformance.py`,
  `features/wct-config-declared-001.feature`,
  `features/wct-doctor-conformance-001.feature`. Cablea dry.min_lines,
  dry.min_nodes, dry.template_threshold, dry.review_threshold, lcom.min_methods,
  lcom.threshold, y la sección de doctor. La inyección al gate G-DRY-TPL va
  por el engine (parámetros con default desde config), NO por checks.py —
  así los archivos quedan disjuntos.

## DoD-F1 — feature `wct-config-wiring-001` (asigna W1)

1. Feature aterrizado en `features/` y `wct accept parse` EXIT=0.
2. Tests en verde, con rojo-primero documentado en el handoff:
   regresión byte-idéntica (comandos actuales capturados en paso 0), fixture
   con valor distinto → flag distinto, clave ausente → FAIL que la nombra.
3. **Cero literales de umbral** en las rutas cableadas: `grep -nE "max-crap.*6|
   fail-under.*90|min-confidence.*80" tools/wct/gate/` no devuelve los literales
   (los valores solo provienen del loader); xenon sin `'"B"'/'"A"'` constantes.
4. Tiers fast/commit sin regresión (solo G-META-1 esperado por tools/wct).
5. Handoff incluye la captura PRE (comandos con literales) y POST (cableados)
   — diff visible por gate.

## DoD-F2 — feature `wct-config-declared-001` (asigna W2)

1. Feature aterrizado y parseando.
2. **El diff de thresholds.yaml es EXACTAMENTE el congelado en ADR-B-02 §1**
   (el arquitecto lo compara contra el ADR antes de aceptar; cualquier valor
   existente tocado = rechazo).
3. Los 6 literales mueren (grep: `DEFAULT_TEMPLATE_THRESHOLD`, `MIN_LINES`,
   `MIN_NODES`, `review_threshold = 0.95`, `MIN_METHODS`, `LCOM_THRESHOLD`
   sin resultados como asignaciones en dry/lcom).
4. Los CLIs standalone (`wct lcom --json`, `wct dry --normalized`) consumen el
   YAML: demostrado con test o con salida en handoff.
5. **Ratchets invariantes**: las salidas de `wct dry --normalized` y
   `wct lcom --json` son idénticas pre/post cableado con el YAML vigente
   (mismos valores, otra fuente). Si `dry-template-clusters` o `lcom-classes`
   cambian de conteo, el cableado alteró semántica — no se acepta.
6. Clave ausente → error que la nombra (contrato ADR-B-01 §3), testeado.

## DoD-F3 — feature `wct-doctor-conformance-001` (asigna W2)

1. Feature aterrizado y parseando.
2. `wct doctor` muestra la sección con ≥11 pares clave→gate, valores leídos
   del YAML en vivo (test con fixture de valor distinto lo demuestra).
3. Doctor sigue siendo advisory: no bloquea, no cambia exit codes existentes.
4. Sin lista estática de valores; solo el mapa clave→gate puede ser estático.

## DoD por commit (ambos coders)

1. Conventional commit + byline `By coder.`
2. Hooks pasados sin `--no-verify` (formato incluido).
3. Cada commit deja el árbol coherente: suite verde en el estado intermedio
   (verificado por el coder y declarado en handoff).

## DoD de la revisión de arquitecto (por workstream)

1. Diff completo leído línea a línea — no se acepta sobre el handoff.
2. Cada criterio del DoD-F correspondiente verificado INDEPENDIENTEMENTE por
   el arquitecto (el coder escribió; el arquitecto verifica — PROC-005).
3. Toda propuesta del coder aceptada/refutada/rechazada **con razón escrita**
   en la respuesta de revisión.
4. Desviaciones del SPEC: ninguna silenciosa; las aceptadas quedan
   documentadas como apéndice del plan.

## DoD de merge (referencia)

El de [VERIFICATION.md](VERIFICATION.md): bless verificado, CI verde,
squash merge, main verificado contra las predicciones falsables
(comandos idénticos, ratchets invariantes, sección doctor presente).
