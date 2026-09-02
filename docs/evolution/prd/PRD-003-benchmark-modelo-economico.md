# PRD-003 — Benchmark de uplift para modelos económicos

- Estado: propuesta
- Prioridad: P1
- Decisiones relacionadas: [ADR-004](../decisions/ADR-004-plano-de-evaluacion-separado.md) y [ADR-006](../decisions/ADR-006-oraculos-independientes.md)

## Problema

No existe evidencia causal de cuánto mejora un modelo económico al usar WCT ni
si ese tratamiento cierra la brecha frente a un modelo de referencia. Comparar
solo tiers verdes confunde conformidad con calidad y omite costo.

## Objetivo

Medir uplift semántico, gap recuperado, escapes y costo por éxito mediante tareas
emparejadas, oráculos ocultos y ablaciones de reglas/gates/reparación.

## Audiencia

- equipo que decide qué modelo usar por clase de tarea;
- mantenedor que prioriza reglas/gates por impacto;
- usuario que necesita conocer límites y costo real;
- revisor externo que audita claims de eficacia.

## No objetivos

- declarar un “mejor modelo” universal;
- optimizar prompts contra el holdout;
- comparar providers con presupuestos o permisos desiguales;
- usar replay como sustituto de runs reales;
- publicar un leaderboard sin intervalos y task provenance;
- ocultar resultados negativos o tareas retiradas.

## Requisitos experimentales

| ID | Requisito | Criterio |
|---|---|---|
| BM-001 | brazos A0–A5 | tratamiento de cada brazo está versionado y difiere solo como se declara |
| BM-002 | bloqueo por tarea | todos los brazos parten del mismo snapshot |
| BM-003 | repeticiones | cantidad derivada del piloto/power analysis |
| BM-004 | orden | asignación aleatoria reproducible por bloque |
| BM-005 | equidad | permisos, tools y presupuesto iguales o comparación costo-equivalente explícita |
| BM-006 | oracle | oculto, independiente, estable y mismo entre brazos |
| BM-007 | preregistro | endpoint, margen, exclusiones y stopping congelados |
| BM-008 | ceguera | revisión humana no conoce modelo ni brazo |
| BM-009 | costo | tokens facturados/estimados, tiempo, gate compute y retries |
| BM-010 | incertidumbre | intervalos por métrica primaria y análisis emparejado |
| BM-011 | estratos | resultados por tipo, dificultad, riesgo y duración |
| BM-012 | integridad | todos los intentos y desviaciones permanecen en ledger |

## Outcomes

### Primarios

- éxito semántico binario o conjunto preregistrado de requisitos independientes;
- escapes críticos;
- costo total por éxito;
- A3−A0 y A3 frente a A4 con margen aprobado.

### Secundarios

- gates activados, reparación y repair yield;
- tokens/tiempo al primer verde y al oracle pass;
- mutantes visibles y holdout;
- complejidad, diff y dependencias;
- bypass, error, timeout, flake y replay;
- distribución de fallos por taxonomía.

## Experimentos

### Piloto

- propósito: factibilidad y varianza, no claim confirmatorio;
- rango: 12–20 tareas;
- brazos: A0/A3/A4;
- punto inicial: tres repeticiones;
- salida: floor/ceiling, costos, variance y power analysis.

### Ablación confirmatoria

- propósito: mecanismo y no inferioridad;
- rango de planificación: 30–50 tareas, sujeto a power analysis;
- brazos: A0–A5 o subconjunto preregistrado;
- salida: estimaciones, intervalos, discordantes y análisis por estrato.

### Robustez

- budgets por tokens y por costo;
- providers/runtimes alternativos;
- tareas longitudinales;
- tool failure y prompts adversariales;
- sensibilidad a modelos/versiones posteriores.

## Criterios de claim

Un claim “WCT mejora el modelo económico” solo puede publicarse si:

- H1 estaba preregistrada y el intervalo soporta uplift en el corpus declarado;
- no hay incremento material de escapes críticos;
- denominador, fallos, timeouts y exclusiones son visibles;
- costo total y no solo precio por token está incluido;
- perfil WCT, modelo, versión, corpus y fecha acompañan el claim;
- el resultado no depende de una sola tarea, repo o run;
- limitaciones y estratos sin beneficio se publican.

Un claim “no inferior al modelo de referencia” requiere adicionalmente margen
aprobado antes de observar holdout y análisis acorde de no inferioridad.

## Métricas de producto del benchmark

- porcentaje de tareas calificadas;
- runs completados frente a preregistrados;
- integridad de costo y ledger;
- estabilidad del oracle;
- amplitud de intervalos;
- discrepancias de revisión;
- tiempo para reproducir un resultado;
- claims revalidados ante cambio de modelo o corpus.

## Riesgos

- costo de una matriz A0–A5 amplia;
- version drift de modelos durante el estudio;
- task contamination;
- oracle demasiado fácil o implementation-specific;
- conclusions fishing por muchos estratos;
- confundir una muestra de Python con universalidad.

## Criterio de salida

El estudio produce una decisión útil incluso si H1 o H2 no se sostienen: qué
componentes aportan, para qué tareas, a qué costo y con qué escapes. Un resultado
inconcluso por poca potencia se reporta como inconcluso, no como equivalencia.
