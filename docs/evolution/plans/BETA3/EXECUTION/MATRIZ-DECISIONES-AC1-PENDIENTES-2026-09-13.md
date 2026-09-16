# Matriz única de decisiones pendientes — AC1 (2026-09-13)

Estado: consolidación de referencia para decisión humana. **Esta matriz no
ratifica nada por sí misma**, no ejecuta campañas, no cambia producto ni
gobernanza. Base vigente: `fa3558d` (T5 aceptado y congelado como referencia;
sin nuevas modificaciones de ese test). Revisión de decisiones ejecutables:
`01c901dfdb6713de22ac8d60737c6ecf4b4a8d98`; recomendaciones NO APROBADAS en
`PLAN-EJECUTABLE-CIERRE-AC1-BETA3-2026-09-15.md` §3–§9. El cambio de corte
no traslada evidencia automáticamente. Fuentes reutilizadas: matriz
`ADJUDICACION-SUPERVIVIENTES-AC1-R3-2026-09-13.{md,json}` (clasificaciones y
sondas), `ADENDA-AC1-R3-DENOMINACION-ORACULOS-REGRESIONES-2026-09-13.md`
(oráculos de hooks y regresa­ciones), `RESULTADO-AC1-LOTE-R3-2026-09-13.md`
(resultado bruto), `RATIFICACION-AC1-R2B-H01-H04-2026-09-13.md` (precedente de
ratificación y mecanismo), expediente `build/tmp/ac1-r2-qualification/`.

**Nota de oleada (2026-09-15):** la oleada técnica autorizada ejecutó las
comprobaciones r3 (cuatro casos, siete límites y dos hooks), el despacho
`REGISTRY` y el diseño de partición TEST-007; el rediseño de aceptación quedó
implementado y verde en copia, pero bloqueado por una colisión nueva con
G-ACCEPT que exige decisión humana. Resultados, presupuestos, dictamen del
verifier y siguientes pasos en
`OLEADA-TECNICA-CIERRE-AC1-2026-09-15.md`. No ratifica equivalencias ni
cierra AC1/beta.3.

## 0. Ya cerradas (contexto, sin acción pendiente)

| Ítem | Cierre | Referencia |
|---|---|---|
| 5 equivalentes L1 (receipt ×2, zip ×3) | Ratificados | Acta L1b + addenda RESULTADO-AC1-R2 |
| 24 equivalentes r2b | Ratificados (H-01, alcance acotado) | Acta H-01–H-04 |
| Frontera IR canónico; defensa interna del parser; preflight como instrumento | Decididos (H-02/H-03/H-04) | Ídem |
| 11 defectos funcionales r3 | Regresiones incorporadas (8 pruebas; original verde, 11/11 mutantes caen) | `6e4398e`, `fa3558d` |
| T5 (salida pendiente tras líder terminado) | Aceptado; doble de Popen + selector real | `fa3558d` |

## A. Equivalencias acotadas — 14 IDs por ratificar (decisión D-A)

Ratificar/rechazar/pedir más evidencia **por ID**, exclusivamente bajo bytes
(SHA-256 del manifiesto r3), runtime (`sh-p01-CND-80B8`, Python 3.13.14,
mutmut 3.7.0) y precondiciones de la matriz R3. Si cambian, la adjudicación
revierte. Ratificar NO convierte el `survived` histórico en `killed`.

| # | ID (r3) | Mutación | Base técnica de la equivalencia |
|---|---|---|---|
| A1 | `campaign.x__attempt__mutmut_4` | `ensure_ascii=False` → `None` | `None` es falsy: mismo parámetro efectivo en CPython |
| A2 | `campaign.x__attempt__mutmut_9` | `encode("utf-8")` → `encode("UTF-8")` | alias canónico del códec (precedente L1) |
| A3 | `process.x__execute__mutmut_30` | guarda del `finally`: `is None` → `is not None` | **JUSTIFICACIÓN PENDIENTE DE REVISIÓN** — no es equivalencia demostrada: el resumen («ya se invocó antes; inocuo sobre muerto») requiere revisión antes de cualquier ratificación |
| A4–A11 | `process.x__observe__mutmut_7/11/12/13/22/26/27/28` | `cast("BinaryIO")` → `XX…XX`/`binaryio`/`BINARYIO`/`None` (stdout y stderr) | `typing.cast` es identidad en runtime |
| A12 | `process.x__read__mutmut_12` | `min(65536→65537, remaining + 1)` | **JUSTIFICACIÓN PENDIENTE DE REVISIÓN** — el mínimo NO siempre es `remaining + 1`: difiere cuando `remaining ≥ 65536` (pide 65537 en lugar de 65536); no es equivalencia demostrada. **Nota sucesora (2026-09-15, `CIERRE-FRENTE-C-Y-REVISION-PARTICION-2026-09-15.md` §7)**: la justificación de la oleada («la petición de 65537 no puede servirse por un pipe») queda corregida y acotada — pedir 65537 es legal (lectura corta de `min(count, disponible)`); lo imposible con capacidad por defecto es que una sola `read(2)` devuelva 65537; 65536 es capacidad por defecto del host, no garantía de POSIX; el oráculo propuesto («≥65537 disponibles») es inalcanzable sin `F_SETPIPE_SZ`. **Disposición R3 (2026-09-15, `DISPOSICION-R3-Y-DISENO-PARTICION-2026-09-15.md` §4)**: equivalencia deductiva bajo precondiciones explícitas (capacidad por defecto ≤65536, `os.read` cruda, hijos sin `F_SETPIPE_SZ`) — y frontera demostrada: con capacidad ampliada ≥65537 y `remaining==65536`, el mutante finge `output limit exceeded` (motivo público + log truncado + SIGKILL), sonda sellada `a12-sonda/`. Propuesta B con invalidantes declarados; SIN ratificar |
| A13 | `tools.wct.accept.process.x__read__mutmut_14` | tamaño de lectura: `min(65536, remaining + 1)` → `min(65536, remaining + 2)` | **JUSTIFICACIÓN PENDIENTE DE REVISIÓN** — la lectura pide hasta un byte más por vuelta; no es equivalencia demostrada mientras el contrato observable del tamaño de lectura no la fije. **Disposición R3 (2026-09-15, `DISPOSICION-R3-Y-DISENO-PARTICION-2026-09-15.md` §4.3)**: equivalencia DEDUCTIVA total sin precondición de capacidad — ambos retornan el motivo de exceso exactamente cuando `disponible > remaining` y persisten el mismo `chunk[:remaining]`; con `disponible ≤ remaining` leen idéntico; el residuo (bytes extra consumidos en la ronda ya señalada) no es observable (el hijo se termina y los streams se cierran). Sonda S3 confirma los puntos de frontera (remaining 10, disponibles 9/11/12). Propuesta B; SIN ratificar |
| A14 | `tools.wct.accept.process.x__read__mutmut_17` | EOF de un stream: `continue` → `break` | **JUSTIFICACIÓN PENDIENTE DE REVISIÓN** — el `break` altera la re-selección ante eventos posteriores; no es equivalencia demostrada para todos los órdenes de eventos. **Disposición R3 (2026-09-15, `DISPOSICION-R3-Y-DISENO-PARTICION-2026-09-15.md` §5)**: defecto demostrado con REGRESIÓN PERMANENTE (`test_eof_on_one_stream_still_captures_sibling_output_in_same_round`): EOF en stdout y bytes pendientes en stderr en la misma selección con reloj en el plazo — original verde, variante ROJA por causa contractual (`stderr.log` vacío, captura parcial perdida), verificada contra el mutante real en copia sellada. Propuesta A; ratificación humana pendiente |

**Corrección 2026-09-15 (referencias, sin reabrir la adjudicación)**: las
filas A13/A14 de la versión anterior cruzaban las mutaciones de
`read_mutmut_14`/`read_mutmut_17`; el diff autoritativo del lote r3 asigna
`remaining+1 → remaining+2` a `_14` y `continue → break` a `_17`. La mutación
`selector.select 0.05 → 1.05` pertenece a
`tools.wct.accept.process.x__read__mutmut_2`, ya entre los 11 defectos
funcionales con regresión. La adenda r3 de 2026-09-13 repite la
correspondencia antigua; rige el diff autoritativo. Los IDs abreviados de esta
sección corresponden a `tools.wct.accept.<módulo>.x…`; quedan resueltos por
esta nota. Sin recampaña.

Contabilidad en tres capas (separadas, sin agregaciones):

- **Bruto histórico r3**: 497 = 450 killed + 47 survived. Inmutable.
- **Demostraciones posteriores** (sin recampaña): los 11 funcionales tienen
  regresiones que los matan en demostración (`6e4398e`, `fa3558d`); eso es
  sensibilidad de tests, no veredicto de campaña.
- **Decisiones pendientes**: excluyendo las 14 de esta sección, el inventario
  497 deja **483 sitios no cubiertos por esta decisión**; de los 47
  supervivientes brutos quedan 33 clasificados (11 funcionales con regresión
  demostrada + 15 no contratados + 7 limitaciones), ninguno convertido en
  killed.

Efecto de ratificar estas 14: quedan registradas como equivalentes en alcance
acotado (precedente H-01) y el remanente sin decisión baja a 33 supervivientes
clasificados; **no** se afirma «450/450 muertos» ni cierre del lote. Efecto de
rechazar: quedan como huecos abiertos y el lote sigue FAIL.

**Recomendación, no ratificación (plan §3):** separar A1 (falsy), A2
(códec), A4–A11 (identidad de cast y transferencia explícita del hash r3
bdbb5646… al vigente 84b9340f…). A3/A12/A13/A14 requieren comprobación
causal acotada; no ratificar con las justificaciones vigentes. Las 213 pruebas
de la reparación son evidencia histórica, no una nueva campaña. La adenda
antigua también confunde `_12`: rige el diff autoritativo de esta tabla.

## B. Comportamiento no contratado — 15 IDs (decisión D-B, por familia)

Decisión por familia: ¿es **contrato observable** (entonces aserciones
normativas exactas en un incremento de tests) o **presentación** (queda sin
test; opcionalmente simplificación futura revisable)? Sin decisión, ningún
test se añade y ningún ID se convierte en equivalente por omisión. Recomendar
JSON semántico para B1/B2, causa identificable sin grafía exacta para B3/B4 y
nombre interno para B5 según consumidores revisados (plan §3). Estas decisiones
no resuelven por sí solas TEST-002 ni la disposición de los 15 IDs.

| # | Familia | IDs | Pregunta de contrato |
|---|---|---|---|
| B1 | Indentación de `attempt.json` | `campaign.x__attempt__mutmut_86/88/89` | ¿El formato textual del intento es evidencia contractual o presentación? |
| B2 | Indentación de `report.json` | `campaign.x_run_mutations__mutmut_89/91/92` | ¿El reporte requiere representación textual estable además del esquema JSON? |
| B3 | Literal de `reason` | `campaign.x__results__mutmut_22/23` | ¿`"prior attempt did not pass protocol"` es API de diagnóstico o texto informativo? |
| B4 | Grafía del mensaje de hash | `pytest_receipt.xǁ_Recorderǁ__init____mutmut_10/11/12` | ¿La grafía exacta de `"AC1 original IR hash mismatch"` es contrato? (re-extracción por excepción emitida ya en adenda §2) |
| B5 | Nombre interno del plugin | `pytest_receipt.x_pytest_configure__mutmut_5/7/8/9` | ¿`"wct-accept-receipt-observer"` es contrato de registro? |

## C. Limitaciones instrumentales — 7 IDs (decisión D-C, por grupo)

La terminación acotada, recolección del hijo y captura parcial ya son
obligaciones del CONTRATO-AC1; no son opcionales. Decidir aparte si el límite
interno exacto (p. ej. wait=1 s) debe ser **contrato operativo**. Si lo es, la
vía prioritaria es un **doble por los puntos de sustitución existentes**
(`process_transport.subprocess` / `selectors`, como en T5 y en la prueba de
reloj controlado) — **sin cambio de producto**. Sólo si esos puntos
demostraran ser insuficientes se propondría un adaptador inyectable, y siempre
como incremento separado con TDD propio. Si el límite no es contrato, los IDs
quedan sin ratificar — no se convierten en equivalentes por omisión y no se
fabrican estados imposibles.

| # | Grupo | IDs | Límite en cuestión |
|---|---|---|---|
| C1 | Timeout de `wait` | `process.x__execute__mutmut_28/29`, `x__terminate__mutmut_6/7` | `wait(timeout=1)` frente a `None`/`2`. **Disposición R3 (2026-09-15, `DISPOSICION-R3-Y-DISENO-PARTICION-2026-09-15.md` §4.4–§5)**: `_28/_29` → propuesta B deductiva por alcanzabilidad (el `wait` de `_execute` siempre opera sobre hijo ya terminado o recolectado; sobre hijo muerto el timeout es inmaterial). `terminate__6` (`None`) → defecto demostrado con REGRESIÓN PERMANENTE (`test_terminate_gives_up_on_slow_reap_within_bounded_budget`: reap modelado muy tardío con reloj controlado; original verde cede con `TimeoutExpired`; variante `None` bloquea hasta el reap y retorna normal — ROJO por motivo/duración), verificada contra el mutante real. `terminate__7` (`2`) → C: sin violación (la regresión pasa verde bajo él); decidir si `wait=1 s` exacto es contrato operativo |
| C2 | Deadline inclusivo | `process.x__observe__mutmut_33` | `>=` frente a `>` en la frontera de timeout. **Disposición R3 (2026-09-15)**: divergencia confirmada en frontera (oleada rc=1; afecta bytes persistidos: el mutante lee tras el plazo); la clasificación exige aprobar antes la aclaración contractual «frontera inclusiva: el timeout gana antes de otra lectura». Mientras no se apruebe: conclusión insuficiente (D); aprobada: A con regresión convertible de la sonda |
| C3 | Defensas de cleanup | `process.x__execute__mutmut_31/32` | `_terminate` en `finally` y cierre explícito de streams |

## D. Hooks decorados no instrumentables — 2 hooks (decisión D-D)

`_Recorder.pytest_runtest_makereport` y `.pytest_sessionfinish` son dos
**hooks**, no dos IDs generados: mutmut omite funciones decoradas. Sigue
pendiente autorizar comprobación alternativa. La receta heredada contiene
una contradicción: JSON HOOK-MR-01 = mismatch→pass, adenda §6 espera error.
Propuesta corregida, **NO APROBADA**, en plan §3: control con SemanticMismatch,
exit1 y recibo mismatch válido; MR cambia caso/evento a pass y el validador
rechaza por exit1; SF cambia receipt.exit a 0 conservando exit real1 y el
validador rechaza. Exit no cero solo no es discriminante. Copias temporales,
decoradores intactos, 30 s/corrida y 120 s total propuestos; sin campaña ni
cambio de producto. Evidencia de casos y de fases se conserva por separado.

## E. Cadena restante de AC1 — decisiones de programa (decisión D-E)

**Fuentes externas** (checkout principal, FUERA del worktree de esta rama;
consultadas en modo sólo lectura con corte 2026-09-13; no se copian ni
stagean aquí): `docs/evolution/plans/BETA3/EXECUTION/` del checkout principal:
`PREPARACION-LOTE-GATE-SELFTEST-AC1-2026-09-13.md`,
`ADENDA-PREPARACION-LOTE-GATE-SELFTEST-2026-09-13.md`,
`RECETA-FASE-G-GATE-SELFTEST-2026-09-13.md`,
`ADJUDICACION-FASE-E-GATE-SELFTEST-2026-09-13.md` y
`CIERRE-ADJUDICACION-FASE-E-2026-09-13.md`. El estado formal de cada decisión
es el que consta en esos documentos; esta matriz no convierte propuestas en
ratificaciones.

| # | Pendiente | Estado según fuente | Desbloquea |
|---|---|---|---|
| E1 | **Fase G** (generación y asociaciones del lote gate/selftest): 959 mutantes generados; subconjunto objetivo de 31 IDs de `checks._declared` y `fixtures_tools.f9_a`; **no ejecutó mutantes** | Registrado en la receta de Fase G | Fase E y siguientes |
| E2 | **Fase E** (ejecución de los 31 IDs): bruto **27 killed + 4 survived** (intacto); los ocho kills por excepción **ratificados** y el contrato mínimo de `f9_a`/`load_config` **aprobado**; los cuatro no contratados **detectados** (killed-por-oráculo) en la micro-campaña posterior de exactamente esos 4 IDs; **los 928 restantes no fueron ejecutados** | Ejecución y ratificación en `EJECUCION-INCREMENTO-F9A-LOADCONFIG-2026-09-13` (evidencias de fase E y micro separadas); cierre previo en `CIERRE-ADJUDICACION-FASE-E` | Decisión propuesta por identidad/diff (plan §4): 928 = 649 de checks + 279 de fixtures, funciones preexistentes sin cambio; no excluir archivos completos ni trasladar veredictos. TEST-007 separado |
| E3 | **GS-1**: `semgrep_schema.py` + `semgrep_verdict.py` | **CERRADO por evidencia sucesiva** (sin re-campaña conjunta): R2 midió **280 killed + 2 survived** con el refuerzo O1–O4; el residuo O5 (2 separadores) quedó **RECHAZADO-EVIDENCIADO** bajo el contrato de presentación aprobado e integrado en esta rama (`CIERRE-GS1-O1-O5-INTEGRACION-2026-09-14.md`, base `c6be7ee`). Históricos intactos por capas | Cobertura de mutación de esos módulos |
| E4 | **GS-2**: `semgrep_scope.py` | **EJECUTADO; regresiones integradas; sensibilidad demostrada 16/16** (posterior, `ddb1b46`): bruto **102 killed + 16 survived** (base `ee1e878`); 16 supervivientes RECHAZADOS por regresiones. **Diagnóstico de activación** (`GS2-DIAGNOSTICO-ACTIVACION-SONDAS-2026-09-15.md`): defecto del lanzador sellado; hipótesis in-process retirada (mutmut 3.7.0 forkea por mutante). **Revalidación sucesora** (`GS2-REVALIDACION-Y-PREPARACION-CIERRE-2026-09-15.md`): 34/34 IDs abiertos con activación in-process acreditada, control original verde y causa del mutante en fase call; `x__unique_dirs__mutmut_7` promovido por evidencia sellada; 0 discrepancias, 0 timeouts; **atribución pendiente resuelta / sin residuos abiertos bajo evidencia sucesiva** (verifier independiente: APROBAR-EXPEDIENTE CON RESERVAS menores). Final: 63 histórico + 4 adenda + 35 sucesores + 16 supervivientes = 118. No es campaña completa ni PASS de G-MUT/AC1. **Estado ya autorizado**: «GS-2 cerrado en su alcance mediante evidencia sucesiva; atribución pendiente y residuos resueltos, sin nueva campaña conjunta ni PASS automático de G-MUT o acreditación integral AC1» | Sin puerta nominal E4-PASS ni campaña para cambiar etiqueta; conserva presupuesto histórico consumido 102.3 s de 600 s |
| E5 | **GS-3**: `semgrep.py` | **EJECUTADO** sobre `eec71fb1…` (autorización humana + verifier de puerta APROBAR-CAMPAÑA): inventario 108 mutantes (26 `x__topology` + 8 `x__policy` + 74 `x_gate_sast_semgrep`; 51 sitios WCT, 3 funciones), campaña serial con IDs explícitos, activación acreditada 108/108, canario original verde/mutante rojo, 0 fallos instrumentales. Bruto **74 killed + 34 survived** → **FAIL-survivors-stop** conforme al anexo §7.5; 34 supervivientes conservados con ID, diff, selección y resultado (agrupados; sin reparaciones ni equivalencias ratificadas). Presupuestos: A ~706.6 s de 3600; B ~524.5 s de 1800. Verifier final: CONFORME CON RESERVAS (R1–R4 menores) sobre expediente sellado (`gs3.sha256`, digest `63c83bd2…`). No acredita AC1 ni beta.3. Ver `GS3-SEMGREP-RESULTADO-2026-09-15.md`. **Adjudicación 2026-09-15** (`ADENDA-GS3-ADJUDICACION-2026-09-15.md`): 34/34 clasificados — **13 A** (gap de oráculo), **14 B** (no contratado), **7 C** (equivalencia acotada; 5 medidas y 2 estructurales); sensibilidad medida 27/27 A+B; propuesta F1–F8; sin reparaciones ni equivalencias ratificadas. Verifier: CONFORME CON RESERVAS (R1–R6 menores, atendidas). **Contratos y regresiones 2026-09-15** (`GS3-CONTRATOS-REGRESIONES-Y-EQUIVALENCIAS-2026-09-15.md`): D1–D5 formalizados en `docs/gates.md` y trazados a 4 escenarios y 4 tests de binding; los **27 A+B** con regresión permanente y sensibilidad **27/27** sobre el árbol mutante real (sin campaña completa; 95 corridas/149.1 s de 900); **4 equivalencias ratificadas** en alcance (`mutmut_6/11/26/31`, check falsy; revisión obligatoria si cambia fuente/runtime/precondición); `mutmut_24/29/33`: **propuesta A de equivalencia acotada** (`GS3-DOMINIO-BYTES-STRING-2026-09-15.md`), dominio = salida JSON del binario Semgrep 1.174.0 sin BOM + decodificación UTF-8 del consumidor, respaldada por implementación del productor y observación empírica, con precondiciones, invalidantes y contraejemplos (BOM; locale no-UTF-8) declarados; **no ratificada** (la exclusión categórica previa del BOM queda corregida por nota sucesora). Fast 7/7; tier commit 20 PASS + G-META-1 pre-bless del incremento acumulado. **Cierre acotado 2026-09-15** (`ACTA-CIERRE-ACOTADO-GS3-2026-09-15.md`): el humano ratificó las equivalencias de `mutmut_24/29/33` (dictamen A) **exclusivamente bajo precondiciones explícitas** (Semgrep 1.174.0 y productor identificado; COMMAND exacto; stdout directo sin wrapper que altere los bytes; JSON UTF-8 sin BOM; decodificación efectiva UTF-8), con revisión obligatoria si cambia fuente, productor, comando, runtime o condiciones relevantes; mantuvo el tratamiento actual del decode error (el runner lo convierte en `ERROR` «guard crash» y el CLI bloquea; sin cambio de producto y sin presentarlo como garantía universal); y registró **GS-3 cerrado en su alcance medido** («mediante evidencia sucesiva y equivalencias ratificadas con precondiciones explícitas»). Se conservan: bruto **108 = 74 killed + 34 survived**, **27 regresiones** posteriores, **7 equivalencias ratificadas** en sus respectivos alcances (4 `check` + 3 bytes/string), sin campaña conjunta 108/108 y sin PASS automático de G-MUT, acreditación AC1 ni cierre beta.3. La comprobación de precondiciones de 24/29/33 se ejecuta al calificar el SHA final (acta §5). | Pendientes según el plan ejecutable (`PLAN-EJECUTABLE-CIERRE-AC1-BETA3-2026-09-15.md`): R3-DA/D-B/D-C/D-D y anclaje tras el descomillado de casts; destino de los 928; E6 REGISTRY y TEST-007; aceptación/operador y E8; bless/re-lock de G-META-1 (**23 rutas** medidas) para merge |
| E6 | **GS-4** (denominación original del pendiente sobre archivos preexistentes): el delta de REGISTRY en `runner.py` necesita su comprobación conductual **separada** | **CERRADO en su alcance (2026-09-15)**: prueba PX-REG por la entrada real `REGISTRY["G-SAST-SEMGREP"]` (fuente completa PASS / omisión total ERROR con `0 de 1 fuentes` y `omitida: src/a.py`) y dos controles de sensibilidad que fallan en el caso de omisión; original verde. Ver `OLEADA-TECNICA-CIERRE-AC1-2026-09-15.md` §3. Las puertas finales conservan su alcance | Test conductual y dos controles de sensibilidad acotados; no contrato nuevo |
| E7 | **TEST-007**: obligación de tamaño por sitios WCT de archivos cambiados | **Diseño entregado; implementación sigue bloqueada (2026-09-15)**: métricas productivas 258/442/191 con 264 sitios de módulo en `runner.py`; partición fachada propuesta con submódulos, allowlist y el obstáculo real de los parches por ruta `tools.wct.gate.runner.*`. Ninguna excepción concedida; no se editó ningún archivo. Ver informe §5. **Corrección sucesora (2026-09-15, `CIERRE-FRENTE-C-Y-REVISION-PARTICION-2026-09-15.md` §6)**: la afirmación general de §5.4 queda refutada por patrón para los parches de `shutil.which`/`subprocess.run` (mutan el módulo stdlib compartido; compatibles con mover funciones, demostrado con control discriminante y precedente `mutation.py`) y confirmada solo para nombres co-importados en runner (P2: `remote_base`→`gate_coverage_diff`), cuyo rompimiento es hoy **silencioso**. **Disposición R3 (2026-09-15, `DISPOSICION-R3-Y-DISENO-PARTICION-2026-09-15.md` §6)**: diseño compatible MEDIDO en sandbox aislado — 17 archivos resultantes todos ≤100 sitios (medidos con el motor WCT, datos incluidos); parches P2/P2′/P2″ preservados por diseño de fachada y P1 por imports retenidos, acreditados con falsos que registran y con la suite de los archivos sensibles (20 passed sin tocar tests); suite unitaria del sandbox idéntica al baseline (642 passed); 0 ciclos; `REGISTRY` único (47 = 22+14+11+3) con identidad de entradas verificada; mapa/allowlist/impacto (re-anclaje de `_declared`/`f9_a` y preexistencia 928) y orden de integración por fases entregados. La implementación sigue SIN autorizar y TEST-007 sigue abierto | Partición acotada con rutas previamente aprobadas, o decisión humana previa de procedimiento de excepción; ninguna concedida |
| E8 | Puertas posteriores una vez cerrados los lotes: mutación de aceptación → cobertura/CRAP → DRY → tier full | **Parcial (2026-09-15)**: comprobaciones r3 ejecutadas con resultado por ID (cuatro casos, siete límites, dos hooks; ver informe §2) y regresión permanente de limpieza/captura. La tabla/Outlines de aceptación quedó implementada y verde en copia, pero **bloqueada** porque el literal aprobado produce 3 hallazgos nuevos de G-ACCEPT (§4). **Actualización sucesora (2026-09-15, `CIERRE-FRENTE-C-Y-REVISION-PARTICION-2026-09-15.md`)**: aprobada la alternativa 1 de §4.3, el frente C quedó **desbloqueado, integrado y publicado** en `codex/beta3-ac1-r2-integration` (dos Outlines con selectores numéricos, inventario 47 trazado al histórico 48, reformulación de los tres pasos del aborto); G-ACCEPT 0 hallazgos, focales/colección conciliadas (686 = 667+19), A/B verdes, fast 7/7, commit 20 PASS + G-META-1 pre-bless sin otro rojo. Q-ACCMUT y campaña global **no ejecutadas** | Calificación pre/post-bless con identidades T/B/M/V separadas (plan §2) |
| E9 | Revisión humana del drift de integridad pre-bless declarado en la PR #53 | **23 rutas protegidas** en drift al candidato de `REPARACION-INTEGRACION-GDEPS-GDEAD-2026-09-15.md` (7 modificadas + 16 nuevas; la fórmula previa «20 rutas» queda superada por la medición). Re-medido en la oleada 2026-09-15: 23 = 7 + 16, **sin drift nuevo** (solo tests cambiados). G-META-1 sigue siendo el único rojo del tier `commit`. Pendiente | Cualquier bless futuro |
| E10 | Convención de versión/tag de beta.3 (vigente `1.0.0-beta.2`) | **Convención elegida (2026-09-15)**: `1.0.0b3.dev1` como objetivo futuro, sin claim beta.3 completa y sin dispensar obligaciones del incremento publicado (plan §6). Bump/lock/tag no autorizados ni ejecutados | Release, si llega a ser elegible; versión/custodia/SBOM/smokes/D3 no autorizados |
| E11 | Revisión del diff completo y salida de borrador de la PR #53 | Pendiente | Merge, sólo con E1–E9 conformes |

## Registro de incidente de staging (punto 6 del cierre de T5)

El fichero ajeno `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md` fue
**publicado accidentalmente** en `5f1ae51` (ya estaba en el índice antes del
`git add` explícito) y **retirado del seguimiento** en `38bdf88`; el diff final
de la rama no lo contiene y el fichero permanece en disco sin seguimiento.
Se registra como publicación accidental corregida en el diff final — **no**
como ausencia de publicación.

## Recomendación de orden

Decisiones concretas y prompt técnico en plan ejecutable §3–§9; no crear otra
oleada de dossiers. Decidir fundamentos r3 por separado, alcance por diff y
vía TEST-007; aprobar contratos de tabla/arnés antes de implementación.
REGISTRY y hooks pueden comprobarse en paralelo en copias independientes;
las ediciones r3/aceptación del mismo test se integran de forma serial.
GS-1/2/3 conservan cierres acotados y evidencia histórica, sin campaña nueva
para cambiar etiquetas. Resolver fuentes antes de E8 y seguir PRE-BLESS /
POST-BLESS del plan, con revisión protegida humana y verificación del SHA real
integrado antes de publicación. Ninguna recomendación habilita por sí sola
ratificación, excepción, bless, merge, bump, tag ni release.
