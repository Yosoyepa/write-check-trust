# Registro REANCLAJE-19 — refuerzo contractual L3 y recalificación única con activación fiel (2026-09-19)

Estado: **17 oráculos reparados con polaridad contractual, controles de
módulo independientes, y ÚNICA campaña externa con activación anterior al
primer import medida sobre los 129 IDs: 129 killed + 0 survived.** El bruto
histórico R17 se conserva íntegro (129 = 99 + 30); la transición medida es
99 killed→killed y 30 survived→killed (17 de oráculo + 13 de factoría).
Sin residuos, sin timeouts, sin segunda campaña, sin equivalencias nuevas.
La expectativa del encargo se cumplió como resultado medido, no impuesto.

## 1. Base, identidades y aislamiento

Base `c446faf0823b85f7aa096991c2d496b4595632fd` == remoto == headRefOid PR #56
(borrador, OPEN); merge-base = main `8a379d64…` (= main de referencia); tag
`v1.0.0b3.dev1` intacto. Sin avance desde R18: no hubo invalidantes que
clasificar. Expediente aislado `build/tmp/reanclaje19-20260919/` (guardián
propio, sobres §13); árbol de trabajo `build/tmp/reanclaje19/` (clon local
con raíz Git propia en la base); checkout principal, índices, runtimes
compartidos, worktrees, tags y expedientes históricos preservados (verificado
por el verifier de puerta previa). Runtime: Python 3.13.14, pytest 9.1.1,
mutmut 3.7.0.

## 2. Los 17 oráculos: frontera, polaridad y casos

Frontera: **observations manuales** por `validate_payload` público
(§2 l.112-116), NO el decoder — su vía del wire anticipa estos rechazos y la
obligación vive en el reconcile (R17 §5). Instancias con una sola violación
sobre una base válida (los demás campos válidos para que otro error no tape
el defecto); esperados literales del contrato. Polaridad por ID (diff contra
custodia R18 `12-diffs-17-reproducidos.json`, 17/17 verificados):

- **Rechazo** (`invalid_observation` con campo exacto): `clean_string_3`
  (>4096 bytes, §2 l.97-99), `clean_string_6` (DEL 0x7F), `is_argv_5`
  (argv `()`, §3 l.209), `is_broad_text_1` (C0 en broad-text, con vacío
  permitido fijado aparte), `is_cwd_5/6` (segmento `.`: `split(None)` /
  `split("XX/XX")` no aíslan componentes), `is_cwd_11` (segmento `.` exacto:
  membresía `XX.XX`), `is_cwd_13` (segmento `..` exacto), `is_digest_1`
  (digest no lowerhex64, §2 l.56/§3 l.201), `is_text_6` (vacío en clase
  no-report), `is_xfail_3/4/5` (XfailObservation real con un campo no bool,
  §2 l.236), `within_2` (bool en `argument_exit`, §2 l.46-47/§3 l.227).
- **Aceptación** (obligación vigente satisfecha por el producto):
  `clean_string_8` (espacio 0x20: C0 es <0x20), `is_u_6` (SEQ_MAX exacto en
  U), `within_6` (exit 255 exacto; con rechazo adyacente de 256 que
  discrimina el rango independientemente).

Sensibilidad 17/17 (sobre S): original verde (128 passed) y por cada ID un
**mutante real activado desde el arranque del proceso** (trampolines sellados
R17, byte-verificados) con el nodeid oráculo previsto entre los fallos
(`logs/S02-sondas-resumen.json`): rc=1 en 17/17. Las microsondas no son
campaña ni se sumaron al bruto.

## 3. Controles de código de módulo

- **Matriz independiente de `_PAYLOAD_CHECKS`** derivada de la tabla §3
  (21 clases × campos): instancias válidas con fronteras deliberadas
  (SEQ_MAX, 255, espacio, vacío-en-broad-text, optionales presentes/ausentes,
  enumeraciones completas) y ~70 filas de violación única con campo exacto.
  La tabla productiva NO se copia ni se importa; el ancla es
  `CONTRACT_PAYLOAD_FIELDS` (§3) y el catálogo del SUT (21 códigos).
  Anti-vacuo por inventario determinado (21, ni más ni menos).
- **Sensibilidad empírica en copia desechable** (R18 §5 cerrado): omisión del
  check `argument_exit` → exactamente las filas bool/256 fallan por DID NOT
  RAISE; intercambio discriminante `_within(0,255)`→`_is_u` → falla la fila
  256. Árbol restaurado byte-idéntico. Nota honesta: la primera omisión (v1)
  quedó confundida por una tupla malformada (crash de unpacking); se repitió
  limpia (v2) con la tupla unitaria correcta.
- **Frozen conductual de las 21 clases** (§2 l.60-61): bandera + asignación
  real sobre instancia válida (FrozenInstanceError) + conservación del valor;
  clases resueltas por la fachada con cotejo de identidad contra la matriz.
- **Enumeraciones** (§3/§5): transcripción literal ROLES/PHASES/OUTCOMES/
  TERMINATIONS/CHANNEL_DEFECTS (TERMINATIONS excluye `unobserved`, nunca
  admitido en wire, y hay fila que lo rechaza).
- **Orden e inventario de campos** (§3): transcripción de las 21 filas
  (ExecutionStart íntegro con role y digests; el subconjunto wire ya estaba
  controlado por WIRE_FIELDS desde R10).
- **`__all__` de la fachada**: sin test nuevo — no existe contrato ni
  consumidor que exija un inventario literal de `__all__` (composición §10:
  «No crear módulos vacíos ni API extra/export en __init__»); la reexportación
  relevante (`EVENT_CATALOG`) ya está transcrita y aseverada desde R10
  (`CONTRACT_EVENT_CATALOG`). La ausencia de aserción no crea la obligación.

## 4. Arnés externo: generación y ejecución separadas

**mutmut GENERA** (copia nueva, `gen/`): `mutmut run --max-children 1
ZZ_GENERACION_R19_NO_MATCH` con firma admisible (rc=1 «nothing matches» tras
«done», 6 files mutated, cero mutantes ejecutados, sin 🎉/🙁), pyproject
instrumental con preimagen y delta identificados (solo el bloque
`[tool.mutmut]` de gobernanza sustituido por el bloque L3 con la selección
580), snapshot de stats congelado. **El arnés EJECUTA** (lanzador fail-closed
heredero de R12–R18, no es «mutmut run»): intérprete nuevo por ID,
`MUTANT_UNDER_TEST` en el entorno ANTES del spawn (antes de importar pytest,
fuentes o consumidores), con doble identidad llamador-lanzador y sonda
ambiental de identidad+imports en proceso fresco.

Inventario y correspondencia (no solo números): 129 IDs por conjuntos ==
histórico (99 predicates + 30 validate; 4 fuentes con 0 IDs);
`hash_by_function_name` de los 6 `.meta` idéntico al histórico; las 2 fuentes
con IDs **byte-idénticas** a la custodia R17; los 17 diffs clave verificados
contra R18. Las 4 fuentes sin IDs conservan controles separados (matriz de
clases/validación, catálogo, límites por conducta — R17 §6).

Canario de factoría (exigido §7): distingue la **closure almacenada** mutada
de una original — bajo `x__within__mutmut_6`, la closure de
`_PAYLOAD_CHECKS[SessionEnd]["argument_exit"]` rechaza 255; bajo original lo
acepta (procesos frescos, rc=0/0 con exit 4 en disidencia). Canario
end-to-end: `clean_string_8` muerto exactamente por el oráculo de frontera.
Negativos 5/5 rc=2: ID ajeno, selección vacía, **activación ausente**,
**identidad incorrecta**, tests desactualizados (árbol restaurado tras la
perturbación).

## 5. Selección, baseline y campaña única

Selección final por unión: **580 = 452 de R17/R18 + 128 nuevos** (colección
real, 0 bajas, 0 duplicados, digest congelado; property fuera conforme
TEST-008 — 1 property en el repo corre aparte). Baseline ORIGINAL sobre esa
selección en el árbol congelado: **580 passed, 0 skips/xfails**, 15.06 s
(puerta de viabilidad: 129 × 15.06 ≈ 1943 s < 3600 s). Verifier de puerta
previa: **DICTAMEN FAVORABLE** (sondas propias 4/4 sobre V: factoría
históricamente oculta `within_6`, `member_of_1` con 305 fallos, oráculo
`clean_string_3`, y ORIGINAL 580 passed), sin correcciones obligatorias.

**ÚNICA campaña** (B): serial, 129 IDs explícitos, un intérprete nuevo por ID
vía lanzador, selección congelada, timeout 180 s/ID (timeout ≠ killed), sin
reparaciones, sin veredictos heredados. Resultado autoritativo del ledger:
**129 KILLED · 0 SURVIVED · 0 TIMEOUT · 0 instrumental**, wall 2201.4 s
(B 2201.4/3600). Reconciliación: generado == autorizado == ejecutado ==
resultados == 129; cero duplicados/ajenos/faltantes; `LANZADOR-OK` y diff
esencial y primer fallo presentes en 129/129. Estados `.meta` históricos
intactos (no sobrescritos).

## 6. Causalidad y transición

Transición por ID respecto del bruto R17 (99 killed + 30 survived):

| Transición | IDs | Sustento |
|---|---|---|
| killed→killed | 99 | detecciones históricas conservadas (tests preexistentes) |
| survived→killed | 17 | clase B: oráculos reparados; primer fallo en test oráculo nuevo 17/17 |
| survived→killed | 13 | clase E: activación fiel — la tabla `_PAYLOAD_CHECKS` se construye con la factoría mutada (~247 fallos medios) |

Exit 1 == test failures con causa contractual (ningún fallo de
imports/colección; ningún timeout que adjudicar). La partición 17+13 == 30
sobrevivientes R17 es exacta y disjunta (verificada contra el bruto por-ID).

## 7. Corrección post-campaña X→Y (declarada) y batería

La primera pasada de la batería reveló un hallazgo propio: **G-INTROVERT**
marcó 2 tests nuevos (aserciones sin traza al SUT por indirección de
parametrización) y rompía el ratchet `introverted-tests` (baseline 0). El
candidato de campaña (X) estaba congelado y la campaña es única, así que la
corrección fue mínima y **documentada con equivalencia de medición**
(`custodia/equivalencia-X-Y.json`): 2 funciones, 17 líneas; las funciones
corregidas solo leen `ps.EVENT_CATALOG` y `pp` (fuentes con 0 mutantes del
inventario 129) y maquinaria dataclass; los 17 oráculos y todo test de
detección son byte-idénticos; los 129 logs de campaña acreditan colección
sobreviviente bajo cada mutante — ningún veredicto puede cambiar. El
verifier final audita esta equivalencia.

Batería sobre Y (I): colección 1337; **suite normativa completa 1337 passed,
0 fallos**; property separada (1 passed, 1336 deselected); ruff check/format
limpios; ratchets sin relajaciones (gobernanza intacta); **gate fast 7/7
PASS**; gate commit 20 PASS · 1 FAIL — **G-META-1, rojo conocido del PR**
(`governance/lint/vulture_whitelist.py`, preexistente, fuera del delta de
este encargo). Incidentes de batería declarados: primera pasada de gates sin
`.venv/bin` en PATH («herramienta ausente», 8 falsos fallos sast) repetida
con PATH correcto.

## 8. Presupuestos e incidentes

S 31.09/900 · A 113.29/300 · B 2201.40/3600 · V 67.41/300 · I 761.61/900 ·
PUB §10. Total ≈ 3175 de 6180. Intentos inválidos cargados: 3 arranques de
fase-a (TOML sin escapar `"`/`\` en nodeids → escapado TOML/json; aserción
de trampolines en fuentes con 0 IDs; nombres `x__fn__orig` vs
`x__fn__mutmut_orig` y regex `x_+`), omisión v1 tupla malformada, batería
con PATH incompleto, 1 cargo conservador de 60 s por el `uv sync` inicial no
medido en vivo. Sin transferencias ni saldos históricos.

## 9. Custodia y dictámenes

Expediente con identidades, matriz, diffs de tests, sensibilidades,
perturbaciones, selección, generación/inventario/sellos, lanzador y
negativos, ledger de campaña por ID, reconciliación y causalidad,
equivalencia X→Y, dictámenes y presupuestos; logs cerrados antes del
manifiesto; digest y verificación fuera de sus miembros; hooks/publicación/CI
en archivos separados del sello. Puerta previa: FAVORABLE (ver §5). Verifier
final independiente: dictamen en el expediente (audita, entre otros, la
equivalencia X→Y y el bruto).

## 10. Estado de lotes y siguiente incremento PROPUESTO (no ejecutado)

| Lote | Estado |
|---|---|
| L2 | cerrado en su alcance (R10–R11) |
| L4 | cerrado por resultado medido (R12–R16) |
| **L3** | **RECALIFICADO aquí: 129 killed + 0 survived con activación fiel; sin residuos** |
| L1 | pendiente de TEST-007 (partición/decisión humana) |
| L5–L9 | pendientes conforme al plan de R6 |

Binding PA01–PA12 pausado. Sin invalidante concreto, L2 y L4 no se reabren.
Próximo mínimo propuesto: L1 conforme TEST-007 (partición del archivo de
sitios >100 por fachada, decisión humana), NO ejecutado. Quedan fuera:
928 IDs, Q-ACCMUT, cobertura/CRAP/DRY/full, E9, bless, update-manifest,
merge, bump, tag o release.
