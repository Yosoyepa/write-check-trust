# Beta.3 — calificación y feedback de la ejecución multiagente

Fecha de inspección: 2026-09-08 01:05 UTC (2026-09-07, America/Bogota).
Base inspeccionada: `46669278ece7e3b7cc8059a5eff9ae27c2735284`.
Estado: **propuesta operativa para decisión del arquitecto/humano**. Este
documento no cambia el alcance aprobado, policy, thresholds, escenarios,
historia SH-P01, autoridad de bless ni publicación. No es un acta de beta.3
terminada. La auditoría fue documental/estática y consulta remota de CI; no
ejecutó producto, baterías pesadas, inferencias externas ni leyó cuentas/modelos.

Estado posterior al corte de esta auditoría: P01 integrado en `0228acc`, CI de
PR y main success; ver [EVIDENCE §§3/5](EVIDENCE.md). Los hallazgos de partida
se conservan fechados; QF-01 ya fue atendido por esa secuencia, sin afirmar que
se hayan implementado P02–P10 o cumplido toda esta matriz.

## 1. Dictamen del punto de partida

P01 tiene una reparación técnicamente conforme dentro de su contrato, pero
**no está integrada ni calificada como una cadena P1**. La PR #45 permanece
OPEN en el SHA indicado. La corrida quality
[34174535018](https://github.com/Yosoyepa/write-check-trust/actions/runs/34174535018)
falló en integridad con exit 1 sobre exactamente:

```text
nuevo protegido: tools/wct/evidence/__init__.py
nuevo protegido: tools/wct/evidence/identities.py
```

El commit tier, auditoría de dependencias, cobertura, ratchets, property,
diff-cover, mutación de aceptación y red team quedaron **skipped por el fallo
previo**. Eso no demuestra que tengan un defecto ni que pasarán después del
bless. No hay aprobación adicional de bless observada por esta auditoría.

Fuentes: [integración P01](../SELF-HOSTING/INTEGRACION-P01.md),
[acta R1](../SELF-HOSTING/reviews/REVIEW-CND-74E0.md),
[gobernanza §5](../SELF-HOSTING/GOBERNANZA.md#5-integridad-y-bless-en-un-repo-que-se-cambia-a-sí-mismo)
y consulta `gh pr view 45`, `gh run view 34174535018 --json headSha,conclusion,jobs`
y `--log-failed`. Son observaciones de ese corte, no estado remoto perpetuo.

El arquitecto comunicó además corridas nuevas en este mismo worktree y SHA:
commit exit 1, 20 PASS/0 SKIP y solo G-META-1 rojo; G-TEST PASS en 102671 ms;
lint-imports 4 contratos cumplidos/0 rotos (9 archivos, 8 dependencias);
archmetrics `example.*` sin violaciones/ciclos y dos avisos de zona de dolor;
DRY por defecto 3 unidades/0 candidatos. Son resultados **del arquitecto**, no
ejecuciones de este auditor ni nuevas medidas de tools por esos motores.
No hubo nuevo LCOV/full/mutación en esas comprobaciones comunicadas.

## 2. Hallazgos priorizados: lo que falta de verdad

Los IDs QF-* son de este dossier; no son issues remotos ni aprobaciones.

| ID / prioridad | Hallazgo y motivo | Decisión requerida / comprobación de cierre |
|---|---|---|
| QF-01 / bloqueo de promoción | P01 pre-bless no tiene CI completa; conformidad técnica no es integración | Humano revisa diff/bless; integrador valida artefactos y nuevo SHA; quality completa y post-merge sobre ese SHA |
| QF-02 / HIGH | P02–P09 no se pueden sustituir por más tests del kernel P01. El contrato de salida incluye evidencia, molde, consumidores, adopción y contexto por rutas reales | Cerrar APIs/Gherkin/allowlists por pieza y verificar matriz de §4; cualquier recorte vuelve a decisión humana |
| QF-03 / HIGH | Verdes de CRAP, mutación, arquitectura o DRY del ejemplo no miden automáticamente `tools/wct`. R0 ya mostró la consecuencia | Matriz ruta→regla→consumidor real por PR; mediciones focales adicionales y límites de mutación explícitos; no ampliar policy como atajo |
| QF-04 / HIGH | `G-TEST-RANDOM` existe en REGISTRY pero no pertenece a ningún tier. full verde no demuestra TEST-006 | Corridas separadas con plugin/versiones/semillas/selección registrados y todos los incidentes conservados |
| QF-05 / MEDIUM | El tier `pr` no reproduce toda quality: no contiene el paso exigible de ratchets ni audit de dependencias del workflow | Tratar CI y receta local como matrices distintas; ejecutar los pasos faltantes, no anunciar paridad por el nombre del tier |
| QF-06 / HIGH | Parseo y binding no demuestran ejecución de cada escenario/fila. La aceptación de CI usa el ejemplo histórico | P03/P06 deben probar fila→nodeid→terminal y omisión con resto verde; P09 debe probar entrada real y efecto persistente |
| QF-07 / HIGH | Un candidato puede pasar revisiones cooperativas sin existir aislamiento frente a un proceso hostil | Calificar límites del scorer antes de claims de holdout privado; worktree no se presenta como sandbox |
| QF-08 / HIGH para replay | Artefactos históricos grandes permanecen `local-only`. Markdown con hash no asegura custodia ni recuperación | Antes de limpiar/publicar evidencia, inventario, copia a destino autorizado, cotejo de hashes y responsable; sin copia, conservar limitación |
| QF-09 / HIGH para claims | Las nuevas sesiones/cohorte no están calificadas como equivalentes al ensayo ciego histórico; no se afirma si comparten o no modelo. Una serie de reparaciones asistidas no estima el efecto causal ni el ahorro | Lotes separados, asistencia/primer candidato conservados, ninguna inspección de identidad o precio; GO económico distinto de técnico |
| QF-10 / MEDIUM | Un full puede devolver SKIP para herramientas opcionales y el upload acepta ausencia de archivos. Exit 0 no acredita todos los claims ni custodia | Inventario de gates/estados y logs completos; capabilities requeridas y SBOM de release no se aceptan por SKIP |
| QF-11 / HIGH para adopción | Crecimiento de suite puede superar el presupuesto vigente de commit 120 s | Medir clon limpio y presupuesto emparejado; si falla, diagnosticar/optimizar por PR propia o pedir decisión, nunca elevarlo silenciosamente |

Fuentes ejecutables de QF-03–06/10–11:
[runner y tiers](../../../../../tools/wct/gate/runner.py),
[builders](../../../../../tools/wct/gate/checks.py),
[policy](../../../../../governance/policy.yaml),
[thresholds](../../../../../governance/thresholds.yaml),
[selección de coverage/mutmut](../../../../../pyproject.toml),
[quality](../../../../../.github/workflows/quality.yml),
[full-hardening](../../../../../.github/workflows/full-hardening.yml),
[adoption-smoke](../../../../../.github/workflows/adoption-smoke.yml).
QF-07–09 se apoyan además en
[GOBERNANZA](../SELF-HOSTING/GOBERNANZA.md),
[ENTREGA-v2](../SELF-HOSTING/ENTREGA-v2.md) y
[EVALUACION-CIEGA](../SELF-HOSTING/EVALUACION-CIEGA.md).

## 3. Cuatro GO separados, ninguno se hereda de otro

| Decisión | Condición para GO | Estado al corte / resultado que NO basta |
|---|---|---|
| GO técnico beta.3 | P01–P09 comprometidas funcionan y se ensamblan; compatibilidad, límites, precisión del instrumento, presupuesto y SHA final calificados; cero bloqueantes sin resolver | Pendiente. Kernel P01 o P01–P06 no satisfacen el alcance de moldes/adopción/contexto |
| GO de aprendizaje | Expediente íntegro de desarrollo, primeros candidatos y reparaciones; detección por actor/capacidad; controles válidos/defectuosos; feedback incorporado en versiones futuras; resultados negativos y datos faltantes visibles | Piloto histórico útil, no lote completo multiagente. Puede dar GO aunque no haya mejora o ahorro |
| GO económico / sustitución | Calidad congelada; consumo completo reconciliado por rol, fallos/retries incluidos; comparación pertinente, incertidumbre y criterio de riesgo aprobados | `INCONCLUSO`: no hay recibos ni comparación equivalente. No convertir unavailable en 0 ni inferir modelo económico por su asignación |
| GO de publicación | GO técnico y aprendizaje para la promesa aprobada, SHA final/bump protegidos, CI/full/smoke, SBOM/procedencia, notas exactas y autorización específica; validación remota del tag/prerelease | Pendiente. Commit, push, bless y terminar un dossier no autorizan release automáticamente |

La evaluación económica inconclusa permite publicar una beta experimental
**solo si la promesa aprobada lo permite y las otras puertas se cumplen**.
No habilita a declarar ahorro. Una medición comparativa comprometida y no
ejecutada sigue pendiente o requiere desviación/recorte humano explícitos; no
desaparece porque el producto funcione. Fuente:
[PIEZAS §5](../SELF-HOSTING/PIEZAS.md#5-qué-permite-decir-que-beta3-está-lista),
[PLAN §5](../PLAN.md#5-contrato-de-salida-beta3) y
[EVALS §8](../EVALS.md#8-tres-decisiones-distintas).

## 4. Matriz técnica por PR y ensamblaje

No son nuevas APIs ni Gherkin aprobados. Es la matriz mínima que el arquitecto
debe convertir a casos concretos **antes** de encargar cada diff, conforme a
[PIEZAS](../SELF-HOSTING/PIEZAS.md),
[SPEC-P1](../specs/SPEC-B3-P1-evidencia.md),
[Gherkin P1](../GHERKIN-P1.md),
[SPEC molde](../specs/SPEC-B3-01-moldes.md) y
[SPEC evidencia/contexto](../specs/SPEC-B3-02-evidencia-contexto.md).

| Pieza | Positivo que debe seguir funcionando | Negativo discriminante / observable requerido |
|---|---|---|
| P01 identidades | Inventarios válidos exactos, orden estable, solución válida alternativa | Mismo N con otros IDs; duplicados múltiples permutados; vacío; conservar todos los diagnósticos. El acta R1 no se reescribe con reglas v2 |
| P02 snapshot/workspace | Mismos inputs en ejecución propia, dos árboles y outputs distintos sin interferencia | Unstaged/nuevo/ignorado en scope, exclusión no aprobada, config/deps/runner alterados, symlink/traversal, colisión de ownership; rechazo sin borrar ajenos y evidencia parcial conservada |
| P03 ejecución observada | Cada obligación y fila parametrizada llega a setup/call/teardown terminales correctos | Falta un ID con N conservado, skip/xfail/xpass, error setup/teardown, crash/cancelación; no inferir ejecución desde exit 0, parser o resumen; no soportar reruns/xdist por accidente |
| P04 LCOV propio | Productor terminal, inputs estables, artefacto propio/íntegro y SF esperados; ratchets aditivos | Viejo/ajeno/sustituido/truncado, contadores imposibles, SF duplicado/faltante, producer fallido con archivo viejo; ningún path histórico contaminado |
| P05 cierre | Cadena válida completa y umbral satisfecho da accredited; fallo real completo da rejected | Invalid domina incomplete/rejected pero conserva FAIL simultáneo; datos/capacidad/obligación ausente no acredita; reject-all debe fallar contra positivo |
| P06 CLI P1 | Ruta ensamblada CLI→productores→consumidores→envelope con argv real; contrato histórico byte-compatible | Todas las familias P1-V/A/I/X/D/E/L y error de uso; dos corridas/árboles, productores fallidos, consumo ajeno; mismas salidas no acreditan capacidades futuras |
| P07 plan molde | Dos layouts equivalentes producen plan semántico equivalente y roles exhaustivos | Módulo sin/doble rol, vacío, root desconocido, keys/extensiones contradictorias, ciclos y cambios posteriores invalidan; M01–M04/M09–M10/M15–M16 |
| P08 consumidores | Puerto en consumidor y adaptador alternativo válido; mapeo real del harness seleccionado | Cambiar cada campo normativo afecta consumidor/veredicto; omitir regla rompe fixture independiente; import prohibido directo/indirecto falla, no seguir analizando solo example |
| P09 adopción/contratos/contexto | Plan no escribe; migración y reversión conservan negocio; dos adapters cumplen la misma suite; CLI invoca comportamiento | Firma inventada, retorno sin persistencia, producto ajeno afectado, reabrir pierde estado, contexto obsoleto, deuda sustituida con N conservado; M05–M08/M11–M14 y E08–E14 según alcance |
| P10 calificación | Todas las filas anteriores trazan al SHA final y fixture válido, sin expected del propio compilador | Deshabilitar/bypassear consumidor, cambiar runner/oráculo, missing artefacto/recibo o run cancelado son visibles; no aceptar un resumen verde ni ignorar un FAIL |

Todo caso debe declarar si su defensa es productiva, prueba de integración,
calificador externo cooperativo o revisión humana. Una prueba que solo rompe
con SyntaxError o un import ausente no acredita sensibilidad semántica.
`Mxx/Exx` son identidades de contratos; no afirmar su ejecución por aparecer
en la tabla. Congelar test/nodeids/expected y verificar ejecución real.

### 4.1 Receta común de verificación sin sobreatribuir alcance

1. Diff completo/allowlist e identidad de imports en el worktree; entorno y
   versión Python registrados. CI utiliza 3.12, el histórico local usó 3.13.
2. Colección real tras tocar tests; suite completa y selección no-property
   separadas de focal/acceptance/property. No sumar corridas como si fueran una.
3. Fast y commit con inventario PASS/FAIL/ERROR/SKIP. Pre-bless se permite
   reportar el único G-META esperado, nunca renombrarlo PASS ni omitir otro rojo.
4. Coverage focal sobre las fuentes nuevas y CRAP/CC/sitios/DRY explícitos sobre
   esas rutas. Buscar reutilización/cross-DRY además del análisis interno. El
   gate histórico de mutación no acredita cero supervivientes en tools: fijar
   instrumento selectivo/contrato con el arquitecto o declarar la limitación;
   no resolverla cambiando silenciosamente paths.source/source_paths.
5. Cobertura **global nueva**, no-property, y `ratchet check --require all`
   secuenciales con mismo input; guardar el hash LCOV. Es receta de entrega
   local; CI actual exige solo coverage-total/docstring-coverage.
6. Negativos causales y positivos alternativos sobre copias operativas,
   finales elegidos antes del juicio. Coder no modifica al juez para pasar.
7. Revisión del verifier distinto sin escritura y del arquitecto, mismo digest.
   Si arquitectura escribió arreglo exacto, contabilizar `architect-assisted`.
8. Tras autorización de bless: revisar lock/log/manifiesto y SHA; luego CI de
   PR, CI de merge y post-merge. Registrar gates saltados por fallos previos.

Fuera de su scope concreto, un gate solo acredita que ejecutó su comprobación;
no una propiedad de la pieza. Guardar la matriz ruta→regla→argv→denominador→log,
tal como exige [ENTREGA-v2 §§1–5](../SELF-HOSTING/ENTREGA-v2.md).

### 4.2 Release sobre un único SHA final

Reusar la disciplina de [RELEASE-BETA2/PLAN](../../RELEASE-BETA2/PLAN.md),
sin copiar sus resultados o asumir sus excepciones para beta.3:

- Quality completa del SHA integrado, sin pasos requeridos SKIP; suite completa
  y matriz de funcionalidades de §4 con cobertura propia/global reciente.
- Full-hardening, inventario real de herramientas y estados; G-DRY-TOK
  ejecutado con jscpd, SBOM generado (no SKIP). No relajar umbral ante deuda.
- Orden PROC-004 verificado: mutación → mutación de Gherkin → CRAP → DRY.
  El workflow full corre aceptación después del tier y no demuestra ese orden.
- Random independiente: versión de plugin fijada y scope explícito; propuesta
  heredada a confirmar: `pytest-randomly==5.0.0`, unit/integration no-property,
  semillas 1, 2, 3 y una generada registrada. Registrar también exclusiones y
  calificar la ruta de aceptación requerida por separado; no prometer random
  de toda la suite con esta selección. No instalarlo aquí por inferencia.
- Smoke de clon limpio: bootstrap→doctor→fast→commit, el paso commit ≤120 s
  vigente. El presupuesto del job (15 min) no reemplaza este requisito.
- Presupuesto P1: decidir techos propuestos antes de medir, cinco pares
  alternados por fixture/condición, frío/caliente separado; N/mediana/rango,
  nunca p95 acreditado con cinco muestras. Overhead de instrumentación no se
  confunde con crecimiento de tests ni se extrapola de una corrida histórica.
- Manifest de release une SHA, versión normalizada, locks, SBOM, logs y
  clasificación de assets. Si `quality-reports` falta, conservar logs y
  diagnosticar: `if-no-files-found: ignore` no es custodia exitosa.
- Bump protegido y todo cambio posterior requieren calificar el SHA final.
  Autorización de publicación aparte; tag inmutable, smoke del tag y consulta
  remota de `isPrerelease=true`, `isDraft=false`, assets/hashes y no Latest
  estable. Un exit 0 de publicación no verifica su estado remoto.

## 5. Protocolo de aprendizaje por PR, desde el primer candidato

### 5.1 Separar las dos cohortes

- **SH-D histórico ciego:** CND-80B8→CND-74E0, contrato `sh-p01/1`, actas y
  adenda conservadas. Un problema, dos candidatos ligados y asistencia
  declarada; no dos tareas independientes. Sus defectos no se borran porque
  R1 sea conforme. El proceso v2 no reevalúa retroactivamente R0/R1.
- **Nueva serie B3-MA-D:** desarrollo multiagente supervisado autorizado ahora.
  IDs opacos por tarea/candidato/actor, contrato/molde/entrega fijados. No
  investigar identidad ni asumir que los subagentes usan el modelo secreto
  anterior, son económicos o constituyen un brazo comparable. No otorgar
  ceguera perfecta si el runtime no la acredita.
- **SH-E comparativo:** lote distinto futuro, si se autoriza: W0/Wn/Qn
  congelados, misma tarea/modelo atestiguado por custodio, oportunidades
  comparables, orden asignado y sesiones separadas. El desarrollo anterior no
  se reclasifica como este lote tras ver su resultado.

### 5.2 Registro mínimo append-only

Usar [REGISTROS](../SELF-HOSTING/REGISTROS.md), con los campos siguientes
explícitos en cada handoff/acta. El formato es documental; no agrega un schema
JSON de producto ni un ledger automático ya implementado.

| Momento | Datos requeridos / frontera |
|---|---|
| Antes del coder | cohort, task/run/actor/candidate IDs; versión y hash contrato/feature/criterios; base+contexto; allowlist; autoridad observada; recibo de entendimiento ENTREGA-v2; instrumentos Wn/Qn y alcance |
| Durante TDD/desarrollo | Intentos observables, comandos/argv/cwd/outputs/exits y tiempos; fallo inicial honesto; ayudas y cambios de contexto; no razonamiento privado ni campos de proveedor en expediente público |
| Primera entrega completa | Congelar patch/digest y fecha; no sustituirla por el candidato reparado; auto-tests/candidate-reported separado del juicio independiente |
| Revisión | Dictamen por dimensión, evidencia, limitaciones, quién detectó primero, discrepancias y controles válidos; snapshot/digest del calificador, acceso e independencia reales |
| Reparación | Nuevo candidate_id y parent; hallazgos que intenta corregir y asistencia; mismo contrato o nuevo contrato explícito si había SPEC-GAP, sin mover el criterio histórico |
| Integración | PR/SHA reales, allowlist staged, bless humano cuando exista, estados CI y post-merge; artefactos de integración distintos del digest de producto |
| Aprendizaje | Defectos únicos por causa/contrato y propuesta Wn+1/Qn+1, positivos/negativos nuevos, riesgo FP/FN, coste observable y limitaciones; decisión del arquitecto/humano para otro lote |

Clasificar primera detección sin inflar la automatización:

`coder-test`, `wct-gate`, `manual-tool`, `review-challenge`, `human-semantic`,
`ci-only`, `post-merge` o `unavailable`. Registrar también actor y fase. Ejemplo:
R0 CRAP medido por comando focal del reviewer es `manual-tool`, no un defecto
que WCT detectó automáticamente. Una regresión añadida después es cobertura
**futura**, no detección automática del candidato original.

### 5.3 Métricas con denominadores cerrados

| Métrica | Definición y cautela |
|---|---|
| Primera aceptación | Tareas cuyo primer candidato completo obtuvo CONFORME sin reparación / tareas asignadas con obligación de entrega; mostrar por separado pendientes/no-evaluables y la tasa entre revisadas |
| Conformidad final | Tareas conformes al cerrar / todas las asignadas; no sobrescribe la primera aceptación. Una PR es unidad de entrega, no necesariamente una tarea independiente |
| Reparación | Entregas posteriores al primer dictamen, ciclos TDD/diagnóstico y tiempo por rol por separado; split/refactor no multiplica artificialmente tareas exitosas |
| Escape visible | Candidatos con controles funcionales exigidos verdes y defecto posterior / candidatos con esos controles verdes realmente revisados. Declarar scope y excepción pre-bless de integridad por separado; cero elegibles = no estimable |
| Detección WCT | Defectos únicos detectados primero por un gate WCT ya vigente / defectos únicos reproducidos de esa cohorte; mostrar las otras fuentes, no asumir que es sensibilidad poblacional |
| Dependencia de reviewer | Defectos detectados solo por herramienta focal/challenge/semántica del reviewer, minutos y tipo de ayuda. Mantenerlo separado de un precio monetario desconocido |
| Precisión instrumental | Controles válidos rechazados / controles válidos ejercitados, por regla; negativos escapados / negativos probados, por familia. No llamarlos tasa poblacional de fallos en producción |
| Tiempo | Pared extremo a extremo, CPU/tiempo herramienta, latencia hasta primer candidato y tiempo por rol. Concurrencia hace que sumar duraciones de agentes no equivalga a elapsed total |
| Coste por tarea/éxito | Costes de todas las solicitudes/roles/fallos/retries, con denominadores asignados/conformes; cero éxitos = no finito. Un coste faltante da incompletitud, no ahorro |

Conservar causas SPEC-GAP, IMPL-LOGIC, INVENTED-API, ARCH-DRIFT,
TEST-ORACLE, HARNESS-ESCAPE, HARNESS-FP, EVIDENCE-GAP y ENVIRONMENT de
[REVISION-Y-FEEDBACK](../SELF-HOSTING/REVISION-Y-FEEDBACK.md). Un mismo
hallazgo repetido en herramientas/actas no cuenta varias veces; una hipótesis
no es causa raíz hasta reproducirla. El primer candidato revisado contra
criterios nuevos se rotula como cambio de contrato, no fallo del coder por
un requisito oculto.

### 5.4 Telemetría y privacidad

En esta ejecución son observables los comandos/resultados, patches, acciones
de los roles y sus timestamps cuando se capturan. Inferencias internas,
facturación, tokens exactos, routing y costes históricos no se deducen de la
longitud del transcript ni del tiempo de herramienta. Registrarlos
`unavailable` con motivo y cobertura del inventario de recibos.

El custodio podrá aportar después export redacted por task/run/candidate/rol,
sin revelar modelo. Reconciliar IDs únicos, recibos faltantes y requests
canceladas; no contar cada chunk/reintento de descarga como nueva inferencia.
Calidad/severidades se congelan antes de abrir costes. No pedir ni consultar
claves, settings, logs privados o identidad de modelos para llenar una tabla.

## 6. Qué puede ir a beta.4 sin recortar beta.3 por cuenta propia

Ya están fuera del MVP o requieren evidencia adicional: routing automático,
cambio autónomo de gates/umbrales, promoción o bless automático, composición
libre de arquitecturas/otros lenguajes, catálogo/marketplace, generalización
confirmatoria multi-repo y sustitución del modelo sin supervisor. Pueden ser
**candidatos de beta.4**, no compromisos autorizados ni capacidades beta.3.

La autonomía debe ganar autoridad por clase de cambio y evidencia: primero
proponer un defecto reproducible, después validar una regla general con
positivos/negativos independientes y presupuesto, y finalmente pedir promoción.
El código que propone mejorar al harness no cambia su árbitro en el mismo
lote. Una futura beta.4 debe conservar límites de escritura, revisión,
reversión, custodia y override humano; no es «autoaprobar» por usar subagentes.

**No se pueden mover sin decisión humana:** P02–P06 de evidencia, P07/P08 del
molde ejecutable, P09 de adopción/contexto/puertos, calificación y feedback
comprometidos de P10, compatibilidad y publicación del SHA final. Tampoco un
piloto comprometido se sustituye silenciosamente por infraestructura.

El lote SH-E de 24 runs es una propuesta separada de P01 SH-D; el piloto
externo de 144 runs conserva su estado de propuesta no ejecutada. Si el
arquitecto/humano decide que beta.3 cerrará con desarrollo B3-MA-D y aprendizaje
descriptivo, debe registrar esa decisión y su efecto sobre PLAN/EVALS/P10,
declarar SH-E y claims económicos pendientes y no decir que se midió causalidad.
Este documento **no toma esa decisión de alcance**. Un ensayo puede terminar
negativo/inconcluso y ser completo; un ensayo no ejecutado no está terminado.

## 7. Handoff de esta auditoría

Lectura completa de AGENTS, PLAN, EVALS, EVALUACION-CIEGA,
REVISION-Y-FEEDBACK, PIEZAS, GOBERNANZA y ENTREGA-v2. Inspección de workflows,
runner/registro/tiers, builders de cobertura/CRAP, configuración de cobertura y
mutación, selecciones de CLI/aceptación y actas de integración/revisión.
Consulta remota read-only de PR45 y logs de su corrida fallida.

No se corrieron fast/commit/full, tests, cobertura, mutación, calificación de
entornos ni aislamiento en esta subtarea. No se hicieron llamadas adicionales
a proveedores ni una campaña de inferencia; el propio trabajo de este subagente
no se considera gratuito y su consumo/coste no está disponible en esta auditoría.
No se afirma que los hallazgos de alcance fueran reproducidos con una batería
nueva: son
inspección estática respaldada por rutas/argv y precedente R0 registrado.
Única escritura: este documento. Producto, gobernanza, expedientes históricos,
commits, push, PR, bless y publicación quedan sin cambios por esta auditoría.
