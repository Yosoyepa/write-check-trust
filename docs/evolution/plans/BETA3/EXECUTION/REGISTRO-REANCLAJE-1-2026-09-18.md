# Registro REANCLAJE-1 — adopción de P03a/R8 y operador tipado fase 1 (2026-09-18)

Estado: registro de un incremento de **adopción prospectiva** sobre
`8a379d64ba13bbe43a707fcfd8df0ea336dd97ed` (= origin/main = tag
`v1.0.0b3.dev1`). No es calificación, no ciere P03a ni beta.3, no autoriza
fase 2, campañas, bless, merge, bump, tag ni release.

## 1. Autorización transcrita (2026-09-18)

Autorización humana recibida en este turno, transcrita en lo esencial:

> «Autorizo prospectivamente: adoptar la implementación existente de REV2
> fase 1 y sus contratos/Gherkin, exclusivamente en el alcance identificado
> por el expediente de reanclaje; incorporar las 43 rutas verificadas: 37 de
> R8 y 6 del operador fase 1; ejecutar la verificación acotada descrita;
> commit/push con hooks y abrir una PR en borrador. Esta autorización NO
> convierte en aprobado retroactivamente el trabajo histórico: conserva la
> laguna de aprobación REV2 como desviación de proceso. No autoriza binding
> PA01–PA12, campañas de mutación, Q-ACCMUT, cambios funcionales
> adicionales, bless, merge, bump, tag ni release. No modificar
> v1.0.0b3.dev1.»

Rutas documentales autorizadas: este registro y únicamente las filas
pertinentes de la matriz vigente. **Ninguna fila de
`MATRIZ-DECISIONES-AC1-PENDIENTES-2026-09-13.md` cambia de estado por este
incremento** (no toca decisiones AC1); no se edita la matriz.

## 2. Adopción actual vs. desviación histórica

**Adoptado ahora (prospectivo):** los bytes sellados de R8 (37 rutas) y de la
fase 1 del operador (6 rutas: 4 nuevas + 2 ediciones), incorporados por copia
verificada por hash, sin cambios funcionales. La verificación de esta rama
acredita el compuesto, no una calificación integral.

**Desviaciones históricas conservadas (no saneadas por esta adopción):**

1. **Laguna de aprobación REV2**: su ESTADO.md
   (`8e26ce874ba6e5c4eb055433dbc125e9a7f5f5dcc269ab04f8afd630c8323875`)
   entregó el contrato «pendiente de aprobación explícita»; no se localizó
   registro posterior que apruebe el CONTRATO REV2 (`48e6940e7b4897d11508928ef9cfa7ab78eac579e130c186da753f84a96019c6`).
   La fase 1 se implementó y selló de facto (sello c23d7273…). Esta
   autorización cubre la **adopción**, no la aprobación retroactiva.
2. La calificación AC1 excluyó expresamente la fase 1
   (`MANIFIESTO-AC1-R2-REANUDACION-2026-09-13.json`: out-of-scope, 23/23).
3. TDD/MIN-006 históricos del expediente P03a quedan como deuda de proceso
   registrada; esta adopción no reconstruye evidencia de ejecución previa.
4. La mutación del scope incorporado (R8 + operador) **no está ejecutada ni
   acreditada** por este incremento.

## 3. Base, identidades y composición

- Base: `8a379d64ba13bbe43a707fcfd8df0ea336dd97ed` (remoto verificado sin
  avance; tag `v1.0.0b3.dev1` intacto). Worktree exclusivo
  `build/tmp/reanclaje1-20260918`, rama `codex/reanclaje-p03a-fase1`.
- Composición verificada: 37 (R8) + 6 (fase 1) = 43 rutas; intersección
  vacía; sin duplicados. Estado resultante: 41 sin seguimiento + 2
  modificadas.
- Preimágenes de las 2 modificadas (verificadas antes de escribir):
  `tools/wct/accept/mutation_cases.py` =
  `a4528b8e764501a6af86d87aef7ab48d570e2f7cb33ae413fd40d2576ff64b75`;
  `tests/acceptance/steps.py` =
  `5b6863ede4090feb8b2221ecd976efe81a62e8480bff74f2efb391add25852e1`.
  Ambas eran los bytes vigentes en la base.
- Sellos verificados antes de copiar (digestes completos):
  R8 `candidate-r8.sha256` =
  `93acd1a5b49fdc06ba2cfa5139fcfe329e5748eb4f7eb613833e8a99bc3c7c8a`;
  fase 1 `phase1-artifacts.sha256` =
  `c23d72736448ea5c3e97bb732d5a47bd4664cea2587bb38983a1913cc0bea20e`.
  Expediente de reanclaje (antecedente):
  `MANIFIESTO-EXPEDIENTE.sha256` =
  `a8312f656f42c56d8573e7dd4e6aaa64f0357ea56fcf45f6ed932ad995b5c069`.

## 4. Las 43 rutas incorporadas y sus identidades

| Ruta | Origen | SHA-256 |
|---|---|---|
| `features/wct-pytest-observation-001.feature` | R8 (sello 93acd1a5…) | `3d957b13ea6a2d1d40cdb8d600467c23420a2c3c781d36b6c0808be9ee26df2d` |
| `features/wct-typed-mutation-001.feature` | fase 1 operador (sello c23d7273…) | `ebf0a0f6e7958e39d0d067ad63a8237f02a05912f37fc14c52d2f912aae4ebff` |
| `tests/acceptance/steps.py` | fase 1 operador (sello c23d7273…) | `86bdd5ebfd8feb78ea9daa8de085f85a894da3b6b0a52dd8d3ad15568e177aab` |
| `tests/acceptance/typed_operator_steps.py` | fase 1 operador (sello c23d7273…) | `beb2dcc81b91a673cc4f5838815771ae817e918695aa5c60b7d5bef12c3a0a3a` |
| `tests/unit/test_accept_typed_operator.py` | fase 1 operador (sello c23d7273…) | `44ba05971fefe7fddc53dcf732a7d17fc5cb8a72e66adfbce03c42b1969130f0` |
| `tests/unit/test_pytest_observation.py` | R8 (sello 93acd1a5…) | `5d3d30a6b6d193956a075d603738070b3d7a37813830678112597b6dc91683db` |
| `tests/unit/test_pytest_phases.py` | R8 (sello 93acd1a5…) | `5f538fb5345bb96130deb0e60d8b873a8fbd6aefdc518d81bc94d45dbf350854` |
| `tests/unit/test_pytest_schema.py` | R8 (sello 93acd1a5…) | `a850808839cc79a9877e088a59041e136b29fe83ab53e68a89a989a1fa855769` |
| `tools/wct/accept/mutation_cases.py` | fase 1 operador (sello c23d7273…) | `dd68580926c080e468b05188d7b9fafa42c386b43c5e46f9da217036c1d7b2dc` |
| `tools/wct/accept/mutation_policy.py` | fase 1 operador (sello c23d7273…) | `dd1a4186d60c981e372e4b0f1f68fa2064d875fa85e2301fb41bcf166e8fe382` |
| `tools/wct/evidence/pytest_api_args.py` | R8 (sello 93acd1a5…) | `410106eebfa28bca0691257f9851ae92f1ce030a066b7f9e8ee72c646c946d79` |
| `tools/wct/evidence/pytest_builders.py` | R8 (sello 93acd1a5…) | `cb0ea790d918fe76c25b65ad7f300c92f5309dff022b2ae79c9e52eddf014901` |
| `tools/wct/evidence/pytest_decode_events.py` | R8 (sello 93acd1a5…) | `d73b5b2682684774b40c89d3d61ed46e0ba23adc926377f5dca3dd7c3d52e826` |
| `tools/wct/evidence/pytest_decode_header.py` | R8 (sello 93acd1a5…) | `ed6f6bc1a90e7e99d013d2dc36eaed3d44a9595221308099bbd194d4d8451cf7` |
| `tools/wct/evidence/pytest_disposition.py` | R8 (sello 93acd1a5…) | `387855f3366c4384fb2f6f9941e4c23ad7c6198843517e3e8c38d5db07d8bd1d` |
| `tools/wct/evidence/pytest_event_catalog.py` | R8 (sello 93acd1a5…) | `0caee719eb69a9234329ac6b80934751c714b2abb42eb040e53c6ce3d8a0dd55` |
| `tools/wct/evidence/pytest_inventory.py` | R8 (sello 93acd1a5…) | `c9086154976d68e70f19b98e76adce4c2d8977fa95ff5946fa0234eacf1f60fc` |
| `tools/wct/evidence/pytest_limits.py` | R8 (sello 93acd1a5…) | `eaa1be95468228e13eddf20083a05751b5c0eaea13831efbda5ab4de9420e827` |
| `tools/wct/evidence/pytest_observation.py` | R8 (sello 93acd1a5…) | `3ec593ba9e49da27bafe00bea9d273832b5ed7b4d92fa670ec8ad24cfd23dbc1` |
| `tools/wct/evidence/pytest_observation_event.py` | R8 (sello 93acd1a5…) | `994c7f3c931b497a5399e42e0d6363f0dd973ff01ebb6a0961c1d813dd4c80e6` |
| `tools/wct/evidence/pytest_observation_events.py` | R8 (sello 93acd1a5…) | `eb907e28e8809c502f0c2695e227178ca4af9d860f5ed28192aed311c0ef59ca` |
| `tools/wct/evidence/pytest_observation_inventory.py` | R8 (sello 93acd1a5…) | `813f82456916cf9fd0be02ff199c268215318984acbad5942ede63a10369c8d9` |
| `tools/wct/evidence/pytest_observation_validate.py` | R8 (sello 93acd1a5…) | `5fdfa9d7c92d9f30a0dff5bad115eff324995d6f7a4769b61aaf6071804ded88` |
| `tools/wct/evidence/pytest_payload_classes.py` | R8 (sello 93acd1a5…) | `bd117302e0bf801a173addfc74bc6c5d90c62e9046d2b9a9cc89d18bfae3df8c` |
| `tools/wct/evidence/pytest_payload_predicates.py` | R8 (sello 93acd1a5…) | `ee321fb7c386d8e407d36c770c3b36a755abaf4336b9d152865783986cb6892a` |
| `tools/wct/evidence/pytest_payload_validate.py` | R8 (sello 93acd1a5…) | `e242772c43fb40d215b8873a8fb054d2a1e212c53d0f57039fc7abea7291b60a` |
| `tools/wct/evidence/pytest_payloads.py` | R8 (sello 93acd1a5…) | `b28d3bb24b6cf00475516139d6a9f64ae24ad536c79ad3379a4c0fc314de20de` |
| `tools/wct/evidence/pytest_phase_pairs.py` | R8 (sello 93acd1a5…) | `da705931b287e5259e8ee275796a191cc6bf7563f6011bf7c2bb9a3efc696460` |
| `tools/wct/evidence/pytest_phases.py` | R8 (sello 93acd1a5…) | `368443477979ab8f6a6b0202cefee8f7dfe2dfbe4f58fede6ec11e3cc58a64c1` |
| `tools/wct/evidence/pytest_scan_closers.py` | R8 (sello 93acd1a5…) | `872f224388acaf2b26f2de11b9983eebe3f1984f540396f363b7034a05328c89` |
| `tools/wct/evidence/pytest_scan_dispatch.py` | R8 (sello 93acd1a5…) | `0e70f17ce4202691342b3a1e072a1a1f506e9ecb02a68651206cee5396041f9b` |
| `tools/wct/evidence/pytest_scan_open.py` | R8 (sello 93acd1a5…) | `04889b64a679150ee37bd42da65d545037ab95bee2098e530a997663e30d15ae` |
| `tools/wct/evidence/pytest_scan_state.py` | R8 (sello 93acd1a5…) | `dbbbef52539139440a4386b3880679d57344acce49ae5aa2746cac9fec6797e7` |
| `tools/wct/evidence/pytest_scan_tests.py` | R8 (sello 93acd1a5…) | `fb45e49717e38764e98bc44b2fcbb3b29b129d4293b8ed2c6b0015104a2c2b87` |
| `tools/wct/evidence/pytest_scan_totals.py` | R8 (sello 93acd1a5…) | `4d4345efdf1c85c6c7f322130c70f3162d664b928c65991d4c4216d77c4c6c83` |
| `tools/wct/evidence/pytest_schema.py` | R8 (sello 93acd1a5…) | `899ad41a48252bc52a5d0e9500ce80a1ed7c99149628b4fab84c5a319bd2da78` |
| `tools/wct/evidence/pytest_sequence.py` | R8 (sello 93acd1a5…) | `014474094a568596eeb794ac58947f6ad848061962b3133c89c6b0431387a84c` |
| `tools/wct/evidence/pytest_termination.py` | R8 (sello 93acd1a5…) | `915c2179dfb9453f41144b09113de2ff04235f6d077f654875dd43185c8d5177` |
| `tools/wct/evidence/pytest_types.py` | R8 (sello 93acd1a5…) | `b2b2b05cf96e91ef277ecea4613006be39ff5682273e68a131b5d3694f22dea3` |
| `tools/wct/evidence/pytest_wire_composites.py` | R8 (sello 93acd1a5…) | `8977f5b4532834a984db188c3c34dd4c1413761a81d9e6c31ee844e7e461c9ca` |
| `tools/wct/evidence/pytest_wire_fields.py` | R8 (sello 93acd1a5…) | `35e74471835091aceb2e3c1e1fc230169e4a5fd91bd4419ce83d7236589c94f7` |
| `tools/wct/evidence/pytest_wire_framing.py` | R8 (sello 93acd1a5…) | `a6261613accc69fc2ffe322b02342d6bf6a919b2d930ea3800202d1b8225f562` |
| `tools/wct/evidence/pytest_wire_values.py` | R8 (sello 93acd1a5…) | `63e25807d864cb47fe24a96c5dcc3bee09ae21926fdeb7c99d9b52ea4a8fe2a3` |

## 5. Contratos citados (hashes completos)

| Documento | SHA-256 | Estado |
|---|---|---|
| DECISION-P03a.md (versionado en main) | `1d98a8944d3a12e10396359656295ace8d79f9ea8b4a77295b602a292eb76fb9` | contrato aprobado D1 |
| PROPUESTA-P03.md (versionado en main) | `47429b8896a38bcd0ec2c835d17a385dd68a4585e5b4207ab86127486ae9f251` | bytes congelados por la decisión |
| OPERADOR-TIPADO-P03A-REV2/CONTRATO.md (solo local; anexo literal §9) | `48e6940e7b4897d11508928ef9cfa7ab78eac579e130c186da753f84a96019c6` | entregado pendiente de aprobación; adopción prospectiva aquí |
| OPERADOR-TIPADO-P03A-REV2/VERIFICACION.md | `f03ca37d18b6942bd00f5e48bf664fb58a3cd628a279365dd7f700975a67e740` | Gherkin/matriz de la fase 1 |
| OPERADOR-TIPADO-P03A-REV2/JOURNALS.md | `09507c26265ed1a5b3a5f9085a70aef61b2d4855d324fc18140e9dd3a3a7651e` | B0 golden documental (1938 bytes) |
| OPERADOR-TIPADO-P03A-REV2/ESTADO.md | `8e26ce874ba6e5c4eb055433dbc125e9a7f5f5dcc269ab04f8afd630c8323875` | estado histórico conservado |
| OPERADOR-TIPADO-P03A-REV2/PROMPT-CODER.md | `b2f2ea142bb5947e4cf9948855ba2ad9e097b4486a77a50df7326e9f514257d3` | antecedente, no autorización |
| OPERADOR-TIPADO-P03A-REV2/INPUTS.sha256 | `42ad42138d60967758451e64bb7ac539930d381528209ab7b870771477e5512b` | verificado |
| OPERADOR-TIPADO-P03A-REV2/ENTREGA.sha256 | `c3989ff349f4597fe1a0814092f159cdbc11b0dbb67efe28f43df5eabe052daa` | sella 6 documentos del expediente |

## 6. Conciliación de la condición AC1 (sin reabrir trabajo cerrado)

**A. Condición histórica REV2 §6** (texto exacto del anexo): «implementación
del binding/integración P03a requiere además AC1 acreditado y pausa levantada
de forma explícita; no inferirlo del pedido documental actual ni de un test
verde.»

**B. ACTA-POST-BLESS-2026-09-17 §4**: «sin PASS de G-MUT sobre la campaña
AC1, sin acreditación AC1, sin cierre de beta.3» (los 928 IDs históricos
siguen sin ejecutar).

**C. ADDENDA-E11-PRECISIONES-2026-09-17 §2** (nota sucesora, posterior a B y
que corrige explícitamente la lectura anterior): «AC1 queda sustentado por
las obligaciones y decisiones vigentes — cadena completa: fuentes resueltas
por adjudicación autorizada → Q-ACCMUT 47/47 → cobertura/CRAP/DRY → full
PRE-BLESS → POST-BLESS + CI verde. Lo único que no existe es una declaración
humana formal posterior "AC1 acreditado": ninguna fuente normativa localizada
la exige como condición separada tras el cierre adjudicado; queda como
etiqueta disponible para el humano, no como evidencia faltante», y «AC1 no es
condición de merge». Q-ACCMUT 47/47 es el killed=planned **de la campaña de
aceptación** (CONTRATO-AC1:101-102); la mutación de fuentes quedó resuelta
por «PUERTA-CONFORME-POR-CIERRE-ADJUDICADO» con decisiones humanas por ID.

**Determinación por precedencia documental**: la sustancia del prerrequisito
«AC1 acreditado» (soporte técnico/documental del motor de aceptación) queda
**satisfecha** por la resolución posterior E11, que como nota sucesora
prevalece sobre la lectura aislada del ACTA-POST-BLESS. Subsiste un residuo
**no técnico**: el segundo conjunto de la cláusula REV2 — «pausa levantada de
forma explícita» — refiere a la pausa registrada en HANDOFF-AC1-2026-09-12
(«Binding P03a no habilitado por esta ronda»; verifier: «desfavorable a
habilitar P03a»), y **ningún documento localizado la levanta
expresamente**; E11 resuelve el estado AC1 pero no menciona P03a.

**Pregunta humana concreta (no bloqueante para este incremento)**: dada la
resolución E11 («AC1 sustentado», etiqueta formal opcional), ¿levanta
expresamente la pausa de fase 2 del binding P03a registrada el 2026-09-12,
o exige antes una declaración formal «AC1 acreditado» u otra garantía? En
cualquier caso, **la fase 2 NO está autorizada por este encargo**: el
prerrequisito técnico/documental sustantivo se considera satisfecho; la
autorización de implementación del binding no ha sido concedida.

## 7. Qué permanece sin integrar o calificar

- **Fase 2 (binding PA01–PA12)**: `tests/acceptance/steps_p03a.py`,
  `p03a_journals.py`, `p03a_campaign.py`,
  `tests/unit/test_accept_steps_p03a.py`, `test_accept_p03a_campaign.py` y el
  sidecar `features/wct-pytest-observation-001.mutation.json` — nunca
  implementados; requieren encargo y puerta propios (§6).
- **Calificación del scope incorporado**: mutación de fuentes/aceptación
  (TEST-002/G-MUT, Q-ACCMUT propio), cobertura diferencial, CRAP, DRY, tier
  full, aleatorización sobre la suite ampliada.
- **Drift protegido**: las rutas nuevas bajo `tools/wct/**` y el hash de
  `mutation_cases.py` abren G-META-1; exige revisión tipo E9 y bless humano
  antes de cualquier merge. Este incremento no ejecuta bless ni
  update-manifest.
- **Publicación**: bump/tag/release (D3) y cierre beta.3 quedan fuera.

## 8. Verificación ejecutada (resumen; detalle en el expediente del encargo)

Con runtime íntegro del venv exclusivo del worktree y logs sellados en el
expediente (`build/tmp/reanclaje1-20260918-exp/logs/`): control negativo de
identidad de imports (4 módulos clave resuelven dentro del worktree);
colección 1183 conciliada por nodeids contra la base 696 (+487 nuevos, todos
en los 4 archivos de tests incorporados, 0 perdidos); focales R8 426/426,
operador 61/61, consumidores AC1 238/238; suite normativa completa
`pytest -q tests/unit tests/integration -m "not property"` = **1 failed,
1180 passed**; property por separado 1/1; gate fast 7/7; estáticos de las
35 fuentes de producto incorporadas (máx 214 LOC de 500; máx 41 sitios de
decisión AST de 100); drift medido: 35 rutas protegidas = 1 modificada
(`mutation_cases.py`) + 34 nuevas, ninguna inesperada.

**Rojos residuales del tier commit (21 gates: 17 PASS · 4 FAIL), con su
carácter, conservados sin reparar por mandato del encargo:**

1. **G-META-1** — drift de las 35 rutas protegidas incorporadas: rojo
   **autorizado** por este incremento; su resolución exige revisión tipo E9
   y bless humano. No se ejecutó bless ni update-manifest.
2. **G-TEST / G-INTROVERT** — misma causa raíz: **regresión real** del
   ratchet `introverted-tests` 0→1 por exactamente un test sellado,
   `tests/unit/test_accept_typed_operator.py:430
   ::test_policy_and_operator_import_no_tests_or_evidence_modules`
   (inspección AST, oráculo O6 de VERIFICACION.md). Su reparación —alza de
   baseline humana registrada o refactor del test sellado con re-sello—
   queda diferida a un incremento con decisión humana; no se silenció el
   test ni el ratchet.
3. **G-DEAD** — vulture (60 % confianza) marca
   `tools/wct/evidence/pytest_types.py:152: unused variable
   'preflight_identities'`: **falso positivo sustantivo** (el campo del
   dataclass lo escribe `pytest_observation.py:246` y lo leen tres tests);
   remedio = entrada en la whitelist de gobernanza, fuera de alcance aquí.
   No se eliminó el campo.

Nota de instrumental: una primera pasada de la suite con venv incompleto
(sin grupo quality) produjo 5 fallos, 4 de ellos ambientales; la reejecución
con runtime íntegro los redujo al único real (logs 07 y 07r conservados).

## 9. Anexo literal — OPERADOR-TIPADO-P03A-REV2/CONTRATO.md

Procedencia: documento local (nunca versionado en main) del paquete
`docs/evolution/plans/BETA3/EXECUTION/OPERADOR-TIPADO-P03A-REV2/CONTRATO.md`
del checkout principal, fechado 2026-09-12. SHA-256 del contenido anexado:
`48e6940e7b4897d11508928ef9cfa7ab78eac579e130c186da753f84a96019c6` (idéntico al original verificado). Se incorpora **como anexo
literal** para que la PR sea autocontenida; su texto histórico se conserva
íntegro, incluyendo su encabezado «Propuesta para aprobación». La decisión
actual de adopción prospectiva es la de §1–§2 de este registro, **fuera** del
anexo; nada del anexo se presenta como aprobación anterior.

```markdown
# Contrato implementable — operador tipado y binding P03a

2026-09-12. Propuesta para aprobación; no implementación ni autorización de ejecución.
Esta revisión reemplaza las decisiones del contrato previo para este incremento y conserva sus bytes.
REV5 rige intención/denominadores; de REV3 se retienen exclusivamente despacho y rutas.
El Gherkin, matriz y allowlist de este expediente se aprueban como una unidad.

## 1. Base y estado comprobado

Raíz: `/home/jandradeu/Documents/well_code_template`. Base Git de construcción:
`932c835ac0eeb75010ec7a1071315b1c51f78eb6`; NO el árbol sucio de main
(HEAD observado `8de9107184288f1aa72c9578a14913686c47ad7c`).
Dos overlays disjuntos, aplicados sobre esa base, sin incorporar otros cambios:

| Overlay | Origen relativo a raíz | Manifiesto relativo a raíz | SHA-256 del manifiesto |
|---|---|---|---|
| AC1, 23 rutas | build/tmp/beta3-acceptance-engine | build/tmp/beta3-acceptance-engine/build/tmp/b3-ma-ac1-r0/candidate-r4-final.sha256 | d28c8991424c085ffb62e2713a053e03b27e8d8fe882dec3f278c391d7e06f9c |
| R8, 37 rutas | build/tmp/beta3-p03a-coder-r0 | build/tmp/p03a-hardening-c2-zct30u3n/candidate-r8.sha256 | 93acd1a5b49fdc06ba2cfa5139fcfe329e5748eb4f7eb613833e8a99bc3c7c8a |

Verificados ahora 23/23 y 37/37. `INPUTS.sha256` fija también documentos leídos.
El handoff CIERRE-INSTRUMENTAL aún describe R7; la sección «Verificación en el
candidato hijo (R8)» de ADJUDICACION-SOBREVIVIENTES-SCAN-CLOSERS es la actualización
vigente del lote: **82 = 78 killed + 4 survived equivalentes adjudicados**.
No acredita las otras 32 fuentes ni cierre integral de P03a.

AC1 está implementado y reutilizable, **no acreditado**. CIERRE-PARCIAL fija R4-final
y pausa humana. Su campaña serial R3 quedó en 1.481 IDs: 1.319 exit1, 112 exit0,
50 null; no son 1.319 muertes calificadas ni medición de R4. Constan fast 7 PASS,
599 colectados y verificaciones focales separadas; no sumar corridas ni afirmar
suite global verde. CALIFICACION conserva cinco fallos reproducidos en base sin
AC1 y problemas de aislamiento: diagnosticarlos no autoriza ignorar un baseline
rojo actual. Pendientes: mutación de fuentes AC1 completa/calificada, aceptación
propia (48 celdas históricas con rechazos léxicos y una fila potencialmente
insensible), cobertura, CRAP/DRY, puertas aplicables y dictamen independiente.
El operador P03a NO resuelve ni activa silenciosamente el rediseño AC2 de esa tabla.

Lectura de implementación: `mutations` enumera todas las celdas; `generate` importa
`tests.acceptance.steps.execute_scenario`; el consumidor carga `WCT_ACCEPT_IR` o
BASE_IR y ejecuta un test por escenario, no por fila. `steps` ya delega a
campaign_steps para AC1. `run_mutations` y `accept_verdict` importan directamente
mutation_cases; el segundo retorna `(failed, messages)`: **False significa PASS**.
No hacen falta cambios en esos consumidores para propagar la política dentro del IR.

## 2. API y política cerradas

Módulo nuevo `tools/wct/accept/mutation_policy.py`:

```python
class MutationPolicyError(ValueError): ...


def load_policy(feature_path: Path, policy_path: Path) -> dict[str, Any]: ...
def validate_policy(ir: dict[str, Any], policy: object) -> list[dict[str, Any]]: ...
```

`load_policy` lee JSON UTF-8 estricto, verifica hash de los bytes originales de
feature_path, parsea esa feature con `parsing.parse_feature` y usa validate_policy;
retorna el objeto validado, sin callbacks ni imports dinámicos. Errores de IO,
JSON, UTF-8, esquema o incompatibilidad → MutationPolicyError con ruta y causa.
Clase concreta cumple N818. No reexportar en pipeline ni __init__.

`validate_policy` es pura: retorna una copia de las celdas en orden canónico;
rechaza configuración inválida incluso si se inyecta directamente en el IR.
`mutation_cases.mutations(ir)` mantiene firma y formato de resultados actual.
**Solo ausencia de la clave** `mutation_policy` selecciona histórico; presencia
con null, {}, false, lista u otra configuración inválida siempre falla. No se
consulta filesystem ni se importan tests/extractores desde mutations.

Sidecar P03a: `features/wct-pytest-observation-001.mutation.json`.
Objeto con exactamente estas claves, cada celda con exactamente las cuatro indicadas:

```json
{
  "schema_version": 1,
  "source": "features/wct-pytest-observation-001.feature",
  "source_sha256": "3d957b13ea6a2d1d40cdb8d600467c23420a2c3c781d36b6c0808be9ee26df2d",
  "cells": [
    {"scenario":0,"row":0,"field":"expected","type":"bool"},
    {"scenario":0,"row":1,"field":"expected","type":"bool"},
    {"scenario":0,"row":2,"field":"expected","type":"bool"},
    {"scenario":0,"row":3,"field":"expected","type":"bool"},
    {"scenario":0,"row":4,"field":"expected","type":"bool"},
    {"scenario":0,"row":5,"field":"expected","type":"bool"},
    {"scenario":0,"row":6,"field":"expected","type":"bool"},
    {"scenario":0,"row":7,"field":"expected","type":"bool"},
    {"scenario":0,"row":8,"field":"expected","type":"bool"},
    {"scenario":0,"row":9,"field":"expected","type":"bool"},
    {"scenario":0,"row":10,"field":"expected","type":"str"},
    {"scenario":0,"row":11,"field":"expected","type":"bool"}
  ]
}
```

Validación: schema_version int exacto =1 (no bool); source string no vacío igual
al IR; digest 64 hex minúsculas; cells lista no vacía; coordenadas int exactas
no negativas existentes; field string de columna existente; type exactamente
bool/str; celda original string, bool solo `true`/`false`; sin coordenadas
repetidas, claves extra, claves JSON duplicadas o constantes NaN/Infinity.
No imponer nombres de caso ni campos del binding en el motor genérico.
Orden: índice de escenario, índice de fila, orden de columna original del IR;
el orden de cells del JSON no altera las identidades. Políticas parciales son
válidas genéricamente; la receta P03a exige por separado el conjunto exacto de 12.

Transformaciones: bool `true` ↔ `false`; str concatena `__typed` (incluidos vacío,
Unicode o cadena que ya termina en ese sufijo: siempre cambia). No tipado numérico
nuevo. Histórico exacto: regex `-?\d+(?:\.\d+)?`, Decimal cero→`1`, otro número→`0`;
resto concatena `__mutated`. Preservar también orden, metadatos y clones JSON.

Activación explícita ÚNICA: receta §5 parsea feature, llama load_policy con ambas
rutas explícitas y añade `ir["mutation_policy"] = policy` antes de generate,
run_mutations y accept_verdict. Ningún descubrimiento por sidecar/source/tag,
ninguna nueva opción CLI ni variable ambiente. Tener sidecar sin ese paso no
activa nada. Se conservan hash de feature, policy y archivo IR realmente usado.
La validación de hash físico ocurre en load_policy; validate_policy no pretende
releerlo ni autenticar al caller. La receta comprueba de nuevo esos hashes antes
al lanzar. Los clones mutados conservan política y source originales.

## 3. Binding y doce oráculos

Despacho exacto al inicio de steps.execute_scenario:
`ir.get("source") == "features/wct-pytest-observation-001.feature"` → import local
de `tests.acceptance.steps_p03a.execute_p03a_scenario` y return. Otro source
conserva el camino existente (incluido campaign_steps), sin importar steps_p03a.
Un segundo guard exacto para `features/wct-typed-mutation-001.feature` despacha
al ejecutor de pruebas del operador; no sustituye el dispatcher AC1.

API nueva: `execute_p03a_scenario(ir: dict[str, Any], scenario_index: int) -> None`.
Procesa Background+steps, sustitución por fila y contexto nuevo por fila como
el ejecutor actual. Given/When/Then tienen exactamente el vocabulario de la
feature R8. Caso desconocido → AssertionError `unknown p03a case: <case>`;
campo desconocido → AssertionError `unknown p03a field: <field>`; paso desconocido,
orden imposible, literal bool inválido o par case/field conocido pero incompatible
→ error de arnés con causa. Nunca SemanticMismatch para estos errores.
`P03A_CASES` fija data+kwargs; `P03A_FIELDS` fija extractor+tipo y la relación 1:1.
No importar test_pytest_observation ni sus builders; reutilizar el literal B0 de
JOURNALS.md y serialización stdlib propia para deltas. No usar encoder del SUT.

Entradas comunes: B0 documental (SHA y bytes en JOURNALS.md), run_id=`"0"*32`;
executions=(ExecutionExpectation("collection-1","collection",D,D,D),
ExecutionExpectation("producer-1","producer",D,D,D)), D=`"a"*64`;
`decode_pytest_journal(data, run_id=run_id, executions=executions, max_bytes=len(data))`;
`reconcile_pytest(obs, expected=("t",), property_ids=())`, salvo delta expreso.
Imports públicos desde pytest_observation y pytest_types, no módulos internos.
`obs` es JournalObservation, `r` PytestObservation, `t=r.executions[1].tests[0]`.
L[i] identifica la línea original B0 de índice i. Reemplazos JSON se serializan
UTF-8 con sort_keys=True, ensure_ascii=False, separators=(",",":"), allow_nan=False,
y LF. Offset[i]=suma de bytes de L[0:i], nunca índice de caracteres.

| Caso / field | Data y kwargs exactos | Extractor; esperado literal |
|---|---|---|
| PA01 / protocol_complete | B0 | `r.executions[1].protocol_complete`; `true` |
| PA02 / decoder_prefix_preserved | concatenar L[0:25] y bytes `[25,1,13,` sin LF | `obs.consumed_bytes == Offset[25] and obs.tail_sha256 == sha256(b"[25,1,13,").hexdigest()`; `true` |
| PA03 / framing_defect_visible | concatenar L[0:25] y bytes `[25,1,13,` más LF | `any(f.code == "invalid_json" and f.offset == Offset[25] for f in obs.findings)`; `true` |
| PA04 / phase_defect_visible | B0 con L[21]=`[21,1,9,14,[0,1,0,true,null,false,null]]` más LF | `any(f.code == "invalid_field" and f.offset == Offset[21] for f in obs.findings)`; `true` |
| PA05 / failed_terminal_preserved | B0 con L[21]=`[21,1,9,14,[0,1,1,true,"AssertionError",false,null]]`, L[22]=`[22,1,10,15,[0,1,1,false]]` | `t.terminal and not t.pass_eligible and t.call_disposition == "observed" and any(p.phase == "call" and p.disposition == "failed" for p in t.phases)`; `true` |
| PA06 / identity_substitution_detected | B0, expected=("u",) | `r.identities.status == "mismatch"`; `true` |
| PA07 / property_mismatch_detected | variante P7 abajo; property_ids=() | `any(f.code == "unexpected_property" and f.execution_id == "producer-1" and f.nodeid == "p" for f in r.property_findings)`; `true` |
| PA08 / exit_not_replaced | B0, solo payload L[29][4][0]=1, termination sigue "exited" | `r.executions[1].exit_code == 1 and r.executions[1].termination == "exited"`; `true` |
| PA09 / exact_boundary_allowed | B0, solo L[4][4][1]="a"*4096; expected=("a"*4096,) | `t.nodeid == "a"*4096 and t.terminal and t.pass_eligible and not r.findings`; `true` |
| PA10 / over_boundary_rejected | B0, solo L[4][4][1]="a"*4097; expected sigue ("t",) | `any(f.code == "invalid_field" and f.offset == Offset[4] for f in obs.findings)`; `true` |
| PA11 / provenance | B0 | `r.provenance`; `caller-supplied-unverified` (str) |
| PA12 / invalid_argument_rejected | B0; llamada exacta abajo | booleano contractual; `true` |

P7: partir de eventos B0; después de L[4] insertar declaración supervisor ex0,
code0, payload `[1,"p"]`; después de L[5] insertar dos eventos ex0 code8 `[1,true]`
y code10 `[1,true]`; después de L[15] insertar iguales dos eventos ex1; cambiar
payload de los collect_end originales L[7] y L[17] a `[1,1]`. Conservar el orden
de todos los demás eventos. Renumerar seq global desde 1 y local_seq desde 1
independientemente por ejecución, solo eventos cuyo local original no era null;
las inserciones code8/code10 son locales y code0 supervisor. No ejecutar p.
La propiedad está deseleccionada pero no autorizada en property_ids: esta entrada
produce el finding elegido, a diferencia de la contradicción del contrato previo.

PA12: el When invoca **`reconcile_pytest(observation, expected=("\x01t",), property_ids=())`**.
Captura solo ObservationError: True si `type(error) is ObservationError` y
code="invalid_reference" y field="expected"; cualquier otra ObservationError
(incluida subclase) → False; ausencia de excepción → False. TypeError,
RuntimeError, fallos del decoder y otras excepciones instrumentales se propagan.
No envolver todo el Given/When en un catch genérico ni convertir errores en True.

Solo Then compara una vez valor tipado; exige `type(actual) is bool/str` según
campo (tipo erróneo es ERROR, no aceptación de 1 como True). Ante desigualdad,
lanza el alias público SemanticMismatch con mensaje EXACTO:
`[wct-p03a] <case>/<field>: expected <expected!r>, got <actual!r>`.
Case/field nunca se mutan en campaña: los controles son 12 filas con case="PA99"
y 12 con field="inventado", cada uno aislado en IR completo; total 24 rechazos
clasificados error, fuera de planned/killed.

## 4. Allowlist exacta propuesta

Solo en copia nueva; pertenecer a la antigua allowlist AC1 no concede permiso.
Los overlays son importación byte a byte, no autorización para editar sus 60 rutas.
Cambios de implementación permitidos tras aprobar este contrato:

| Ruta | Operación y límite |
|---|---|
| tools/wct/accept/mutation_policy.py | nueva, carga/validación pura de política |
| tools/wct/accept/mutation_cases.py | editar: import explícito validate_policy y rama tipada; histórico intacto |
| tests/acceptance/steps.py | editar: solo dos guards con imports locales §3 |
| tests/acceptance/steps_p03a.py | nueva: dispatcher, casos, extractores y comparación |
| tests/acceptance/p03a_journals.py | nueva: literal B0 y deltas independientes, importado por steps_p03a |
| tests/acceptance/typed_operator_steps.py | nueva: ejecutor del Gherkin del operador contra APIs reales |
| tests/acceptance/p03a_campaign.py | nueva: receta explícita §5 y comprobación/custodia de atribución |
| tests/unit/test_accept_typed_operator.py | nueva: operador/política/compatibilidad |
| tests/unit/test_accept_steps_p03a.py | nueva: binding, despacho, PA12, 24 rechazos |
| tests/unit/test_accept_p03a_campaign.py | nueva: integración real, atribución y errores |
| features/wct-typed-mutation-001.feature | nueva: bloque Gherkin de VERIFICACION.md |
| features/wct-pytest-observation-001.mutation.json | nueva: sidecar literal §2 |

Imports exactos autorizados: mutation_cases→mutation_policy; mutation_policy→parsing;
steps→steps_p03a/typed_operator_steps (locales); steps_p03a→p03a_journals,
pytest_observation, pytest_types, accept.semantic; typed_operator_steps y
p03a_campaign→accept.pipeline y mutation_policy, bibliotecas stdlib/pytest ya
instaladas según necesidad de pruebas. Nuevos unitarios importan los módulos que
prueban y APIs existentes AC1. Sin imports del motor a tests ni a evidence.

NO editar: pipeline/__init__, generation, campaign, process, receipt*,
pytest_receipt, semantic, verdict*, parsing, ir_checks, campaign_steps,
protocol_runner, cinco tests unitarios AC1 existentes, fuentes/tests R8,
feature P03a, CLI, gobernanza, dependencias, lockfiles, otros bindings.
Tests generados: generar únicamente con generate en ruta exclusiva de build/tmp;
NO editar/regenerar `tests/acceptance/generated/test_acceptance.py` versionado.
Si límites de tamaño/sitios requieren más particiones, presentar ampliación
concreta antes de escribir otra ruta; no autoautorizar imports o archivos.

## 5. Campaña, identidades y custodia

Receta pública `tests.acceptance.p03a_campaign.run_p03a_campaign(root: Path) -> dict[str, Any]`:
rechaza cwd distinto de root; root es la copia aislada. Preflight comprueba hash
literal de feature R8, carga sidecar explícito y coteja IR contra las doce filas
literales de §3 (case, field y expected), escenario 0 con nombre exacto
`Distinguir observaciones y defectos del protocolo`, tres columnas y ningún otro
escenario. Luego adjunta política. Comparar inventario contra tabla independiente
literal, no deducir el denominador del reporte ni contar únicamente resultados.
Conjunto esperado `(id,scenario,row,field,from,to)`: id=row=0..11, nombre anterior,
field="expected", from="true"/to="false", excepto id10 con from=
"caller-supplied-unverified", to="caller-supplied-unverified__typed". Exactamente
12, sin omisiones, duplicados ni extras; cada clon difiere solo en su celda.

Crear directorio exclusivo en build/tmp, conservar policy/feature/IR/inventario;
generate(ir, <directorio>/test_acceptance.py). Runner exacto: sys.executable,
`-m pytest -q -o addopts= --tb=short --color=no`, ruta absoluta del generado.
Mantener protocolo/plugins AC1; no runner personalizado que fabrique recibos.
PYTHONPATH y ejecutables de la copia/runtime declarados y verificados. Invocar
`run_mutations(ir, command)` y después `accept_verdict(ir, report)` reales; conservar
reporte sin sustituir sus resultados y dictamen `{failed,messages}` aparte.
Política inválida aborta antes de baseline, no inventa reporte aprobado vacío.

Baseline del IR original **pass/exit0/recibo válido** obligatorio; si falla, cero
mutantes ejecutados. El protocolo productivo debe cerrar planned=12, killed=12,
survived=errors=not_run=0, sin pendientes y `(failed=False, messages=[])`.
Un FAIL no se corrige mediante conciliación externa. Los diagnósticos adicionales
pueden BLOQUEAR la entrega aunque el motor pase; nunca hacerlo pasar si falla.

Custodia por intento a cargo de receta; comprobación a cargo del verifier:
mapa id→mutation-id/attempt.json→ir.json/receipt.json/receipt.events.json/logs.
Comprobar nonce único, fase por directorio, hash IR calculado de bytes igual al
attempt y receipt, metadatos de celda iguales al inventario literal, exit externo
igual al recibo, colección del nombre generado y una fase call mismatch sin
errores setup/teardown. SHA-256 de TODOS esos archivos en manifiesto del expediente.
El recibo y events no guardan mensaje: la fuente de atribución es stdout/stderr
conservado por process. Extraer la línea diagnóstica de excepción, no textos del
código mostrados por traceback; normalizar únicamente prefijo pytest/tipo de
excepción. Exigir un único mensaje lógico completo con el formato §3 y valores
exactos del id: bool expected=False/got=True; PA11 expected cadena con sufijo/got
cadena original. Duplicados idénticos impresos por pytest se deduplican conservando
archivo y números de línea; mensajes conflictivos, ausentes, cruzados entre
intentos o truncados bloquean. Guardar attribution.json con id, case, field,
expected, actual, attempt_id, ir_sha256, log_sha256 y líneas fuente.
No falsificar attribution desde la tabla de expectativas. Un stdout con mensaje
correcto pero receipt/phase inválido nunca es killed. Baseline no tiene mismatch.
Custodia es local y cooperativa; no autenticación frente a procesos del mismo UID.

## 6. Puertas

Aprobación explícita de contrato+Gherkin+allowlist habilita implementación aislada
del operador (primera fase). Se preserva la secuencia REV5: implementación del
binding/integración P03a requiere además AC1 acreditado y pausa levantada de forma
explícita; no inferirlo del pedido documental actual ni de un test verde.
No quedan decisiones técnicas delegadas al coder. Quedan decisiones de autorización:
aprobar este alcance y resolver/reanudar la calificación AC1, incluida su puerta
de aceptación propia. No se presupone autorización AC2 ni excepción de residuos.
La campaña P03a futura acredita este binding; ni ella ni las pruebas del operador
acreditan AC1 completo o las otras 32 fuentes P03a.
```
