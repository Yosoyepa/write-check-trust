# Registro REANCLAJE-14 — oráculos L4, selección ampliada, custodia R12 y análisis de atribución (2026-09-19)

Estado: **reparación acotada de los huecos contractuales L4 sin campaña.** Selección
L4 ampliada (152), quince oráculos bajo contrato vigente con sensibilidad medida
(15/15), control separado del estado inicial `expected_seq=1` (sitio de módulo no
instrumentado), corrección documental de la custodia R12, y análisis contractual del
canal de atribución con propuesta de reclasificación. El bruto L4 se conserva
**exacto**: 473 = 426 killed + 46 survived + 1 timeout. **Sin campaña nueva** (la
campaña completa de L4 se autorizará una sola vez sobre tests y decisiones
estabilizados), sin cambios de producto, sin contratos nuevos, sin ratificaciones, sin
excepciones, sin binding PA01–PA12, sin Q-ACCMUT, sin cobertura/CRAP/DRY/full.

## 1. Base, aislamiento y SHAs

| Elemento | Identidad | Comprobación |
|---|---|---|
| Base comunicada | `1d01ff3c39bf69ece1f9bae1bd4b18e1d39c6bfd` resuelto; == HEAD de la rama `codex/reanclaje-p03a-fase1` == `headRefOid` de PR #56 (borrador, OPEN) | `git rev-parse` + `gh pr view 56` |
| Corte técnico L4 | `0487448032c1e1cf56bd18f98f9bea9586f3fc46`; delta técnico→documental 0487448→1d01ff3 = SOLO docs (R12+R13) | `git diff --stat` sobre src/tools/tests/features/governance/pyproject/uv.lock: vacío |
| Manifiesto R12 | digest `5229c127922106f337fb56c2297f4f93b365e5cf359bc2912b7cc7476b0300` (recalculado aquí); 91/93 miembros verifican hoy | `sha256sum` + §2 |
| Manifiesto R13 | digest `6241f2ea1faba93676997ea319247d03c07168690da810ba7a9c6d660e395e74`; 70/70 miembros verifican | `sha256sum -c` |
| Copia de trabajo | `build/tmp/reanclaje14-20260919/` (Git propio en `repo/`, detached 1d01ff3; `run/` + `run/mutants/` copiados del expediente R13 y re-verificados contra custodia R12 byte a byte) | `cmp` 3 instrumentadas + 2 tests == sellos |
| Árbol instrumentado | 3 fuentes con trampolines byte-idénticas a `custodia/instrumentado-*.py` de R12; tests base idénticos a sellos; lanzador fail-closed propio con los 6 controles heredados de R12 | lanzador + `cmp` |

Checkout principal, índices ajenos, expedientes históricos, main, tag y release:
intactos. Sin lectura de credenciales.

## 2. Corrección de custodia R12

El manifiesto histórico R12 conserva su resultado real **91/93**; no se sobrescribió
nada para fabricar 93/93. Los dos miembros derivados y su demostración byte-exacta:

| Miembro | Sellado | Actual | Escritura posterior al sellado (01:04:16) |
|---|---|---|---|
| `logs/00-ledger-guardian.csv` | `24dbab8a…` | `9593ceb5…` | 2 filas PUB appendizadas (`gate-fast-prepublicacion`, 01:04:28–34, wall 6.33 s): `head -n -2` del archivo actual reproduce el digest sellado |
| `guardian-state.json` | `6448412…` | `81197a49…` | una reescritura atómica del guardián: `spent.PUB` 0.0 → 6.333…; el estado sellado se re-deriva del actual restaurando `PUB=0.0` con la serialización exacta `json.dumps(indent=2)` y verifica por hash |

Distinción explícita: la del ledger es verificación de prefijo (hecho del archivo);
la del state es reconstrucción explicativa verificada por igualdad de hash — los
bytes en reposo al sellado no se conservan y no se pretende verificarlos. Ningún
resultado sustantivo depende de estos archivos: son contabilidad de presupuesto; las
91/91 evidencias restantes (fuentes, selección 140, inventario/diffs, meta-final,
stats, 47 sondas, campaña) verifican sin cambios — fuentes, selección, resultados e
identidades de mutantes NO cambiaron. Artefactos sucesores (en este expediente):
`custodia-r12/NOTA-SUCESORA-R12.md` + `custodia-r12/MANIFIESTO-REANCLAJE12-SUCESOR.sha256`
(93/93 bytes actuales; digest del manifiesto `4c8c0c065d67ca182974fff643960107ecf9a27457bcfab3c1eec2116058ff24`,
calculado y verificado fuera de sus miembros). Reglas R14 adoptadas: logs activos
fuera del conjunto sellado; logs cerrados antes de incorporarse al manifiesto;
verificación y digest fuera de los miembros; ninguna escritura sobre miembros
sellados; novedades en artefactos sucesores. Nota sucesora acotada añadida a
REANCLAJE-13 (§ de cierre): la derivación del state también es byte-exacta y el
manifiesto sucesor existe.

## 3. Selección L4 ampliada (sin re-demostrar lo ya medido)

- **Composición por conjuntos**: selección 140 (R12, digest `9b96790c…`) ∪ 12 nodeids
  PA09/PA10 (R13 `custodia/reparacion-minima-12.nodeids`, digest `ac70d539…`);
  intersección **0**, unión **152** nodeids exactos.
- Archivo: `custodia/seleccion-L4-ampliada-152.nodeids`, digest
  `a75bc4706e938f4a724a281853b0b8157561d9c37a921eb29b50475b5dc64c6a`. Orden: 140 en
  orden sellado, luego los 12 en orden R13.
- **Verificación de composición** (no re-demostración): colección 152/152 en el árbol
  acreditado y **ORIGINAL 152 passed** (baseline verde, 4.4 s, sobre S → ver §9).
- La sensibilidad de los 8 huecos-de-selección NO se repitió: la identidad de los 12
  nodeids y la evidencia de R13 (medición 8/8 rojos, `logs/06` de R13) siguen siendo
  válidas porque los tests base no cambiaron (sellan idénticos). Correspondencia
  mutante→test→causa documentada por R13 §4 se conserva.

## 4. Los quince oráculos + un control (tests bajo contrato vigente)

Archivo editado: **solo** `tests/unit/test_pytest_schema.py` (+138 líneas, 9 tests);
`tests/unit/test_pytest_observation.py` intocado (no hizo falta). Sin cambios de
nodeids existentes. Cada test nace VERDE sobre el original (caracterización/refuerzo)
y su sensibilidad quedó medida por sonda (§5).

| # | Test | Obligación contractual | Entrada y observable | IDs que discrimina |
|---|---|---|---|---|
| 1 | `test_execution_index_non_integer_is_invalid_field` | §2 «no lanza excepciones por contenido malformado… devuelve prefijo y findings» + §4 prec. 4 «Tipo/rango JSON errado invalid_field» | evento con `ex="1"` (string); sin excepción, events `()`, finding único `invalid_field` en offset de la línea | `attributed_execution_3`, `execution_index_3/5/7/8` (5) |
| 2 | `test_resolve_field_nodeid_non_integer_index_is_invalid_field` | §4 prec. 4 «referencia nodeid»; índice no-entero = invalid_field | frontera del módulo del resolvedor: `{"nodeid": "0"}` → `_DefectError("invalid_field")` (por API pública el coerce `_int_in` anticipa el mismo código: caracterización del helper) | `resolve_field_nodeid_6/7/8` (3) |
| 3 | `test_sequence_zero_is_invalid_field_not_sequence_error` | §2 «enteros en rangos explícitos» (seq ∈ 1..SEQ_MAX) + §4 prec. 5 | primer evento seq=0 → `invalid_field` (no `sequence_error`) | `check_sequence_1` |
| 4 | `test_seq_at_seq_max_boundary_stays_in_range` | §2: SEQ_MAX es el tope INCLUSIVO de U | seq=SEQ_MAX exacto → `sequence_error` (en rango, fuera de orden) | `check_sequence_7` |
| 5 | `test_local_seq_at_seq_max_boundary_stays_in_range` | §2 idem local_seq; complementa `test_local_seq_out_of_range` (SEQ_MAX+1) | local=SEQ_MAX exacto → `sequence_error` | `advance_local_11` |
| 6 | `test_nodeid_index_above_seq_max_is_invalid_field` | §4: prec. 3 (rangos del payload) antes que 4 (referencias) | declaración válida + item con índice SEQ_MAX+1 → `invalid_field` (no `foreign_reference`) | `validated_vector_19/20` (2) |
| 7 | `test_event_vector_shaped_as_object_is_invalid_field` | §4 literal «vector con objeto en lugar de array es invalid_field» | línea de evento = objeto JSON de 5 claves → `invalid_field` | `decode_event_3` |
| 8 | `test_header_execution_entry_shaped_as_object_is_invalid_field` | §4 misma cláusula de forma sobre el vector de ejecución de cabecera | `executions[0]` = objeto de 5 claves → finding `invalid_field` offset 0, sin excepción | `bad_execution_1` |
| 9 | `test_first_event_seq_not_one_is_sequence_error` | §4 «seq global contiguo desde 1» | primer evento seq=2 → `sequence_error` | **NINGUNO del inventario** — control del sitio de módulo `expected_seq=1` (§6) |

Requisitos cumplidos: oráculos independientes del algoritmo (entradas construidas con
el serializador propio `_dump`; códigos esperados transcritos del catálogo §4);
API pública en 8/9 (el resolvedor solo es observable en su frontera porque el coerce
del vector anticipa idéntico código por API pública); fronteras explícitas
(SEQ_MAX, SEQ_MAX+1, 5 claves) y justificadas por §2; sin mocks; sin estados
imposibles; sin retiro de casos; sin literales nuevos inventados (todos los códigos
son del catálogo §4). El original pasa los 9 (9/9 verde): no se inventó rojo
histórico del producto.

## 5. Sensibilidad medida (sondas individuales, sin mutmut run)

Por cada ID de la tabla anterior, con el árbol L4 acreditado y el lanzador
fail-closed (ID ∈ inventario; hashes de fuentes originales == sellos; mutants
instrumentado byte-idéntico a custodia; selección no vacía; `MUTANT_UNDER_TEST`
verificado ambientalmente; imports resolviendo en mutants/): **15/15 rojos por la
causa prevista** (logs/05-*, resumen logs/06):

- `attributed_execution_3` — TypeError `'<=' not supported between instances of
  'int' and 'str'`: el decoder lanza donde §2 exige devolver finding (crash causal).
- `execution_index_3/5` — `assert None == 'invalid_field'`; `_7/_8` —
  `'XXinvalid_fieldXX'`/`'INVALID_FIELD'`.
- `resolve_field_nodeid_6/7/8` — idem en la frontera del resolvedor.
- `check_sequence_1` — `assert 'sequence_error' == 'invalid_field'` (rango
  reclasificado como orden).
- `check_sequence_7` / `advance_local_11` — `assert 'invalid_field' ==
  'sequence_error'` (frontera exacta excluida del rango).
- `validated_vector_19/20` — `assert 'foreign_reference' == 'invalid_field'`
  (precedencia 3↔4).
- `decode_event_3` — `assert 'unknown_event' == 'invalid_field'`.
- `bad_execution_1` — `KeyError: slice(2, 5, None)`: el guard mutado deja pasar el
  objeto y `wire[2:5]` lanza; excepción del SUT causalmente ligada a la conducta
  mutada y al contrato (§2 exige finding, no excepción).

Un fallo instrumental no cuenta como discriminación: todos los lanzamientos pasaron
los controles previos del lanzador (exit 2 habría sido rechazo, no kill).

## 6. Control adicional `expected_seq=1` (separado del inventario)

«15+1» aclarado: los 15 son mutantes del inventario L4 (hueco-de-oráculo); el «+1»
es el **sitio de módulo no instrumentado** `expected_seq: int = 1` (default de
dataclass; L47 del original y L50 del árbol instrumentado — mutmut 3.7 no
instrumenta ese sitio): NO es un superviviente adicional y NO genera ID. Control
implementado: test
#9 de la tabla. Sensibilidad por perturbación puntual en copia desechable
(`desechable-expectedseq/`): diff EXACTO de una línea (`expected_seq: int = 1` →
`= 2`), hash del archivo perturbado `5710cfdf…`, test #9 ROJO (rc=1: acepta el
primer seq=2 y el finding desaparece) contra ORIGINAL verde. La perturbación no se
cuenta como ID generado ni como kill de L4; la copia es desechable y no forma parte
del árbol acreditado.

## 7. Atribución de `execution_id`: análisis contractual (sin reparación)

Los 11 IDs clasificados por R13 como COMPORTAMIENTO-NO-CONTRATADO (todos tocan el
canal `finding.execution_id` del decoder) se reanalizaron por ID y camino alcanzable
contra el contrato completo y el consumidor real (`_decoder_blocks` →
`scan_protocol_complete` → `protocol_complete` por ejecución).

**Hallazgo estructural (nuevo, decisivo).** `attributed` se consume en UN único
lugar (`_execution_index`) y en sus dos ramas de raise el valor computado es
**siempre None**: la rama `invalid_field` exige `type(ex_value) is not int`, que
contradice la guarda `type(ex_value) is int` de `_attributed_execution`; la rama
`foreign_reference` exige `ex_value` fuera de `[0, len)`, que contradice `0 <=
ex_value < len`. Todos los demás raise del paquete no pasan ejecución, y `_finish`
copia `defect.execution_id`. **El canal de atribución es inerte: constantemente
None en todo camino alcanzable del original.** Sonda empírica
(logs/08): defecto en línea con `ex=0` válido → `findings[0].execution_id is None`;
consecuencia: `_decoder_blocks` bloquea **ambas** ejecuciones (hoy el efecto de un
finding de decoder es GLOBAL, no por ejecución).

Respuestas del análisis: (1) el dato que cambia es `finding.execution_id`; (2) el
cambio NO es alcanzable en el original — el plumbing existe pero su valor observable
es constante None; (3) hoy altera la completitud de TODAS las ejecuciones por igual;
(4) con el canal inerte no hay acreditación indebida por atribución — el sesgo es a
rechazar de más; poblarlo sin contrato podría acreditar de más (ejecución no
afectada completa pese a defecto de otra); el riesgo de pérdida de diagnóstico
existe pero es simétrico al actual; (5) obligaciones derivadas del contrato: §2 fija
el TIPO (`str o None`) — cumplido; §4 fija el catálogo y offsets — cumplido; NI UNA
línea obliga a poblar el valor (grep «atribu» en PROPUESTA-P03: 0). La semántica del
docstring del consumidor («un finding de decoder afecta a esta ejecución o no está
atribuido») presupone que la atribución puede existir, pero no la impone.

**Propuesta de reclasificación (pendiente de decisión humana, no ratificada aquí):**
los 11 pasan de COMPORTAMIENTO-NO-CONTRATADO a **EQUIVALENCIA-PROPUESTA por canal
inerte**, con invalidantes explícitos: (a) reparación de producto que pueble la
atribución; (b) contrato nuevo que fije la regla «un finding con execution_index
válido lleva la atribución de esa ejecución y solo bloquea a esa ejecución». NOTA:
esa regla contractual NUEVA haría al original NO conforme (nunca atribuye) →
requeriría reparación de producto con autorización propia. Reconciliación resultante
si el humano acepta: 46 = 8 selección + 15 oráculo (ahora con tests) + 23
equivalencia propuesta (12+11) + 0 no contratado. Si el humano prefiere preservar el
canal como no contratado, la disposición explícita queda como en R13 §7-R5. No se
exceptúan en bloque: cada ID conserva su diff y fundamento en la tabla R13 + este
análisis.

## 8. Otros sitios no instrumentados, tope 20000 y timeout

- **_CATALOG (1 sitio)**: consumo real (`_decode_event` → origin/kind/clase);
  PA03-event-code y todos los journals válidos lo ejercitan posicionalmente. La
  transcripción literal propuesta por R13 §6 NO se implementa (sin nuevos controles
  permanentes en este encargo).
- **_CAPPED (5 sitios)**: el CONSUMO (`_inventory_key`) queda sensible tras la
  reparación de selección (los 12 PA09/PA10); la transcripción de la tabla queda
  como propuesta R13 §6, sin implementar.
- **Topes**: **10000** es contractual (§2 «Máximo10 000 entradas por
  inventario/execution… Exacto permitido; +1… limit_exceeded»; §4 l.280); el control
  de frontera REAL existe y pasa (`test_wire_inventory_cap_at_the_real_boundary`:
  10 000 exacto / 10_001 → limit_exceeded). **Corrección a R13 §6**: 20000 SÍ tiene
  línea literal contractual — §3 l.157 «índices desde0 contiguos, cada string único,
  máximo20 000 declaraciones» (R13 lo buscó solo en §4). Hoy se controla con
  constante reducida (`test_declaration_limit_isolated_with_reduced_constant`);
  la frontera real 20 000/20 001 queda como propuesta pendiente, no implementada.
  Ninguna cifra de implementación se convirtió en obligación nueva.
- **Docstrings de módulo/clase (5 sitios)**: sin efecto conductual identificado; sin
  equivalencias inventadas ni tests artificiales.
- **Timeout `x__consume_line__mutmut_22`**: estado bruto **timeout** conservado; la
  demostración causal de no-terminación (R12/R13: original 2.78 s verde vs mutante
  SIGXCPU/−9 en el mismo entorno) NO se repitió. **Texto de decisión humana
  propuesto (D-C', sin aprobar)**: «Un mutante que vuelve no-terminante una función
  cuya obligación contractual (§4: retornar la observación para toda entrada dentro
  del límite) exige terminar, cuenta como defecto detectado, con evidencia de
  original terminante en idéntico entorno e imports; el bruto conserva su estado
  timeout y el límite de 117 s es del arnés (RLIMIT_CPU de mutmut), no un SLA del
  producto. Alternativa si se rechaza: timeout instrumental, disposition explícita.»

## 9. Batería de integración, presupuesto y estado del árbol

Integración (sobre I, bytes finales, en `repo/` aislado):

| Paso | Resultado |
|---|---|
| Colección completa | **1206 tests coleccionados** (rc=0) |
| Focales (schema + observation) | **423 passed** (rc=0) |
| Suite normativa (`-m "not property"`) | **1205 passed, 1 deselected** (rc=0) |
| Property separada (`-m property`) | **1 passed** (rc=0) |
| `wct gate --tier fast` | rc=0 tras corrección de formato/lint (ver abajo) |
| `wct gate --tier commit` | **21 puertas: 20 PASS · 1 FAIL — G-META-1, PREEXISTENTE en la base** |

G-LINT/G-FMT fallaron en la primera pasada por dos E501 míos y formato; corregidos
(wrap de dos líneas + `ruff format` con la config del gate) y re-verificados con la
invocación exacta del gate (`--config governance/lint/ruff.toml`). **G-META-1 está
rojo en el base prístino 1d01ff3 (36 violaciones: `vulture_whitelist.py` y
`mutation_cases.py` «modificado», 34 módulos «nuevo protegido» no registrados en
`governance/integrity.lock`) y limpio en main (0 violaciones)**: la rama del PR #56
añadió archivos protegidos sin refrescar el lock. La CI del PR ya falla hoy por
exactamente eso (`commit-gates` FAILURE, mismas violaciones). Actualizar el lock es
escritura de gobernanza (SEC-005): NO se hizo; se reporta y requiere autorización
humana explícita. Mi delta deja G-LINT/G-FMT/G-TYPE/G-TEST/G-ARCH y demás puertas
del tier en verde.

Presupuesto (guardián monotónico propio, grupos de proceso, ledger
`logs/00-ledger-guardian.csv`): cierre **S 92.47/480 + SV 0/120** (agregado
experimental 92.47 de 600) e **I 705.35/900**. Sin transferencias ni ampliaciones.
Intentos inválidos: 2 instrumentales ANTES de ejecución válida (split de nodeids
por espacios → colección vacía; `lanzador.py` sin bit de ejecución) corregidos sin
costo de hijo; una corrida de colección rc=4 registrada.

## 9.1. Verifier independiente — DICTAMEN FAVORABLE (condición atendida)

Verifier distinto del autor, solo lectura sobre el expediente, copia propia para
reproducciones (SV 10.14 s de 120). **DICTAMEN: FAVORABLE a publicar el delta
técnico**, con una condición innegociable — H1 — atendida antes de publicar: §10 de
este registro describía la publicación como hecha cuando aún no existía el commit
(HEAD en base); se reescribió §10 como secuencia ejecutada tras el dictamen y el
resultado real queda en la entrega, no anticipado aquí. Reprodujo: ORIGINAL 9/9
verde; 6 sondas de grupos distintos rc=1 con las causas exactas (check_sequence_7,
validated_vector_19, bad_execution_1, attributed_execution_3,
resolve_field_nodeid_6, execution_index_3); contabilidad 46 y «15+1» byte-idéntica
al sellado; custodia R12 (91/93, prefijo ledger y state byte-exactos, sucesor
93/93); canal de atribución inerte confirmado en código y grep; delta solo tests+docs.
Menores: H2 (filas «D» del ledger R12 son sintéticas de ERA R12 — preexistentes,
no tocadas aquí; trazabilidad), H3/H4 (citas §2/§4 de los tests #4/#5/#8 leídas
como inferenciales pero conformes), H5 (la línea de `expected_seq` es L50 del árbol
instrumentado y L47 del original — precisión incorporada a §6). No reproducido por
presupuesto/alcance: 9 sondas restantes (vía documental), perturbación expected_seq
(logs leídos), baseline 152 y batería completa (logs leídos), demo del timeout
(fuera de alcance), G-META-1 local (corroborado vía CI viva sobre la base).
Informe: `build/tmp/reanclaje14-20260919-verifier/INFORME-VERIFIER.md`. **No
ratifica equivalencias, no admite el timeout, no cierra L4, no aprueba contratos
nuevos.**

## 10. Publicación

Ejecutada DESPUÉS del dictamen favorable del verifier (§9.1), con esta secuencia:
staging por rutas explícitas (`tests/unit/test_pytest_schema.py`,
`docs/…/REANCLAJE-14-L4-ORACULOS.md`, nota sucesora en
`docs/…/REANCLAJE-13-L4-ADJUDICACION.md`); commit convencional con byline; hooks
activos (tier fast + commitizen); push normal a `codex/reanclaje-p03a-fase1`;
**PR #56 permanece en borrador**. Sin código experimental ni artefactos masivos;
sin bless. El resultado real del push y de la CI se reporta en la entrega del
encargo, no aquí: este registro no anticipa estados. El fallo preexistente de
`commit-gates` (G-META-1) no se manipula ni se anticipa.

## 11. Entrega (resumen ejecutivo)

1. Base `1d01ff3c…` == headRefOid PR #56 (borrador); corte técnico `0487448…` solo
   docs por delante. 2. Custodia R12 corregida documentalmente: desfase = 2 filas
   PUB post-sello, demostración byte-exacta (ledger por prefijo; state por
   reconstrucción hasheada), histórico 91/93 intacto, manifiesto sucesor 93/93
   (`4c8c0c06…`). 3. Selección ampliada 152 = 140 ∪ 12 (intersección 0), digest
   `a75bc470…`, colección y baseline ORIGINAL verde. 4. 9 tests nuevos (15 oráculos
   + 1 control), solo en `test_pytest_schema.py`, nacidos verdes, con contrato
   citado por test. 5. Sensibilidad 15/15 rojos por causa prevista. 6.
   `expected_seq=1`: control separado, perturbación de una línea en copia
   desechable, roja; no cuenta como ID/kill. 7. Atribución: canal INERTE
   (estructural + empírico); propuesta de reclasificación 11 → equivalencia por
   canal inerte, decisión humana pendiente; contrato nuevo la haría reparación de
   producto. 8. Equivalencias propuestas: 12 de R13 + 11 reclasificables; timeout:
   texto de decisión D-C' entregado; 20000 es contractual (§3 l.157 — corrección a
   R13). 9. Batería completa verde salvo G-META-1 PREEXISTENTE en base (también
   rojo en CI del PR); presupuesto dentro de sobres. 10. Próximo incremento mínimo:
   decisión humana D-A' (equivalencias 12+11), D-B' (atribución), D-C' (timeout),
   D-D' (sitios de módulo: transcripción _CATALOG/_CAPPED, frontera real 20000) —
   y SOLO ENTONCES la única campaña completa L4 autorizada sobre selección 152 +
   9 tests nuevos, con expectativa medible: 8 + 15 mueren, 426+1 sin cambios no
   forzados, 46 → 23 sobrevivientes esperados (12+11 pendientes de decisión).
