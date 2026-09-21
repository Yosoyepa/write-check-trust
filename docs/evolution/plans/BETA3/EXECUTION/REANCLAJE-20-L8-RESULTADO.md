# Registro REANCLAJE-20 — primera calificación L8 con activación fiel y precisiones de cierre de R19 (2026-09-19)

Estado: **primera campaña L8 ejecutada y reconciliada: 398 = 359 killed +
39 survived, FAIL-SURVIVORS-STOP con los 39 reproducidos en sonda fresca y
adjudicados por grupo con diff.** Sin ratificaciones, sin reparaciones, sin
segunda campaña. En el mismo registro: la precisión de R19 — transferencia
X→Y confirmada por revisión independiente y contabilidad de suite corregida
(suite completa 1337 vs normativa 1336 vs G-TEST canónico). R19 no se
reescribe ni se recampaña.

## 1. Base, identidades y aislamiento

Cabeza comunicada `87a4af7daf2a6b1cf98490b4dd415155adb546f7` == remoto ==
headRefOid PR #56 (borrador, OPEN); commit técnico de R19
`2737fffca1e97c8d2d9c8a85936cb132b96b84fc`; main de referencia
`8a379d64…` = merge-base; tag `v1.0.0b3.dev1` intacto. Sin avance desde la
publicación de R19. Expediente aislado `build/tmp/reanclaje20-20260919/`
(guardián propio, sobres §12); copia de trabajo `build/tmp/reanclaje20/`
(clon local con raíz Git propia); checkout principal y expedientes
históricos preservados (verificado por el verifier de puerta previa).
Runtime: Python 3.13.14, pytest 9.1.1, mutmut 3.7.0; imports resueltos
dentro de la copia por sonda del lanzador.

## 2. Precisión de R19 (nota sucesora, sin recampaña)

**Transferencia X→Y — CONFIRMADA por auditoría independiente** (aceptación
puntual del humano, encargo §2):

- X medido `89988f7aa1ac37a7…a92c1` (== sellos R19 == run/mutants) y Y
  publicado `3ee6c0d74ff84dfc…e13` (== commit 2737fff), recalculados por el
  auditor desde el commit.
- Diff completo: exactamente 2 funciones, 13+4 = 17 líneas; 107/109
  enunciados de nivel superior byte-idénticos, 0 añadidos/eliminados.
- Oráculos detectores: las funciones `test_manual_payload_*` y SUS tablas
  de parametrización (`_VALID/_INVALID/CONTRACT_*`) son byte-idénticas; los
  129 primeros fallos del ledger viven en funciones byte-idénticas.
- Mecanismos conservados (no basta «cero mutantes en fuentes consultadas»):
  imports idénticos posición a posición, 0 fixtures, inventario de nombres
  de nivel superior idéntico, SUT byte-idéntico al sellado, selección 580 ⊆
  colección bajo Y (252==252 en schema) y los 16 nodeids oráculo presentes.
  Entre X e Y no cambia qué tests existen, ni cómo se parametrizan, ni qué
  datos consumen, ni contra qué SUT corren.
- Alcance de la revisión previa (R19) documentado: cubrió bruto/transición/
  hashes/diff-2-funciones/sellos; NO cubrió explícitamente la cabecera de
  imports ni las tablas de parametrización como tal — esta auditoría los
  cerró.
- Contabilidad separada: **129/129 MEDIDO sobre X**; vigencia sobre Y por
  transferencia confirmada; **desviación de la secuencia de congelación
  declarada** (edición post-campaña puntual; NO autoriza futuras ediciones
  post-campaña ni convierte la secuencia histórica en conforme).

**Contabilidad de suite de R19 (corrección narrativa):** la corrida I10 fue
la suite COMPLETA sin filtro (`pytest -q`): **1337 passed = 1325 unit +
10 integration + 1 property + 1 acceptance**. La **normativa excluyendo
property es 1336**. La ejecución canónica de G-TEST es
`pytest -q tests/unit tests/integration -m "not property"` (unit+integration,
sin acceptance ni property; PASS en el tier commit de R19 y de R20). El
registro R19 llamó «suite normativa completa» a la corrida completa: se
corrige aquí; sin invalidante técnico.

## 3. Alcance, inventario e instrumentalización L8

Las 4 fuentes autorizadas, hashes congelados en sellos-R20.json. Referencia
R6 REVALIDADA con el motor canónico del candidato: **213 sitios**
(31+92+45+45) y **15 callables** (ObservationError.__init__ + 4 builders +
2 schema + 8 inventory). Generación pura en copia nueva (rc=1 «nothing
matches» tras «done», 4 files mutated, cero mutantes ejecutados, snapshot de
stats, pyproject desechable con preimagen y delta). **Inventario: 398 IDs**
(builders 170 — solo las 4 funciones nombradas; schema 75; inventory 153).

Limitaciones de instrumentación (documentadas, no cobertura):
- **pytest_types: 0 IDs** — `ObservationError.__init__` (dunder) no
  instrumentable por mutmut 3.7; las 9 dataclasses son generadas. Su
  conducta observable (code/field, excepción normal) ya está controlada por
  tests existentes (§11).
- **Las 17 lambdas de `_BUILDERS` no reciben trampolines** (mutmut no
  instrumenta lambdas en literales de diccionario de módulo). Sin factorías
  llamadas en import: la tabla guarda REFERENCIAS a las 4 funciones
  trampolín — control A07: la referencia ALMACENADA despacha la variante
  (bajo `x__build_execution_start__mutmut_2` devuelve argv=None; bajo
  original, la tupla).

## 4. Selección, baseline, activación y puerta previa

Selección derivada por consumidores reales: los 3 archivos L3 — cadena
`decode_pytest_journal → decode_journal → _BUILDERS` (builders/schema),
reconcile → `pytest_inventory`, types en todos — **580 nodeids** únicos
(digest congelado; colección real; 0 duplicados; sin property conforme
TEST-008). `test_mutation_scan.py` excluido POR DERIVACIÓN (no importa
evidence), no por assert arquitectónico. Baseline ORIGINAL vía lanzador:
580 passed, 0 skips/xfails, 13.75 s. Negativos 5/5 rc=2 (id ajeno, selección
vacía, activación ausente, identidad incorrecta, tests desactualizados).

Política de campaña congelada ANTES de la puerta: 398 × ~15 s ≈ 6000 s no
cabía en B=3600; se fijó **selección completa + `-x`** (semántica de
veredicto por identidad: exit 0 ⇔ los 580 pasaron ⇔ SURVIVED; exit 1 ⇔
primer fallo ⇔ KILLED; timeout 180 s no es killed). Sin recorte de tests.
Calibración: rápida 2.02 s, costosa 5.52 s, cota 13.75 s.

Puerta previa: dictamen inicial DESFAVORABLE con UNA corrección exacta
(C1: los rc=1 por error de COLECCIÓN — sin líneas FAILED — deben contar
como KILLED con diagnóstico separado, no INSTRUMENTAL), aplicada al driver
antes de la campaña y confirmada **FAVORABLE** por verificador distinto.
Sondas del verifier (V): decode_journal_1 rc=1 por error de colección
(motivó C1), identity_comparisons_1 rc=1, ORIGINAL focal rc=0.

## 5. Única campaña y bruto reconciliado

Serial, 398 IDs explícitos, un intérprete nuevo por ID vía lanzador
fail-closed (MUTANT_UNDER_TEST desde el arranque), selección congelada, sin
reparaciones ni resultados heredados. NO es «mutmut run». Reconciliación:
generado == autorizado == ejecutado == resultados == 398; cero
duplicados/ajenos/faltantes; `LANZADOR-OK` en 398/398.

**Bruto: 398 = 359 KILLED + 39 SURVIVED** (2467.8 s de 3600; timeout 0;
instrumental 0). Detecciones: **228 por fallo de test** (primer fallo con
causa contractual) y **131 por error de colección** — cada uno con
diagnóstico separado (§10): el error de colección ocurre bajo el mutante
activo (p. ej. `TypeError: ChannelEnd.__init__…`, `KeyError: 'XXeofXX'`
desde los builders mutados) mientras el ORIGINAL coleciona limpio (baseline
y negativos); los fallos del instrumento quedan filtrados a rc=2 por el
lanzador. Ningún error instrumental convertido en detección sin diagnóstico.

## 6. Adjudicación de los 39 supervivientes (todos reproducidos)

Sondas frescas en C con selección COMPLETA sin `-x`: **39/39
SURVIVED-REPRODUCIDO** (580 passed en cada sonda). Agrupación descriptiva
(sin ratificar):

| Grupo | IDs | Lectura |
|---|---|---|
| Equivalencia propuesta | 8 (`build_execution_start` 1/7/8/9/19/35/36/37) | placeholders de role/digests (""→None/"XXXX") sobrescritos SIEMPRE por `replace()` del decoder desde la cabecera (§3: se reconstruyen inequívocamente); conducta observable idéntica |
| Hueco de oráculo: frontera de cabecera | 5 (`_consume_header` 10/13/14/15/16) | cabecera sin LF con JSON completo (unterminated) y longitud exacta de 64KiB±1 no ejercitadas a nivel cabecera |
| Hueco de oráculo: atribución de findings | 22 (inventory: `_finding` 2/3, `_deselection_rule` 8/9/20/21/32/33, `_deselection_findings` 3/13, `_duplicate_findings` 4/5, `_missing_findings` 2/3, `property_findings` 9/21/22/23/32, `selection_findings` 3/7/8) | execution_id/nodeid/offset exactos de findings property/selection y el multiconjunto de deselección no aseverados por caso en journals con ambas ejecuciones |
| Hueco de oráculo: fronteras del builder | 4 (`build_execution_end` 31/32/46/47) | exit_code −256/−255/255/256 y signal 1/2/64/65 sin journals discriminantes por la vía decode |

**Estado del lote: FAIL-SURVIVORS-STOP** — 39 supervivientes reproducidos
sin disposición (la reparación de oráculos requiere tests nuevos: fuera de
este encargo). Nada ratificado; propuesta en §9.

## 7. Código de módulo sin IDs (§11)

- **types (0 IDs)**: obligación §2 (frozen + orden normativo de campos de
  los 9 tipos de valor; ObservationError excepción normal con code/field).
  Evidencia existente: `test_value_types_are_frozen_with_normative_fields`,
  `test_frozen_is_behavioral_on_a_real_value`,
  `test_observation_error_is_plain_exception_with_code_and_field`. Cambios
  plausibles que distinguiría: campos/orden/frozen/conducta del error.
  Hueco: el dunder `__init__` no es medible por mutación; su conducta sí
  está observada. Limitación documentada, no conformidad por «0 IDs».
- **builders — 17 lambdas**: obligación §3 (conversión por clase). Evidencia
  existente: conducta observada transitivamente por los tests decode (los
  mismos coercers _s/_u/_b/_enum/_int_in están medidos en L2 y en las 4
  funciones nombradas de este lote). Hueco: sin IDs no hay medición mutante
  de las lambdas — limitación instrumental; propuesta (NO implementada):
  eventual matriz por builder bajo decisión D-D.
- **schema — fachada**: `__all__` sin contrato de inventario literal (como
  la fachada de payloads en R19); la reexportación relevante
  (EVENT_CATALOG) ya está transcrita. `decode_journal`/`_consume_header`
  SÍ medidos (75 IDs).
- **inventory — tablas PROPERTY_FINDING_CODES/NON_BLOCKING_CODES y
  ExecutionInventory**: catálogo §7 l.475-476 con cobertura solo conductual
  (los códigos se emiten y ordenan); sin transcripción literal — hueco
  menor, propuesta D-D no implementada. ExecutionInventory es tipo interno
  de construcción, sin contrato directo en §2.

## 8. Gates, presupuestos, incidentes y dictámenes

- Gates (I): **fast 7/7 PASS**; commit **20 PASS · 1 FAIL — G-META-1**
  (`governance/lint/vulture_whitelist.py` como primer hallazgo, 254 hallazgos
  del gate; rojo conocido del PR por drift de integridad de rutas protegidas
  — referencia, no cifra impuesta; sin rojos nuevos: este encargo no toca
  producto ni tests). **G-TEST PASS** con su selección canónica
  (`tests/unit tests/integration -m "not property"`), registrada. Sin
  baterías pesadas por rutina (sin cambios permanentes de código).
- Presupuestos: A 101.05/300 · B 2467.76/3600 · C 650.54/900 · V 9.5/300 ·
  I 180.71/300 · PUB §13. Total ≈ 3410 de 5580. Incidentes: 3 sondas del
  verifier ejecutadas fuera del guardián y recargadas a V (9.5 s,
  declaradas); 1 arranque de script con cwd erróneo fallido antes de
  ejecutar nada; el dictamen condicional de puerta previa exigió la
  corrección C1 del driver ANTES de la campaña (aplicada y confirmada por
  verificador distinto).
- Dictámenes: auditor X→Y (transferencia CONFIRMADA) · puerta previa
  (DESFAVORABLE→C1→FAVORABLE confirmada) · verifier final (en el
  expediente).

## 9. Custodia y próximo incremento PROPUESTO (no ejecutado)

Expediente con identidades, precisión X→Y, inventario/métricas, selección,
generación/activación, ledger por ID, causalidad, límites instrumentales,
dictámenes y presupuestos; logs cerrados antes del manifiesto; digest fuera
de sus miembros; publicación/hooks/CI en sello sucesor; históricos intactos.
Publicación documental autorizada con dictamen favorable aunque el lote
termine FAIL-SURVIVORS-STOP (estado real explícito). PR #56 en borrador.

Próximo mínimo propuesto (NO ejecutado): **REANCLAJE-21 — reparación acotada
L8**: oráculos para los 31 de hueco (fronteras de cabecera 64KiB/sin-LF,
atribución execution_id/nodeid/offset por caso, fronteras exit/signal del
builder) y decisión humana sobre los 8 de equivalencia propuesta
(placeholders) y sobre la matriz de las 17 lambdas; tras ello, única
recampaña. Allowlist propuesta: tests/unit/test_pytest_schema.py +
tests/unit/test_pytest_observation.py + docs. L1 sigue pendiente de
TEST-007; L5–L7 y L9 conservan sus encargos; binding PA01–PA12 pausado. Sin
aceptación mutada, calificación integral, bless, merge ni release.
