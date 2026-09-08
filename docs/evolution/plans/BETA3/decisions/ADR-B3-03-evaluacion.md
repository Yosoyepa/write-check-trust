# ADR-B3-03 — Optimizar coste por solución correcta, con evaluación neutral

> Adenda D0: **aceptable como protocolo exploratorio, sin gasto**.
> [Preparación](../PILOTO-PREPARACION.md) concreta personalAssistant elegido por
> el usuario, Codex autor/revisor en sesiones separadas, tareas candidatas y
> fórmula de tope total. Modelos/tarifas/monto siguen pendientes. Delta no se
> elige de resultados del piloto; se deriva del riesgo de producto antes del
> confirmatorio. Dos sesiones Codex no equivalen a independencia de proveedor.

Estado: **propuesto**, 2026-09-07. No autoriza consumo de API.
Extiende [PRD-003](../../../prd/PRD-003-benchmark-modelo-economico.md) y
[SPEC-002](../../../specs/SPEC-002-metricas-y-estadistica.md); no redefine A0–A5.

## Decisión recomendada

Evaluar el **sistema completo modelo + runtime + contexto + controles +
reparaciones**, distinguiendo el efecto de cada componente cuando el diseño
experimental lo permite. No llamar «modelo mejorado» a una selección de sus
mejores intentos ni a un cambio de precio por token.

Conservar WCT core sin dependencia de una API de modelos. El plano experimental
usa un contrato neutral de tareas, runs y scorers. Un único adaptador probado es
suficiente para el piloto si permite ambos modelos; añadir otro solo por una
necesidad concreta de la comparación. DeepSeek/Inspect son candidatos, no
dependencias aprobadas.

El método toma de las buenas prácticas de evaluación la especificidad de tarea,
el registro y la calibración humana; no acopla beta.3 a la plataforma Evals de
OpenAI. Véase la investigación y sus fuentes, incluida la deprecación anunciada.

## Comparaciones que sí responderán preguntas

| Comparación | Pregunta | Restricción |
|---|---|---|
| A3 − A0 | ¿ayuda WCT beta.2 al modelo económico? | presupuesto y tareas comparables |
| B3 − A3 | ¿ayuda el paquete beta.3? | tratamiento compuesto, no atribuir todo al molde |
| B3 − A4 | ¿se acerca al baseline de referencia y a qué coste? | diferencia no significativa no implica equivalencia |
| Ablación de B3 | ¿cuánto aportan contexto, contrato y feedback? | fase posterior preregistrada, no inferirlo del piloto |

A0/A4 mantienen tests funcionales neutrales y herramientas útiles de la tarea.
Todos reciben los mismos requisitos arquitectónicos y funcionales en lenguaje
natural. El brazo con molde recibe además representación ejecutable/contexto
derivado; no se lo favorece con requisitos secretos nuevos.

## Economía y autorización

Coste total incluye intentos fallidos, inferencia, herramientas, compute y
tiempo humano de revisión. Mostrar también coste marginal y coste de preparar
el molde amortizado a distintos volúmenes de tareas. Una gran inversión inicial
puede no convenir a un repo con dos cambios al mes.

La elección de modelo se hace por clase de tarea y fecha. No se fija en este
dossier un proveedor ni un «más barato» universal. Antes del piloto se aprueban
model IDs/versiones, tarifa vigente, límites por run y tope total.

No habrá compras ni inferencias de pago sin esa puerta. Presupuesto agotado es
resultado terminal visible; un escalamiento a otro modelo no borra ni excluye
el coste previo. Escalación automática se difiere hasta conocer la frontera de
coste/calidad y contar con un presupuesto explícito.

## Evidencia y condición de reversión

Un piloto con intervalos amplios es exploratorio. Publicar ahorro con calidad
comparable requiere éxito independiente, escapes y márgenes preregistrados;
el resultado negativo también se publica. Si el molde aumenta coste sin reducir
errores útiles, revisar su rigidez/contexto antes de añadir más gates.

[EVALS](../EVALS.md) define tamaños iniciales de planificación, no garantías
estadísticas, y la diferencia entre una beta publicable y un claim de ahorro
confirmado.
