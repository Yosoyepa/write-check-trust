# Portafolio de oportunidades y features

## Método de priorización

La prioridad combina:

- **integridad de la evidencia:** cuánto puede invalidar afirmaciones actuales;
- **valor de aprendizaje:** qué incertidumbre de producto reduce;
- **dependencias:** qué otras oportunidades desbloquea;
- **riesgo de sobreconstrucción:** cuánto añade antes de demostrar valor;
- **costo esperado:** estimación relativa, no compromiso de calendario.

P0 precede cualquier claim experimental; P1 habilita el estudio; P2 amplía
validez y adopción.

## Resumen

| ID | Oportunidad / feature | Prioridad | Valor | Esfuerzo | Dependencias |
|---|---|---:|---:|---:|---|
| O-001 | contrato de evidencia y Report V2 | P0 | muy alto | medio | ninguna |
| O-002 | suite end-to-end de calificación de gates | P0 | muy alto | alto | O-001 |
| O-003 | coherencia de scope para coverage/mutation/property | P0 | muy alto | medio | O-002 |
| O-004 | aceptación no vacua y corpus completo | P0 | muy alto | medio | O-002 |
| O-005 | conformidad configuración → runtime | P0 | alto | medio | O-001 |
| O-006 | semántica de completitud y perfiles | P0 | alto | medio | O-001, O-005 |
| O-007 | Evidence Lab neutral | P1 | muy alto | alto | P0 completo |
| O-008 | benchmark de uplift y ablación | P1 | muy alto | alto | O-007, O-009 |
| O-009 | corpus con oráculos ocultos | P1 | muy alto | alto | O-002 |
| O-010 | telemetría de costo y trayectoria | P1 | alto | medio | O-007 |
| O-011 | replay y smokes de ruta real | P1 | alto | medio | O-007 |
| O-012 | compatibilidad de licencias | P1 | medio | medio | O-002, O-005 |
| O-013 | orden aleatorio y política de flakes | P1 | medio | bajo/medio | O-002 |
| O-014 | observatorio de adopción | P2 | alto | alto | O-007, O-009 |
| O-015 | postmortem → fixture → métrica | P2 | alto | medio | O-002, O-011 |
| O-016 | contrato polyglot | P2 | medio | alto | P0, O-007 |
| O-017 | adaptadores de benchmarks/runtimes | P2 | medio | alto | O-007 |
| O-018 | valor longitudinal de ratchets | P2 | alto | alto | O-014 |

## P0 — integridad del instrumento

### O-001 — contrato de evidencia y Report V2

**Problema.** Un `PASS` no declara siempre qué valor, umbral, baseline, scope y
artefacto lo sustentan. `wct report` describe configuración, no una medición
auditable de la ejecución.

**Feature propuesta.** Un contrato único para resultados y un reporte que separe
corrección, completitud y validez de evidencia. Debe poder serializarse y
compararse entre ejecuciones sin parsear texto humano.

**Criterios de aceptación de diseño.** Todo gate identifica claim/version,
observación, unidad, operador, umbral, baseline, scope/exclusiones, herramienta,
versión, configuración efectiva, artefactos/hash, duración/presupuesto y
provenance. Un campo no disponible se declara como ausencia, no se omite. Los
aliases señalan su medición origen.

**Métrica de éxito.** 100 % de claims del perfil seleccionado producen registros
schema-valid; cero `PASS` sin evidencia mínima; una ejecución puede reconstruirse
desde el reporte y sus hashes.

**Riesgo.** Convertir el contrato en un data warehouse prematuro. Mitigación:
empezar por el conjunto mínimo de [SPEC-003](specs/SPEC-003-ledger-y-replay.md).

### O-002 — suite end-to-end de calificación de gates

**Problema.** Tests unitarios y red team paralelo no prueban que el CLI real
rechace un repo defectuoso ni que acepte uno válido.

**Feature propuesta.** Corpus versionado de micro-repositorios que ejecuta cada
gate por su entrypoint productivo con positivos, negativos, fronteras, fallos de
tool, timeout, configuración y bypass.

**Criterios de aceptación de diseño.** Cada claim bloqueante tiene al menos un
control bueno, malo y de frontera; el fixture no llama funciones internas del
detector; los casos prueban `PASS/FAIL/SKIP/ERROR`; los falsos positivos son
casos de primera clase; los resultados agregan confusion matrix por clase.

**Métrica de éxito.** Sensibilidad y especificidad publicadas por gate; cero
claims etiquetados “calificados” sin ruta real y controles negativos; toda
regresión real genera un fixture.

### O-003 — coherencia de scope para coverage, mutation y property

**Problema.** El ejemplo recibe coverage/mutación mientras el core queda fuera;
property tests participan en métricas de las que deberían estar aislados; el
baseline de coverage no bloquea.

**Feature propuesta.** Matriz declarada de targets/suites por métrica, artefactos
separados para template y harness, exclusiones verificables y ratchet de
cobertura realmente conectado.

**Criterios de aceptación de diseño.** El reporte enumera archivos medidos y
excluidos; core y template no se mezclan; un property test que accidentalmente
entra a coverage/mutación falla un fixture; baseline−1 falla y baseline pasa; un
LCOV stale o de otro commit no es válido.

**Métrica de éxito.** Cero discrepancias entre scope declarado y artefacto; 100 %
de los baselines de cobertura tienen prueba de frontera; mutation score del core
y del template se publica por separado.

### O-004 — aceptación no vacua y corpus completo

**Problema.** Parsear Gherkin no prueba su ejecución; el default muta solo una
feature y un escenario sin `Examples` puede pasar con cero mutaciones.

**Feature propuesta.** Manifiesto de features, mapping escenario → test
recolectado → ejecución, requisitos de parametrización y umbrales mínimos de
mutantes aplicables.

**Criterios de aceptación de diseño.** Toda feature de producto está en el
manifiesto; todo escenario declarado genera o enlaza un test recolectado; cero
mutaciones aplicables es `FAIL` o `NOT_APPLICABLE` justificado, nunca éxito; se
prueba `require_parameters`; el reporte identifica cada mutante y oracle que lo
mató.

**Métrica de éxito.** Cobertura bidireccional 100 % entre escenarios exigibles y
tests; cero éxitos vacuos; mutation score Gherkin por feature y por campo.

### O-005 — conformidad configuración → runtime

**Problema.** Hay claves declaradas sin efecto observable y valores hardcoded que
pueden sombrear umbrales.

**Feature propuesta.** Inventario verificable de cada clave pública a parser,
consumidor, test de frontera y documentación. Detectar claves huérfanas,
consumidores sin configuración y fuentes duplicadas.

**Criterios de aceptación de diseño.** Cada clave tiene un owner y estado
`active/deprecated/removed`; cambiarla dentro de valores válidos cambia un
resultado observable o se rechaza; no hay dos fuentes de verdad; perfiles y
modos enumeran las capacidades que activan.

**Métrica de éxito.** Cero claves activas sin consumidor; cero umbrales
duplicados; diff de configuración efectiva disponible en cada run.

### O-006 — semántica de completitud y perfiles

**Problema.** `SKIP` es no bloqueante incluso cuando falta una capacidad que el
nombre `full` sugiere presente. La opcionalidad está distribuida.

**Feature propuesta.** Perfiles versionados con capacidades requeridas y
opcionales, y resultado tridimensional: corrección, completitud, validez.

**Criterios de aceptación de diseño.** Un perfil “certificado” es incompleto si
falta una herramienta requerida; desarrollo local puede quedar correcto pero
incompleto; toda opcionalidad proviene de una sola fuente; el resumen no cuenta
`SKIP` como pass; aliases no inflan el denominador.

**Métrica de éxito.** Dos entornos con el mismo perfil ejecutan el mismo conjunto
de claims o fallan por capacidad ausente; cero ambigüedad entre “no bloqueó” y
“cumplió el perfil”.

## P1 — laboratorio y benchmark

### O-007 — Evidence Lab neutral

**Problema.** No existe una unidad reproducible que conecte tarea, brazo, modelo,
workspace, resultado WCT, oracle y costo.

**Feature propuesta.** Plano de evaluación separado, con contratos neutrales de
tarea, experimento, run y scorer. Un runner concreto queda detrás de un adaptador.

**Criterios de aceptación de diseño.** El mismo task package corre en al menos un
runner mínimo; el dominio no importa tipos de provider; cada run tiene workspace
y home aislados; el scorer oculto opera después del tratamiento; los artefactos
se cierran con hash.

**Métrica de éxito.** Repetición desde manifest produce el mismo entorno y scorer;
comparación A0/A3 se genera sin edición manual de la tarea.

### O-008 — benchmark de uplift y ablación

**Problema.** No se sabe cuánto del resultado proviene del modelo, de las reglas,
de gates, de reparación o simplemente de mayor compute.

**Feature propuesta.** Protocolo A0–A5 emparejado por tarea con presupuestos
equivalentes, preregistro, repeticiones y análisis de costo/éxito.

**Criterios de aceptación de diseño.** Brazos difieren solo en el tratamiento
declarado; orden aleatorio; endpoint y margen congelados; ejecución ciega del
holdout; intervalos de confianza y casos discordantes publicados.

**Métrica de éxito.** Estimación de uplift absoluto/relativo, gap recuperado,
costo/éxito e interacción por clase de tarea con incertidumbre.

### O-009 — corpus con oráculos ocultos

**Problema.** Los mismos gates visibles no pueden ser tratamiento y scorer
primario. Los benchmarks públicos también pueden estar contaminados o mal
especificados.

**Feature propuesta.** Corpus estratificado, versionado y revisado, con splits
dev/validation/holdout, tests ocultos, invariantes, mutantes holdout y revisión
humana ciega donde sea necesario.

**Criterios de aceptación de diseño.** Cada tarea tiene provenance, snapshot,
oracle hash, solución de referencia, alternativa válida, negativos y varias
ejecuciones limpias; el agente no puede leer holdout; retiros conservan historia.

**Métrica de éxito.** Tasa de tareas calificadas, flake cero en liberación,
distribución por estrato y defectos plausibles rechazados por tarea.

### O-010 — telemetría de costo y trayectoria

**Problema.** El snapshot final no revela tokens, caching, retries, vueltas de
gate, tool calls ni costo del hardening.

**Feature propuesta.** Event log append-only y modelo de costo que separe uso
facturado, estimado, gate CPU, wall time y reintentos.

**Criterios de aceptación de diseño.** Cada evento tiene run/step/time y fuente;
tokens exactos no se mezclan con estimados; el costo usa una tabla versionada de
precios; se identifica primer verde, éxito semántico y terminación.

**Métrica de éxito.** ≥99 % de runs cerrados tienen contabilidad completa o una
marca explícita de dato faltante; reconciliación contra factura cuando exista.

### O-011 — replay y smokes de ruta real

**Problema.** Las API de modelos introducen costo y variabilidad, mientras los
tests internos pueden omitir el producto ensamblado.

**Feature propuesta.** Record/replay keyless para integración, snapshots cerrados
e invariantes semánticos, más smokes por CLI/SDK real.

**Criterios de aceptación de diseño.** El replay consume todos los eventos;
detecta requests extra/faltantes; normaliza solo campos autorizados; un snapshot
refresh no puede cambiar invariantes; se prueban timeout, retry, stream roto y
tool call.

**Métrica de éxito.** Replays deterministas y smokes reales detectan fixtures de
regresión conocidos; cero golden aprobado sin oracle semántico.

### O-012 — compatibilidad de licencias

**Problema.** SBOM inventaría componentes, pero no evalúa la regla de
compatibilidad.

**Feature propuesta.** Política explícita de licencias permitidas, prohibidas y
de revisión, aplicada al grafo desplegable y al artefacto de distribución.

**Criterios de aceptación de diseño.** Fixtures compatibles/incompatibles/unknown;
provenance de licencia; override solo con aprobación registrada; SBOM stale
rechazado; resultado separado de CVE.

**Métrica de éxito.** 100 % de componentes desplegables clasificados o bloqueados
como desconocidos; cero claim SEC-008 sustentado solo por generación del SBOM.

### O-013 — orden aleatorio y política de flakes

**Problema.** El gate está registrado, pero la herramienta no existe en la
fotografía. Un flake se puede confundir con mejora o regresión del modelo.

**Feature propuesta.** Capacidad requerida en el perfil apropiado, seeds
persistidos, registro de primer fallo y retry diagnóstico conforme a la política.

**Criterios de aceptación de diseño.** Fixture con estado compartido falla bajo
orden aleatorio; seed se reproduce; retry no convierte el resultado original en
pass; el registro contiene test/job/fecha/resultado posterior.

**Métrica de éxito.** Tasa de flakes conocida y separada de fallos deterministas;
100 % de flakes observados tienen registro.

## P2 — validez externa y aprendizaje continuo

### O-014 — observatorio de adopción

**Problema.** Una mejora en el repositorio de ejemplo no demuestra valor en
equipos reales.

**Feature propuesta.** Cohortes opt-in con telemetría agregada, entrevistas,
baselines antes/después y registro de escapes, costo de feedback y fricción.

**Criterios de aceptación de diseño.** Consentimiento y minimización de datos;
proyectos anonimizados; definición de adopción activa; comparadores; publicación
de sesgo y attrition.

**Métrica de éxito.** Cambio longitudinal de escapes, tiempo de revisión,
completitud y costo; distribución entre proyectos, no solo promedio global.

### O-015 — bucle postmortem → fixture → métrica

**Problema.** Un escape corregido sin fixture se olvida; un fixture sin causa puede
probar el detalle equivocado.

**Feature propuesta.** Plantilla de postmortem con causa, safeguard ausente,
porqué los controles pasaron, invariante durable y owner de seguimiento.

**Criterios de aceptación de diseño.** Todo escape clasificado produce fixture de
ruta real y actualiza la taxonomía; refresh de snapshots no elimina el invariante;
se registra tiempo de detección y recurrencia.

**Métrica de éxito.** Cero escape cerrado sin guardrail o justificación; tasa de
recurrencia y tiempo escape→fixture decrecientes.

### O-016 — contrato polyglot

**Problema.** Acoplar claims a Python limita adopción, pero extender herramientas
antes del contrato puede multiplicar inconsistencia.

**Feature propuesta.** Claims y evidencia neutrales al lenguaje; paquetes de
capacidad por stack que preserven semántica de estado y reporting.

**Criterios de aceptación de diseño.** Un segundo stack produce el mismo contrato
de resultado; las diferencias de herramienta son explícitas; no se promete
equivalencia sin corpus de calificación propio.

**Métrica de éxito.** Comparabilidad de claims homologados y cobertura de casos
de calificación por stack.

### O-017 — adaptadores de benchmarks y runtimes

**Problema.** Un runner propio único reduce comparabilidad y puede recrear
infraestructura existente.

**Feature propuesta.** Puertos para runners/scorers con adaptadores opcionales a
DeepSeek Harness, Inspect AI o Harbor, sin filtrar sus tipos al dominio.

**Criterios de aceptación de diseño.** Conformance suite común; task/run/result
neutrales; capacidades faltantes declaradas; misma tarea comparable en dos
runners antes de considerar estable un adaptador.

**Métrica de éxito.** Diferencias de runner cuantificadas y ningún cambio del
oracle para cambiar de runtime.

### O-018 — valor longitudinal de ratchets

**Problema.** Un ratchet puede prevenir erosión o simplemente trasladar trabajo;
su beneficio acumulado no se conoce.

**Feature propuesta.** Series por proyecto de baseline, intentos de regresión,
bloqueos correctos, overrides, tiempo de reparación y escapes posteriores.

**Criterios de aceptación de diseño.** Cada cambio de baseline tiene provenance;
se distinguen mejoras, deuda heredada y raises; se controlan tamaño/proyecto y
madurez; análisis no usa solo repos supervivientes.

**Métrica de éxito.** Defectos evitados y costo marginal por ratchet, tendencia de
overrides y relación con escapes reales.

## Oportunidades deliberadamente no priorizadas

- Añadir muchos gates nuevos antes de calificar los existentes.
- Crear un score único comercial sin publicar componentes e incertidumbre.
- Extender a múltiples lenguajes antes de estabilizar evidencia y claims.
- Entrenar o fine-tunear un modelo como primera respuesta: primero hay que medir
  si el uplift proviene de feedback y en qué modos de fallo.
- Integrar una arquitectura completa de plugins de agente en el core.
- Subir o bajar ratchets para facilitar el piloto.

## Criterio de selección para el siguiente incremento

El primer incremento debería ser O-001 + una rebanada estrecha de O-002 aplicada
a dos gates representativos: uno cuantitativo con baseline y uno de detección
binaria. Eso valida el contrato sin diseñar todo el laboratorio por anticipado.
Después, el orden está definido en el [roadmap](05-roadmap.md).
