# Plan ejecutable — decisiones de cierre AC1 y salida incremental (2026-09-15)

**Propuestas NO APROBADAS.** Este plan corrige la secuencia y concreta los
encargos pendientes; no ratifica equivalencias, concede excepciones ni autoriza
implementación, campañas, bless, merge, bump, tag o release. Sustituye la
oleada genérica de crear dossiers por las decisiones de §3–§6. No crea otro
expediente general. Los resultados históricos permanecen en sus fuentes.

## 1. Corte, fuentes y alcance de esta revisión

Comprobado en el worktree `build/tmp/beta3-ac1-r2-integration` del repositorio
`/home/jandradeu/Documents/well_code_template`:

- HEAD completo `01c901dfdb6713de22ac8d60737c6ecf4b4a8d98`, rama
  `codex/beta3-ac1-r2-integration`; remoto `origin` =
  `https://github.com/Yosoyepa/write-check-trust.git`, rama remota idéntica.
  `main` remoto: `932c835ac0eeb75010ec7a1071315b1c51f78eb6`.
- Índice vacío y ningún cambio seguido al iniciar. Único untracked:
  `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md` en este directorio:
  ajeno, leído, no copiado ni incorporado. El checkout principal contiene
  trabajo ajeno y solo se consulta.
- PR #53 OPEN y **borrador**; `commit-gates` FAILURE, run `35041871211`.
  Log remoto: `rules check` pasa y `integrity check` termina con exit 1;
  `doctor` y los pasos posteriores no corren. No se heredan resultados de
  CI ni del tier commit de otra identidad.
- Comprobación ligera local `UV_NO_SYNC=1 uv run wct integrity check`:
  **exit 1, 23 rutas = 7 modificadas + 16 nuevas**, sin bless ni cambios
  de runtime. Es resultado real de integridad, no PASS.
- G-DEPS/G-DEAD ya reparados en `b4403c5`; las 213 regresiones focales y el
  tier commit 20 PASS + G-META-1 FAIL son mediciones históricas de
  `REPARACION-INTEGRACION-GDEPS-GDEAD-2026-09-15.md` §5–§7, no corridas nuevas.

Fuentes versionadas de este mismo directorio: `CONTRATO-AC1.md`,
`CALIFICACION-AC1.md`, `MATRIZ-DECISIONES-AC1-PENDIENTES-2026-09-13.md`,
`ADJUDICACION-SUPERVIVIENTES-AC1-R3-2026-09-13.{md,json}`,
`ADENDA-AC1-R3-DENOMINACION-ORACULOS-REGRESIONES-2026-09-13.md`,
`GS2-REVALIDACION-Y-PREPARACION-CIERRE-2026-09-15.md`,
`ACTA-CIERRE-ACOTADO-GS3-2026-09-15.md` y los registros de GS-1/2/3 que citan.
Fuentes normativas: `AGENTS.md`, `governance/rules/10-testing.yaml`,
`governance/thresholds.yaml`, `docs/gates.md`, `docs/runbook.md`,
`tools/wct/gate/runner.py`, `tools/wct/mutate/engine.py`,
`.github/workflows/quality.yml`, `docs/evolution/plans/BETA3/PLAN.md`.

Fuentes locales ajenas, **solo lectura**, bajo
`/home/jandradeu/Documents/well_code_template/docs/evolution/plans/BETA3/EXECUTION/`:
`RECETA-FASE-G-GATE-SELFTEST-2026-09-13.md`,
`ADJUDICACION-FASE-E-GATE-SELFTEST-2026-09-13.md`,
`CIERRE-ADJUDICACION-FASE-E-2026-09-13.md`,
`ADENDA-PREPARACION-LOTE-GATE-SELFTEST-2026-09-13.md` y
`DECISION-INTEGRACION-Y-SIGUIENTE-INCREMENTO-2026-09-13.md`.
La preparación de salida incremental citada arriba aporta custodia y
publicación; no se duplica. Si falta una fuente local al ejecutar otro
encargo, detener su transferencia de evidencia; no reconstruirla por memoria.

Tres cierres separados: **AC1 no acreditado** (mutación de fuentes y cadena E8
pendientes); **integración/publicación bloqueadas** por pendientes técnicos,
revisión protegida, bless y CI; **beta.3 completa no terminada**. Una versión
incremental no elimina las obligaciones del código que sí se publique.

**GS-2 cerrado en su alcance mediante evidencia sucesiva; atribución pendiente
y residuos resueltos, sin nueva campaña conjunta ni PASS automático de G-MUT
o acreditación integral AC1.** Este es el estado ya autorizado. No queda una
puerta nominal «E4-PASS» ni se pide una campaña para cambiar esa etiqueta.
Se conservan bruto 102 killed + 16 survived y evidencia posterior en la matriz.
GS-3 conserva el cierre acotado del acta, sus 27 regresiones y 7 equivalencias
ratificadas en sus respectivos dominios; no se re-ratifican aquí.

## 2. Secuencia ejecutable e identidades

### PRE-BLESS y POST-BLESS

Lectura de `runner.py::_COMMIT_GATES/TIERS`: fast = 7 (sin G-META-1),
commit = 21 (con G-META-1), full = 34 (hereda commit), pr = 27 (hereda
commit). **Full no incluye G-ACCEPT-MUT**: aceptación mutada se ejecuta por
separado; el tier pr sí la incluye. CI comprueba integridad antes de ejecutar
commit y las comprobaciones siguientes. No alterar tiers ni saltar puertas.

| Etapa | Acción y salida exigida |
|---|---|
| PRE-BLESS: candidato técnico | Resolver los pendientes del alcance autorizado; congelar código, tests, docs, versión/lock si aprobados. Registrar identidades de fuentes, selección, runtime y configuración. Tras mutación de fuentes resuelta, seguir `CALIFICACION-AC1` §Evidencia: aceptación mutada → LCOV/cobertura/CRAP → DRY → full. Ejecutar solo con autorización y presupuesto propios. Conservar salida completa, exit y G-META-1 aunque falle por drift. Cero otros bloqueos técnicos sin resolver; no declarar «full PASS» ni acreditación integral por ignorar ese rojo. |
| PRE-BLESS: revisión protegida | Inventariar nuevamente **todas** las rutas protegidas y revisar su diff exacto, incluida versión/lock y cualquier artefacto añadido. La lista actual de 23 no congela el alcance futuro. El humano aprueba ese cambio protegido; decir «rojo esperado» no sustituye revisión. Si hay otro FAIL/ERROR o verificación faltante, detener antes de bless. |
| Bless humano | Solo con revisión conforme y autorización específica, el humano aplica el procedimiento de `docs/runbook.md`; registrar el commit que contiene lock/log y demás artefactos generados. No editar manifests a mano. |
| POST-BLESS | Sobre ese commit, repetir integridad y verificaciones finales pertinentes (incluido full requerido y CI completa). Exigir G-META-1 verde y gates pertinentes verdes antes de merge. Un cambio técnico durante el bless invalida la transferencia y vuelve a revisión/calificación. |
| Post-merge | Identificar el commit **real** integrado en main; revisar diferencia/procedencia y calificarlo antes de autorizar el tag. Cualquier bloqueo = NO-GO; no reparar directamente sobre main ni publicar para cerrar después. |

Las 23 rutas revisables actuales (comprobación local y CI concordantes):
modificadas `governance/lint/vulture_whitelist.py`, `pyproject.toml`, `uv.lock`,
`tools/wct/accept/pipeline.py`, `tools/wct/gate/checks.py`,
`tools/wct/gate/runner.py`, `tools/wct/selftest/fixtures_tools.py`;
nuevas `tools/wct/accept/{campaign,generation,ir_checks,mutation_cases,parsing,process,pytest_receipt,receipt,receipt_validation,semantic,verdict,verdict_validation}.py`
y `tools/wct/gate/{semgrep,semgrep_schema,semgrep_scope,semgrep_verdict}.py`.
Las llaves abrevian los nombres de archivos, no son una allowlist para editar.

### Cuatro identidades, no una igualdad imposible

| Identidad | Qué se registra | Transición y verificación |
|---|---|---|
| `T`: SHA del candidato técnico | SHA completo, tree, base, fuentes/tests/config/runtime y evidencia pre-bless | Antes de pasar a B, diff T→B completo y procedencia de cada artefacto; revisión humana protegida. |
| `B`: SHA con artefactos de bless | Commit real de lock/log, aprobación y comandos humanos | Integridad repetida, full/finales pertinentes y CI verde sobre B; si hay commits documentales o técnicos adicionales, identificarlos y revisar/verificar su impacto también. |
| `M`: SHA integrado en main | SHA remoto resuelto tras merge; padres, modo de merge y tree | Diff B→M conocido; un squash o merge commit puede cambiar SHA. Incluso con árbol igual se registra procedencia; con árbol distinto no se traslada evidencia automáticamente. Repetir calificación post-merge del árbol real según impacto y requisitos de salida. |
| `V`: SHA autorizado para tag | Decisión D3 que nombra SHA completo verificado y versión | Verificar que V corresponde al commit integrado seleccionado y que tag resuelve exactamente a V. Si se añade bump u otro cambio, vuelve a la cadena de revisión, bless si corresponde, CI e integración; no etiquetar un árbol no calificado. |

Cada transición conserva diff (incluido diff vacío), identidad, procedencia y
verificación correspondiente. Cambios no revisados, origen de imports ajeno o
hashes discordantes obligan a parar. No exigir T=B=M; no suponer que el merge
preserva el SHA. Las actas/evidencias nuevas también son cambios que deben
identificarse sin escribir dentro de un commit su propio SHA futuro.

## 3. Frente A — r3: decisiones por fundamento

El bruto **497 = 450 killed + 47 survived** no cambia. Las 11 regresiones
posteriores son sensibilidad, no una recampaña. Prefijo de los IDs abreviados
de esta sección: `tools.wct.accept.`; las listas son cerradas.

| Pendiente / hecho comprobado | Obligación y recomendación concreta | Alternativa, coste estimado | Decisión humana y cierre |
|---|---|---|---|
| `R3-DA-10`: A1 `campaign.x__attempt__mutmut_4` | `ensure_ascii=None` y False son falsy en el runtime adjudicado: recomendar ratificación acotada de este ID con evidencia existente. | Pedir revisión focal adicional ≤120 s; no aporta contrato de formato nuevo. | Ratificar por ese fundamento y bytes/runtime, sin modificar el bruto. |
| A2 `campaign.x__attempt__mutmut_9` | Alias `utf-8`/`UTF-8`: recomendar ratificación separada por equivalencia del códec. | Misma alternativa de revisión, no test cosmético. | Decisión independiente de A1. |
| A4–A11 `process.x__observe__mutmut_7/11/12/13/22/26/27/28`, `R3-CAST` | Recomendar ratificación histórica de los ocho por identidad de `typing.cast` y transferencia documental explícita bajo las precondiciones siguientes. | Revisión afectada ≤120 s si no se acepta la transferencia; no campaña completa automática. | Ratificar esos IDs históricos y decidir transferencia por diff/hashes; no reutilizar IDs como inventario actual. |
| `R3-DA-4`: A3/A12/A13/A14 | Las justificaciones actuales no prueban equivalencia; recomendar las cuatro comprobaciones acotadas de abajo. | Mantener abiertos sin ejecución cuesta 0 ejecución y bloquea su cierre; ratificar sin fundamento no es alternativa. | Autorizar comprobaciones y decidir después por ID: equivalencia, hueco de oráculo o defecto original. |
| `R3-DB`: B1–B5, 15 IDs | Recomendar JSON semántico, causa identificable y nombre de plugin interno en los términos siguientes. TEST-002 sigue vigente. | Convertir formato/literal/nombre en API nueva: contrato/Gherkin previo y pruebas ≤120 s focales, más implementación estimada 1–2 h. | Decidir cada familia; «presentación» no ratifica, excluye ni cierra por omisión sus mutantes. |
| `R3-DC`: siete límites instrumentales | Ya son obligatorias terminación acotada, recolección y captura parcial. Probarlas por fronteras existentes; separar la posible norma nueva wait=1 s. | Adaptador de producto solo si se demuestra insuficiencia de las fronteras; coste sin calibrar, encargo separado. | Aprobar pruebas y aclaraciones de frontera; ≤300 s focales, cierre con resultado observable por ID. |
| `R3-DD`: dos hooks decorados | Mutmut no los instrumenta; recomendar control y dos semillas con oráculo externo coherente (abajo). | Otra semilla requiere otra expectativa aprobada; no basta exit no cero. | Autorizar tres ejecuciones ≤120 s total; evidencia por hook, sin inventar killed. |

**Anclaje de casts.** `process.py` r3
`bdbb564604f2e893ed870e435db4f26751a4a725c1d4c5e5a70f4c4b3dc396d1`
→ vigente `84b9340fd16b424a2d778e512166c4419c048001588665a313dcdf9f5d263ef7`:
exactamente dos líneas `cast("BinaryIO", stream)` → `cast(BinaryIO, stream)`.
Python ahora evalúa el nombre importado; no es solo resolución estática.
El segundo argumento retornado sigue siendo el mismo bajo import correcto,
`typing.cast` ordinario no sustituido y streams iguales. `campaign.py` y
`pytest_receipt.py` siguen en los hashes r3 `686070cd…` y `d4f136ae…`.
Las 213 pruebas de la reparación son evidencia histórica de no regresión,
no ejecutadas aquí ni equivalencia universal. Si cambia alguna precondición,
no se transfiere la ratificación propuesta.

**Cuatro comprobaciones, no sondas ejecutadas.** Se contrastaron IDs contra
`build/tmp/ac1-r2-qualification/evidence/mutation-code-lot-r3-survivor-diffs.log`
(sha256 `51d99c9bdb45679dbed1300f2959bfb96ee27f0178cb5d48a669bf634c204b21`).
La adenda antigua §4 no es fuente de identidad: también confunde `_12`.

| ID bajo `process.` | Entrada propuesta | Oráculo contractual, no detalle interno |
|---|---|---|
| `x__execute__mutmut_30` (A3): guarda finally `is None`→`is not None` | Hijo propio vivo, salida parcial y excepción de IO/selector durante observación. | Error reportado, captura conservada, hijo recolectado y streams cerrados **antes** del rescate externo; no solo llamadas a `_terminate`. |
| `x__read__mutmut_12` (A12): 65536→65537 | `remaining=65536`, ≥65537 bytes disponibles, dos streams y reloj controlado. | Logs, causa, límite combinado y plazo propagados a `run_process`; pedir un byte más no demuestra por sí solo defecto contractual. |
| `x__read__mutmut_14` (A13): remaining+1→+2 | Remaining 0, 1, 65534; suficientes bytes y competencia de streams. | Nunca persistir más de 1 MiB combinado; distinguir efecto observable de bytes consumidos solo para detectar exceso. |
| `x__read__mutmut_17` (A14): continue→break | EOF de un stream antes de otro legible en la misma selección; reloj cerca de deadline y orden inverso como control. | Captura, causa y duración; comprobar efecto de re-selección y deadline sin presumir redrenaje universalmente equivalente. |

`x__read__mutmut_2` es **select 0.05→1.05**, ya tiene regresión y no se reabre.
Allowlist propuesta A3/A12–14: expediente exclusivo bajo `build/tmp/`; solo
`tests/unit/test_accept_campaign.py` para regresiones que se aprueben tras el
dictamen. Presupuesto conjunto **300 s** de controles/sondas, seriales, timeout
exterior y limpieza de procesos propios. Si falla el original, detener y
proponer reparación separada; este encargo futuro de comprobación no autoriza
cambiar producto.

**B: contratos realmente nuevos frente a obligaciones ya escritas.** Los IDs
exactos siguen en MATRIZ §B; no se duplica su tabla histórica:

- B1/B2: los seis mutantes de indentación cambian representación; consumidores
  cargan JSON. Recomendar esquema/identidad/cuentas/persistencia como contrato,
  sin indentación estable. Hacer estable el texto sería contrato nuevo.
- B3/B4: los cinco mutantes de reason/hash cambian grafía. No se encontró
  consumidor productivo del literal completo en tools/tests. Conservar causa
  identificable y rechazo de hash incorrecto, sin fijar capitalización.
  Si se decide API textual, probar excepción emitida/reporte real, no la línea
  fuente del traceback (adenda §2). Un código estructurado sería producto nuevo.
- B5: los cuatro mutantes de nombre del plugin afectan identidad consultable,
  no solo presentación. `_configured_plugins` en `test_accept_pytest.py`
  consulta el nombre, pero su uso sin protocolo solo exige ausencia del
  observer; no se halló consumidor productivo del registro activo exacto.
  Recomendar nombre interno. Si se declara API cooperativa, aprobar contrato
  y test pytest real que consulte registro y compruebe recibo válido del mismo
  observer (incluidas consecuencias de colisión/desregistro relevantes).

Decidir presentación o interno **no cierra** estos 15 IDs bajo TEST-002. La
adjudicación compatible con el contrato elegido sigue necesaria; simplificar
producto es opcional solo si se autoriza por valor propio, nunca para omitir
obligaciones. Allowlist condicional de tests: `test_accept_campaign.py` y
`test_accept_pytest.py` bajo `tests/unit/`; ningún cambio implícito de API.

**C: siete límites.** CONTRATO-AC1 exige 30 s por intento, 600 s por campaña,
1 MiB combinado, terminar grupo/recolectar hijo y conservar captura parcial:

- C1 `process.x__execute__mutmut_28/29`, `x__terminate__mutmut_6/7`: doble
  de proceso/espera y reloj controlado, terminación antes/después del plazo;
  observar resultado, duración y recolección. `None` puede quitar acotación;
  `2` no es equivalente a None. **Exactamente 1 s interno no está contratado**:
  decidirlo aparte, no imponer un test de argumentos por score.
- C2 `x__observe__mutmut_33`: reloj exactamente en deadline y salida lista;
  proponer frontera inclusiva (timeout antes de otra lectura) y oráculo de
  causa/captura/duración. Aclaración contractual pendiente de aprobación.
- C3 `x__execute__mutmut_31/32`: excepción con hijo vivo/streams abiertos;
  compartir montaje con A3, mantener dictamen por ID y comprobar recursos sin
  depender de GC. Cleanup y acotación no son trabajo opcional.

Allowlist propuesta: `tests/unit/test_accept_campaign.py`; dobles en los
puntos `process_transport.subprocess/selectors/time` ya usados por T5. Tope
**300 s** conjunto para C, además del de A; sin adaptador nuevo por defecto.

**D: corregir receta antes de aprobar hooks.** El JSON propone HOOK-MR-01
mismatch→pass; la adenda §6 exige status:error: no son compatibles. Propuesta
cerrada que sustituiría esa expectativa solo tras aprobación:

1. Copia del plugin y proyecto pytest mínimo en
   `build/tmp/ac1-r2-qualification/r3-hook-alternative/<run>/`; un escenario
   generado cuyo call lanza `SemanticMismatch`, IR/hash/nonce propios,
   decoradores y firmas intactos. Registrar módulo realmente cargado y hash.
2. Control: pytest exit1, `cases[0].status=mismatch`, errors vacío, evento
   call mismatch y `validate_receipt`→mismatch. Es control correcto de rechazo,
   no control pytest exit0.
3. HOOK-MR-01: cambiar solo clasificación del call mismatch→pass tras yield;
   exit real1, caso/evento pass e identidad intacta; validador→invalid por
   contradicción status/exit. No esperar status:error.
4. HOOK-SF-01: elegir solo alterar `document["exit"]` a 0 antes de persistir;
   exit real1, recibo exit0, caso/evento mismatch; validador→invalid por exit
   discordante. No dejar dos semillas alternativas en la orden ejecutable.
5. Tres ejecuciones, 30 s exteriores cada una y **120 s total** incluyendo
   preparación; grupo propio, limpieza en finally y capturas parciales.
   Evidencia de fases en `receipt.events.json`, de casos en `receipt.json`.

Allowlist solo ese directorio temporal. Exit1 por sí solo no detecta la
semilla: también ocurre en el control. No retirar decoradores ni sumar estos
resultados al bruto mutmut. Todos los presupuestos de §3 son propuestas,
no mediciones ni ampliaciones del contrato operativo.


## 4. Frente B — alcance 928 y TEST-007

| Hecho comprobado | Obligación y recomendación | Alternativa / coste aproximado | Decisión y criterio de cierre |
|---|---|---|---|
| G generó 959; E ejecutó 31 | TEST-002 exige código cambiado. Delimitar por diff y función, conservando lo medido; no excluir archivos completos. | Medir 928 con nueva selección/preflight: coste **no calibrado**, solo 9/40 funciones tenían asociaciones. Retirar la extrapolación 4.000–5.000 s de otro lote como presupuesto. | Aprobar alcance por identidad descrito abajo; revisión documental estimada ≤1 h. |
| TEST-007 sigue abierto en 3 archivos | Recomendar partición fachada **acotada** y separada, preservando comportamiento, imports y tests; sin refactor funcional amplio. | Excepción no disponible por un procedimiento vigente localizado; requiere definir y aprobar desviación/procedimiento primero. No es «coste cero». | Aprobar dirección de partición y después sus rutas concretas, o mantener bloqueo mientras se decide un mecanismo de excepción. |

Comparación base `932c835ac0eeb75010ec7a1071315b1c51f78eb6` → candidato
`01c901dfdb6713de22ac8d60737c6ecf4b4a8d98`:

| Ruta bajo `tools/wct/` | Delta del incremento | Verificado / preexistencia |
|---|---|---|
| `gate/checks.py` | Solo `_declared`: guard de gobernanza propia | 11 IDs de `_declared` ejecutados; otros **649** de funciones sin cambio, no ejecutados. |
| `selftest/fixtures_tools.py` | Solo `f9_a`: gobernanza plantada y raíz Git propia | 20 IDs ejecutados; otros **279** de funciones sin cambio, no ejecutados. |
| `gate/runner.py` | Import y entrada `REGISTRY["G-SAST-SEMGREP"]`; ninguna función modificada | Dato de módulo fuera de trampolines; **no forma parte de los 928**. Falta wiring (§5). |

Las tres fuentes son byte-idénticas entre corte G/E
`fb7f7254129bf47ebd20a50d6045ebed4982e667` y este candidato: hashes respectivos
`4797460040b5738934aa7aeb1f5c2e4fb2200f68b7506cf692883cf8ae391af6`,
`3834548749ebcdcd48862fcb67a519f5bd34326caf044192b4ac0076655d2ce7`,
`6e568767066c10bd7bc1fde6a8410133a64e30c3dc6be7cbe27b71d09acd8943`.
Conservar bruto E **27 killed + 4 survived**, ocho kills por excepción ya
ratificados y micro posterior `f9_a__mutmut_10/11/12/13` detectada por oráculo,
sin transformarlo retrospectivamente en campaña 31/31. Fuentes G/E de §1 y
`EJECUCION-INCREMENTO-F9A-LOADCONFIG-2026-09-13.md` en este directorio.

Propuesta de alcance: 928 = 649+279 como **preexistencia fuera del incremento
por identidad/diff**, sin veredicto nuevo, ni exclusión de `_declared`, `f9_a`
o archivos completos. Si una partición o cambio posterior afecta esas
funciones/rutas, revisar alcance y necesidades de verificación; la decisión
no exime cambios futuros ni evita TEST-007. No editar inventario bruto/metas.

**Regla frente a implementación del gate.** TEST-007 exige partir cualquier
archivo fuente cambiado con >100 sitios. Umbral vigente 100; métrica WCT de
`mutation_sites` (nodos AST definidos en `engine.py`, no mutantes mutmut).
Mediciones del corte, con bytes actuales idénticos: **checks 258, runner 442,
fixtures_tools 191**; `_declared` 7 y `f9_a` 8 no eximen al archivo.

La explicación anterior del PASS era incorrecta: `policy.yaml` declara
`paths.source: [src]`; `scan()` solo recorre source y **no mide esos tools**.
En archivos incluidos, G-MUT-SITES bloquea `over_limit AND changed_functions`:
el límite es total por archivo, el cambio se determina por fingerprint contra
manifest, no por Git. Un cambio de dato de módulo tampoco aparece como función
cambiada. El PASS habitual no demuestra cumplimiento de TEST-007 en estos
archivos (`CALIFICACION-AC1.md` ya advierte el alcance src).

Camino conforme mínimo: planificar la partición de esas tres rutas mediante
el `split-plan` existente y revisar cohesión antes de fijar submódulos. Runner
tiene **264 sitios de módulo**: mover solo funciones no basta. Estimación
**tres incrementos, 1–3 jornadas** de implementación/revisión; no es presupuesto
de campañas. Cada fachada y módulo resultante ≤100, imports públicos iguales,
tests intactos y verificación por identidad del traslado. Antes de crear rutas
nuevas se aprueba la allowlist concreta; el plan no inventa nombres de módulos.
No iniciar el refactor para simplificar este informe.

No se localizó procedimiento vigente de excepción TEST-007 en reglas,
runbook/CLI y procedimiento de adjudicación: el de equivalencias por ID y
`ratchet raise` **no dispensan tamaño por archivo**. La alternativa requiere
primero decisión humana explícita sobre desviación y procedimiento/registro,
y autorización separada si toca gobernanza (SEC-005/PROC-010). Sin ello rige
partición y el pendiente sigue abierto; este documento no concede excepción.


## 5. Frente C — aceptación y despacho REGISTRY

### Operador/tabla AC1 (`Q-DESIGN-ACC`)

Hecho por lectura de `mutation_cases._changed`, `campaign_steps._modes/_verdict`
y `features/wct-acceptance-evidence-001.feature`: 6×8 = **48 celdas**.
Exactamente **18 inválidas**: columnas baseline/mutation/verdict en filas 1–6.
Sus ordinales históricos (1-based, no sustituyen IR/hash) son
`1,2,4; 9,10,12; 17,18,20; 25,26,28; 33,34,36; 41,42,44`.
El operador añade `__mutated`: pass/mismatch, missing_receipt, wrong_identity,
mixed_error y fail quedan fuera del vocabulario. `_modes/_verdict` lanzan
ValueError; **error de arnés exterior no es rechazo semántico ni killed**.

Además fila 2/mutation (ordinal 10, row=1) no discrimina aun con reemplazo
válido mismatch→pass: baseline mismatch aborta antes de ejecutar mutantes.
No comparar entradas consigo mismas para simular un oráculo. Las otras 30
celdas numéricas parecen discriminantes por lectura, **no se midió** su kill.
La falta deliberada de recibo del runner **interno** es entrada del SUT; si el
SUT reporta sus errores correctamente el arnés exterior pasa. Solo discrepancia
entre resultado real y esperado permite `SemanticMismatch` exterior.

**Recomendación mínima:** aprobar contrato de selectores numéricos del fixture,
conservar operador histórico y protocolo productivo; separar aborto baseline
en otro Outline sin parámetro mutation inoperante. Es cambio de contrato de
prueba que requiere aprobación explícita, no una exclusión disimulada.

| Campo del fixture | Dominio propuesto |
|---|---|
| baseline | 1=pass, 0=mismatch |
| mutation | 0=mismatch, 1=pass, 2=missing_receipt, 3=wrong_identity, 4=mixed_error |
| verdict | 1=pass, 0=fail |

Selector desconocido sigue siendo error instrumental. Primer Outline mantiene
Given/When/Then actuales (con esos códigos documentados) y las cinco filas de
baseline sana:

| baseline | mutation | planned | verdict | killed | errors | survived | not_run |
|---|---|---|---|---|---|---|---|
| 1 | 0 | 1 | 1 | 1 | 0 | 0 | 0 |
| 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| 1 | 2 | 1 | 0 | 0 | 1 | 0 | 0 |
| 1 | 3 | 1 | 0 | 0 | 1 | 0 | 0 |
| 1 | 4 | 1 | 0 | 0 | 1 | 0 | 0 |

Segundo Outline propuesto (contrato nuevo para aprobar, no implementado):

```gherkin
Scenario Outline: Abortar antes de lanzar mutantes si falla baseline
  Given un ejecutor con baseline "<baseline>" y un mutante que no debe ejecutarse
  When ejecuto una campana con "<planned>" mutacion
  Then el veredicto es "<verdict>" con "<killed>" killed y "<errors>" errores
  And quedan "<survived>" supervivientes y "<not_run>" sin ejecutar
  And no se crea ningun intento mutante
  Examples:
    | baseline | planned | verdict | killed | errors | survived | not_run |
    | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
```

El fixture fijo usa modo mismatch válido como centinela; su independencia de
todos los modos válidos se conserva en regresión parametrizada que observa
reporte, veredicto y ausencia real de directorios `mutation-*`. No se retira
el caso de aborto de Gherkin ni se traslada solo a unit tests.

Nuevo IR: **40+7=47 celdas**, otro inventario. Trazar todas las coordenadas
históricas al nuevo: fila 1→primer Outline fila 1; filas 3–6→filas 2–5;
fila 2→Outline aborto y sus siete campos; fila 2/mutation→configuración fija
con prueba de independencia. Conservar histórico 48 intacto, sin llamarlo
47/48, kill, equivalencia ratificada ni eliminación de un ID histórico.
Si no se aprueba el nuevo denominador y contrato, Q-DESIGN-ACC sigue bloqueado.

Allowlist propuesta: **solo** `features/wct-acceptance-evidence-001.feature`,
`tests/acceptance/campaign_steps.py`, `tests/unit/test_accept_campaign.py`.
Reutilizar `_campaign`, `protocol_runner.MODES`, parser/generate,
plugin/recibos y accept_verdict; no cambiar protocol_runner ni producto.
Generados de comprobación bajo build/tmp con la herramienta; no sobrescribir
el generated histórico. Cierre: TDD, colección, controles de código desconocido
y Then incorrecto, baseline exterior sano de ambos escenarios, inventario
exacto y verificación posterior de sensibilidad; no presumir 47 killed.
Estimación **2–4 h** de implementación/revisión, **600 s** focales. Q-ACCMUT
posterior requiere autorización separada, **900 s** exteriores de preparación
+ ejecución, respetando **600 s/campaña y 30 s/intento** productivos.

Alternativa: operador enum explícito con dominios/reemplazos y validación
fuente/IR, nueva feature productiva (estimación 1–2 jornadas); también requiere
separar fila 2. Candidato ajeno existente
`/home/jandradeu/Documents/well_code_template/build/tmp/beta3-p03a-phase1-candidate`
contiene `mutation_policy.py` (`dd1a4186…`) y `mutation_cases.py` (`dd685809…`):
solo bool/str, true↔false y sufijo `__typed`; **no resuelve enums AC1**.
Reutilizable como referencia su validación fuente/hash/coordenadas, no como
injerto calificado. No copiar P03a, cambiar operador ni usar selección de
celdas para ocultar inválidas dentro de PR #53.

### REGISTRY (`PX-REG`)

Camino público leído: CLI gate → `run_tier(root,tier)` →
`REGISTRY[gate_id](root)` → `gate_sast_semgrep`. Los tests GS3
`test_binding_la_herramienta_ausente_declara_skip_visible` y
`test_binding_el_retorno_final_expone_duracion_y_comando` ya cubren SKIP y
argv literal **del gate directo**. Superseden huecos b/c de la adenda G/E;
no pedir otra decisión de contrato. Queda el despacho por la entrada real.

Encargo recomendado: solo `tests/unit/test_sast_targets.py`; reutilizar
`_raiz_git_con_politica`, `_instrumento_controlado`, `_document`; raíz Git
válida que exige `src/a.py`, sin sustituir REGISTRY en el control positivo.
Invocar `REGISTRY["G-SAST-SEMGREP"](root)` con dos respuestas semgrep exit0:

- JSON scanned=["src/a.py"], sin hallazgos/errores → PASS, gate_id exacto.
- JSON scanned=[], sin hallazgos/errores → ERROR, gate_id exacto y resumen
  `0 de 1 fuentes`, con detalle `omitida: src/a.py` (rama de omisión total).

Sensibilidad **en copia exclusiva build/tmp**: (1) reponer la entrada antigua
`external(...)`; (2) entrada que retorna PASS constante. Ambas deben fallar
por aserción de estado/diagnóstico en el caso de omisión, con original verde;
fallo de colección/setup no acredita wiring. Afirmar función/llamada solamente
no basta (TEST-003). No es una prueba CLI completa, sino del punto público de
despacho que cambió; las puertas finales conservan su alcance.
Decisión: autorizar ese test y dos controles acotados, no contrato nuevo.
Estimación **1–2 h**, tope focal **120 s**, colección/fast aparte.
Alternativa full para comprobar despacho mezcla gates y cuesta más (tope
1800 s); sigue siendo obligatorio al calificar, no para sustituir este test.


## 6. Frente D — recomendación de salida incremental

Recomendar **`1.0.0b3.dev1` / `v1.0.0b3.dev1`**, pendiente de decisión humana,
como salida de desarrollo previa a beta.3. El plan original §5 propone
`v1.0.0-beta.3` y exige el contrato integral; no afirmar que dev1 lo cumple.
Alternativa: esperar beta.3 completa, coste no estimable sin decisiones y
presupuestos de los incrementos restantes. Dev1 reduce la promesa funcional,
no las exigencias de calidad del incremento publicado.

Notas propuestas, sujetas a calificación: **entregado** = núcleo AC1 de
baseline/recibos/atribución y endurecimientos realmente incluidos en el diff;
**experimental** = protocolo cooperativo y evidencia por lotes/identidad con
sus límites; **pendiente** = cierre integral AC1 mientras no pase su cadena,
y capacidades no integradas. No anunciar autonomía, ahorro, superioridad de
modelos ni mutación fresca/completa de todo WCT.

Contraste con BETA3/PLAN §1/§5: fuera quedan resto de B3-P1 (cadena mínima de
evidencia completa), B3-P2 molde/schema/dos layouts, B3-P3 adopción brownfield,
compatibilidad/migración nuevas, B3-P4 contexto y contract tests ensamblados,
B3-P5 piloto/corpus/calidad/coste y G1b como claim acreditado. B3-P0 no se da
por resuelto por este informe; B3-P6 no está ejecutado. Tampoco se incorporan
P02–P10 o P03a por analogía con el cierre de GS. El eventual perfil limitado
no puede eludir ninguna obligación aplicable al código que sí salga.

Reutilizar `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md` §2/§4–§8 y
PLAN §5; **no crear otra revisión general de release**. Siguen explícitamente
pendientes: decisión de versión; bump/lock/notas con autorización propia antes
del congelamiento; destino/owner de custodia y recuperación; SBOM y smokes;
revisión protegida y bless; CI completa; merge y calificación post-merge de
M/V; autorización D3 y publicación/verificación remota. El plan de custodia no
es evidencia de recuperación: copia durable independiente antes de D3,
manifiesto sin autorreferencia, prueba en host limpio; asset de prerelease
solo copia posterior. El runtime de release se prepara en encargo propio según
§4, no se reutiliza sin más el runtime histórico ni se instala en este turno.

Decisión exacta requerida: aceptar alcance dev1 y convención de versión,
sin autorizar todavía bump/lock ni publicación. Acción posterior: encargo de
versión sobre `pyproject.toml`/`uv.lock` y notas existentes, validando la
compatibilidad de Commitizen y tags históricos antes de revisar el diff
protegido. Cierre de salida solo con SHA autorizado, SBOM/smokes, custodia,
CI/gates y consulta remota (prerelease=true, draft=false, tag→V, assets,
sin Latest estable) conformes. No mover tags ni reparar main directamente.


## 7. Autorizaciones propuestas — NO APROBADO

Cada texto se aprueba o rechaza por separado; aprobar una fila no concede las
demás. Las decisiones se incorporan a este plan/matriz con su referencia
humana, sin crear un dossier por frente. Hasta entonces todos los pendientes
analizados siguen abiertos.

1. **A1 — NO APROBADO:** «Ratifico exclusivamente
   `tools.wct.accept.campaign.x__attempt__mutmut_4` bajo bytes/runtime r3,
   por la semántica falsy de ensure_ascii=None; el bruto no cambia».
2. **A2 — NO APROBADO:** «Ratifico exclusivamente
   `tools.wct.accept.campaign.x__attempt__mutmut_9` bajo bytes/runtime r3,
   por alias del códec UTF-8; el bruto no cambia».
3. **A4–A11/CAST — NO APROBADO:** «Ratifico los ocho IDs
   `tools.wct.accept.process.x__observe__mutmut_7/11/12/13/22/26/27/28`
   históricos por identidad de typing.cast y apruebo transferencia documental
   al hash 84b9340f… únicamente con el diff de dos casts y precondiciones de §3;
   no transfiero ni renumero inventarios ni ratifico otros IDs».
4. **A-revisión/C/DD — NO APROBADO:** «Autorizo las comprobaciones de las cuatro
   cuestionadas, los siete límites y los dos hooks con entradas, semillas,
   oráculos, allowlists y topes de §3. Mantengo acotación/recolección/captura
   obligatorias; aclaro deadline inclusivo, no impongo exactamente wait=1 s.
   No autorizo cambios de producto ni ratificación automática tras una sonda».
5. **B1–B5 — NO APROBADO:** «Declaro JSON semántico sin indentación estable para
   B1/B2; causa identificable y rechazo de hash, sin grafía exacta para B3/B4;
   nombre de plugin interno para B5 conforme a los consumidores revisados.
   No declaro por ello equivalentes ni excluidos los 15 IDs; su disposición
   bajo TEST-002 permanece pendiente».
6. **PX-928 — NO APROBADO:** «Delimito este incremento por diff
   932c835a…→01c901df…: _declared y f9_a medidos, y wiring REGISTRY por verificar.
   Los 928 de otras funciones son preexistencia fuera del incremento, sin
   veredicto ni exclusión de archivos completos. Cualquier cambio posterior
   exige revisar alcance por identidad/diff; TEST-007 permanece aplicable».
7. **PX-T007 — NO APROBADO:** «Selecciono partición fachada acotada como vía
   conforme. Autorizo únicamente diseñar el reparto de checks/runner/fixtures_tools
   mediante split-plan y presentar allowlist concreta antes de editar.
   No concedo excepción ni autorizo todavía crear módulos. Si prefiero una
   excepción, decidiré primero su procedimiento y registro explícitos».
8. **PX-REG — NO APROBADO:** «Autorizo el test conductual por REGISTRY y los dos
   controles de sensibilidad descritos en §5, solo test_sast_targets.py como
   cambio permanente, sin cambios de producto ni nuevos contratos».
9. **Q-DESIGN-ACC — NO APROBADO:** «Apruebo los selectores y los dos Outlines de
   §5, inventario nuevo de 47 trazado al histórico de 48, aborto independiente
   del modo y códigos desconocidos como error; autorizo TDD y verificación
   focal en las tres rutas listadas. No autorizo P03a/operador tipado, exclusión
   de IDs previos ni Q-ACCMUT: esa ejecución conserva autorización separada».
10. **REL-SCOPE/VERSION — NO APROBADO:** «Selecciono salida incremental
    1.0.0b3.dev1 con los límites de §6, sin claim beta.3 completa ni elusión
    de requisitos del código publicado. No autorizo aún bump, lock, bless,
    merge, tag ni publicación».

Custodia necesita una decisión adicional con **destino durable, responsable,
retención y prueba de recuperación concretos**, todavía no proporcionados.
Bless exige revisión humana del diff final; D3 exige M/V calificado. No se
ofrecen ahora como autorizaciones vacías o concedidas por aprobar §7.


## 8. Siguiente oleada técnica — NO EJECUTAR HASTA APROBACIÓN

El encargo siguiente empieza solo tras respuestas explícitas a §7. Es una
oleada técnica acotada, no otra ronda de dossiers; ejecuta únicamente los
módulos aprobados y no pretende cerrar todos los pendientes por omisión.

```text
ENCARGO — Comprobaciones r3, wiring y tabla AC1 aprobados
NO EJECUTAR HASTA APROBACIÓN

Repositorio: /home/jandradeu/Documents/well_code_template
Worktree fuente: /home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration
Rama fuente: codex/beta3-ac1-r2-integration; PR #53 en borrador.
Corte leído por el plan: 01c901dfdb6713de22ac8d60737c6ecf4b4a8d98.
Plan vinculante: docs/evolution/plans/BETA3/EXECUTION/PLAN-EJECUTABLE-CIERRE-AC1-BETA3-2026-09-15.md,
secciones 3–7, con parámetros, tablas, IDs, semillas, oráculos y allowlists.

PUERTA INICIAL
Lee AGENTS.md, CONTRATO-AC1, CALIFICACION-AC1 y la matriz en ese directorio.
Exige referencias humanas explícitas a los textos aprobados de §7; registrar
cuáles NO están aprobados. La mera presencia de este prompt no da permiso.
Comprueba HEAD completo, remoto, índice, diff respecto al corte y trabajo ajeno.
El commit documental que publique este plan será la nueva base: verifica que
su delta es solo el plan/matriz, sin asumirlo ni fijar un SHA futuro.
Crea copias/worktrees privados desde esa base confirmada, con índice propio;
usa build/tmp para temporales. No tocar ni stagear el documento untracked
PREPARACION-SALIDA-INCREMENTAL-BETA3.1 ni archivos del checkout principal.
No instalar ni cambiar runtime; registrar ejecutable, imports, versiones y hashes.
Para sondas históricas usa el runtime existente build/tmp/sh-p01-CND-80B8/.venv
solo tras comprobar procedencia; no lo presentes como runtime de release.

TRABAJO APROBABLE (cada módulo tiene permiso propio)
A. Si §7.4 aprobado: cuatro comprobaciones r3 §3, tope300s; siete límites,
   tope300s; hooks control+HOOK-MR-01+HOOK-SF-01, 30s/corrida y 120s total.
   Solo copias temporales y, si corresponde a regresiones autorizadas,
   tests/unit/test_accept_campaign.py. Priorizar dobles por fronteras existentes.
   Acreditar activación real/ID y causa observable, conservar control y parcial.
   No ratificar resultados; si falla original, detener ese frente y proponer
   reparación separada. La clasificación no da permiso para cambiar producto.
B. Si §7.8 aprobado: test en tests/unit/test_sast_targets.py que llame entrada
   REGISTRY real con src/a.py requerido: scanned completo PASS, omitido ERROR
   con resumen 0 de 1 fuentes y detalle omitida: src/a.py. Reusar helpers de
   §5. Original verde y en copia dos
   semillas de wiring (external antiguo / PASS fijo) fallan por aserción
   conductual. Tope120s focal; no repetir SKIP/comando ya cubiertos ni full.
C. Si §7.9 aprobado: TDD de selectores numéricos y dos Outlines exactos §5.
   Solo features/wct-acceptance-evidence-001.feature,
   tests/acceptance/campaign_steps.py y tests/unit/test_accept_campaign.py.
   Operador productivo intacto; tabla 40+7, trazabilidad histórica48→nuevo47,
   aborto para todos los modos válidos, códigos desconocidos siguen error,
   Then incorrecto produce SemanticMismatch. Generados solo en build/tmp.
   Tope600s de verificación focal; NO ejecutar Q-ACCMUT ni campaña global.
D. Si §7.7 aprobado: lectura/split-plan de las tres rutas, identificar reparto
   coherente (incluye datos de módulo runner), presentar allowlist exacta y
   métricas esperadas para aprobación. NO implementar partición sin esa decisión.

ORDEN Y LÍMITES
A y C comparten test_accept_campaign.py: serializar sus cambios o worktrees
independientes con integración revisada. B puede ir paralelo; hooks solo en
su directorio. Si se integra después una partición, revisar/repetir controles
sobre el nuevo árbol según impacto, nunca trasladar evidencia automáticamente.
No campañas928, nuevos contratos de literales/API, adaptadores, P03a, edición
protegida, manifests manuales, ratchets, bless, merge, bump, tag ni release.
No crear issues externos ni dossiers permanentes por agente.

VERIFICACIÓN Y ENTREGA
Tests enfocados primero rojos por defecto plausible, luego verde; colección
pytest --collect-only -q después de tocar tests. Focal no equivale a gate.
Verifier independiente sin permiso de escritura revisa evidencia y límites;
git diff --check y fast exigido. No omitir obligaciones posteriores de mutación,
cobertura/CRAP/DRY/finales: lo no autorizado queda abierto para su encargo.
Conservar logs cerrados, hashes/IDs y dictamen por resultado sin cambiar brutos.
Parar por presupuesto, fallo instrumental, falta de activación, alcance nuevo,
contrato sin aprobar, original incorrecto o identidad discordante; no ampliar
ni reintentar campañas por iniciativa propia.
Entregar diff concreto, comandos/resultados/tiempos y pendientes en el plan/
matriz existentes con referencias a evidencia temporal; sin commit/push de
producto ni integración automática a PR #53. El coordinador solicita después
la revisión/autorización del incremento concreto. Detenerse al finalizar.
```


## 9. Dependencias, presupuestos y paradas

Decisiones A1/A2/CAST son documentales independientes. A/C instrumental y
hooks pueden prepararse en copias separadas; REGISTRY no depende de medir
928. Tabla AC1 y r3 comparten test_accept_campaign: coordinar integración.
Partición necesita primero rutas aprobadas; su resultado precede al
congelamiento/calificación y obliga a revisar evidencia de las rutas movidas.
La siguiente oleada no cierra B1–B5 ni TEST-007 automáticamente.

Después, en **encargos separados**: mutación de fuentes resuelta →
Q-ACCMUT → Q-COVCRAP → Q-DRY → Q-FULL PRE-BLESS (§2) → revisión protegida →
bless → integridad/finales/CI POST-BLESS → merge → calificación M/V → D3.
Q-PRE-EQ comprueba sobre T/B/M aplicables las precondiciones de GS3 24/29/33
(acta §5: productor 1.174.0, fuente/COMMAND, stdout directo UTF-8 sin BOM,
decodificación efectiva UTF-8). Si cambian, no trasladar ratificación.
Q-RANDOM conserva suite aleatoria, property separado y colección. Custodia
puede prepararse en paralelo y debe recuperarse **antes** de D3, sin depender
de que exista un asset de release. Versión/lock aprobados antes de T/bless.

| Trabajo futuro | Tope propuesto / vigente | Parada |
|---|---|---|
| A-cuatro / C-siete / hooks / REGISTRY / tabla | 300 / 300 / 120 / 120 / 600 s (estimados; no medidos) | Conservar parciales, no ampliar alcance/tiempo automáticamente. |
| Q-ACCMUT | 900 s exterior propuesto; 600 s/campaña y 30 s/intento vigentes | Baseline inválida, survived/error/not_run impiden PASS. |
| Q-COVCRAP | 600 s estimados; diff ≥90%, CRAP ≤6 y ratchet total vigentes | No trasladar LCOV de otro candidato. |
| Q-DRY | 600 s estimados | Cero duplicación nueva; no pasar a la siguiente puerta con findings pendientes. |
| Q-FULL | 1800 s vigente, por corrida autorizada | PRE-BLESS conservar FAIL de integridad; ningún otro bloqueo sin resolver. POST-BLESS exigir verde completo. |
| Q-RANDOM / Q-PRE-EQ | 600 / 120 s estimados | Flakes se registran; precondición fallida vuelve a decisión humana. |
| Recuperación custodia | 600 s estimados | Sin recuperación conforme no hay D3. |

Estos son topes de planificación, no permisos ni mediciones. No sustituyen
las autorizaciones de runtime/campañas/recursos de cada encargo. El fast
reglamentario no autoriza full, campaña o sondas adicionales. Ante evidencia
local ausente, cambio no revisado, allowlist insuficiente o agotamiento,
conservar diagnóstico y parar el trabajo dependiente; no inventar excepción.


## 10. Bloqueos reales de integración y publicación

- **Bless:** resolver pendientes técnicos del alcance elegido, calificación
  pre-bless con resultados reales y revisión humana del diff protegido final.
  G-META-1 sigue FAIL; el bless no sustituye calificación.
- **Merge:** post-bless íntegro, CI completa verde, revisión integral,
  autorización y salida de borrador. PR #53 permanece en borrador ahora.
- **Publicación:** versión y alcance decididos; custodia durable recuperada;
  SBOM, smokes y calificación de M/V; D3 y verificación remota del tag,
  prerelease/metadata/assets. Ninguno se ejecuta en este encargo.
- **AC1:** r3, alcance por identidad, TEST-007, wiring y operador/tabla más
  cadena E8 pendientes. Los cierres GS y el eventual merge no la acreditan.
- **beta.3 integral:** contrato de salida de BETA3/PLAN §5 y alcance §1
  pendientes; la propuesta dev1 no anuncia su cumplimiento.
