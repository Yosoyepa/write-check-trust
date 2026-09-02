# PRD-002 — Suite de calificación end-to-end de gates

- Estado: propuesta
- Prioridad: P0
- Decisión relacionada: [ADR-005](../decisions/ADR-005-calificar-gates-antes-de-modelos.md)

## Problema

El estado verde del repositorio demuestra que la implementación y sus tests
actuales concuerdan. No demuestra necesariamente que cada gate detecte su modo
de fallo por la ruta productiva, aplique su configuración, maneje herramientas
ausentes o acepte alternativas válidas.

## Objetivo

Convertir cada claim de WCT en un instrumento calificado mediante fixtures
conocidos-buenos y conocidos-malos que ejecuten el entrypoint real y publiquen
sus tasas de detección, escapes y falsos positivos.

## No objetivos

- lograr cero falsos positivos para toda heurística;
- simular todos los repositorios posibles;
- subir baselines para acomodar fixtures;
- sustituir tests unitarios rápidos;
- usar los resultados como benchmark de inteligencia de un modelo.

## Entidades de producto

| Entidad | Responsabilidad |
|---|---|
| claim | afirmación estrecha, versionada y falsable |
| capability | herramienta/configuración necesaria para medir el claim |
| fixture | workspace cerrado con outcome esperado y rationale |
| execution | resultado de correr el gate productivo sobre el fixture |
| qualification | agregación por claim, versión, plataforma y herramienta |
| escape | defecto inequívoco que produjo pass/no bloqueo |
| false positive | alternativa válida rechazada por el gate |

## Requisitos

| ID | Requisito | Criterio de producto |
|---|---|---|
| GQ-001 | claim registry | toda entrada define alcance, fuerza E/M/H/P/U y owner |
| GQ-002 | ruta productiva | fixture invoca CLI/tier público, no recognizer paralelo |
| GQ-003 | controles | cada claim tiene positivo, negativo y frontera cuando aplique |
| GQ-004 | estados | se califican `PASS/FAIL/SKIP/ERROR` y completitud |
| GQ-005 | entorno | tool missing, crash, timeout y versión incompatible son casos explícitos |
| GQ-006 | configuración | cambios en claves activas alteran el resultado esperado |
| GQ-007 | artefactos | stale, scope incorrecto y hash ajeno se rechazan |
| GQ-008 | bypass | modificación de governance, baseline, manifest o supresión se prueba |
| GQ-009 | controles negativos | alternativas válidas evitan sobreajuste del detector |
| GQ-010 | métricas | confusion matrix y casos no aplicables por claim/plataforma |
| GQ-011 | no vacuidad | cero unidades aplicables no equivale a éxito |
| GQ-012 | aliases | alias hereda evidencia y no cuenta como detector independiente |
| GQ-013 | reproducibilidad | fixture contiene snapshot, locks, tool versions y expected rationale |
| GQ-014 | escape lifecycle | cada escape abre postmortem y fixture de regresión |

## Matriz mínima por clase de gate

| Clase | Casos adicionales |
|---|---|
| métrica con ratchet | baseline−1, baseline, baseline+1; baseline corrupto/ausente |
| detector estático | hallazgo inequívoco, variante válida, supresión/bypass |
| herramienta externa | binario ausente, exit inesperado, output malformado, timeout |
| artefacto encadenado | productor falló, archivo stale, hash de otro commit, scope vacío |
| Gherkin/aceptación | escenario no recolectado, cero mutantes, example variante, oracle decorativo |
| hook | evento real, path relativo/absoluto, rename, comando equivalente |
| proceso/historia | declarar límite; requerir provenance o revisión humana, no fingir enforcement |

## Scenarios críticos del corte actual

- 97 % de cobertura con baseline 100 debe fallar el claim de ratchet.
- LCOV que solo cubre el ejemplo no puede sustentar claim sobre `tools/wct`.
- Property test incluido en coverage/mutación debe romper el aislamiento.
- Payload adversarial debe materializarse como repo y ejecutar el gate señalado.
- Feature sin `Examples` no puede “matar 0 de 0” y aprobar mutación.
- `jscpd` ausente permite flujo local, pero impide perfil completo.
- Cambiar una clave activa produce un cambio observable; una clave deprecated
  genera diagnóstico.
- SBOM con licencia incompatible no satisface el claim de compatibilidad.
- Gate alias no aumenta el denominador de capacidades independientes.

## Salidas

- catálogo de claims y fuerza de evidencia;
- matriz fixture → expected → actual;
- sensitivity, specificity, precision, FPR y FNR;
- límites conocidos por plataforma/tool version;
- lista de capabilities faltantes;
- casos no calificables y rationale;
- historial de escapes y regresiones;
- badge o resumen solo si distingue “correcto”, “completo” y “calificado”.

## Métricas de producto

- claims con cobertura mínima completa;
- escape rate por modo de fallo;
- false-positive rate en alternativas válidas;
- tiempo para convertir un escape en fixture;
- divergencias configuración/runtime;
- fixtures flake y estabilidad por plataforma;
- porcentaje de red team que usa ruta productiva;
- porcentaje de reglas correctamente etiquetadas E/M/H/P/U.

## Criterio de salida P0

Todo gate que vaya a participar en el benchmark tiene claim versionado, fixture
positivo/negativo/frontera, scope y configuración efectivos, semántica de
completitud y resultado agregado. Lo restante aparece explícitamente como no
calificado, sin impedir su uso cotidiano como señal.
