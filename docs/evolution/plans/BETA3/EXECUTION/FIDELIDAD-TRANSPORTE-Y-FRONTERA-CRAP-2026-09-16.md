# Fidelidad del transporte y frontera CRAP — AC1 / PR #53 (2026-09-16)

Registro sucesor único del encargo «corregir la fidelidad del test de streams
ausentes, revisar la evidencia afectada y resolver la frontera de las 66
funciones CRAP; DRY solo si las puertas anteriores quedan conformes». Código
de este incremento: commit `ebf41df` sobre `907fd74`, que a su vez contiene la
reparación `aed2acf`. Base de PR #53: `origin/main` =
`932c835ac0eeb75010ec7a1071315b1c51f78eb6`. Este registro **no** declara PASS
de G-MUT, **no** acredita cierre integral AC1 ni beta.3, **no** ratifica
equivalencias nuevas, **no** modifica producto, gobernanza, umbrales,
baselines, manifests, lock ni versión, y **no** bendice, no hace merge, bump,
tag ni release. El informe histórico `REPARACION-CRAP-Y-RECALIFICACION-2026-09-16.md`
se conserva sellado: sus cifras 87/87 y 90.00% describen el candidato con el
test hoy retirado y aquí se registran como evidencia histórica con su
limitación, no como resultado vigente. El documento ajeno
`PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md` permaneció intacto, sin
seguimiento y fuera del incremento (sha256 `dedda9f3f057e9a02bd40740404c2c25773ed21b502798360ec5146a0fd1d430`).
La evidencia bajo `build/tmp/` es temporal y no es custodia durable.

## 1. Preflight e identidades

- Worktree `build/tmp/beta3-ac1-r2-integration`, rama
  `codex/beta3-ac1-r2-integration`. HEAD de partida
  `907fd749e2e5b22384b2cbbfcf614fa35551aee6` = `origin` = `headRefOid` de la
  PR #53 (OPEN), sin avances remotos posteriores (`git ls-remote`). Índice
  vacío salvo el untracked ajeno citado.
- Copias aisladas con raíz Git propia bajo
  `build/tmp/fidelidad-transporte-20260916/`: `candidate` (907fd74 + retirada
  del test), `mutation` (misma base + receta mutmut privada) y `base`
  (`origin/main`). Runtime acreditado: `.venv` del worktree, Python 3.13.14,
  pytest 9.1.1, mutmut 3.7.0, coverage 7.15.4, diff-cover 10.5.1, crap4py
  0.1.1, jscpd 5.0.16; imports resueltos con `PYTHONPATH` de la copia
  (`$PWD:$PWD/src`) para que `src/example` no se atribuya al worktree
  compartido. Nada instalado ni sincronizado; runtime no modificado.
- CI remoto al corte: corridas `35148504901`, `35148627039`, `35148769361`,
  `35148889100` y `35149027003` (907fd74) terminan FAILURE en
  `wct integrity check` por el drift pre-bless; los pasos posteriores no
  corren. No se heredan resultados de CI.

## 2. Hallazgo del test y resolución (decisión B)

El test retirado
`tests/unit/test_accept_campaign.py::test_process_with_unavailable_streams_still_returns_the_child_result`
(construido en `aed2acf`) presentaba tres defectos de fidelidad:
construía un doble de `Popen` con `stdout=None`/`stderr=None` aunque el SUT
solicita ambos con `PIPE`; sustituía el selector por uno que acepta registros
sin mantenerlos (`register` no-op y `get_map()` vacío) para saltar la
observación; y afirmaba `double.wait_timeouts == [1]`, un detalle de
implementación sin obligación contractual.

Inspección del productor (`tools/wct/accept/process.py`, `subprocess` POSIX
del runtime acreditado), sin asumir que «cerrado» equivale a `None`:

- **Retorno correcto de `Popen`:** en POSIX `self.stdout`/`self.stderr`
  arrancan en `None` (subprocess.py:873-874), se envuelven los pipes
  *antes* del lanzamiento (1021-1037) y cualquier fallo de `_execute_child`
  cierra lo abierto y **re-lanza** (1048-1075); un `Popen` con `PIPE` que
  retorna nunca deja esos atributos en `None`.
- **Streams solicitados con PIPE:** existen siempre en el objeto retornado.
- **Stream cerrado vs. ausente:** un stream cerrado sigue siendo un objeto y
  `close()` es idempotente; la guarda protege el caso `None`, no el cerrado.
- **Fallo de construcción:** `Popen` lanza antes de asignarse a `process`; el
  `finally` de `_execute` no se ejecuta y el propio `Popen` ya limpió.
- **Vías admitidas que alteren los atributos antes del `finally`:** ninguna;
  `_execute`, `_observe`, `_terminate` y `_close_streams` no asignan esos
  atributos. Único consumidor público: `campaign._attempt` → `run_process`.

No existe camino real admitido (A) ni defecto de producto (C). **Decisión B
aplicada:** se retira el test inválido como evidencia del flujo público y la
rama defensiva queda pendiente de disposición (§6, reserva R1). El diff sobre
`907fd74` es exactamente −50/+1 líneas y el archivo resultante es
byte-idéntico al de `a529adb`
(sha256 `fd7075ac7fbdca5a0dcfef892712a0b57b7f25fc4f1ece8ca43c4d55bd317fd2`),
es decir, se revierte el andamiaje `wait_timeouts` y no se retira ninguna otra
prueba: el conteo de `def test_` vuelve de 33 a 32 y la colección de
690/691 (1 property deselected). ¿Se creó un test sustituto? No: los oráculos
de terminación acotada, recolección, captura y limpieza siguen cubiertos por
`test_transport_timeout_preserves_partial_streams_real_exit_and_reaps`,
`test_failed_observation_reports_reaps_and_closes_live_child`,
`test_transport_reads_pending_output_after_leader_terminates`,
`test_terminate_gives_up_on_slow_reap_within_bounded_budget`,
`test_deadline_boundary_prevents_a_new_read_and_keeps_captured_bytes` y los
demás transportes reales. La aserción `wait_timeouts == [1]` se retira: la
disposición C1 de la matriz declara que «exactamente 1 s interno no está
contratado» y `ACTA… §2.6` lo confirma para `terminate__7`; no se creó
obligación para matar mutantes. Cambio de identidad documentado: una prueba
retirada, ninguna añadida.

## 3. Impacto en el 87/87 de mutación (por ID)

El bruto histórico se conserva intacto: `REPARACION-CRAP §4` declaró 87/87
killed sobre el candidato con el test hoy retirado. Se repitió la campaña
acotada con la misma receta (mutmut 3.7.0, `only_mutate` a
`tools/wct/gate/semgrep_scope.py` y `tools/wct/accept/process.py`, selección
`tests/unit/test_sast_targets.py` + `tests/unit/test_accept_campaign.py` con
el deselect de `test_binding_el_preflight_tolera_git_no_cero_acotado`) sobre
la copia `mutation` corregida:

- Resultado: **85 killed + 2 survived + 0 errors + 0 not_run** (~102 s de
  pared; ejecución de mutantes del orden histórico). Evidencia:
  `evidence/mutmut-results-corrected.txt`, `mutmut-corrected-run.log`.
- IDs afectados por la retirada:
  `tools.wct.accept.process.x__execute__mutmut_28` (`wait(timeout=1)` →
  `None`) y `_29` (→ `2`). Eran los **únicos** que dependían de la aserción
  del timeout exacto: ningún otro test observaba ese argumento (el doble del
  test retirado era el único que lo registraba).
- Disposición: su kill histórico queda **invalidado como sensibilidad de
  test** (artefacto del test infiel, no de un oráculo contractual). Ambos
  están ya dispositionados en el ledger como **equivalencia deductiva
  ratificada** (MATRIZ §C registro final; `ACTA… §4`): el `wait` final de
  `_execute` solo opera sobre hijo terminado o recolectado en todos los
  caminos admitidos, por lo que el valor del timeout es inmaterial. Esa
  ratificación estaba anclada a `process.py` `84b9340f…`; se **re-ancla** al
  hash vigente `0a218827…` porque la extracción de `_close_streams` no toca
  la línea del `wait` (reserva R2). No se convierte ningún `survived` en
  `killed` ni se ratifica equivalencia nueva.
- Resto de los 85 IDs: el kill se reproduce sin el test retirado. En
  particular `_close_streams__mutmut_1` (`if stream is not None` → `is None`)
  lo mata evidencia independiente del test retirado: los tests de limpieza
  con streams reales desechan el cierre y fallan por aserción de recurso
  (atribución por lectura + campaña; reserva R3).
- Los 87 IDs conservan su veredicto histórico por capas; la transferencia
  válida al candidato corregido es 85/87 kills y 2/87 supervivientes con
  disposición ya registrada. No se sigue presentando el 87/87 como
  calificación íntegra del árbol corregido.

## 4. Vigencia de Q-ACCMUT

`process.py` cambió respecto del candidato que obtuvo 47/47 (`192c869`):

- Diff exacto `84b9340f16b424a2d778e512166c4419c048001588665a313dcdf9f5d263ef7`
  → `0a218827bb55219569fde1c4c9149894d6bc45173680e4f562b811314c0083e4`:
  extracción pura de `_close_streams` (el bucle de cierre se mueve a un
  helper llamado en el mismo punto del `finally`; sin cambio de orden,
  mensajes ni resolución observable). `campaign.py` `686070cd…` y
  `pytest_receipt.py` `d4f136ae…` no cambian.
- Camino usado por la campaña de aceptación: `wct accept mutate` →
  `campaign.run_mutations` → `_attempt` → `run_process` (esta copia) para el
  baseline y cada mutante; `_close_streams` se ejecuta en cada intento.
- La extracción no altera ningún resultado de transporte y no hay
  interdependencia con la clasificación semántica de recibos; el argumento de
  transferencia se documenta **y** se ejecutó una repetición fresca del mismo
  alcance AC1 sobre el candidato corregido, previa a cualquier declaración de
  vigencia: baseline `pass` (exit 0), **planned=47, killed=47, survived=0,
  errors=0, not_run=0**, todos los rechazos semánticos contractuales
  (`attempt.json` status `mismatch`, exit 1, recibo ligado a los bytes del IR
  mutado, `errors` vacío). Evidencia privada:
  `candidate/build/tmp/wct-accept-ypwdde2w/report.json` sha256 `6b21c7f9…`;
  ~88 s exteriores de 600 s/campaña. Pre/post hashes de feature, bindings,
  generado y `process.py` idénticos (el generado histórico no se sobrescribió).
- Límite: la repetición se ejecutó después de cerrar la mutación de fuentes
  afectada (§3). Si cambia `process.py`, la feature, los bindings, el
  operador o el runtime, la vigencia debe revisarse de nuevo.

## 5. Frontera de las 66 funciones CRAP

Medición fresca suplementaria `crap4py tools/wct --lcov build/coverage/lcov.info
--max-crap 6`: exit 1, **66 violaciones** (los 3 cuerpos reparados por
`aed2acf` ya no aparecen). Clasificación contra la base real de PR #53
(`origin/main` `932c835`) por fingerprint AST de cuerpo (docstring excluido,
nombres conservados); evidencia `evidence/crap-classification-66.{json,txt}`:

| Categoría | N | Detalle |
|---|---:|---|
| `trasladada_mecanicamente` | 9 | cuerpo AST idéntico en `checks.py`/`runner.py` de la base; módulo destino nuevo de la partición TEST-007 |
| `preexistente_sin_cambios` | 57 | 54 en módulos fuera del diff + 3 en `gate/runner.py` tocado con cuerpo idéntico (`gate_meta_rules` 30.0, `run_tier` 7.2, `gate_mutation_sites` 7.0) |
| `modificada` | 0 | — |
| `nueva` | 0 | — |

Los 9 trasladados: `checks_scanners.gate_archmetrics` 30.0,
`runner_audit.gate_audit` 30.0, `checks_scanners.gate_accept` 20.0,
`checks_scanners.gate_introvert` 20.0, `runner_secrets.gate_secrets` 13.1,
`checks_scanners.gate_dry` 12.0, `checks_quality.gate_dry_tpl` 12.0,
`checks_quality.gate_lcom` 12.0, `checks_debt.gate_suppressions` 12.0. La
«anidada» `archmetrics/analyzer._cycles.walk` 6.1 quedó localizada como
preexistente, no como categoría de exclusión.

«Trasladada» no se acepta por sí sola: `evidence/resolution-check.txt`
compara cada nombre global leído por los 9 cuerpos contra el proveedor en la
base y el destino. Los únicos cambios de resolución son de **ruta de
proveedor con implementación idéntica**: `_result` (antes def en
`checks.py`/`runner.py`; ahora importado desde `gate/checks_debt.py` o local) y
`_audited_secrets` (movido de `runner.py` a `runner_secrets.py`); se verificó
que ambos cuerpos son AST-idénticos entre base y destino. El resto de
referencias resuelven al mismo proveedor.

Frontera y obligación aplicable:
- **STYLE-002** («CRAP ≤ 6 en toda función que escribas o modifiques»,
  `governance/rules/30-style.yaml`, verificado por `G-CRAP`) y **ADR-003** +
  `governance/thresholds.yaml crap.changed_max: 6` («6 aplica SIEMPRE al
  código cambiado»). Ninguna de las 66 es cuerpo nuevo o modificado: las 66
  son deuda preexistente o cuerpos mecánicamente trasladados, por lo que no
  hay incumplimiento aplicable al incremento.
- La receta canónica **G-CRAP** (`checks_debt.crap_command`) tiene scope
  registrado `("src",)`; no cubre `tools/wct`. La medición suplementaria es
  evidencia propia, no un gate. No hay baseline de CRAP y este encargo no
  autoriza crearla ni subir umbrales.
- **Caso que requiere decisión normativa:** si un traslado mecánico de archivo
  (mismos bytes de cuerpo, nueva ruta de resolución) activa la obligación
  incremental de STYLE-002, y si ADR-003 («el repo completo usa el umbral de
  su perfil») debe operacionalizarse sobre `tools/wct` con su propio baseline.
  No se concede excepción ni se resuelve por analogía: queda como
  disposición humana explícita. Los 3 cuerpos idénticos en archivo tocado
  (`runner.py`) caen en la misma pregunta.

## 6. Cobertura y CRAP sucesores

Receta canónica G-COV-TOTAL (`pytest --cov --cov-branch
--cov-report=lcov:build/coverage/lcov.info --cov-fail-under 74.5 -q -m "not
property"`), property excluido por marcador, sin LCOV heredado, base
`origin/main`:

| Verificación | Resultado |
|---|---|
| Suite completa | **690 passed, 1 deselected**, exit 0 (352 s) |
| Total combinado coverage.py | **88.00%** ≥ 74.5 (intento previo inválido por `PYTHONPATH` sin `src`: atribuía `src/example` al worktree compartido; descartado) |
| LCOV fresco | sha256 `f9a3d84834d23c96f863cd2a5deae1daa7f688b8196152d313045e32fa016ecd` |
| Diferencial canónico diff-cover | **91%**, 1180 líneas, 97 ausentes, exit 0 |
| Ratchet total | `coverage-total,docstring-coverage`: 2 de 2 exigibles, exit 0 |
| CRAP canónico `src` | exit 0, 9 funciones, máx. 3.0 |
| CRAP focal `process.py` | `_execute` 4.0, `_close_streams` **3.1**, `_observe` 6.0, `_read` 4.0, `run_process` 3.0, `_terminate` 1.0 — todas ≤ 6 |
| CRAP focal `semgrep_scope.py` | máx. 5.4 (`_python_file` 5.0, `_build_values` 5.0, `_python_files` 3.0, `_build_dirs` 2.0) |
| Ramas de líneas Python añadidas | **350 arcos / 314 tomados = 89.71%** |

Caída real y su causa: el único arco cuya toma cambia al retirar el test es la
rama falsa del guard `if stream is not None` de `_close_streams`
(`BRDA:53,0,jump to line 52,0`); `process.py` pasa de 24/24 a 23/24 y el total
de 315/350 (90.00%) a 314/350 (89.71%). No es una regresión de producto: el
candidato **pre-reparación** (`b212f30`) ya estaba en 89.71%; fue el test
infiel el que elevaba el número a 90.00% exacto. En el conjunto añadido hay 36
arcos no tomados (p. ej. `runner_audit` 0/6, `checks_scanners` 2/12); el guard
es el único no tomado **en `process.py`** y el único cuya cobertura cambió.
No se usaron `no cover`, supresiones ni exclusiones para ocultarlo. El gate
canónico aplicable (diff-cover, líneas) pasa con 91%; la cláusula literal de
rama de TEST-004 queda en 89.71% y **no se presenta como PASS**: es la rama
defensiva pendiente de disposición (decisión B), con opciones (a) mantener el
producto sin cambios y registrar la disposición de la rama inalcanzable
(estado actual), (b) retirar el guard como cambio de producto con TDD y
revisión propia —no autorizado aquí—, o (c) cubrirlo con un test unitario
fiel del helper sobre un `Popen` real sin pipes, que cambiaría la clase de
evidencia y requiere decisión normativa. Criterio de continuación evaluado:
reparación fiel, fuentes conformes (85/87 + equivalencias), aceptación vigente
(47/47 fresca), CRAP incremental conforme y residuales con disposición
explícita; la cláusula de rama queda declarada, no silenciada.

## 7. DRY (condicionado, ejecutado)

Interfaz real del CLI, alcance canónico y suplementario, sin reparaciones ni
supresiones:

| Verificación | Resultado |
|---|---|
| G-DRY estructural (`wct dry`, scope `src`) | 3 unidades, **0 candidatos**, exit 0 |
| G-DRY-TPL (`wct dry --normalized`) | **17 candidatos = baseline 17** (`governance/baselines/dry-template-clusters.json`), sin erosión |
| G-DRY-TOK (`jscpd src tools --exit-code 1`) | 0 clones (73 archivos, 8.368 líneas) |
| Suplementario estructural `tools/wct` (92 archivos, 354 unidades) | 19 candidatos: 17 EXTRACT + 2 LEAVE_ALONE; **los 19 pares tienen fingerprint de cuerpo idéntico ya en `origin/main`** (`evidence/dry-base-tools-structural.json`): 0 hallazgos nuevos |

Clasificación: `dry/analyzer.py` y `dry/tpl.py` (pares `visit_*`, `_unit`) son
deuda previa en archivos no tocados; `gate/checks_quality.py`
(`gate_cognitive ~ gate_wire`) es el par trasladado desde `checks.py`; los
pares de `selftest/fixtures_{adversarial,engine,git,governance}.py`
(`f10_a~f10_b`, `f11_a~f11_b`, `f11_a~f1_b`, `f12_a~f12_b`, `_duplicate_pair`,
`_mock_only_test`, `_pure_assertion_test`, ciclos) son **fixtures de caso del
selftest**: matrices de casos pequeños que deben conservarse (principio
MIN-008) y que el guard de matrices no marca. Alcance y propuesta mínima para
un encargo propio, si se decide atacar la deuda: deduplicar los pares de
`dry/analyzer.py`/`dry/tpl.py` con extracción de un `ast.NodeVisitor` común;
los pares de fixtures requieren diseño que preserve la semántica de fixture.
Nada de esto se implementa aquí.

## 8. Verificación, presupuestos y límites

- `git diff --check` limpio (previo y sobre el commit `ebf41df`).
- Colección: **690/691** (1 property deselected, exit 0); identidad retirada
  conciliada (ninguna añadida).
- Focales `tests/unit/test_sast_targets.py tests/unit/test_accept_campaign.py`:
  **109 passed** (16.2 s), rojo/verde del test retirado documentado.
- Property separado: **1 passed, 690 deselected**, exit 0.
- Fast (`wct gate --tier fast`): **7/7 PASS**.
- Commit (`wct gate --tier commit`): **20 PASS / 1 FAIL**; el único rojo es
  **G-META-1** por drift pre-bless **recalculado 37 = 7 modificadas + 30
  nuevas** (sin rutas nuevas de este incremento). G-TEST, G-ACCEPT y
  G-INTROVERT PASS. Un intento previo del tier commit falló 44 pruebas por un
  error **instrumental propio** (PATH con `.venv/bin` relativo: los tests que
  cambian de cwd dejaban de resolver `mutmut`, `interrogate`, etc.); se
  descarta y la corrida válida es la de PATH absoluto.
- Verifier independiente (sin escritura sobre el código revisado): dictamen
  **`APROBAR-FIDELIDAD`** con reservas no bloqueantes — (R1) registrar la
  rama defensiva y la cláusula de rama <90% antes del handoff; (R2) re-anclar
  la equivalencia de `execute_28/29` al hash vigente (hecho en §3); (R3) la
  atribución del kill de `_close_streams` a su test es por lectura + campaña,
  no por aislamiento. Re-ejecutó de forma independiente: métrica de ramas
  314/350, diff-cover 91%, crap focal y suplementario 66, subconjunto mutmut
  (28/29 survived, close_streams killed), sonda de `Popen` POSIX, fingerprints
  AST muestreados y `sha256sum -c` del manifiesto (31/31).
- Presupuestos: A ≈ 120 s de 600 (focal 16 s + campaña corregida 102 s +
  sondas); B ≈ 5 s de 180 (clasificación y resolución; revisión documental
  aparte); cobertura/CRAP ≈ 600 s de 900 acumulados (intento inválido 275 s +
  corrida válida 352 s + herramientas + verifier); Q-ACCMUT ≈ 90 s de 900
  exteriores (1 campaña, ≤2 s/intento); DRY ≈ 20 s de 600.
- Límites: no se ejecutaron tier `full`, G-MUT global, bless/update-manifest,
  merge, bump/lock, tag, release ni declaración de cierre integral AC1/beta.3.
  El drift 37 = 7+30 y G-META-1 siguen siendo el rojo pre-bless conocido. La
  cláusula de rama de TEST-004 (89.71% en líneas añadidas) y la frontera
  normativa de los 12 cuerpos trasladados/en archivo tocado quedan como
  disposiciones humanas explícitas pendientes; nada de esto se presenta como
  puerta aprobada.
- Próxima acción mínima: decisión humana sobre (i) disposición de la rama
  defensiva de `_close_streams` y (ii) frontera de los 12 cuerpos
  trasladados/en archivo tocado; después, la cadena pre-bless ya definida
  (revisión protegida del diff, bless, POST-BLESS, merge, M/V, D3).
