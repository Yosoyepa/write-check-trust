# Matriz única de decisiones pendientes — AC1 (2026-09-13)

Estado: consolidación de referencia para decisión humana. **Esta matriz no
ratifica nada por sí misma**, no ejecuta campañas, no cambia producto ni
gobernanza. Base vigente: `fa3558d` (T5 aceptado y congelado como referencia;
sin nuevas modificaciones de ese test). Fuentes reutilizadas: matriz
`ADJUDICACION-SUPERVIVIENTES-AC1-R3-2026-09-13.{md,json}` (clasificaciones y
sondas), `ADENDA-AC1-R3-DENOMINACION-ORACULOS-REGRESIONES-2026-09-13.md`
(oráculos de hooks y regresa­ciones), `RESULTADO-AC1-LOTE-R3-2026-09-13.md`
(resultado bruto), `RATIFICACION-AC1-R2B-H01-H04-2026-09-13.md` (precedente de
ratificación y mecanismo), expediente `build/tmp/ac1-r2-qualification/`.

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
| A12 | `process.x__read__mutmut_12` | `min(65536→65537, remaining + 1)` | **JUSTIFICACIÓN PENDIENTE DE REVISIÓN** — el mínimo NO siempre es `remaining + 1`: difiere cuando `remaining ≥ 65536` (pide 65537 en lugar de 65536); no es equivalencia demostrada |
| A13 | `process.x__read__mutmut_14` | EOF de un stream: `continue` → `break` | **JUSTIFICACIÓN PENDIENTE DE REVISIÓN** — el resumen («re-selección en la siguiente vuelta») no cubre todos los órdenes de eventos; no es equivalencia demostrada |
| A14 | `process.x__read__mutmut_17` | `selector.select(timeout=0.05)` → `1.05` | **JUSTIFICACIÓN PENDIENTE DE REVISIÓN** — el resumen («latencia dentro del presupuesto») no está demostrado para todos los caminos; no es equivalencia demostrada |

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

## B. Comportamiento no contratado — 15 IDs (decisión D-B, por familia)

Decisión por familia: ¿es **contrato observable** (entonces aserciones
normativas exactas en un incremento de tests) o **presentación** (queda sin
test; opcionalmente simplificación futura revisable)? Sin decisión, ningún
test se añade y ningún ID se convierte en equivalente por omisión.

| # | Familia | IDs | Pregunta de contrato |
|---|---|---|---|
| B1 | Indentación de `attempt.json` | `campaign.x__attempt__mutmut_86/88/89` | ¿El formato textual del intento es evidencia contractual o presentación? |
| B2 | Indentación de `report.json` | `campaign.x_run_mutations__mutmut_89/91/92` | ¿El reporte requiere representación textual estable además del esquema JSON? |
| B3 | Literal de `reason` | `campaign.x__results__mutmut_22/23` | ¿`"prior attempt did not pass protocol"` es API de diagnóstico o texto informativo? |
| B4 | Grafía del mensaje de hash | `pytest_receipt.xǁ_Recorderǁ__init____mutmut_10/11/12` | ¿La grafía exacta de `"AC1 original IR hash mismatch"` es contrato? (re-extracción por excepción emitida ya en adenda §2) |
| B5 | Nombre interno del plugin | `pytest_receipt.x_pytest_configure__mutmut_5/7/8/9` | ¿`"wct-accept-receipt-observer"` es contrato de registro? |

## C. Limitaciones instrumentales — 7 IDs (decisión D-C, por grupo)

Primero decidir si el límite exacto es **contrato operativo**. Si lo es, la
vía prioritaria es un **doble por los puntos de sustitución existentes**
(`process_transport.subprocess` / `selectors`, como en T5 y en la prueba de
reloj controlado) — **sin cambio de producto**. Sólo si esos puntos
demostraran ser insuficientes se propondría un adaptador inyectable, y siempre
como incremento separado con TDD propio. Si el límite no es contrato, los IDs
quedan sin ratificar — no se convierten en equivalentes por omisión y no se
fabrican estados imposibles.

| # | Grupo | IDs | Límite en cuestión |
|---|---|---|---|
| C1 | Timeout de `wait` | `process.x__execute__mutmut_28/29`, `x__terminate__mutmut_6/7` | `wait(timeout=1)` frente a `None`/`2` |
| C2 | Deadline inclusivo | `process.x__observe__mutmut_33` | `>=` frente a `>` en la frontera de timeout |
| C3 | Defensas de cleanup | `process.x__execute__mutmut_31/32` | `_terminate` en `finally` y cierre explícito de streams |

## D. Hooks decorados no instrumentables — 2 IDs (decisión D-D)

`_Recorder.pytest_runtest_makereport` y `.pytest_sessionfinish` (mutmut excluye
funciones decoradas). Decisión: **autorizar o no** la comprobación alternativa
ya especificada (no ejecutada): copia del plugin + proyecto pytest mínimo bajo
`build/tmp/ac1-r2-qualification/r3-hook-alternative/<run>/`; control +
`makereport` sembrado + `sessionfinish` sembrado; oráulos definidos en la
adenda §6 (`receipt.json`/`events` difieren y `validate_receipt` invalida);
30 s de timeout exterior, grupo propio, limpieza en `finally`. No retira
decoradores ni altera API; no es campaña.

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
| E2 | **Fase E** (ejecución de los 31 IDs): bruto **27 killed + 4 survived** (intacto); los ocho kills por excepción **ratificados** y el contrato mínimo de `f9_a`/`load_config` **aprobado**; los cuatro no contratados **detectados** (killed-por-oráculo) en la micro-campaña posterior de exactamente esos 4 IDs; **los 928 restantes no fueron ejecutados** | Ejecución y ratificación en `EJECUCION-INCREMENTO-F9A-LOADCONFIG-2026-09-13` (evidencias de fase E y micro separadas); cierre previo en `CIERRE-ADJUDICACION-FASE-E` | Decidir el destino de los 928 no ejecutados (GS-4); TEST-007 separado |
| E3 | **GS-1**: `semgrep_schema.py` + `semgrep_verdict.py` | **CERRADO por evidencia sucesiva** (sin re-campaña conjunta): R2 midió **280 killed + 2 survived** con el refuerzo O1–O4; el residuo O5 (2 separadores) quedó **RECHAZADO-EVIDENCIADO** bajo el contrato de presentación aprobado e integrado en esta rama (`CIERRE-GS1-O1-O5-INTEGRACION-2026-09-14.md`, base `c6be7ee`). Históricos intactos por capas | Cobertura de mutación de esos módulos |
| E4 | **GS-2**: `semgrep_scope.py` | **EJECUTADO; regresiones integradas; sensibilidad demostrada 16/16** (posterior, `ddb1b46`): bruto **102 killed + 16 survived** (base `ee1e878`); los 16 supervivientes están RECHAZADOS por las regresiones del contrato de diagnóstico aprobado. **Diagnóstico de activación corregido** (`GS2-DIAGNOSTICO-ACTIVACION-SONDAS-2026-09-15.md`): las 34 sondas focales del cierre no activaron `MUTANT_UNDER_TEST` (defecto del lanzador sellado) — su exit 0 mide el original y queda `EVIDENCIA-DE-SONDA-INSUFICIENTE`; `x__unique_dirs__mutmut_6` queda `PENDIENTE-DE-REVALIDACIÓN`; la hipótesis de contaminación in-process / corrupción de trampolín queda retirada (mutmut 3.7.0 forkea por mutante). Contabilidad completa: 63 KILLED-EVIDENCIADO histórico + 4 de la adenda + 34 sin evidencia + 1 pendiente + 16 supervivientes = 118. Lote NO aprobado como PASS | Revalidar los 34 IDs con la receta corregida y, si se requiere, revisar ID a ID los 63; no ejecutado en este incremento |
| E5 | **GS-3**: `semgrep.py` | Lote PROPUESTO, no ejecutado | Ídem |
| E6 | **GS-4** (denominación original del pendiente sobre archivos preexistentes): el delta de REGISTRY en `runner.py` necesita su comprobación conductual **separada** | Pendiente; G/E sólo avanzaron la medición de `_declared` y `f9_a` | Cierre del alcance preexistente |
| E7 | **TEST-007**: obligación de tamaño por sitios WCT de archivos cambiados | Abierta; **no** se resuelve seleccionando sólo 31 mutantes ni mediante su adjudicación | Conformidad de límites |
| E8 | Puertas posteriores una vez cerrados los lotes: mutación de aceptación → cobertura/CRAP → DRY → tier full | No iniciadas | Calificación de integración |
| E9 | Revisión humana del drift de integridad pre-bless (20 rutas protegidas `tools/wct/**`) declarado en la PR #53 | Pendiente | Cualquier bless futuro |
| E10 | Convención de versión/tag de beta.3 (vigente `1.0.0-beta.2`) | Pendiente | Release, si llega a ser elegible |
| E11 | Revisión del diff completo y salida de borrador de la PR #53 | Pendiente | Merge, sólo con E1–E9 conformes |

## Registro de incidente de staging (punto 6 del cierre de T5)

El fichero ajeno `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md` fue
**publicado accidentalmente** en `5f1ae51` (ya estaba en el índice antes del
`git add` explícito) y **retirado del seguimiento** en `38bdf88`; el diff final
de la rama no lo contiene y el fichero permanece en disco sin seguimiento.
Se registra como publicación accidental corregida en el diff final — **no**
como ausencia de publicación.

## Recomendación de orden

D-B (definir contratos) antes que D-A (ratificar equivalencias) si se quiere
decidir con la política de mensajes ya fijada; D-C y D-D son independientes y
pueden resolverse en paralelo; el lote GS-1/2/3 puede
planificarse en cuanto D-A/D-C tengan dictamen y el destino de los 928 no
ejecutados de la Fase E esté decidido, para no arrastrar huecos abiertos. Ninguna decisión
de esta matriz habilita por sí sola bless, merge, bump, tag ni release.
