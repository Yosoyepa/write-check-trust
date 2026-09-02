# ADR-004 — Separar el plano de control del plano de evaluación

- Estado: **Propuesto**
- Fecha: 2026-09-01
- Decisores requeridos: mantenedor de WCT y responsable de evaluación
- Alcance: arquitectura conceptual; no autoriza implementación

## Contexto

Las reglas, hooks y gates de WCT influyen directamente en lo que el agente hace.
Si esos mismos gates se usan como único scorer, el experimento mide en parte la
capacidad de optimizar una señal visible, no la corrección general de la solución.

Además, el core actual mezcla promesas de enforcement, mediciones, heurísticas y
proceso humano bajo el concepto amplio de “gate automatizado”. Para comparar
modelos se necesitan observaciones más ricas: tarea y snapshot, tratamiento,
trayectoria, tokens, costo, artefactos y resultado de un oracle independiente.

## Decisión propuesta

Definir dos planos con contratos separados:

1. **Plano de control WCT:** reglas, hooks, gates, ratchets y feedback visible al
   agente. Su responsabilidad es prevenir, detectar y ayudar a reparar.
2. **Plano de evaluación:** tareas versionadas, asignación de brazos, aislamiento,
   ledger, oráculos ocultos, scoring y análisis. Su responsabilidad es medir el
   efecto sin modificar el tratamiento.

El plano de evaluación dependerá de contratos neutrales de tarea, experimento,
run, evento, resultado de gate y resultado de oracle. Los adapters de modelos o
runtimes serán periféricos. Los tipos de provider no cruzarán al dominio del
laboratorio.

Los gates visibles podrán ser outcomes secundarios y variables de mecanismo,
pero no el único endpoint primario.

## Invariantes

- El agente no accede al holdout ni a su rubric.
- El scorer no cambia por brazo.
- La configuración del tratamiento tiene versión y digest.
- El resultado de control no puede sobrescribir el del oracle.
- Un run incompleto permanece en el ledger.
- `SKIP` y dato faltante no se convierten en `PASS`.
- El plano de evaluación puede cambiar de runtime sin cambiar la tarea u oracle.

## Consecuencias positivas

- Evita la medición circular y permite estimar escapes condicionales a gate verde.
- Hace comparables modelos, perfiles y versiones.
- Permite estudiar el mecanismo: prevención, detección, reparación y costo.
- Conserva WCT pequeño y provider-neutral.
- Facilita auditoría, replay y reproducción externa.

## Costos y riesgos

- Duplica deliberadamente parte del concepto de “resultado”: control y oracle.
- Requiere proteger un corpus oculto y administrar provenance.
- Introduce una frontera de datos que debe minimizar información sensible.
- Puede aumentar el costo inicial antes de producir una cifra de uplift.

## Alternativas descartadas

### Usar el tier `full` como score único

Descartada por circularidad, diferente completitud entre entornos y falta de
calificación independiente de algunos gates.

### Incorporar evaluación dentro del runner de gates

Descartada porque mezcla el tratamiento con el scorer, dificulta ceguera y acopla
el benchmark al CLI actual.

### Crear un índice ponderado de calidad

Descartada como outcome primario porque los pesos ocultarían tradeoffs entre
calidad, seguridad, costo y latencia.

## Condición de aceptación

Antes de implementar, aprobar [SPEC-001](../specs/SPEC-001-contratos-experimentales.md),
[SPEC-002](../specs/SPEC-002-metricas-y-estadistica.md) y el threat model de
holdout/aislamiento. Una rebanada mínima debe comparar A0/A3 sobre una tarea sin
filtrar tipos de runtime al contrato neutral.
