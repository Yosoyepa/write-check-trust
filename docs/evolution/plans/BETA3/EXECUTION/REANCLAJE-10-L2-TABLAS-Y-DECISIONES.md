# Registro REANCLAJE-10 — comprobación contractual de WIRE_FIELDS y expediente de decisiones L2 (2026-09-18)

Estado: **tabla WIRE_FIELDS verificada con oráculo independiente transcrita
del contrato + control de consumo posicional (4/4 perturbaciones rojas con
original verde)**; **expediente decisorio completo para las 10 equivalencias
y los 2 comportamientos no contratados** (nadie ratifica aquí); **selección
futura de L2 congelada** (141 nodeids, baseline verde) y receta definida.
Sin campaña de 278, sin cambios de producto, contratos, gobernanza ni
configuración. Bruto histórico intacto: 278 = 233 + 45.

## 1. Base, identidades y verificación del expediente anterior

| Elemento | Identidad | Comprobación |
|---|---|---|
| Base | `c26aa172fffecfe95f05285122ab6452f1d4a21e` = origin `codex/reanclaje-p03a-fase1` = headRefOid PR #56 (borrador, OPEN) | `git ls-remote` + `gh pr view 56` al inicio y revalidado antes de publicar |
| main / baseRefOid / merge-base | main `8a379d64…` = baseRefOid = merge-base (PR descendiente limpio de main; sin avance material) | `git ls-remote` + `git merge-base` |
| Sello R9 | `MANIFIESTO-REANCLAJE9.sha256` en `build/tmp/reanclaje9-20260918/`, digest **exacto** `eb61f1db…`, 75/75 miembros OK | `sha256sum -c` (ubicación resuelta desde el propio registro R9 §10) |
| Fuentes históricas usadas | R7 logs/02/09/15/16 (sellados en manifiesto R7 `4687309f…`), R8 §5 (registro versionado en la base), contrato P03 `47429b88…` (copia congelada re-hashada), sello R8 de fuentes `93acd1a5…` | verificaciones de este encargo |
| Copia de trabajo | `build/tmp/reanclaje10-20260918/` (raíz Git propia en `repo/`, venv propio `uv sync --all-groups`) | aislamiento acreditado |

Las 4 fuentes wire en c26aa17 siguen byte-idénticas al sello (`63e25807…`,
`35e74471…`, `8977f5b4…`, `a6261613…`): el commit R9 solo tocó tests y docs.

## 2. Nota sucesora — precisiones al expediente R9 (sin tocar sellado)

### 2.A Selecciones de 111 y 139 nodeids

Derivadas de sus artefactos (`sondas.py::SELECTION` + `logs/03-microcampana.json`
de R9; `logs/02-nodeids-pa0203.txt` de R7 + `logs/13` de R9). Derivación
completa en `logs/14-precision-selecciones.txt`:

- **111 (campaña/sondas R9)** = `tests/unit/test_pytest_schema.py` completo
  (110 = 98 históricos + 12 oráculos R9) + PA01-unicode. Propósito:
  **atribución de rojo por mutante** (sensibilidad por ID); no incluía los 28
  PA02/PA03 porque no eran necesarios para atribuir los 33 rojos.
- **139 (batería R9, logs/13)** = 110 schema + **28 PA02/PA03** + PA01-unicode.
  Propósito: **batería verde** que demuestra selección histórica L2 ∪ oráculos
  nuevos ∪ PA01-unicode en verde sobre el original.
- **Álgebra**: 139 \ 111 = los 28 PA02/PA03; 111 \ 139 = ∅; es decir
  **139 = 111 ∪ 28**. No son iguales ni debían serlo. Cubrimiento: tests
  históricos de selección → solo la 139; tests nuevos → ambas (archivo
  completo); PA01-unicode → ambas.

### 2.B Árbol instrumentado: igualdad, anclaje y procedencia

- **Igualdad entre copias**: la copia `mutants/` de R9 era byte-idéntica al
  árbol in situ de R7 (321 archivos por hash). Esto acredita **igualdad**,
  no procedencia histórica independiente.
- **Anclaje**: el inventario sellado (R7 logs/09: 278 IDs) y el snapshot de
  stats pre-campaña sellado (logs/08) anclan el CONTENIDO esperado del árbol;
  el `mutmut-stats.json` in situ difiere del snapshot sellado por las
  asociaciones que la campaña escribió después — consistente con la
  narrativa R7, pero es consistencia, no prueba criptográfica.
- **Qué estaba sellado**: solo los miembros de los manifiestos R7/R8
  (ENTREGA, logs, lanzador). El árbol `run/mutants/` **nunca fue sellado
  como árbol**; se conservó in situ. La frase «miembros sellados» de R8 §1
  sobre los `.meta`/stats es imprecisa y así quedó registrado en R9 §1.
- **Límite no resoluble**: no se puede probar criptográficamente que el
  árbol in situ es el exactamente usado en la campaña R7 (nadie selló el
  árbol antes de la campaña). No se fabrica procedencia: para la campaña
  futura **se generará un árbol nuevo sobre el candidato final** (§7), que
  no necesita procedencia histórica; el 278 histórico queda como referencia
  a reconciliar, no como imposición.

### 2.C CI del commit R9 (run 35419254995, c26aa17)

El job `commit-gates` ejecutó su paso «Verify generated policy and control
-plane integrity» y **falló ahí** por el drift preexistente del propio PR;
los pasos mecánicos posteriores del job quedaron **SKIPPED** como
consecuencia del fallo (semántica normal de workflow, idéntica en el run de
eb8f2ea 35416955687): esos son los únicos **pasos reales del workflow no
ejecutados**, y lo fueron por fallo, no por omisión. **Bless** (actualizar
integrity.lock) y **merge** son operaciones humanas fuera del job: no son
pasos omitidos del workflow ni se registran como tales. Drift exacto
(`wct integrity check`, `logs/13`): **34 «nuevo protegido»** —rutas del
kernel R8/operador ausentes del lock— **+ 2 «modificado»** —
`vulture_whitelist.py` y `mutation_cases.py` con hash pre-edición en el
lock—. El resultado del run es FAILURE por diseño del gate ante drift
protegido — se cita sin reinterpretar. La misma causa falla en todos los
runs del PR desde 2dbc509.

## 3. Reconciliación de los doce residuos

45 survived = **33** con sensibilidad sucesora (R9, 33/33 rojos atribuidos) +
**10** equivalencias propuestas + **2** no contratados. IDs completos,
funciones y diffs extraídos de la evidencia (R7 logs/15/16, sellados) — no de
números abreviados: `logs/01-diffs-residuos.txt`. Hashes de fuente:
composites `8977f5b4…`, framing `a6261613…` (byte-idénticos al sello R8).

## 4. Tabla decisoria — las diez equivalencias (NINGUNA ratificada aquí)

Leyenda por mecanismo. «Sonda R8» = sonda fresca R8 sin divergencia
(experimento, no prueba); «verificado R10» = hecho estructural re-verificado
en la base de este encargo (no lectura de R8).

### 4.1 Subsumción por checks posteriores (composites; fuente `8977f5b4…`)

| ID | Diff | Cadena subsumida |
|---|---|---|
| `…pytest_wire_composites.x__cwd__mutmut_5` | `_s(value, min_len=1)` → `_s(value, )` | `""` ya rechazado por `not text.startswith("/")` (§3: cwd absoluto POSIX) |
| `…x__utc__mutmut_5` | ídem en `_utc` | `""` ya rechazado por `_UTC_RE.fullmatch` (formato de 32 chars) |
| `…x__utc__mutmut_6` | `min_len=1` → `2` | toda cadena de 1 char ya falla el regex de 32 chars exactos |

- **Comportamiento contractual**: §3 l.209 (cwd) y l.230-233 (utc exige
  formato exacto, stdlib). **Dominio/precondiciones**: entradas `str` del
  wire (no-str ya rechazado por el type-check de `_s`).
- **Razonamiento estructural**: `min_len` solo puede divergir en cadenas de
  longitud 0 (cwd_5/utc_5) o 1 (utc_6); en ambos casos el check contractual
  posterior rechaza esas cadenas con el mismo `invalid_field` (subsumido).
- **Experimental**: sondas R8 sin divergencia (dominio str). **Consumidores**:
  builders execution_start/execution_end vía `decode_events`.
- **Contraejemplos**: ninguno dentro del dominio; fuera (no-str) no aplica.
- **Invalidantes**: reordenar `_cwd`/`_utc` (check contractual antes del
  tamaño) o relajar el formato absoluto/regex.
- **Ratificación propuesta (texto exacto)**:
  «`x__cwd__mutmut_5`, `x__utc__mutmut_5` y `x__utc__mutmut_6` son
  equivalentes en el dominio wire de entradas str: la obligación contractual
  posterior (cwd absoluto POSIX; utc con formato exacto de 32 caracteres)
  rechaza con invalid_field exactamente las cadenas cortas que el min_len
  original excluía, subsumiendo la mutación.»

### 4.2 Parámetros falsy de stdlib json (framing; fuente `a6261613…`)

| ID | Diff | Mecanismo |
|---|---|---|
| `…pytest_wire_framing.x_canonical_bytes__mutmut_3` | `ensure_ascii=False` → `None` | `None` es falsy: `json.dumps` lo trata como `False` (verificado R10: salidas idénticas) |
| `…x_canonical_bytes__mutmut_6` | `allow_nan=False` → `None` | `None` falsy ≡ `False`: `dumps(nan)` sigue raisiendo `ValueError` (verificado R10) |

- **Dominio**: stdlib json de CPython (semántica de truthiness de parámetros).
  **Nota**: cb_6 es equivalente **estructuralmente independiente de la
  alcanzabilidad de NaN** (a diferencia de cb_11/16, §4.3).
- **Invalidantes**: una implementación json que distinga `None` de `False`.
- **Ratificación propuesta**:
  «`x_canonical_bytes__mutmut_3` y `x_canonical_bytes__mutmut_6` son
  equivalentes bajo la stdlib json de CPython: `ensure_ascii=None` y
  `allow_nan=None` se evalúan falsy y producen byte a byte la misma
  serialización que `False`.»

### 4.3 allow_nan inalcanzable por los callers actuales (framing)

| ID | Diff | Mecanismo |
|---|---|---|
| `…x_canonical_bytes__mutmut_11` | `allow_nan=False` removido (default `True`) | con `True`, `dumps(nan)` serializaría `NaN` en vez de raisear |
| `…x_canonical_bytes__mutmut_16` | `allow_nan=False` → `True` | ídem |

- **Comportamiento contractual**: §3 l.134-135 «JSON canónico… No
  floats/NaN»; §2 l.106. **Dominio/precondiciones**: los DOS únicos callers
  (grep R10): `canonical_header` (datos de `ExecutionExpectation` ya
  validados por el API público: digests lowerhex64, strings; sin floats) y
  `_parse_line` (el valor pasó por `_loads` con `parse_constant=
  reject_constant`: NaN/Infinity nunca sobreviven). NaN es **inalcanzable**
  en ambos.
- **Experimental**: sondas R8 sin divergencia. **Consumidores**: cadena
  header/decode completa. **Contraejemplo**: un caller FUTURO que pase
  `float("nan")` directo a `canonical_bytes` diverge (serializa en vez de
  raisear) — límite declarado del dominio «callers actuales».
- **Invalidantes**: nuevo caller sin validación previa; relajar
  `parse_constant` en `_loads`.
- **Ratificación propuesta**:
  «`x_canonical_bytes__mutmut_11` y `x_canonical_bytes__mutmut_16` son
  equivalentes en el dominio de los callers actuales de `canonical_bytes`
  (canonical_header y _parse_line): NaN/Infinity no pueden alcanzar la
  serialización canónica porque el API público valida digests y `_loads`
  rechaza constantes antes. El dominio excluye callers futuros no validados.»

### 4.4 Alias de codec utf-8/UTF-8 (framing)

| ID | Diff | Sitio |
|---|---|---|
| `…x_canonical_bytes__mutmut_18` | `.encode("utf-8")` → `"UTF-8"` | serialización canónica |
| `…x__parse_line__mutmut_4` | `raw.decode("utf-8")` → `"UTF-8"` | decodificación de línea |
| `…x__line_defect__mutmut_7` | `line.decode("utf-8")` → `"UTF-8"` | precedencia de línea |

- **Razonamiento estructural**: `codecs.lookup` es case-insensitive;
  `codecs.lookup("utf-8") is codecs.lookup("UTF-8")` (verificado R10 en la
  base). Mismo codec, mismos bytes de entrada/salida y mismas excepciones.
- **Dominio**: registro de codecs de CPython. **Contraejemplos**: ninguno en
  Python. **Invalidantes**: manipulación exótica del registro de codecs
  (fuera del runtime del proyecto).
- **Ratificación propuesta**:
  «`x_canonical_bytes__mutmut_18`, `x__parse_line__mutmut_4` y
  `x__line_defect__mutmut_7` son equivalentes: "utf-8" y "UTF-8" resuelven
  al mismo codec en el registro de CPython (búsqueda case-insensitive), con
  idéntico comportamiento de decodificación, codificación y excepciones.»

Cada fila es decidible por ID o por grupo homogéneo; las ratificaciones
quedan **propuestas, no aprobadas** (decisión humana D-A).

## 5. Los dos comportamientos no contratados de `_DefectError` (fuente `a6261613…`)

Distinción previa: `_DefectError` es **canal interno** del decoder (§2 l.50:
el decoder no lanza por contenido malformado — convierte a findings); los
catchers (`decode_events.py:169`, `schema.py:57`, `framing.py:85`) consumen
`.code` y `.execution_id`, **nunca el mensaje**.

### 5.1 `xǁ_DefectErrorǁ__init____mutmut_1` — `super().__init__(code)` → `(None)` (mensaje)

- **Lectores del mensaje**: cero en `tools/` (grep R10 re-verificado: ningún
  `str(exc)`/`.args` sobre `_DefectError`; los existentes son de otras
  excepciones). **Observable por API pública**: ninguno — el finding lleva
  `code` (intacto).
- **Obligación contractual aplicable**: no existe para el mensaje de un canal
  interno; §4 define findings como datos.
- **Clasificación propuesta: B** (comportamiento no contratado). Opciones:
  (1) **preservar** como superficie interna sin efecto externo
  (recomendado; con nota: cualquier lector futuro del mensaje exigirá
  oráculo propio); (2) contratar el mensaje (no recomendado: añadiría
  contrato a un canal interno); (3) excepción puntual vía el mecanismo real
  aplicable — el registro de equivalencias/excepciones del expediente de
  mutación con aprobación humana explícita, alcance: «mensaje de
  _DefectError no observable por API pública; cero lectores».
- **No es equivalencia** (la superficie existe y es medible internamente) y
  **no se excluye del denominador** hasta decisión.

### 5.2 `xǁ_DefectErrorǁ__init____mutmut_3` — `self.execution_id = execution_id` → `None`

- **Lectores**: SÍ existen — `pytest_decode_events.py:125,127` construyen
  con atribución y `:140` lee `defect.execution_id` hacia
  `ProtocolFinding.execution_id` (campo contractual §2 l.67: `str o None`).
- **Dominio alcanzable hoy**: los raises con atribución ocurren solo en
  `_execution_index`, y `_attributed_execution` retorna `None` exactamente
  en los caminos que llegan al raise (no-int → None; fuera de rango →
  None). **Verificado empíricamente en R10** (sonda: ex=7 →
  `foreign_reference` con `execution_id=None`; ex="x" y ex=True →
  `invalid_field` con `None`; `logs/05-sonda-defecterror3.txt`).
- **Diferencia observable**: hoy ninguna vía API pública; un raise futuro
  con atribución no-None haría el mutante visible (finding sin la
  atribución esperada).
- **Obligación contractual aplicable**: §4 exige offset y código para
  findings de línea; **no** exige atribución de execution_id. No hay
  obligación vigente incumplida → no es A.
- **Clasificación propuesta: B**. Opciones: (1) **preservar** documentando
  que la atribución existe como estructura pero su valor es None en todos
  los caminos actuales (recomendado); (2) **contratar** la atribución
  («cuando el defecto de execution_index sea atribuible, el finding lleva
  ese execution_id») — exigiría oráculo nuevo y posiblemente tocar el
  dominio del raise, fuera de este encargo; (3) excepción puntual (mecanismo
  y alcance como en 5.1).
- **C (inconcluso): ningún caso** — ambos residuos tienen evidencia completa
  para decidir.

## 6. WIRE_FIELDS: oráculo independiente y consumo (implementado)

Allowlist ejecutado: SOLO `tests/unit/test_pytest_schema.py`
(`8eef7362…` → `e7d82c99…`, +84 líneas, 0 retiradas; corrección H-1 del verifier).

1. **Confirmación contra el contrato**: 21 clases / 59 strings confirmados
   contra la tabla §3 (l.206-228) + transformación de execution_start
   (l.167: viaja sin role ni digests). El literal del test
   (`CONTRACT_WIRE_FIELDS`) se transcribió del TEXTO contractual: no lee
   `WIRE_FIELDS`, dataclasses, builders ni funciones productivas.
2. **`test_wire_fields_table_is_the_contract_transcription`** — verifica
   inventario exacto de clases (igualdad de conjuntos de nombres) y tupla
   completa por clase (la igualdad detecta omisión, extra, sustitución y
   orden en una aserción por clase).
3. **`test_wire_decoder_binds_payload_positions_to_contract_fields`** —
   consumo: evento `session_end` con vector `[3, 7]` (valores
   distinguibles elegidos independientemente) decodificado por la API
   pública → `argument_exit == 3`, `observed_exit == 7`. Demuestra que el
   decoder **consume** posiciones (no que la tabla sea correcta).
4. **Perturbaciones (copia desechable `copia-perturbacion/`, identidad por
   hash y diff exacto en `logs/02-perturbaciones.txt`)** — ORIGINAL verde y
   4/4 rojas:
   - P1 omisión (`ExecutionEnd` sin `utc`): tabla roja, consumo verde →
     demuestra **contenido** de tabla.
   - P2 adición (`ChannelEnd` + `reintentos`): tabla roja, consumo verde →
     **contenido**.
   - P3 sustitución (`PluginClaim` `module`→`modulo`): tabla roja, consumo
     verde → **contenido**.
   - P4 permutación (`SessionEnd` invertido): tabla **y** consumo rojas →
     la misma perturbación es visible por DOS mecanismos distintos
     (igualdad literal vs comportamiento del decoder); se registran como
     pruebas **no equivalentes**.
5. Los **5 docstrings** (4 de módulo + `DefectError`) quedan documentados
   como contenido sin efecto conductual identificado (limitación
   instrumental declarada, sin dispensa y sin mutantes inventados).

## 7. Selección congelada para la futura campaña L2

- **Lista**: `logs/03-seleccion-futura-L2.nodeids` — **141 nodeids únicos**
  (112 de `test_pytest_schema.py` completo = 98 históricos + 12 de R9 + 2 de
  R10; 28 PA02/PA03 de R7; PA01-unicode). 0 duplicados; todos coleccionan.
- **Digest** (sha256 de la lista): `e8dcdff18e4ba85d742f401a3f88ec5454188e721cbcd63da3de80d1b5c65c17`.
- **Baseline**: 141 passed, exit 0, sin skips/xfails (2.91 s; property fuera).
- **Archivos**: `tests/unit/test_pytest_schema.py` (`e7d82c99…`),
  `tests/unit/test_pytest_observation.py` (hash en
  `logs/15-hashes-seleccion.txt`). **Runtime**: venv propio
  (`uv sync --all-groups`; Python 3.13.14, pytest 9.1.1, mutmut 3.7.0).
- **Fuentes** (candidato): las 4 wire, hashes sellados ídem §1.
- **Receta prevista** (heredera R7, sobre el candidato FINAL tras
  decisiones): pyproject experimental con `source_paths` = las 4 wire y
  selección congelada como `pytest_add_cli_args_test_selection`;
  **generación pura** (`mutmut run ZZ_…_NO_MATCH`, assert antes de todo
  test); campaña serial con IDs explícitos bajo `timeout` guardián;
  lanzador fail-closed (ID ∈ inventario generado, hashes de fuentes contra
  sello del candidato, `MUTANT_UNDER_TEST` re-asignado, `PYTHONPATH` a la
  copia instrumentada); **canario** `x__u__mutmut_1` (38 failed con causa
  `invalid_field`≠`limit_exceeded`) + negativos del lanzador;
  **asociaciones** por `tests_by_mangled_function_name` del stats (no vacías).
- **Inventario**: el 278 histórico es **referencia a reconciliar** (por
  conjuntos, diff por ID), no un número que imponerse: la nueva generación
  sobre el candidato final puede diferir y toda diferencia debe atribuirse
  causalmente. **No se genera ni ejecuta nada de esto en este encargo.**

## 8. Presupuestos (guardián monotónico, ledger `logs/02-ledger-guardian.csv`)

- **Experimental**: 9.51 / 600 s — perturbaciones 5×≈0.6 s + ORIGINAL×3
  (controles repetidos por corrección de un bug de desempaque en el driver,
  declarado) + colecta/baseline de selección 4.1 s + sonda _DefectError_3
  0.21 s + corridas manuales registradas. **Reserva verifier 120 s intacta**
  hasta su ejecución (§9).
- **Integración**: 316.6 / 900 s — colecciones 2×, focal, normativa 145.7 s,
  property, fast 5.2 s, commit 156.7 s.
- Sin transferencia entre sobres; timeouts por hijo ≤ saldo−5 s; solo
  procesos propios; intentos inválidos contabilizados (bug del driver:
  2 lanzamientos ORIGINAL con salida no desempaquetada — las corridas SÍ
  ocurrieron y constan en el ledger).

## 9. Dictamen del verifier independiente

Agente distinto del autor, sin escritura en el workspace del autor ni en
evidencia sellada; reprodujo en copia propia (clon a c26aa17, hashes
coincidentes) con ledger propio. **DICTAMEN: FAVORABLE** — 21/21 tuplas del
literal contrastadas campo a campo contra el contrato (independencia
acreditada); ORIGINAL verde + 2 perturbaciones reproducidas (V1 omisión de
otro campo: tabla roja/consumo verde; V2 permutación: ambas rojas, hash de
fuente perturbada byte-idéntico al del autor) + control negativo (docstring:
ambos tests siguen verdes — inercia correcta); digest de la selección
recalculado; álgebra 139 = 111 ∪ 28 y partición 45 = 33 + 10 + 2 por
conjuntos; hechos estructurales de las 10 equivalencias re-verificados en
Python puro; lectores de _DefectError exactos; CI contrastada en ambos runs.
Cuatro hallazgos MENORES/OBSERVACIONES, ninguno bloqueante: H-1 (+95→+84,
corregido en §6/§11), H-2 (skips mecánicos del job, corregido en §2.C),
H-3/H-4 (exit code implícito en logs/04; un nodeid con espacio literal —
parámetro preexistente ` \n-` — colecciona y pasa en el baseline; sin
acción). Consumo: ~15 s de la reserva de 120 s. Informe:
`verifier/INFORME-VERIFIER.md`. Su dictamen aprueba expediente y tests;
**no** concede ratificaciones humanas ni declara L2 cerrado.

## 10. Verificación del compuesto

| Comprobación | Resultado | Evidencia |
|---|---|---|
| Colección baseline (c26aa17 prístino) | 1195 | `logs/06` |
| Colección modificada | **1197** (+2, 0 perdidos, conciliación por nodeids) | `logs/07` |
| Focal del archivo modificado | 112 passed | `logs/08` |
| Selección L2 futura (141) | 141 passed, exit 0, sin skips | `logs/04` |
| Suite normativa | **1196 passed, 0 failed** (PATH del venv) | `logs/09` |
| Property separada | 1 passed | `logs/10` |
| `wct gate --tier fast` | 7 PASS · 0 FAIL | `logs/11` |
| `wct gate --tier commit` | 20 PASS · 1 FAIL: **G-META-1 preexistente** | `logs/12`, detalle `logs/13` |

G-META-1 declarado: drift protegido preexistente del propio PR (34 «nuevo
protegido» + 2 «modificado», §2.C) — su regularización es bless humano al
fusionar, fuera de alcance. Ningún rojo nuevo introducido por el candidato.

## 11. Sellado y publicación

Expediente `build/tmp/reanclaje10-20260918/`: `MANIFIESTO-REANCLAJE10.sha256`
sin auto-hash, digest y verificación fuera de sus miembros; históricos
R5–R9 intactos. Publicación en PR #56 (borrador): diff exacto = el test
autorizado (+84) y este registro; commit convencional con byline; hooks sin
bypass; push normal; CI observada con seguimiento acotado (§ entrega).

## 12. Decisiones humanas exactas (pendientes)

- **D-A (10)**: ratificar o rechazar cada equivalencia de §4 — decidible por
  ID o por grupo homogéneo (4.1 subsumción ×3; 4.2 falsy ×2; 4.3 allow_nan
  inalcanzable ×2; 4.4 alias codec ×3). Textos de ratificación propuestos in situ.
- **D-B (2)**: disponer §5.1 (mensaje) y §5.2 (execution_id) entre
  preservar / contratar / excepción puntual (mecanismo y alcance citados).
- **D-Campaña**: autorizar la campaña completa L2 con la selección congelada
  (§7) y el prompt de §13, una vez decididas D-A/D-B.

## 13. Prompt propuesto para la campaña final L2 — NO EJECUTAR SIN AUTORIZACIÓN

> **Encargo CAMPAÑA-L2-FINAL — re-campaña completa de mutación del lote L2
> con selección congelada.**
>
> **Base exacta**: el headRefOid de PR #56 vigente al arrancar, que debe
> incluir los commits R9/R10 y las decisiones D-A/D-B registradas (sus
> actas). Si el remoto avanzó, reancla identidad antes de empezar.
>
> **Objetivo conductual**: generar el árbol instrumentado NUEVO sobre el
> candidato final (4 módulos wire, hashes contra sello del candidato) y
> ejecutar TODOS los mutantes del inventario generado contra la **selección
> congelada de 141 nodeids** (digest `e8dcdff1…`; lista
> `logs/03-seleccion-futura-L2.nodeids` de REANCLAJE-10), bajo la receta §7
> (generación pura, canario `x__u__mutmut_1` con causa, negativos del
> lanzador, asociaciones no vacías, guardián de presupuesto monotónico).
>
> **Métricas separadas de forma inviolable**: (1) **bruto histórico**
> 278 = 233 + 45 se conserva y cita SIN reescribir; (2) el **resultado
> nuevo** se reporta como expediente propio. **Prohibido sumar** 233
> históricos + kills nuevos como una sola campaña: son corridas distintas
> con selecciones distintas.
>
> **Reconciliación de inventario obligatoria**: comparar por conjuntos el
> inventario generado vs el histórico 278; toda diferencia (IDs nuevos,
> ausentes, renombrados) se **atribuye causalmente** (diff del fuente,
> versión de mutmut, cambio de candidato) antes de ejecutar; nunca se
> ejecuta un subconjunto sin explicar el resto.
>
> **Atribución de anomalías**: toda transición inesperada (un killed
> histórico que sobrevive, un survived histórico que muere, un ID nuevo)
> exige sonda individual con causa contractual antes de contarse; los
> survived del resultado nuevo se adjudican con el método R8 (hueco /
> equivalencia propuesta / no contratado) SIN ratificar nada.
>
> **Presupuestos**: definir sobres explícitos (generación, campaña,
> sondas, verifier) con guardián monotónico; sin transferencias; reserva
> para verifier.
>
> **Prohibido**: ratificar equivalencias (puerta D-A ya resuelta o
> pendiente, pero no en la campaña), cambiar producto/tests/contratos,
> bless, merge, tag, release. Entrega: bruto nuevo, reconciliación,
> atribuciones por ID, dictamen del verifier, manifiesto sellado.
