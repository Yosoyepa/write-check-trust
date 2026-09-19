# Registro REANCLAJE-17 — primera campaña del lote L3 (payloads y catálogo): resultado y límites (2026-09-19)

Estado: **primera campaña L3 ejecutada y reconciliada, con límite instrumental
descubierto y FAIL-SURVIVORS-STOP declarado.** Bruto conservado íntegro:
**129 = 99 killed + 30 survived** (sin timeouts ni estados anómalos). Nada
ratificado; sin reparaciones; sin segunda campaña. **Corrección de la propuesta
final de R16**: el cierre de L4 NO habilita saltar lotes — este encargo midió
L3 únicamente porque un encargo específico lo autorizó; L1 y L5–L9 siguen
pendientes de los suyos.

## 1. Base, identidades y aislamiento

Base `e8d6141d16a487db3a94fc1a92c447a0650e5349` == remoto == headRefOid PR #56
(borrador, OPEN); merge-base con main `8a379d64…` = main; tag `v1.0.0b3.dev1`
intacto; checkout principal y expedientes históricos preservados. Sin avance
que clasificar. Expediente aislado `build/tmp/reanclaje17-20260919/` (Git
propio, venv propio `uv sync --all-groups`); runtime acreditado: Python
3.13.14, pytest 9.1.1, mutmut 3.7.0, imports resolviendo dentro de la copia.

## 2. Fuentes, sitios y mutantes (referencia R6 REVALIDADA, no impuesta)

Las 6 fuentes autorizadas, hashes congelados (logs/02, logs/05):
`pytest_payload_classes bd117302…`, `pytest_payload_predicates ee321fb7…`,
`pytest_payload_validate e242772c…`, `pytest_payloads b28d3bb2…`,
`pytest_event_catalog 0caee719…`, `pytest_limits eaa1be95…`.

| Métrica | R6 (referencia) | R17 (revalidada) |
|---|---|---|
| Sitios WCT | 337 (métrica del motor, por función) | **357** (pasada AST propia con `MUTABLE_NODES` sobre el árbol completo; la diferencia es metodológica: incluye sitios de cuerpos de módulo/clase contados distinto) |
| Callables | 15 | **15 exactos** (13 predicates + 2 validate) |
| **IDs mutmut** | — (no es conversión) | **129**: predicates 99 + validate 30 |

**Cuatro fuentes con 0 IDs** (classes, payloads, event_catalog, limits: sin
callables; mutmut 3.7 no instrumenta sentencias de módulo). «0 mutantes» NO es
cobertura ni equivalencia. Su tratamiento en §7.

## 3. Selección pertinente (evitando el hueco de L4)

Derivada desde consumidores y obligaciones (auditoría documental independiente
incluida): la cadena predicates → payload_validate → observation_event se
ejercita SOLO en RECONCILE (el decode usa coercers paralelos del wire);
`EVENT_CATALOG` en ambos. Los tres archivos seleccionados son el universo
COMPLETO de tests que importan las 6 fuentes: **schema 124 + observation 302 +
phases 26 = 452 nodeids únicos** (digest
`7a6d337e…` en `custodia/seleccion-L3.nodeids`), colección real 452/452,
baseline ORIGINAL **452 passed, 0 skips/xfails**. Exclusión justificada:
`test_accept_typed_operator.py` (61) ejercita el OPERADOR tipado — su propio
test certifica que NO importa `tools.wct.evidence.*`; incluirlo no puede matar
mutantes L3. Property: los tres archivos no tienen marcas (TEST-008). **Asociaciones**:
cobertura de sentencias Y ramas 100 % sobre predicates+validate con la selección
(logs/07) — 15/15 funciones con tests asociados no vacíos.

## 4. Instrumento, puerta previa y campaña única

Árbol desde `git archive e8d6141`; pyproject original `f27de519…` /
experimental `798883ba…` (source_paths = exactamente las 6 fuentes; selección
452); generación pura con firma admisible (rc=1 por filtro sin coincidencias
tras «done»); stats y copias ejecutadas congeladas (`custodia/instrumentado-L3-*`);
lanzador fail-closed (7 controles; negativos rc=2); **canario acreditado desde
diff real**: `x__clean_string__mutmut_2` (except UnicodeEncodeError: False→True)
con `test_payload_validate_rejects_bad_nested_values` → rc=1 «DID NOT RAISE»
(acepta surrogate; causa prevista). **Puerta previa: APROBADA** por verifier
independiente (1.76 s). Campaña única: `mutmut run --max-children 1 <129 IDs
explícitos>`, sin globs, sin reparaciones, 108.24 s (B 108.24/1800).
Reconciliación: generado == autorizado == resultados == 129; cero
duplicados/ajenos/faltantes; log por-mutante (🎉/🙁) == meta en 129/129.

## 5. Bruto y clasificación causal de los 30 sobrevivientes

**Killed 99** (69 predicates + 30 validate): detección por tests existentes con
causa contractual (muestreo del verifier final: `is_utc_2` y `member_of_3`
matados por `test_abnormal_exit_is_visible_as_cause` con
`invalid_observation: events[0].payload.<campo>`). **Survived 30**, en tres
grupos con evidencia separada:

- **SURVIVED-REPRODUCIDO-EN-SONDA (15)** — sonda fresca con la selección
  completa 452, activación acreditada, rc=0: `clean_string_3/6/8`,
  `is_argv_5`, `is_broad_text_1`, `is_cwd_5/6/11/13`, `is_digest_1`,
  `is_text_6`, `is_u_6`, `is_xfail_3/4/5`. Patrón dominante (coincide con la
  auditoría documental): **lado-rechazo de predicates sin oráculo en toda la
  suite** — la vía decode rechaza antes de construir el payload y no existe
  test de observation MANUAL con: cwd con segmentos `.`/`..`, argv vacío/ítem
  vacío, xfail malformado, fronteras `_within` (0/255/256), `_optional`
  malformado, digest no-hex, broad-text sucio, C0/DEL/espacio exacto en
  payload manual, SEQ_MAX exacto por `_is_u`, vacío por `_is_text`.
- **SURVIVED-EN-CAMPAÑA → KILLED-EN-SONDA (10)**: `member_of_1/2/3/4/5`,
  `optional_1/2/3/4`, `within_1` — rc=1 bajo selección completa (member_of_1/3/4/5:
  270 failed; optional: ~232; within_1: 232; member_of_2: exactamente
  `test_manual_invented_outcome_is_invalid_observation`). **Límite
  instrumental descubierto (narrativa corregida por el verifier final, que
  reejecutó y falsó la primera hipótesis del autor)**: el stats de mutmut
  atribuye EXACTAMENTE 1 test a cada factoría (`x__member_of/_optional/_within`:
  1; vs `x__clean_string`: 274, `x__is_utc`: 269) y la campaña gastó ~0.1 s por
  ellas (durations_by_key) — PERO ese único test atribuido
  (`test_abnormal_exit_is_visible_as_cause`) ES letal en proceso fresco: el
  falso-survived proviene del RUNNER de la campaña, no de una selección
  irrelevante. Mecanismo consistente con la evidencia: `_PAYLOAD_CHECKS` se
  construye EN IMPORT llamando a las factorías; el trampolín intercepta
  LLAMADAS, y en el arnés de mutmut la mutación no se materializa en la tabla
  (proceso/estado de import previo), mientras que en un proceso lanzado con
  `MUTANT_UNDER_TEST` desde el arranque (nuestro lanzador) sí. El bruto NO se
  convirtió: siguen exit 0.
- **SURVIVED-EN-CAMPAÑA sin sonda (5)**: `within_2/3/4/5/6` — misma familia,
  diffs conocidos (`type is int` → `or`, `is not int`, frontera `high`
  exclusiva…), NO reproducidas ni matadas: presupuesto C agotado (587.23/600)
  tras 25 sondas. Estado entregado tal cual.

**Estado del lote: FAIL-SURVIVORS-STOP** — 15 sobrevivientes reproducidos sin
disposición (más 5 sin sonda y 10 falsos del instrumento con estado bruto
conservado). Ningún timeout que adjudicar; la admisión D-C de L4 NO se hereda
(aquí no hay no-terminación). El residuo queda agrupado para adjudicación
futura; nada ratificado.

## 6. Fuentes sin IDs: evidencia reutilizada y huecos (auditoría documental)

- **event_catalog**: cubierto con transcripción independiente
  (`CONTRACT_EVENT_CATALOG`) + derivación/consumo (control D-D de R16) +
  reconcile (`PA12-observation-incoherent`, manual-subclass). Hueco conocido: ninguno.
- **limits**: fronteras reales medidas por conducta (64 KiB ±1, 2 MiB,
  4096 ±1, SEQ_MAX, profundidad 8, C0/DEL/surrogate, digests, utc, aridades 5/3,
  max_bytes, catálogo de findings cerrado). Hueco: sin transcripción literal de
  la tabla (riesgo bajo); los topes 10000/20000 viven en L4 ya controlados.
- **payload_classes**: identidad de clases vía catálogo; PERO sin transcripción
  de campos para 20/21 clases (solo ExecutionStart), ni enums, ni frozen-ness
  de las 21 — análogo al sitio WIRE_FIELDS de L2; pendiente de decisión D-D
  propia de L3.
- **payloads (fachada)**: ejercitada como superficie por los consumidores;
  `__all__` completo y `pp.EVENT_CATALOG` sin aserción (menor).
- **Hueco estructural mayor (auditoría)**: `_PAYLOAD_CHECKS`
  (pytest_payload_validate L49-120) es literal de módulo — NO instrumentable
  por mutmut 3.7 y sin control de transcripción: quitar/intercambiar un check
  de la tabla es invisible para cualquier campaña de este instrumento.

## 7. Gates, presupuestos, incidentes, dictámenes

- **Gates (I 144.42/300)**: sin cambios de tests/producto no se repitieron
  baterías pesadas; `wct gate --tier fast` rc=0; tier commit **20 PASS · 1
  FAIL — G-META-1 recalculado: 36 rutas heredadas** (2 modificadas + 34 nuevas
  protegidas; ninguna del delta; main limpio). Rojo conocido del PR; sin
  bless ni reparación (fuera de allowlist).
- **Presupuestos**: A 51.58/300 · B 108.24/1800 · C **587.23/600** (agotado
  honestamente tras 25 sondas; 1 refused documentado) · V 30.26 en ledgers de
  verifiers (puerta 1.76 + final ~28.5; sobre V del guardián sin uso) ·
  I 144.42/300 · PUB ver §9. **Total ≈ 922 s de 3420.** Intentos inválidos:
  4 arranques del lanzador (ruta de inventario heredada de R16 + rechazo por
  fuentes sin trampolines), todos <0.1 s, documentados; 1 crash del script de
  sondas al agotarse C (log inexistente leído); 1 FileNotFoundError de un
  intento de escritura de resumen que nunca corrió.
- **Incidentes**: la primera hipótesis del autor sobre el límite instrumental
  (test atribuido «irrelevante») fue FALSADA por el verifier final con
  reejecución; la narrativa de §5 es la corregida. El resumen de sondas
  (logs/13) se reconstruyó documentalmente desde los 25 logs existentes.
- **Dictámenes**: auditor documental — selección pertinente y completa, huecos
  de suite PREDICHOS antes de la campaña (§5/§6 los confirma). Puerta previa —
  APROBADA. Verifier final — FAVORABLE con corrección obligatoria aplicada
  (narrativa del límite instrumental) y un matiz de atribución (el killer de
  `is_utc_2` es `test_abnormal_exit`, no el test de valores anidados).

## 8. Estado de lotes (corrección a la propuesta final de R16)

| Lote | Estado |
|---|---|
| L2 | cerrado en su alcance (R10–R11; 266 killed + 12 survived adjudicados) |
| L4 | cerrado por resultado medido y adjudicación explícita (R12–R16; 446+26+1) |
| L1 | pendiente de TEST-007 (partición/decisión humana) |
| **L3** | **medido aquí**: bruto 129 = 99+30, FAIL-SURVIVORS-STOP, límite instrumental documentado |
| L5–L9 | pendientes conforme al plan de R6; el reuso de la evidencia de scan_closers sigue separado y por identidad |
| Binding PA01–PA12 | pausado |

## 9. Custodia y publicación

Manifiesto del expediente con logs cerrados; digest y verificación fuera de
sus miembros; estados inicial/final separados; hooks, publicación y CI en
archivos externos al sello. Hooks instalados y verificados ANTES del commit;
staging por la única ruta autorizada; conventional commit con byline; push
normal; **PR #56 permanece en borrador**. La publicación documental procede
con dictamen favorable AUNQUE el lote termina FAIL-SURVIVORS-STOP: ningún
residuo oculto. CI del SHA publicado: los pasos omitidos por integridad son NO
EJECUTADOS; sin pronóstico post-bless.

## 10. Próximo incremento mínimo PROPUESTO (no ejecutado)

> **REANCLAJE-18 — adjudicación L3 y refuerzo acotado.** (1) Decisiones humanas
> por grupo de los 30: (a) 15 reproducidos → hueco-de-oráculo (tests de
> observations MANUALES con lado-rechazo: cwd `.`/`..`, argv vacío, xfail
> malformado, fronteras 0/255/256, `_optional`, digest no-hex, broad-text,
> C0/DEL/espacio, SEQ_MAX, vacío) o equivalencia propuesta, por ID con diff;
> (b) 10 falsos del runner → re-clasificar con la sonda como evidencia y decidir
> el tratamiento del límite del arnés (documentar, no convertir bruto);
> (c) 5 within sin sonda → completar sondas. (2) Decisión D-D L3:
> transcripción de `_PAYLOAD_CHECKS`, campos/enums/frozen de payload_classes
> (20/21), `__all__` de la fachada. (3) Solo tras (1)–(2): eventual re-campaña
> L3 con selection íntegra por mutante (el límite del runner exige sondas
> completas o arnés alternativo), autorizada una sola vez. Allowlist propuesta:
> tests/unit/test_pytest_schema.py + docs. NO ejecutar sin encargo.
