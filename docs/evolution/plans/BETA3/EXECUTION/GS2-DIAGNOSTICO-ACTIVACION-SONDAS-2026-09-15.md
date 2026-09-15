# GS-2 — diagnóstico de activación de sondas y atribución (2026-09-15)

Sucesora de `GS2-CIERRE-ATRIBUCION-REGRESIONES-2026-09-14.md` (que queda
sellada e intacta). Responde H1–H4 del encargo: si las sondas declaradas
discrepantes ejecutaron realmente el mutante; corrección del lanzador en un
expediente sucesor aislado; comparación mínima original/canario/ID discrepante;
reconciliación de los 118 IDs. Sin campaña completa, sin `mutmut run`, sin
regenerar el inventario, sin cambios de producto o tests, sin runner
productivo, sin bless/merge/bump/tag/release. PR #53 permanece en borrador.

Premisa de método: no se parte de que mutmut esté defectuoso, ni de que todos
los kills históricos sean válidos. La distinción central es
**activación acreditada** frente a **exit code**.

## 0. Base, fuentes y custodia

- Worktree de integración `build/tmp/beta3-ac1-r2-integration`, rama
  `codex/beta3-ac1-r2-integration`, HEAD `ddb1b460788e2a3225c320463ced21a751ac3218`
  (local == remoto al momento de esta nota); sin escrituras ajenas al índice
  salvo el untracked ya registrado en la matriz
  (`PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md`, no stageado).
- Runtime: `build/tmp/sh-p01-CND-80B8/.venv` (Python 3.13.14), mutmut 3.7.0.
- Expedientes históricos leídos sin modificar, sellos reverificados:
  `build/tmp/gs2.YfTuE4/` (106/106), `build/tmp/gs2-adenda.67I6HX/` (12/12),
  `build/tmp/gs2-cierre.nDW4ha/` (129/129).
- Expediente sucesor de este diagnóstico: `build/tmp/gs2-diac.yuISyH/`
  (lanzador `sonda-succ.sh`, instrumento temporal `instrumento.py`, sondas,
  evidencia). Sello `gs2-diac.sha256`: 20 miembros, verificación 20/20 fuera de
  los miembros; SHA-256 del manifiesto
  `8ef50b6e04d744460f00d5c0f09586720370b7b2860b082efa1476838e0fa73e`.
- La tabla de reconciliación de §6 se generó con
  `build/tmp/gs2-diac-gen/gen_tabla.py` (SHA-256
  `15a17e2869cd942d238183939552c894db5b0b91c81065b171938eb0cd45004b`) a partir
  de los ledgers sellados; su salida `tabla-118.md` (SHA-256
  `dc7e7471c019a6b85bca41b98873926376d9ac2d7c9e594baeb03962aa669358`) se
  incorpora íntegra en §6.
- **Custodia**: la evidencia bajo `build/tmp/` es local y temporal; la custodia
  durable de estas conclusiones es esta nota versionada. No se afirma lo
  contrario.

## 1. H1 — el lanzador del cierre no activó el mutante: CONFIRMADO

Script y bytes inspeccionados: `build/tmp/gs2-cierre.nDW4ha/sonda-fc.sh`
(SHA-256 `d60289e03bd554225de9e0e37f496dd29f9b08396fc5ee1f5a2e2095a5cc34bc`,
miembro del sello 129/129 del cierre).

- Línea 67: `unset … MUTANT_UNDER_TEST 2>/dev/null` (junto a `PYTEST_PLUGINS`
  y las `WCT_ACCEPT_*`).
- Línea 69: `timeout … "$V/bin/pytest" …` — la variable **no se reasigna al
  comando efectivo**. El trampolín de mutmut, sin variable, ejecuta
  `orig_func` (`mutmut/mutation/trampoline.py:78-88`): la sonda mide el código
  original.
- Los 34 metas de la tanda focal de cierre (`probes/*.meta`) son consistentes
  con esos bytes: mismo juego de campos, incluido `pythonpath_efectivo` (campo
  que solo escribe la revisión final del lanzador) apuntando a
  `checkout/mutants`, y `exit=0` en los 34; sus logs dicen `47 passed` sin
  ningún frame del mutante. El ledger `atribucion-35-ledger.tsv` (34 filas,
  todas `focal`, exit 0) es un artefacto **derivado** de esas corridas (3
  columnas frente a las 4 que emite `sonda-fc.sh:79`); no hay captura cruda de
  4 columnas sellada.
- La única activación de esa tanda es `probes/kills/x__unique_dirs__mutmut_6.focal.log`
  (12:41, `1 failed, 26 passed`, `TypeError`), que corresponde al ID 35,
  ausente del ledger, y sin meta asociada. Su meta de las 12:38 (modo kill,
  13 nodeids, exit 0) carece de `pythonpath_efectivo`, por lo que proviene de
  una revisión inmediatamente anterior del lanzador.
- **Límite declarado**: la identidad histórica exacta de la fila de
  `x__unique_dirs__mutmut_6` de las 12:38 no es demostrable con los bytes
  presentes; no se atribuyen retrospectivamente todos los resultados a los
  bytes actuales. La identidad de los 34 (formato de meta y ventana horaria)
  sí es compatible con el script sellado.

Consecuencia: los 34 exit 0 **no** acreditan supervivencia del mutante ni
contaminación alguna; midieron el original. Escribir el ID en un log no
acredita activación; tampoco lo acredita un exit 0 sin variable.

Preservados con activación explícita (para contraste): `sondas-gs2.sh`
(`MUTANT_UNDER_TEST="$id" pytest …`, SHA-256 `9713d08a…`, sello del original)
y `sonda.sh` de la adenda (`…`, SHA-256 `e78c7555…`, sello de la adenda). La
adenda detectó y declaró su propia desviación (suite completa en vez de tests
asociados); su defecto latente `local` fuera de función (línea 12) no altera
la activación de la línea 17.

## 2. H2 — lectura del runner de mutmut: contaminación in-process RETIRADA

Código instalado inspeccionado:
`…/sh-p01-CND-80B8/.venv/lib/python3.13/site-packages/mutmut/__main__.py`
(3.7.0).

- `set_start_method("fork")` (línea 1349).
- `os.fork()` por mutante (línea 1472); en el hijo
  `os.environ["MUTANT_UNDER_TEST"] = mutant_name` (1475), `runner.run_tests`
  (1490) y `os._exit(result)` (1494); `os._exit(33)` sin tests (1481).
- `PytestRunner.execute_pytest` (438-450) llama `pytest.main` (445) **dentro
  del hijo forkeado**, no en un único proceso persistente.
- `fork` no es `exec`: el hijo hereda el estado importado del padre, pero cada
  mutante forkea del padre común y su estado no alcanza al siguiente. No hay
  contaminación cruzada de estado de proceso entre mutantes.

Por tanto quedan **retiradas** las afirmaciones del informe de cierre
(`GS2-CIERRE…md:33-42`): “pytest in-process … secuencialmente para los 118
mutantes”, “corrupción de despacho del trampolín” y “contaminación de estado
del runner in-process”. Los frames `trampoline.py:84` observados en logs
sellados son el paso por `orig_func` de trampolines anidados bajo un mutante
de **otra** función del mismo módulo; la causa es la mutación:
`x__unique_dirs__mutmut_6` llama `_relative(root, )` sin `raw`
(`semgrep_scope.py:695`) y `x__unique_dirs__mutmut_7` propaga `None`. No es
corrupción de despacho.

## 3. H3 y H4 — contabilidad: CONFIRMADO

- **H3**: 63 + 35 + 16 = 114 es incompleto. La composición real del bruto
  118 = 102 killed + 16 survived es **63 KILLED-EVIDENCIADO histórico + 4
  KILLED-EVIDENCIADO de la adenda (`x__unique_dirs__mutmut_2/3/4/5`) + 34
  sondas del cierre sin activación + 1 pendiente (`x__unique_dirs__mutmut_6`)
  + 16 supervivientes**. El informe de cierre omitió en su narrativa los 4 que
  su propio expediente conserva en `clasificacion-sucesora-39.tsv`.
- **H4**: el ledger del cierre tiene 34 filas; el informe habla de 35. La
  diferencia es exactamente `x__unique_dirs__mutmut_6` (`ids-35-pendientes.txt`
  − ledger34 = {_u6}), cuyo resultado documentado es divergente: adenda
  “invalidada in-flight”; cierre kill 12:38 exit 0 sin activación; focal 12:41
  activado exit 1. El informe lo menciona aparte y a la vez lo incluye en “las
  35 → exit 0”, contradicción interna. Estados asignados:
  `EVIDENCIA-DE-SONDA-INSUFICIENTE` (34) y `PENDIENTE-DE-REVALIDACIÓN` (u6).
  Ninguno de los dos es `DISCREPANCIA-DEMOSTRADA`.

## 4. Fase 1–2 — copia sucesora y comparación mínima ejecutada

Copia aislada `build/tmp/gs2-diac.yuISyH`: fuente, tests y árbol generado
identificados por hash (`evidence/hashes-pre-sonda.sha256`); coinciden con la
campaña: generado `1ccdf8d6794bd0e1bfbfe7b5b1ff99cbd9d5447430fcdb8a12cf32cceb894faa`,
tests históricos `8b0f71e375c7581fab06287f3eb9a25082ca760074862bab4cee03778b0ed2fe`
(no las regresiones `ddb1b46`), pyproject de receta
`2d7ede5a9e1839b2a3cc386e262badf3fc70e1fdb47f2ec4510491fd24a6911f`,
asociaciones `e4ab74bd738b451df0d3ee14db65b2593a5cde7abac92e31885aba875880a877`,
colección `f8b4ebbbb65ad36cc116678cd90e4df0b5669f4d2c65d3ca18be6142e4878234`.

Lanzador sucesor `sonda-succ.sh` (fail-closed): ID completo obligatorio y
perteneciente al inventario; asociaciones presentes, legibles y con sección;
selección no vacía y sin fallback a suite completa; nodeids verificados contra
la colección; entorno saneado primero; modo explícito `original` (`env -u
MUTANT_UNDER_TEST`) o `mutante` (`env MUTANT_UNDER_TEST=<id>`); cwd y
`PYTHONPATH` dentro de la copia (`checkout/mutants` + `src` + raíz del
expediente); argv como lista (sin `eval`); timeout por sonda y códigos 2–8
registrados. Antes de cada sonda, un autochequeo en proceso hijo acredita la
transmisión del modo (`selftest-esperado`/`selftest-leido`).

Instrumentación temporal mínima (`instrumento.py`, cargado con
`-p instrumento`; no es plugin productivo): dentro del proceso pytest emite
`INST-SONDA` con PID, intérprete, cwd, valor efectivo de `MUTANT_UNDER_TEST`,
ruta efectiva de la fuente instrumentada y pertenencia del nombre de mutante
a la tabla `MutantDict` generada (`variante_en_tabla`).

Selecciones resueltas desde el inventario (sin reconstruir IDs abreviados):

- A (canario histórico documentado): `x__build_dirs__mutmut_1` — el ledger
  histórico registra exit 1 por `AssertionError: assert <Status.ERROR> is
  <Status.FAIL>` y el cierre lo usó como control de sanidad (exit 0 sin
  activación).
- B (ID del conjunto discrepante): `x__unique_dirs__mutmut_7` — fila del
  ledger de 34 con exit 0; su diff está disponible (variante en el árbol
  generado) y sus tests asociados, en la colección verificada.

| Sonda | Selección | Modo | Exit | Resultado registrado |
|---|---|---|---|---|
| Control A | `x__build_dirs__mutmut_1` | original | 0 | 11 passed, 10.461 s; `selftest-leido=<AUSENTE>` |
| Canario A | `x__build_dirs__mutmut_1` | mutante | 1 | 1.490 s; `FAILED test_binding_fixture_adversarial_raiz_propia`; `AssertionError: assert <Status.ERROR> is <Status.FAIL>` (causa histórica prevista) |
| Control B | `x__unique_dirs__mutmut_7` | original | 0 | 13 passed, 10.212 s; `selftest-leido=<AUSENTE>` |
| Discrepante B | `x__unique_dirs__mutmut_7` | mutante | 1 | 1.565 s; `FAILED test_binding_fixture_adversarial_raiz_propia`; `TypeError: unsupported operand type(s) for /: 'PosixPath' and 'NoneType'` |

Activación acreditada en el mismo proceso de las sondas mutantes (logs
`sonda`): `mutant_under_test=<id completo>`,
`fuente=<copia>/checkout/mutants/tools/wct/gate/semgrep_scope.py`,
`variante=<nombre>`, `variante_en_tabla=mutants_<función>__mutmut`. El control
original conserva fuentes, tests, selección, flags y entorno; la única
diferencia intencional es la activación. Un exit 1 no se interpreta como kill
por sí solo: en el canario coincide con la causa documentada y en B con un
`TypeError` mecánicamente explicable por el diff del mutante.

**Presupuesto real (Fase 2)**: 23.728 s de pytest (4 sondas) + 4 autochequeos
de entorno (< 1 s) + comprobaciones de bloqueo sin pytest. Total < 25 s de los
300 s autorizados. Sin reintentos; el verifier no reejecutó nada (modalidad
documental).

## 5. Fase 3 — conclusión causal acotada

Resultado **tipo 1** para los casos medidos: la corrección de la receta
restaura una detección esperada. El canario reproduce la causa histórica exacta
con activación acreditada, y el ID discrepante pasa de exit 0 (sin activación)
a exit 1 con activación acreditada y causa propia del mutante. Esto es
evidencia de defecto de la receta del cierre, no de mutmut.

No se extrapola a los otros 33 IDs del ledger, ni a los 63, ni al bruto 102:
la afirmación de artefacto instrumental del cierre queda sin sustento para el
caso medido; no se declara corrupción de mutmut; no se invalidan ni rehabilitan
en bloque los resultados previos. El `TypeError` de `x__unique_dirs__mutmut_6`
es mecanismo del kill (llamada mutada sin argumento), no corrupción del
trampolín; su revalidación formal sigue pendiente.

## 6. Reconciliación de los 118 IDs

Leyenda de estados: `KILLED-EVIDENCIADO-HISTÓRICO` (sonda histórica con
activación explícita; sin revalidación posterior ID a ID — la evidencia es
lanzador sellado + ledger, no instrumentación por ID);
`KILLED-EVIDENCIADO-ADENDA` (activada, detectada por suite completa, desviación
declarada); `EVIDENCIA-DE-SONDA-INSUFICIENTE` (sonda del cierre sin
activación); `PENDIENTE-DE-REVALIDACIÓN` (`unique_dirs_6`); `SURVIVED-HISTÓRICO`
(regresión posterior demostrada en `ddb1b46`; no convierte `survived` en
`killed`). Las regresiones posteriores son sensibilidad de tests, no veredicto
de campaña.

| ID | Bruto histórico | Evidencia causal y procedencia | Evidencia posterior | Estado actual de revisión | Motivo y referencia |
|---|---|---|---|---|---|
| `x__build_dirs__mutmut_1` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | GS2-DIAG §4: control original exit 0 / mutante activado exit 1 (AssertionError ERROR vs FAIL) | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_10` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_11` | survived | sonda activada exit 0; asociados pasan (sonda exit 0, todos los tests asociados pasan) | demostración 16: exit 1 RECHAZADO; E Failed: DID NOT RAISE SemgrepScopeError; regresiones ddb1b46 | SURVIVED-HISTÓRICO | regresión posterior demostrada (ddb1b46); no convierte survived en killed |
| `x__build_dirs__mutmut_12` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_13` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_14` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: 'NoneType' object is not iterable | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_15` | survived | sonda activada exit 0; asociados pasan (sonda exit 0, todos los tests asociados pasan) | demostración 16: exit 1 RECHAZADO; E AssertionError: assert False; regresiones ddb1b46 | SURVIVED-HISTÓRICO | regresión posterior demostrada (ddb1b46); no convierte survived en killed |
| `x__build_dirs__mutmut_16` | survived | sonda activada exit 0; asociados pasan (sonda exit 0, todos los tests asociados pasan) | demostración 16: exit 1 RECHAZADO; E AssertionError: assert False; regresiones ddb1b46 | SURVIVED-HISTÓRICO | regresión posterior demostrada (ddb1b46); no convierte survived en killed |
| `x__build_dirs__mutmut_17` | survived | sonda activada exit 0; asociados pasan (sonda exit 0, todos los tests asociados pasan) | demostración 16: exit 1 RECHAZADO; E AssertionError: assert False; regresiones ddb1b46 | SURVIVED-HISTÓRICO | regresión posterior demostrada (ddb1b46); no convierte survived en killed |
| `x__build_dirs__mutmut_18` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: 'NoneType' object is not iterable | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_19` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_build_anidado_respeta_el_limite_de_directorio; E tools.wct.gate.semgrep_scope.SemgrepScopeError: ruta de construcción no normalizable bajo la raíz: 'src/bui… | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_2` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_build_anidado_respeta_el_limite_de_directorio; E AssertionError: assert ['src/build/g...c/builder.py'] == ['src/build2/...c/builder.py'] | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_20` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_build_anidado_respeta_el_limite_de_directorio; E tools.wct.gate.semgrep_scope.SemgrepScopeError: ruta de construcción no normalizable bajo la raíz: 'src/bui… | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_21` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_build_anidado_respeta_el_limite_de_directorio; E tools.wct.gate.semgrep_scope.SemgrepScopeError: ruta de construcción no normalizable bajo la raíz: 'src/bui… | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_22` | survived | sonda activada exit 0; asociados pasan (sonda exit 0, todos los tests asociados pasan) | demostración 16: exit 1 RECHAZADO; E AssertionError: assert False; regresiones ddb1b46 | SURVIVED-HISTÓRICO | regresión posterior demostrada (ddb1b46); no convierte survived en killed |
| `x__build_dirs__mutmut_23` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_build_anidado_respeta_el_limite_de_directorio; E TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_24` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_build_anidado_respeta_el_limite_de_directorio; E TypeError: unsupported operand type(s) for *: 'PosixPath' and 'PosixPath' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_3` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_4` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: unhashable type: 'list' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_5` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_6` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E KeyError: 'XXpathsXX' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_7` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E KeyError: 'PATHS' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_8` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_build_anidado_respeta_el_limite_de_directorio; E AssertionError: assert ['src/build/g...c/builder.py'] == ['src/build2/...c/builder.py'] | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__build_dirs__mutmut_9` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_build_anidado_respeta_el_limite_de_directorio; E AssertionError: assert ['src/build/g...c/builder.py'] == ['src/build2/...c/builder.py'] | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__is_string_list__mutmut_1` | survived | sonda activada exit 0; asociados pasan (sonda exit 0, todos los tests asociados pasan) | demostración 16: exit 1 RECHAZADO; E Failed: DID NOT RAISE SemgrepScopeError; regresiones ddb1b46 | SURVIVED-HISTÓRICO | regresión posterior demostrada (ddb1b46); no convierte survived en killed |
| `x__is_string_list__mutmut_2` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: 'NoneType' object is not iterable | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_1` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AttributeError: 'NoneType' object has no attribute 'add' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_10` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: 'NoneType' object is not iterable | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_11` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_build_anidado_respeta_el_limite_de_directorio; E TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_12` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_build_anidado_respeta_el_limite_de_directorio; E AssertionError: assert [] == ['src/build2/...c/builder.py'] | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_13` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AttributeError: 'NoneType' object has no attribute 'parts' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_14` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_15` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fuente_ignorada; E AssertionError: assert <Status.PASS: 'PASS'> is <Status.ERROR: 'ERROR'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_16` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: 'NoneType' object is not iterable | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_17` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_caches_y_entornos_anidados_quedan_fuera; E AssertionError: assert [] == ['src/a.py'] | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_18` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: sequence item 0: expected str instance, NoneType found | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_2` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: 'NoneType' object is not iterable | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_3` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_4` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fuente_ignorada; E AssertionError: assert <Status.PASS: 'PASS'> is <Status.ERROR: 'ERROR'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_5` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fuente_ignorada; E AssertionError: assert <Status.PASS: 'PASS'> is <Status.ERROR: 'ERROR'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_6` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AttributeError: 'NoneType' object has no attribute 'is_relative_to' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_7` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_8` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__python_files__mutmut_9` | survived | sonda activada exit 0; asociados pasan (sonda exit 0, todos los tests asociados pasan) | demostración 16: exit 1 RECHAZADO; E AssertionError: assert False; regresiones ddb1b46 | SURVIVED-HISTÓRICO | regresión posterior demostrada (ddb1b46); no convierte survived en killed |
| `x__relative__mutmut_1` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia;  | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__relative__mutmut_10` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__relative__mutmut_2` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia;  | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__relative__mutmut_3` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia;  | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__relative__mutmut_4` | survived | sonda activada exit 0; asociados pasan (sonda exit 0, todos los tests asociados pasan) | demostración 16: exit 1 RECHAZADO; E AssertionError: assert False; regresiones ddb1b46 | SURVIVED-HISTÓRICO | regresión posterior demostrada (ddb1b46); no convierte survived en killed |
| `x__relative__mutmut_5` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AttributeError: 'NoneType' object has no attribute 'is_relative_to' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__relative__mutmut_6` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: unsupported operand type(s) for *: 'PosixPath' and 'PosixPath' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__relative__mutmut_7` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia;  | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__relative__mutmut_8` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__relative__mutmut_9` | survived | sonda activada exit 0; asociados pasan (sonda exit 0, todos los tests asociados pasan) | demostración 16: exit 1 RECHAZADO; E AssertionError: assert False; regresiones ddb1b46 | SURVIVED-HISTÓRICO | regresión posterior demostrada (ddb1b46); no convierte survived en killed |
| `x__scoped_dirs__mutmut_1` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__scoped_dirs__mutmut_10` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__scoped_dirs__mutmut_11` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fuente_ignorada; E AssertionError: assert <Status.PASS: 'PASS'> is <Status.ERROR: 'ERROR'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__scoped_dirs__mutmut_12` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__scoped_dirs__mutmut_13` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: unhashable type: 'list' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__scoped_dirs__mutmut_14` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__scoped_dirs__mutmut_15` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__scoped_dirs__mutmut_16` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__scoped_dirs__mutmut_17` | survived | sonda activada exit 0; asociados pasan (sonda exit 0, todos los tests asociados pasan) | demostración 16: exit 1 RECHAZADO; E AssertionError: assert False; regresiones ddb1b46 | SURVIVED-HISTÓRICO | regresión posterior demostrada (ddb1b46); no convierte survived en killed |
| `x__scoped_dirs__mutmut_18` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: 'NoneType' object is not iterable | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__scoped_dirs__mutmut_2` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__scoped_dirs__mutmut_3` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__scoped_dirs__mutmut_4` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__scoped_dirs__mutmut_5` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AssertionError: assert <Status.ERROR: 'ERROR'> is <Status.FAIL: 'FAIL'> | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__scoped_dirs__mutmut_6` | survived | sonda activada exit 0; asociados pasan (sonda exit 0, todos los tests asociados pasan) | demostración 16: exit 1 RECHAZADO; E AssertionError: assert False; regresiones ddb1b46 | SURVIVED-HISTÓRICO | regresión posterior demostrada (ddb1b46); no convierte survived en killed |
| `x__scoped_dirs__mutmut_7` | survived | sonda activada exit 0; asociados pasan (sonda exit 0, todos los tests asociados pasan) | demostración 16: exit 1 RECHAZADO; E AssertionError: assert False; regresiones ddb1b46 | SURVIVED-HISTÓRICO | regresión posterior demostrada (ddb1b46); no convierte survived en killed |
| `x__scoped_dirs__mutmut_8` | survived | sonda activada exit 0; asociados pasan (sonda exit 0, todos los tests asociados pasan) | demostración 16: exit 1 RECHAZADO; E AssertionError: assert False; regresiones ddb1b46 | SURVIVED-HISTÓRICO | regresión posterior demostrada (ddb1b46); no convierte survived en killed |
| `x__scoped_dirs__mutmut_9` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AttributeError: 'NoneType' object has no attribute 'extend' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__unique_dirs__mutmut_1` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E AttributeError: 'NoneType' object has no attribute 'setdefault' | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__unique_dirs__mutmut_10` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia;  | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__unique_dirs__mutmut_11` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia;  | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__unique_dirs__mutmut_12` | survived | sonda activada exit 0; asociados pasan (sonda exit 0, todos los tests asociados pasan) | demostración 16: exit 1 RECHAZADO; E AssertionError: assert False; regresiones ddb1b46 | SURVIVED-HISTÓRICO | regresión posterior demostrada (ddb1b46); no convierte survived en killed |
| `x__unique_dirs__mutmut_13` | killed | sonda activada exit 1; mata tests/unit/test_sast_targets.py::test_binding_fixture_adversarial_raiz_propia; E TypeError: 'NoneType' object is not iterable | — | KILLED-EVIDENCIADO-HISTÓRICO | sonda histórica con MUTANT_UNDER_TEST explícito (sondas-gs2.sh:18); sospecha de GS2-CIERRE §2 sin instrumento que la sostenga; sin revalidación ID a ID |
| `x__unique_dirs__mutmut_2` | killed | sonda activada exit 1 (suite completa); mata tests/unit/test_redteam_tools.py::test_tool_case_catches_planted_defect[F9-a]; E TypeError: unsupported operand type(s) for /: 'PosixPath' and 'NoneType' | — | KILLED-EVIDENCIADO-ADENDA | adenda GS-2 §1; detección por suite completa (desviación declarada) |
| `x__unique_dirs__mutmut_3` | killed | sonda activada exit 1 (suite completa); mata tests/unit/test_redteam_tools.py::test_tool_case_catches_planted_defect[F9-a]; E TypeError: unsupported operand type(s) for /: 'NoneType' and 'PosixPath' | — | KILLED-EVIDENCIADO-ADENDA | adenda GS-2 §1; detección por suite completa (desviación declarada) |
| `x__unique_dirs__mutmut_4` | killed | sonda activada exit 1 (suite completa); mata tests/unit/test_redteam_tools.py::test_tool_case_catches_planted_defect[F9-a]; E AssertionError: F9-a: ruta de alcance no normalizable bajo la raíz: None | — | KILLED-EVIDENCIADO-ADENDA | adenda GS-2 §1; detección por suite completa (desviación declarada) |
| `x__unique_dirs__mutmut_5` | killed | sonda activada exit 1 (suite completa); mata tests/unit/test_redteam_tools.py::test_tool_case_catches_planted_defect[F9-a]; E TypeError: x__relative__mutmut_orig() missing 1 required positional argument: 'raw' | — | KILLED-EVIDENCIADO-ADENDA | adenda GS-2 §1; detección por suite completa (desviación declarada) |
| `x__unique_dirs__mutmut_6` | killed | adenda: 5.ª sonda invalidada in-flight; cierre kill exit 0 sin activación; log focal 12:41 activado exit 1 (TypeError, lanzador no atribuido) | — | PENDIENTE-DE-REVALIDACIÓN | adenda §1 (invalidada) + GS2-DIAG §4-§5; no se acredita activación sellada |
| `x__unique_dirs__mutmut_7` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | GS2-DIAG §4: control original exit 0 / mutante activado exit 1 (TypeError PosixPath / NoneType) | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x__unique_dirs__mutmut_8` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x__unique_dirs__mutmut_9` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_relative_path__mutmut_1` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_relative_path__mutmut_2` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_relative_path__mutmut_3` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_relative_path__mutmut_4` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_relative_path__mutmut_5` | survived | sonda activada exit 0; asociados pasan (sonda exit 0, todos los tests asociados pasan) | demostración 16: exit 1 RECHAZADO; E Failed: DID NOT RAISE SemgrepScopeError; regresiones ddb1b46 | SURVIVED-HISTÓRICO | regresión posterior demostrada (ddb1b46); no convierte survived en killed |
| `x_relative_path__mutmut_6` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_relative_path__mutmut_7` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_relative_path__mutmut_8` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_1` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_10` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_11` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_12` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_13` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_14` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_15` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_16` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_17` | survived | sonda activada exit 0; asociados pasan (sonda exit 0, todos los tests asociados pasan) | demostración 16: exit 1 RECHAZADO; E AssertionError: assert [] == ['src/a.py']; regresiones ddb1b46 | SURVIVED-HISTÓRICO | regresión posterior demostrada (ddb1b46); no convierte survived en killed |
| `x_required_sources__mutmut_18` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_19` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_2` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_20` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_21` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_22` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_23` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_24` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_25` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_3` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_4` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_5` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_6` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_7` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_8` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |
| `x_required_sources__mutmut_9` | killed | sonda cierre focal exit 0 SIN activación (sonda-fc.sh:67-69; el trampolín cayó a orig) | — | EVIDENCIA-DE-SONDA-INSUFICIENTE | GS2-DIAG §4; la sonda corrió el original, el exit 0 no mide al mutante |

Contabilidad: 118 filas = 118 IDs únicos del inventario
(`inventario-autorizado.txt`), sin duplicados: 63 + 4 + 34 + 1 + 16 = 118, que
preserva 102 killed + 16 survived.

## 7. Afirmaciones retiradas, matizadas y confirmadas

Retiradas (por refutación documental de §1–§2):

1. “pytest in-process … secuencialmente para los 118 mutantes” — mutmut 3.7.0
   forkea por mutante; `pytest.main` corre en el hijo.
2. “corrupción de despacho del trampolín” — los frames `trampoline.py:84` son
   paso a `orig_func` de trampolines anidados; la causa es la mutación.
3. “contaminación de estado del runner in-process” — sin mecanismo posible
   entre hijos forkeados del mismo padre.
4. “los 35 → exit 0 bajo el mutante activado” — son 34 sin activación; `u6` es
   divergente.
5. “los 63 quedan bajo sospecha de artefacto” (sospecha en bloque) — sin
   instrumento que la sostenga; su estatus histórico no cambia.
6. “63 + 35 + 16 = 114” — omite los 4 de la adenda.

Matizadas:

- “47 tests focales” describe el archivo completo ejecutado por la sonda
  focal, no la selección del ID.
- La nota de grafía `x_` vs `x__` es una regla (usar el ID exacto del
  inventario, sin normalizar), no una regla léxica general.
- La cita `__main__.py:438-451` corresponde a `execute_pytest`, no al bucle de
  campaña (1472-1494).
- `x__unique_dirs__mutmut_6`: de “DISCREPANCIA-NO-REPRODUCIDA” a
  `PENDIENTE-DE-REVALIDACIÓN` (nunca tuvo sondeo con activación sellado;
  adenda ya la declaró invalidada).

Confirmadas:

- Bruto histórico 118 = 102 killed + 16 survived (inalterado).
- Los lanzadores de la campaña y de la adenda sí activaban
  (`sondas-gs2.sh:18`, `sonda.sh:17`).
- Los 4 de la adenda (`unique_dirs_2/3/4/5`) con detección activada por suite
  completa.
- Los 16 supervivientes con regresión posterior demostrada (`ddb1b46`) que no
  los convierte en kills de campaña.

Reservas y límites declarados: los 63 conservan su evidencia de lanzador y
ledger sin revalidación ID a ID; `sonda.sh:12` usa `local` fuera de función
(defecto latente, no invalidante); la primera fila de
`demostraciones-16-ledger.tsv` es una cabecera anómala del artefacto sellado
(no se edita); la tabla de §6 no pertenece al sello del expediente y se
identifica por sus hashes en §0.

## 8. Revisión independiente

Modalidad: **documental, sin reejecución** (el verifier no ejecutó pytest ni
`mutmut`; su presupuesto adicional fue 0 s). Dictamen: **favorable con
reservas**. Confirmó la correspondencia lanzador–evidencia (sellos 106/106,
12/12, 129/129), la ausencia de activación en las 34 sondas focales, la
transmisión de la activación en el expediente sucesor, la lectura de
fork/pytest.main/os._exit, la reconciliación de 118 identidades y la ausencia
de extrapolaciones; y señaló como reservas: `u6` sin atribución a lanzador
sellado, tabla no sellada, evidencia de los 63 sin instrumentación por ID,
`local` en `sonda.sh:12`, y las correcciones de §7 (todas incorporadas a esta
nota).

## 9. Próxima acción mínima (no ejecutada)

Revalidar los 34 IDs con la receta corregida y los tests históricos (estimado
≈ 12 s por sonda ≈ 7 min de pytest, fuera del presupuesto de este encargo),
empezando por `x__unique_dirs__mutmut_6`; con los resultados, decidir si se
revalida ID a ID una muestra de los 63. No ejecutar en este incremento.
No abre GS-3, no habilita bless/merge/bump/tag/release.
