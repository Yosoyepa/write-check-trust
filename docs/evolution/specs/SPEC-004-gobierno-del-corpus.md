# SPEC-004 — Gobierno del corpus de tareas y oráculos

- Estado: propuesta
- Naturaleza: política de evaluación, no implementación

## Objetivo

Crear un corpus que discrimine soluciones correctas de incorrectas, resista
contaminación y permita retirar errores sin reescribir el pasado.

## Capas y splits

### Capas

- **C1 gate qualification:** micro-fixtures públicos o internos; no puntúan modelo.
- **C2 ingeniería curada:** tareas funcionales representativas.
- **C3 adversarial:** bypass, seguridad, configuración y evidencia.
- **C4 longitudinal:** secuencias sobre un mismo proyecto.

### Splits

| Split | Visibilidad | Uso permitido |
|---|---|---|
| dev | prompt, ejemplos y oracle parcial públicos | desarrollar contratos y agents |
| validation | prompt visible, oracle custodiado | seleccionar protocolo antes del freeze |
| holdout | prompt liberado por run, oracle privado | estimación confirmatoria |
| retired | preservado, no puntúa claims nuevos | historial, análisis de fallos y entrenamiento si licencia permite |

Mover una tarea entre splits crea versión/evento y registra exposición. No se
“descontamina” una tarea volviéndola privada.

## Ciclo de vida

1. **propuesta:** provenance, licencia y modo de fallo.
2. **redacción:** especificación observable y restricciones.
3. **oracle:** tests/invariantes/review rubric separados.
4. **challenge:** negativos, alternativa válida y red team del oracle.
5. **repetición:** solución de referencia ejecutada varias veces en limpio.
6. **revisión:** al menos dos revisores; tercero para desacuerdo material.
7. **freeze:** hashes, imagen, lock, presupuesto y split.
8. **uso:** ledger de exposiciones y ejecuciones.
9. **revalidación:** por tiempo, tool/model drift o incidente.
10. **retiro:** razón, impacto en resultados y versión sustituta.

## Checklist de calificación

### Especificación

- Describe comportamiento observable y límites.
- Todo requisito que puntúa está expresado o es una expectativa de seguridad
  universal aprobada.
- No depende de conocimiento tácito del autor.
- Permite más de una implementación cuando el problema no exige una sola.
- Tiene criterio de terminación y presupuesto razonable.

### Oracle

- Solución de referencia pasa en entorno limpio.
- Al menos una alternativa válida pasa cuando sea aplicable.
- Implementaciones plausiblemente incorrectas fallan por la razón esperada.
- Tests no inspeccionan estructura interna innecesaria.
- Casos límite no son copias literales de ejemplos visibles.
- Requisitos críticos se puntúan separadamente.
- Logs no revelan el holdout durante el tratamiento.

### Estabilidad

- Propuesta inicial: cinco ejecuciones consecutivas de la solución de referencia
  sin flake, inspirada por prácticas de Terminal-Bench; el número puede revisarse
  con evidencia.
- Imágenes y dependencias usan digests/locks.
- No depende de servicios externos mutables salvo mock/fixture congelado.
- Tiempo y recursos tienen margen respecto a la solución de referencia.
- Plataformas soportadas están enumeradas.

### Procedencia y contaminación

- Licencia permite el uso previsto.
- Fuente, issue y commit están registrados.
- Se busca aparición pública del task/oracle cuando sea posible.
- Se declara si la tarea proviene de benchmark conocido.
- No se afirma ausencia total de contaminación; se clasifica el riesgo.

## Roles

| Rol | Owns | No debe ser único owner de |
|---|---|---|
| task author | especificación inicial y rationale | aprobación final del oracle |
| oracle author | tests/invariantes | scoring de un run cuyo brazo conoce |
| reviewer | consistencia spec/oracle | edición silenciosa post-freeze |
| challenger | alternativas y negativos | decisión unilateral de ignorar finding |
| custodian | holdout/acceso/hashes | análisis con desenmascaramiento temprano |
| adjudicator | disputas y retiros | autoría única de la tarea disputada |
| analyst | plan y estimadores | cambio post hoc del corpus |

En equipos pequeños una persona puede ocupar más de un rol, pero la falta de
independencia se declara y el confirmatorio requiere revisión externa.

## Rubric de revisión

Cada revisor responde de forma independiente:

- ¿la tarea es resoluble con la información visible?;
- ¿cada test deriva de un requisito válido?;
- ¿hay tests demasiado estrechos o amplios?;
- ¿una alternativa razonable sería penalizada?;
- ¿los negativos representan errores plausibles?;
- ¿el entorno es estable y reproducible?;
- ¿el presupuesto permite la solución sin ventaja específica de un modelo?;
- ¿el riesgo/criticidad está bien clasificado?;
- ¿hay contaminación o conflicto de interés?;

Se conserva acuerdo y desacuerdo, no solo el veredicto final.

## Taxonomía de modos de fallo

La taxonomía F1–F15 del proyecto debe tener fuente única y versión. Para el
benchmark puede ampliarse sin reutilizar IDs con otro significado. Toda tarea
declara modos objetivo y observados; los nuevos escapes pueden crear una clase,
pero no recodificar resultados antiguos silenciosamente.

Dimensiones adicionales:

- funcional, arquitectura, seguridad, supply chain, test, mantenibilidad;
- prevención, detección, reparación o escape;
- visible, holdout o revisión humana;
- severidad e impacto;
- herramienta/entorno/modelo implicado.

## Control de contaminación

- Ledger de quién accedió a prompt, solución y oracle.
- Holdout no entra en prompts, repos visibles, logs del agente ni replay público.
- Tareas públicas se usan preferentemente para dev/validation.
- Tareas nuevas o transformaciones sustanciales se reservan para holdout.
- Una fuga mueve la tarea a exposed/retired y activa análisis de impacto.
- Cambiar nombres o literales no convierte automáticamente una tarea pública en
  no contaminada.
- Se reporta desempeño con y sin tareas de riesgo alto de contaminación.

## Challenge y adjudicación

Un participante puede impugnar una tarea por underspecification, test inválido,
entorno roto o solución alternativa. La adjudicación:

1. se hace ciega al brazo/modelo cuando sea posible;
2. reproduce el caso;
3. decide mantener, corregir para versión futura o retirar;
4. no reescribe el oracle congelado de runs pasados;
5. publica impacto sobre estimaciones;
6. añade fixture para la clase de error del benchmark.

## Retiro y versionado

Motivos de retiro:

- oracle defectuoso;
- especificación insuficiente;
- contaminación;
- dependencia o imagen irrecuperable;
- flake persistente;
- cambio de seguridad/licencia;
- tarea redundante o sin poder discriminador.

El retiro no borra runs. Los informes nuevos excluyen la versión con rationale y
recalculan sensibilidad; los informes históricos conservan el set original y
añaden errata.

## Métricas de salud del corpus

- tareas por capa, clase, dificultad, plataforma y modo de fallo;
- tasa de aceptación/rechazo en revisión;
- agreement entre revisores;
- alternativas válidas y negativos por tarea;
- flake rate y tiempo de oracle;
- challenges, uphold/retire y causa;
- contaminación conocida/sospechada;
- floor/ceiling por modelo y brazo;
- antigüedad desde revalidación;
- concentración por repo/autor/stack;
- casos discordantes que aportan nuevo modo de fallo.

## Criterio para abrir holdout

El holdout confirmatorio solo se abre cuando:

- protocolo, arms y análisis están congelados;
- gates usados como métricas están calificados;
- tasks de validation no muestran defectos sistémicos del oracle;
- power/costo fueron aprobados;
- acceso y respuesta a incidentes están operativos;
- exclusiones y stopping rule tienen digest;
- reviewers confirman que el score no filtra tratamiento.

Si una condición falla, se corrige en dev/validation y se genera un nuevo
preregistro; no se usa el holdout como entorno de depuración.
