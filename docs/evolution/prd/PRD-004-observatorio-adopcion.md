# PRD-004 — Observatorio de adopción y valor longitudinal

- Estado: propuesta
- Prioridad: P2
- Dependencias: Evidence Lab estable y corpus/gates calificados

## Problema

Un benchmark controlado estima capacidad bajo condiciones definidas. No responde
si equipos reales mantienen WCT, cuánto feedback toleran, qué escapes encuentran
o si los ratchets previenen erosión a lo largo de meses.

## Objetivo

Medir efectividad, fricción y sostenibilidad de WCT en proyectos externos mediante
cohortes opt-in, datos mínimos, comparadores explícitos y aprendizaje continuo de
escapes.

## Principios

- participación voluntaria y revocable;
- minimización y clasificación de datos;
- ninguna extracción de código o prompts por defecto;
- métricas agregadas acompañadas de contexto cualitativo;
- publicación de attrition y sesgo de selección;
- comparación temporal no confundida con causalidad automática;
- feedback al corpus sin exponer propiedad intelectual.

## Preguntas de producto

1. ¿Qué perfiles y gates permanecen activos después de la instalación?
2. ¿Cuánto tarda el feedback y cuántas veces se omite?
3. ¿Qué gates encuentran defectos que la revisión habría dejado pasar?
4. ¿Qué falsos positivos causan overrides o abandono?
5. ¿Los ratchets frenan regresión o desplazan costo?
6. ¿Qué clases de proyecto/modelo obtienen mayor beneficio?
7. ¿Qué escapes reales no existían en el corpus?

## Requisitos

| ID | Requisito | Criterio |
|---|---|---|
| AO-001 | consentimiento | alcance, campos y retención son visibles y revocables |
| AO-002 | minimización | no se recolecta código, secretos, prompts o PII por defecto |
| AO-003 | definición de adopción | activo, parcial, pausado y abandonado tienen reglas explícitas |
| AO-004 | denominador | proyectos y periodos sin datos/abandonos permanecen reportados |
| AO-005 | eventos | gate, estado, duración, perfil y versión; contenido sensible excluido |
| AO-006 | escapes | formulario causal y clasificación, con anonimización |
| AO-007 | overrides | baseline raises y omisiones tienen razón y aprobación agregables |
| AO-008 | comparación | antes/después y cohortes comparables con límites declarados |
| AO-009 | devolución | adoptantes reciben su propio resumen y pueden corregir datos |
| AO-010 | gobernanza | acceso, retención, borrado y publicación tienen owners |

## Métricas

- retención de adopción a 30/90/180 días;
- perfiles/gates activos y `SKIP` por capacidad;
- latencia p50/p95 por tier;
- defectos detectados, reparados y escapados;
- false positives y overrides por 100 cambios;
- tiempo de reparación y costo humano percibido;
- tendencia de baselines y raises;
- incidentes convertidos en fixture;
- satisfacción cualitativa y razones de abandono;
- variación entre proyectos, no solo promedio.

## Diseño analítico

- series interrumpidas cuando exista baseline preadopción suficiente;
- cohortes por tamaño, stack, madurez y modelo;
- proyectos comparadores cuando sean razonablemente equivalentes;
- análisis de sensibilidad a attrition;
- triangulación con entrevistas y postmortems;
- no atribuir causalidad a simples correlaciones antes/después.

## Privacidad y seguridad

- ids seudónimos y rotables;
- agregación con umbral mínimo antes de publicar;
- secretos y paths nunca incluidos;
- separación entre telemetría operacional y contenido voluntario de postmortem;
- política de incidente y borrado;
- revisión legal/ética antes de invitar externos.

## Criterio de salida

El observatorio demuestra utilidad si puede identificar al menos una mejora y una
fricción accionables, cuantificar adopción/attrition sin ocultar denominadores y
convertir escapes en cambios del corpus, todo sin recolectar código por defecto.
