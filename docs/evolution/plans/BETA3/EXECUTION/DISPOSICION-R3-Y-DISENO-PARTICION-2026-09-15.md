# Disposición técnica R3 de A12–A14/C1–C2 y diseño de partición TEST-007 (2026-09-15)

Registro sucesor del encargo «cerrar la disposición técnica de A12–A14/C1–C2,
concretar una partición TEST-007 compatible y conciliar el conteo de tests».
Ejecuta sobre la base publicada en `26b1955` (`CIERRE-FRENTE-C-Y-REVISION-PARTICION-2026-09-15.md`).
Este documento **no** ratifica equivalencias ni clasificaciones: las propuestas
quedan servidas para decisión humana. No acredita AC1, no cierra beta.3, no
bendice, no actualiza manifiestos, no hace merge, bump, lock, tag ni release,
no ejecuta Q-ACCMUT, mutmut ni la campaña de los 928 IDs (sin ejecución y sin
veredicto). No implementa la partición: el experimento vive en copia aislada
bajo `build/tmp/` y no se publica como producto.

## 1. Identidades y preflight

- Worktree `build/tmp/beta3-ac1-r2-integration`, rama
  `codex/beta3-ac1-r2-integration`. HEAD de partida `26b1955` (resuelto:
  `26b1955234422908ad032828e508630515b7a0d2`) = `headRefOid` de la PR #53
  (OPEN) = `origin/codex/beta3-ac1-r2-integration` tras `git fetch`: **sin
  avances remotos posteriores**, no hay impacto que congelar.
- Índice limpio al iniciar; único untracked el documento ajeno
  `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md`, conservado fuera del
  incremento (no stageado, no copiado).
- Runtime: `.venv` del worktree (Python 3.13.14, pytest 9.1.1), invocado con
  `UV_NO_SYNC=1 uv run` o por ruta; nada instalado ni sincronizado.
- Inventario sellado r3 verificado:
  `build/tmp/ac1-r2-qualification/evidence/mutation-code-lot-r3-survivor-diffs.log`
  sha256 `51d99c9bdb45679dbed1300f2959bfb96ee27f0178cb5d48a669bf634c204b21`
  (coincide con el anclado en matriz y plan). Fuente vigente
  `tools/wct/accept/process.py` sha256
  `84b9340fd16b424a2d778e512166c4419c048001588665a313dcdf9f5d263ef7`
  (coincide con el hash del plan §3). Ningún inventario regenerado, ningún
  `mutmut run`.

## 2. Conciliación de los 686 tests (por identidades y causas)

Corridas comunicadas por la entrega anterior (HEAD `26b1955`): colección 686;
normativa `pytest -q tests/unit tests/integration -m "not property"` →
684 passed; property `pytest -q tests/property` → 1 passed. La diferencia
686 − 684 − 1 = 1 **no es un test perdido**: es un tercero con ámbito propio.

Colección completa por directorio (re-medida en `26b1955`; log de la entrega en
`build/tmp/disposicion-r3/verificacion/01-coleccion.txt`):

| Ámbito | Tests | Corrida que lo ejecuta | Resultado comunicado |
|---|---|---|---|
| `tests/unit` | 674 | normativa (por ruta) | dentro de los 684 |
| `tests/integration` | 10 | normativa (por ruta) | dentro de los 684 |
| `tests/property` | 1 (`test_reservation_conserves_units_when_quantity_is_available`) | property (por ruta) | 1 passed |
| `tests/acceptance/generated` | 1 (`test_001_reserve_available_units`, binding generado de `features/example.feature`) | **ninguna de las dos** | no ejecutada en esa entrega |

684 (normativa) + 1 (property) + 1 (aceptación generada) = **686**. La
identidad restante es
`tests/acceptance/generated/test_acceptance.py::test_001_reserve_available_units`,
fuera del alcance de ambas corridas por ruta. Además, el resumen de la
normativa no lista deselects: no hay tests marcados `property` dentro de
unit/integration. Sin pérdida; cifras históricas conservadas con su
procedencia. (En el incremento de esta entrega la colección pasa a 688 por las
dos regresiones nuevas de §5: 676 unit + 10 integration + 1 property +
1 acceptance.)

## 3. Identidad de A12–A14/C1–C2 (antes de clasificar)

Todos los IDs resueltos contra el inventario sellado (diffs extractados de las
líneas citadas del log r3, hash verificado en §1). Prefijo completo:
`tools.wct.accept.process.`. Runtime histórico r3: `sh-p01-CND-80B8`,
Python 3.13.14, mutmut 3.7.0. La corrección de 2026-09-15 de la matriz (rige el
diff autoritativo, no la adenda antigua) queda confirmada por el sello.

| Etiqueta | ID completo | Diff real (sellado) | Evidencia existente | Estado pendiente exacto |
|---|---|---|---|---|
| A12 | `process.x__read__mutmut_12` | `min(65536, remaining+1)` → `min(65537, remaining+1)` en `_read` L23 | Sonda oleada (rc=0); DICTAMEN del cierre C §7; sonda nueva §4 de este registro | Ratificación por decidir (B propuesta, precondiciones §4) |
| A13 | `process.x__read__mutmut_14` | `remaining + 1` → `remaining + 2` en la misma línea | Sonda oleada (rc=0, remaining 0/1/65534); análisis deductivo nuevo §4.3 | Ratificación por decidir (B propuesta, sin precondición de capacidad) |
| A14 | `process.x__read__mutmut_17` | `continue` → `break` en EOF de un stream (`_read` L26) | Sonda oleada rc=1 (late-data ausente); **regresión permanente nueva §5** | Defecto demostrado bajo contrato vigente (A propuesta); falta ratificación humana del dictamen |
| C1a | `process.x__execute__mutmut_28` | `process.wait(timeout=1)` → `wait(timeout=None)` en `_execute` L67 | Sonda oleada rc=0 | Clasificación por decidir (B deductiva propuesta, §4.4) |
| C1b | `process.x__execute__mutmut_29` | `wait(timeout=1)` → `wait(timeout=2)` ídem | Sonda oleada rc=0 | Ídem |
| C1c | `process.x__terminate__mutmut_6` | `wait(timeout=1)` → `wait(timeout=None)` en `_terminate` L18 | Sonda oleada rc=1 (3600 s simulados sin cota); **regresión permanente nueva §5** | Defecto demostrado bajo contrato de terminación acotada (A propuesta); falta ratificación |
| C1d | `process.x__terminate__mutmut_7` | `wait(timeout=1)` → `wait(timeout=2)` ídem | Sonda oleada rc=0 (1,5 s simulados < 2) | C: sin violación de contrato; decidir si `wait=1 s` exacto es contrato operativo |
| C2 | `process.x__observe__mutmut_33` | `time.monotonic() >= deadline` → `>` en `_observe` L41 | Sonda oleada rc=1 (lee tras el plazo y devuelve `""` en `_read`) | Divergencia demostrada (bytes persistidos en la frontera); la aclaración contractual «frontera inclusiva del deadline» sigue sin aprobar → decidir contrato y luego clasificar |

No se infirió ningún ID por similitud de nombres; las etiquetas agrupan
exactamente los IDs listados (C1 son CUATRO IDs, no uno).

## 4. A12: la falsa disyuntiva eliminada

El encargo pedía no asumir que A12 solo puede decidirse ampliando un pipe con
`F_SETPIPE_SZ`. El análisis por capas (tamaño pedido vs leído vs persistido,
estado observable posterior, entradas admitidas por el contrato del
transporte) muestra que la decisión tiene dos ramas, NINGUNA de las cuales
exige `F_SETPIPE_SZ` para sostenerse:

**4.1 Mecánica real.** `_read` llama `os.read(key.fd, min(N, remaining+1))`
cruda sobre el fd del pipe de `Popen` (una syscall, sin buffer de stream).
Original pide 65536 y variante 65537 solo cuando `remaining ≥ 65536`; con
`remaining ≤ 65535` ambas piden `remaining+1` (idénticas). `read(2)` sirve
siempre como lectura corta `min(count, disponible)`.

**4.2 Equivalencia deductiva bajo las entradas admitidas (propuesta B).** El
transporte admite pipes creados por `Popen(stdout/stderr=PIPE)`. En el runtime
adjudicado su capacidad por defecto es 65536 (medida `F_GETPIPE_SZ`; default
configurable del host, no garantía POSIX). Como `disponible ≤ capacidad` en
cada lectura, la variante nunca recibe más que 65536: el chunk es idéntico al
del original en TODO estado alcanzable. La no-divergencia es deductiva
(invariante de capacidad + semántica de `read(2)`), no muestral. Precondiciones
explícitas: (i) runtime Linux con capacidad por defecto ≤ 65536; (ii) lectura
cruda `os.read` (no `BufferedReader`, contraejemplo refutado en el DICTAMEN del
cierre C); (iii) hijos del producto que no amplían su propio pipe
(`grep -rn F_SETPIPE_SZ tools/ src/` → 0 usos).

**4.3 Frontera con capacidad ampliada: hay oráculo público real.** Bajo
capacidad ≥ 65537 (alcanzable sin privilegios con `F_SETPIPE_SZ` por-pipe
hasta 1 MiB — un hijo puede agrandar su propio stdout), existe un estado donde
el mutante diverge con efecto PÚBLICO, no solo granularidad de syscalls:
`remaining == 65536` (acumulados 983040) y ≥65537 bytes simultáneos en un fd.
Original: lee 65536, `remaining→0`, sin señal. Variante: lee 65537,
`chunk[:65536]` persiste lo mismo PERO `remaining→−1` → retorna
**"output limit exceeded"** → `_terminate` (SIGKILL), log truncado, veredicto
del límite falsado. Sonda demostrada (log sellado
`build/tmp/disposicion-r3/a12-sonda/sonda-salida.log`): S1 (capacidad por
defecto, 65536 disponibles): original y mutante idénticos `{'', 65536}`;
S2 (capacidad 131072, 65537 disponibles): original `{'', 65536}` vs mutante
`{'output limit exceeded', 65536}`. La sonda usa copias byte a byte del fuente
sellado (hash del original = `84b9340f…`) con UN diff sellado aplicado por
mutante, runtime del worktree, sin cambios de configuración global ni
privilegios, y el oráculo NO es el argumento de `read()` sino motivo retornado
+ bytes persistidos. S3 confirma A13 (§4.3): m14 idéntico al original en
remaining 10 con 9/11/12 disponibles.

**4.4 Consecuencias de clasificación (propuestas, no ratificadas).**
- **A12 → B** bajo las precondiciones de §4.2 (equivalencia total en este
  host/runtime con capacidad por defecto). La frontera §4.3 queda documentada
  como invalidante: si el contrato del transporte amplía entradas (hijos que
  redimensionen pipes), A12 pasa a A con oráculo público ya demostrado.
  Decisión humana: ratificar B con esas precondiciones, o tratar la frontera
  como hueco contractual del producto (el hijo puede agrandar su pipe hoy sin
  privilegios y el producto no lo detecta como exceso real).
- **A13 → B sin precondición de capacidad**: deductivo. Con `remaining ≤
  65534` el pedido es `remaining+1` vs `remaining+2`; en cuanto `disponible >
  remaining` AMBOS retornan el mismo motivo de exceso y persisten el mismo
  `chunk[:remaining]`; con `disponible ≤ remaining` ambos leen exactamente
  `disponible`. La trayectoria posterior de `remaining` y los bytes persistidos
  coinciden en todo caso; el residuo (bytes de más consumidos de la cola en la
  ronda ya señalada) no es observable (el hijo se termina y los streams se
  cierran). Sonda S3 lo confirma en los tres puntos de frontera.
- **C1a/C1b (`execute__28/29`) → B deductiva**: en todos los caminos
  alcanzables de `_execute`, el `wait(timeout=…)` final opera sobre un hijo YA
  terminado o YA recolectado por `_terminate` (si `reason` es verdadera,
  `_terminate` recolectó o su excepción aborta antes del `return`; el bucle de
  `_observe` solo sale con `poll() is not None` y selector vacío). Sobre hijo
  muerto, `wait(None)`, `wait(2)` y `wait(1)` retornan idénticos e inmediatos.
  Sin sonda adicional: la equivalencia es por alcanzabilidad de estados, no por
  ausencia de contraejemplo.
- **C1d (`terminate__7`) → C**: `wait(2)` acota igual que `wait(1)`; sin
  contrato del valor exacto no hay violación demostrable. Decide el humano si
  «wait=1 s» es contrato operativo (la regresión nueva de §5 pasa verde bajo
  este mutante, coherente con la no-imposición del valor exacto).
- **C2 → D con dictamen servido**: la divergencia en la frontera del deadline
  está demostrada (oleada, rc=1) y afecta bytes persistidos, pero la
  clasificación exige aprobar antes la aclaración contractual «frontera
  inclusiva: el timeout gana antes de otra lectura». Aprobada esa aclaración,
  C2 es A con regresión convertible.

## 5. Regresiones permanentes nuevas (allowlist respetada)

Solo `tests/unit/test_accept_campaign.py` (permitida). Dos pruebas, anexas al
final del archivo; ningún test preexistente modificado; sin cambio de producto;
dobles sobre los puntos de sustitución existentes
(`process_transport.subprocess/selectors/time`, patrón T5).

1. `test_eof_on_one_stream_still_captures_sibling_output_in_same_round`
   (**A14 / `x__read__mutmut_17`**). Escenario: pipes reales; EOF en stdout y
   bytes pendientes en stderr dentro de la MISMA selección; reloj controlado
   que llega al deadline tras la primera ronda; selector real con orden de
   ronda fijado al de registro (`_OrderedSelector`, mismo ready-set). Oráculo
   público: `stderr.log == b"late-data\n"`, motivo `timeout`, hijo recolectado
   de verdad. Condiciones §6: contrato aprobado (captura parcial, CONTRATO-AC1);
   original verde; la variante falla por la causa contractual prevista
   (`stderr.log == b""` — captura perdida por el `break`); estado realizable
   (el de la sonda de la oleada, ahora determinista).
2. `test_terminate_gives_up_on_slow_reap_within_bounded_budget`
   (**C1c / `x__terminate__mutmut_6`**). Escenario: hijo propio real para
   `killpg` seguro; reap modelado como muy tardío (3600 s simulados, estado D)
   con reloj controlado; `wait(timeout)` del doble cede con `TimeoutExpired`
   sin recolectar, `wait(None)` bloquea hasta el reap tardío — semántica real
   de `Popen.wait`. Oráculo público: motivo `process error:`, `exit is None`,
   `duration ≤ 5.0` simulados; el hijo real queda recolectado. Condiciones §6:
   contrato aprobado (terminación acotada y recolección); original verde; la
   variante falla porque la espera sin cota retorna normal tras 3600 s
   simulados (`reason == "timeout"`, `duration 3600.2`); estado realizable
   (hijo no recolectable dentro del plazo, p. ej. estado D).

Matriz rojo/verde contra mutantes REALES (copias aisladas de HEAD con el diff
sellado aplicado; log `build/tmp/disposicion-r3/regresion/MATRIZ-ROJO-VERDE.md`):

| Prueba | Original (`26b1955`) | Copia `_17` | Copia `_6` |
|---|---|---|---|
| eof_on_one_stream… | VERDE | **ROJO** `stderr.log b'' != b'late-data\n'` | VERDE (independencia) |
| terminate_gives_up… | VERDE | VERDE (independencia) | **ROJO** `reason 'timeout' != 'process error:'` (y `duration 3600.2` > cota) |

Sin errores de colección, setup, launcher ni infraestructura en ningún rojo;
los kills son por aserción de estado público. Los tests NO matan
`terminate__7` (verde bajo él, coherente con C1d: no se impone el valor
exacto 1 s) ni a `execute__28/29` (fuera de su camino; B deductiva).

## 6. TEST-007: partición compatible diseñada y MEDIDA (sin implementar)

Diseño completo medido en sandbox aislado
`build/tmp/disposicion-r3/particion2/` (extraído de HEAD por `git archive`;
`tests/` intocado byte a byte; nada volcado al worktree). Resumen sellado:
`particion2/RESUMEN-EXPERIMENTO.md`. Presupuesto: ~118 s de 180 s (incluye
corridas inválidas y el baseline).

**Restricción rectora (de la tabla de patches del cierre C):** conservar en la
FACHADA `tools/wct/gate/runner.py` los consumidores de los tres parches P2:
`gate_coverage_diff` + `remote_base`, `gate_mutation_sites` + `scan_mutations`,
y `run_tier` leyendo el global `REGISTRY` (compuesto allí). Los parches P1
(`runner.shutil.which`/`runner.subprocess.run`) requieren que la fachada
conserve `import shutil`/`import subprocess` para que la RUTA del parche
resuelva: la interceptación sobrevive al traslado de funciones porque muta el
módulo stdlib compartido (demostrado). Además, las tres entradas del registro
que declaran gates residentes en la fachada (`G-META-2`, `G-MUT-SITES`,
`G-COV-DIFF`) se componen en la fachada para evitar que los submódulos
importen hacia arriba (cero ciclos).

**Mapa función/dato → destino y responsabilidad (17 archivos resultantes):**

| Módulo destino | Contenido (funciones y datos) | Sitios medidos | Responsabilidad |
|---|---|---|---|
| `gate/runner.py` (fachada) | `Gate`, `gate_meta_rules`, `MANIFEST_DIAGNOSTICS`, `gate_coverage_diff`(+`remote_base`), `gate_mutation_sites`(+`scan_mutations`), `run_tier`; compone `REGISTRY` = static+process+derived y las 3 entradas propias; re-exporta todo lo movido | **75** | Registro, tiers y los gates que los tests parchean por nombre |
| `gate/runner_support.py` | `dynamic`, `external`, `alias` | 23 | Trampolines de construcción de entradas |
| `gate/runner_secrets.py` | `SECRET_PATHS`, `_audited_secrets`, `gate_secrets` | 47 | G-SECRET |
| `gate/runner_audit.py` | `gate_audit` | 37 | G-AUDIT |
| `gate/runner_docstrings.py` | `gate_docstrings` | 19 | G-DOC |
| `gate/registry_static.py` | Mitad estática del literal `REGISTRY` (menos G-META-2/G-MUT-SITES) | 96 | Entradas de analizadores puros y configuración |
| `gate/registry_process.py` | Mitad de proceso (menos G-COV-DIFF) | 77 | Entradas de procesos externos y artefactos |
| `gate/registry_derived.py` | `derived(base)` con las 8 entradas del `update` (alias/compuestos, `REGISTRY[...]`→`base[...]`) | 25 | Derivadas sin importar la fachada |
| `gate/tier_map.py` | `_COMMIT_GATES`, `TIERS` | 52 | Mapa de tiers (mismos objetos; `run_tier` los lee desde la fachada) |
| `gate/checks.py` (fachada) | Re-exporta los tres grupos | 1 | Fachada P3 (imports de tests/runner intactos) |
| `gate/checks_debt.py` | `_result`, `gate_meta_integrity`, `coverage_total_command`, `_declared`, `crap_command`, `coverage_diff_command`, `dead_code_command`, `gate_rules_drift`, `gate_suppressions`, `gate_debt`, `COVERAGE_TOTAL_BASELINE` | 92 | Comandos de deuda y metas |
| `gate/checks_quality.py` | `XENON_FLAGS/KEYS`, `cognitive_command`, `gate_cognitive`, `gate_wire`, `gate_lcom`, `gate_dry_tpl` | 79 | Complejidad y calidad estructural |
| `gate/checks_scanners.py` | `gate_archmetrics`, `gate_dry`, `gate_introvert`, `gate_accept`, `gate_size` | 89 | Analizadores |
| `selftest/fixtures_tools.py` (fachada) | `Builder`, `BUILDERS` + re-exports | 14 | Punto público de builders (tests lo importan) |
| `selftest/fixtures_governance.py` | `MUTMUT_PYPROJECT`, `VULTURE_MIN_CONFIDENCE`, `IMPORT_LINTER`, `mutmut_pyproject`, `_plant`, `_vulture_governance`, `_arch_tree`, `_aws_secret_value`, `_private_key_block`, `f1_b` | 57 | Fixtures de gobernanza plantada |
| `selftest/fixtures_git.py` | `COVERAGE_DIFF_MIN`, `_git_track`, `_git_base`, `f11_a`, `f11_b` | 48 | Fixtures de raíces Git |
| `selftest/fixtures_adversarial.py` | `SEMGREP_RULES`, `_ORM_TYPES_REGEX`, `_CREDENTIAL_NAME_REGEX`, `DEPS_PYPROJECT`, `SECRET_PATHS`, `f6_a`, `f9_a`, `f10_a/b`, `f12_a/b`, `f2_a`, `_mutation_adversary`, `F2_BILLING_ADVERSARY`, `F5_CLAMP_ADVERSARY`, `f4_b` | 75 | Fixtures adversariales |

Todos los sitios son MEDIDOS con `tools.wct.mutate.engine.mutation_sites` sobre
los archivos generados (no estimados); incluye datos y nivel de módulo. Los 17
cumplen ≤100. Reequilibrio aplicado frente a la propuesta de la oleada:
`gate_cognitive` pasa a `checks_quality` (scanners medía 101) y los datos van
con su consumidor (p. ej. `XENON_*` con `cognitive_command`;
`SEMGREP_RULES`/`SECRET_PATHS` con `f9_a`/`f12_*`).

**Verificación del experimento:** suite `tests/unit` del sandbox: 642 passed +
28 skipped, IDÉNTICA al baseline HEAD medido en copia aparte (mismos 4 fallos
ambientales por herramientas ausentes sin PATH de venv: detect-secrets,
semgrep). Ficheros sensibles a parches (test_gate_preflight,
test_gate_config_wiring, test_mutation_gate): 20 passed sin tocar un test.
Controles discriminantes con falsos que REGISTRAN: P1 sobre función MOVIDA
(`gate_secrets`→`runner_secrets`): INTERCEPTA; P2 `remote_base`: INTERCEPTA;
P2′ `scan_mutations`: INTERCEPTA; P2″ `REGISTRY`: acreditado por
`test_gate_preflight` (verde). Identidad de estructuras: las 36 entradas
literales del `REGISTRY` compuesto son LOS MISMOS objetos de las mitades
(`is`-check OK); las 8 derivadas se construyen una única vez por composición
(instancia única en el proceso; cada función de construcción vive solo en
`registry_derived.py`); `TIERS` ídem; `REGISTRY` no se duplica (cada entrada
literal existe una vez; total 47 = 22 estáticas + 14 de proceso + 8 derivadas
+ 3 compuestas en fachada). Grafo de dependencias: 0 ciclos; la fachada
importa a los submódulos; ningún submódulo importa la fachada. Imports
públicos: los re-exports de fachada mantienen `from tools.wct.gate.runner
import REGISTRY/TIERS/run_tier/gate_*` y los de checks/fixtures_tools
(exactamente los que hoy usan tests y CLI).

**Allowlist exacta de una futura implementación** (a ratificar antes de
editar): `tools/wct/gate/runner.py`, `tools/wct/gate/checks.py`,
`tools/wct/selftest/fixtures_tools.py` y los NUEVOS
`tools/wct/gate/{runner_support,runner_secrets,runner_audit,runner_docstrings,registry_static,registry_process,registry_derived,tier_map}.py`,
`tools/wct/gate/{checks_debt,checks_quality,checks_scanners}.py`,
`tools/wct/selftest/{fixtures_governance,fixtures_git,fixtures_adversarial}.py`.
Cero archivos de test: ningún parche migrado (P2 se preserva por diseño de
fachada; P1 por imports retenidos). En la implementación real, los imports
retaining solo para parche (`shutil`/`subprocess` en la fachada si algún uso
local desaparece) deberán llevar `# noqa: F401` con justificación (STYLE-008).

**Impacto en identidades y evidencias históricas:** el manifiesto de mutación
indexa `archivo::qualname`; al mover `_declared` (→`checks_debt.py`) y `f9_a`
(→`fixtures_adversarial.py`) cambian sus claves: la evidencia de los 11 IDs de
`_declared` y los 20 de `f9_a` (fase E) y la preexistencia de los 928 NO se
transfiere automáticamente y exigirá re-ancle/re-verificación por identidad.
`PX-REG` (frente B) queda anclado a `runner.py`, que conserva `REGISTRY`,
`run_tier` y los gates parcheados, pero deberá reejecutarse sobre el árbol
particionado. Las ratificaciones GS-1/2/3 (semgrep*) no dependen de estos
archivos; el wiring de `G-SAST-SEMGREP` se re-verifica con la suite.

**Orden mínimo de integración (propuesto):** (1) Fase de datos y soporte:
`runner_support`, `runner_secrets`, `runner_audit`, `runner_docstrings`,
`tier_map`, `registry_static`, `registry_process`, `registry_derived` + fachada
`runner.py` (un solo incremento, es donde viven los parches); verificación:
suite de los 21 archivos consumidores de runner + PX-REG + discriminantes con
falsos que registran. (2) Fase checks: `checks_debt`, `checks_quality`,
`checks_scanners` + fachada `checks.py`; verificación: gates ligeros y
`G-MUT-SITES` sobre el árbol nuevo. (3) Fase fixtures:
`fixtures_governance`, `fixtures_git`, `fixtures_adversarial` + fachada
`fixtures_tools.py`; verificación: tests de redteam/selftest. Cada fase con
colección, normativa y fast; tier commit al cierre. Si se aprueba, la
implementación es su propio encargo con TDD de traslado (fingerprints,
imports, PX-REG re-medido) — este registro NO la autoriza.

**Obstáculo encontrado y resuelto en el diseño** (por eso el experimento
completo valía la pena): las entradas `G-META-2`/`G-MUT-SITES`/`G-COV-DIFF`
del literal `REGISTRY` referencian gates que la compatibilidad de parches
obliga a dejar en la fachada; extraerlas a submódulos crearía un ciclo. La
composición de esas tres entradas en la fachada lo resuelve sin duplicar nada
y sin tocar tests.

## 7. Verificación del incremento publicado (worktree, runtime `.venv`)

| Verificación | Resultado |
|---|---|
| `git diff --check` | Limpio |
| Colección completa | **688** = 676 unit + 10 integration + 1 property + 1 acceptance (conciliación exacta: 686 normativa-ámbito + 1 property + 1 acceptance) |
| Focales A+B+C (`test_accept_campaign.py` + `test_sast_targets.py`, PATH venv) | **106 passed** (52 + 54), 11,9 s |
| Normativa (`tests/unit tests/integration -m "not property"`) | **686 passed** (684 + 2 nuevas), 131 s |
| Property (`tests/property`) | **1 passed** |
| G-ACCEPT | **PASS, 0 hallazgos** |
| Ratchets (`wct ratchet check`) | «Todos los ratchets se mantienen», exit 0 |
| Introvertidos (`wct introvert`) | 415 extroverted / 5 conditional / 5 questionable / 8 cloistered; **0 introverted**; exit 0 |
| Fast (`wct gate --tier fast`) | **7/7 PASS**, exit 0 |
| Tier commit (`wct gate --tier commit`) | **20 PASS + G-META-1 FAIL** (148,8 s). G-TEST, G-INTROVERT, G-MUT-SITES, G-ACCEPT verdes; el único rojo es el drift pre-bless conocido |
| Integridad (`wct integrity check`) | exit 1; drift **23 rutas = 7 modificadas + 16 nuevas**, idéntico al medido en el cierre C: **ninguna ruta nueva de este incremento** (solo `tests/unit/test_accept_campaign.py`, no protegida) |

G-META-1 rojo pre-bless por el drift acumulado, esperado y no nuevo; ningún
otro fallo. Las focales no se presentan como ejecución de un gate global.

## 8. Presupuestos reales

| Frente | Tope | Consumo real |
|---|---|---|
| Sondas y controles (sonda A12/A13 + matriz rojo/verde + copias mutantes), incluidos intentos inválidos | 600 s | ~6 s (sonda 3×0,1 s; 6 corridas de un test ~0,3 s; preparación de copias ~1 s); incluye lo reejecutado por el verifier (~5,9 s) |
| Experimento de partición (sandbox completo, incl. baseline comparativo, corridas inválidas y discriminantes) | 180 s | ~118 s, desglosado: 4 corridas de la suite unitaria del sandbox de 25,2/27,2/26,5/26,2 s (incluida la inválida y el baseline comparativo), corrida de los 3 archivos sensibles a parches 0,7 s, discriminantes ~1 s, mediciones de sitios de 17 archivos ~9 s, cirugía/compilaciones ~2 s |

Baterías ordinarias del incremento (colección, focales, normativa 131 s,
property, gates: fast 0,9 s, commit 148,8 s) se contabilizan aparte, conforme
a la convención de los registros previos.

## 9. Dictamen del verifier independiente

Agente distinto del autor, sin escritura sobre producto/tests; informe y
evidencia propios en `build/tmp/disposicion-r3/verifier/VEREDICTO.md`.
**Dictamen: APROBAR CON RESERVAS** (R1–R5, no bloqueantes). Reejecutó: sellos
sha256 del inventario y de `process.py`; los 7 IDs contra el log sellado;
matriz rojo/verde completa (original 2 passed; mut17 → eof ROJO por
`stderr.log` + terminate VERDE; mut6 → terminate ROJO por motivo + eof VERDE;
copias = HEAD + un diff sellado, tests byte-idénticos); sonda A12/A13
reproducida con salidas idénticas; colección 688 = 676+10+1+1; focales
52 passed; partición: 17 archivos medidos ≤100 (coinciden 1:1), `REGISTRY` 47
con literales idénticas por `is`, P1/P2 INTERCEPTAN, sandbox sin `.git` y
`tests/` byte-idéntico a HEAD; 0 ciclos; el candidato solo toca los 3 archivos
declarados (+202/−0 en tests). Reservas y su atención: R1 (referencia de log
inexistente → corregida a `01-coleccion.txt`); R2 (aritmética de derivadas:
22+14+8+3=47 → corregida); R3 (identidad `is` limitada a las 36 literales;
derivadas de instancia única → reword aplicado); R4 (desglose del presupuesto
de partición → añadido en §8); R5 (§9 estaba pre-redactada por el autor →
reescrita citando el informe del verifier). No ratifica por ausencia de
contraejemplo.

## 10. Pendientes humanos servidos y próximo incremento mínimo

Decisiones que este registro deja listas (ninguna ratificada automáticamente):
1. **A12**: ratificar B bajo precondiciones §4.2, o declarar la frontera §4.3
   hueco contractual del transporte y abrir decisión de producto.
2. **A13**: ratificar B (equivalencia deductiva sin precondición de capacidad).
3. **A14** y **C1c**: ratificar los dictámenes A (defecto con regresión
   permanente y sensibilidad demostrada contra el mutante real).
4. **C1a/C1b**: ratificar B deductiva por alcanzabilidad; decidir si
   `wait=1 s` exacto es contrato operativo (afecta a C1d).
5. **C2**: aprobar (o rechazar) la aclaración contractual de la frontera
   inclusiva del deadline; aprobada, convertir la sonda en regresión.
6. **TEST-007**: elegir la partición de §6 y ratificar su allowlist antes de
   cualquier edición; sin excepción concedida.

**Próximo incremento mínimo propuesto**: ninguno de código para R3; el
natural es la decisión humana de los puntos 1–6 y, por separado, la
autorización de la implementación de la partición por fases (§6). Allowlist
del incremento publicado en ESTE registro: `tests/unit/test_accept_campaign.py`
+ este documento + las filas afectadas de la matriz.

## 11. Límites

No ratifica equivalencias ni clasificaciones; no ejecuta Q-ACCMUT, mutmut ni
la campaña de los 928 (sin veredicto); no implementa ni publica la partición
(sandbox temporal bajo `build/tmp/`); no incorpora P03a; no bendice, no hace
merge, bump, lock, tag ni release; no declara cierre integral AC1/beta.3. La
conversión de la sonda C2 en regresión queda condicionada a la aclaración
contractual pendiente. La evidencia de sondas vive bajo `build/tmp/`
(temporal, no publicada como producto).
