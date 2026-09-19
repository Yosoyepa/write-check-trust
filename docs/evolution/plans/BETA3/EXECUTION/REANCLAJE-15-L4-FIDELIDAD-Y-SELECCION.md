# Registro REANCLAJE-15 — fidelidad del oráculo de nodeid, reconciliación de tres IDs y selección definitiva (2026-09-19)

Estado: **frontera de prueba resuelta, tres IDs reconciliados, selección definitiva
congelada.** El test de frontera de módulo de R14 fue RETIRADO por infiel al
producto (estado inalcanzable por los llamadores admitidos, sin contrato
independiente) y sustituido por una caracterización por API pública. Los tres
mutantes asociados SOBREVIVEN bajo la selección corregida y se proponen como
equivalencia observable acotada — SIN ratificar. El bruto L4 se conserva exacto:
473 = 426 killed + 46 survived + 1 timeout. Sin campaña, sin producto, sin
contratos nuevos, sin bless. Esto NO cierra L4.

## 1. Base, identidad y aislamiento

| Elemento | Identidad | Comprobación |
|---|---|---|
| Cabeza comunicada R14 | `2fe18efe671ac5b7928843d1d278d29443dd2983` resuelta; == remoto `codex/reanclaje-p03a-fase1` == headRefOid PR #56 (borrador, OPEN). **Sin avance**: nada que clasificar | `git ls-remote` + `gh pr view 56` |
| main de referencia | `8a379d64ba13bbe43a707fcfd8df0ea336dd97ed` == baseRefOid del PR; **merge-base rama/main = main** (la rama está estrictamente por delante); tag `v1.0.0b3.dev1` = `5aeb9ce…`, intocado | `git merge-base` |
| Corte técnico L4 | `0487448032c1e1cf56bd18f98f9bea9586f3fc46` (sin cambios; las 3 fuentes sellan idénticas) | sha256 de run/tools |
| Copia de trabajo | `build/tmp/reanclaje15-20260919/` (Git propio en `repo/`, detached 2fe18ef; `run/`+`run/mutants/` del expediente R14, re-verificados: 3 instrumentadas byte-idénticas a custodia R12; fuentes originales == sellos) | `cmp` + sha256 |
| Lanzador R15 | fail-closed heredado de R12–R14 MÁS un control nuevo: el archivo de tests de `mutants/` debe ser byte-idéntico al corregido del `repo/` (los tests que pytest usa están acreditados) | §6 |

Checkout principal, índices ajenos, expedientes históricos, main y tag: intactos.
Sin lectura de credenciales. Runtime: venv propio del expediente (`uv sync
--all-groups`); PATH y PYTHONPATH controlados por el lanzador; imports acreditados
resolviendo dentro de `mutants/`.

## 2. Revisión decisiva del test cuestionado — DECISIÓN: RETIRAR

Pregunta: ¿puede la entrada `{"nodeid": "0"}` (índice no-entero) llegar a la
guardia `type(index) is not int` de `_resolve_field_nodeid` por algún camino
admitido, y existe un contrato independiente que obligue al helper a diagnosticarla?

**Trazado del autor y auditoría documental independiente coinciden (dos análisis
separados, mismas conclusiones):**

- **(a) Llamadores reales.** Exactamente UNO productivo: `_build_payload`
  (`pytest_decode_events.py:55-56`), llamado solo por `_decode_event` (l.85),
  que siempre ejecuta `_validated_vector` (l.84) antes, en línea recta. Ningún
  otro llamador en src/tools/tests; el helper no está exportado (`__init__.py`
  sin símbolos; `__all__` de pytest_schema no lo incluye). `reconcile_pytest` y
  la validación manual de observations no invocan al resolvedor (el nodeid de las
  dataclasses es string; la resolución de índices es exclusiva del decoder).
- **(b) Entradas alcanzables.** Ninguna. Para TODA clase con `"nodeid"` en
  WIRE_FIELDS salvo NodeDeclaration, `_validated_vector` aplica
  `fields["nodeid"] = _int_in(fields["nodeid"], 0, SEQ_MAX)` incondicionalmente
  (l.48-49); `_int_in` rechaza todo no-entero (bool incluido) y devuelve int
  exacto. NodeDeclaration queda excluido por la doble guardia idéntica
  `cls is not NodeDeclaration` (l.48 y l.55). La condición de llamada del helper
  es la MISMA que la del coerce previo.
- **(c) Alteración intermedia.** Ninguna: solo dos asignaciones a
  `fields["nodeid"]` en el producto — la del coerce (int exacto) y la del nodeid
  resuelto (después de la guardia). Entre validación y resolución hay cero
  instrucciones.
- **(d) Contrato independiente.** Ausente. §3 l.154-155 «nodeid de toda clase
  salvo NodeDeclaration viaja como índice entero a tabla global anterior»; §4
  precedencia 3 (l.255) pone rangos del payload y referencia nodeid en el MISMO
  escalón, con l.272 «Tipo/rango JSON errado invalid_field» — el contrato fija el
  observable público (finding `invalid_field`), no el módulo interno que diagnostica.
  §9 es íntegramente de API pública; DECISION-P03a nada añade. (Precisión sobre
  R14: citó «§4 precedencia 4»; la cita correcta de «referencia nodeid» es
  precedencia 3.) La línea §3 l.157 (20000 declaraciones) es ajena a este punto.

**Decisión ejecutada (autorizada por el encargo §3):** se RETIRÓ
`test_resolve_field_nodeid_non_integer_index_is_invalid_field` (el estado que
introduce es rechazado por todos los caminos admitidos antes del helper) junto con
los imports que quedaron huérfanos (`pytest_decode_events as pdev`,
`_DefectError`; verificados por grep: cero usos restantes). La guardia productiva
NO se tocó; el decoder no se refactorizó. La obligación pública quedó cubierta
(§4 del encargo): no existía prueba conductual previa (PA03-bool-int lleva el
bool en el PAYLOAD de plugins_end, no en el índice de nodeid;
PA03-node-reference-missing usa índice int fuera de tabla → foreign_reference),
así que se añadió la caracterización mínima autorizada:

- `test_nodeid_index_non_integer_is_invalid_field` — journal real por
  `decode_pytest_journal` con helpers existentes: declaración válida + item con
  índice `"0"` (string) → `events == 1`, `findings[0].code == "invalid_field"`.
  Nace verde (0.96 s, 9/9 del bloque). NO mata a los tres mutantes (muere en el
  coerce del vector, antes del helper) y NO se presenta como sustituto de
  aquella sensibilidad: es la obligación pública, no la guardia interna.

## 3. Reconciliación de los tres IDs — SIN RATIFICAR

Fuente de identidad: inventario nuevo sellado + diffs de custodia (byte-idénticos
a R12). Fuente hash `d73b5b2682684774b40c89d3d61ed46e0ba23adc926377f5dca3dd7c3d52e826`
(`tools/wct/evidence/pytest_decode_events.py`).

| ID completo | Diff exacto | Test que lo detectaba en R14 | Frontera ejercitada | Resultado bajo selección corregida (161) | Clase propuesta |
|---|---|---|---|---|---|
| `tools.wct.evidence.pytest_decode_events.x__resolve_field_nodeid__mutmut_6` | `raise _DefectError("invalid_field")` → `raise _DefectError(None)` | el test retirado (llamada directa con `{"nodeid": "0"}`) | ninguna contractual: rama `type(index) is not int` inalcanzable por los llamadores admitidos | **SOBREVIVE** (161 passed, rc=0, sonda con activación acreditada) | EQUIVALENCIA-OBSERVABLE-ACOTADA |
| `…x__resolve_field_nodeid__mutmut_7` | → `raise _DefectError("XXinvalid_fieldXX")` | idem | idem | **SOBREVIVE** | EQUIVALENCIA-OBSERVABLE-ACOTADA |
| `…x__resolve_field_nodeid__mutmut_8` | → `raise _DefectError("INVALID_FIELD")` | idem | idem | **SOBREVIVE** | EQUIVALENCIA-OBSERVABLE-ACOTADA |

Fundamento de la clase propuesta: la mutación solo altera el diagnóstico (el
código alzado) de una rama que ningún llamador admitido alcanza (§2 a-c);
el observable público es idéntico porque el coerce del vector produce el mismo
`invalid_field` antes. Invalidantes: (i) un llamador admitido nuevo que pase el
nodeid sin validar; (ii) un contrato que obligue al resolvedor como unidad;
(iii) refactor que exponga el helper. **Esta propuesta NO queda ratificada por
este encargo**; es deuda de sensibilidad (TEST-002) en rama muerta, no defecto
conductual. La supervivencia se informa como es: tres sobrevivientes más que la
campaña futura verá como survived salvo ratificación previa.

## 4. Sensibilidades — separación explícita (corrección histórica de R14)

La frase «15/15 sensibilidad medida» de R14 se conserva con su límite: era
sensibilidad FRENTE A LOS TESTS DE R14, no quince defectos del contrato público.

- **Sensibilidades contractuales vigentes (12 IDs, oráculos fieles conservados):**
  `attributed_execution_3`, `execution_index_3/5/7/8` (ex no-entero → invalid_field
  sin crash); `check_sequence_1` (seq=0); `check_sequence_7`, `advance_local_11`
  (fronteras SEQ_MAX); `validated_vector_19/20` (índice > SEQ_MAX, precedencia
  3-antes-que-4); `decode_event_3`, `bad_execution_1` (vector-objeto, cláusula
  literal §4). Más el control separado `expected_seq=1` (sitio de módulo, sin ID).
- **Sensibilidad RETIRADA por infiel (3 IDs):** `resolve_field_nodeid_6/7/8` —
  solo detectables mediante un estado que el producto no admite; ver §3.
- **Sensibilidades por ampliación de selección (8 IDs, R13):** intactas, mediadas
  por los 12 PA09/PA10, sin re-demostrar.
- **Equivalencias propuestas (12, R13):** intactas, pendientes de D-A'.
- **Equivalencias propuestas por canal inerte (11, R14 §7):** intactas,
  pendientes de D-B'. Cada diff concreto conserva su justificación de no-activar
  el canal (el valor es constantemente None en todo camino alcanzable); NO se
  reabrieron sus experimentos (sin invalidante nuevo).
- **Timeout causal (`x__consume_line__mutmut_22`):** bruto timeout conservado;
  admisión propuesta (D-C') sin aprobar; no reejecutado.

## 5. Selección definitiva L4

Derivada por UNIÓN DE CONJUNTOS y ACREDITADA POR COLECCIÓN REAL (ningún número
anticipado): 140 históricos (R12, digest `9b96790c…`) ∪ 12 PA09/PA10 (R13,
digest `ac70d539…`) ∪ 9 casos nuevos pertinentes tras la corrección (los 8
oráculos fieles de R14 + la caracterización pública nueva; el test retirado NO
participa) = **161 nodeids**. Intersecciones 140∩12 = 140∩9 = 12∩9 = ∅; sin
duplicados; altas netas respecto de R14: +1 (`test_nodeid_index_non_integer…`),
bajas netas: −1 (`test_resolve_field_nodeid…`); colección real: **161/161
collected** en el árbol acreditado.

- Archivo: `custodia/seleccion-L4-final.nodeids`, digest
  `51674414fbfcdbcec64ac1125e5e199e1dbbb109a915cd7c5f54b75e1b1ef350`.
- **ORIGINAL con la selección completa: 161 passed, rc=0, cero fallos, cero
  skips, cero xfails** (logs/04). La selección focal no acredita el gate
  completo; la batería de §7 sí corrió.

## 6. Sondas acotadas y activación (presupuesto S)

Tres sondas de los IDs + controles, todas con el lanzador fail-closed (ID ∈
inventario; 3 fuentes originales == sellos; 3 instrumentadas byte-idénticas a
custodia R12; tests de mutants == archivo corregido del repo; selección no vacía;
`MUTANT_UNDER_TEST` verificada por sonda ambiental en el MISMO entorno del hijo;
imports resolviendo en mutants/): ORIGINAL 9/9 verde (antes) y 161/161 verde
(después); los 3 IDs → rc=0 (sobreviven, §3); **canario ya acreditado**
`x__check_sequence__mutmut_7` + su test conservado → rc=1 (la instrumentación
mata cuando hay sensibilidad real: la activación está acreditada y el verde de
los 3 IDs no es un verde del original). Sin `mutmut run`, sin regeneración, sin
otros mutantes, sin sondas del timeout. Selección vacía o activación ausente
abortan con exit 2 antes de producir evidencia (heredado del lanzador).

## 7. Batería, presupuesto y gates

| Paso | Resultado |
|---|---|
| Colección ANTES (base 2fe18ef) | 1206 tests (R14; identidad del SHA publicada, sin re-correr) |
| Colección DESPUÉS (corregido) | **1206 tests collected** (rc=0); conciliación por nodeid: −1 retirado, +1 caracterización, resto idéntico |
| Selección L4 final (161) sobre ORIGINAL | 161 passed, rc=0, **0 fallos / 0 skips / 0 xfails** |
| Focales (schema + observation) | **423 passed** (rc=0) |
| Suite normativa (`-m "not property"`) | **1205 passed, 1 deselected** (rc=0) |
| Property separada (`-m property`) | **1 passed** (rc=0) |
| Ruff (invocación exacta del gate, `--config governance/lint/ruff.toml`) | limpio en el diff y en el repo |
| `wct gate --tier fast` | **rc=0** (7/7 puertas: incluye ratchets de supresiones y deuda) |
| `wct gate --tier commit` | **20 PASS · 0 SKIP · 1 FAIL — solo G-META-1** |

**G-META-1 (fallo conocido del PR, no de main):** alcance RECALCULADO en el
árbol corregido: **36 rutas** (2 «modificado» — `governance/lint/vulture_whitelist.py`,
`tools/wct/accept/mutation_cases.py` — y 34 «nuevo protegido», los módulos P03a no
registrados en `governance/integrity.lock`). Coincide con la base 2fe18ef: NINGUNA
ruta es achacable al delta de R15 (tests+docs). main está limpio (0 violaciones).
No se reparó (fuera de allowlist; SEC-005). Ningún otro rojo: el único FAIL del
tier commit es este.

Presupuesto (guardián monotónico propio, grupos de proceso, sin saldos previos):
S ≤ 480, SV ≤ 120, I ≤ 900 (agregado autor+verifier), PUB ≤ 180. Cierre en §10.

## 8. Incidente de hooks de R14 — relato fiel

En R14, los hooks NO estaban instalados al crear el commit `2fe18ef` (clon
fresco sin `pre-commit install`); se instalaron y comprobaron DESPUÉS, antes del
push (cz check ✓ sobre el mensaje real; `pre-commit run wct-fast --all-files`
✓). Esas comprobaciones posteriores NO equivalen a ejecución de hooks durante
aquel commit: aquel commit se creó sin que ningún hook corriera. No se reescribió
historia ni se hizo force push. Para R15: hooks instalados y verificados ANTES
del primer commit, con evidencia de ejecución real (PUB), sin bypass.

## 9. Sitios de módulo y tabla de decisiones humanas

Estado documental (sin pruebas nuevas para tablas/topes en este encargo):
`expected_seq=1` — control conductual independiente, no mutante generado;
`_CATALOG`/`_CAPPED` — consumo cubierto (PA03-event-code/journals válidos;
PA09/PA10 vía `_inventory_key`), transcripción pendiente por identidad;
tope 10000 — frontera REAL medida en el wire (`test_wire_inventory_cap_at_the_real_boundary`
10 000 exacto / 10 001 → limit_exceeded), aparte de las pruebas con constantes
reducidas; tope 20000 — contractual (§3 l.157), probado hoy SOLO con constante
reducida (`test_declaration_limit_isolated_with_reduced_constant`); la frontera
real 20 000/20 001 queda PENDIENTE.

| ID/sitio | Propuesta | Fundamento | Precondiciones | Invalidantes | Evidencia | Aprobar / Rechazar |
|---|---|---|---|---|---|---|
| 12 equivalencias R13 (validated_vector_13/16/17, match_executions_10/13/14, inventory_key_9/12/15, validated_vector_24/25, bad_wire_strings_5) | D-A': ratificar por grupo o por ID | fundamento estructural + dominio + invalidantes por ID (logs/07 R13) | decisión humana explícita | reordenar/quitar chequeo previo; aridad; guardar clase sin phase | R13 §4 + logs/07 | aprobar → 12 survived quedan como equivalentes registrados; rechazar → permanecen survived con deuda TEST-002 |
| 11 por canal inerte (attributed_execution_2/4/5, decode_event_19/20/39, execution_index_4/6/14/16, finish_5) | D-B': reclasificar a equivalencia por canal inerte | atribución constantemente None en todo camino alcanzable (estructural + sonda); cada diff concreto no activa el canal | decisión humana explícita | poblar la atribución en producto; contrato nuevo de atribución (haría al original no conforme → reparación aparte) | R14 §7 + logs/08 | aprobar → 11 survived equivalentes; rechazar → volver a «no contratado» y disponer el canal |
| 3 de este registro (resolve_field_nodeid_6/7/8) | D-A'': equivalencia observable acotada (rama inalcanzable) | §2/§3 de este registro; sobreviven con activación acreditada | decisión humana explícita | llamador admitido sin validar; contrato del resolvedor como unidad; refactor que exponga el helper | §3 + logs/05,06 | aprobar → 3 survived equivalentes; rechazar → survived con deuda TEST-002 (guardia duplicada, decisión de producto) |
| Timeout x__consume_line__mutmut_22 | D-C': admisión como defecto detectado por no-terminación causal | §4 obliga retornar para toda entrada; original terminante en idéntico entorno (2.78 s vs SIGXCPU); límite 117 s es del arnés | decisión humana explícita | rechazar la causalidad; descubrir terminación del mutante | R12/R13 §5 + R14 §8 | aprobar → cuenta como detección (bruto conserva timeout); rechazar → disposition explícita de timeout instrumental |
| Sitios de módulo (_CATALOG, _CAPPED, 20000, docstrings) | D-D': transcripción de tablas y frontera real 20000; docstrings documentados | consumo ya cubierto; transcripción pendiente por identidad; 20000 contractual §3 l.157 | decisión humana explícita | cambio de catálogo/tabla/topes en producto | R14 §8 + §9 aquí | aprobar → habilita pruebas de transcripción/frontera en incremento propio; rechazar → quedan como limitación instrumental |

Cuatro aprobaciones SEPARADAS; ninguna se combina con otra. Ninguna queda
otorgada por este registro.

## 10. Verifier, presupuesto, sellos y publicación

**Verifier final — DICTAMEN FAVORABLE** (distinto del autor; sin escritura
versionada; copia propia; 9.71 s de sus 120). Derivó por sí mismo la
inalcanzabilidad (un llamador productivo; coerce incondicional con condición
idéntica a la de llamada; 0 menciones del resolvedor en el contrato); reejecutó
ORIGINAL 9/9, los 3 IDs (rc=0, SOBREVIVEN), canario rc=1 y la colección;
recalculó la unión (161, digest `51674414…`), el delta y G-META-1 (36 rutas,
ninguna del delta). **Hallazgo menor H8**: el registro se editó durante su
verificación (§7 pasó de placeholders a cifras reales de la batería); el
contenido final coincide con sus recálculos y el expediente queda CONGELADO a
partir de este cierre. No verificado por presupuesto/alcance: gates completos
(leyó logs del autor y recalculó G-META-1), bruto 473 (documental), main limpio,
CI (posterior). Informe:
`build/tmp/reanclaje15-20260919-verifier/INFORME-VERIFIER.md`. No cierra L4, no
ratifica equivalencias, no emite PASS de G-MUT.

**Presupuesto de cierre** (guardián propio; sin saldos previos): autor
S **20.94/480**, SV 0/120 (la reserva la consumió el verifier en SU ledger:
9.71/120), I **257.16/900** del autor + 9.71 del verifier = **266.87/900
agregados**, PUB: ejecutado tras el sellado en `logs-pub/` con sello sucesor
(máx 180). Intentos inválidos: 0.

**Sellos.** Manifiesto del expediente del autor generado con logs CERRADOS;
digest y verificación fuera de sus miembros; ninguna operación posterior
(hooks, ledger de publicación, seguimiento de CI) escribe sobre miembros
sellados — esa evidencia vive en archivos separados (`logs-pub/`) y, si se
precisa, en un sello sucesor sin sobrescribir el anterior.

**Publicación (tras el dictamen favorable).** Hooks instalados y verificados
ANTES del primer commit, con evidencia de ejecución real en `logs-pub/`; sin
bypass; dos commits (test + documental) con staging por rutas explícitas e
inspección de `--cached`; conventional commits + byline del rol; push normal;
**PR #56 permanece en borrador**. El resultado real de la CI del SHA publicado
se reporta en la entrega: los pasos omitidos por integridad son NO EJECUTADOS,
no éxitos ni fallos medidos.
