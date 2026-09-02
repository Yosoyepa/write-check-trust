# SPEC-002 — Métricas, estadística y criterios de decisión

- Estado: propuesta para revisión estadística
- Naturaleza: protocolo; no fija todavía márgenes ni tamaño muestral

## Jerarquía de outcomes

### Nivel 1 — calidad independiente

Cada tarea define requisitos críticos y no críticos antes del run. La métrica
binaria primaria propuesta es éxito si todos los requisitos críticos y el umbral
preregistrado de requisitos restantes pasan el oracle. El detalle por requisito
se conserva; no se infiere éxito solo por exit code global.

### Nivel 2 — seguridad y escapes

Un escape es un defecto presente según el oracle que no impidió el cierre verde
del perfil visible. Escapes críticos se reportan individualmente y no se
compensan con mejoras de estilo.

### Nivel 3 — eficiencia

Costo total incluye consumo del modelo, cache/reasoning cuando estén disponibles,
tooling externo, compute de gates y wall time. Costos exactos y estimados se
presentan por separado.

### Nivel 4 — mecanismo y mantenibilidad

Gates activados, reparaciones, tamaño del diff, mutación, complejidad y deuda
explican cómo se obtuvo el resultado. Son secundarios salvo preregistro distinto.

## Definiciones

| Métrica | Definición |
|---|---|
| pass rate | runs con éxito semántico / runs asignados elegibles según intention-to-treat |
| uplift absoluto | `pass_rate(A3) − pass_rate(A0)` en puntos porcentuales |
| uplift relativo | uplift absoluto / `pass_rate(A0)`; no se usa si baseline es cero |
| gap recuperado | `(A3 − A0) / (A4 − A0)`; solo si el denominador es positivo y estable |
| critical escape rate | runs con ≥1 escape crítico / runs con oracle evaluable |
| conditional escape | runs con defecto oculto y perfil visible verde / runs con perfil visible verde |
| costo por éxito | suma de costos del brazo / número de éxitos; failures permanecen en el numerador |
| repair yield | fallos visibles cuya reparación termina pasando el oracle / reparaciones intentadas |
| first-green latency | tiempo desde inicio hasta primer perfil visible verde |
| semantic latency | tiempo desde inicio hasta estado final que pasa oracle; solo conocido post-run |
| completeness | claims requeridos ejecutados con evidencia válida / claims requeridos |
| replay fidelity | invariantes preservados y requests consumidos / replays intentados |

Si A4≤A0, “gap recuperado” no tiene interpretación útil y se omite con rationale.

## Calificación de gates

Para un defecto objetivo:

- **TP:** fixture defectuoso que el gate rechaza;
- **FN:** fixture defectuoso que pasa/no bloquea;
- **TN:** alternativa válida que el gate acepta;
- **FP:** alternativa válida que el gate rechaza.

| Métrica | Fórmula |
|---|---|
| sensibilidad/recall | `TP / (TP + FN)` |
| especificidad | `TN / (TN + FP)` |
| precision | `TP / (TP + FP)` |
| false-positive rate | `FP / (FP + TN)` |
| false-negative rate | `FN / (FN + TP)` |

Se publican numeradores y denominadores. Una celda sin casos es “no estimable”,
no 0 % ni 100 %. Los resultados se estratifican por herramienta, versión,
plataforma y clase de fixture cuando haya volumen.

## Corrección, completitud y validez

Un run de gates produce tres ejes:

| Eje | Pregunta | Ejemplo negativo |
|---|---|---|
| corrección | ¿algún claim ejecutado falló? | finding real |
| completitud | ¿se ejecutaron todas las capacidades requeridas? | `jscpd` ausente |
| validez | ¿artefactos/scope/config corresponden al run? | LCOV stale |

Solo `correcto + completo + válido` sustenta un perfil certificado. Un flujo
local puede ser correcto pero incompleto. `SKIP` nunca aumenta el numerador de
pass ni desaparece del denominador de capacidades.

## Estimandos y comparaciones

### Efecto de WCT en modelo económico

Estimando primario: diferencia emparejada A3−A0 en probabilidad de éxito sobre la
población de tareas descrita por el corpus.

### No inferioridad

Estimando: A3−A4. Se declara no inferioridad solo si el límite inferior del
intervalo preregistrado está por encima de `−delta`, donde `delta` fue aprobado
antes del holdout. No rechazar diferencia no demuestra equivalencia.

### Mecanismo

A1−A0 estima efecto de persuasión; A2−A0, efecto de gate/repair; A3 frente a A1 y
A2, combinación; A5−A4, interacción sobre modelo de referencia. Estas son
comparaciones secundarias o requieren control de multiplicidad.

## Método estadístico propuesto

- Bloquear y emparejar por tarea.
- Para una ejecución por brazo/tarea, McNemar describe pares binarios discordantes.
- Con repeticiones y heterogeneidad, usar modelo logístico mixto con tratamiento
  fijo y tarea como efecto aleatorio; declarar cualquier efecto adicional antes.
- Para uplift/costo no normal, bootstrap agrupado por tarea, manteniendo juntas
  repeticiones y brazos.
- Presentar intervalo de confianza y distribución de discordantes.
- Reportar efectos por estrato con intervalos; no convertir exploratorios en
  conclusiones confirmatorias.
- Ajustar multiplicidad para familia de hipótesis confirmatorias o etiquetar el
  resto exploratorio.
- Hacer análisis de sensibilidad a timeouts, infra errors y tareas retiradas.

## Tamaño muestral

No se fija por convención. El piloto estima:

- pass rate de baseline;
- correlación dentro de tarea;
- proporción de pares discordantes;
- varianza entre tareas y runs;
- costo y attrition.

Con eso se calcula potencia para el efecto mínimo útil o margen de no inferioridad.
El rango 12–20 del piloto y 30–50 del estudio son presupuestos de planificación,
no garantías estadísticas.

## Missing data, errores y reruns

- Budget exhausted cuenta como fallo primario bajo intention-to-treat.
- Agent/runtime error cuenta según política congelada y siempre se reporta.
- Infrastructure error puede autorizar rerun solo por una regla objetiva previa;
  original y rerun permanecen vinculados.
- Oracle unavailable hace el run no evaluable, pero permanece en el denominador
  de integridad y se analiza como missing.
- Ningún run se elimina porque su resultado sea adverso.
- Exclusiones se deciden sin conocer el brazo cuando sea posible.

## Precios y costo

- Tabla de precios tiene fecha, moneda, provider, modelo y unidades.
- Uso facturado prevalece sobre estimación, conservando ambos si difieren.
- Cache read/write y reasoning no se mezclan con input/output ordinario.
- Costo de compute propio declara método de asignación.
- Se reportan costo por run, por éxito y distribución; no solo promedio.
- Comparaciones históricas pueden recalcularse a precios constantes y deben
  distinguirse de costo nominal de la fecha.

## Criterios de decisión propuestos

| Decisión | Evidencia mínima |
|---|---|
| escalar del piloto | protocolo estable, oracle calificado, varianza/costo estimables |
| afirmar uplift | intervalo de A3−A0 compatible con efecto útil preregistrado |
| afirmar no inferioridad | límite inferior > `−delta` preregistrado |
| recomendar por costo | menor costo/éxito con escapes críticos no peores |
| retirar/degradar gate | baja sensibilidad o FPR/costo inaceptable en corpus relevante |
| promover gate | claim calificado y repair yield positivo con costo aceptable |
| recomendar modelo por tarea | efecto consistente en estrato y muestra externa suficiente |

Los valores de “útil” e “inaceptable” requieren aprobación de producto/riesgo;
no deben inferirse del mismo dataset usado para evaluar.

## Reporte mínimo

- flow de tareas/runs asignados, completados, inválidos y excluidos;
- tabla por brazo con denominadores;
- estimaciones e intervalos;
- costos exactos/estimados y tabla de precio;
- escapes críticos y casos discordantes;
- `SKIP`, errors, timeouts y flakes;
- análisis por estrato preregistrado;
- desviaciones del plan;
- versiones de modelo, WCT, corpus y oracle;
- limitaciones, contaminación y fecha de expiración del claim.
