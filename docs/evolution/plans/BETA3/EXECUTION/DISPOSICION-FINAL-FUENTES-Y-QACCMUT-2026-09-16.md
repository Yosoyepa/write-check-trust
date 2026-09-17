# Disposición final de mutación de fuentes y Q-ACCMUT (2026-09-16)

Registro consolidado del encargo «consolidar las decisiones finales de mutación
de fuentes y, únicamente si queda acreditada esa puerta, ejecutar Q-ACCMUT».
Consolida las disposiciones por ID con su evidencia, el ledger por lote y la
frontera de alcance. **No** ejecuta campañas nuevas de fuentes, no ratifica
nada fuera de lo aquí registrado, no cambia producto, tests, features,
gobernanza, manifests, ratchets, lock ni versión, no bendice, no hace merge,
bump, tag ni release. Q-ACCMUT solo corre si la puerta previa queda acreditada
por verifier independiente; en caso contrario se declara NO EJECUTADO con
razón. El documento ajeno `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md`
permanece intacto, sin seguimiento y fuera del incremento.

## 1. Preflight e identidades

- Worktree `build/tmp/beta3-ac1-r2-integration`, rama
  `codex/beta3-ac1-r2-integration`. HEAD
  `3638cfaaefa3a45e32c4201029c4ce7c47f981b4` = `origin` =
  `headRefOid` de la PR #53 (OPEN; `mergeStateStatus` BLOCKED). Sin avances
  remotos posteriores al corte comunicado; sin reset, rebase, force push ni
  sobrescritura de trabajo concurrente. El checkout principal solo se consulta.
- Índice al iniciar y al cerrar: vacío salvo el untracked ajeno citado.
- Runtime acreditado: `.venv` del worktree (Python 3.13.14, pytest 9.1.1,
  mutmut 3.7.0), invocado con `UV_NO_SYNC=1` o por ruta; nada instalado ni
  sincronizado.
- Anclajes de fuentes vigentes (sha256 calculados en este preflight):
  `tools/wct/accept/process.py` `84b9340f…`, `campaign.py` `686070cd…`,
  `pytest_receipt.py` `d4f136ae…` — coinciden con el ancla del plan §3 y con
  los bytes usados por las sondas de las disposiciones. Evidencia r3 sellada
  `build/tmp/ac1-r2-qualification/evidence/mutation-code-lot-r3-survivor-diffs.log`
  sha256 `51d99c9b…` (coincide con el ancla de matriz/plan).
- La evidencia de sondas y campañas vive bajo `build/tmp/` (temporal). No se
  afirma custodia durable por conservarla; este registro no la convierte en
  producto.

## 2. Decisión A12 — registrada

La aclaración aprobada por el encargo es:

> «Cuando concurren el vencimiento del plazo y el exceso de salida, cualquiera
> de ambos motivos bloqueantes es válido. Deben respetarse el límite de bytes
> persistidos, la terminación acotada y la limpieza. Esta tolerancia no permite
> comenzar otra lectura una vez alcanzado el deadline y no altera el contrato
> de C2.»

**Comprobación de consumidores (previa a disponer).** No se infirió ausencia
de consumidores por búsqueda literal: se rastrearon todos los llamadores de
`run_process` y todos los usos de `reason` en `tools/` y `tests/`.

- `run_process` tiene un único consumidor productivo:
  `tools/wct/accept/campaign.py::_attempt` (línea 47).
- Usos productivos de `reason`:
  `campaign.py:48-49` (razón no vacía ⇒ `status="invalid"` y razón propagada),
  `campaign.py:82` (constante `"prior attempt did not pass protocol"`),
  `campaign.py:90` (propaga la razón del intento),
  `verdict_validation.py:23-24,49-50` (solo exige string no vacío),
  `verdict.py:56` (incluye la razón en el mensaje de baseline no sano).
- No hay decisión, reintento, clasificación ni tratamiento diferente por el
  literal: `timeout` y `output limit exceeded` producen el mismo `status`
  (`invalid`), el mismo resultado (`error`), la misma parada de campaña y el
  mismo formato de mensaje. Ningún consumidor compara el literal.
- No hay obligación vigente de causa exacta que la tolerancia contradiga:
  CONTRATO-AC1 exige «guardar causa y captura parcial acotada» (se guarda una
  causa válida en ambos casos); la aclaración C2 fija la frontera del deadline
  («al alcanzar o superar el deadline no comienza otra lectura; prevalece el
  timeout») y la ventana A12 no la infringe: en ambos extremos la ronda de
  lectura comenzó antes del deadline y ninguna implementación inicia otra
  lectura después.
- Los oráculos de test que fijan literales (`tests/unit/test_accept_campaign.py`
  444, 507, 527, 869, 923, 1050, 1144, 1273) describen escenarios sin la
  concurrencia de la ventana A12; ninguno se debilita ni se toca.

**Registro.** A12 (`tools.wct.accept.process.x__read__mutmut_12`) queda
registrado como **equivalencia respecto del contrato aclarado**, limitada a las
fuentes, runtime y precondiciones identificadas; no es igualdad exacta del
resultado ni equivalencia universal:

- Fuentes: `process.py` sha256 `84b9340f…` en `3638cfa` (diff sellado
  `min(65536→65537, remaining + 1)`).
- Runtime/precondiciones de las sondas: Linux con capacidad por defecto de
  pipe ≤65536 (medida con `F_GETPIPE_SZ`), `os.read` cruda sobre el fd, hijos
  que no redimensionan su propia tubería, y transporte admisible del
  CONTRATO-AC1.
- Propiedades exigidas por la aclaración, verificadas en las sondas:
  bytes persistidos idénticos (stdout.log 1048576 B, sha256 `8f990ba0…`),
  exit 9, `stderr` 0 B, hijo recolectado.
- Divergencia histórica conservada: en la ventana del deadline entre ambas
  señalizaciones, el original reporta `timeout` y la variante
  `output limit exceeded` con bytes idénticos
  (`RECALIFICACION-POSTPARTICION-Y-A12-2026-09-16.md` §3; sonda de transporte
  `PARTICION-TEST007-Y-CIERRE-R3-2026-09-16.md` §5). La tolerancia cubre
  exactamente esa concurrencia; no se impone prioridad nueva ni se cambia el
  producto.
- Invalidante declarado: si el dominio del transporte admite hijos que
  amplíen su propia tubería, A12 pasa a defecto con oráculo público ya
  demostrado (`DISPOSICION-R3-Y-DISENO-PARTICION-2026-09-15.md` §4.3).

## 3. Disposición de los demás IDs

### 3.1 A13 — equivalencia observable acotada (condición cumplida)

`tools.wct.accept.process.x__read__mutmut_14` (`remaining+1 → remaining+2`).
La condición del encargo («únicamente si el verifier confirma el argumento
completo sobre bytes, motivo, terminación y limpieza») quedó cumplida: el
verifier re-ejecutó sondas propias y confirmó que con `remaining ≤ 65534` y
`disponible > remaining` ambas variantes retornan el mismo motivo
(`output limit exceeded`) y persisten el mismo `chunk[:remaining]`; con
`disponible ≤ remaining` leen exactamente `disponible`; con
`remaining ≥ 65535` ambas peticiones son idénticas (tope 65536); la variante
consume a lo sumo un byte más solo en ronda terminal, de una cola que muere con
el proceso terminado en la misma ronda, sin alcanzar bytes persistidos, motivo,
terminación acotada ni limpieza. **Registrada como equivalencia observable
acotada**; no se afirma identidad de todo el estado interno. Fuente
`process.py` `84b9340f…`; runtime y precondiciones de las sondas; re-revisión
obligatoria si cambian.

### 3.2 execute__28/29 — equivalencia deductiva por alcanzabilidad (condición cumplida)

`tools.wct.accept.process.x__execute__mutmut_28/29` (`wait(timeout=1)` final →
`None`/`2`). La condición del encargo («demostrar que el `wait` final solo
opera sobre un proceso terminado/recolectado en todos los caminos admitidos»)
quedó cumplida: el verifier confirmó la demostración con sonda propia sobre
`Popen` de CPython 3.13 — en todos los caminos admitidos de `_execute`, el
`wait` final (línea 67) solo se evalúa cuando el hijo ya terminó y fue
recolectado:

- rama `seconds <= 0`: no hay proceso ni `wait` final;
- razón no vacía: `_terminate` (línea 66) ejecuta `wait(timeout=1)`; si retorna,
  el hijo quedó recolectado y el `wait` final retorna de inmediato; si lanza
  (p. ej. `TimeoutExpired`), el `wait` final no se alcanza (la excepción
  propaga y el `finally` cierra/recolecta);
- razón vacía: `_observe` solo retorna `""` cuando `selector.get_map()` está
  vacío **y** `process.poll() is not None` (línea 40), es decir, hijo ya
  recolectado o en estado muerto según la semántica de `Popen.poll()`.

Sobre hijo terminado/recolectado, `wait(None)`, `wait(2)` y `wait(1)` son
indistinguibles. **Registrada la equivalencia deductiva**; los IDs permanecen
en el inventario. Fuente `process.py` `84b9340f…`; re-revisión obligatoria si
cambia el adaptador/runtime.

### 3.3 Defectos detectados por regresiones permanentes (no equivalencias)

Se registran como **defectos de mutantes detectados por regresiones
permanentes**: el original expresa la conducta contractual y el mutante la
rompe; la regresión permanente lo detecta con sensibilidad demostrada contra el
mutante real. No se clasifican como equivalencias ni se recalcula el bruto
histórico.

| ID | Cambio | Regresión permanente | Evidencia |
|---|---|---|---|
| `process.x__read__mutmut_17` (A14) | `continue`→`break` en EOF | `test_eof_on_one_stream_still_captures_sibling_output_in_same_round` | `DISPOSICION-R3…` §5; `PARTICION…` §7 |
| `process.x__terminate__mutmut_6` | `wait(1)`→`wait(None)` | `test_terminate_gives_up_on_slow_reap_within_bounded_budget` | `DISPOSICION-R3…` §5 |
| `process.x__observe__mutmut_33` (C2) | `>=`→`>` en el deadline | `test_deadline_boundary_prevents_a_new_read_and_keeps_captured_bytes` | `PARTICION…` §7; aclaración C2 aplicada |
| `process.x__execute__mutmut_30` (A3) | guarda `finally` invertida | `test_failed_observation_reports_reaps_and_closes_live_child` | `OLEADA-TECNICA…` §2.1 |
| `process.x__execute__mutmut_31/32` | `_terminate(None)`; streams no cerrados | `test_failed_observation_reports_reaps_and_closes_live_child` | `OLEADA-TECNICA…` §2.2 |
| Los 11 `DEFECTO_FUNCIONAL` r3 (`campaign.x__attempt__mutmut_6/7`, `campaign.x__results__mutmut_11/12`, `process.x__execute__mutmut_1/8/14`, `process.x__observe__mutmut_31`, `process.x__read__mutmut_2`, `process.x__terminate__mutmut_1`, `process.x_run_process__mutmut_25`) | varios | 8 pruebas de `6e4398e` + `fa3558d` (ver `ADENDA-AC1-R3-DENOMINACION-ORACULOS-REGRESIONES-2026-09-13.md` §3) | 11/11 mutantes reales caen en su aserción |

No se traslada automáticamente ningún resultado: las regresiones fueron
verificadas contra los mutantes reales del lote r3 y `process.py` conserva el
sha256 `84b9340f…` del anclaje; si cambia una fuente o el runtime, la
sensibilidad debe re-verificarse.

### 3.4 terminate__7 — comportamiento distinto no contratado; bloqueo con propuesta exacta

`process.x__terminate__mutmut_7` (`wait(timeout=1)` → `wait(timeout=2)`).
No se aprueba imponer exactamente `wait=1 s` como contrato; no es equivalencia
automática ni exclusión tácita. Procedimiento vigente localizado: TEST-002 es
regla dura (`governance/rules/10-testing.yaml`), `max_survivors_changed: 0`
(`governance/thresholds.yaml`) y la única vía usada para disponer
supervivientes no equivalentes es la ratificación/registro humano explícito
(precedente H-01); **no existe un procedimiento de excepción para
comportamiento no contratado**. Por tanto la puerta queda bloqueada en este ID
a falta de decisión humana. Propuesta exacta de excepción (no aplicada, no
editada en gobernanza):

> «Excepción TEST-002 para `tools.wct.accept.process.x__terminate__mutmut_7`:
> se acepta como comportamiento distinto no contratado que `_terminate` use
> `wait(timeout=2)` en lugar de `wait(timeout=1)`; no se fija `wait=1 s` como
> contrato operativo; no es equivalencia. La terminación acotada y la
> recolección del hijo directo siguen obligatorias. La excepción alcanza solo
> a este ID, fuente (`process.py` sha256 `84b9340f…`), runtime y precondiciones
> documentados, y se revisa si cambian.»

### 3.5 Hooks decorados (D-D)

`_Recorder.pytest_runtest_makereport` y `.pytest_sessionfinish` no son IDs de
mutmut. La comprobación alternativa corregida fue ejecutada
(`OLEADA-TECNICA…` §2.3: control con `SemanticMismatch`, HOOK-MR-01 y
HOOK-SF-01 con validador `invalid` por contradicción/exit discordante, canario
de plugin acreditado). La evidencia está disponible; su disposición formal
humana (aceptar la comprobación como cierre de los dos hooks) sigue pendiente y
no suma al bruto mutmut.

## 4. Ledger de mutación de fuentes por lote, fuente e identidad

Los lotes se conservan separados; no se suman como campaña conjunta. Ningún
lote se re-ejecutó en este encargo.

| Lote | Fuente / identidad | Bruto histórico | Estado y clasificación vigente |
|---|---|---|---|
| r3 AC1 | `tools/wct/accept/*`; log sellado `51d99c9b…`; runtime `sh-p01-CND-80B8` (Python 3.13.14/mutmut 3.7.0) | **497 = 450 killed + 47 survived** (inmutable) | 47 supervivientes adjudicados y dispuestos: 14 equivalencias acotadas → **A12 y A13 registradas**; A3/A14 a defectos con regresión; **A1, A2, A4–A11 pendientes**. 15 no contratados (B1–B5) pendientes. 7 limitaciones → **execute__28/29 registradas**; execute__31/32, observe__33 (C2) y terminate__6 a defectos con regresión; **terminate__7 pendiente con propuesta** |
| r3 funcionales | idem | 11 `DEFECTO_FUNCIONAL` dentro de los 47 | Regresiones permanentes (`6e4398e`, `fa3558d`); 11/11 caen. No equivalencias |
| fase E histórica | `gate/checks.py::_declared`, `selftest/fixtures_tools.py::f9_a` en el corte G/E | **27 killed + 4 survived** (intacto) | No se transforma en campaña 31/31; los 4 supervivientes cayeron después por oráculo |
| recalificación post-partición (fase A) | `checks_debt.py::_declared`, `fixtures_adversarial.py::f9_a`; copia `build/tmp/recalificacion/frenteA/` | **31 killed + 0 survived + 0 instrumentales** (lote nuevo, 25 s) | Correspondencia 1:1 por diff normalizado con los 31 históricos; 333 no objetivo `not checked`. No convierte `survived` histórico en `killed` |
| GS-1 | `semgrep_schema/verdict` | 280 killed + 2 survived | CERRADO en su alcance (O5 rechazado-evidencia, integrado) |
| GS-2 | `semgrep_scope` | 102 killed + 16 survived | CERRADO por evidencia sucesiva (34/34 abiertos con activación acreditada; sin residuos) |
| GS-3 | `semgrep.py` | 74 killed + 34 survived | CERRADO acotado: 34/34 clasificados, 27 regresiones permanentes y 4 equivalencias ratificadas en su acto; `mutmut_24/29/33` con propuesta A de dominio |
| partición TEST-007 | 17 archivos resultantes | sin campaña fresca | Cubierto por controles estructurales: 72/72 fingerprints idénticos, 0 ciclos, `REGISTRY` 47 con literales idénticas, P1/P2/P2′/P2″ + PX-REG, D1–D4; recalificación de sus 31 IDs re-anclados |
| 928 IDs históricos | `checks`/`fixtures_tools` (preexistentes) | **sin ejecución y sin veredicto** | Sin decisión de alcance explícita: ver §5 |
| hooks | 2 hooks decorados | no instrumentables | Comprobación alternativa ejecutada; disposición formal pendiente (§3.5) |

Contabilidad sin agregaciones: ratificar equivalencias no convierte
`survived` en `killed`; el bruto r3 sigue 497; la campaña nueva de
recalificación es otro lote y no modifica la historia. G-MUT **no se ejecutó**:
no se declara PASS de ese gate.

Capas distinguidas en este ledger:

- **Resultados brutos históricos**: r3 497 = 450 + 47; fase E 27 + 4; GS-1
  280+2; GS-2 102+16; GS-3 74+34 — inmutables y sin recampaña.
- **Regresiones posteriores y sondas de sensibilidad**: 11 `DEFECTO_FUNCIONAL`
  (8 pruebas), A14, terminate__6, C2 (observe__33), A3/execute__31/32; sondas
  A12/A13/C2 con mutantes reales en copias selladas.
- **Nueva campaña post-partición de `_declared`/`f9_a`**: 31 killed + 0
  survived (lote propio, correspondencia 1:1 con los 31 históricos).
- **Equivalencias ratificadas con precondiciones**: A12, A13 y execute__28/29.
- **Comportamientos no contratados y excepciones pendientes**: B1–B5 (15 IDs)
  y terminate__7 (propuesta exacta, sin procedimiento de excepción).
- **Limitaciones instrumentales**: los 7 IDs de la clase r3, cada uno
  dispuesto como equivalente acotada, defecto con regresión o pendiente según
  lo anterior; ninguna limitación queda sin explicar.
- **Cambios estructurales cubiertos por controles**: partición TEST-007
  (fingerprints, composición de `REGISTRY`, parches, D1–D4, PX-REG).
- **Alcance sin medir o sin decisión**: 928 IDs de funciones preexistentes y
  los 17 archivos particionados sin campaña fresca (§5).

## 5. Frontera de alcance — decisiones faltantes

1. **Los 928 IDs siguen sin ejecución.** No existe decisión de alcance
   explícita que los deje fuera del incremento: la propuesta PX-928 del plan
   §7.6 está **NO APROBADA**, y quedó redactada sobre el candidato
   `01c901df…` antes de la partición. La decisión faltante exacta es una
   delimitación por identidad/diff sobre el candidato particionado vigente
   (`3638cfa`) que declare preexistencia fuera del incremento a los 928 y
   preserve la recalificación de los 31, sin excluir archivos completos.
2. **Alcance de mutación de la partición.** Los 17 archivos resultantes no
   tienen campaña fresca; su cobertura son los controles estructurales y la
   recalificación de los 31 IDs re-anclados. La decisión de alcance (punto 1)
   debe cubrir también las funciones trasladadas.
3. **A1/A2/A4–A11 (10 IDs)** y **B1–B5 (15 IDs)**: sin ratificación/decisión.
4. **terminate__7**: sin excepción registrada (§3.4).
5. **Hooks**: sin disposición formal (§3.5).

Ningún pendiente se resuelve por omisión ni por este informe; no se
ejecutan los 928 ni se excluyen por cuenta propia.

## 6. Receta de Q-ACCMUT verificada contra su implementación (sin ejecutar)

Lectura de la implementación vigente, sin lanzar campaña:

- CLI: `tools/wct/cli.py:95-99` define `wct accept {parse,ir-dry,generate,run,mutate}`
  y `--output` (default `tests/acceptance/generated/test_acceptance.py`);
  `cli.py:299-329` ejecuta `parse_feature(feature)` → `generate(ir, output)` →
  `run_mutations(ir, command)` con comando por defecto
  `[sys.executable, "-m", "pytest", "-q", <generated>]`, cwd del invocador.
- Operador histórico: `tools/wct/accept/mutation_cases.py::_changed`
  (numérico: `0→"1"`, resto `→"0"`; no numérico `+"__mutated"`) y
  `mutations(ir)` (una celda por campo, en orden). No es el operador tipado
  P03a; no se injerta otro candidato.
- Inventario de la feature `features/wct-acceptance-evidence-001.feature`:
  5 filas × 8 campos + 1 fila × 7 campos = **47 celdas**, trazadas al inventario
  histórico de 48 por `test_ac1_feature_inventory_traces_the_48_historical_coordinates`.
- Bindings/consumidores productivos: `tests/acceptance/steps.py::execute_scenario`
  despacha a `tests/acceptance/campaign_steps.py`; el runner de prueba es
  `tests/acceptance/protocol_runner.py`; el recibo lo emite el plugin
  `tools.wct.accept.pytest_receipt` vía `PYTEST_PLUGINS`; veredicto con
  `accept_verdict` (sin conciliación personalizada).
- Riesgo de receta detectado (para una ejecución futura autorizada): el default
  de `--output` **sobrescribiría** el generado histórico de `example.feature`.
  Una ejecución conforme debe pasar `--output` bajo `build/tmp` (y el runner
  correspondiente), o el generado de la feature AC1 en su propia ruta; no se
  autoriza modificar el generado histórico.

## 7. Puerta previa — dictamen del verifier independiente

Agente distinto del autor, sin escritura sobre archivos versionados; informe y
evidencia propios en `build/tmp/verifier-qaccmut/VEREDICTO.md` (365 líneas).
Reejecuciones propias: 3 sondas, 0,51 s acumulados; sin mutmut, campañas ni
bless. Revisión documental distinguida de la reejecución. Reservas no
bloqueantes registradas: el log `r3-regression-demo.log` nombra `mut31` con la
prueba pre-rename de `bfcaf66` (la sensibilidad vigente está demostrada por la
oleada y por `fa3558d`); el directorio de evidencia ya contenía artefactos de
una corrida previa/paralela que el verifier no usó ni citó.

| Tarea | Resultado |
|---|---|
| 1. Identidades y vigencia | **CONFIRMADO**: hashes `84b9340f…`/`686070cd…`/`d4f136ae…` y log sellado `51d99c9b…` exactos; runtime Python 3.13.14 / pytest 9.1.1 / mutmut 3.7.0; evidencia citada presente |
| 2. A12 — consumidores y obligaciones | **CONFIRMADO**: único consumidor productivo `campaign.py:47`; nadie compara `timeout` vs `output limit exceeded`; sin obligación de causa exacta; la ventana A12 no contradice C2 (bytes idénticos). A12 sustentada |
| 3. A13 | **CONFIRMADO** con sondas propias: mismo motivo y bytes persistidos en todas las fronteras; sin contraejemplo |
| 4. execute__28/29 | **CONFIRMADO** con sonda `Popen` 3.13: tras `poll() != None` el hijo ya está recolectado y los tres `wait` retornan idénticos e inmediatos; el camino con excepción no alcanza la línea 67 |
| 5. Defectos con regresión | **CONFIRMADO** (reserva R-T5): las 4 regresiones y las 8 pruebas existen y son permanentes; `process.py` sin drift desde `aa2ffa9`; mutantes reales m30/m31/m32, mut17, mut6, mut33 y los 11 funcionales con registro de caída |
| 6. Ledger y frontera | **CONFIRMADO**: 497 = 450+47; fase E 27+4; recalificación 31; GS-1/2/3 cerrados. Pendientes completos; A1/A2/A4–A11 y B1–B5 **sin ratificación humana**; PX-928 **NO APROBADA** y sin decisión posterior para los 928 |
| 7. Receta Q-ACCMUT | **CONFIRMADO**: `cli.py:95-99,299-329`, operador `_changed`, 47 celdas, bindings y riesgo real del `--output` por defecto |

**Dictamen de la puerta: `NO APROBAR-Q-ACCMUT`.** La puerta de mutación de
fuentes no está satisfecha de forma sustentada: además de lo registrado en
§2–§3, faltan decisiones humanas explícitas para los IDs y el alcance listados
en §9 (A1, A2, A4–A11, B1–B5, terminate__7, hooks y delimitación 928 +
partición). No se inventa ninguna excepción ni se declara G-MUT en PASS.

## 8. Q-ACCMUT — NO EJECUTADO

Conforme al encargo («Q-ACCMUT depende de la puerta previa, no corre en
paralelo con su aprobación»), y ante el dictamen `NO APROBAR-Q-ACCMUT`:

- **NO EJECUTADO**: 0 s de los 900 s exteriores consumidos; sin preflight de
  campaña, sin generación de bindings, sin baseline, sin mutantes, sin
  intentos ni recibos. No se forzó el inventario de 47 celdas ni se declaró
  47/47 por construcción. No se ejecutaron P03a, campañas globales ni los 928.
- Razón exacta: la puerta de mutación de fuentes no está satisfecha; faltan
  las decisiones humanas de §9 (en particular A1/A2/A4–A11, B1–B5,
  terminate__7, hooks y la delimitación de alcance de los 928 + partición).
- La receta de §6 queda verificada y lista para una ejecución futura
  autorizada; requerirá `--output` fuera del generado histórico.

## 9. Pendientes concretos para decisión humana

Formato: ID/ruta/cambio → obligación → evidencia faltante → acción mínima.

1. `campaign.x__attempt__mutmut_4` (`ensure_ascii=False`→`None`) → TEST-002 →
   ratificación/rechazo humano bajo bytes/runtime r3 → decidir §7.1 del plan
   (`Ratifico exclusivamente…`).
2. `campaign.x__attempt__mutmut_9` (`utf-8`→`UTF-8`) → TEST-002 → idem →
   decidir §7.2.
3. `process.x__observe__mutmut_7/11/12/13/22/26/27/28` (cast de typing) →
   TEST-002 → ratificación + transferencia documental por diff/hash al
   `84b9340f…` → decidir §7.3.
4. B1–B5 (15 IDs: indentación de `attempt.json`/`report.json`, literal de
   `reason`, grafía del mensaje de hash, nombre del plugin) → TEST-002 →
   decisión de contrato → decidir §7.5 y disponer cada ID.
5. `process.x__terminate__mutmut_7` → TEST-002 sin procedimiento de excepción →
   excepción humana explícita (texto propuesto en §3.4) o imposición aprobada
   de `wait=1 s` con test → registrar decisión.
6. Hooks `pytest_runtest_makereport`/`pytest_sessionfinish` → TEST-002/DD →
   disposición formal de la comprobación alternativa → aceptar o especificar
   otra vía.
7. Alcance 928 + partición → TEST-002/incremento → decisión de delimitación
   por identidad/diff post-particionada → aprobar el texto PX-928 actualizado.

## 10. Presupuestos

- Revisión experimental y comprobaciones de consumidores de este encargo:
  solo lecturas, `rg`, `sha256sum` y consultas de runtime (segundos acumulados;
  muy por debajo de 180 s). Revisión documental contabilizada aparte.
- Q-ACCMUT: **0 s ejecutados**; el tope de 900 s exteriores no se consumió.
  No se repitieron campañas históricas de fuentes.

## 11. Verificación del candidato documental

- `git diff --check`: limpio.
- Fast (`UV_NO_SYNC=1 uv run wct gate --tier fast`): **7/7 PASS** (G-META-2,
  G-RULES-DRIFT, G-SUPPRESS, G-DEBT, G-LINT, G-FMT, G-TYPE).
- Integridad (`wct integrity check`): exit 1; drift **recalculado 37 = 7
  modificadas + 30 nuevas**, idéntico al medido tras la partición. Este
  incremento es documental (dos rutas no protegidas) y no añade rutas
  protegidas. G-META-1 sigue siendo el rojo pre-bless conocido; no se ejecutó
  bless ni se usó su ausencia como causa.
- No se ejecutaron cobertura/CRAP, DRY ni tier full: la puerta previa quedó
  bloqueada y el encargo detiene la cadena aquí.

## 12. Límites

No ratifica equivalencias fuera de las registradas en §2–§3; no ejecuta
Q-ACCMUT, mutmut, campañas de fuentes ni los 928 IDs; no modifica producto,
tests, features, gobernanza, manifests, ratchets, lock ni versión; no bendice,
no hace merge, bump, tag ni release; no declara cierre integral AC1/beta.3. La
evidencia citada bajo `build/tmp/` es temporal, no custodia durable. La
publicación de este registro y las filas afectadas de la matriz es el único
cambio versionado de este encargo.
