# Cierre del frente C y revisión de partición/A12 (2026-09-15)

Registro sucesor del encargo «desbloquear e integrar el frente C de
aceptación de la PR #53 y comprobar dos afirmaciones técnicas del informe de
la oleada». Ejecuta la decisión humana ya otorgada (alternativa 1 de §4.3 de
`OLEADA-TECNICA-CIERRE-AC1-2026-09-15.md`): reformular únicamente los tres
pasos compartidos del Outline de aborto. Este documento **no** acredita AC1,
no cierra beta.3, no bendice, no actualiza manifiestos, no hace merge, bump,
lock, tag ni release, no ratifica equivalencias ni ejecuta Q-ACCMUT,
mutmut ni campaña global de aceptación. La campaña de los 928 IDs sigue sin
ejecución y sin veredicto.

## 1. Identidades y preflight

- Worktree de integración `build/tmp/beta3-ac1-r2-integration`, rama
  `codex/beta3-ac1-r2-integration`, HEAD de partida
  `06af946001775c9e6d56ab1887917f3f5ca0bcc4` = `headRefOid` de la PR #53
  (OPEN). Sin drift remoto al iniciar ni al publicar. Índice vacío; único
  untracked el documento ajeno
  `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md`, conservado fuera
  del incremento (ni leído para integrar, ni copiado, ni stageado).
- Parche preservado recibido: la ruta relativa del expediente resuelve al
  propio worktree de integración:
  `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration/build/tmp/oleada-ac1-cierre-20260915/c-candidate/frente-c-exacto.patch`,
  sha256 verificado `497cd9cf328711d7c0cf69cd99db7c2f83a0533455dfa5f48a5157636be9c4c3`
  — coincide con el comunicado. Con él, `c-green.log` (49 passed) y
  `g-accept-counterexample.log` (3 hallazgos).
- Runtime acreditado: `.venv` del worktree, Python 3.13.14, pytest 9.1.1
  (imports y ejecución con `UV_NO_SYNC=1 uv run` o el intérprete del venv;
  sin instalar ni sincronizar el entorno compartido). Copias aisladas vía
  `git archive 06af946 | tar -x` bajo `build/tmp/cierre-c-r2/`
  (nota operativa: `git apply` desde directorios anidados dentro del repo
  «salta» parches con rc=0 engañoso; los controles usaron copia directa de
  archivos).
- Dos de los tres archivos base del parche siguen en los blobs de HEAD
  (`campaign_steps.py` `c3236ab…`, feature `257aed7…`);
  `test_accept_campaign.py` divergió (`ff20c65…` → `6e57db7…`, regresión del
  frente A), por lo que el candidato se **recompuso** sobre el HEAD real en
  lugar de reemplazar el archivo: el parche exacto aplica limpio (los hunks
  caen en la zona temprana intacta) y el delta del frente A (aditivo, al
  final) se conserva íntegro.

## 2. Reproducción del bloqueo (candidato exacto)

En copia aislada `build/tmp/cierre-c-r2/c-exact-repro` (worktree Git temporal
en 06af946 + parche exacto verificado por hash):

- `gate_accept` real sobre la copia: **FAIL** con exactamente 3 hallazgos
  `placeholder-variant` en las líneas 17, 18 y 19 de la feature — los tres
  pasos compartidos `When/Then/And` del Outline de aborto. Idéntico al
  contraejemplo preservado (`g-accept-counterexample.log`), ahora sobre el
  HEAD actual: el bloqueo es el comunicad, no otro fallo del entorno.
- `gate_accept` sobre HEAD limpio: **PASS** (el fallo es nuevo y atribuible
  al diseño literal).

## 3. Reformulación autorizada aplicada

Secuencia TDD documentada sobre la copia aislada, luego integrada:

1. **Rojo** (solo la feature reformulada; implementación intacta): 6 fallos
   conductuales, 44 verdes. `execute_scenario` del aborto muere en
   `AssertionError: missing acceptance step: ejecuto la campana abortada con
   "1" mutacion` (no por import) y el oráculo congelado reporta
   `abort steps differ`. Ningún fallo por colección o import.
2. **Verde**: `campaign_steps.py` reconoce las tres formas nuevas y despacha
   **al comportamiento existente** (`_campaign`/`_verdict`/`_remaining`;
   fusionadas con `or` por SIM114 de ruff, sin lógica duplicada); el
   oráculo `ABORT_STEPS` del test se actualiza a los literales aprobados.
   El resto del diseño aprobado no cambia: dos Outlines, cinco filas de
   baseline sana, aborto de siete campos, selectores numéricos
   (`BASELINE_SELECTORS`/`MUTATION_SELECTORS`/`VERDICT_SELECTORS`),
   centinela `mismatch`, paso «no se crea ningun intento mutante».

Pasos aprobados aplicados (únicos cambios de texto en el Outline de aborto):

```gherkin
When ejecuto la campana abortada con "<planned>" mutacion
Then el veredicto del aborto es "<verdict>" con "<killed>" killed y "<errors>" errores
And tras el aborto quedan "<survived>" supervivientes y "<not_run>" sin ejecutar
```

La normalización de `ir_dry` (números y cadenas entrecomilladas → `<value>`)
confirma que las tres formas nuevas difieren de las primarias por palabras
reales, por lo que los hallazgos desaparecen por diseño, no por configuración.
No se tocó G-ACCEPT, sus reglas ni su configuración.

### Reparaciones propias de la recomposición (no estaban en el parche exacto)

El parche exacto nunca pasó G-LINT/G-INTROVERT (se revirtió antes de la
publicación). La recomposición sobre HEAD añadió dos reparaciones:

- **Lint**: E501 en dos líneas de `campaign_steps.py` y PT011 en los dos
  `pytest.raises(ValueError)` de selectores desconocidos (ahora con `match=`
  que además fija la identidad del error instrumental).
- **Introvert/ratchet**: cinco tests del parche exacto quedaban
  `introverted` (baseline 0 → ratchet rojo; primera corrida normativa falló
  en `test_repo_introverted_ratchet_holds_baseline` — registrado como intento
  inválido). Causa: el helper local `_feature_ir()` rompía la derivación
  desde `parse_feature` (SUT) que el analizador exige, y los tests de
  mapeo aseveraban solo sobre `context` (arnés). Corrección:
  `ir = parse_feature(_feature_path())` inline en los cinco casos, y los dos
  tests de selectores ahora ejecutan una **campaña real** vía `run_mutations`
  con los modos mapeados y aseveran el estado del reporte (los selectores
  numéricos quedan probados contra el supervisor real, no solo contra el
  diccionario del arnés). Tras la corrección: 0 introverted, ratchets OK.

## 4. Pruebas y criterios de cierre de C

| Criterio del encargo | Evidencia | Resultado |
|---|---|---|
| G-ACCEPT sin hallazgos nuevos y PASS final | `gate_accept` real sobre el candidato integrado; y dentro del tier commit | **PASS, 0 hallazgos** |
| Ambos escenarios se ejecutan realmente | `test_ac1_feature_executes_real_campaigns`: 6 reportes reales de campaña (5 primarios + 1 aborto), sobre subprocesos `protocol_runner` | **Verde** |
| Examples = inventario aprobado exacto | Oráculo congelado `_inventory_violations` (nombres, pasos, filas, campos) | **Verde** |
| Vacío/retirada/duplicación/alteración bloquean | Parametrizada `test_ac1_inventory_oracle_rejects_corruption` (4 casos) + control de artefacto: retirar una fila del `.feature` real en copia aislada puso 3 tests en rojo (base verde demostrada antes) | **Verde** |
| Selector desconocido → error instrumental | `test_ac1_unknown_selector_is_an_instrumental_error` (3 givens, `ValueError` con `match`, y `not isinstance(..., SemanticMismatch)`) + variante de veredicto | **Verde** |
| Then contractual incorrecto → SemanticMismatch | `test_ac1_wrong_numeric_then_is_semantic_mismatch` (veredicto `1`→`0` sobre fila real) | **Verde** |
| Baseline exterior sana | Las cinco filas primarias ejecutan campañas reales con `baseline status == "pass"` aseverado sobre los 5 reportes | **Verde** |
| Aborto independiente de los cinco modos válidos | `test_ac1_failed_baseline_aborts_independently_of_every_valid_mode` (5 modos, reporte/veredicto/ausencia `mutation-*`) | **Verde** |
| Sin intentos mutantes si falla baseline | Paso Gherkin `no se crea ningun intento mutante` + globs `mutation-*` vacíos en aborto, centinela e independencia | **Verde** |
| Regresiones A y B intactas y verdes | `test_failed_observation_reports_reaps_and_closes_live_child` (A) conservada byte a byte; `test_sast_targets.py` (B) sin tocar; ambos archivos verdes (104 passed conjunto) | **Verde** |

No se declara 47/47 killed (el inventario 47 es denominador de diseño, no un
veredicto de campaña); un selector desconocido generado por mutación sería
error instrumental, no killed. Q-ACCMUT, mutmut y campañas globales: **no
ejecutados** (prohibidos en este encargo).

## 5. Trazabilidad de inventarios 48 → 47

Sin cambios respecto al diseño aprobado de la oleada (§4.2 de su informe),
ahora ejecutada: inventario histórico 48 = 6 filas × 8 campos intacto; el
nuevo compone 40 (primer Outline: filas históricas 1 y 3–6, traducidas a
selectores numéricos) + 7 (Outline de aborto: fila 2, siete campos); la
celda fila 2/mutación pasa a la configuración fija `mismatch` con la prueba
parametrizada de independencia de los cinco modos. El test
`test_ac1_feature_inventory_traces_the_48_historical_coordinates` recorre las
48 coordenadas y afirma su destino (`traced == 48`); el total de celdas del
IR nuevo suma 47. Ningún ID histórico eliminado ni resultado trasladado.

## 6. Investigación acotada — partición y parches (TEST-007)

Informe completo: `build/tmp/cierre-c-r2/particion/INFORME.md` (experimento
desechable en `…/particion/sandbox`, tests byte a byte, runtime prestado,
presupuesto real ~4,9 s de 180 s). Resumen de la tabla por patrón:

| Patrón de import/patch | Evidencia | Veredicto |
|---|---|---|
| P1: string-setattr sobre atributo stdlib compartido vía ruta `runner.shutil.which` / `runner.subprocess.run` (10 archivos: test_gate_secrets, test_gate_tiers, test_gate_config_wiring, test_gate_commands, test_gate_docstrings, test_gate_coverage_total, test_gate_drytok, test_gate_mutation, …) | El parche resuelve `runner.subprocess` → objeto módulo stdlib **compartido** y lo muta para todo el proceso; nadie usa `from subprocess import run`. Control discriminante: ambos falsos invocados con `__module__` = submódulo nuevo tras mover `gate_secrets`. Precedente vigente: `gate_mutation` ya vive en `mutation.py` y hoy se intercepta parcheando `tools.wct.gate.runner.shutil.which` | **COMPATIBLE** con mover funciones |
| P2: string-setattr sobre nombre co-importado en runner (`runner.remote_base`) | `test_gate_config_wiring.py:41`; consumidor `gate_coverage_diff`. Discriminante: la falsa **jamás** se invoca tras el traslado; corre la real (hit `run:git`), y la suite sigue verde (**rompimiento silencioso** demostrado) | **INCOMPATIBLE** con mover `gate_coverage_diff` sin reescribir el punto de parche o dejarla en la fachada |
| P2′: `runner.scan_mutations` | `test_mutation_gate.py` (5 sitios); consumidor `gate_mutation_sites` | Incompatible por el mismo mecanismo (no movida en el experimento) |
| P2″: `runner.REGISTRY` | `test_gate_preflight.py:30`; consumidor `run_tier` | Compatible mientras `run_tier` quede en la fachada |
| P3: import directo de la función desde runner | 4+ archivos (`from tools.wct.gate.runner import gate_secrets`, …) | **COMPATIBLE** (la fachada re-exporta el mismo objeto) |
| P4: sustitución del objeto completo (`setattr(m, "subprocess", SimpleNamespace)`) | **No existe** sobre runner (existe para `process_transport` en test_accept_campaign; no se extrapola) | No presente |
| P5: parche en sitio de definición (`util.git.run_git`) | `test_gate_tiers.py:85,113` | Compatible/neutro |

**Nota sucesora que corrige §5.4 del informe de la oleada:** la afirmación
general «mover las funciones que usan shutil/subprocess cambia su espacio de
nombres global y rompe esos parches» queda **refutada por patrón de uso**
para los parches de `shutil.which`/`subprocess.run` (P1, la mayoría
abrumadora): esos parches nunca vivieron en el namespace de `runner` sino en
el módulo stdlib compartido, y siguen interceptando tras el traslado
(demostrado con control discriminante y con el precedente de `mutation.py`).
Queda **confirmada acotadamente** para los parches de nombres co-importados
en runner (P2: `remote_base`), con el matiz crítico de que ese rompimiento
es hoy **silencioso** (la suite no lo detecta; exige control discriminante).
Nada de esto elige variante A/B ni amplía la allowlist de implementación;
la partición sigue sin estar autorizada y TEST-007 sigue abierto.

## 7. Investigación acotada — A12 y capacidad de pipes

Dictamen completo: `build/tmp/cierre-c-r2/a12/DICTAMEN.md` (presupuesto real
~0,24 s de 60 s; documentación primaria `man 7 pipe`, `man 2 read`,
`man 2 fcntl` + sonda local `os.pipe`). Veredicto: **justificación corregida
y acotada** — la conclusión del renglón (sin divergencia observable) se
mantiene, el mecanismo invocado no:

- Pedir 65537 bytes es una petición **legal**: `read(2)` la sirve siempre
  como lectura corta de `min(count, disponible)` (sonda: `os.read(fd, 65537)`
  con 65536 disponibles → 65536, exit 0). Lo imposible con capacidad por
  defecto es que una sola `read(2)` **devuelva** 65537, no que se pida.
- El 65536 es la **capacidad por defecto de este host** (16 páginas de
  4 KiB, verificada `F_GETPIPE_SZ`; configurable con `F_SETPIPE_SZ`, tope
  sin privilegios `/proc/sys/fs/pipe-max-size` = 1 MiB): propiedad del host,
  no garantía de POSIX («Applications should not rely on a particular
  capacity»). PIPE_BUF (4096) es atomicidad de escrituras: pista falsa aquí.
- `_read` usa `os.read` cruda sobre fd (una syscall), no el `BufferedReader`
  de Popen; a nivel stream la afirmación sería falsa (`BufferedReader.read(65537)`
  devuelve 65537 encadenando lecturas internas — contraejemplo demostrado
  que NO aplica a este código).
- **Consecuencia para el plan**: la precondición del oráculo A12 propuesto
  («≥65537 bytes disponibles») es físicamente inalcanzable en un pipe con
  capacidad por defecto; construirla exige `F_SETPIPE_SZ` desde el arnés, y
  aun así solo observaría granularidad de lecturas, no los artefactos
  persistidos. A12 **sigue pendiente**: no se ratifica equivalencia por
  ausencia de contraejemplo ni por esta corrección (la equivalencia total
  bajo capacidad por defecto y la confinada a syscalls bajo capacidad
  ampliada dejan abierta la decisión: equivalencia estructural vs hueco de
  oráculo).

## 8. Verificación del candidato integrado

Cwd: worktree de integración. Runtime: `UV_NO_SYNC=1 uv run` sobre `.venv`
(Python 3.13.14). Logs en `build/tmp/cierre-c-r2/`.

| Verificación | Comando | Resultado |
|---|---|---|
| Espacios en blanco | `git diff --check` | Limpio |
| Colección completa | `pytest --collect-only -q` | **686** coleccionadas; conciliación: HEAD puro 667 (referencia en copia aislada) + 19 nuevas, todas en `test_accept_campaign.py` (los 19 del diseño C: 1 trazabilidad + 4 corrupción + 1 Then incorrecto + 5 independencia + 3 mapeo + 1 centinela + 3 selector desconocido + 1 selector de veredicto) |
| Focales A+B+C | `pytest tests/unit/test_accept_campaign.py tests/unit/test_sast_targets.py -q` | **104 passed** (50 + 54), 11,9 s |
| Suite normativa | `pytest -q tests/unit tests/integration -m "not property"` | **684 passed** (2:21). Primera corrida sobre un estado intermedio: 1 failed (`test_repo_introverted_ratchet_holds_baseline`, introverted 5>0) — intento inválido registrado, corregido (§3), reejecución final verde |
| Property por separado | `pytest -q tests/property` | **1 passed** |
| G-ACCEPT | `gate_accept` real (gate del tier) | **PASS, 0 hallazgos** |
| Ratchets | `wct ratchet check` | «Todos los ratchets se mantienen», exit 0 |
| Introvertidos | `wct introvert` | 0 introverted (413 extroverted / 5 conditional / 5 questionable / 8 cloistered); G-INTROVERT PASS |
| Fast gate | `wct gate --tier fast` | **7 PASS**, exit 0 |
| Tier commit | `wct gate --tier commit` | **20 PASS + G-META-1 FAIL** (2m56s). G-ACCEPT PASS |
| Integridad | `wct integrity check` | exit 1; drift **23 rutas = 7 modificadas + 16 nuevas**, recalculadas una a una: mismas rutas que la oleada (governance/lint/vulture_whitelist.py, pyproject.toml, uv.lock, tools/wct/accept/pipeline.py, gate/checks.py, gate/runner.py, selftest/fixtures_tools.py + 16 nuevas de accept/semgrep). **Ninguna ruta del incremento C** (features/ y tests/ no son rutas protegidas): cero drift nuevo |

G-META-1 rojo pre-bless por el drift acumulado, esperado y no nuevo; ningún
otro fallo. Las focales no se presentan como ejecución de un gate global.

## 9. Dictamen del verifier independiente

Agente distinto del autor, sin escritura sobre producto/tests; evidencia en
`build/tmp/cierre-c-r2/verifier/VEREDICTO.md`. **Dictamen: APROBAR.** Lo que
ejecutó: diff compuesto contra HEAD real (byte a byte el parche final,
sha256 `3438f825…`; exactamente los tres archivos; documento ajeno fuera;
nada de partición/A12 filtrado); frente A byte a byte idéntico a HEAD y
frente B intacto (0 funciones eliminadas, 8 añadidas); focales A (50
passed) y B (54 passed); G-ACCEPT real PASS 0; control de artefacto en
copia propia (verde → sabotaje de una fila de Examples → 2 failed, exit 1);
ejecución independiente con script propio que observa las 5 campañas reales
del primario (baseline pass + `mutation-*` real) y el 6.º reporte del aborto
(mismatch, not_run=1, cero `mutation-*`); control de fidelidad con el
parche exacto aplicado en scratch — delta = exactamente la reforma §4.3-1
en feature/steps, refuerzos estrictamente aditivos en tests. Revisó
documentalmente: trazabilidad 48→47 (conteos 40+7=47 y traced==48),
clasificación de errores (instrumental ≠ SemanticMismatch; ningún error
instrumental contado como éxito) y las dos investigaciones con anclajes
verificados (`os.read` cruda L23, truncado L27; sonda A12 reproducida con
salida idéntica; 0 `from subprocess/shutil import` en el repo).

Observaciones no bloqueantes registradas: (1) G-ACCEPT per se no detecta
manipulación del inventario de Examples — la protección vive en G-TEST, que
sí enrojece (así se diseñó: oráculo congelado en tests); (2) invocar gates
con el venv activado en PATH para evitar dos falsos fallos ambientales de
`test_sast_targets` (semgrep ausente fuera de `uv run`; preexistentes en
HEAD y reproducidos en copia pura); (3) los refuerzos de tests más allá de
los tres pasos (PT011, introvert) fueron verificados aditivos.

## 10. Presupuestos reales

| Frente | Tope | Consumo real |
|---|---|---|
| C (focales + controles, autor) | 600 s | ~36 s: reproducción bloqueo ~2 s; HEAD limpio ~1 s; rojo 4,2 s (+detalle ~1 s); verde 4,7 s; control artefacto 4,3 s base + 4,1 s rojo; focales A+B 11,9 s; focales post-corrección 4,5 s |
| C (verifier) | incluido arriba | ~40 s de pytest/gates (focales A/B, G-ACCEPT, sabotaje, ejecución independiente, control de fidelidad) |
| Partición | 180 s | ~4,9 s (investigador; sandbox + corridas + discriminantes) |
| A12 | 60 s | ~0,24 s (man + sonda) |

Total C ≈ 76 s de 600 s (autor + verifier).

Colección, suite normativa, property y gates se contabilizan aparte (138 s +
141 s + 0,4 s + 1 s + 176 s). Intentos inválidos incluidos: primer `git
apply` en directorio anidado (saltado, rc engañoso — detectado y corregido
con copia directa), primera corrida normativa con ratchet introvert rojo, y
un `ruff format` invocado por error sobre la feature (Gherkin, no Python;
sin efecto).

## 11. Límites, pendientes y siguiente incremento

Este registro no ratifica A12 ni otros IDs de la matriz; no elige variante
A/B de partición ni amplía su allowlist; no incorpora P03a; no ejecuta
Q-ACCMUT ni campañas; la evidencia de partición/A12 vive bajo `build/tmp/`
(temporal, no publicada como producto). Pendientes que quedan servidos para
decisión humana: A12/A13/A14 y C1/C2 por ID (§7), variante y allowlist de
TEST-007 (con la corrección de §6 como insumo nuevo), E9/bless (23 rutas,
revisar diff protegido), E10/versión, Q-ACCMUT y cadena E8 posterior.

**Siguiente incremento mínimo propuesto**: ninguno de código para C (cerrado
en este alcance); el encargo siguiente natural es la decisión por ID de
A12–A14/C1–C2 con las entradas ya acotadas (A12: oráculo solo posible con
`F_SETPIPE_SZ`, decisión equivalencia-estructural vs hueco-de-oráculo), y
por separado la elección de variante/allowlist de partición con la tabla de
§6. Allowlist del incremento publicado: exactamente
`features/wct-acceptance-evidence-001.feature`,
`tests/acceptance/campaign_steps.py`,
`tests/unit/test_accept_campaign.py` + este registro y las filas afectadas
de la matriz. Criterio de cierre de C (cumplido): G-ACCEPT 0 hallazgos,
focales/colección conciliadas, controles negativos de selector/Then/
artefacto, A/B verdes, fast 7/7 y commit 20+G-META-1(pre-bless) sin ningún
otro rojo.
