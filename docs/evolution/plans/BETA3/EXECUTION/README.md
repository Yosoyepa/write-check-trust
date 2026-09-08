# Ejecución beta.3 — contrato de la campaña y puertas pendientes

Fecha local: 2026-09-07. Encargo: ejecutar beta.3 con varios subagentes y
revisión del arquitecto, recogiendo feedback para decidir después beta.4.
**Estado de esta primera ola: preparación y revisión de contratos; beta.3 no
está completa.** El encargo general no se interpreta como bless ni aprobación
de escenarios futuros; se distingue del bless de P01 observado después.

## 1. Decisión de arquitectura y autoridad

Se conserva el alcance funcional de [PIEZAS](../SELF-HOSTING/PIEZAS.md): P01–P06
construyen evidencia; P07–P09 entregan molde, consumidores, adopción y contexto;
P10 califica y prepara salida. Terminar solo evidencia no permite llamar
«beta.3 completa» a un producto sin moldes operativos.

La dirección y uso de subagentes están autorizados por el encargo actual. Las
puertas concretas de AGENTS/PROC-003, SEC-005 y gobernanza siguen aplicando:
contrato/Gherkin aprobado antes de código, revisión separada del diff, bless
humano por PR y publicación del SHA calificado con autorización propia. La
orden de completar el proyecto no cambia esos mecanismos ni permite falsear
aprobaciones. No se modifica `policy.mode` para describir esta coordinación.

La nueva serie se denomina **B3-MA-D**: desarrollo asistido multiagente, no
estudio causal ni continuación intercambiable del coder ciego original.
R0/R1 y sus contratos conservan sus bytes/atribución. El modelo privado no se
investiga. Marca/tokens/precios no disponibles quedan `unavailable`, nunca cero.

## 2. Estado de partida observado

- Main remoto: `8de9107184288f1aa72c9578a14913686c47ad7c`.
- Al inicio, [PR #45](https://github.com/Yosoyepa/write-check-trust/pull/45): OPEN,
  `46669278ece7e3b7cc8059a5eff9ae27c2735284`; P01 conforme técnicamente,
  todavía no integrado. CI falla en integridad por los dos archivos nuevos de
  `tools/wct/evidence`; los pasos posteriores no se ejecutaron.
- Durante la revisión aparecieron en su worktree los tres artefactos del
  bless registrado a nombre de `yosoyepa` para ese SHA/PR. Se revisaron por
  separado, pasó commit 21/21 y se incorporaron en `3795032`. La evolución
  remota y su evidencia se registran en [EVIDENCE](EVIDENCE.md); el rojo inicial
  no se reescribe retroactivamente como verde.
- El trabajo ajeno y los cuatro archivos P01 permanecieron intactos. La PR #45
  recibió únicamente los artefactos de integridad revisados. Esta campaña
  prepara documentación en otro worktree/rama, sin mezclar G1/POST-PR36/REVIEW-G1.
- P02–P10 tenían reglas generales, no todos los contratos de API/fixtures y
  archivos cerrados. [ENTREGA-v2 §1](../SELF-HOSTING/ENTREGA-v2.md) exige cerrar
  ese paquete antes del coder; no encargarle que invente el expected.
- PR #33 y G1b siguen separados. No se actualizan dependencias, canales de
  releases anteriores ni umbrales como parte de esta preparación.

## 3. Primera ola realmente ejecutada

| Actor | Tarea independiente | Salida / límites |
|---|---|---|
| Subagente `p02_spec` | Contrato de inventario/snapshot P02a | [Propuesta P02a](PROPUESTA-P02a.md); no implementación |
| Subagente `molds_audit` | Consumidores y cortes P07–P09 | [Moldes y adopción](MOLDES-Y-ADOPCION.md); no compilador ni modificación de otros repos |
| Subagente `qualification_audit` | Matriz de salida y medición de feedback | [Calificación](CALIFICACION-Y-FEEDBACK.md); no campaña de inferencias |
| Arquitecto principal | Dependencias P02b–P06, revisión de propuestas y verificaciones centrales | [Cadena P1](CADENA-P03-P06.md), síntesis y decisiones; sin autoaprobar futuros escenarios |

Los tres subagentes escriben archivos distintos, no ramas de producto
concurrentes. La implementación tendrá worktree/PR propios por incremento.
Este aislamiento es operativo/cooperativo: no una barrera de seguridad entre
procesos con el mismo usuario. No se consultan secretos ni holdout de evaluación.

## 4. Cola de implementación por dependencias

Los identificadores siguientes son cortes locales, **no números de PR remotos**.
Antes de activar cada fila: paquete de entrada cerrado, Gherkin aprobado,
presupuesto técnico y denominadores fijados. No crear toda una cadena de PRs de
producto sobre contratos aún variables.

| Corte | Depende de | Salida que permite avanzar |
|---|---|---|
| P01 / PR #45 | Bless, CI y post-merge completados | Integrado en `0228acc`; detalle y límites en EVIDENCE |
| P02a snapshot | P01 promovido y propuesta aprobada | Inventario independiente; bytes/contexto/metadata separados; sin verde vacuo |
| P02b propiedad | Tipos P02a fijados | Run/workspace exclusivo, rechazo de symlinks/colisiones y preservación de parciales |
| P03 colección/terminales | P02a/b y protocolo de eventos aprobado | Obligación por identidad y fases; no inferir éxito de exit 0 o texto |
| P04 LCOV privado | P02b y contrato de productor | Artefacto propio completo; ratchet aditivo sin reescribir globals/ruta legacy |
| P05 cierre | Interfaces de P02–P04 fijadas | Ejes y causas completas; un control correcto debe poder acreditar |
| P06 ensamblaje | P03/P04/P05 revisados | CLI real, compatibilidad y matriz P1 completas, presupuesto emparejado |
| P07 plan de molde | P06 calificado | Plan efectivo sin pérdida de campos/archivos; dos layouts equivalentes |
| P08 consumidores | Esquema del plan fijado | Cada campo produce un veredicto observable en motores reales |
| P09 adopción/contexto/puertos | P08 | Brownfield revisado, plan sin escritura, contratos de efectos y ruta CLI real |
| P10 calificación/release | P01–P09 integrados | GO técnico/aprendizaje separados del económico; SHA, smoke, SBOM y autorización de publicación |

Paralelizar solo lo que no lee el resultado del otro: contratos/fixtures de
consumidores pueden prepararse mientras se revisa la pieza anterior. No fijar
interfaces distintas en dos coders simultáneos. P03 y P04 podrán implementarse
en paralelo únicamente cuando compartan contratos de P02 estables y archivos
de ensamblaje asignados a un único responsable.

## 5. Ciclo obligatorio de cada PR

1. Arquitecto cierra contrato/API/errores, regla→test→negativo→evidencia,
   allowlist y alcance de herramientas; el humano aprueba los escenarios.
2. Coder devuelve recibo de entendimiento, usa TDD y entrega candidato/hash.
   No puede editar el criterio de aceptación, el calificador ni el bless.
3. Verifier distinto revisa bytes y ejecuta checks sin corregir el candidato.
   Arquitecto revisa diseño/efectos y explicita sus propios supuestos.
4. Si falla, registrar causa y devolver a coder; nuevo candidate ID, sin
   sobrescribir R0. No devolver un fix entero sin marcar asistencia del arquitecto.
5. Publicar PR con staging cerrado, evidencia real y límites. Revisión humana
   de cambios protegidos → bless humano → artefactos revisados → CI del SHA nuevo.
6. Tras autorización/integración, repetir sobre el SHA resultante. Congelar Wn
   antes de usarlo como referencia de la siguiente pieza; no cambiar el juez
   durante un mismo lote y atribuir después el efecto al modelo.

Un gate verde que apunta al ejemplo no acredita el harness. Los checks que no
pertenecen a ningún tier y los pasos extra de CI se incluyen explícitamente
en [calificación](CALIFICACION-Y-FEEDBACK.md). No se decide por número de badges.

## 6. Aprendizaje beta.3 y decisión beta.4

Beta.3 debe conservar, por PR/candidato: defectos y escapes por clase, detector
automático frente a hallazgo exclusivamente humano, controles válidos/falsos
positivos, primer intento, reparaciones, tiempo de revisión y costes disponibles
de todos los intentos. Planificar tres subagentes no son tres tareas de código
resueltas ni tres éxitos del experimento.

Automejora autónoma, cambio automático del propio juez, routing de modelos y
afirmaciones causales/económicas no se dan por entregados. Beta.4 puede estudiar
un bucle de propuestas con promoción separada y comparaciones controladas cuando
existan los instrumentos. Eso no difiere silenciosamente las mediciones de
aprendizaje y los requisitos de producto de beta.3. El piloto comparativo del
plan original debe ejecutarse con su protocolo o recortarse mediante decisión
humana registrada; una corrida multiagente no lo sustituye.

## 7. Puerta que requiere intervención antes del coder

P01 está integrado con CI post-merge verificada. Revisar y aprobar el bloque
Gherkin, API y allowlist de [P02a](PROPUESTA-P02a.md) después
de su revisión arquitectónica. La aprobación de esta propuesta no autoriza
P02b–P10 por anticipado ni levanta gates. Si se solicita cambiar el procedimiento
de aprobaciones, ese cambio deberá ser explícito y separado del producto.

La [sonda Git](SONDA-GIT-P02a.md) conserva los rojos de propuesta 1; revisión 2
incorpora las decisiones de corrección y explicita qué sigue por calificar.
Esta revisión reduce ambigüedades antes del coder, pero no lo sustituye.
El [encargo siguiente](ENCARGO-P02a.md) ya está preparado con handoff y
fronteras exactas. Sigue desactivado hasta la aprobación D1; no es una
autorización incorporada al prompt por el propio arquitecto.

Esta primera ola no se presenta como beta.3 terminada ni como PR de código
implementada por los nuevos subagentes. El bloqueo es de autoridad/contrato,
no de haber alcanzado un presupuesto de trabajo.
