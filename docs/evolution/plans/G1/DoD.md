# G1 — Definition of Done, por incremento con criterios independientes

G1 NO está "completo" al cerrar G1a: los claims de frescura/completitud/
causa son de G1b, y selección/scope son H0/H1. Tras G1a, F01/F02 quedan
parcialmente cerrados (recepción/clasificación sí; lo demás declarado
abierto en el diagnóstico del propio gate).

## G1a — Recepción y clasificación (SPEC-G1a-1)

- [ ] Adaptador run → `results --all true` → clasificación completa con
      precedencia ERROR>FAIL conservando identidades; retorna GateResult
      (sin tipo nuevo); versión de mutmut en el diagnóstico.
- [ ] Los 10 estados + renglones inválidos clasificados según ADR-G1-01;
      run-fail = FAIL "ejecución no completada" (sin etiqueta producto);
      SKIP conservado.
- [ ] Control sano de PR-E extendido con inventario (RG01), NO duplicado.
- [ ] RG02/03/04/08/09 en verde con la atribución de evidencia correcta
      (dobles solo donde TEST-MATRIX los etiqueta).
- [ ] CLI: exit 0/1/2 + diagnóstico `estado:`/`fase:`/`identidades:`
      probado por SUBPROCESS sobre micro-repo sin manifiesto del repo.
- [ ] Redteam 30/30 · 13 · 13 · 4 · 0 · 0 SIN cambios; fast 7/7; commit
      solo G-META-1 rojo (bless propio, no el de #36).
- [ ] Feature `wct-mutation-verdict-001` verbatim de GHERKIN-G1.md §G1a
      (aprobada por el humano ANTES del código); parse + ir-dry limpios;
      cada escenario enlazado a un nodeid recolectado (no basta parse).
- [ ] Presupuesto exploratorio reportado (muestras declaradas); el
      emparejado definitivo NO se afirma — es gate de G1b (RG12).
- [ ] EVIDENCE.md actualizado con las corridas de verificación del coder.

## G1b — Pertenencia, completitud y causa (SPEC-G1b-1, BLOQUEADO)

Desbloqueo: G1a fusionada + ADR-G1-02/04 aprobados + Gherkin §G1b aprobado
+ RG12/13 medidos y aprobados. Criterios de hecho (nada cumplido hoy):

- [ ] RG07: tests debilitados conservando llamadas → gate y CLI reflejan
      tests actuales (repetición pública literal del alcance).
- [ ] RG05: exit 3 separado de exit 1 vía lector versionado (esquema
      divergente → ERROR, nunca dependencia accidental).
- [ ] RG06: pérdida parcial → ERROR por divergencia esperado/recibido —
      o requisito declarado ABIERTO por el humano con límite visible.
- [ ] RG10 (versión), RG11 (concurrencia/symlinks), RG13 (invalidación
      completa incl. stats) con pruebas etiquetadas.
- [ ] Presupuesto emparejado (≥3 repeticiones, mediana/rango, por consumidor)
      aprobado ANTES de obligar repetición en tiers.
- [ ] Una sola política certificada (sin `fresh=False`); delta cero
      sigue informativo (RG08) y re-probado.

## Unidad de revisión (ambos incrementos)

- [ ] Verifier independiente (PROC-005) reproduce los controles clave
      (sano, timeout, inyección etiquetada, CLI subprocess).
- [ ] Diff staged archivo por archivo (sin `git add -A`); frontera del
      SPEC respetada; sin governance/pyproject/redteam/workflow.
- [ ] Ningún mensaje del código afirma frescura/causa en G1a.
