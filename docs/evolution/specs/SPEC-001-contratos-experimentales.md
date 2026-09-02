# SPEC-001 — Contratos de tarea, experimento y ejecución

- Estado: propuesta para revisión
- Naturaleza: especificación conceptual, no schema ejecutable
- Relacionada con: PRD-001 y PRD-003

## Objetivo

Definir la información mínima que hace reproducible una comparación y evita que
diferencias accidentales entre brazos se atribuyan a WCT.

## Principios

- IDs estables, contenido inmutable por versión.
- Referencias por digest, no por “latest”.
- Campos desconocidos se marcan como tales; no se sustituyen por cero.
- Tarea, tratamiento, runtime y oracle son entidades distintas.
- El task package visible nunca contiene el holdout privado.
- Una ejecución fallida sigue siendo una ejecución.
- El contrato describe qué debe conocerse, no exige una tecnología de storage.

## Contrato de tarea

| Campo | Obligación | Propósito |
|---|---|---|
| task id y versión | requerido | identidad estable y retiro sin reescritura |
| título y clase | requerido | bug/feature/refactor/security/adoption, etc. |
| repo source y commit | requerido | snapshot exacto |
| source provenance | requerido | licencia, autoría y contaminación |
| setup/image digest | requerido | entorno reproducible |
| dependency lock hash | requerido | grafo exacto |
| prompt visible hash | requerido | igualdad entre brazos |
| archivos/contexto visibles | requerido | frontera de información |
| ediciones permitidas/prohibidas | requerido | scope y seguridad |
| tools/permisos/red | requerido | equidad del entorno |
| presupuesto default | requerido | tokens, tiempo, calls y storage |
| criterios observables | requerido | vínculo especificación → oracle |
| oracle id/hash | requerido, contenido separado | scoring independiente |
| criticidad por requisito | requerido | éxito y escapes críticos |
| modos de fallo objetivo | requerido | cobertura del corpus |
| dificultad esperada | requerido | estratificación, no score final |
| plataformas soportadas | requerido | límites ambientales |
| solución de referencia | custodiada | calificación y debugging |
| alternativas válidas | al menos una cuando aplique | control de tests estrechos |
| negativos plausibles | requerido | demostrar poder discriminador |
| reviewers/aprobaciones | requerido | cadena de custodia |
| estado de contaminación | requerido | clean/exposed/suspected/retired |
| fecha de freeze/revalidación | requerido | drift y expiración |

## Contrato de tratamiento/brazo

| Campo | Obligación | Propósito |
|---|---|---|
| arm id y versión | requerido | A0–A5 o extensión preregistrada |
| modelo/provider/snapshot | requerido | capacidad exacta |
| parámetros de inferencia | requerido o unavailable | temperature, reasoning, max tokens |
| instrucciones WCT | hash o ausencia explícita | aislar persuasión |
| perfil/capabilities WCT | hash o ausencia explícita | aislar prueba |
| política de reparación | requerida | número/condición de iteraciones |
| feedback visible | requerido | qué resultados recibe el agente |
| tool policy | requerida | igualdad y permisos |
| límites de ejecución | requeridos | compute comparable |
| runtime/adapter version | requerido | provenance de ejecución |
| diferencias frente a control | derivado y revisado | detectar confounders |

Un tratamiento “sin WCT” debe definir qué checks neutrales conserva. No puede
eliminar los tests funcionales indispensables de la tarea solo para empeorar el
control.

## Contrato de experimento

| Campo | Obligación | Propósito |
|---|---|---|
| experiment id/version | requerido | identidad |
| research question | requerida | evita análisis oportunista |
| hypotheses/endpoints | requeridos | preregistro |
| task set y split | hashes requeridos | corpus congelado |
| arms | lista cerrada | tratamiento |
| blocking/randomization | requerido | asignación reproducible |
| repetition plan | requerido | variabilidad |
| budget policy | requerida | equidad/costo |
| non-inferiority margin | si aplica, pre-run | decisión válida |
| exclusions/reruns | pre-run | integridad del denominador |
| stopping rule | pre-run | evita optional stopping |
| analysis plan | pre-run | estimadores e intervalos |
| reviewer/custodian | requerido | roles independientes |
| start/end window | requerida | model drift |
| price table version | requerida | costo reproducible |
| preregistration digest | requerido | detectar cambios post hoc |

## Contrato de run

| Campo | Obligación | Propósito |
|---|---|---|
| run id | único | unión de evidencia |
| experiment/task/arm refs | requeridas | pertenencia |
| assigned order/seed | requeridos | aleatorización |
| workspace/home/session ids | requeridos | aislamiento |
| environment/image/host | requeridos | reproducción |
| start/end/termination | requeridos | tiempo y estado |
| prompt/context digests | requeridos | igualdad real |
| effective config digest | requerido | tratamiento efectivo |
| event log hash | requerido | trayectoria |
| base/final tree y patch hashes | requeridos | resultado material |
| gate evidence refs | requeridas según perfil | control |
| oracle evidence ref | requerido para cierre evaluable | outcome independiente |
| token/cost record | requerido o missing explícito | eficiencia |
| retries/infra incidents | requeridos | distinguir modelo de entorno |
| completeness/validity | requeridos | no equiparar ausencia con pass |
| deviations/exclusions | requeridos, incluso vacíos | auditoría |
| signer/producer versions | requeridos | provenance |

## Estados terminales

| Estado | Significado | Tratamiento analítico por defecto |
|---|---|---|
| completed | agente terminó y oracle pudo correr | incluir |
| budget_exhausted | alcanzó tokens/tiempo/calls | fallo en intention-to-treat, salvo plan distinto |
| agent_error | runtime/model falló después de iniciar | incluir según política preregistrada |
| infrastructure_error | fallo externo demostrable | rerun solo según regla predefinida; conservar original |
| cancelled | interrupción humana/sistema | conservar y clasificar; no excluir silenciosamente |
| invalid | contaminación, config o artifact no corresponde | excluir del estimador solo con razón; conservar denominador |
| incomplete | faltan oracle/artefactos | nunca presentar como pass |

## Invariantes de aislamiento

- Base tree de todos los brazos de una tarea tiene el mismo hash.
- Ningún workspace se reutiliza.
- El home/cache del agente no se comparte, salvo condición experimental explícita.
- El oracle se monta solo después de finalizar el tratamiento.
- Secretos no se escriben en task package, event log o patch.
- Teardown enumera residuos y falla si un run siguiente podría observarlos.
- El orden real coincide con la asignación preregistrada.

## Conformance de un adapter

Un adapter de runtime debe demostrar:

1. materialización de sesión aislada;
2. captura de terminación externa;
3. eventos ordenables y durables;
4. accounting con exact/estimated/unavailable;
5. cancelación y timeout sin perder evidencia;
6. patch/tree final verificable;
7. replay o declaración explícita de no soporte;
8. ausencia de tipos del runtime en contratos neutrales;
9. redacción de secretos;
10. versionado de capacidades.

## Pruebas/evals de aceptación del contrato

| Caso | Invariante que debe detectar |
|---|---|
| A3 recibe un archivo extra | diff de tratamiento no preregistrado |
| segundo run ve cache del primero | aislamiento roto |
| modelo reporta éxito sin patch | terminación no equivale a outcome |
| oracle se ejecuta durante reparación | fuga del holdout |
| provider no informa cache tokens | dato unavailable, no cero |
| run timeout desaparece del reporte | violación append-only/intention-to-treat |
| imagen usa tag mutable | snapshot no reproducible |
| adapter cambia el prompt | hash visible diverge |
| rerun reemplaza al original | pérdida de provenance |

## Preguntas abiertas para aprobación

- ¿Qué aislamiento mínimo es aceptable para tareas no adversariales?
- ¿Quién custodia el holdout y firma una liberación?
- ¿Qué campos pueden publicarse y cuáles solo compartir bajo acuerdo?
- ¿Qué runtime mínimo sirve de baseline antes de evaluar DeepSeek Harness?
- ¿Qué clocks y tablas de precio son fuente de verdad?
