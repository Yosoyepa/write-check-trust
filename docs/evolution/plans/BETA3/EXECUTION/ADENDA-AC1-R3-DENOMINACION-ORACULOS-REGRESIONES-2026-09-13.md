# Addenda AC1 r3 — denominación, oráculos y regresiones (2026-09-13)

Complemento de `ADJUDICACION-SUPERVIVIENTES-AC1-R3-2026-09-13.{md,json}` que no
reescribe ninguna clasificación histórica. Sin cambios de producto, gobernanza,
bless, merge, bump ni tag. Encargo: incremento acotado de regresiones de r3.

## 1. Corrección de denominación

La clase `DEFECTO_FUNCIONAL` (11 IDs) **no atribuye 11 bugs al producto**. La
distinción correcta, aplicable a toda la matriz:

- **Defecto introducido por el mutante** (los 11 `DEFECTO_FUNCIONAL`): el
  original expresa la conducta deseada y es el mutante el que la rompe. El
  producto actual está en lo correcto en cada una de esas 11 filas.
- **Hueco del oráculo**: la suite no distinguió el mutante — es la razón de la
  supervivencia, no un defecto del producto.
- **Defecto reproducido en el original**: un fallo del producto sin mutar.
  **Ninguna fila de la matriz r3 evidencia uno**; de haberlo, se abriría
  incremento de reparación propio con TDD, separado de esta adjudicación.

## 2. Re-extracción de `wrong_hash_message` (punto 2)

La evidencia original observó la línea fuente del traceback del
`INTERNALERROR` (se conserva en el JSON, clave `probe`, sin modificar). La
corrección observa la **excepción emitida**: se construye `_Recorder()` con un
recibo cuyo hash no coincide, capturando el `ValueError` real
(`preflight-h04/r3-wrong-hash-exception-emitted.log`):

| Variante | Excepción emitida |
|---|---|
| Original | `ValueError: AC1 original IR hash mismatch` |
| `xǁ_Recorderǁ__init____mutmut_10` | `ValueError: XXAC1 original IR hash mismatchXX` |
| `xǁ_Recorderǁ__init____mutmut_11` | `ValueError: ac1 original ir hash mismatch` |
| `xǁ_Recorderǁ__init____mutmut_12` | `ValueError: AC1 ORIGINAL IR HASH MISMATCH` |

La clasificación no cambia (`COMPORTAMIENTO_NO_CONTRATADO`): la grafía exacta
del mensaje no tiene contrato aprobado y no se añade test (punto 6 del encargo).

## 3. Regresiones incorporadas y sensibilidad por ID (punto 7a)

Sólo se editaron `tests/unit/test_accept_campaign.py` (8 pruebas nuevas) y
`tests/unit/test_accept_pytest.py` (sin cambios: no hay IDs funcionales de
`pytest_receipt`). Casos e identidades existentes intactas. Demostración con
el runtime original y los mutantes existentes del lote r3 — el original pasa
las 8 y cada mutante cae en SU aserción
(`preflight-h04/r3-regression-demo.log`):

| Prueba nueva | Mata a | Sonda |
|---|---|---|
| `test_campaign_transports_ir_bytes_as_utf8_without_ascii_escaping` | `campaign.x__attempt__mutmut_6`, `__7` | bytes de `ir.json` literales en UTF-8 y `receipt.ir_sha256` = SHA-256 de esos bytes |
| `test_report_and_results_omit_internal_ir_even_when_baseline_invalid` | `campaign.x__results__mutmut_11`, `__12` | resultados y `report.json` sin clave `ir` aun con baseline inválido |
| `test_zero_budget_reports_timeout_without_launching` | `process.x__execute__mutmut_1` | presupuesto 0: `exit=None`, razón `campaign timeout`, sin lanzamiento (marcador ausente) |
| `test_run_process_child_receives_eof_not_parent_stdin` | `process.x__execute__mutmut_8`, `__14` | hijo con stdin aislado: lee EOF, no el stdin del padre |
| `test_transport_reads_pending_output_after_leader_terminates` | `process.x__observe__mutmut_31` | doble controlado autorizado de proceso/selector: secuencia fija leer-líder → confirmación explícita de EOF acotada por un deadline propio del test con tope de 5 s (sin esperas de gracia ni sleeps) → lectura de la salida pendiente por una tubería propia del test → fin. Estado realizable: la salida del líder no implica streams cerrados. Oráculo sobre resultado observable del SUT: `stdout.log` == `leader-done\ndescendant-late\n`, `exit == 0`, `reason == ""`. Historia del mecanismo: v1 sleep(0.3) (dependía del scheduler); v2 marcador (rompía la sensibilidad); v3 pidfd abandonado con diagnóstico (`preflight-h04/pidfd-diag/`: getppid sufre carrera de reparentización; con pid por argv el original pasa pero el transporte mutado puede drenar los buffers pendientes antes de observar la muerte → sensibilidad no determinista); v4 final: doble controlado. El nombre anterior (`…descendant_output_after_leader_exit`) cambió para no prometer un descendiente real; la integración real de captura/limpieza sigue cubierta por las pruebas de transporte existentes |
| `test_silent_attempt_duration_tracks_budget_with_controlled_clock` | `process.x__read__mutmut_2` | reloj controlado: la duración de un intento silencioso no supera el presupuesto |
| `test_terminate_an_already_exited_process_does_not_raise` | `process.x__terminate__mutmut_1` | terminar un hijo ya recolectado no lanza `TypeError` |
| `test_duration_is_a_measurement_not_an_accumulation` | `process.x_run_process__mutmut_25` | reloj controlado: `duration` es fin-inicio, no suma |

Higiene de procesos (punto 5): grupos propios (`start_new_session` del
transporte), sincronización explícita (`wait()`/pipes), timeout exterior
(`subprocess.run(timeout=60)` y presupuestos del SUT) y limpieza en `finally`
(`_cleanup_transport_child`). Duraciones por reloj controlado con aserción
sobre el resultado del SUT, no por límites temporales frágiles.

## 4. Decisiones pendientes — 14 `EQUIVALENCIA_ACOTADA` (punto 7b)

`campaign.x__attempt__mutmut_4` (ensure_ascii=None), `__mutmut_9`
(encode UTF-8), `process.x__execute__mutmut_30` (inversión del guarda de
`finally`), `process.x__observe__mutmut_7/11/12/13/22/26/27/28` (cast de
typing, 8), `process.x__read__mutmut_12` (tope remaining+2), `__mutmut_14`
(continue→break con redrenaje), `__mutmut_17` (select 0.05→1.05). Ninguna se
ratifica por omisión: requieren decisión humana por ID conforme a la matriz
(runtime y precondiciones descritos).

## 5. Plan concreto — 7 `LIMITACION_INSTRUMENTAL` (punto 7c)

`process.x__execute__mutmut_28/29` (wait timeout None/2), `__mutmut_31`
(`_terminate(None)` en defensa), `__mutmut_32` (cierre de streams),
`process.x__observe__mutmut_33` (deadline inclusivo), `process.x__terminate__mutmut_6/7`
(wait None/2). Plan: (1) decidir si esos límites exactos son contrato
operativo; (2) si lo son, autorizar un adaptador/doble de subprocess
inyectable — cambio de producto con TDD propio — que observe los límites sin
matar procesos ajenos; (3) mientras tanto quedan sin ratificar y sin test:
no se fabrican estados ni se dependen de GC implícito.

## 6. Defectos sembrados y oráculos para los dos hooks (punto 7d)

Conforme a `alternative_hook_check` del JSON, aún **no ejecutado**: copiar el
plugin y un proyecto pytest mínimo bajo
`build/tmp/ac1-r2-qualification/r3-hook-alternative/<run>/`; control +
`pytest_runtest_makereport` sembrado + `pytest_sessionfinish` sembrado.
Oráculos exactos propuestos: (a) sembrado en `makereport`: `receipt.json`
conserva identidad y esquema pero la fase del escenario sembrado figura con
`status: "error"` y el evento queda en `receipt.events.json`; (b) sembrado en
`sessionfinish`: el recibo no se escribe o `validate_receipt` emite
`invalid`; (c) en ambos, exit de pytest ≠ 0 y diff verificable contra el
control. Timeout exterior 30 s, grupo propio y limpieza en `finally`. La
comprobación no se ejecuta en este incremento.

## 7. Residuos sin contrato (punto 6)

Los 15 `COMPORTAMIENTO_NO_CONTRATADO` (indentación JSON de
`attempt.json`/`report.json`, nombre interno del plugin, grafía de `reason` y
del mensaje de hash) **no reciben tests** y **no se convierten en equivalentes
ratificados por omisión**: siguen pendientes de decisión humana explícita.
