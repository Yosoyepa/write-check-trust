> **Entrada vigente:** [integración de CND-74E0](INTEGRACION-P01.md).
> Para encargos posteriores leer [ADR-SH-02](ADR-SH-02.md),
> [entrega v2](ENTREGA-v2.md), [molde v2](MOLDE-WCT-v2.md) y
> [prompt v2](PROMPT-CODER-v2.md). P01/R0/R1 conservan sus contratos originales.
> El resto de este documento describe la preparación histórica, no el estado
> actual de promoción ni una orden de ejecutar otra vez el prompt de P01.

# Beta.3 — WCT mejora WCT, con evaluación ciega

Fecha: 2026-09-07. Base inspeccionada: `8de9107184288f1aa72c9578a14913686c47ad7c`
(tag beta.2). **Diseño entregado; producto e instrumentos nuevos aún no implementados.**

## Dirección que cambia con este encargo

El usuario pide desarrollar beta.3 sobre el propio WCT, usando un coder cuyo
modelo permanecerá **oculto al arquitecto/evaluador**, y evaluar después el
coste por tarea con datos de OpenRouter. No se pide escoger modelo ni aplicar
un filtro monetario de aprobación. No se ejecutaron llamadas de inferencia.

El primer sujeto pasa a ser **`tools/wct`**, no `src/example` ni
personalAssistant. El piloto externo de D0 se conserva como segunda etapa de
generalización. El ensayo interno no lo satisface por sustitución.

Hay dos productos distintos:

1. **WCT candidato:** piezas reales que añaden evidencia, moldes y contexto.
2. **Expediente de evaluación:** expectativas, revisión, versiones, intentos y
   costes que el candidato no puede reescribir para darse por aprobado.

El resultado deseado no es «el modelo siempre escribe bien». Es identificar
qué contratos y controles permiten aceptar determinadas tareas a calidad
conocida, cuántos defectos escapan y cuánto trabajo cuesta corregirlos.

## Primera entrega implementable

**SH-P01: comparar identidades esperadas, recogidas y ejecutadas.** Una pieza
pura, sin procesos, archivos, CLI nueva, migración ni cambio de umbrales.
Detecta vacuidad, omisiones, sustituciones y duplicados. Devuelve `match`, no
`PASS` ni `accredited`: aún no ha observado la ejecución de ningún test.

El [contrato P01](P01-IDENTIDADES.md) fija API, ejemplos, límites, archivos y
DoD. El [prompt del coder](PROMPT-CODER.md) autoriza **solo esa rebanada cuando
el usuario lo envíe como encargo**, no toda beta.3. El modelo puede permanecer
ciego; los datos de facturación no bloquean la revisión funcional.

## Paquete de trabajo

| Documento | Decisión o trabajo que habilita |
|---|---|
| [ADR-SH-01](ADR-SH-01.md) | automejora sin autoaprobación; precedencia respecto de D0 |
| [Gobernanza y contratos](GOBERNANZA.md) | autoridad, negocio de la evidencia, versiones, aislamiento y bless |
| [Molde del harness](MOLDE-WCT.md) | límites de las piezas nuevas; relación con el pack hexagonal público |
| [Piezas y ensamblaje](PIEZAS.md) | cortes P01–P10, consumidores reales, puertas y salida beta.3 |
| [P01](P01-IDENTIDADES.md) y [Gherkin](GHERKIN-P01.md) | primer encargo completo y casos aprobables |
| [Evaluación ciega](EVALUACION-CIEGA.md) | desarrollo vs experimento; modelo secreto y coste posterior |
| [Revisión y aprendizaje](REVISION-Y-FEEDBACK.md) | rúbrica, severidad, retroalimentación y regresiones del harness |
| [Registros](REGISTROS.md) | plantillas de tarea, intentos, recibos privados y handoff |
| [Prompt](PROMPT-CODER.md) | siguiente acción concreta, sin reabrir toda la planificación |
| [Evidencia de preparación](EVIDENCE.md) | comprobaciones realizadas y comprobaciones pendientes |

## Lo que ya sabemos y lo que no

- **Observado ahora:** suite `347 passed`; las cifras 334/345 de informes
  anteriores pertenecen a otros cortes. El detalle está en EVIDENCE.
- **Observado:** `lint-imports` conserva 4 contratos sobre 9 archivos del
  ejemplo. No acredita la arquitectura de `tools/wct`. Tipos y cobertura sí
  incluyen el harness; no todos los gates comparten ese alcance.
- **Observado:** la aceptación histórica genera un test por escenario y recorre
  sus filas dentro de él. No tenemos hoy terminales independientes por fila.
- **Por construir:** captura independiente por ejecución, pertenencia de LCOV,
  compilador del molde, contexto derivado y un scorer separado calificado.
- **No medido:** uplift de calidad, ahorro por tarea, no inferioridad frente a
  otro modelo ni resistencia del evaluador a código hostil.

## Puertas prácticas

1. Aprobar P01 enviando su prompt; preparar una copia limpia de implementación
   sin tocar esta rama documental ni el trabajo ajeno. El usuario custodia el
   modelo; la revisión recibe solo un identificador ciego.
2. El coder entrega diff, tests y registro de todos sus intentos. El arquitecto
   revisa el contrato; un verifier distinto ejecuta las comprobaciones sobre
   ese mismo diff congelado. Si comparten host, declarar esa limitación.
3. Solo con dictamen y revisión humana del diff exacto: decisión de bless,
   commit/PR/CI. Ninguno de esos actos está ejecutado por este dossier.
4. Calificar y promover la pieza antes de usarla para evaluar otra. Congelar
   versión y oráculo durante cada lote comparativo; aprender entre lotes.

La aprobación de un diseño no certifica una implementación futura. Usar WCT
durante el desarrollo aporta evidencia de utilidad, pero el efecto causal se
estudia con tareas emparejadas, controles y resultados independientes.
