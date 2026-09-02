# ADR-006 — Usar oráculos independientes y holdout privado

- Estado: **Propuesto**
- Fecha: 2026-09-01
- Decisores requeridos: mantenedor, responsable de evaluación y custodio del corpus
- Alcance: metodología de evaluación

## Contexto

El agente ve reglas, tests públicos y diagnósticos de gates. Esa visibilidad es
precisamente la intervención que WCT desea estudiar. Si el éxito se define solo
por poner verdes esas señales, no se conoce la tasa de overfitting ni los
defectos que quedan fuera del scope.

Los benchmarks externos tampoco son automáticamente válidos. La experiencia de
SWE-bench Verified demuestra que tareas revisadas pueden contener tests estrechos,
amplios o rotos. El oracle debe calificarse y gobernarse igual que el tratamiento.

## Decisión propuesta

El endpoint primario de calidad será un oracle que:

- no sea visible al agente;
- sea idéntico entre brazos;
- se ejecute después del tratamiento en entorno limpio;
- mida requisitos observables, no detalles accidentales de implementación;
- tenga solución de referencia, negativos plausibles y alternativas válidas;
- esté versionado, hasheado y revisado independientemente;
- pueda retirarse sin borrar resultados históricos.

El oracle podrá combinar tests ocultos, invariantes metamórficos, mutantes
holdout, análisis especializado y revisión humana ciega. Ninguna modalidad basta
por sí sola para todas las tareas.

Se mantendrán splits `dev`, `validation` y `holdout`. El holdout no se utilizará
para diseñar prompts, gates, umbrales o criterios de exclusión.

## Consecuencias positivas

- Mide generalización y defect escape, no solo conformidad al feedback visible.
- Permite calcular escapes condicionados a tier verde.
- Reduce Goodhart y comparaciones sesgadas entre brazos.
- Hace explícita la calidad del propio benchmark.

## Costos y riesgos

- Custodia, acceso y rotación del holdout.
- Mayor esfuerzo de revisión humana y creación de alternativas válidas.
- Riesgo de filtración o contaminación del modelo.
- Algunos requisitos humanos tendrán agreement imperfecto.

## Controles requeridos

- acceso mínimo y auditado;
- task packages separados del paquete privado;
- hash visible sin contenido;
- revisión ciega del diff;
- ledger de contaminación y exposición;
- freeze antes del confirmatorio;
- procedimiento de challenge, adjudicación y retiro;
- publicación del denominador y tareas excluidas.

## Alternativas descartadas

### Usar solo tests públicos

Descartada porque mide adaptación directa y permite soluciones estrechas.

### Usar revisión humana no ciega

Descartada como única fuente por costo, variabilidad y sesgo por modelo/brazo.

### Usar un benchmark público sin curación adicional

Descartada por contaminación, drift ambiental y posible inconsistencia del oracle.

## Condición de aceptación

Aprobar [SPEC-004](../specs/SPEC-004-gobierno-del-corpus.md), custodio del holdout,
política de incidentes y rubric de calificación antes de ejecutar el primer run
que se pretenda usar como evidencia de producto.
