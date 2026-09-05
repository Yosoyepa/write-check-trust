# ADR-G1-01 — Recepción y clasificación del reporte del motor (G1a)

Estado: **aceptado** (yosoyepa, 2026-09-05). Sustituye a la versión del
primer dossier; trazabilidad: REVIEW-G1 §1, §2, §4, §8 y D1/D2.

## Decisión

`gate_mutation` (y el CLI cuando mide) deriva su veredicto de la secuencia
**run → `mutmut results --all true`**, con esta clasificación:

| Condición (por precedencia) | Gate | CLI | Causa declarada |
|---|---|---|---|
| results fallido/ilegible/formato desconocido | ERROR | 2 | evidencia inválida (fase results) |
| inventario legible VACÍO donde se exige trabajo | ERROR | 2 | no acreditado (fase inventario) |
| identidad duplicada, renglón truncado o estado fuera de vocabulario | ERROR | 2 | evidencia inválida (fase clasificación) |
| timeout / suspicious / not checked / interrupted / segfault / skipped / caught by type check | ERROR | 2 | fuera del contrato de certificación WCT |
| survived o no tests (sin condición ERROR previa) | FAIL | 1 | criterio de mutación incumplido |
| ERROR y FAIL coexistentes | **ERROR** | 2 | con las identidades de FAIL conservadas en details |
| todos killed con inventario aceptable | **PASS limitado** | 0 | clasificación del motor |
| herramienta ausente | **SKIP** (sin cambio) | error explícito, propuesto 2 | compatibilidad; no medición |
| `mutmut run` exit ≠ 0 | **FAIL** | 1 | **"ejecución no completada"** — compatibilidad PR-E/redteam F2-a; NO atribuye defecto de producto |
| delta cero (solo CLI, antes de medir) | n/a | 0 informativo | "sin trabajo diferencial" — no es medición |

Notas de diseño:

1. **Claim limitado de PASS**: "el motor reportó todo su inventario como
   killed". No certifica causa (exit 1 y 3 colapsan a killed,
   `__main__.py:82-104`) ni pertenencia a esta corrida (herencia posible;
   la cierra G1b). El diagnóstico del gate lleva la salvedad cuando aplique.
2. **`caught by type check` y `timeout`** se tratan como fuera del contrato
   por POLÍTICA conservadora de WCT, no como descripción universal del
   estado (pueden ser detecciones terminales legítimas de otro verificador
   o señal útil); certificarlos exige política explícita futura.
3. **No se exige stdout no vacío de results por defecto** (vacío válido
   medido, P1): la ambigüedad la resuelve el inventario `--all true`.
4. **run exit ≠ 0 conserva FAIL** (no ERROR) como compatibilidad temporal
   con el contrato PR-E y el caso redteam F2-a (catch = FAIL). Migrar a
   ERROR es decisión humana explícita que exige actualizar tests/redteam —
   documentada aquí como pendiente, no ejecutada.
5. **SKIP se conserva** para herramienta ausente (estado actual,
   `mutation.py:43`); el primer dossier dijo ERROR por error y queda
   corregido.

## Alternativas rechazadas

- Rechazar stdout vacío de results: rompe el control sano (P1).
- Confiar solo en exit de run: exit 0 con survived y timeout (P2/P8).
- Leer los `.meta` directamente en G1a: acoplamiento a formato interno; el
  lector versionado es decisión de G1b (ADR-G1-04) con compatibilidad
  explícita, no una lectura incidental.
- Parsear la barra de progreso del run: formato de spinner no contractual.

## Consecuencias

- Inventario con timeouts (P8) pasa de PASS falso a ERROR con identidades.
- Corridas que hoy pasan con estados fuera del contrato pasarán a ERROR:
  correcto y visible; el diagnóstico nombra estado, conteo y versión.
- Los casos redteam F2-a (run-fail→FAIL), F2-b/F5-b (survived→FAIL)
  permanecen intactos: la precedencia ERROR>FAIL solo aplica con
  condiciones de evidencia coexistentes, que esos fixtures no producen.
