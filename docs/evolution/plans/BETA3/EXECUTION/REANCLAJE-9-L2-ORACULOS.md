# Registro REANCLAJE-9 — oráculos L2 bajo contrato vigente y sensibilidad demostrada sobre los 33 IDs (2026-09-18)

Estado: **oráculos G1–G7 implementados en la ruta autorizada y sensibilidad
acreditada por ID (33/33) bajo la selección ampliada**, sin cambios de
producto, contratos ni gobernanza. El bruto histórico se conserva intacto:
**278 = 233 killed + 45 survived**. Lo aquí ejecutado es **evidencia sucesora
de sensibilidad**, no una reescritura de la campaña ni una nueva campaña de
278. Las 10 equivalencias propuestas y los 2 comportamientos no contratados
siguen **pendientes de decisión humana** (D-A/D-B): nadie los ratifica aquí.

## 1. Base, identidades y sellos

| Elemento | Identidad | Comprobación |
|---|---|---|
| Base documental | `eb8f2ea23128545aa0116d5b1f2f9b5813ea6ddf` (= origin `codex/reanclaje-p03a-fase1` = headRefOid PR #56, borrador) | `git ls-remote` + `gh pr view 56` al inicio y revalidados antes de publicar |
| main / tag | main `8a379d64…`, tag `v1.0.0b3.dev1` intactos | `git ls-remote` |
| Checkout principal del usuario | rama `codex/plan-beta3-moldes-evals` (8de9107), árbol con trabajo ajeno sin commit | no se tocó rama/índice/archivos |
| Copia de trabajo | `build/tmp/reanclaje9-20260918/repo` (raíz Git propia, detached en eb8f2ea) + `mutants/` (copia del árbol instrumentado R7) | preflight por lanzamiento |
| Cuatro fuentes wire | `pytest_wire_values.py` `63e25807…`, `pytest_wire_fields.py` `35e74471…`, `pytest_wire_composites.py` `8977f5b4…`, `pytest_wire_framing.py` `a6261613…` | byte-idénticas al sello R8 (`candidate-r8.sha256`, digest `93acd1a5…`) en eb8f2ea, en `run/` de R7 y en la copia — **sin drift material** |
| Sello R7 | manifiesto 26/26 OK, digest `4687309f…` | `sha256sum -c` |
| Sello R8 | manifiesto 53/53 OK, digest `3996976f…` | `sha256sum -c` |
| pyproject en eb8f2ea | `f27de519…` = original sellado por R7 (la sección `[tool.mutmut]` versionada es la original de `src/example`, NO la experimental de R7) | sha256 |

**Nota de sellado**: el árbol instrumentado `run/mutants/` de R7 **no está
sellado como árbol** por ningún manifiesto (la frase de R8 §1 «miembros
sellados» es imprecisa: ni R7 ni R8 incluyen los `.meta`/stats entre sus
miembros; el snapshot pre-campaña sellado es `logs/08-stats-snapshot.json` y
difiere del in-situ `mutmut-stats.json` por las asociaciones que la campaña
escribió después — consistente con la narrativa de R7). Por eso la acreditación
de identidad de este encargo es **por comparación de hash de los 321 archivos**
de la copia propia contra el árbol in situ (`logs/00-identidad-mutants.sha256`),
más el inventario sellado `logs/09-inventario-ids.json` (278 IDs).

## 2. Reconciliación del alcance — los 33

Derivados de la tabla adjudicada R8 §5.1 y verificados por script contra las
fuentes selladas: **33 únicos ⊆ 45 survived (R7 logs/15) ⊆ 278 inventario
(R7 logs/09)**; partición exacta 33 hueco + 10 equivalencia + 2 no
contratados = 45. Diff real por ID: R7 logs/16 (extraito en
`logs/01-diffs-33.txt`). Fuente y grupo por ID: tabla §4 de este registro.

Clasificación de los 33 por causa:

- **A — test inexistente o insuficiente: 32.** La selección L2 (126 nodeids)
  no contenía ningún caso que ejercitara la obligación de frontera
  correspondiente (p. ej. nunca envió un PluginClaim con opcionales válidos,
  nunca un argv con item vacío, nunca NaN/Infinity, nunca profundidad ==8).
- **B — test existente omitido de la selección: 1** (`x_canonical_bytes__mutmut_12`,
  grupo G6): el oráculo `test_observation_case[PA01-unicode-byte-offsets]`
  YA EXISTE en la suite R8 (R8 §4 lo demostró: falla bajo cb_12 en
  `test_pytest_observation.py:2749`). El hueco era de la selección de campaña.
  Se corrige **ampliando la selección** (G6a); el test no se duplica ni se
  edita.
- **C — atribución que requería aclaración: 0** tras la evidencia individual.
  `cb_8` NO comparte causa con cb_12 por vecindad de función: la sonda propia
  y la microcampaña muestran que cb_8 muere por la aserción de canonicidad del
  test nuevo (y también por PA01-unicode), con causa distinta (remoción del
  argumento `ensure_ascii` vs `True` explícito) — evidencia por ID separada en
  `logs/03-microcampana.json`.

## 3. Diseño por grupo (obligación, cita, entrada, observable, IDs)

Contrato: PROPUESTA-P03.md sha256 `47429b88…` (congelado). Todas las entradas
son journals construidos con el serializador propio del test (`_dump`,
`ensure_ascii=False`) o literales de bytes; el esperado jamás se calcula con
el SUT. Ruta única editada: `tests/unit/test_pytest_schema.py`
(antes `a8508088…`, después `8eef7362…`; **+144 líneas, 0 retiradas**).

| Grupo | Obligación contractual (cita) | Entrada → observable | Test (reutilizado/nuevo) | IDs que discrimina |
|---|---|---|---|---|
| G1a límites S de opcionales | §3 l.213 PluginClaim «distribution/version: S no vacío o N; source_sha256: H o N» | claim con `"d"/"v"`/D64 válidos → aceptado con valores preservados; `""` → `invalid_field` | nuevo `test_wire_plugin_claim_optionals…` | opt_s 2/3/4/5/6, opt_h_2 (6) |
| G1b argv | §3 l.209 «argv: tupla no vacía de S no vacíos» | `["x"]` → aceptado `("x",)`; `["x",""]` → `invalid_field` | nuevo `test_wire_argv_items…` | argv 12/13 (2) |
| G1c cwd mínimo | §3 l.209 «cwd: S absoluto POSIX…» | `"/"` (1 byte) → aceptado | nuevo `test_wire_cwd_accepts_root…` | cwd_6 (1) |
| G1d exception_type | §3 l.222+235 «exception_type:S no vacío o N» con coherencia present/name | present=true `"E"` → aceptado `"E"`; `""` → `invalid_field` | nuevo `test_wire_phase_make_keeps_short…` | exception_type 2/3/5/6 (4) |
| G2 cwd componentes | §3 l.209 «sin componentes . o ..» | `/a/./b` → `invalid_field` | ídem G1c (segunda aserción) | cwd_15 (1) |
| G3 JSON estricto | §2 l.106 «floats/NaN/Infinity rechazados» + §4 l.267 vocabulario | línea con `NaN`/`Infinity` → finding `invalid_json` exacto, sin crash | nuevo `test_wire_constant_literals…[nan,infinity]` | loads 10/11/12/17/21 (5) |
| G4 profundidad límite | §2 l.107 «Contenedor máximo8 niveles, contando objeto exterior como1» + precedencia §4 | profundidad ==8 (hoja escalar y hoja vacía) → NO es `invalid_json`: el defecto baja a `invalid_field` (forma del vector) | nuevo `test_wire_depth_at_eight…[hoja-escalar,hoja-vacia]` | depth 5/7/13, loads_30 (4) |
| G5 C0 en listas | §2 l.97-98 «strings… sin surrogate, C0/DEL» | argv `["python","\u0001"]` → `invalid_encoding` | nuevo `test_wire_control_char_inside_list_item…` | check_strings_2 (1) |
| G6 canónico unicode | §3 l.134 «ensure_ascii=False» + §4 l.267 vocabulario | declaración `"café"` (UTF-8) → aceptada con nodeid preservado; línea con escape `"\ud800"` → `invalid_encoding` | nuevo `test_wire_canonical_utf8…` + **selección ampliada** con PA01-unicode existente (G6a) | canonical_bytes 8/12, parse_line 12/13/14 (5) |
| G7 digest H | §3 l.202 «H=digest lowerhex64» + §4 `invalid_field` | `"z"*64` → `invalid_field` exacto; `5` → `invalid_field` sin crash | nuevo `test_wire_digest_field…[hex-invalido,numerico]` | h 1/6/7/8 (4) |

Regla de diseño aplicada en todos: el esperado es el **código del catálogo §4
o la aceptación con preservación del valor**, nunca texto interno, prefijos ni
detalles de implementación; sin mocks; sin estados imposibles; sin copiar el
algoritmo productivo.

## 4. Resultados por ID (microcampaña, selección ampliada, ORIGINAL verde)

Selección ampliada de campaña (111 nodeids) = `tests/unit/test_pytest_schema.py`
completo (110: 98 históricos + 12 nuevos) + `test_observation_case[PA01-unicode-byte-offsets]`.
ORIGINAL: **111 passed, exit 0** (9.0 s). Microcampaña: **33/33
ROJO-ATRIBUIDO** (cada mutante activo cae por el test previsto en §3; detalle
completo en `logs/03-microcampana.json`, salidas por ID en `logs/micro/`).

| ID (sufijo) | Causa de la muerte bajo el mutante | Fallo atribuido |
|---|---|---|
| argv_12 | `["x",""]` aceptado (min_len removido) → findings `()` ≠ `invalid_field` | test argv |
| argv_13 | `["x"]` rechazado (min_len=2) → findings ≠ `()` | test argv |
| cwd_6 | `"/"` rechazado (min_len=2) | test cwd |
| cwd_15 | `/a/./b` aceptado (`"XX.XX" in parts`) | test cwd |
| exception_type_2 | `_s(None)` eleva invalid_field en la vía de éxito | test phase_make |
| exception_type_3 | **TypeError** `'<=' not supported NoneType/int` (min_len=None) — canal crash, causa y relación contractual demostradas (`logs/04-crash-canales.txt`) | test phase_make |
| exception_type_5 | `""` aceptado (min_len removido) | test phase_make |
| exception_type_6 | `"E"` (1 char) rechazado (min_len=2) | test phase_make |
| opt_s_2/3/4 | vía de éxito rota: invalid_field / TypeError comparación None / TypeError argumento faltante (`logs/04`) | test plugin |
| opt_s_5 | `""` aceptado | test plugin |
| opt_s_6 | `"d"` (1 char) rechazado | test plugin |
| opt_h_2 | D64 válido → `_h(None)` eleva invalid_field | test plugin |
| loads_10/11/12 | código del finding manglado (None/XX/mayús) | test constant_literals [nan, infinity] |
| loads_17/21 | **ValueError** «Out of range float values are not JSON compliant: nan» escapa del canal _DefectError (`logs/04`) — el original emite `invalid_json` limpio | test constant_literals |
| depth_5 | hoja escalar ==8 medida 9 → `invalid_json` ≠ `invalid_field` | test depth [hoja-escalar] |
| depth_7 | ambos casos ==8 medidos 9 → `invalid_json` | test depth [ambos] |
| depth_13 | hoja vacía ==8 medida 9 (default=1) → `invalid_json` | test depth [hoja-vacia] |
| loads_30 | ==8 rechazado (`>=`) → `invalid_json` | test depth [ambos] |
| check_strings_2 | items de lista saltados (`_check_strings(None)`) → C0 aceptado | test control_char |
| canonical_bytes_8 | `café` → noncanonical (ensure_ascii por defecto) y surrogate aceptado | test canonical_utf8 **y** PA01-unicode |
| canonical_bytes_12 | ídem (ensure_ascii=True) | test canonical_utf8 **y** PA01-unicode |
| parse_line_12/13/14 | código del canal surrogate manglado (None/XX/mayús) | test canonical_utf8 |
| h_1 | `"z"*64` aceptado (or→and) y `5` → **TypeError** regex (`logs/04`) | test digest [ambos params] |
| h_6/7/8 | código `invalid_field` manglado | test digest [ambos params] |

La selección ampliada queda registrada como **receta del expediente**
(`sondas.py::SELECTION`), no como configuración del repositorio. No se
modificó el test PA01-unicode ni `pyproject.toml`.

## 5. Métricas separadas (bruto histórico ≠ evidencia sucesora)

- **Bruto histórico (in tacto)**: 278 = 233 killed + 45 survived (campaña R7).
  Nadie lo reescribe; los 233 kills históricos NO se repitieron.
- **Evidencia sucesora (este encargo)**: sobre los 33 IDs con hueco, cada uno
  fue re-ejecutado individualmente (sonda por mutante con MUTANT_UNDER_TEST,
  arnés fail-closed, ORIGINAL verde) bajo la selección ampliada de 111: 33/33
  rojos atribuidos. **No** se afirma «266 killed»: eso requeriría una campaña
  completa re-ejecutada con la selección ampliada, que este encargo no
  ejecuta ni autoriza. Los 10 de equivalencia y los 2 no contratados no
  fueron ejecutados (salvo el control de pertenencia documentado: NO están
  en el conjunto de 33).
- Aislamiento: se reutilizó el árbol instrumentado histórico **sin
  regenerarlo** (cero invocaciones a `mutmut run`; los `.meta` no se
  tocaron); identidad acreditada por hash de 321 archivos; la única
  divergencia autorizada de la copia es el test sucesor sincronizado
  repo→mutants (excepción explícita, documentada y verificada por hash en
  cada lanzamiento; `__pycache__` excluido como artefacto derivado).

## 6. Pendientes que este encargo NO resuelve

- **D-A**: ratificación o rechazo de las 10 equivalencias acotadas (cwd_5,
  utc_5/6, cb_3, cb_6, cb_11, cb_16, cb_18, parse_line_4, line_defect_7) con
  sus dominios y contraejuntos declarados en R8 §5.2.
- **D-B**: disposición de los 2 comportamientos no contratados de
  `_DefectError` (mensaje, execution_id) — R8 §5.3.
- **D-C/D-D**: decisión sobre WIRE_FIELDS (§7) y docstrings inertes.

## 7. WIRE_FIELDS — propuesta de verificación independiente (NO implementada)

Los 59 strings contractuales (21 clases; 59 = Σ tuplas de
`pytest_wire_fields.py`) no son instrumentables por mutmut 3.7 (literales de
módulo). Propuesta preparada, **no ejecutada**:

1. **Oráculo literal independiente**: transcribir de la tabla §3 del contrato
   (PROPUESTA-P03, `47429b88…`) un literal `dict[type, tuple[str, …]]` COMPLETO
   por clase, escrito a mano en el test (no generado ni importado desde la
   tabla productiva). Comparación exacta por clase contra `WIRE_FIELDS`.
2. **Controles por clase**: omisión de campo, campo extra, campo sustituido y
   orden intercambiado (mutaciones del literal del oráculo en copia local del
   test, verificando que la comparación exacta los detecta — anti-tautología).
3. **Verificación de consumo, distinta de la igualdad de tabla**:
   `pytest_decode_events.py:44` consume `names = WIRE_FIELDS[cls]` con
   extracción posicional (`zip(names, values, strict=True)`); el control de
   consumo es que un vector con aridad/orden correctos según el CONTRATO
   decodifica al payload con campos en orden normativo (ya cubierto hoy por
   `test_wire_fields_arity_per_class` para 2 clases y los PA09-*-exact vía
   decode); la propuesta extiende la igualdad a las 21 clases, y el consumo
   queda demostrado por los oráculos de aceptación existentes.
4. Los 5 docstrings (4 de módulo + 1 de clase `DefectError`) quedan separados:
  constantes inertes en runtime; su calificación de «limitación instrumental
  sin dispensa» no exige mutaciones conductuales inventadas.

## 8. Incidente del verifier de R8 — aclaración (requisito del encargo)

La frase «restauró los artefactos que su reejecución sobrescribió» (R8 §9-bis)
se aclara así, con evidencia re-verificada en este encargo:

- **Qué archivos**: 5 — `logs/02-ledger-guardian.csv`, `logs/sonda-ORIGINAL.txt`,
  `logs/sonda-…x__loads__mutmut_17.txt`, `logs/sonda-…x__h__mutmut_1.txt`,
  `logs/sonda-…x__utc__mutmut_6.txt` (el guardián del autor escribía el
  ledger y el arnés las sondas en rutas del expediente).
- **En qué copia**: la del expediente del autor
  (`build/tmp/reanclaje8-20260918/logs/`), NO un árbol histórico externo.
- **Eran miembros sellados**: sí, los 5 están en `MANIFIESTO-REANCLAJE8.sha256`.
- **Qué acreditó la restauración**: el verifier respaldó los originales ANTES
  de reejecutar (`verifier/backup-pre-reejecucion/SHA256SUMS.txt`, 5 hashes);
  tras restaurar, los 5 archivos coinciden byte a byte con el backup Y con
  las entradas del manifiesto (re-verificado aquí por doble vía); el
  manifiesto re-verificó 53/53. Sus propias salidas viven separadas en
  `verifier/mi-reejecucion/`.
- **Qué resultados dependen de ellos**: la evidencia de sonda de R8 para
  ORIGINAL/loads_17/h_1/utc_6 y el ledger de sondas; ninguno cambió de
  contenido (restauración byte-exacta), de modo que ningún dictamen de R8 se
  apoya en bytes distintos de los sellados.
- **Desviación registrada**: sobrescribir miembros sellados (aun con
  restauración acreditada) es una desviación de proceso que R8 declaró a
  medias; queda asentada aquí sin borrarla. El verifier de ESTE encargo no
  escribió en el workspace del autor: trabajó en `verifier/copia-mutants/`
  desechable propia con ledger y hashes propios.

## 9. Verificación del compuesto, presupuestos y dictamen

Batería (copias propias; PATH con el bin del venv):

| Comprobación | Resultado | Evidencia |
|---|---|---|
| Colección baseline (eb8f2ea prístino) | 1183 colectados | `logs/10` |
| Colección modificada | **1195** = 1183 + **12 nuevos, 0 perdidos** (conciliación por nodeids) | `logs/11` |
| Focal del archivo modificado | 110 passed | `logs/12` |
| Selección L2 histórica + nuevos (139 nodeids: 110 schema + 28 PA02/PA03 + PA01-unicode) | 139 passed | `logs/13` |
| Selección ampliada de campaña (111) — ORIGINAL | 111 passed | `logs/03-microcampana.json` |
| Microcampaña 33 IDs | 33/33 ROJO-ATRIBUIDO | `logs/03` + `logs/micro/` |
| Suite normativa (`-m "not property"`) | **1194 passed, 0 failed** | `logs/17` |
| Property separada (`-m property`) | 1 passed | `logs/15` |
| `wct gate --tier fast` | **7 PASS · 0 SKIP · 0 FAIL** (incl. G-SUPPRESS/ratchets) | `logs/18` |
| `wct gate --tier commit` | **20 PASS · 1 FAIL: G-META-1** por `governance/lint/vulture_whitelist.py` | `logs/19` |

- Los **7 fallos** de la primera pasada de la suite normativa
  (`logs/14`) fueron **artefacto de PATH de la invocación** (subprocesos sin
  el bin del venv: `ruff`/`semgrep` no hallados); reproducidos idénticos en
  el árbol prístino (stash, `logs/16`) y en verde con PATH correcto
  (79/79 y luego 1194). No son del candidato.
- **G-META-1 FAIL es el drift preexistente del propio PR**: el commit
  REANCLAJE-5 (ea0b75a) editó la whitelist vulture (hash actual a2877ee8… vs
  integrity.lock 90e52d7f…) sin re-bless; este encargo no tocó gobernanza.
  Se declara (criterio de cierre del encargo); su regularización (revisión
  tipo E9 + bless) sigue siendo puerta humana al fusionar.
- **Presupuestos** (guardián monotónico, ledger `logs/02`, dos sobres sin
  transferencia): experimental **326.42 / 600 s** (autor 308.81 de 480 + 2
  rechazos fail-closed previos a lanzamiento + verifier 17.61 de su reserva
  de 120; incluye 1 intento instrumental inválido de 0.03 s en int);
  integración **411.98 / 900 s**. Margen de cleanup respetado; ningún hijo
  llegó al timeout; solo procesos propios.
- **Dictamen del verifier independiente** (agente distinto del autor, copia
  propia desechable, ledger y hashes propios en `verifier/`): **FAVORABLE** —
  fidelidad 12/12 (citas §2/§3/§4, aserciones exactas, cero mocks, +144/−0,
  colección reproducida), sensibilidad 6/6 sondas en 5 grupos con 2 fronteras
  y selección ampliada (cb_12: fallan AMBOS tests), negativo cwd_5 ausente
  del conjunto, evidencia del autor íntegra. 2 hallazgos menores de
  etiquetado incorporados (§10 nota). No ratifica equivalencias ni declara L2
  cerrado. Informe: `verifier/INFORME-VERIFIER.md`.

## 10. Sellado y publicación

- Workspace del expediente: `build/tmp/reanclaje9-20260918/`
  (`repo/`, `mutants/`, `logs/`, `sondas.py`, `guardian.py`, `verifier/`).
- Manifiesto `MANIFIESTO-REANCLAJE9.sha256` sin auto-hash; digest y
  verificación fuera de sus miembros. Históricos R5–R8 intactos.
- Publicación en PR #56 (borrador): diff exacto =
  `tests/unit/test_pytest_schema.py` (+144) y este registro. Commits
  convencionales con byline; hooks activos, sin bypass ni force push; push
  normal a `codex/reanclaje-p03a-fase1`; CI observado con seguimiento
  acotado (resultado en la entrega del turno).
- Nota de etiquetado (hallazgo 5 del verifier): «selección L2 ampliada»
  (139 nodeids, `logs/13`) y «selección ampliada de campaña» (111 nodeids,
  usada por sondas/microcampaña) son selecciones distintas; el registro las
  nombra así desde esta sección.

## 11. Siguiente decisión mínima

Decidir **D-C residual → campaña completa re-ejecutada**: una vez ratificadas
o rechazadas las 10 equivalencias (D-A) y dispuestos los 2 no contratados
(D-B), la siguiente acción mínima es re-ejecutar la campaña L2 de 278 con la
selección ampliada (111) para convertir esta evidencia sucesora en bruto
nuevo (o mantener los brutos separados por diseño). Alternativa más pequeña:
implementar el oráculo independiente de WIRE_FIELDS (§7) bajo D-D. Nada de
eso se ejecuta aquí: este encargo se detiene tras publicar y verificar.
