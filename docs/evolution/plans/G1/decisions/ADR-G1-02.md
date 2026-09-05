# ADR-G1-02 — Frescura por repetición pública del alcance; NO borrar `.meta` (G1b)

Estado: **aceptado como DIRECCIÓN** (yosoyepa, 2026-09-05); su
implementación es G1b y sigue BLOQUEADA tras los gates de SPEC-G1b-1
(G1a no la implementa). Sustituye al "fresh=True borra metas" del primer
dossier. Trazabilidad: REVIEW-G1 §5, §6, D3; sonda D3 de EVIDENCE.md.

## Contexto

Sin nombres, mutmut hereda veredictos no-None (`__main__.py:1455`); la
invalidación es por hash de función, no de tests (P5bis: falso verde E2E).
El gate afirma "cero sobrevivientes" — un claim sobre LOS TESTS ACTUALES
que la herencia puede volver falso. El repo principal REPORTA reutilización
(mtimes 09:10 + corrida 1.8 s sin reescritura); la validez con los tests
actuales no está acreditada ni refutada (REVIEW-G1 §3).

## Decisión

**La política de frescura es la repetición pública de todo el alcance con
argumento literal** — `mutmut run` seguido de la re-ejecución explícita del
alcance completo mediante el comodín público (`'*'` pasado como argumento
literal en la lista de subprocess, jamás expandido por shell). Demostrado
[O] en la sonda D3: tras debilitar aserciones conservando llamadas, la
repetición literal re-ejecutó (28.06 mutations/second), re-colectó stats y
volvió `survived` a ambos mutantes — sin borrar un solo artefacto.

- **Una sola política certificada** para gate y CLI (REVIEW-G1 §6): cuando
  se mide, ambos usan repetición completa. `fresh=False` NO existe como vía
  certificada; un futuro modo cache advisory debe ser distinto y explícito,
  nunca el PASS predeterminado.
- **Delta cero** (CLI): salida temprana informativa "sin trabajo
  diferencial", exit 0, sin claim de calidad — y con prueba propia (RG08).
- **No es selección diferencial H0**: el comodín re-evalúa TODO el alcance
  actual del motor; el mapping función→mutante y la invalidación por
  import/config/test-solo (M06/M08/RG13) siguen siendo H0.
- Excepción documentada y acotada a la prohibición de "nombres": G1a-G1b no
  seleccionan subconjuntos; usan el comodín completo del alcance vigente.

## Qué garantiza y qué no (límites honestos)

- Garantiza [O] D3: los mutantes del inventario se ejecutaron con los
  tests/asociaciones de ESTA invocación (stats re-colectados por `collect_
  or_load_stats` en cada `_run`).
- NO garantiza completitud del inventario (pérdida parcial entre fases →
  ADR-G1-04/RG06) ni causa de los killed (exit 3 → ADR-G1-04/RG05).
- Costo: re-ejecución completa del alcance en cada medición. A escala
  actual ≈ costo base (D3: 1.7 s vs 1.4 s, muestra 1, NO emparejado);
  **presupuesto emparejado por medir (RG12)** antes de aprobarlo como
  obligatorio en tiers — la aprobación humana del presupuesto es requisito
  de liberación de G1b.

## Alternativa evaluada y descartada como diseño por defecto

**Borrar `mutants/**/*.meta`** (propuesta original): destruye evidencia del
usuario (gitignore no concede propiedad), carece de contrato de
concurrencia/symlinks/recuperación, y es inconsistente con rechazar leer
el formato interno mientras se borra. Queda registrada solo como último
recurso con autorización humana específica, jamais automática. Otras
alternativas si la pública no alcanzara: workspace de corrida aislado con
entradas explícitas, o invalidación completa soportada por el motor — a
diseñar con medición antes de usar.

## Concurrencia y protección (requisitos G1b, no resueltos aquí)

Repetición concurrente sobre el mismo árbol → aislamiento o rechazo
visible, nunca mezcla (RG11). Escritura/borrado confinados a la raíz
autorizada de la corrida; sin seguimiento de symlinks hacia fuera.
