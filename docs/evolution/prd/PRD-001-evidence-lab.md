# PRD-001 — Evidence Lab

- Estado: propuesta
- Prioridad: P1, bloqueada por la calificación P0
- Decisión relacionada: [ADR-004](../decisions/ADR-004-plano-de-evaluacion-separado.md)

## Problema

WCT puede ejecutar gates, pero no existe un producto de evaluación que una de
forma reproducible tarea, tratamiento, modelo, trayectoria, patch, resultados,
oracle y costo. Sin esa unidad, las comparaciones dependen de pasos manuales y no
pueden auditarse o repetirse con otro runner.

## Objetivo

Permitir que un investigador defina una matriz de tareas y brazos, ejecute cada
celda en un entorno aislado, aplique un oracle independiente y obtenga un paquete
de evidencia autocontenido y comparable.

## Usuarios

- mantenedor de WCT que diseña el protocolo;
- verificador que reproduce una ejecución sin editarla;
- custodio del corpus que administra holdout;
- analista que compara brazos y calcula incertidumbre;
- adoptante externo que audita un claim publicado.

## No objetivos

- entrenar o fine-tunear modelos;
- reemplazar CI del proyecto evaluado;
- ser un proveedor de sandbox de alta seguridad;
- imponer DeepSeek Harness u otro runtime;
- decidir automáticamente qué margen de no inferioridad es aceptable;
- convertir resultados exploratorios en claims confirmatorios.

## Jobs to be done

1. Dado un task package, demostrar exactamente qué snapshot y oracle se usaron.
2. Dado un experimento, reconstruir qué difiere entre A0 y A3.
3. Dado un run, seguir la trayectoria desde prompt hasta oracle y costo.
4. Dado un resultado, reproducir integración sin API mediante replay cuando sea
   posible.
5. Dado un claim, verificar que no se excluyeron runs adversos post hoc.

## Requisitos funcionales

| ID | Requisito | Criterio de producto |
|---|---|---|
| EL-001 | Contratos neutrales | tarea, experimento, run, evento y score no contienen tipos de provider |
| EL-002 | Aislamiento | cada run recibe workspace, home, sesión y secretos independientes |
| EL-003 | Tratamientos versionados | todo brazo tiene digest y diff legible frente al control |
| EL-004 | Asignación reproducible | orden, seeds y repeticiones quedan congelados antes de ejecutar |
| EL-005 | Oracle posterior | scoring corre fuera del proceso del agente y en entorno limpio |
| EL-006 | Ledger append-only | intentos, fallos, timeouts y exclusiones se conservan |
| EL-007 | Artefactos cerrados | patch, logs, gates, oracle y entorno tienen hash y owner |
| EL-008 | Costo completo | tokens, caché, reasoning, wall time, tool calls y gates se separan |
| EL-009 | Replay | sesiones elegibles se reproducen sin credencial y exigen consumo completo |
| EL-010 | Exportación | paquete permite revisión offline sin revelar contenido privado no autorizado |
| EL-011 | Capability report | runtime declara qué campos exactos, estimados o no disponibles produce |
| EL-012 | Cierre del run | estado terminal externo distingue éxito, timeout, error, cancelación e incompleto |

## Requisitos no funcionales

- **Reproducibilidad:** manifests, imágenes, locks y precios son versionados.
- **Seguridad:** secretos no entran al ledger; el holdout tiene acceso mínimo.
- **Privacidad:** prompts, patches y logs pueden contener IP; exportación aplica
  clasificación y redacción sin alterar los hashes originales custodiados.
- **Portabilidad:** al menos un runner mínimo; adapters externos opcionales.
- **Auditabilidad:** toda transformación de datos declara versión y fuente.
- **Fail closed:** un paquete incompleto no se presenta como reproducible.

## Flujo conceptual

1. Calificar y congelar una tarea.
2. Preregistrar experimento y asignación.
3. Materializar workspace aislado.
4. Ejecutar el brazo y registrar eventos.
5. Cerrar patch y artefactos visibles.
6. Ejecutar gates del tratamiento según perfil.
7. Aplicar oracle privado en entorno limpio.
8. Calcular costo y estado de completitud.
9. Sellar el run en el ledger.
10. Analizar solo después de cerrar el conjunto preregistrado.

## Escenarios de aceptación propuestos

| Escenario | Dado | Cuando | Entonces |
|---|---|---|---|
| aislamiento | dos brazos de la misma tarea | se ejecutan en cualquier orden | ningún archivo, cache o sesión del primero aparece en el segundo |
| tratamiento | A0 y A3 | se comparan manifests efectivos | solo difieren campos preregistrados de WCT |
| run fallido | el provider corta el stream | el run termina | se conserva como incompleto/error con costo y eventos; no desaparece |
| oracle oculto | agente termina | se aplica scoring | el agente nunca recibió path, contenido ni diagnóstico del holdout |
| replay | una sesión grabada y cerrada | se reproduce sin API | todos los requests se consumen y los invariantes semánticos pasan |
| artifact stale | LCOV pertenece a otro commit | se sella el run | la evidencia se marca inválida y el perfil no queda completo |
| adapter parcial | provider no informa reasoning tokens | se calcula costo | el campo queda `unavailable/estimated`, nunca cero implícito |

## Métricas de producto

- porcentaje de runs con ledger completo;
- porcentaje reproducible desde manifest;
- discrepancias entre costo calculado y fuente facturada;
- contaminación o acceso indebido al holdout;
- diferencias no preregistradas entre brazos;
- tasa de replay determinista;
- tiempo humano para auditar y reproducir un run;
- adapters que pasan la conformance suite.

## Dependencias

- O-001 contrato de evidencia;
- O-002 gates calificados;
- ADR-006 y gobierno del holdout;
- SPEC-001 y SPEC-003 aprobadas;
- threat model de ejecución y almacenamiento.

## Riesgos de producto

- almacenar demasiados datos antes de validar las preguntas;
- que el runner concreto dicte el dominio;
- que replay sea interpretado como evaluación del modelo;
- que la redacción de privacidad rompa reproducibilidad;
- que el costo de operar el laboratorio supere el uplift estudiado.

## Criterio de salida beta

Una comparación A0/A3 sobre al menos una tarea calificada puede ser ejecutada por
un actor y reproducida por otro; el paquete demuestra aislamiento, oracle oculto,
trayectoria, costo y provenance, y no necesita edición manual para reconciliar
los brazos.
