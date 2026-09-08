# PRD beta.3 — Confianza acotada para código de modelos económicos

> Primer caso de uso actualizado por el usuario: automejora de `tools/wct`
> con modelo oculto al evaluador, contratos revisados y costes reconciliados
> después. [ADR-SH-01](SELF-HOSTING/ADR-SH-01.md) y
> [piezas SH-P01–P10](SELF-HOSTING/PIEZAS.md) concretan el camino. El molde
> local de desarrollo no sustituye el pack de producto hexagonal ni demuestra
> todavía ahorro, generalización o corrección universal.

Estado: propuesto. Responsable de producto propuesto: `yosoyepa`.
Depende de aprobar [ADRs](README.md), alcance, corpus y presupuestos por separado.

## Problema de usuario

Quiero delegar cambios pequeños de mi codebase a un modelo de menor coste sin
tener que rediseñar, corregir o auditar manualmente todo lo que produce.
Necesito saber qué partes encajan con mi arquitectura y qué comportamiento se
verificó, además del coste real hasta una solución aceptable.

Hoy la plantilla ayuda a imponer disciplina, pero persisten adaptación manual,
suposiciones del ejemplo, artefactos sin provenance integral y falta de una
medición causal del beneficio. Más reglas indiscriminadas pueden aumentar
falsos positivos, contexto y coste en vez de mejorar el resultado.

## Propuesta de valor y límites

**Una especificación arquitectónica ejecutable reduce decisiones repetitivas;
una evidencia comprobable limita qué se puede dar por aprobado; un experimento
independiente permite decidir cuándo merece la pena usar un modelo económico.**

No prometer «cualquier modelo produce siempre código correcto». Prometer, si
los criterios se cumplen: «este cambio satisface este contrato, para este
alcance, con estas pruebas y limitaciones». La calidad del requisito, los
efectos distribuidos y la adecuación al negocio conservan revisión humana.

## Usuarios y recorridos

| Usuario | Recorrido mínimo | Resultado útil |
|---|---|---|
| Mantenedor de repo existente | inventario → mapeo propuesto → revisión → medición sin cambiar src | sabe coste/deuda y si el molde encaja antes de adoptarlo |
| Equipo con proyecto nuevo | elegir molde validado → mapear módulos → aprobar contratos | estructura verificable sin imponer lógica de negocio generada |
| Desarrollador con modelo económico | tarea pequeña → contexto comprobado → feedback → reparación acotada | cambio evaluable o escalación explícita, nunca aprobación por autoinforme |
| Arquitecto/verificador | revisar contrato, excepciones y evidencia del mismo árbol | distingue conformidad, pruebas ejecutadas y zonas no cubiertas |

## Features delimitadas

| Feature | Prioridad y alcance | Criterio de aceptación de producto | Dependencias / precedente |
|---|---|---|---|
| B3-01 Evidencia mínima | P0; envoltura versionada para capacidades seleccionadas y cierre explícito | otra configuración/árbol, artefacto viejo, tool ausente o inventario incompleto no producen un cierre acreditado | O-001/O-006, SPEC-B3-02 |
| B3-02 Molde ejecutable | P0; un `hexagonal-python`, más traducción compatible del perfil beta.2 | instrucciones, contratos, scope y reporte derivan del mismo plan; ningún módulo del scope queda sin disposición | F01–F03, SPEC-B3-01 |
| B3-03 Adopción revisable | P0 para el uso en repos existentes; mapeo y diff, sin refactor automático | dos layouts distintos conservan src byte a byte en planificación; conflictos bloquean aplicación | O-014, ciclo adopt ya existente |
| B3-04 Contexto y feedback de tarea | P1; rutas/roles/símbolos del repo, restricciones y errores estructurados | API/contexto obsoleto se señala; error produce diagnóstico útil y no permite rebajar regla | SPEC-B3-02; no runtime LLM nuevo |
| B3-05 Calificación del molde y piloto | P0 para claims de confianza; P1 para corridas de pago | fixtures buenos/malos por capacidad; estudio emparejado con coste por éxito, fallos y resultado independiente | PRD-002/003; EVALS |
| B3-06 Cierre operativo | P0 antes de publicar; pruebas de migración, orden, canal y SHA final | prerelease real, assets/evidencia ligados al SHA y límites publicados | incidente metadata beta.2, PLAN |

G1b es un trabajo previo con su propia especificación y puerta de aprobación;
no se renombra como una feature nueva ni se introduce silenciosamente en B3-01.

## MVP obligatorio frente a extensiones

**MVP:** Python; un paquete de negocio por instancia; roles configurables en
varias carpetas dentro de una raíz de fuente declarada; dependencias de imports,
puertos con contratos observables; compatibilidad beta.2; planificación de
adopción; evidencia de capacidades seleccionadas; piloto reportable.

**Diseñado pero no comprometido:** múltiples bounded contexts, monorepo con
varias raíces, overlay web/persistencia, selección automática de modelo y
escalación automática. Beta.3 debe rechazarlos como no soportados cuando excedan
el contrato, no simular que están cubiertos. Las composiciones descritas en la
SPEC son tests de diseño y próximos candidatos, no soporte publicado.

**Fuera:** catálogo libre de plugins, marketplace, transformación masiva del
codebase, ejecución arbitraria desde packs, nuevos lenguajes, fine-tuning,
leaderboard público, benchmark completo dentro de cada PR, aceptación sin humano
de cambios críticos o un framework propio de agentes.

## Qué mediremos

| Dimensión | Medida | Interpretación |
|---|---|---|
| Adaptación | tiempo hasta mapeo aprobado y primer resultado completo; módulos sin clasificar | ahorro operativo, no éxito de negocio |
| Arquitectura | violaciones requeridas detectadas; alternativas válidas rechazadas | sensibilidad/FPR dentro del corpus del molde |
| Comportamiento | éxito de tareas frente a oráculo independiente; escapes críticos | outcome de calidad, separado de gates visibles |
| Economía | coste total/éxito y minutos de intervención humana | identifica falsos ahorros por retries/revisión |
| Usabilidad | reparaciones por tarea, errores no accionables y escalaciones | más gates no es mejor si no se pueden usar |
| Integridad | evidencias válidas/completas; errores y SKIP por capacidad | no es un porcentaje genérico de «confianza» |

Los umbrales de seguridad, ahorro útil y no inferioridad **no están aprobados**.
El piloto estimará coste/varianza; la fase confirmatoria necesitará márgenes
predefinidos. Cero escapes observados no significa riesgo cero.

## Riesgos y decisiones que evitan sobreconstrucción

- Molde excesivamente rígido: aceptar múltiples implementaciones válidas y rutas
  equivalentes; separar contrato de ejemplo.
- Compilador y detector con el mismo error: fixtures etiquetados a mano y pruebas
  por CLI productivo; no generar expected desde el mismo compilador.
- Autoengaño por tests que el agente cambia: oráculo fuera de su alcance y runner
  de evaluación independiente.
- Coste de validación mayor al ahorro de inferencia: medir compute, retries y
  revisión, no solo tokens; no obligar mutación completa en cada edición.
- Greenfield exitoso, brownfield imposible: incluir un repo existente con deuda
  clasificada y tiempos reales en la prueba de adopción.
- Requisitos ambiguos: pedir una decisión y detener esa tarea; el molde no debe
  inventar restricciones del negocio.

## Condición de éxito beta.3

Un usuario puede mapear dos layouts Python equivalentes al mismo molde, recibir
diagnósticos correctos ante desviaciones reales, conservar su implementación y
ver qué se comprobó. El equipo puede ejecutar y auditar un piloto que determine
si el sistema reduce coste a calidad comparable, aunque el resultado sea
negativo o inconcluso. No se exige que el experimento confirme la hipótesis para
publicar una herramienta honesta; sí para anunciar el beneficio como hecho.
