# ADR-005 — Calificar los gates antes de usarlos para claims sobre modelos

- Estado: **Propuesto**
- Fecha: 2026-09-01
- Decisores requeridos: mantenedor de WCT y verificador independiente
- Alcance: orden de evidencia; no autoriza cambiar gates o umbrales

## Contexto

Un benchmark no puede ser más confiable que sus instrumentos. La auditoría
encontró diferencias entre algunas promesas y sus rutas efectivas: coverage sin
ratchet conectado, scopes parciales, property tests no aislados, red team con
reconocedores paralelos, aceptación potencialmente vacua, configuración sin
consumidor y `SKIP` tratado como no bloqueante.

Ejecutar cientos de corridas de modelos antes de resolver esas incertidumbres
produciría números precisos sobre un instrumento no calibrado.

## Decisión propuesta

Ningún gate será usado como evidencia cuantitativa de uplift, ni descrito como
“calificado”, hasta que su claim versionado supere una suite end-to-end por el
entrypoint productivo.

La calificación exige, como mínimo:

- control conocido-bueno;
- defecto conocido-malo;
- fronteras del umbral;
- herramienta ausente, error y timeout;
- artefacto stale;
- cambio de configuración;
- intento de bypass;
- alternativa válida para medir falsos positivos;
- scope y exclusiones verificables;
- semántica de estado y completitud.

Los resultados se publicarán por claim mediante confusion matrix. Un alias no
cuenta como medición independiente. Las reglas históricas o humanas se etiquetan
como evidencia de proceso en vez de enforcement completo.

## Orden acordado

1. Definir claim y evidencia mínima.
2. Crear fixture que fallaría ante una implementación plausible incorrecta.
3. Ejecutar la ruta real.
4. Medir sensibilidad, especificidad y fronteras.
5. Resolver o declarar limitaciones.
6. Solo entonces incluir el gate como outcome del estudio de modelos.

## Consecuencias positivas

- Reduce falsos claims y localiza gaps antes de gastar tokens.
- Convierte escapes en regresiones reproducibles.
- Hace observable la diferencia entre gate útil, heurístico y no calificado.
- Permite retirar o degradar un gate sin cuestionar todo WCT.

## Costos y riesgos

- Retrasa el benchmark de modelos.
- Los fixtures end-to-end son más lentos y ambientales que tests unitarios.
- Algunas herramientas externas no permiten un oracle perfecto.
- La calibración local no garantiza validez en todos los repos o lenguajes.

## Alternativas descartadas

### Confiar en los tests unitarios actuales

Descartada porque una función interna puede pasar mientras el entrypoint,
configuración o ensamblaje está roto.

### Aceptar `30/30` red team como calibración completa

Descartada porque la mayoría de casos no ejecuta el gate que pretende validar.

### Calificar solo después de encontrar discrepancias en el benchmark

Descartada porque contamina el holdout, desperdicia corridas y favorece cambios
post hoc.

## Condición de aceptación

Aprobar el alcance de [PRD-002](../prd/PRD-002-calificacion-de-gates.md), la
clasificación E/M/H/P/U y una política que prohíba elevar un claim por encima de
la evidencia de su fixture.
