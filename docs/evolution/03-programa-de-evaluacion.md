# Programa de evaluación del valor de WCT

## Pregunta de investigación

¿Puede un modelo económico, usando reglas, gates y reparación guiada por WCT,
alcanzar una calidad semántica no inferior a la de un modelo de referencia a un
costo total significativamente menor, sin aumentar escapes de seguridad,
arquitectura o mantenibilidad?

La pregunta contiene cuatro dimensiones que deben reportarse por separado:

1. calidad semántica de la solución;
2. defectos que WCT detecta y que deja escapar;
3. costo y latencia totales;
4. confiabilidad de la ejecución y reproducibilidad.

## Hipótesis propuestas

Estas hipótesis deben preregistrarse con modelo, corpus, margen y presupuesto
antes de ver el holdout:

- **H1 — uplift:** modelo económico + WCT completo supera al mismo modelo sin WCT
  en tasa de éxito semántico.
- **H2 — no inferioridad:** modelo económico + WCT completo no es inferior al
  modelo de referencia sin WCT más allá de un margen definido por producto.
- **H3 — eficiencia:** el costo total por tarea semánticamente exitosa es menor
  para el modelo económico + WCT.
- **H4 — seguridad:** el tratamiento no aumenta la tasa de escapes críticos ni
  intentos de bypass exitosos.
- **H5 — mecanismo:** reglas y gates aportan efectos distinguibles; el beneficio
  no proviene únicamente de más tokens o más iteraciones.

No se fija aquí un margen de no inferioridad: debe derivarse del impacto de un
fallo y aprobarse antes de la ejecución. Elegirlo después de observar resultados
invalidaría H2.

## Brazos experimentales

| Brazo | Modelo | Reglas/persuasión | Gates visibles | Reparación | Pregunta aislada |
|---|---|---:|---:|---:|---|
| A0 | económico | no | mínimos neutrales | no guiada | baseline económico |
| A1 | económico | sí | no | no guiada | efecto de instrucciones |
| A2 | económico | mínimo neutral | sí | sí | efecto de prueba/feedback |
| A3 | económico | sí | sí | sí | tratamiento WCT completo |
| A4 | referencia | no | mínimos neutrales | no guiada | baseline de capacidad |
| A5 | referencia | sí | sí | sí | techo e interacción modelo × WCT |

“Sin WCT” no significa sin requisitos ni sin tests necesarios para entregar la
tarea. Significa sin las reglas y gates específicos de WCT. Todos los brazos
reciben la misma especificación funcional, permisos, test público indispensable,
presupuesto y condición de terminación.

Para el piloto puede usarse A0/A3/A4 y reservar la ablación completa hasta haber
calificado el instrumento. Afirmar el mecanismo exige luego A1 y A2.

## Unidad experimental y emparejamiento

La unidad primaria es **tarea × snapshot de repositorio**. Todos los brazos de
una tarea parten del mismo commit y se ejecutan en workspaces aislados. La tarea
es el bloque estadístico: comparar A0 con A3 dentro de la misma tarea controla
gran parte de la diferencia de dificultad.

Cada celda debe repetirse con seeds o sesiones independientes. Si el provider no
garantiza seeds, la repetición sigue midiendo variabilidad operacional. El orden
de brazos se aleatoriza por bloque para reducir efectos de hora, caché o carga.

## Condiciones de equidad

- mismo prompt funcional y anexos visibles;
- misma revisión, dependencias y estado inicial;
- mismas herramientas básicas y política de red;
- mismo límite de tokens, tiempo y tool calls, salvo que el experimento declare
  explícitamente una comparación por costo;
- temperatura, reasoning y parámetros fijados cuando el provider lo permita;
- versión exacta o identificador de snapshot del modelo;
- caché declarada y contabilizada;
- ningún brazo accede a oráculos ocultos ni rubricas privadas;
- sesiones, homes, contenedores y credenciales aislados;
- teardown que comprueba ausencia de estado residual;
- mismo criterio de terminación externa, no solo autodeclaración del agente.

## Corpus de tareas

El corpus debe mezclar cuatro capas:

### C1 — calificación de gates

Micro-repositorios conocidos-buenos y conocidos-malos para cada gate, umbral,
scope, error, `SKIP` y bypass. No miden inteligencia del modelo; miden el
instrumento WCT.

### C2 — tareas de ingeniería curadas

- bugfix con comportamiento observable;
- feature pequeña y feature transversal;
- refactor con invariantes;
- ampliación de tests ante código defectuoso;
- deuda de arquitectura;
- actualización de dependencia sin romper supply chain;
- corrección de seguridad;
- adopción de WCT sobre deuda preexistente;
- tareas ambiguas deliberadamente excluidas o reescritas tras revisión.

### C3 — tareas adversariales

- intento de editar gobernanza o bajar umbrales;
- ocultar un fallo con supresión;
- test que se autoafirma o solo verifica mocks;
- shortcut que pasa tests públicos y falla holdout;
- manipulación de manifests o artefactos stale;
- tool ausente, timeout, crash y resultado parcial;
- dependencia transitiva o licencia incompatible;
- solución sobreconstruida que cumple funcionalmente pero viola límites.

### C4 — secuencias longitudinales

Varias tareas consecutivas sobre el mismo proyecto para medir si los ratchets
detienen la erosión, cuánto cuesta mantenerlos y si el agente aprende a evadirlos.

## Oráculos independientes

El resultado primario debe provenir de una fuente fuera del tratamiento WCT:

- tests ocultos de comportamiento, creados o revisados independientemente;
- invariantes metamórficos;
- casos límite no presentes en ejemplos visibles;
- compilación/ejecución en entorno limpio;
- revisión humana ciega para requisitos que no son automatizables;
- análisis de seguridad dedicado para la clase de tarea;
- mutantes holdout que no forman parte de `G-MUT` visible.

Los gates visibles siguen siendo métricas secundarias valiosas: permiten observar
qué defecto detectó WCT y cuánto costó repararlo. No deben ser el único scorer.

## Calificación de una tarea antes de liberarla

Inspirado por las lecciones de SWE-bench Verified y Terminal-Bench, una tarea no
entra al benchmark porque tenga tests. Debe superar:

1. revisión independiente de especificación y oracle;
2. solución de referencia reproducible;
3. varias ejecuciones limpias del oracle —propuesta inicial: cinco— sin flake;
4. prueba de al menos una solución alternativa válida;
5. pruebas negativas de implementaciones plausiblemente incorrectas;
6. verificación de que los tests no exigen detalles no especificados;
7. estimación de dificultad y presupuesto;
8. revisión de contaminación y procedencia;
9. congelamiento de snapshot, dependencias e imágenes;
10. hash del paquete oculto y aprobación de los revisores.

La [auditoría posterior de SWE-bench Verified](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/)
es una advertencia directa: aun un benchmark revisado puede contener tests
demasiado estrechos, amplios o ambientalmente rotos. El oracle también necesita
red team, versionado y retiros.

## Métricas

### Primarias

- tasa de éxito semántico por tarea;
- tasa de escape de defectos críticos;
- costo total por tarea exitosa;
- diferencia A3−A0 y margen A3 frente a A4.

### Secundarias

- éxito parcial por requisito independiente;
- mutation score visible y kills del set holdout;
- sensibilidad/especificidad de gates por modo de fallo;
- tiempo y tokens hasta primer verde y hasta éxito semántico;
- tool calls, reparaciones y vueltas por el mismo gate;
- tamaño de diff, archivos tocados, dependencias y deuda introducida;
- intentos de bypass detectados y exitosos;
- `SKIP`, `ERROR`, flaky/retry y terminaciones incompletas;
- estabilidad de replay y divergencia entre corridas;
- cobertura del corpus por lenguaje, tarea, dificultad y modo de fallo.

### Métricas derivadas

- **uplift absoluto:** `p(A3) − p(A0)` en puntos porcentuales;
- **uplift relativo:** uplift absoluto dividido por el baseline, siempre junto al
  absoluto;
- **gap recuperado:** fracción de la brecha A4−A0 recuperada por A3;
- **costo por éxito:** costo total de un brazo dividido por éxitos semánticos;
- **eficiencia marginal:** uplift por dólar y por minuto adicional;
- **repair yield:** fallos de gate que terminan en una corrección semánticamente
  válida, no solo en verde;
- **escape conditional:** defectos del holdout dado que todos los gates visibles
  pasaron.

No se recomienda un score único de “calidad WCT”. Calidad, costo, latencia y
seguridad deben mostrarse en una frontera de Pareto. Un índice compuesto puede
ocultar que un brazo compra velocidad con escapes críticos.

## Plan estadístico

- Preregistrar endpoint primario, margen, exclusiones, brazos y stopping rule.
- Usar comparaciones emparejadas por tarea.
- Reportar estimación puntual e intervalo de confianza, no solo `p`-value.
- Para binario emparejado, considerar McNemar; para corpus heterogéneo y
  repeticiones, modelo logístico mixto con tarea como efecto aleatorio.
- Usar bootstrap agrupado por tarea para costo/éxito y métricas no normales.
- Tratar múltiples comparaciones como secundarias o aplicar corrección definida.
- Estimar varianza en el piloto y hacer power analysis antes del estudio
  confirmatorio; no convertir un número arbitrario de runs en garantía.
- Publicar resultados por estrato además del agregado para descubrir efectos
  negativos en seguridad, refactor o tareas largas.
- No imputar un timeout como éxito parcial; su tratamiento debe estar
  preregistrado y reportado.

Los detalles normativos están en
[SPEC-002](specs/SPEC-002-metricas-y-estadistica.md).

## Fases propuestas

### Fase 0 — calificar el termómetro

Objetivo: ningún claim sobre modelos.

- contratos de gate y resultado;
- corpus C1 de positivos/negativos/frontera;
- rutas reales end-to-end;
- completitud y semántica de `SKIP`;
- cierre de scope, configuración y artifacts;
- baseline de falsos positivos/negativos.

### Fase 1 — piloto de factibilidad

Rango de planificación: 12–20 tareas curadas, tres repeticiones y brazos
A0/A3/A4. El número final se determina por costo y varianza, no se usa para una
conclusión confirmatoria. Objetivos:

- depurar contratos y telemetría;
- observar floor/ceiling effects;
- calibrar presupuestos y dificultad;
- estimar varianza para power analysis;
- detectar fallas del oracle antes del holdout.

### Fase 2 — estudio de ablación

Rango inicial: 30–50 tareas calificadas con A0–A5 y repeticiones determinadas
por el piloto. Objetivos:

- estimar uplift causal;
- separar reglas de gates;
- probar no inferioridad y costo/éxito;
- analizar interacción con clase de tarea y modelo.

### Fase 3 — validación externa

- proyectos no usados para diseñar WCT;
- al menos dos equipos y stacks;
- tareas aportadas por mantenedores externos;
- pre-registro y paquete de reproducción;
- revisión ciega de casos discordantes;
- publicación de negativos y limitaciones.

### Fase 4 — observación longitudinal

- cohortes de adopción;
- series antes/después con proyectos comparables;
- defectos escapados a revisión o producción;
- costo de mantenimiento y duración de feedback;
- valor de ratchets a través de múltiples cambios.

## Amenazas a la validez y mitigaciones

| Amenaza | Efecto | Mitigación |
|---|---|---|
| contaminación del modelo con tareas públicas | infla éxito | holdout privado, provenance y tareas nuevas |
| oracle defectuoso | castiga soluciones válidas o acepta inválidas | revisión múltiple, negativos, alternativas y retiros |
| WCT aparece en el scorer primario | medición circular | scorer oculto independiente |
| más tokens en el brazo WCT | confunde tratamiento con compute | presupuestos iguales y análisis costo-equivalente |
| versiones de modelo cambian | serie no comparable | id exacto, ventanas cortas y rebaselines explícitos |
| caché o estado compartido | contaminación entre brazos | homes/workspaces aislados y orden aleatorio |
| un solo repo de ejemplo | baja validez externa | corpus estratificado y proyectos externos |
| snapshots regrabados | normalizan regresiones | invariantes semánticos y revisión de refresh |
| cherry-picking de runs | sesgo de selección | ledger append-only y stopping preregistrado |
| aliases contados como gates distintos | infla cobertura | claims versionados y deduplicados |
| `SKIP` tratado como pass | exagera capacidad | eje de completitud separado |
| reviewer conoce el brazo | sesgo humano | revisión ciega del diff y resultado |
| tests públicos demasiado informativos | overfitting | ejemplos mínimos y holdout de casos/mutantes |

## Decisiones que el piloto debe habilitar

Al finalizar, el equipo debería poder escoger con evidencia entre:

- mantener WCT como herramienta de hardening sin claim de uplift;
- ajustar qué reglas o gates aportan más beneficio por costo;
- recomendar un modelo económico para ciertas clases de tarea;
- definir qué tareas aún requieren un modelo de referencia;
- promover, degradar o retirar gates según calibration;
- invertir o no en un adaptador DeepSeek;
- fijar criterios beta/GA ligados a reproducibilidad y evidencia externa.

El protocolo de contratos está en [SPEC-001](specs/SPEC-001-contratos-experimentales.md),
el ledger en [SPEC-003](specs/SPEC-003-ledger-y-replay.md) y el gobierno del corpus
en [SPEC-004](specs/SPEC-004-gobierno-del-corpus.md).
