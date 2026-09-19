# Registro REANCLAJE-6 — plan de calificación exacta del PR #56 (2026-09-18)

Estado: **plan ejecutable, acotado y verificable** para calificar P03a/R8 y el
operador tipado fase 1 sobre el candidato actual. Solo inspección, inventarios
y comprobaciones de preparación; sin campañas, sin generación de mutantes, sin
binding, sin cambios de producto/tests/gobernanza. Base verificada:
`4974e6a9138486b5ac45641bcc6fda5e7129f3af` (= HEAD de la copia = origin
`codex/reanclaje-p03a-fase1` = headRefOid PR #56; baseRefOid = merge-base =
main `8a379d64…` = tag `v1.0.0b3.dev1`; PR en borrador). Delta remoto
registrado: nueva rama `origin/fix/redteam-productive` (histórica, no toca
esta rama ni main) — no material para el corte. Expediente R5 verificado
antes de reusar evidencia: digest comunicado
`9564d3e19ca627bf6b03eea35946f3c3f46e9b92ddb8a61ac1b43c3d58afbf7b` = sha256
de `MANIFIESTO-REANCLAJE5.sha256`, 33/33 miembros OK. Copia aislada:
`build/tmp/reanclaje6-20260918/repo` (raíz Git propia; venv propio
`uv sync --all-groups`, sin tocar runtimes ajenos).

Runtime de las comprobaciones de preparación: Python 3.13.14, pytest 9.1.1,
vulture 2.16, ruff 0.16.4, mypy 2.3.1, **mutmut 3.7.0 (solo inspección de
versión; ni generación ni ejecución)**, wct 1.0.0b3.dev1 editable resolviendo
dentro de la copia. Colección fresca **1183** (2,6 s); focales por archivo:
test_pytest_observation **302**, test_pytest_schema **98**,
test_pytest_phases **26** (R8 = 426), test_accept_typed_operator **61**;
155 nodeids case-ID `test_observation_case[PA…]` (PA01 5, PA02 8, PA03 20,
PA04 16, PA05 13, PA06 9, PA07 8, PA08 19, PA09 13, PA10 13, PA11 6, PA12
25). `tests/conftest.py` inspeccionado: la colección no ejecuta campañas
(aislamiento Git de fixtures, sin efectos laterales). fast 7/7 (5,4 s) sobre
la copia antes de este registro.

## 1. Inventario real del incremento (diff contra merge-base 8a379d6)

49 rutas (`git diff --name-status 8a379d6..4974e6a`), clasificación:

| Clase | # | Rutas |
|---|---:|---|
| **A. Fuentes productivas nuevas** | 34 | 33 × `tools/wct/evidence/pytest_*.py` + `tools/wct/accept/mutation_policy.py` |
| **B. Fuentes productivas modificadas** | 1 | `tools/wct/accept/mutation_cases.py` |
| **C. Tests** | 6 | `tests/acceptance/steps.py` (M, guard operador), `typed_operator_steps.py`, `tests/unit/test_accept_typed_operator.py`, `test_pytest_{observation,schema,phases}.py` |
| **D. Features/contratos ejecutables** | 2 | `wct-pytest-observation-001.feature` (12 filas PA01–PA12), `wct-typed-mutation-001.feature` |
| **E. Configuración protegida** | 1 | `governance/lint/vulture_whitelist.py` (M; análisis, NO objetivo ordinario de mutación) |
| **F. Documentación** | 5 | registros REANCLAJE-1…5 |
| **G. Ajenos al incremento** | 0 | — |

Las 43 rutas incorporadas por REANCLAJE-1 **no son 43 archivos de producto**:
son 35 fuentes (34 A + 1 B) + 6 tests + 2 features. La whitelist (E) y los
docs (F) se incorporaron después (R3/R5).

### 1.1 Cambios sucesores separados de la incorporación original

| Cambio | Ruta(s) | Encargo | Naturaleza |
|---|---|---|---|
| Incorporación original (43 rutas, hashes en REGISTRO-REANCLAJE-1 §4) | A/B/C/D | REANCLAJE-1 | bytes sellados R8 `93acd1a5…` / fase 1 `c23d7273…` |
| Eliminación `InstanceReport` | `pytest_phases.py` | R3 | − clase muerta; 36844347→ea95730c |
| Reparación test O6 | `test_accept_typed_operator.py` | R2 | +oráculo runtime sobre SUT; 44ba0597→655c78fa |
| Eliminación `_ScanState.expectation` | `pytest_scan_state.py`, `pytest_observation.py` | R5 | − campo muerto + kwarg; dbbbef52→0c995e77, 3ec593ba→46309fc8 |
| Whitelist ratificada +3 | `vulture_whitelist.py` | R5 | 8c2f819b→a2877ee8 (20 entradas REANCLAJE + 7 ADR-D-02) |

### 1.2 Inventario AST de las 35 fuentes productivas

Método: motor WCT (`tools/wct/mutate/engine.py`: `mutation_sites`,
`function_sites`, `function_hashes`) + pasada AST independiente (defs,
métodos, defs anidadas, decoradores, constantes de módulo, imports internos,
consumidores reversos). Detalle completo por función:
`build/tmp/reanclaje6-20260918/logs/30-inventario-ast.json` (expediente).
**Sitios WCT** = nodos AST mutables (BoolOp/BinOp/UnaryOp/Compare/If/IfExp/
While/Constant ≠ None/Ellipsis — `MUTABLE_NODES` del motor) por función
interna — es la métrica de planeación del propio WCT, **no** un conteo de
mutantes mutmut.

| Archivo | Sitios WCT | Callables | LOC | Importadores (consumidores en el repo) |
|---|---:|---:|---:|---|
| pytest_api_args.py | 84 | 9 | 85 | observation_validate |
| pytest_builders.py | 92 | 4 | 137 | observation_events |
| pytest_decode_events.py | 94 | 10 | 147 | observation_events |
| pytest_decode_header.py | 72 | 7 | 76 | observation_events |
| pytest_disposition.py | 75 | 7 | 92 | phases |
| pytest_event_catalog.py | 43 | 0 | 49 | decode_events, event_catalog consumers |
| pytest_inventory.py | 45 | 8 | 122 | observation_inventory |
| pytest_limits.py | 41 | 0 | 35 | observation_validate |
| pytest_observation.py | 88 | 15 | 213 | tests R8, typed_operator_steps (vía API pública) |
| pytest_observation_event.py | 81 | 6 | 59 | observation_events |
| pytest_observation_events.py | 82 | 6 | 83 | observation |
| pytest_observation_inventory.py | 24 | 1 | 23 | observation |
| pytest_observation_validate.py | 96 | 8 | 82 | observation |
| pytest_payload_classes.py | 74 | 0 | 147 | validate, builders, scan_* |
| pytest_payload_predicates.py | 61 | 13 | 61 | payload_validate |
| pytest_payload_validate.py | 87 | 2 | 135 | observation_events |
| pytest_payloads.py | 31 | 0 | 69 | varios (union de payloads) |
| pytest_phase_pairs.py | 74 | 8 | 101 | phases, scan_tests |
| pytest_phases.py | 41 | 5 | 106 | observation (composition) |
| pytest_scan_closers.py | 29 | 5 | 43 | dispatch |
| pytest_scan_dispatch.py | 78 | 8 | 133 | observation |
| pytest_scan_open.py | 33 | 11 | 86 | dispatch |
| pytest_scan_state.py | 65 | 2 | 85 | todos los scan_*, observation |
| pytest_scan_tests.py | 69 | 15 | 136 | dispatch |
| pytest_scan_totals.py | 60 | 7 | 72 | observation |
| pytest_schema.py | 45 | 2 | 73 | observation |
| pytest_sequence.py | 81 | 6 | 91 | decode_events, dispatch |
| pytest_termination.py | 72 | 10 | 77 | dispatch |
| pytest_types.py | 31 | 1 | 116 | observation, types consumers |
| pytest_wire_composites.py | 46 | 5 | 42 | decode_events |
| pytest_wire_fields.py | 60 | 0 | 69 | decode_events |
| pytest_wire_framing.py | 65 | 9 | 116 | decode_header |
| pytest_wire_values.py | 49 | 9 | 43 | wire_fields, decode |
| mutation_policy.py | 161 | 10 | 160 | mutation_cases, typed_operator_steps, tests |
| mutation_cases.py (M) | 46 | 4 | 53 | campaign, verdict, pipeline (AC1) |
| **Total** | **2275** | **213** | — | 218 hashes de función WCT |

Constantes de módulo relevantes (código de módulo exigible):
`_SESSION_SCOPED`, `_TAILLESS_DEFECTS`, `_SESSION_ALTERNATIVES`,
`_TEST_PHASE_KINDS`, `_PRE_CHANNEL_CLOSERS`, `_COLLECTION_KINDS`
(scan_state); catálogos de eventos/defectos (event_catalog, limits); tablas
de campos wire (wire_fields/composites); `P03A_*` no existe aún (fase 2).

**Hallazgo material de preparación (G-MUT-SITES)**: el gate está cableado
con `scope=("src",)` (`tools/wct/gate/runner.py:163`) y
`paths.source: [src]` (policy.yaml) — **no mide tools/wct**. En el scope del
PR, `mutation_policy.py` tiene **161 sitios WCT > 100**
(`mutation.max_sites_per_file`). Por TEXTO de TEST-007 («si un archivo
fuente cambiado tiene más de 100 sitios de mutación, pártelo preservando
comportamiento antes de entregar»), el operador exige decisión humana ANTES
de su lote: partición fachada (re-sello sucesor del c23d7273) o excepción
documentada. Ninguna otra fuente supera 100 (máx: observation_validate 96).
Nota: no confundir con los «41 sitios de decisión AST» de REANCLAJE-1 §8 —
esa es la métrica CC/estilos, distinta de los sitios WCT.

## 2. Mapa de vigencia de evidencia histórica

| Pieza | Candidato/hash histórico | Hash actual (4974e6a) | Alcance medido | Reutilizable | Invalidantes comprobados | Re-medir |
|---|---|---|---|---|---|---|
| Sello R8 (37 rutas) | manifiesto `93acd1a5…` sobre snapshot R8 | 34/37 idénticas; 3 divergen (phases R3, scan_state+observation R5) | procedencia de bytes | sí, por ruta idéntica | divergencias exactamente las 3 documentadas (verificado R5 §7 y hoy) | nada, mientras hashes no cambien |
| Sello fase 1 (6 rutas producto de `c23d7273…`) | manifiesto fase 1 | 5/6 idénticas; diverge test O6 (R2) | procedencia | sí, por ruta | O6 documentada | nada |
| Focales R8 426 + operador 61 + AC1 238 | R5 sobre 4974e6a | = base de este encargo | caracterización conductual | **sí — re-medidos frescos hoy** (302/98/26 + 61; AC1 238 en R5) | suite verde con árbol idéntico | batería completa tras CUALQUIER cambio futuro |
| Colección 1183 + nodeids | R3/R5 | idéntica (medida hoy 2,6 s) | integridad de suite | sí | diff vacío vs R5 | tras cambios de tests |
| **Lote de mutación scan_closers** (82 = 78 killed + 4 equiv. adjudicados; oráculos R7→R8) | acta ADJUDICACION-SOBREVIVIENTES-SCAN-CLOSERS + réplicas `p03a-mutcal-4m5r7b`, `p03a-mutbatch2-qfjjc6` sobre bytes R8 | fuente `872f2243…` = sello R8 (**sin cambio**); tests `5d3d30a6…` = sello R8 (**sin cambio**) | módulo pytest_scan_closers.py completo | **sí, por identidad** (fuente+tests byte-idénticos; receta y evidencia custodiadas) | cambio de cuerpo/imports de scan_closers o de sus tests; cambio de instrumento SOLO si se re-ancla | nada si se reusa por identidad; re-anclaje solo por decisión humana |
| Q-ACCMUT 47/47 (motor AC1) | E11+addenda sobre main | main intacto; PR toca `mutation_cases.py`/`steps.py` del camino de campaña (no `process.py`) | campaña de aceptación del motor | condicional | cláusula vigencia nombra `process.py` (sin cambio); ediciones del PR son no-op para IRs sin `mutation_policy` (histórico intacto, REV2 §2) | **repetición fresca recomendada** en la cadena (§6) por honestidad de cadena, no por invalidante probado |
| 928 IDs (OBL-03, PR #53) | ACTA-DECISIONES-FINALES §2.4: 649 `gate.checks` + 279 `selftest.fixtures_tools`, 38 funciones, AST idénticos post-partición | verificado HOY: el diff del PR **no toca** ninguna ruta `tools/wct/gate/checks*` ni `tools/wct/selftest/fixtures*`; ninguno de esos módulos importa los módulos del PR (grep `evidence.|mutation_cases|mutation_policy|typed_operator` = 0) | delimitación FUERA, con fundamento | sí — **sin invalidante** | cambio de cuerpo/resolución/wiring de esas 38 funciones (ninguno) | nada |
| Coverage/CRAP/DRY/full PRE-BLESS históricos (OBL-07..09/11) | main 8a379d6 (scope AC1) | no cubren el scope del PR | motor AC1 | para el motor, sí | no aplican a P03a/operador | TODO el scope del PR es nuevo para estas puertas |

**No existe** campaña de mutación alguna para las otras 33 fuentes R8 ni
para el operador: la adopción R1 §2.4 lo declara y hoy se confirma (solo
existen `p03a-mutcal-4m5r7b` y `p03a-mutbatch2-qfjjc6`, ambos scan_closers).
Tests verdes NO son prueba de vigencia de campaña; y una campaña válida no
se repite por cambio de SHA documental sin invalidante (scan_closers se
reusa, no se repite).

## 3. Disposición del alcance histórico (928 IDs y demás)

- **928 IDs**: se conserva la disposición humana de PR #53 (ACTA §2.4 /
  OBL-03 «FUERA, CON FUNDAMENTO») — fundamento: delimitación por
  identidad/diff con 38/38 cuerpos AST idénticos. PR #56 **no introduce
  invalidante**: no cambia cuerpos, ni resolución (qualname), ni wiring de
  esas funciones; no altera sus imports ni precondiciones. Los 928 siguen
  NO EJECUTADOS y sin veredicto; no se les atribuye ejecución. Si un encargo
  futuro toca `gate/checks*` o `selftest/fixtures*`, la delimitación se
  revisa antes de reusarla.
- **scan_closers (82 IDs)**: reutilización por identidad citando el acta;
  los 4 equivalentes siguen excluidos del killed SOLO por esa adjudicación.
  Re-anclaje con instrumento actual (mutmut 3.7.0) solo si el humano lo
  pide; la identidad del instrumento del lote histórico consta en sus
  réplicas custodiadas.
- **Q-ACCMUT (47 celdas)**: sin invalidante probado, pero se propone
  repetición fresca en la puerta de aceptación mutada de la cadena (§6)
  porque el PR edita dos módulos del camino de campaña.
- **Brutos históricos AC1** (498/486/497/282/…/74): inmutables; sus
  disposiciones por ID (14 equivalencias, excepción puntual B1–B5+
  terminate__7, 5 sucesoras D-A') NO se reabren: ninguna fuente de esas
  disposiciones cambia en el PR.

## 4. Plan de mutación por lotes (PROPUESTA — no ejecutado)

Principios: un lote = un encargo con copia aislada propia; generación y
ejecución en el mismo proceso acreditado; inventario independiente esperado
= la tabla §1.2 (los `function_sites`/`function_hashes` del JSON del
expediente son el oráculo de conciliación ANTES de ejecutar); receta mutmut
de la calibración histórica (`p03a-mutcal-4m5r7b`): selección por rutas
explícitas, `MUTANT_UNDER_TEST` para sondas causales,Tests del lote como
comando de mutmut; baseline verde del lote obligatoria antes de mutar;
cero mutantes ejecutados si la baseline falla.

Controles comunes por lote (de la calibración y TEST-005/006):
1. selección no vacía: el conteo planificado por mutmut > 0 y concilia con
   los sitios WCT del lote (razón histórica ≈ 2,8 mutantes/sitio —
   **estimación**);
2. identidad de fuente: hash del archivo antes/después de la campaña igual
   al inventario; imports resuelven dentro de la copia (control `__file__`);
3. canario discriminante: un mutante conocido del lote debe morir con el
   test que el propio lote nombra (si el canario sobrevive, el arnés está
   mal cableado — parar, no adjudicar);
4. residuo: cada sobreviviente se adjudica con diff + sonda
   `MUTANT_UNDER_TEST` (nada de exclusión sin acta);
5. custodia: manifiesto SHA-256 de logs/diffs/adjudicaciones en
   `build/tmp/<lote>/`; sin tocar governance ni manifests del repo.

| Lote | Rutas exactas | Sitios WCT | Funciones (callables) | Tests/nodeids (procedencia) | Notas |
|---|---|---:|---:|---|---|
| **L1 — Operador tipado** | mutation_policy.py, mutation_cases.py | 207 | 14 | test_accept_typed_operator (61), AC1 238, feature typed-mutation | **bloqueado por decisión D-1** (TEST-007: mutation_policy 161 > 100) |
| **L2 — Wire puro** | wire_values, wire_fields, wire_composites, wire_framing | 220 | 23 | test_pytest_schema (98) + case-IDs PA02/PA03 (28) | primer lote ejecutable sin decisiones abiertas |
| **L3 — Payloads y catálogo** | payload_classes, payload_predicates, payload_validate, payloads, event_catalog, limits | 337 | 15 | schema (98) + PA03 (20) | payload_classes = dataclasses: esperar alto ratio de equivalentes de anotación; adjudicar con sonda |
| **L4 — Decoder y secuencia** | decode_header, decode_events, sequence | 247 | 23 | PA02/PA03 + schema | frontera decode |
| **L5 — FSM apertura** | scan_state, scan_dispatch, scan_open | 176 | 21 | PA04–PA08 + phases (26) | scan_state ya divergió del sello (R5): sucesor |
| **L6 — FSM eventos y fases** | scan_tests, scan_totals, disposition, phase_pairs, phases | 319 | 42 | PA04/PA05/PA07 + phases | phases = sucesor R3 |
| **L7 — Reconciliación** | observation, observation_event(s), observation_inventory, observation_validate, api_args | 455 | 45 | PA01–PA12 (155) + schema | núcleo; observation = sucesor R5 |
| **L8 — Contratos de tipos** | types, builders, schema, inventory | 213 | 15 | schema (98) + PA01/PA09/PA10 (31) | types = dataclasses del §2; riesgo de equivalentes de anotación |
| **L9 — Cierre** | termination | 72 | 10 | PA08 (19) | scan_closers (29 sitios) queda FUERA de ejecución: reuso por identidad (§2/§3) |

Totales: 2246 sitios a ejecutar + 29 reusados = 2275; 208 callables en
lotes + 5 de scan_closers (reuso) = 213. **Estimaciones**
(rotuladas): ≈6300 mutantes esperados (razón 2,8/sitio, IC amplio);
generación ≤ 120 s/lote; ejecución ≤ 1800 s/lote (cap del instrumento
600 s/campaña → sub-lotes); sondas causales ≤ 300 s/lote; revisión
independiente ≤ 300 s/lote.

**Presupuesto agregado cerrado (techo propuesto)**:
- generación: 9 × ≤120 s = **≤ 1080 s**
- ejecución: 8 lotes ejecutables × ≤1800 s = **≤ 14 400 s** (L9 reuso = 0)
- sondas causales: **≤ 2700 s**
- revisión independiente: **≤ 2700 s**
- **TOTAL: ≤ 20 880 s (~5,8 h)** con parada dura si un lote excede su techo
  (un exceso es un hallazgo de arnés o de selección, no presupuesto extra).
- Orden recomendado: L2 → L4 → L3 → L8 → L5 → L6 → L7 → L9; L1 tras D-1.

## 5. Matriz de aceptación — obligación por componente

| Componente | Obligación | Escenario | Binding | Operador aplicable | Evidencia disponible | Pendiente |
|---|---|---|---|---|---|---|
| **A. Motor AC1** (existente en main) | CONTRATO-AC1; E11: sustentado (fuentes por adjudicación + Q-ACCMUT 47/47 + cobertura/CRAP/DRY + full + POST-BLESS) | `wct-acceptance-evidence-001` (47 celdas) | existente (campaign_steps) | pipeline AC1 sin política | cadena E11 completa sobre main; unidades 238 verdes en el PR | Q-ACCMUT fresco en el candidato final (recomendado); nada más — AC1 **no** es infraestructura a recalificar por P03a |
| **B. Operador tipado fase 1** | REV2 §2 (`load_policy`/`validate_policy` + histórico intacto en `mutations`) | `wct-typed-mutation-001` | **EXISTENTE**: guard en `steps.py:26-28` → `typed_operator_steps` | receta REV2 §5 (activación explícita por IR; sidecar de P03a NO aplica) | 61 unitarios + O6 reforzado + feature parseable (G-ACCEPT PASS) | mutación L1 (tras D-1) + **campaña de aceptación del propio feature** (sus celdas Examples, con el motor AC1) — **calificable POR SEPARADO**, sin dependencia de PA01–PA12 |
| **C. P03a (PA01–PA12)** | PROPUESTA-P03 §9: feature de 12 familias; TEST-010 | `wct-pytest-observation-001` (12 filas + 155 case-IDs unitarios) | **AUSENTE**: sin `steps_p03a.py`, sin guard P03a, sin sidecar, sin `p03a_campaign.py` (fase 2, pausa 2026-09-12 vigente) | tras binding: receta REV2 §5 (12 celdas exactas + 24 rechazos PA99/inventado) | 426 unitarios R8 (caracterización) + 82 IDs scan_closers (parcial, por identidad) | (i) mutación de fuentes L2–L9 **sin** binding; (ii) binding **requiere decisión humana** (levantar pausa); (iii) campaña PA01–PA12 + Q-ACCMUT propio solo tras (ii). **No hay dependencia circular**: unitarios y mutación de fuentes NO requieren binding; el binding no requiere la campaña; la campaña requiere el binding |

Confusiones evitadas por diseño: AC1-calificado ≠ operador calificado ≠ P03a
aceptado; la campaña histórica de 47 celdas es del motor (A), no del
operador (B) ni de P03a (C). La resolución E11 satisface el prerrequisito
sustantivo «AC1 acreditado» de REV2 §6, pero la **pausa de fase 2**
(HANDOFF-AC1-2026-09-12) sigue sin levantarse expresamente — R1 §6 la
formuló y nadie la resolvió.

**Decisión humana exacta requerida (D-2, para PA01–PA12)**: «¿Levanta
expresamente la pausa de fase 2 del binding P03a (2026-09-12) y aprueba el
allowlist REV2 §4 de fase 2 (`steps_p03a.py`, `p03a_journals.py`,
`p03a_campaign.py`, sidecar `wct-pytest-observation-001.mutation.json`,
edición del guard en `steps.py`, `test_accept_steps_p03a.py`,
`test_accept_p03a_campaign.py`) con el contrato REV2 §3/§5 vigente, para un
encargo de implementación separado de toda campaña y de todo bless?». Sin
D-2: P03a se califica en fuentes (L2–L9) y la aceptación queda PENDIENTE;
no se declara calificación integral posible.

## 6. Cadena posterior exigible (PROC-004; nada ejecutado aquí)

| # | Puerta | Receta canónica | Alcance/inputs | Depende de | Éxito | Parar si |
|---|---|---|---|---|---|---|
| 1 | Mutación de fuentes | lotes §4 (mutmut 3.7.0, calibración histórica) | 2246 sitios + reuso closers | D-1 para L1 | 0 sobrevivientes no adjudicados; manifiestos de custodia | canario sobrevive; baseline roja; selección vacía |
| 2 | Disposición de residuos | actas de adjudicación por ID (sondas `MUTANT_UNDER_TEST`) | sobrevivientes de #1 | #1 | cada ID killed/equivalente/excepción con acta | equivalencia sin justificación estructural+empírica |
| 3 | Aceptación mutada aplicable | motor AC1: receta Q-ACCMUT (47 celdas) + feature operador (B) | `wct-acceptance-evidence-001`, `wct-typed-mutation-001` | #1 (L1) para B; nada para A | killed=planned, 0 survived/errors/not_run | baseline falla; política inválida |
| 4 | PA01–PA12 | receta REV2 §5 (12 celdas + 24 rechazos) | feature P03a + sidecar | **D-2 + binding implementado** | planned=12, killed=12, `(failed=False)` | 24 rechazos mal clasificados |
| 5 | Cobertura fresca | `pytest --cov` con rama sobre el delta (G-COV-DIFF) + ratchet total | líneas nuevas del PR | #1–#4 | ≥90 % rama en líneas nuevas; total no baja | rama <90 sin plan |
| 6 | CRAP | `wct crap` focal sobre funciones tocadas + suplementario pertinente | fuentes del PR | #5 | CRAP ≤6 | CRAP>6 por CC (partir) o cobertura (tests) — remedio correcto |
| 7 | DRY | `wct dry` sobre pares del scope | fuentes del PR | #6 | 0 clones nuevos (LEAVE_ALONE de matrices respetado) | clon estructural nuevo |
| 8 | Aleatorización | `pytest -p randomly` (TEST-006) | suite normativa | #5 | verde en orden aleatorio (≥2 semillas) | fallo por estado compartido |
| 9 | full PRE-BLESS | `wct gate --tier full` | repositorio | #1–#8 | único rojo G-META-1 | cualquier otro rojo |
| 10 | Revisión protegida E9 | mecánica EQUIVALENCIAS-SUCESORAS-Y-REVISION-E9 sobre drift 36 rutas | lock + candidato | #9 | dictamen E9 favorable | delta no explicado |
| 11 | Bless humano | `wct integrity bless --reason --approved-by` | lock | #10 | lock nuevo; G-META-1 verde | — |
| 12 | POST-BLESS | `wct gate --tier commit` + CI del SHA | repositorio | #11 | 21/21 verde; CI verde | cualquier rojo |

Nota TEST-004: la cobertura total del repo es ratchet; las líneas NUEVAS
del PR (todo A/B) exigen ≥90 % de rama — hoy no medida para el scope (las
mediciones históricas 314/348 son del motor AC1). El G-MUT por defecto
sobre `src/example` NO califica P03a: su scope es `paths.source=[src]`.

## 7. Decisiones humanas enumeradas

1. **D-1 — TEST-007/mutation_policy (161 sitios)**: partición fachada
   preservando comportamiento (con allowlist y re-sello sucesor del
   c23d7273) O excepción documentada por acta. Bloquea L1.
2. **D-2 — Pausa binding PA01–PA12**: texto exacto en §5. Bloquea la
   aceptación de P03a (no la mutación de fuentes).
3. **D-3 — Reuso scan_closers**: ratificar reuso por identidad (recomendado)
   u ordenar re-anclaje con mutmut 3.7.0.
4. **D-4 — Plan de lotes y presupuesto**: aprobar §4 (o ajustar techo).
5. **D-5 — Q-ACCMUT fresco** en candidato final (recomendado, §6 puerta 3).
6. Posteriores y separadas: E9+bless (D-6), merge de PR #56 (D-7), fase 2
   tras D-2 (D-8), bump/tag/release (D-9).

## 8. Prompt del siguiente incremento

> **PROPUESTO — NO EJECUTAR SIN AUTORIZACIÓN**
>
> **Encargo REANCLAJE-7 — Lote 2 de mutación: wire puro de P03a.**
>
> - **Base exacta**: `4974e6a9138486b5ac45641bcc6fda5e7129f3af`
>   (revalidar remoto y headRefOid de PR #56; parar ante avances).
> - **Objetivo**: mutar `tools/wct/evidence/pytest_wire_values.py`,
>   `pytest_wire_fields.py`, `pytest_wire_composites.py`,
>   `pytest_wire_framing.py` (220 sitios WCT, 23 callables) con receta de
>   calibración (`p03a-mutcal-4m5r7b`): copia aislada, venv propio
>   `uv sync --all-groups` (mutmut 3.7.0), baseline verde de
>   `tests/unit/test_pytest_schema.py` + case-IDs PA02/PA03, generación y
>   ejecución en el mismo proceso, conciliación previa contra
>   `function_sites`/`function_hashes` del inventario REANCLAJE-6 (JSON del
>   expediente), canario discriminante, sondas `MUTANT_UNDER_TEST` para
>   sobrevivientes, manifiesto SHA-256 de custodia en `build/tmp/`.
> - **Cambio de producto**: NINGUNO. Solo evidencia bajo build/tmp y un
>   registro documental. Tests nuevos SOLO como oráculos de sobrevivientes
>   (TDD: rojo bajo `MUTANT_UNDER_TEST`, verde sin él), en rutas ya
>   aprobadas.
> - **Presupuesto**: 2520 s (generación ≤120, ejecución ≤1800, sondas ≤300,
>   revisión ≤300); parada dura al exceder.
> - **Criterios de parada**: entregar con 0 sobrevivientes no adjudicados;
>   parar ante canario sobreviviente, baseline roja o selección vacía
>   (hallazgo, no bug del arnés).
> - **Prohibido**: tocar governance, manifests del repo, producto, features;
>   otros lotes; Q-ACCMUT; bless.

Elección: L2 es el primer incremento completable y revisable sin mezclar
implementación (no requiere cambios de producto), campañas de aceptación ni
bless; no depende de D-1/D-2. L1 queda tras D-1 por el PARTITION de
mutation_policy; la aceptación (B/C) va en encargos propios.

## 9. Comprobaciones ejecutadas en este encargo (presupuesto)

≈50 s de 300 s: verificaciones de identidad y digest (§0), colección 1183 y
conteos por archivo, inventario AST (motor WCT + pasada propia), greps de
invalidantes 928/Q-ACCMUT, inspección conftest, fast 7/7 (5,4 s, presupuesto
de publicación). Revisión documental aparte (R1–R5, contratos, actas).
Prohibido y no ejecutado: generación/ejecución de mutantes, Q-ACCMUT,
suites pesadas, implementación, instalación en runtimes compartidos.

## 10. Dictamen del verifier independiente

**FAVORABLE** (agente distinto del autor, solo lectura; reejecutó diff de
rutas, `mutation_sites` del motor sobre las 35 fuentes, hashes contra sellos
R8/fase-1/R5, greps de invalidantes 928, estado real de bindings/features,
colección/focales/distribución PA y aritmética de lotes y presupuesto).
Confirmó: clasificación 49 rutas 100 %; 2275 sitios exactos y el hallazgo
G-MUT-SITES scope=src con mutation_policy 161>100; 928 IDs sin invalidante y
sin atribución de veredicto; reuso scan_closers por identidad byte-exacta
(fuente y tests = sello R8) con acta y autorización citadas; binding del
operador presente (steps.py:26–28) y binding P03a ausente (sin steps_p03a/
p03a_journals/p03a_campaign/sidecar) con pausa vigente; feature P03a = 12
filas PA01–PA12; generado = 1 test; sin claims de aceptación no sustentados
ni PASS anticipados; estimaciones rotuladas (razón 2,8/sitio = 82/29
histórica); lotes/presupuesto/cadena conciliados; §8 rotulado PROPUESTO con
bloqueo explícito de L1 por D-1. Dos hallazgos menores NO bloqueantes,
ambos incorporados antes de publicar: (1) columna callables de §4 no
conciliaba en L6/L7/L8 (corregida: 42/45/15; total lotes 208 + 5 reuso =
213; la métrica load-bearing —sitios— siempre concilió); (2) la descripción
de la métrica omitía `ast.Compare` en `MUTABLE_NODES` (corregida en §1.2).
El candidato permaneció intacto durante la revisión.
