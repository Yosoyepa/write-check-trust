# Matriz de trazabilidad

La matriz evita que una idea atractiva quede desconectada de una observación, un
requisito verificable y una métrica de decisión.

| Hallazgo u oportunidad | Decisión | PRD | Especificación | Evidencia de salida |
|---|---|---|---|---|
| Resultados sin valor, umbral ni scope | ADR-004 | PRD-001 | SPEC-003 | ledger y reporte autocontenidos |
| Gates no calificados por su ruta real | ADR-005 | PRD-002 | SPEC-001, SPEC-002 | sensibilidad, especificidad y controles de frontera |
| `SKIP` no bloquea la promesa `full` | ADR-005 | PRD-001, PRD-002 | SPEC-002 | completitud separada de corrección |
| Cobertura total no aplica su baseline | ADR-005 | PRD-002 | SPEC-002 | prueba de frontera a ambos lados del umbral |
| Núcleo `tools/wct` fuera de coverage/mutación | ADR-005 | PRD-002 | SPEC-004 | matriz explícita de scope por gate |
| Property tests contaminan otras métricas | ADR-005 | PRD-002 | SPEC-001 | fixture que prueba inclusión y exclusión |
| Red team usa reconocedores paralelos | ADR-005 | PRD-002 | SPEC-001 | cada caso ejecuta el gate productivo |
| Aceptación puede pasar con cero mutaciones | ADR-005 | PRD-002 | SPEC-001 | invariantes mínimos y fallo por vacuidad |
| Configuración declarada sin consumidor | ADR-004 | PRD-002 | SPEC-003 | inventario key → consumidor → test → doc |
| Calidad del agente medida por su propio feedback | ADR-006 | PRD-003 | SPEC-002, SPEC-004 | oráculo oculto e independiente |
| Falta comparación causal entre tratamientos | ADR-006 | PRD-003 | SPEC-001, SPEC-002 | ablación A0–A5 por tarea emparejada |
| Falta telemetría de costo y trayectoria | ADR-004, ADR-007 | PRD-001, PRD-003 | SPEC-003 | tokens facturados, tiempo, eventos y costo/éxito |
| Falta replay determinista | ADR-007 | PRD-001 | SPEC-003 | consumo completo de replay e invariantes semánticos |
| Snapshots pueden legitimar regresiones | ADR-006, ADR-007 | PRD-001 | SPEC-003 | snapshot más invariantes independientes |
| Falta evidencia en adopciones reales | ADR-006 | PRD-004 | SPEC-004 | cohortes, escapes y tendencia longitudinal |
| SBOM no valida licencias | ADR-005 | PRD-002 | SPEC-002 | corpus de licencias compatibles/incompatibles |

## Cobertura de las preguntas de producto

| Pregunta | Documento responsable |
|---|---|
| ¿Qué está realmente implementado hoy? | [Auditoría de gates](01-auditoria-de-gates.md) |
| ¿Qué conviene aprender de DeepSeek Harness? | [Estudio comparativo](02-estudio-deepseek-harness.md) |
| ¿Cómo aislar el efecto de WCT? | [Programa de evaluación](03-programa-de-evaluacion.md) |
| ¿Qué se construiría y en qué orden? | [Portafolio](04-portafolio-de-oportunidades.md) y [roadmap](05-roadmap.md) |
| ¿Cómo se decide si el modelo económico mejoró? | [SPEC-002](specs/SPEC-002-metricas-y-estadistica.md) |
| ¿Cómo se reproduce una ejecución? | [SPEC-003](specs/SPEC-003-ledger-y-replay.md) |
| ¿Cómo se evita contaminar el benchmark? | [SPEC-004](specs/SPEC-004-gobierno-del-corpus.md) |
