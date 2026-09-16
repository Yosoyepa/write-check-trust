# Prompt propuesto — GS-3: calificación de mutación de `tools/wct/gate/semgrep.py`

> **ESTADO: propuesta documental. NO EJECUTADO. NO autoriza nada.** Este texto
> no es un encargo activo ni un permiso de campaña: la ejecución de GS-3 exige
> (a) autorización humana explícita y (b) dictamen independiente previo de sólo
> lectura (PROC-005) sobre la receta y las identidades congeladas.
> No es bless, merge, bump, tag ni release; no acredita AC1 ni beta.3.
>
> **Nota sucesora (2026-09-15)**: GS-3 se ejecutó después con autorización
> humana, verifier de puerta y corte `eec71fb1a1dc502b3ab7d557893fcdae4a33be2b`.
> Resultado: FAIL-survivors-stop (74 killed + 34 survived de 108), sin PASS ni
> reparaciones; ver `GS3-SEMGREP-RESULTADO-2026-09-15.md`. Las referencias de
> este anexo afectadas por el nuevo corte quedaron actualizadas en §1 y §1.3.

Este prompt es autosuficiente: incorpora el alcance confirmado por inspección
estática, las precondiciones, la receta fail-closed derivada de las lecciones
de GS-2, los controles (canario + negativos), el formato de evidencia por ID,
el sellado, el presupuesto estimado y las condiciones de parada.

---

## 0. Encargo y límites

1. Ejecutar **únicamente GS-3**: medir la sensibilidad de mutación de
   `tools/wct/gate/semgrep.py` y clasificar causalmente cada ID del inventario
   generado, sobre un corte congelado y una copia aislada.
2. Prohibido sin autorización nueva: tocar producto, tests, features,
   gobernanza, workflows ni dependencias del checkout principal o del worktree;
   reparar supervivientes; abrir GS-4; ejecutar aceptación, cobertura/CRAP, DRY
   o tier full; bless, merge, bump, tag ni release.
3. **No reabrir ni re-ejecutar GS-1 ni GS-2**: sus expedientes sellados no se
   editan ni se reutilizan como veredicto de este lote. Si GS-2 sigue sin
   cierre (E4 de la matriz), GS-3 no arranca (ver §7).
4. La parada es por lote: entrega al terminar o al agotar presupuesto. Los
   casos dudosos quedan pendientes y declarados; no pasan por muestreo ni se
   convierten en equivalentes por omisión.

## 1. Alcance confirmado (inspección estática; corte ejecutado `eec71fb…`)

Corte de referencia de este prompt:
`eec71fb1a1dc502b3ab7d557893fcdae4a33be2b` (corte congelado y ejecutado de
GS-3; antes de la ejecución la referencia era `bdb7db3…`). El incremento
ejecutor congela su propio candidato al autorizarse; si el SHA difiere,
re-verifica los hashes de §1.3 y, si `semgrep.py` cambia, **BLOQUEA y
re-planifica**.

### 1.1 Módulo objetivo

| Ruta | sha256 en el corte | LOC | Funciones AST |
|---|---|---|---|
| `tools/wct/gate/semgrep.py` | `0126c4e1bdad3a445a3d3821b46cdd75d1ebec6e2d080ab299fd8d2ebd682657` | 96 | 3: `_topology`, `_policy`, `gate_sast_semgrep`; 0 decoradas; 0 anidadas |

Es el único archivo de nombre `semgrep.py` del árbol. Es archivo **nuevo**
(alta en `88de60e`), por lo que no le aplica TEST-007 de archivos
preexistentes; su frontera contractual es ≤100 sitios WCT.

Datos de módulo: `GATE_ID = "G-SAST-SEMGREP"`, `COMMAND = ("semgrep", "--quiet",
"--error", "--severity", "ERROR", "--config", "governance/semgrep", "--json")`,
`__all__` (re-exporta `SemgrepScopeError`, `Verdict`, `classify`,
`required_sources`). **Limitación instrumental declarada**: mutmut 3.7.0 no
trampolina código de módulo; `COMMAND`/`GATE_ID`/`__all__` quedan fuera del
universo de mutación. La política de comando se verifica por las corridas
reales de semgrep y por aserciones existentes, no por mutación (hueco conocido,
ADENDA §5-5.c; no se convierte en cobertura).

### 1.2 Sitios de mutación WCT (métrica del motor productivo, reproducida)

`mutation_sites` (mismos bytes del corte): **51 sitios** = `<module>` 17 +
`_topology` 13 + `_policy` 6 + `gate_sast_semgrep` 15. Coincide con el valor
51 registrado en `ADENDA-PREPARACION-LOTE-GATE-SELFTEST-2026-09-13` §3.
**No confirmado**: el número de mutantes mutmut (sólo lo fija el gen-only) y
las asociaciones exactas (sólo las fija la fase de stats). Estimar ≈60–110
mutantes es una hipótesis de presupuesto, no una medición. *(Medido en la
ejecución GS-3 sobre `eec71fb`: 108 mutantes generados y 108 asociaciones no
vacías; la hipótesis queda superada por la medición.)*

Identidad esperada de IDs (a confirmar en gen-only; no normalizar):
`tools.wct.gate.semgrep.x__topology__mutmut_N`,
`tools.wct.gate.semgrep.x__policy__mutmut_N`,
`tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_N` (privadas `x__`,
pública `x_`).

### 1.3 Inputs de congelación (hashes del corte, `git show <SHA>:<ruta>`)

| Ruta | sha256 en `eec71fb` |
|---|---|
| `tools/wct/gate/semgrep.py` | `0126c4e1bdad3a445a3d3821b46cdd75d1ebec6e2d080ab299fd8d2ebd682657` |
| `tests/unit/test_sast_targets.py` | `a042b6f8e70eff3e853dcbf0073fb7262cde2d0f06eca495296f49faea878f08` |
| `tests/conftest.py` | `063f5dccefacdc5ed58f70fae6e5095394cd7a9d8af5d5d98536753a4fda6d73` |
| `pyproject.toml` | `c3a1b3e7eaca4545eadb0c935750f199bef390c407f91863e3965b0fdd2c4509` |
| `uv.lock` | `072b223b206c6a42fe97373b3b0c59a694b6f21383e0b8bf84b4a671625f3409` |
| `features/wct-sast-targets-001.feature` | `bb69bdf7fcffd638fbd22e50bee1d86cdc520e6718875d3906f33af78a22373f` |
| `tools/wct/gate/runner.py` (consumidor) | `6e568767066c10bd7bc1fde6a8410133a64e30c3dc6be7cbe27b71d09acd8943` |
| `tools/wct/gate/semgrep_scope.py` (dependencia) | `0bf26c714de0c512ed76ecbd9008efe3a2be7199ca241273a802bc24279bb12e` |
| `tools/wct/gate/semgrep_verdict.py` (dependencia) | `3c10978038cbfe91578f8f9ef749d865b4322f7cd3cd03aa30d71cf204d19be4` |

Cualquier diferencia **BLOQUEA** antes de generar.

### 1.4 Dependencias, consumidores y herramientas externas

- Dependencias: `tools.wct.config` (`ConfigError`, `load_yaml`),
  `tools.wct.gate.semgrep_scope` (`SemgrepScopeError`, `required_sources`),
  `tools.wct.gate.semgrep_verdict` (`Verdict`, `classify`),
  `tools.wct.model` (`GateResult`, `Status`).
- Consumidores: `tools/wct/gate/runner.py` (import + entrada
  `REGISTRY["G-SAST-SEMGREP"] = declares(gate_sast_semgrep, tools=("semgrep",),
  scope=(".",))`); `tests/unit/test_report_profile.py` (despacho/presencia/
  scope); `tests/unit/test_sast_targets.py` (llamadas directas).
- Procesos externos: `git rev-parse --show-toplevel` (`_topology`) y el binario
  `semgrep` con `COMMAND` (`gate_sast_semgrep`); `shutil.which("semgrep")`
  gobierna el SKIP por herramienta ausente.
- Tests focales existentes (selección de la receta:
  `tests/unit/test_sast_targets.py`), con **guard de skip** por `semgrep`:
  1. `…::test_raiz_absorbida_por_ancestro_ajeno_es_error` (`_topology`)
  2. `…::test_raiz_git_propia_permite_analisis_sano` (gate completo, semgrep real)
  3. `…::test_binding_fixture_adversarial_raiz_propia` (gate completo, semgrep real)
  4. `…::test_fallo_de_ejecucion_del_instrumento_es_error` (OSError monkeypatched)
  Los 4 skipean si `shutil.which("semgrep") is None`: un skip hace el mutante
  no discriminable. **Semgrep y git deben estar en el PATH de la copia y la
  colección focal debe dar 0 skips**, usando el runtime de §2.
- No confirmado: asociación exacta ID→nodeids y coste real por mutante; se
  miden en stats/calibración (§3 P6 y P8).

## 2. Precondiciones

1. **Autorización humana expresa** del lote, del corte y del presupuesto (§6),
   y **dictamen independiente previo** (PROC-005) que apruebe esta receta, los
   hashes de §1.3 y la identidad del instrumento.
2. **Estado del programa**: GS-2 (E4 de `MATRIZ-DECISIONES-AC1-PENDIENTES`)
   cerrado o explícitamente desbloqueado; decisión humana sobre el orden
   frente a los pendientes D-A/D-C (recomendación de la matriz:
   GS-1 → GS-2 → GS-3). Si GS-2 no está cerrado, **no arrancar**.
3. **Runtime existente, sin sync ni instalación**:
   `<raíz>/build/tmp/sh-p01-CND-80B8/.venv` — Python 3.13.14, mutmut 3.7.0,
   pytest 9.1.1, semgrep 1.174.0; `git` 2.55.0 del sistema. PATH incluye
   `<runtime>/bin` (semgrep se resuelve solo así); registrar versiones.
4. **Aislamiento**: clon Git real desprendido del SHA candidato
   (`git clone --no-hardlinks file://<raíz>` + `checkout --detach`), árbol
   limpio (`status --porcelain` vacío); no `git archive`, no reutilizar copias,
   `mutants/` ni veredictos de campañas anteriores; temporales privados y
   precreados; todo bajo `build/tmp` (PROC-007), nunca `/tmp`.
5. **Asociaciones**: `mutmut tests-for-mutant <id>` no vacío para cada ID del
   conjunto objetivo; nodeids verificados contra la colección real;
   «asociación ≠ discriminación».
6. **Activación**: lanzador fail-closed (§3 P9) con modo explícito
   original/mutante, autochequeo de transmisión y acreditación **dentro del
   proceso real** (no basta el exit code). Lección GS-2: un exit 0 bajo un
   lanzador que no re-asigna `MUTANT_UNDER_TEST` mide el original
   (`GS2-DIAGNOSTICO-ACTIVACION-SONDAS-2026-09-15` §1 y §4).
7. **Baseline**: selección focal con exit 0 y **0 skipped, 0 xfail, 0 error**
   antes de generar; si hay skips, **BLOQUEA** (no se muta lo no
   discriminable).

## 3. Receta fail-closed (fases P0–P12)

Placeholders: `R=<raíz del repo>`, `V=<runtime>/.venv`,
`CUT=<SHA candidato congelado>`, `RUN=$(mktemp -d $R/build/tmp/gs3.XXXXXX)`
con toda la evidencia bajo `$RUN/evidence/`.

- **P0 — Entorno limpio por paso**: `PATH=$V/bin:$PATH`,
  `PYTHONDONTWRITEBYTECODE=1`, `PYTHONSAFEPATH=1`, `PYTHONNOUSERSITE=1`,
  `TMPDIR=$RUN/tmp` y `PYTEST_DEBUG_TEMPROOT=$RUN/tmp/tmp-pytest` privados y
  precreados, sin `WCT_ACCEPT_*` ni `PYTEST_PLUGINS` heredados, `UV_NO_SYNC=1`;
  cada paso re-fija su `cd` (no depender del heredado).
- **P1 — Clon aislado**: clon `file://` + `checkout --detach $CUT`; registrar
  `rev-parse HEAD` y exigir `status --porcelain` vacío (si no, BLOQUEA).
- **P2 — Hashes de corte**: `sha256sum -c corte.sha256` con las rutas de §1.3;
  cualquier diferencia BLOQUEA antes de continuar.
- **P3 — `pyproject.toml` privado de mutmut** (sustituir la sección
  `[tool.mutmut]`, registrar su sha256):
  ```toml
  [tool.mutmut]
  source_paths = ["tools"]
  only_mutate = ["tools/wct/gate/semgrep.py"]
  also_copy = ["src", "features", "governance"]
  pytest_add_cli_args_test_selection = ["tests/unit/test_sast_targets.py"]
  pytest_add_cli_args = ["-m", "not property"]
  use_git_change_detection = false
  ```
- **P3b — Pre-poblar `mutants/`** con el árbol del clon excluyendo `./mutants` y
  `./.git` (sin esto, el stats corre pytest con `cwd=mutants` sin selección y
  el run crashea antes de la firma admisible — lección RECETA-FASE-G P3b).
  Comprobar que `mutants/tests/unit/test_sast_targets.py`,
  `mutants/tests/conftest.py` y `mutants/pyproject.toml` existen; si no,
  BLOQUEA.
- **P4 — Baseline y colección** (PYTHONPATH `$RUN/checkout` +
  `$RUN/checkout/src`): `pytest --collect-only -q tests/unit/test_sast_targets.py
  -m "not property"` → `evidence/nodeids.txt`; baseline verde con 0 skips (si
  hay skip, BLOQUEA). Acreditar `semgrep`/`git` en PATH.
- **P5 — Gen-only (generación completa, cero mutantes ejecutados)**: precrear
  `mutants/` y `mutants/src`; `PYTHONPATH=$RUN/checkout/mutants:
  $RUN/checkout/mutants/src`; `timeout --signal=INT --kill-after=30s 900s
  $V/bin/mutmut run --max-children 1 'ZZZ_SIN_COINCIDENCIAS*'`. Única
  terminación admisible: exit ≠ 0 con la firma
  `AssertionError: Filtered for specific mutants, but nothing matches`, log de
  generación completa («1 file mutated, …»), stats corrida y ausencia de
  «Running mutation testing». Cualquier otro final BLOQUEA (conservar log y
  árbol).
- **P6 — Inventario y asociaciones**: snapshot `mutmut-stats.json` **antes** de
  cualquier otra lectura; `mutmut results --all true` → IDs; **no invocar
  `print-time-estimates`** (antecedente invalidado: destruye asociaciones);
  `mutmut tests-for-mutant <id>` por cada ID. Bloquean: inventario vacío; IDs
  fuera de `semgrep.py`; ausencia de las 3 funciones esperadas; funcionalidad
  AST sin instrumentar (0/3); asociación vacía para cualquier ID; drift de
  fuente.
- **P7 — Procedencia**: `python -c "import tools.wct.gate.semgrep as m;
  print(m.__file__)"` debe resolver bajo `$RUN/checkout/mutants/…`; fuga al
  worktree/checkout principal BLOQUEA.
- **P8 — Calibración obligatoria (antes de campaña completa)**: ejecutar en
  modo sonda los **primeros 10 IDs explícitos** del inventario (no globs) con
  el lanzador de P9; medir duración real y proyectar `IDs_totales ×
  coste_observado`. Si la proyección excede el tope de §6-A, **PARAR** y
  entregar preflight; no ampliar tiempo.
- **P9 — Sondas con lanzador fail-closed** (modelo: lanzador sucesor descrito
  en `GS2-DIAGNOSTICO-ACTIVACION-SONDAS-2026-09-15` §4; reconstruirlo desde esa
  especificación si su expediente local no está disponible):
  - ID completo obligatorio, perteneciente al inventario congelado (sin
    normalizar `x_`/`x__`, sin abreviar, sin globs).
  - Asociaciones presentes, legibles y con sección; selección no vacía y **sin
    fallback a suite completa**; nodeids verificados contra la colección.
  - Entorno saneado primero; `cwd` y `PYTHONPATH` dentro de la copia; `argv`
    como lista (sin `eval`); timeout por sonda (120 s) y códigos 2–8
    registrados.
  - Modos explícitos: `env -u MUTANT_UNDER_TEST` (original) y
    `env MUTANT_UNDER_TEST=<id>` (mutante); antes de cada sonda, autochequeo en
    proceso hijo que acredita la transmisión (`selftest-esperado` ==
    `selftest-leido`); discrepancia → BLOQUEA.
  - Instrumento temporal no productivo (`instrumento.py`, cargado con `-p`)
    que emita, **dentro del proceso pytest**: PID, intérprete, `cwd`, valor
    efectivo de `MUTANT_UNDER_TEST`, ruta efectiva de la fuente instrumentada y
    `variante_en_tabla` (pertenencia al `MutantDict` generado). Registrar su
    sha256.
  - **Activación acreditada** = los cuatro campos coherentes con el ID y la
    copia. El exit code por sí solo no acredita nada.
- **P10 — Campaña serial**: `mutmut run --max-children 1` con los **IDs
  explícitos** del inventario congelado (uno por argumento, sin globs), bajo
  `timeout --signal=INT --kill-after=30s <tope-A>`. Revalidar tras el run:
  `sha256sum -c corte.sha256`; inventario post-run conjunto-idéntico al
  congelado (comparación por conjuntos, no por totales; `LC_ALL=C`); los IDs
  fuera del lote permanecen `not checked`. Diferencias → BLOQUEA.
- **P11 — Clasificación causal por ID**: una fila por ID con estado bruto
  mutmut, exit de sonda, campos de activación, tests asociados y causa
  (aserción/excepción en el cuerpo). Mapeo con salvaguardas: `killed` **sólo**
  con exit 1 + activación acreditada + causa atribuible; exit 3 = ERROR-INTERNO
  (no cuenta como killed); exit 0 = `survived`; no-tests/timeout/skip/suspicious
  nunca cuentan como killed.
- **P12 — Sellado**: cerrar el log de pasos **antes** de generar el manifiesto;
  el manifiesto es la última escritura; `sha256sum -c` completo; ningún archivo
  sellado se reescribe después.

## 4. Controles obligatorios (canario + negativos)

1. **C0 — Autochequeo de transmisión** (por sonda): `selftest-esperado` vs
   `selftest-leido`; discrepancia o ausencia → sin acreditación y BLOQUEO.
2. **C1 — Control original**: misma selección e ID con
   `env -u MUTANT_UNDER_TEST` → exit 0. Si el original no pasa, BLOQUEA.
3. **C2 — Canario positivo**: un ID del inventario con efecto conductual
   documentado en la calibración (diff del mutante + causa esperada) → modo
   mutante con activación acreditada y exit no-cero con causa mecánicamente
   atribuible a la mutación. Sin canario discriminante, **no hay campaña**
   (sería una medición ciega).
4. **N1 — Negativo del lanzador**: una variante defectuosa que no re-asigna
   `MUTANT_UNDER_TEST` (patrón `sonda-fc.sh:67-69`) debe ser **rechazada** por
   el autochequeo o registrar activación ausente; el harness no debe contarla
   como evidencia. Reproducir esta variante como control y conservar su log.
5. **N2 — Negativo de identidad**: ID inexistente, incompleto o fuera del
   inventario → aborta antes de pytest.
6. **N3 — Negativo de asociación**: ID sin asociaciones o selección vacía →
   aborta antes de pytest (sin fallback a suite completa).

## 5. Evidencia por ID, clasificación y contabilidad

- Una fila por ID con: `id_completo | función | estado_bruto_mutmut | exit |
  modo | MUTANT_UNDER_TEST_efectivo | fuente_efectiva | variante_en_tabla |
  nodeids_asociados | causa | clase`.
- Clases: `KILLED-EVIDENCIADO`, `SURVIVED-CONFIRMADO`,
  `PENDIENTE-SIN-SONDA` (presupuesto agotado; declarado, nunca oculto),
  `EVIDENCIA-DE-SONDA-INSUFICIENTE` (activación no acreditada),
  `INSTRUMENTAL`, `NO-TESTS`/`TIMEOUT`/`SKIP` (no contables como killed).
- Contabilidad cerrada: suma de clases = número de IDs del inventario.
  Nada se agrega con lotes anteriores ni con GS-1/GS-2; el bruto histórico no
  se reinterpreta.

## 6. Presupuesto (TODO ESTIMACIÓN; requiere autorización)

| Bloque | Tope propuesto (estimación) | Base de la estimación |
|---|---|---|
| **A — generación + stats + baseline + calibración + campaña** | **3600 s** | Tope de lote GS-3 (subprocess) en `PREPARACION-LOTE-GATE-SELFTEST` §6; el coste por mutante de GS-3 será superior al de GS-2 (274,46 s / 118 mutantes, sin procesos) porque los tests lanzan `git` y `semgrep` reales. Calibración obligatoria en P8: si la proyección excede el tope, parar y entregar preflight sin ampliar tiempo. |
| **B — sondas causales de activación** | **1800 s** | Estimación a ≈10–20 s/sonda (tests con semgrep real; ancla GS-2: 4 sondas puras en 23,7 s; RECETA-FASE-G: 48 tests focales en 8 s). Con ≈60–110 IDs, si la proyección de las 10 primeras sondas excede el tope: parar y declarar `PENDIENTE-SIN-SONDA`. Timeout por sonda: 120 s. |
| **C — verificación independiente** | aparte, la fija el verificador | Modalidad documental + re-ejecución de lectura; no consume A/B. |

Los topes son **tope, no objetivo**. Ningún ahorro de presupuesto ni exit 0
constituye PASS.

*(Consumo real de la ejecución autorizada sobre `eec71fb`: sobre A ≈ 706.6 s
de 3600; sobre B ≈ 524.5 s de 1800; parada por supervivientes (§7.5) con
74 killed + 34 survived de 108. Ver `GS3-SEMGREP-RESULTADO-2026-09-15.md`.)*

## 7. Condiciones de parada (obligatorias)

1. **Skips**: cualquier `skipped` en colección/baseline → BLOQUEA y detiene
   (mutante no discriminable). Preferible no arrancar antes que medir a ciegas.
2. **Inventario vacío** o ausencia de las 3 funciones instrumentadas →
   BLOQUEA.
3. **Falta de asociación** para cualquier ID o selección vacía → BLOQUEA el ID
   (sin fallback a suite completa).
4. **Activación no acreditada** (autochequeo fallido o campos ausentes) →
   `EVIDENCIA-DE-SONDA-INSUFICIENTE`; si es sistémica, parada instrumental.
5. **Supervivientes** → `FAIL-survivors-stop`: parar, conservar diffs
   (`mutmut show <id>`) e inventario; la adjudicación es un incremento separado
   con decisión humana. Sin reparaciones ni re-campañas dentro del lote.
6. **Timeouts / ERROR-INTERNO / no-tests / suspicious** → parada instrumental:
   conservar logs completos, no atribuir muertes.
7. **Presupuesto agotado** (A o B) → parar y entregar lo sellado, declarando
   pendientes; nunca silenciar el faltante.
8. **Drift de hashes o desviación del lanzador** (autochequeo, P2/P10) →
   BLOQUEA.
9. **GS-2 sin cierre (E4)** → no arrancar GS-3.

## 8. Sellado, verificación independiente y PASS

- Expediente propio `$RUN/evidence/` con manifiesto `gs3.sha256`; log de pasos
  cerrado antes del manifiesto; manifiesto como última escritura; verificación
  completa con `sha256sum -c`.
- **Verificador independiente sin permiso de escritura (PROC-005)** revisa:
  identidades y hashes, receta, baseline, inventario, asociaciones,
  activación acreditada por ID, clasificación causal, presupuestos y sellado.
  Dictamen con hallazgos bloqueantes/menores.
- **PROHIBIDO declarar PASS del lote sin (a) activación acreditada en el
  proceso real de cada ID contabilizado y (b) dictamen independiente favorable
  sobre el expediente sellado.** Ni un exit code, ni un log con el ID, ni un
  bruto de campaña sustituyen esas dos condiciones. Tampoco este lote acredita
  AC1, GS-2 ni beta.3.

## 9. Prohibiciones explícitas

- No editar producto/tests/features/gobernanza/docs ni el `pyproject.toml`
  real; la configuración mutmut vive sólo en la copia.
- No `git archive`, no `git init` como sustituto, no reutilizar copias ni
  veredictos, no escribir en el checkout principal ni en el worktree.
- No `print-time-estimates`, no globs en la campaña, no fallback a suite
  completa en sondas, no `eval` en el lanzador, no `/tmp` (PROC-007).
- No `git commit --no-verify`, no saltar hooks, no relajar umbrales ni
  ratchets.
- No bless, merge, bump, tag, release, aceptación, CRAP, DRY ni tier full.
- No extrapolar a los 63/34/16 de GS-2 ni mezclar contabilidades.
- No convertir `survived` en `killed` por regresión posterior fuera de este
  lote.

## 10. Entregables

1. Handoff único bajo `$RUN` con: comandos, hashes, inventario (IDs por
   función), asociaciones, resultados brutos y clasificación por ID, sondas y
   activaciones, duraciones y exit codes, causas reales, presupuesto consumido.
2. Acta versionada en `docs/evolution/plans/BETA3/EXECUTION/` (a cargo de quien
   consolide, nunca por el propio ejecutor en el mismo turno) con custodia
   durable de las conclusiones y referencia por hashes al expediente local.
3. Actualización propuesta (no aplicada) de la fila E5 de la matriz y del
   estado del lote; el resultado real manda: `FAIL-survivors-stop`,
   parada instrumental o cierre con evidencia, sin inflar el veredicto.
