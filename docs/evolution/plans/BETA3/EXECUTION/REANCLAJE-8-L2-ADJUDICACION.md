# Registro REANCLAJE-8 — adjudicación técnica de los 45 sobrevivientes L2 y delimitación de los sitios no instrumentados (2026-09-18)

Estado: **clasificación técnica sustentada por ID** con sondas causales
acotadas y propuestas mínimas de oráculos. Sin equivalencias definitivas,
excepciones, contratos nuevos, reparaciones, otra campaña ni avance a L4.
El bruto histórico se conserva: **278 = 233 killed + 45 survived**.

## 1. Identidades

- Base documental: `21c0166de155294a121e637a065f745053dc2811` (= origin =
  headRefOid PR #56, borrador). **Corte técnico de L2:**
  `8b8868ac0420f0aa7b2f442129c3d8b9bfb4de72`. Delta documental entre ambos
  = exactamente el registro REANCLAJE-7 (+166 líneas docs): **no cambia
  fuentes, tests, receta ni premisas** — sin drift material. main
  `8a379d64…` y tag intactos.
- Expediente R7 verificado: digest comunicado
  `4687309f8148a83778675346d2e32636f4e200d4f30f8724ef5e38579ba87766` =
  sha256 del manifiesto; 26/26 miembros sellados OK; árbol instrumentado
  `run/mutants/` (4 .meta + stats) **disponible in situ** — los .meta y el
  snapshot son miembros sellados del expediente por sus hashes; el árbol
  mutants/ es artefacto conservado in situ (distingo explícito). No se
  regeneró ningún mutante.

## 2. Desviación de presupuesto histórica (registrada, sin reescribir)

Sobre de sondas R7 autorizado **300 s**; consumo comunicado **~390 s**
(exceso **~90 s**). Recalculo con registros: loop 45 sondas = 367.2 s
(medido), sonda manual 8.06 s, canario/negativos ~15 s **sin numeración
wall (incertidumbre ±5 s declarada)**. Agregado R7 ~645/2520 s dentro del
techo, **sin autorización de transferencia**. La validez técnica de la
evidencia (dictámenes FAVORABLE) y la conformidad presupuestaria son
cuestiones distintas: **el dictamen no regulariza el exceso**, y este
encargo NO es autorización retroactiva. La evidencia técnicamente válida
no se repitió por la desviación.

## 3. Reconciliación de los 45 (desde el bruto)

Derivados de los 4 `.meta` (exit_code==0): **45 IDs únicos**, todos
pertenecientes al inventario de 278, **igualdad exacta por conjuntos** con
los survived históricos (logs/14 de R7) y con la lista transcrita
(logs/15). Diffs reales por ID: logs/16 de R7 (43/45 de una línea física;
2 con reflujo de formato). Función y fuente por ID: en la tabla §5.
Evidencia por ID separada en: **A** resultado de campaña (exit 0 sobre
conjunto asociado completo); **B** activación disponible (trampoline
MUTANT_UNDER_TEST, arnés acreditado en R7); **C** reproducción fresca
(este encargo: sonda propia por ID discriminante — ver §4); **D**
suficiencia (campaña + sonda); **E** adjudicación técnica propuesta (§5).

## 4. Sondas acotadas ejecutadas (guardián monotónico)

Presupuesto experimental **600 s** con reserva explícita de **120 s** para
el verifier; guardián `guardian.py` (reloj monotónico, rechazo con saldo
<30 s, límite por hijo min(saldo,60 s), ledger CSV, kill solo de procesos
propios), probado con control barato antes de usar (import resuelto en
mutants/, 0.54 s). Arnés `probe_payload.py` (bajo build/tmp, no versionado):
30 casos de frontera contra `_parse_line`/`_BUILDERS` del árbol
instrumentado. **Control ORIGINAL verde** antes de cada familia (26-30
hechos base en logs/sonda-ORIGINAL*). Canario de activación re-verificado
(`x__u__mutmut_1` diverge: argv_one_char ok→invalid_field).

**Intento inválido declarado**: un primer lote de 36 sondas (corrige el
«37» inicial; filas 5-40 del ledger) corrió SIN activación real — con
`python script.py`, sys.path[0] es el directorio del script y `tools.wct`
resolvía al editable original (sin trampolines); detectado por divergencia
cero + verificación directa, corregido fijando `PYTHONPATH=mutants` en el
guardián, y rehecho completo. Coste del lote inválido ~3.2 s
(contabilizado). Nota de superficie del arnés (hallazgo 6 del verifier):
43/45 sondas se capturaron con la versión de 29 casos del arnés; los casos
`opt_h_*` (31) llegaron después (solo loads_30, opt_h_2 y el ORIGINAL
final los tienen); todas las divergencias declaradas ocurren en casos
comunes a ambas versiones. **46 sondas válidas** ejecutadas, **~40 s de
hijos + ~20 s de drivers ≈ 60 s** de los 480 s del sobre de sondas; 120 s
reservados intactos para el verifier. Un fallo instrumental no cuenta como
discriminación: las 2 clases de fallo encontradas (lote sin activación;
etiqueta "ok" del guardián que agrupa exit 0/1) fueron declaradas y
corregidas con recaptura.

**Hecho decisivo adicional**: el test existente
`test_observation_case[PA01-unicode-byte-offsets]` (familia PA01, fuera de
la selección L2) **falla bajo `canonical_bytes__mutmut_12`** — salida
textual conservada aquí por evidencia (filas 87-89 del ledger: ORIGINAL
pasa; cb12 → `1 failed in 0.89s`, `AssertionError: assert (ProtocolFind...
offset=860),) == ()` en `test_pytest_observation.py:2749`; recaptura
completa a demanda) — el oráculo YA EXISTE en la suite R8; el hueco de
cb_8/cb_12 es de la **selección de campaña**, no de la suite.

## 5. Clasificación técnica por ID

Leyenda de evidencia: S = sonda fresca de este encargo (divergencia
observada entre ORIGINAL y mutante en el mismo arnés); C = campaña R7
(exit 0, conjunto asociado); E = razonamiento estructural delimitado.
Contrato citado: §3/§4 de PROPUESTA-P03 (`47429b88…`, congelado).

### 5.1 HUECO-DE-ORÁCULO BAJO CONTRATO VIGENTE — 33 IDs

| IDs | Mutación | Contrato/cita | Entrada → efecto bajo mutante | Consumidor real | Evidencia |
|---|---|---|---|---|---|
| composites.x__argv__mutmut_12/13 | `min_len=1` → removido / `2` en items | §3 ExecutionStart «argv: tupla no vacía de S no vacíos» | `["x",""]` aceptada / `["x"]` rechazada | builders `_build_execution_start` → decode_events | S |
| composites.x__cwd__mutmut_6 | `min_len=2` | §3 «cwd: S absoluto POSIX…» | `cwd="/"` (1 char válido) rechazado | ídem | S |
| composites.x__cwd__mutmut_15 | `"." in parts` → `"XX.XX" in parts` | §3 «sin componentes . o ..» | `/a/./b` aceptado | ídem | S |
| composites.x__exception_type__mutmut_2/3/5/6 | `name→None` / `min_len=None` / removido / `2` | §3 PhaseMake «exception_type:S no vacío o N» con coherencia present/name | nombre válido rechazado / TypeError crash / `""` aceptado / 1-char rechazado | builders `_build_phase_make` | S |
| framing.x__check_strings__mutmut_2 | `_check_strings(item)` → `(None)` | §2 «strings representables en UTF-8 estricto, sin surrogate, C0/DEL» (l.97-98; §3/§4 lo implican vía canonicidad y vocabulario invalid_encoding) | `["\u0001"]` aceptado (items de lista sin revisar) | `_parse_line` → decode | S |
| framing.x__depth__mutmut_5/7/13 | hoja `0→1` / `1+→2+` / `default 0→1` | §3/§4 límite de profundidad (MAX_DEPTH=8 medido) | profundidad == MAX válida rechazada (5/7 también hoja vacía) | `_loads` | S |
| framing.x__loads__mutmut_30 | `>` → `>=` | ídem límite | profundidad == MAX rechazada | `_loads` | S |
| framing.x__loads__mutmut_10/11/12 | código `invalid_json` → None/XX/mayús en reject_constant | §4 vocabulario de defectos (codes finding) | NaN/Infinity → código None/`XXinvalid_jsonXX`/`INVALID_JSON` | `_loads` → findings | S |
| framing.x__loads__mutmut_17/21 | `parse_constant=reject_constant` → None / removido | §4 «JSON estricto» | NaN/Infinity → **crash ValueError** (escapa del canal _DefectError) | `_loads` → decode_events (solo captura _DefectError) | S |
| framing.x__parse_line__mutmut_12/13/14 | código `invalid_encoding` → None/XX/mayús (canal surrogate) | §4 vocabulario | `"\ud800"` → código manglado | `_parse_line` → findings | S |
| framing.x_canonical_bytes__mutmut_8/12 | `ensure_ascii=False` → removido(default True) / `True` | §4 serialización canónica UTF-8 sin escapes | línea válida con «é» → noncanonical_json; surrogate escape → **aceptado** | `_parse_line`; **oráculo existente fuera de selección: PA01-unicode FALLA bajo mutante** | S + test existente |
| values.x__h__mutmut_1 | `or` → `and` | §3 «H» digest lowerhex64; rechazo como invalid_field | digest numérico → **crash TypeError**; hex inválido `"z"*64` → **aceptado** | builders SessionStart/ExecutionEnd/Options | S |
| values.x__h__mutmut_6/7/8 | código `invalid_field` → None/XX/mayús | §3 vocabulario | digest inválido → código manglado | ídem | S |
| values.x__opt_h__mutmut_2 | `value→None` en `_h(None)` | §3 «H o N» | `source_sha256="a"*64` válido rechazado | builders PluginClaim | S |
| values.x__opt_s__mutmut_2/3/4/5/6 | `value→None` / `min_len=None` / arg removido / min_len removido / `2` | §3 «S no vacío o N» (distribution/version) | válido rechazado / TypeError crash ×2 / `""` aceptado / 1-char rechazado | builders PluginClaim | S |

### 5.2 EQUIVALENCIA ACOTADA PROPUESTA — 10 IDs (ninguna ratificada aquí)

| IDs | Mutación | Equivalencia propuesta y dominio | Contraejemplo fuera del dominio | Evidencia |
|---|---|---|---|---|
| composites.x__cwd__mutmut_5 | `min_len` removido | Toda cadena de longitud 0 falla `startswith("/")` (subsumido) — dominio: entradas str (no-str ya rechazadas por `_s` tipo) | ninguno conocido | S (sin divergencia) + E |
| composites.x__utc__mutmut_5/6 | `min_len` removido / `2` | `_UTC_RE` exige formato exacto de 32 chars: toda cadena <32 falla el regex (subsumido) — dominio: str | ninguno conocido | S (sin divergencia) + E |
| framing.x_canonical_bytes__mutmut_3 | `ensure_ascii=None` | `None` es falsy en CPython json → idéntico a `False` — dominio: stdlib json de CPython | otra implementación json | S (sin divergencia) + E |
| framing.x_canonical_bytes__mutmut_6/11/16 | `allow_nan` → None/removido/True | NaN/Infinity no pueden llegar a `canonical_bytes`: `_loads` los rechaza antes (parse_constant intacto) y los demás callers (canonical_header, observation_events) solo reciben datos ya validados — dominio: callers actuales | un caller futuro que pase floats NaN diverge | S (sin divergencia) + E |
| framing.x_canonical_bytes__mutmut_18, x__parse_line__mutmut_4, x__line_defect__mutmut_7 | `utf-8` ↔ `UTF-8` | Alias del mismo codec en CPython (búsqueda case-insensitive) — dominio: stdlib codecs | ninguno en Python | S (sin divergencia) + E |

Límites declarados: una sonda sin divergencia NO demuestra equivalencia
por sí sola; cada propuesta añade razonamiento estructural y dominio; la
ratificación es decisión humana (D-A).

### 5.3 COMPORTAMIENTO NO CONTRATADO — 2 IDs

| ID | Mutación | Superficie | Hallazgo | Evidencia |
|---|---|---|---|---|
| framing.xǁ_DefectErrorǁ__init____mutmut_1 | `super().__init__(None)` | mensaje de la excepción (`str(exc)`) | **Cero consumidores** del mensaje en tools/ (grep: los `str(exc)`/`.args` existentes son de otras excepciones); el código contractual viaja en `.code` (intacto) | C + grep + S (sin divergencia) |
| framing.xǁ_DefectErrorǁ__init____mutmut_3 | `self.execution_id = None` | atributo `execution_id` | Corrección tras verifier: `pytest_decode_events.py:125,127` SÍ pasan `execution_id` a `_DefectError` y `:140` lo lee (`defect.execution_id`) — PERO `_attributed_execution()` retorna `None` en todos los caminos de raise medidos (type-no-int → None; fuera-de-rango → None), de modo que el valor real es siempre `None` y la mutación no es observable hoy; la clasificación se sostiene con esta justificación corregida | C + grep + lectura de fuente + S (sin divergencia) |

No se convierten en equivalentes ni en contratos: se elevan como decisión
humana (D-B: contratar la superficie o eliminarla — eliminar toca fuente
sellada y exigiría allowlist/re-sello propios).

### 5.4 Recuento

**33 HUECO + 10 EQUIVALENCIA ACOTADA PROPUESTA + 2 COMPORTAMIENTO NO
CONTRATADO + 0 LIMITACIÓN INSTRUMENTAL + 0 INCONCLUSO = 45.** Bruto
conservado: 233 killed + 45 survived = 278.

## 6. Sitios de módulo no instrumentados (64)

Desglose reproducido por AST propio (R7 lo midió con el motor WCT):
- **59** constantes-string dentro de `WIRE_FIELDS`
  (`pytest_wire_fields.py`): la tabla clase→tupla de nombres en orden del
  vector `payload_values` — **contrato §3** («Todas las demás clases
  conservan orden de la tabla…» y §3 líneas de `payload_values exacto`).
  Consumidor productivo: `pytest_decode_events.py:44`
  (`names = WIRE_FIELDS[cls]` — extracción posicional del vector) +
  re-export en payloads. Tests que observan su efecto:
  `test_wire_fields_arity_per_class` (aridad ExecutionStart=5 + tupla
  exacta de PhaseMake) y los PA09-*-exact (composición del vector vía
  decode). **Controles ausentes**: igualdad de tupla completa contra
  oráculo independiente para las ~19 clases restantes (omisión de campo,
  campo extra, orden intercambiado no detectados hoy por test directo).
  **Método alternativo propuesto** (no ejecutado): test con **literal
  independiente** transcrito de la tabla §3 del contrato (no generado
  desde la tabla productiva), comparación exacta por clase — detecta
  omisión/extra/asociación incorrecta; sin prueba tautológica.
- **1** docstring de módulo de `pytest_wire_fields.py`, **1** de
  `wire_values`, **1** de `wire_composites`, **1** de `wire_framing`
  (módulo) + **1** docstring de clase `DefectError` (nivel clase,
  contado en el bucket módulo por el motor) = **5** docstrings:
  constantes inertes en runtime (afectan a lo sumo G-DOC por presencia,
  no por contenido). Propuesta: declararlas **limitación instrumental
  sin dispensa** (no exigen equivalencias ni campaña alternativa).

La limitación de mutmut 3.7 (no instrumenta literales de módulo) **no
constituye dispensa automática ni obliga a inventar equivalencias**;
queda delimitada como arriba.

## 7. Propuesta mínima de reparación (agrupada por conducta; NO ejecutada)

| Grupo | Tests mínimos propuestos (entrada → observable) | Contrato | IDs que discriminaría | Demostración ya ejecutada | Allowlist | Presupuesto futuro |
|---|---|---|---|---|---|---|
| G1 límites S/opt | frontera vacío/1-char/válido de `_s(min_len=1)`/`_opt_s`/`_opt_h` vía PluginClaim/PhaseMake/argv/cwd | §3 «S no vacío (o N)» | opt_s 2-6, opt_h_2, argv 12/13, cwd_6, exception_type 2/3/5/6 (13) | sonda divergente por ID | tests/unit/test_pytest_schema.py (ruta aprobada) | ~120 s |
| G2 cwd componentes | `/a/./b` → invalid_field | §3 «sin componentes . o ..» | cwd_15 (1) | sonda | ídem | ~10 s |
| G3 NaN/Infinity | línea con NaN/Infinity → finding invalid_json, sin crash | §4 JSON estricto | loads 10/11/12/17/21 (5) | sonda (incluye canal crash) | ídem | ~30 s |
| G4 profundidad límite | profundidad == MAX aceptada; hoja vacía en límite aceptada | §3/§4 | depth 5/7/13, loads_30 (4) | sonda | ídem | ~30 s |
| G5 C0 en listas | `["\u0001"]` → invalid_encoding | §3/§4 | check_strings_2 (1) | sonda | ídem | ~10 s |
| G6 canónico unicode | (a) **expandir selección de campaña** wire con PA01-unicode existente; (b) línea «é» aceptada; `\ud800` → invalid_encoding | §4 canonicidad | canonical_bytes 8/12, parse_line 12/13/14 (5) | (a) demostrado: el test mata cb12; (b) sonda | receta de campaña (selección) + schema | ~60 s |
| G7 digest H | digest numérico → invalid_field sin crash; hex inválido → invalid_field exacto | §3 «H» | h 1/6/7/8 (4) | sonda | schema | ~40 s |
| G8 superficie _DefectError | (decisión, no test) | — | DefectError 1/3 (2) | grep de consumidores | decisión D-B | — |

Expectativas, no resultados medidos: la columna «discriminaría» es
hipótesis sustentada en la sonda de este encargo; la validación real
ocurrirá al ejecutar los oráculos en su encargo. Cobertura de grupos:
13+1+5+4+1+5+4 = 33 huecos + 2 (G8) = 35 IDs tratados; los 10 de
equivalencia van a D-A.

## 8. Decisiones humanas requeridas (separadas)

- **D-A** Ratificar o rechazar cada una de las 10 EQUIVALENCIAS ACOTADAS
  (con sus dominios y contraejuntos declarados; precedente: adjudicación
  scan_closers de R8 histórico).
- **D-B** Disponer los 2 COMPORTAMIENTOS NO CONTRATADOS de `_DefectError`
  (contratar mensaje/execution_id o eliminar superficie con allowlist y
  tratamiento de sucesor del sello R8).
- **D-C** Autorizar los oráculos G1–G7 bajo contrato vigente (sin
  contratos nuevos) y la expansión de selección G6(a).
- **D-D** Disponer la limitación instrumental de los 64 sitios (oráculo
  independiente de tabla para WIRE_FIELDS; docstrings declarados inertes).

## 9. Presupuesto, dictamen y sellos

Presupuesto experimental 600 s: sondas ~60 s (93 lanzamientos del ledger
—90 del autor + 3 finales—; incluye el lote inválido declarado de ~3.2 s),
**reserva verifier 120 s intacta** (el verifier consumió 1.94 s de ella),
revisión documental aparte. Guardián con recálculo por ledger (limitación
declarada: el reloj monotónico es por proceso driver; el total se concilia
sumando el ledger).

### 9-bis. Dictamen del verifier independiente

**FAVORABLE** (solo lectura, distinto del autor; reejecutó con su reserva:
ORIGINAL byte-idéntico, loads_17 crash ValueError reproducido, h_1 doble
expectativa confirmada —crash TypeError y hex inválido aceptado—, utc_6 sin
divergencia soportando la equivalencia propuesta; restauró los artefactos
que su reejecución sobrescribió y re-verificó el manifiesto 53/53). Verificó
además: sello, conjunto 45 por conjuntos, separación campaña/reproducción
(33 con divergencia + 12 sin = tablas del registro), contratos de una
muestra contra el P03 congelado, bases estructurales de las 10 equivalencias
en Python puro (`codecs.lookup('utf-8') is codecs.lookup('UTF-8')`,
`ensure_ascii=None`≡`False`, `allow_nan=None` falsy, `_UTC_RE` 32 chars),
sitios 64=59+5 por AST y motor, presupuesto y desviación fiel, coherencia
33+10+2=45 y G1-G8=45. **Seis hallazgos, ninguno invalidante, incorporados
antes de publicar**: (1) MEDIO — justificación de `DefectError_3`
corregida en §5.3 (decode_events SÍ pasa/lee execution_id pero el valor es
siempre None en los caminos de raise; clasificación se sostiene); (2) cita
C0/DEL precisada a §2; (3) lote inválido = 36 sondas (~3.2 s), corregido;
(4) salida PA01-unicode preservada textualmente en §4; (5) «src/tools» →
«tools/»; (6) variación de superficie del arnés declarada en §4. Su
dictamen aprueba el expediente; NO ratifica decisiones humanas ni declara
L2 cerrado.

Expediente `build/tmp/reanclaje8-20260918/`: manifiesto 53 miembros sin
auto-hash (digest `3996976fe063556672326a729b5a861d8f3f19d96aa8cc7021cc299227bab2c7`),
digest fuera de miembros; expedientes R5-R7 intactos.

## 10. Siguiente incremento mínimo propuesto

**PROPUESTO — NO EJECUTAR SIN AUTORIZACIÓN.** REANCLAJE-9 = oráculos
G1–G7 (TDD en `tests/unit/test_pytest_schema.py`, rutas aprobadas, sin
cambios de producto; allowlist solo tests) + re-campaña L2 con selección
expandida (G6a) sobre los 33 IDs con hueco, presupuesto ~600 s; las
equivalencias quedan a la puerta D-A. Alternativa más pequeña: solo G3+G4
(canles de crash y límites; 9 IDs).
