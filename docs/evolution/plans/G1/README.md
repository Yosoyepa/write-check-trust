# G1 — Veredicto de mutación íntegro: dossier reconciliado (G1a + G1b)

Fecha: 2026-09-05 (2ª revisión). Estado: **APROBADA por humano (yosoyepa,
2026-09-05): Gherkin §G1a + ADR-G1-01 + ADR-G1-03; ADR-G1-02/04 aprobados
como DIRECCIÓN — G1b sigue bloqueado tras los gates de SPEC-G1b-1**.
Implementación de G1a autorizada bajo SPEC-G1a-1.
Código: `0f80122`. Padres: POST-PR36 (plan G) y REVIEW-G1 (auditoría).
La 1ª versión de este dossier fue corregida por REVIEW-G1; este texto la
SUSTITUYE (los errores corregidos están asentados en EVIDENCE.md §correcciones).

## Recomendación (concreta)

1. **Aprobar G1a** (recepción/clasificación, SPEC-G1a-1): cierra el descarto
   del exit de results y los estados ignorados — hoy hay dos falsos verdes
   E2E medidos (caché P5bis y timeout P8). Claim limitado y honesto: "el
   motor reportó su inventario completo como killed", sin causa ni frescura.
2. **Aprobar los ADR-G1-02/04 como dirección** y dejar G1b BLOQUEADO tras
   sus gates (RG12 presupuesto emparejado, RG13 invalidación, Gherkin §G1b
   propio): frescura por repetición pública literal (demostrada en sonda
   D3), completitud esperado-vs-recibido y causa exit 1/3 por lector
   versionado.
3. **No aprobar nada de H0/H1 aquí**: selección diferencial y scope tools
   siguen detrás de G1b con medición propia.

## Estructura

| Documento | Contenido |
|---|---|
| [ANALYSIS.md](ANALYSIS.md) | Contrato mutmut 3.7.0, evidencia tipificada [O]/[I]/[L]/[INF], diseño G1a/G1b, presupuesto POR MEDIR |
| [EVIDENCE.md](EVIDENCE.md) | Registro durable: sondas, tipos, salidas clave, correcciones fácticas, delimitación de roles |
| [decisions/ADR-G1-01](decisions/ADR-G1-01.md) | Recepción y clasificación (G1a): tabla, precedencia, SKIP, run-fail sin etiqueta producto |
| [decisions/ADR-G1-02](decisions/ADR-G1-02.md) | Frescura = repetición pública literal; NO borrar `.meta`; una sola política certificada (G1b) |
| [decisions/ADR-G1-03](decisions/ADR-G1-03.md) | Un adaptador → GateResult; CLI observable por subprocess; misma política al medir (G1a) |
| [decisions/ADR-G1-04](decisions/ADR-G1-04.md) | Completitud y causa (G1b): lector versionado, esperado/recibido, requisitos BLOQUEANTES |
| [specs/SPEC-G1a-1](specs/SPEC-G1-1.md) | Spec del coder para G1a (ÚNICA implementable; sustituye al SPEC-G1-1 original) |
| [specs/SPEC-G1b-1](specs/SPEC-G1b-1.md) | Spec BLOQUEADA de G1b con sus gates de desbloqueo |
| [GHERKIN-G1.md](GHERKIN-G1.md) | §G1a FINAL (para aprobación; validado parse+ir-dry) + §G1b BORRADOR |
| [TEST-MATRIX.md](TEST-MATRIX.md) | RG01–RG13 y M01–M10 por incremento, con estado plan/continuo/bloqueado |
| [DoD.md](DoD.md) | DoD por incremento con criterios independientes y claims acotados |

## Decisiones que requieren tu aprobación

1. **Gherkin §G1a** (`wct-mutation-verdict-001`): el contrato de
   recepción/clasificación parametrizado (8 escenarios, validado).
2. **ADR-G1-01**: la tabla con precedencia ERROR>FAIL, PASS limitado,
   run-fail = FAIL "ejecución no completada" (compatibilidad PR-E/redteam),
   SKIP conservado, `skipped`/`caught by type check` fuera del contrato
   por política conservadora.
3. **ADR-G1-03**: CLI con exit semántico 0/1/2 y diagnóstico imprimible
   (cambio observable); control sano de PR-E extendido, no duplicado;
   CLI probado por subprocess con micro-repo sin manifiesto del repo.
4. **ADR-G1-02/04 como dirección para G1b** (sin código aún): repetición
   pública literal como política de frescura (borrado de `.meta`
   descartado por defecto) y lector versionado para causa/completitud,
   con los gates de SPEC-G1b-1.

Tras TU aprobación explícita (total o por puntos), el flujo es: handoff a
coder con SPEC-G1a-1, TDD, verifier independiente (PROC-005), PR propia y
bless humano específico — el de #36 no se recicla. Esta solicitud de
revisiones NO aprueba el Gherkin por sí misma.
