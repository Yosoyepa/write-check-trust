# Registro REANCLAJE-12 — campaña L4 (decoder y secuencia): resultado bruto y atribución causal (2026-09-19)

Estado del lote: **FAIL-SURVIVORS-STOP.** La campaña L4 se ejecutó completa y
su resultado se mide y atribuye: **473 mutantes = 426 killed (exit 1) + 1
killed por no-terminación (exit −24) + 46 survived**. Los 46 sobrevivientes
quedan **sin disposición** — este encargo no ratifica equivalencias, no
establece excepciones y no traslada las disposiciones de L2 — por lo que el
lote se detiene aquí con residuos declarados. **El dictamen favorable de los
verifiers es al EXPEDIENTE, no al cierre del lote.** No se declara P03a ni
beta.3 cerrados. Sin cambios de producto/tests/contratos, sin otros lotes,
binding, Q-ACCMUT, cobertura/CRAP/DRY/full, bless, merge, bump, tag ni
release. L2 permanece cerrado en su alcance.

## 1. Base, identidades y aislamiento

| Elemento | Identidad | Comprobación |
|---|---|---|
| Base autorizada (técnica) | `0487448032c1e1cf56bd18f98f9bea9586f3fc46` = origin `codex/reanclaje-p03a-fase1` = headRefOid PR #56 (borrador); main `8a379d64…` = baseRefOid = merge-base; sin avance posterior | `git ls-remote` + `gh pr view 56` |
| Árbol del candidato | tree `d00e4725da2a323b7bf1fb202719401912d3625c`; copia Git NUEVA `build/tmp/reanclaje12-20260918/repo/`, detached, árbol limpio durante todo el encargo (el registro se publica después de la revisión) | `git clone` + `git rev-parse HEAD^{tree}` |
| Fuentes autorizadas (hashes completos) | `pytest_decode_header.py` `ed6f6bc1a90e7e99d013d2dc36eaed3d44a9595221308099bbd194d4d8451cf7`; `pytest_decode_events.py` `d73b5b2682684774b40c89d3d61ed46e0ba23adc926377f5dca3dd7c3d52e826`; `pytest_sequence.py` `014474094a568596eeb794ac58947f6ad848061962b3133c89c6b0431387a84c` — intactas al abrir y al cerrar | `sha256sum` apertura/cierre |
| Tests de la selección | `test_pytest_schema.py` `e7d82c9918156a161611dae9d4d3b692e8b28fae18a4d6c8d3691a502037ed1a`; `test_pytest_observation.py` `5d3d30a6b6d193956a075d603738070b3d7a37813830678112597b6dc91683db` — sin cambios (idénticos en repo/, run/ y mutants/) | `sha256sum` + diff |
| Runtime | venv propio (`uv sync --all-groups`): Python 3.13.14, pytest 9.1.1, mutmut 3.7.0; wct del venv; nada instalado en entornos compartidos | `--version` |
| pyproject | original `f27de519…` sellado aparte; experimental `4a45f16b…` SOLO en `run/` (source_paths = las 3 fuentes, also_copy, selección) | hashes separados en custodia |
| Aislamiento | lanzador fail-closed: cwd=`run/mutants`, `PYTHONPATH` absoluto a mutants, sonda de identidad de imports (`tools.wct` resuelve DENTRO) + activación verificada con el mismo entorno del hijo | logs/08 |

Checkout principal, índices ajenos, worktrees/evidencia históricos, main,
tag `v1.0.0b3.dev1` y releases: intactos. Sin lectura de credenciales.

## 2. Inventario independiente y selección congelada

**Inventario AST** (antes de generar): 23 callables = 7 header + 10 events +
6 sequence (defs y métodos; sin defs anidadas ni decoradas con lógica propia
en estas fuentes); tablas/expressions de módulo: `_CATALOG` (events),
`_CAPPED`/constantes de tope (sequence). Consumidores reversos: header y
events ← `pytest_schema.py` (bucle de decodificación, superficie pública);
sequence ← decode_events, decode_header, observation_events,
observation_inventory, schema (`logs/01-inventario-ast.json`).

**Métrica de sitios WCT** reproducida con el motor del repositorio
(`tools.wct.mutate.engine.function_sites`): **247 = 72 header + 94 events +
81 sequence** — coincide exactamente con la referencia del plan. Métrica de
planeación, NO conteo de mutantes: mutmut generó **473** IDs reales
(proporción 1,9 por sitio; sin razón impuesta).

**Selección congelada** (derivada por colección fresca del candidato, NO
reutilizada de L2): `tests/unit/test_pytest_schema.py` completo (112) + 28
case-IDs PA02/PA03 de `test_pytest_observation.py` = **140 nodeids únicos**,
digest `9b96790cef4ff7d1a39d64130b89185f82cb0898c26f4ec3f056b713c2f58bf9`
(`custodia/seleccion-140.nodeids`). Sin amplificación: la selección del plan
resultó suficiente (23/23 asociaciones no vacías). El nodeid con espacio
literal viaja como cadena completa (argv por listas, sin split). Efectos
laterales: ninguno (case-IDs decodifican journals literales; `conftest`
inspeccionado en R6).

**Baseline**: colección 140/140 exit 0; **140 passed, exit 0, sin
skips/xfails/errores, property fuera** (2.82 s; imports acreditados).

## 3. Generación fresca y custodia

Generación pura (centinela `ZZ_GENERACION_R12_NO_MATCH`): «3 files mutated,
0 ignored, 0 unmodified» + assert «Filtered for specific mutants, but nothing
matches» ANTES de todo test; 0 «Listing all tests» (logs/06). Inventario por
AST del instrumentado: **473 = header 113 + events 257 + sequence 103**
(conjunto == claves de `.meta`). Diffs por ID: 473 secciones, digest
`ee2bee59147b006743251d32a4d33556560a2bc6b27b4432d6a52a015af0bd01`.
Asociaciones (stats inicial): **23/23 funciones no vacías; 473/473 IDs con
función portadora asociada** (4–84 IDs por portadora; 28–121 tests asociados).
Custodia estática sellada (12 miembros, `custodia/sello-estatico.sha256`):
acta no aplica (sin decisiones en este encargo), selección, inventario,
diffs, 3 instrumentadas + hashes, 2 tests, pyprojects, stats/meta inicial.
Estados inicial (todo `None`) y final (473 resultados) como snapshots
separados; ningún miembro sellado reescrito. Solo las 3 fuentes autorizadas
contienen trampolines (verificado por el verifier final: 3/35 archivos).
Sin `print-time-estimates`.

**Límite instrumental declarado**: los 14 sitios WCT de cuerpos de módulo
(header 1, events 1, sequence 12 — `_CATALOG`, `_CAPPED`, constantes) NO
generan IDs: mutmut 3.7 solo instrumenta cuerpos de función. Cero IDs ≠
cobertura ni equivalencia para esas tablas.

## 4. Activación, canario y negativos (logs/08, logs/09)

- **Canario L4** `tools.wct.evidence.pytest_decode_events.x__execution_index__mutmut_1`
  (diff `type(ex_value)` → `type(None)`, resuelto por ID y diff en el
  inventario): ORIGINAL **140 passed**; mutante **rojo con causa
  contractual** — 62 failed de 65 asociados; `AssertionError: assert 0 == 4`
  (journal válido decodifica 0 eventos: el mutante rechaza todo
  execution_index VÁLIDO, contrato §4.4). Activación acreditada en el
  proceso de pytest (lanzador fail-closed + trampolines).
- **Negativos** (bloquean ANTES de pytest): ID desconocido → exit 2;
  selección vacía → exit 2; hash adulterado → exit 2 (restaurado y
  revalidado); activación ausente → sonda rc 3; imports incorrectos
  (resolución al árbol original) → sonda rc 3.
- **Verifier preflight independiente**: DICTAMEN FAVORABLE, 0 bloqueantes
  (corte/alcance/selección/inventario/asociaciones/activación/custodia/
  presupuesto reproducidos en copia propia; hallazgos menores: wording del
  estado inicial de `.meta` y redondeo A 26.05↔26.06). Informe:
  `build/tmp/reanclaje12-20260918-verifier/INFORME-PREFLIGHT.md`.

## 5. Campaña y bruto reconciliado

Serial con los 473 IDs explícitos (`mutmut run --max-children 1 <IDs>`), sin
cambios de fuente/tests/selección durante la corrida. **406.0 s, exit 0**
(sobre B; logs/10). Reconciliación por conjuntos: generado = autorizado =
resultados = **473**; 0 duplicados, 0 ajenos, 0 faltantes, 0 no ejecutados;
un estado final por ID. El log corrobora: 426 veredictos 🎉 + 46 🙁 + 1 ⏰
únicos, sin solapes, en desacuerdo 0 con el `.meta`.

**BRUTO MEDIDO (L4, selección 140): 473 = 426 killed (exit 1) + 1 killed por
no-terminación (exit −24) + 46 survived (exit 0).**

## 6. Atribución causal (clasificación separada del bruto)

| Clase | # | Base |
|---|---:|---|
| KILLED-EVIDENCIADO | 426 | campaña exit 1 sobre conjunto asociado completo + arnés acreditado (canario con causa, ORIGINAL verde, asociaciones no vacías, negativos, forced-fail de mutmut) |
| KILLED-EVIDENCIADO (no-terminación) | 1 | `x__consume_line__mutmut_22` (exit −24, señal SIGXCPU a los 117 s): el diff invierte `if defect is not None` → toda línea limpia retorna sin avanzar offset → **bucle infinito**. Sonda fresca: ORIGINAL verde en 2.78 s; mutante matado a los 30 s en el MISMO test (`PA02-invalid-utf8`). No-terminación causada por el mutante, consumida por el bucle público de decodificación (§4: consumed_bytes/tail). Taxonomía mutmut: −24 = killed; aquí se reporta con su causa |
| SURVIVED-REPRODUCIDO | 46 | sonda fresca por ID contra sus tests asociados: 46/46 exit 0 con activación acreditada, 0 contradicciones (363.8 s; logs/12, logs/13) |
| SURVIVED-OBSERVADO-EN-CAMPAÑA | 0 | (todos los sobrevivientes además se reprodujeron) |
| PENDIENTE-DE-ATRIBUCIÓN | 0 | (evidencia causal completa; la DISPOSICIÓN humana queda pendiente, que es otra cosa) |
| INSTRUMENTAL/DISCREPANCIA | 0 | sin errores de colección/imports/lanzador; sin exit 3/5/33/34/35 |

Exit 1 por sí solo no se tomó como kill: la cadena incluye canario con
causa, ORIGINAL verde, asociaciones y — para el caso no estándar (−24) —
sonda fresca de no-terminación. El verifier final reejecutó además un killed
con causa semántica propia (`x__check_sequence__mutmut_2` → `assert
'sequence_error' == 'invalid_field'`, 1 failed de 65, ORIGINAL verde) y dos
sobrevivientes de grupos distintos (ambos exit 0).

### 6.1 Los 46 sobrevivientes, agrupados por comportamiento (DESCRIPTIVO)

Tabla completa por ID en `logs/14-clasificacion-supervivientes.json`;
diffs por ID en `custodia/diffs-por-id-nuevo.txt`. **Ninguna disposición se
ratifica**: equivalencia, hueco de oráculo y excepción quedan para decisión
humana posterior; nada se excluye «por parecerse a L2».

| Grupo | # | Descripción |
|---|---:|---|
| A — atribución de execution_id del defecto | 8 | la atribución se elimina o muta su fuente (`decode_event_19/20/39`, `execution_index_4/6/14/16`, `finish_5`); estructura presente, valor None/omitido en los caminos actuales de raise (el mismo canal que R10 §5.2 analizó para L2 — aquí SOLO como observación, sin trasladar disposición) |
| B — código de finding manglado | 7 | `invalid_field`/`foreign_reference` → None/XX/mayús/atributo en `_execution_index` y `_resolve_field_nodeid` |
| C — zip strict tras chequeo de longitud previo | 6 | `strict` de zip mutado cuando la MISMA función ya validó igualdad de longitudes y raise antes del zip (`validated_vector_13/16/17`, `match_executions_10/13/14`) — observación estructural, NO ratificada |
| D — ventana de atribución | 4 | type/rango de `_attributed_execution` (2/3/4/5); solo aflora en el canal del grupo A |
| E — frontera seq/local_seq | 3 | `or→and` y `>→>=` en los rangos: divergen en valores fuera de rango o en SEQ_MAX exacto, no construidos por la selección |
| F — granularidad de inventario de fases | 9 | clave/default de fase colapsan el bucket por fase o desactivan su tope; observable solo en MAX_INVENTORY_ENTRIES |
| G — clave/coerción de nodeid del vector | 4 | la condición `"nodeid" in fields` manglada nunca aplica / la coerción `_int_in` se desvía a otra clave; divergencia en índices fuera de rango |
| H — forma del vector/cabecera | 2 | `or→and` en tipo-lista/aridad: divergen en entradas malformadas exóticas no construidas por la selección |
| I — slice de digests del header | 1 | `wire[2:5]→[2:6]`: truncado por la longitud exacta validada antes — observación estructural, NO ratificada |
| J — llamada a inventario | 2 | argumentos de `_check_inventory` (ex→None, cls→None): cambian la clave del contador o desactivan el tope |

## 7. Revisión final — verifier independiente: FAVORABLE al expediente

Tercer agente, sin escritura, copia propia. **DICTAMEN: FAVORABLE al
expediente L4** (P1–P6: bruto recalculado 426/46/1 con verificación de
progreso monotónico del log; clasificación con cobertura exacta y sin
ratificaciones — intersección vacía con el lenguaje de disposición de L2;
reejecuciones propias de un killed con causa, dos sobrevivientes de grupos
distintos, la no-terminación y un negativo; fuentes/tests intactos; 3/3
instrumentadas exactas; sello 12/12; ledger sin discrepancias). Hallazgos
menores: la declaración de estado debe quedar en archivo versionado (este
registro la consigna), huérfanos de la sonda de no-terminación (encontrados
y terminados por el verifier; higiene de proceso), redondeos inmateriales.
**El dictamen es al expediente; el estado del LOTE sigue siendo
FAIL-SURVIVORS-STOP.** Informe:
`build/tmp/reanclaje12-20260918-verifier-final/INFORME-FINAL.md`.

## 8. Presupuesto real (guardián monotónico, logs/00)

| Sobre | Techo | Real | Estado |
|---|---:|---:|---|
| A — preflight/baseline/generación/asociaciones/controles | 300 s | 26.06 s | ✔ |
| B — campaña | 1200 s | 405.98 s | ✔ |
| C — sondas causales | 600 s | 396.61 s | ✔ (46 sondas + no-terminación ×2) |
| D — reejecuciones de verifiers | 240 s | 90.93 s (preflight 12.10 + final 78.83, ledgers propios) | ✔ |
| **Experimental total** | **2340 s** | **919.58 s** | ✔ |
| PUB — fast y publicación | 180 s | ver §10 | aparte |

Sin transferencias entre sobres ni uso del saldo de L2; intentos inválidos:
0 (un `print` final de un driver de sondas falló por nombre de variable
DESPUÉS de escribir el JSON — se reporta como incidencia menor del arnés,
sin efecto en evidencia ni presupuesto). Timeouts por hijo limitados al
saldo; control exclusivo de procesos propios; nada dependió del buffering
de stdout. Limitación conocida del guardián (hallazgo del verifier final):
el kill del hijo directo puede dejar nietos colgando en la sonda de
no-terminación — los huérfanos fueron terminados; futuros guardianes deben
matar el grupo de proceso.

## 9. CI y pasos no ejecutados

Commit de este registro observado con seguimiento acotado (§10). El gate de
integridad del PR falla por el drift protegido preexistente (34 «nuevo
protegido» + 2 «modificado», R10 §2.C); los pasos mecánicos posteriores
quedan SKIPPED por ese fallo. **Bless y merge siguen fuera del job**
(operaciones humanas). No se ejecutaron: otros lotes, L1/L3/L5+, repetición
de L2, binding PA01–PA12, Q-ACCMUT, cobertura/CRAP/DRY/full, update-manifest,
bump, tag, release. No se pronostica el resultado de la CI tras bless.

## 10. Sellado y publicación

Expediente `build/tmp/reanclaje12-20260918/`: `MANIFIESTO-REANCLAJE12.sha256`
(logs, lanzador, guardián, custodia y este registro; sin auto-hash; digest y
verificación fuera de sus miembros). Publicación en PR #56 (borrador):
staging exclusivo de este registro; commit convencional con byline; hooks
activos (WCT fast + cz check); push normal sin force; fast ejecutado sobre
la copia bajo el sobre PUB.

## 11. Próxima autorización mínima — NO EJECUTADA

**PROPUESTO**: encargo humano de **disposición de los 46 sobrevivientes L4**
con el método R8/R10 (diff + lectores + sonda de comportamiento contra API
pública; clasificación hueco-de-oráculo → oráculo TDD en rutas aprobadas /
equivalencia propuesta → acta con ratificación humana / no contratado →
disposición explícita), seguido si procede de una re-campaña con la selección
ampliada resultante. Alternativa: pausa de L4 y avance a L3 (payloads y
catálogo) con los sobrevivientes L4 documentados. Nada de esto se ejecutó.
