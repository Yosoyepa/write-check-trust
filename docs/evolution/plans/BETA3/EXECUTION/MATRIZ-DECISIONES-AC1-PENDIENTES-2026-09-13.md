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
| A3 | `process.x__execute__mutmut_30` | guarda del `finally`: `is None` → `is not None` | en la ruta con `reason`, `_terminate` ya se invocó antes; sobre proceso muerto `_terminate` es inocuo |
| A4–A11 | `process.x__observe__mutmut_7/11/12/13/22/26/27/28` | `cast("BinaryIO")` → `XX…XX`/`binaryio`/`BINARYIO`/`None` (stdout y stderr) | `typing.cast` es identidad en runtime |
| A12 | `process.x__read__mutmut_12` | `min(65536→65537, remaining + 1)` | el mínimo efectivo sigue siendo `remaining + 1` |
| A13 | `process.x__read__mutmut_14` | EOF de un stream: `continue` → `break` | el `while` exterior re-selecciona; mismo drenaje en ≥2 vueltas |
| A14 | `process.x__read__mutmut_17` | `selector.select(timeout=0.05)` → `1.05` | latencia interna de sondeo dentro del presupuesto del SUT |

Efecto de ratificar: quedan registradas como equivalentes en alcance acotado
(mecanismo del precedente H-01); el ajustado de r3 pasa a 450/450 no
equivalentes muertos. Efecto de rechazar: quedan como huecos abiertos y el
lote sigue FAIL.

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

Primero decidir si el límite exacto es **contrato operativo**. Si lo es,
autorizar un adaptador/doble de subprocess inyectable (cambio de producto con
TDD propio, incremento separado) que lo observe sin matar procesos ajenos.
Si no lo es, quedan sin ratificar — no se convierten en equivalentes por
omisión y no se fabrican estados imposibles.

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

| # | Pendiente | Desbloquea |
|---|---|---|
| E1 | Autorizar el lote de mutación `gate/{checks,runner,semgrep,semgrep_schema,semgrep_scope,semgrep_verdict}.py` + `selftest/fixtures_tools.py` (receta y foco por presentar antes de ejecutar, estándar r3: preflight H-04 + verifier) | Cierre de fuentes AC1 |
| E2 | Ordenar las puertas posteriores una vez cerrados los lotes: mutación de aceptación → cobertura/CRAP → DRY → tier full | Calificación de integración |
| E3 | Revisión humana del drift de integridad pre-bless (20 rutas protegidas `tools/wct/**`) declarado en la PR #53 | Cualquier bless futuro |
| E4 | Convención de versión/tag de beta.3 (vigente `1.0.0-beta.2`) | Release, si llega a ser elegible |
| E5 | Revisión del diff completo y salida de borrador de la PR #53 | Merge, sólo con E1–E3 cerrados |

## Recomendación de orden

D-B (definir contratos) antes que D-A (ratificar equivalencias) si se quiere
decidir con la política de mensajes ya fijada; D-C y D-D son independientes y
pueden resolverse en paralelo; E1 puede autorizarse en cuanto D-A/D-C tengan
dictamen para no arrastrar huecos abiertos al lote siguiente. Ninguna decisión
de esta matriz habilita por sí sola bless, merge, bump, tag ni release.
