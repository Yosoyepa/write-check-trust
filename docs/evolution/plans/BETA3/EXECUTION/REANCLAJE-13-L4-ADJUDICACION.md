# Registro REANCLAJE-13 — adjudicación de los residuos L4, huecos de selección y resolución del timeout (2026-09-19)

Estado: **adjudicación técnica sustentada de los 46 sobrevivientes L4 + propuesta
de disposición del timeout + desglose de los 14 sitios de módulo no
instrumentados.** Sin reparaciones, sin tests nuevos, sin ratificaciones, sin
campañas, sin avance a L3. El bruto L4 se conserva **exacto**: 473 = 426
killed + 46 survived + 1 timeout. Las decisiones humanas quedan enumeradas y
PENDIENTES. L2 permanece cerrado; L4 sigue detenido con residuos
(FAIL-survivors-stop en los términos de R12), ahora con adjudicación técnica.

## 1. Base, aislamiento y expediente

| Elemento | Identidad | Comprobación |
|---|---|---|
| Base documental | `d84fbf5a8dce82d4b0435a1f2d76e11943b8af55` = origin = headRefOid PR #56 (borrador) | `git ls-remote` + `gh pr view 56` |
| Corte técnico L4 | `0487448032c1e1cf56bd18f98f9bea9586f3fc46`; delta técnico→documental = exactamente el registro R12 (solo docs; sin cambios de fuentes/tests/receta/precondiciones) → traslado de evidencia admisible | `git log 0487448..d84fbf5` |
| Manifiesto R12 | digest completo `5229c127922106f337fb56c2297f4f93b365e5a5cf359bc2912b7cc7476b0300` (verificado, no completado de memoria); **91/93 miembros verifican hoy** — `logs/00-ledger-guardian.csv` y `guardian-state.json` de R12 derivan por exactamente las 2 filas PUB del fast escritas DESPUÉS del sellado (derivación benigna y reconstruible: el ledger menos esas 2 filas reproduce el digest; hallazgo H2 del verifier) | `sha256sum` + `sha256sum -c` + reconstrucción |
| Copia de trabajo | `build/tmp/reanclaje13-20260918/` (Git propio en `repo/`, detached d84fbf5; `run/` copiada del expediente R12) — expediente R12 INTACTO | hash de las 3 instrumentadas == custodia R12; fuentes == sellos |
| Árbol instrumentado | reutilizado por identidad (autorización §7 del encargo): 3 instrumentadas byte-idénticas a `custodia/instrumentado-*.py` de R12; inventario/diffs/stats copiados de la custodia R12 | `cmp` + sha256 |

Checkout principal, índices, sellos históricos, main, tag y release:
intactos. Sin lectura de credenciales.

## 2. Reconciliación por capas (bruto preservado)

| Capa | Contenido |
|---|---|
| **A. Estado del instrumento (bruto)** | 473 = **426 exit 1 + 46 exit 0 + 1 exit −24** (`x__consume_line__mutmut_22`). El timeout NO se reescribe como killed dentro del bruto. Los 426 históricos no se reabren. Recalculado aquí desde `meta-final` de R12: 46 IDs únicos == survived, 1 == timeout, 473 ∈ inventario, 0 solapes, diff y hash por ID en custodia. Sin discrepancias con lo comunicado. |
| **B. Atribución causal (R12)** | 426 KILLED-EVIDENCIADO; 1 KILLED-EVIDENCIADO por no-terminación (sonda); 46 SURVIVED-REPRODUCIDO (sonda 46/46). |
| **C. Admisión contractual propuesta (este registro)** | Hueco de selección (8), hueco de oráculo (17), equivalencia propuesta (10), comportamiento no contratado (11), timeout: admisión como defecto detectado PROPUESTA (§5). |
| **D. Decisión humana** | PENDIENTE en todos los casos de C que la requieren (ratificaciones, contratos nuevos, disposiciones, admisión del timeout). Nadie la concede aquí. |

## 3. Revisión de la selección primero (método)

Batería experimental pertinente (NO versionada, registrada en el expediente):
**293 nodeids** = 155 case-IDs PA01–PA12 + 26 fases + 112 schema
(`custodia/bateria-293.nodeids`, digest `bfdf5593…`), colección y **ORIGINAL 293 passed** (control verde). Cada uno de
los 46 sobrevivientes se ejecutó contra la batería completa con activación
acreditada (46 corridas, `logs/03-*`): **8 mueren** (tests existentes fuera de
la selección L4) y **38 sobreviven la suite pertinente completa**. Cero fallos
dentro de la selección histórica 140 (sin contradicción con la campaña).
Resultado por ID: `logs/04-discriminacion-bateria.json`. La asociación de
función NO se usó como sensibilidad: se midió ejecución real.

## 4. Adjudicación de los 46 (resumen; detalle por ID en `logs/07-adjudicacion-46.json`)

| Clase | # | IDs (sufijo) | Base |
|---|---:|---|---|
| **HUECO-DE-SELECCIÓN** | 8 | `decode_event_59/65`, `inventory_key_2/5/6/7/13/14` | matados por tests EXISTENTES omitidos de la selección L4: familias **PA09-\*-exact** y **PA10-\*-plus-one** (inventarios exactos / frontera +1 del reconstructor). Sensibilidad medida con la selección mínima de 12 nodeids: **8/8 rojos** (`logs/06`). Grupo F de R12 NO era uniforme: 12/15/9 sobreviven (defaults jamás usados) mientras 13/14/2/5/6/7 mueren. |
| **HUECO-DE-ORÁCULO bajo contrato vigente** | 15 | `execution_index_3/5/7/8` + `attributed_execution_3` (caso: ex no-entero → `invalid_field` sin crash; hoy NINGÚN caso envía ex no-entero — PA03-bool-int ejercita un bool en el PAYLOAD); `resolve_field_nodeid_6/7/8` (nodeid índice no-entero); `check_sequence_1` (seq=0/negativo); `check_sequence_7` + `advance_local_11` (frontera SEQ_MAX exacta); `validated_vector_19/20` (índice nodeid > SEQ_MAX → invalid_field: el guard mutado salta el `_int_in`); `decode_event_3` + `bad_execution_1` (vector/entrada como objeto JSON — contrato §4: «vector con objeto en lugar de array es invalid_field») | contrato vigente fija el comportamiento; falta el caso que lo ejercite. Tests propuestos en §8. |
| **EQUIVALENCIA ACOTADA PROPUESTA** (ninguna ratificada) | 12 | `validated_vector_13/16/17` + `match_executions_10/13/14` (strict de zip tras raise de longitud DESIGUAL previo EN LA MISMA FUNCIÓN — el strict nunca puede dispararse); `inventory_key_9/12/15` (default de `getattr(payload,"phase",…)` jamás usado: el guard `cls is PhaseMake or PhaseLog` solo deja pasar clases con `phase: str` REQUERIDO — payload_classes L165+); `validated_vector_24/25` (asignación a clave basura: el RHS `_int_in(...)` se evalúa IDÉNTICO —raise incluido— y la clave destino es inerte para los builders por clave; reclasificación H1 del verifier); `bad_wire_strings_5` (`wire[2:6]` truncado por `len(wire)!=5` que raise antes; `_EVENT_VECTOR_FIELDS=5` y el literal de ejecuciones tiene exactamente 5) | fundamento estructural + dominio + invalidantes por ID en `logs/07`. Invalidantes comunes: reordenar/quitar el chequeo previo de longitud; admitir en el guard una clase sin `phase`; cambio de aridad. Contraejemplos fuera del dominio declarados (p. ej., zip sobre iterables sin len — no ocurre: listas/tuplas). **No se transfieren las ratificaciones de L2.** |
| **COMPORTAMIENTO NO CONTRATADO** | 11 | `decode_event_19/20/39`, `execution_index_4/6/14/16`, `finish_5`, `attributed_execution_2/4/5` — el canal de **atribución** (`finding.execution_id` de decoder) | el campo es público con TIPO contratado (§2 l.67 «str o None») y tiene un **consumidor real**: `_decoder_blocks` (`pytest_observation.py:130`) decide `protocol_complete` POR EJECUCIÓN leyendo `finding.execution_id in (None, execution_id)`; pero el contrato NO fija regla de atribución del valor (grep «atribu» en PROPUESTA-P03: 0). La batería completa no discrimina (los case-IDs con finding no aseveran la atribución ni el bloqueo por ejecución). No es equivalente ni exclusión: es un canal observable SIN línea contractual. Si el humano contrata «un finding de decoder con execution_index válido lleva la atribución de esa ejecución y solo bloquea a esa ejecución», estos 11 pasan a hueco-de-oráculo. |
| LIMITACIÓN INSTRUMENTAL | 0 | — | — |
| INCONCLUSO | 0 | — | — |

Evidencia por ID (capas): campaña R12 exit 0 + sonda fresca SURVIVED-REPRODUCIDO
(R12 logs/13) + batería 293 exit 0 (R13 logs/04) + la específica de la tabla.
Ninguna sonda sin divergencia se usó como equivalencia: las equivalencias
propuestas descansan en fundamento estructural.

## 5. Timeout `x__consume_line__mutmut_22` — propuesta de disposición

**A. Hecho instrumental.** Estado mutmut: **timeout** (taxonomía del propio
mutmut: −24 = SIGXCPU). Mecanismo exacto: `resource.setrlimit(RLIMIT_CPU, …)`
por mutante (`mutmut/__main__.py:1483-1487`), límite =
`ceil((estimated_time_of_tests + timeout_constant) × timeout_multiplier × 2 +
process_time())`; el kernel señala SIGXCPU (exit −24) y mutmut remata con
SIGKILL un segundo después. Duración registrada 117.3 s. El límite es DEL
ARNÉS, no del producto. Limpieza: R12 mató a su hijo directo; los nietos
huérfanos detectados por el verifier final de R12 fueron terminados; el
guardián de R13 usa grupos de proceso (`start_new_session` + `killpg`).

**B. Causa (lectura de control de flujo + evidencia).** Diff: `if defect is
not None:` → `if defect is None:`. En el original, una línea limpia avanza
(retorna `line_end + 1`); en el mutante, la línea limpia retorna
`(None, offset)` **sin decodificar y sin avanzar**. El bucle público de
decodificación (`pytest_schema.py`) vuelve a llamar `_consume_line` con el
MISMO offset: el estado se repite idéntico → **no-terminación real**, no un
bloqueo ambiental: el ORIGINAL con el mismo test, entorno e imports termina en
2.78 s (verde), y el mutante es matado a los 30 s en la misma sonda (R12
logs/13; réplica del verifier final). La entrada empleada (`PA02-invalid-utf8`)
provoca el ciclo en la PRIMERA línea limpia (la cabecera válida del journal).

**C. Contrato.** §4 obliga al decoder a RETORNAR la observación
(events/findings/consumed_bytes/tail) para cualquier entrada: la terminación
es condición de la obligación de salida, no un SLA. Ningún límite de tiempo
 contractual existe; el de 117 s es del arnés. El mutante además invierte la
gestión del defecto (procesa líneas defectuosas y congela las limpias).

**Propuesta: NO-TERMINACIÓN CAUSAL DEMOSTRADA, CANDIDATA A ADMISIÓN COMO
DEFECTO DETECTADO.** Criterio propuesto para la decisión humana (D-pendiente):
«un mutante que vuelve no-terminante una función cuya obligación contractual
es retornar para toda entrada cuenta como detección válida, con evidencia de
original terminante en idéntico entorno». **El bruto conserva su estado
timeout** aunque se admita. Alternativa (si el humano lo rechaza): timeout
instrumental — pero la evidencia de B la contradice.

## 6. Los 14 sitios de módulo no instrumentados (desglose)

Métrica del motor (verificada 247 = 72+94+81): módulo aporta 1 (header) + 1
(events) + 12 (sequence) = 14. Ubicaciones y propuesta:

| Grupo | Ubicaciones | Obligación/consumo | Tests que observan | Propuesta mínima (NO implementada) |
|---|---|---|---|---|
| Docstrings de módulo (3) | header L1, events L1, sequence L1 | sin efecto conductual identificado | ninguno | documentar como limitación instrumental; **no inventar equivalencias** |
| Catálogo `_CATALOG` (1: DictComp events L37) | deriva de `EVENT_CATALOG` (fuente de otro lote) | consumo real: `_CATALOG[code]` en `_decode_event` (miembro→`unknown_event`; unpack origin/kind/cls) | PA03-event-code (memberships) y todos los journals válidos (consumo posicional de origin/kind) | test de transcripción tipo R10-WIRE_FIELDS: literal independiente del catálogo §3 (códigos→(origin,kind,clase)) + consumo posicional distinguible |
| Constantes de tope (2) | sequence L19 `MAX_DECLARATIONS=20000`, L21 `MAX_INVENTORY_ENTRIES=10000` | §4: «inventario excediendo10000 limit_exceeded» — **10000 es contractual**; 20000 (tope de declaraciones) sin línea literal en §4 | ninguno en la frontera (los PA10-plus-one ejercitan exactitud de conteos, NO el tope) | frontera contractual: journal con 10001 items de un tipo → `limit_exceeded` (~400 KB, factible); decisión humana para 20000 si se contrata |
| Tabla `_CAPPED` (5) | sequence L24-28 (clase→clave) | semántica: qué clases tienen inventario con tope y bajo qué clave (fases por nombre) | PA09/PA09-exact y PA10-plus-one ejercitan el CONSUMO (`_inventory_key`) — tras la reparación mínima de §8, el consumo queda sensible | opcional test de transcripción de la tabla; el consumo ya cubierto por la reparación |
| Estado de dataclasses (resto hasta 12) | sequence L34-L51: docstrings de clase ×2, `expected_seq=1`, `field(default_factory=…)` ×4 | `expected_seq=1` es contractual (§4 «seq global contiguo desde 1»); factories = estado inicial del decoder | seq≠1 en primer evento: PA03-global-seq-gap parte de 1 — **falta caso con PRIMER seq≠1**; factories ejercidas por todo journal con inventarios/declaraciones | test: primer evento con seq=2 → `sequence_error` (cubre el default) |

Sitios ≠ mutantes faltantes: 14 sitios de módulo generan 0 IDs (mutmut 3.7 no
instrumenta cuerpos de módulo). Cero IDs no es cobertura ni equivalencia.

## 7. Reparación mínima propuesta (NO implementada) y decisiones humanas

**R1 — Selección (corrige 8 IDs sin tocar tests).** Incorporar a la selección
L4 los **12 nodeids** existentes de PA09/PA10 que matan a los 8
(`custodia/reparacion-minima-12.nodeids`): PA09-deselected/items/phase-log/
phase-make/selected/test-end/test-start-exact + PA10-phase-log/phase-make/
selected/test-end/test-start-plus-one. Sensibilidad MEDIDA 8/8 (logs/06).
Requiere re-campaña L4 futura para hacerla valer en bruto.

**R2 — Oráculos nuevos (17 IDs + 1 sitio de módulo).** Tests mínimos (rutas
aprobadas, estilo R9): (a) ex no-entero → `invalid_field` sin crash [mata 5];
(b) nodeid índice no-entero → `invalid_field` [3]; (c) seq=0 → invalid_field
[1]; (d) seq==SEQ_MAX y local==SEQ_MAX válidos [2]; (e) índice nodeid
SEQ_MAX+1 → invalid_field [2: solo 19/20; 24/25 reclasificados a equivalencia (H1)]; (f) vector-objeto (evento y entrada de
ejecuciones) → invalid_field sin crash [2]. Más (g) primer evento con seq≠1
→ sequence_error [sitio de módulo expected_seq=1]. Expectativas NO ejecutadas
(aquí no se implementan); presupuesto futuro estimado: ~40 s de corridas.

**R3 — Timeout.** Decisión humana de admisión (criterio en §5C). El bruto
conserva timeout.

**R4 — Equivalencias (10).** Ratificación humana por grupo o por ID con los
fundamentos/invalidantes de `logs/07` (no se transfieren las de L2).

**R5 — Atribución (11).** Decisión humana: contratar la regla de atribución
de findings de decoder (→ convierte en hueco-de-oráculo con test de bloqueo
por ejecución) o preservar como canal no contratado (→ disposición explícita,
precedente L2 §5.2 solo como método, no como ratificación transferida).

**R6 — Código no instrumentado.** Decisión humana sobre las propuestas de §6
(transcripción de `_CATALOG`, frontera 10000, seq≠1; docstrings documentados).

## 8. Presupuesto (guardián monotónico, `logs/00`)

S (sondas autor, 480 s): sync 1.12 + ORIGINAL batería 6.98 + 46
discriminaciones ≈ 396 + 8 sensibilidad mínima ≈ 18 + márgenes ≈ **425.2 s** ✔.
SV (reserva verifier): 120 s — intocado hasta su ejecución. PUB: 180 s (fast).
Total agregado ≤ 600 + 180 como autoriza el encargo. Sin mutmut run, sin
regeneración, sin campaña. Intentos inválidos: 0 (una corrección de nombre de
variable en un driver ANTES de ejecutar, sin costo). Limpieza: guardian con
grupos de proceso propios.

## 9. Verifier independiente — DICTAMEN FAVORABLE

Verifier distinto del autor, solo lectura, copia propia (51.13 s de SV).
**DICTAMEN: FAVORABLE al expediente.** Recalculó bruto (426/46/1 exactos),
tabla 46, selecciones (12 ∈ batería ∉ selección 140), reclamos documentales
6/6 (grep «atribu» 0; `_decoder_blocks`; bool_int es payload; phase
requerido; aridad 5; builders por clave) y presupuesto fila a fila.
Reejecutó: 2 huecos-de-selección (exit 1 con causa contractual
`limit_exceeded` de más contra `findings == ()`) + ORIGINAL verde;
`match_executions_14` sin divergencia (94 asociados); la no-terminación
(mutante rc −9 a los 25 s vs original 1.00 s); y `check_sequence_7` contra la
batería completa 293 (exit 0 → confirma hueco de oráculo). **Hallazgos**: H1
(menor SUSTANTIVO, ACEPTADO y corregido: `validated_vector_24/25`
reclasificados de hueco-de-oráculo a EQUIVALENCIA-PROPUESTA — conteos 15/12;
la expectativa del prompt R14 se ajustó a «los 15+1 mueren»); H2 (la cifra
«93/93» corregida a 91/93 con la derivación benigna post-sello explicada en
§1); H3 (artefacto renombrado a bateria-293); H4 (anotación de ledger
preexistente en R12, solo trazabilidad). El expediente R12 permanece intacto.
Informe: `build/tmp/reanclaje13-20260918-verifier/INFORME-VERIFIER.md`. **No
ratifica equivalencias, no admite el timeout, no cierra L4.**

## 10. Publicación

Ruta versionada nueva: `REANCLAJE-13-L4-ADJUDICACION.md` + **nota sucesora
acotada** en `REANCLAJE-12-L4-DECODER-RESULTADO.md` (aclara bruto-timeout vs
clasificación causal; sin borrar ni reescribir resultados sellados).
Staging exclusivo de esas rutas; commit convencional con byline; hooks
activos; push normal; PR #56 en borrador; fast bajo PUB; CI observada.
Manifiesto R13 sin auto-hash, digest y verificación fuera de sus miembros.

## 11. Entrega (resumen ejecutivo)

1. Base: técnico `0487448` / documental `d84fbf5` (= publicado al cierre de
   este registro). 2. Bruto preservado 473=426+46+1. 3. Reconciliado y
   adjudicado: 8+15+12+11 (+1 timeout propuesto a admisión; reclasificación H1:
   validated_vector_24/25 de oráculo a equivalencia). 4. Tests
   existentes omitidos: 12 (PA09/PA10) frente a oráculos faltantes: 7 familias
   de casos nuevos. 5. Timeout: no-terminación causal demostrada; decisión
   humana de admisión pendiente; bruto intacto. 6. Sitios de módulo:
   desglosados y con propuesta. 7. Próxima autorización mínima: prompt del
   §12. Detalle completo en las secciones precedentes.

## 12. Prompt propuesto para el único siguiente incremento — NO EJECUTAR

> **Encargo REANCLAJE-14 — reparación de selección L4 y oráculos de frontera
> del decoder.** Sobre el headRefOid vigente de PR #56: (1) re-campaña L4 con
> la selección 140 ∪ los 12 nodeids PA09/PA10 (digest a congelar; baseline
> verde; receta y sobres herederos R12); expectativa medible: los 8
> huecos-de-selección mueren, los 426+1+38 restantes sin cambios no forzados.
> (2) TDD: implementar SOLO los tests (a)–(g) de R13 §7-R2 (corregido por H1: (e) mata 2) en
> `tests/unit/test_pytest_schema.py` (ruta aprobada), cada uno con entrada y
> código esperado del catálogo §4, con selección re-congelada y segunda
> re-campaña; expectativa: los 15+1 mueren. (3) NO ratificar equivalencias ni
> disponer el canal de atribución: tras las campañas, expediente de decisiones
> humanas D-A' (10 equivalencias), D-B' (atribución 11), D-C' (admisión del
> timeout) y D-D' (sitios de módulo), por ID, con diffs y fundamento de R13.
> Prohibido: producto, binding, L3, Q-ACCMUT, bless, merge, release.
