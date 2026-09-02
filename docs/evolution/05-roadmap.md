# Roadmap propuesto de evolución

## Principio de orden

El roadmap está organizado por **evidencia desbloqueada**, no por cantidad de
features. Cada horizonte tiene una pregunta de salida. No se asignan fechas sin
conocer capacidad del equipo; los rangos de tareas del benchmark son hipótesis de
planificación.

## Horizonte 0 — congelar claims y resolver contradicciones

**Pregunta de salida:** ¿sabemos exactamente qué promete y qué mide cada gate?

Entregables de análisis/decisión:

- inventario versionado claim → regla → gate → tier → scope → baseline;
- clasificación E/M/H/P/U;
- ADR-004, ADR-005 y ADR-006 aprobados o sustituidos;
- definición de perfil local frente a perfil completo;
- decisión de qué claves de configuración se activan, deprecian o retiran;
- taxonomía F1–F15 con fuente única;
- threat model del plano de evaluación y de los oráculos ocultos.

Exit criteria:

- ninguna regla se presenta como automatizada sin indicar fuerza y límites;
- aliases y gates standalone no inflan el conteo;
- contradicciones de documentación tienen owner y resolución propuesta;
- no se ha cambiado un umbral para hacer verde el estado.

## Horizonte 1 — calificar el instrumento

**Pregunta de salida:** ¿los gates detectan las condiciones que dicen detectar a
través de la ruta productiva?

Secuencia:

1. O-001 contrato de evidencia;
2. O-002 framework de fixtures end-to-end;
3. O-003 coverage/mutation/property;
4. O-004 aceptación no vacua;
5. O-005 configuración efectiva;
6. O-006 completitud/perfiles;
7. O-012 licencias y O-013 random/flakes cuando sus contratos estén listos.

Exit criteria:

- matriz positivo/negativo/frontera para todo claim P0;
- falsos positivos/negativos publicados;
- resultados ligados a commit, config y artefacto;
- `full` no oculta capacidades ausentes;
- scopes del core y template son explícitos;
- red team ejecuta gates reales;
- aceptación no puede pasar con cero trabajo aplicable;
- un informe externo puede auditar por qué pasó cada gate.

**Gate de decisión:** si la calificación revela baja sensibilidad o alto costo de
reparación, priorizar rediseñar o degradar esos gates antes de medir modelos.

## Horizonte 2 — construir el laboratorio mínimo

**Pregunta de salida:** ¿podemos repetir una comparación A0/A3 sin intervención
manual ni contaminación?

Secuencia:

1. O-007 contratos neutrales y runner mínimo;
2. O-009 primer corpus curado y holdout;
3. O-010 ledger de trayectoria/costo;
4. O-011 replay y smokes;
5. revisión de ADR-007 y PoC DeepSeek solo si reduce trabajo neto.

Exit criteria:

- tarea, experimento y run tienen manifests versionados;
- workspaces y homes están aislados;
- scorer oculto corre después y fuera del tratamiento;
- evento, patch, gates, oracle y costo se unen por run id;
- una ejecución grabada se reproduce sin API;
- los datos exactos y estimados se distinguen;
- el paquete de reproducción no expone el holdout al agente.

## Horizonte 3 — piloto

**Pregunta de salida:** ¿el protocolo es operable y qué varianza/costo tiene?

Diseño de partida:

- 12–20 tareas calificadas;
- A0/A3/A4;
- tres repeticiones como punto inicial;
- tareas de bug, feature, refactor, tests y adversarial;
- análisis descriptivo, sin marketing confirmatorio.

Exit criteria:

- ≥95 % de runs cierran su ledger o explican la falta;
- cero exposición conocida del holdout;
- oracle estable antes del uso;
- presupuestos no producen floor/ceiling generalizado;
- varianza y costo permiten power analysis;
- casos discordantes revisados de forma ciega;
- protocolo y exclusiones ajustados antes de congelar el confirmatorio.

**Gate de decisión:** si A3 no muestra señal o su costo domina, estudiar A1/A2 en
pequeño antes de escalar; no ampliar el corpus para “buscar significancia”.

## Horizonte 4 — estudio confirmatorio de ablación

**Pregunta de salida:** ¿qué uplift causa WCT y en qué tareas compensa su costo?

Diseño:

- corpus y número de repeticiones definidos por power analysis;
- rango inicial de planificación de 30–50 tareas;
- A0–A5 o subconjunto preregistrado justificadamente;
- holdout congelado;
- análisis emparejado, intervalos y margen de no inferioridad;
- publicación de costo/éxito y escapes por estrato.

Exit criteria:

- H1–H5 resueltas como soportadas, no soportadas o inconclusas;
- resultados negativos incluidos;
- tabla de tareas/modelos excluidos con razón preregistrada;
- paquete reproducible y hashes públicos cuando la confidencialidad lo permita;
- claims comerciales limitados al corpus, versión y perfil evaluados.

## Horizonte 5 — validez externa y GA

**Pregunta de salida:** ¿el efecto sobrevive fuera del proyecto y del equipo que
diseñó WCT?

Secuencia:

- O-014 observatorio en cohortes;
- O-015 postmortems y regresiones;
- O-017 adaptadores y corpus externos;
- O-018 ratchets longitudinales;
- O-016 segundo lenguaje solo si existe demanda y capacidad.

Exit criteria sugeridos para una afirmación GA basada en evidencia:

- reproducción por al menos dos equipos externos;
- más de un repo y clase de tarea con beneficio consistente;
- perfil completo reproducible sin `SKIP` ocultos;
- tasas conocidas de escape y falsos positivos;
- procedimiento de retiro de tareas y respuesta a contaminación;
- historial de modelo/versiones y revalidación definido;
- límites de seguridad, costo y aplicabilidad publicados;
- adopción y mantenimiento no dependen de una sola persona.

## Dependencias críticas

| Dependencia | Bloquea | Razón |
|---|---|---|
| claims de gate versionados | todo el benchmark | evita medir señales ambiguas |
| oráculo independiente | H1–H5 | evita circularidad |
| configuración efectiva | comparabilidad | dos runs deben ejecutar el mismo tratamiento |
| ledger append-only | reproducibilidad | evita cherry-picking y pérdida de trayectoria |
| task qualification | validez | el benchmark también puede estar roto |
| aislamiento | causalidad y seguridad | elimina estado cruzado y exposición del holdout |
| tabla de precios/versiones | costo/éxito | precios y modelos cambian con el tiempo |

## Registro de decisiones por horizonte

Al cerrar cada horizonte se debe conservar:

- decisión tomada y alternativas descartadas;
- evidencia que la soporta;
- criterios que no se cumplieron;
- riesgos residuales;
- cambios al protocolo antes de abrir el siguiente;
- versión de corpus, perfil WCT y modelos;
- owner de revisión y fecha de revalidación.

Este registro impide que un piloto exploratorio se convierta retrospectivamente
en evidencia confirmatoria.
