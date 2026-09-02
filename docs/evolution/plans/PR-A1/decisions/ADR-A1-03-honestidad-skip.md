# ADR-A1-03 — El resumen de gates separa PASS de SKIP

Estado: propuesto (se ejecuta al aprobarse GHERKIN-A1.md).
Contexto: [ANALYSIS.md §1.3](../ANALYSIS.md) · [RESEARCH.md R4](../RESEARCH.md).

## Contexto

`render.py:19-20` calcula `passed = sum(not result.blocking ...)` e imprime
`"{passed}/{total} gates no bloqueantes"`. SKIP no bloquea (`model.py:28-30`),
así que 28 PASS + 5 SKIP se reporta como `33/33` — indistinguible del
full-pass. El tier full puede ser verde con gates opcionales ausentes. Medido:
ningún consumidor parsea esa línea (grep: solo el productor).

## Decisión

1. El agregado del resumen muestra **tres contadores separados**:
   `N gates: X PASS · Y SKIP · Z FAIL/ERROR` (formato final a gusto del
   implementador si mantiene los tres contadores distinguibles y el estilo del
   archivo).
2. **No se cambia la semántica de bloqueo**: SKIP sigue sin bloquear;
   `model.py` no se toca. La tabla por fila ya muestra STATUS por gate y
   sigue tal cual.
3. Tests del render actualizados/añadidos en el mismo commit; re-búsqueda de
   consumidores del formato en verificación (ANALYSIS: 0 hoy).

## Alternativas consideradas

- **(a) SKIP bloqueante en tier full**: rechazada *por ahora*. Es la decisión
  de perfiles "local vs completo" del Horizonte 0 (O-006): convertiría en rojo
  todo entorno sin las herramientas opcionales (semgrep, jscpd, sbom…),
  incluyendo corridas legítimas de desarrollo local y el propio smoke de
  adopción si el grupo quality no está. Cambiar semántica de bloqueo sin esa
  decisión de producto es sobre-alcance. A1 entrega el prerrequisito: con el
  conteo visible, esa decisión futura se toma con datos.
- **(b) Sufijo `(Z SKIP)` sobre la línea actual**: equivalente en información,
  peor en jerarquía — mantiene "X/Y no bloqueantes" como claim principal,
  que es exactamente la sobreafirmación a corregir.
- **(c) Motivo de SKIP en el agregado**: diferida. La razón por gate ya existe
  (fila de tabla); elevarla al agregado es ruido para el caso común. El
  contrato de evidencia completo (valor observado/umbral/motivo por gate) es
  O-001 (Report V2), no A1.

## Consecuencias

- Un tier full verde con skips ya no se lee como verificación completa: el
  claim del reporte se alinea con lo medido sin cambiar qué bloquea.
- COSTO conocido y aceptado: los resúmenes "perfectos" de hoy (33/33) se
  volverán honestamente "32 PASS · 1 SKIP" donde aplique — es el objetivo.
- Base para O-001 (Report V2: contrato de evidencia) y para la decisión de
  perfiles del Horizonte 0, que podrá citar conteos reales de SKIP por
  entorno.
