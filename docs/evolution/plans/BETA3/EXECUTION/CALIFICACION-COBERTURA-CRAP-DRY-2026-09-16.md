# Calificación de cobertura, CRAP y DRY — AC1 / PR #53 (2026-09-16)

Registro único del encargo «reconciliar la puerta de mutación de fuentes y, si
no queda una obligación bloqueante pendiente, ejecutar cobertura fresca → CRAP
→ DRY» (2026-09-16). Candidato congelado y medido:
`b212f30b9c1e50c5bb1d040e9c5115445f2db79e`. Este registro **no** declara PASS
de G-MUT (no ejecutado), **no** modifica producto, tests, features, gobernanza,
umbrales, baselines, manifests, lock ni versión, y **no** bendice, no hace
merge, bump, tag ni release. La evidencia citada bajo `build/tmp/` es temporal:
no es custodia durable. El documento ajeno
`PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md` permanece intacto, sin
seguimiento y fuera del incremento.

Resultado global: **cobertura fresca APROBADA** (con verifier independiente);
**CRAP canónico `src` conforme, CRAP suplementario `tools/wct` INCUMPLE en
alcance nuevo** (3 funciones); **DRY NO EJECUTADO** por parada expresa ante el
incumplimiento de CRAP. La puerta de mutación de fuentes queda conforme por
cierre adjudicado (resultado 1), con «G-MUT no ejecutado (sin PASS)» como hecho
separado.

## 1. Preflight e identidades

- Worktree `build/tmp/beta3-ac1-r2-integration`, rama
  `codex/beta3-ac1-r2-integration`. HEAD medido
  `b212f30b9c1e50c5bb1d040e9c5115445f2db79e` = `origin` = `headRefOid` de la
  PR #53 (OPEN, draft, `mergeStateStatus` BLOCKED), sin avances remotos
  posteriores. `origin/main` remoto = `932c835ac0eeb75010ec7a1071315b1c51f78eb6`.
- Índice del worktree: vacío salvo el untracked ajeno citado (sha256
  `dedda9f3f057e9a02bd40740404c2c25773ed21b502798360ec5146a0fd1d430`), no
  tocado. El checkout principal se consulta; su trabajo ajeno no se toca. No
  hubo reset, rebase, force push ni `git add -A`.
- Copia Git aislada para medir:
  `build/tmp/calificacion-ac1-covcrapdry-20260916/candidate` (`git worktree`
  detached en `b212f30`, índice y árbol limpios; solo artefactos no rastreados
  de la propia corrida).
- Runtime acreditado: `.venv` del worktree — Python 3.13.14, pytest 9.1.1,
  pytest-cov 7.1.0, coverage 7.15.4, diff-cover 10.5.1, crap4py 0.1.1, jscpd
  5.0.16 (disponible; no invocado). Nada instalado, sincronizado ni modificado
  del runtime compartido; invocación por ruta con `UV_NO_SYNC=1` o con
  `PATH`/`PYTHONPATH` explícitos.
- Hashes de configuración del candidato (`config-hashes.txt`): `pyproject.toml`
  `c3a1b3e7…`, `governance/thresholds.yaml` `b6a11078…`,
  `governance/policy.yaml` `0463acbe…`,
  `governance/baselines/coverage-total.json` `74517039…`,
  `governance/generated/mutation-manifest.json` `04bf135a…`.
- CI real al corte: `commit-gates` FAILURE (run `35130458372`). Causa medida en
  el log remoto: `wct integrity check` exit 1 (drift pre-bless G-META-1; lista
  de rutas nuevas protegidas) y los pasos posteriores no corren.

## 2. Reconciliación de la puerta de mutación de fuentes

### 2.1 Contradicción y obligación

El acta `ACTA-DECISIONES-FINALES-Y-QACCMUT-2026-09-16.md` aprobó la puerta
previa (verifier `APROBAR-Q-ACCMUT`) y ejecutó Q-ACCMUT (47/47), pero su §5 y
§10 mantienen «G-MUT de fuentes» como pendiente. La obligación que el
procedimiento exige para continuar es **resolver la mutación de fuentes**
(adjudicación), no «ejecutar y pasar el gate G-MUT»:

- `CALIFICACION-AC1.md` §Evidencia pt. 4: «Solo después de resolver mutación de
  fuentes: mutación de aceptación, LCOV nuevo/CRAP, DRY y tier full, en ese
  orden.»
- `PLAN-EJECUTABLE…2026-09-15.md` §2 (fila PRE-BLESS): «Tras mutación de
  fuentes resuelta, seguir CALIFICACION-AC1 §Evidencia: aceptación mutada →
  LCOV/cobertura/CRAP → DRY → full.»
- Plan §9: «mutación de fuentes resuelta → Q-ACCMUT → Q-COVCRAP → Q-DRY →
  Q-FULL PRE-BLESS».
- `AGENTS.md` PROC-004: orden de verificación pesada: mutación → mutación de
  Gherkin → CRAP → DRY.
- `ACTA…` §10: «G-MUT de fuentes en un encargo propio (adjudicación sobre el
  bruto conservado y las excepciones registradas, sin bless), luego Q-COVCRAP →
  Q-DRY → tier full PRE-BLESS»: el paréntesis define el paso como adjudicación.

### 2.2 Cierre adjudicado (hecho)

- Campañas históricas inmutables (ACTA §5): r3 AC1 `497 = 450+47` (log sellado
  `51d99c9b…`, verificado presente y con hash exacto); fase E `27+4`; GS-1
  `280+2`; GS-2 `102+16`; GS-3 `74+34`.
- Los 47 supervivientes r3 están dispuestos: **14 equivalencias** (A1, A2,
  A4–A11, A12, A13, execute__28/29), **16 excepciones humanas puntuales a
  TEST-002** (B1–B5 = 15 IDs y terminate__7; precedente H-01) y **17 defectos
  con regresión permanente** (11 funcionales + A3, A14, terminate__6, C2,
  execute__31/32). `14 + 16 + 17 = 47`; ningún `survived` se convierte en
  `killed` (ACTA §2–§5).
- Alcance diferencial: 928 IDs (649 checks + 279 fixtures, 38 funciones
  portadoras, cuerpos AST idénticos, 0 discrepancias) delimitados fuera del
  incremento por identidad/diff (ACTA §2.4); recalificación postpartición 31
  killed + 0 survived; partición TEST-007 cubierta por controles estructurales
  + recalificación. Hooks decorados cubiertos por comprobación alternativa
  aceptada (ACTA §2.3).
- Verificación previa: verifier de puerta `APROBAR-Q-ACCMUT` (ACTA §7.1) y
  verifier de campaña `APROBAR-QACCMUT-EJECUTADO` (ACTA §8.2); Q-ACCMUT 47
  killed + 0 survived (61 s).

### 2.3 Ejecución del gate (comportamiento y por qué no representa el cierre)

- `tools/wct/gate/mutation.py:22-43`: `gate_mutation` corre `mutmut run` +
  `mutmut results --all true` y clasifica el inventario completo.
  `tools/wct/mutate/verdict.py:122-148`: PASS solo si TODO el inventario está
  `killed` (claim limitado, `verdict.py:46`); FAIL por `survived`/`no tests`;
  ERROR para estados fuera de contrato. No existe representación de
  equivalencias, excepciones, regresiones ni delimitaciones.
- Alcance declarado: `registry_process.py:54` `scope=("src/example",)`;
  `[tool.mutmut] source_paths = ["src/example"]` (pyproject.toml:91-98);
  `docs/gates.md` G-MUT «sobre `src/example`»; tier `full` (`tier_map.py`).
  La vía diferencial (`engine.py::scan`) recorre solo `policy.paths.source =
  [src]`: medido sobre la copia, `manifest: ok` y `changed_functions: 0`.
- Diferencias de alcance gate ↔ PR: la PR cambia 96 archivos (0 en `src/`; 34
  en `tools/`, 12 tests, 2 features, 1 gobernanza, 44 docs, 3 raíz/config). El
  gate no mide el código cambiado; las campañas que sí lo midieron son los
  lotes adjudicados (r3, GS-1/2/3, fase E), no el gate.
- Una corrida bruta sobre las fuentes r3 volvería a reportar como `survived`
  los 14 equivalentes (indetectables por construcción) y los 16 exceptuados
  (diferencia no contratada): el gate solo produce un bruto que requiere
  disposición separada.
- Ejecuciones adicionales evaluadas: el gate `full` (G-MUT) no mide esta PR y
  su turno es PRE-BLESS, posterior a cobertura/CRAP/DRY; una campaña fresca de
  fuentes repetiría un lote cerrado sin invalidante y el plan rechaza campañas
  para cambiar etiquetas (plan §1, GS-2). No hay obligación ejecutable previa
  pendiente.

### 2.4 Dictamen de la puerta y verifier

Resultado: **1. PUERTA-CONFORME-POR-CIERRE-ADJUDICADO**. El verifier
independiente (sin escritura, ≤ ~15 s de re-ejecución) emitió **APROBAR CON
RESERVAS NO BLOQUEANTES**: confirmó la obligación documental, el alcance del
gate y su incapacidad de representar adjudicaciones, las 47 disposiciones y
`14+16+17=47`, el ancla del log r3 y la ausencia de ejecución obligatoria
previa; no declaró G-MUT PASS. Reservas atendidas: (a) esta calificación es el
acto que cierra el paso §10 del acta; (b) corregida la imprecisión «resto
docs» (3 archivos no-doc). Informe preservado en
`build/tmp/calificacion-ac1-covcrapdry-20260916/VEREDICTO-VERIFIER-PUERTA.txt`
(evidencia temporal). **«G-MUT no ejecutado (sin PASS)» se conserva como hecho
separado.**

## 3. Cobertura fresca (Q-COV)

### 3.1 Receta, comando y alcance

- Receta canónica (G-COV-TOTAL): `tools/wct/gate/checks_debt.py:45-65` —
  `pytest --cov --cov-branch --cov-report=lcov:build/coverage/lcov.info
  --cov-fail-under <piso> -q -m "not property"`; piso = baseline
  `coverage-total` = **74.5**. Fuentes medidas: `[tool.coverage.run]`
  `source = ["src", "tools/wct"]` (la cobertura canónica **no** se limita a
  `src`). Property excluido por marcador (TEST-008). Base Git de la diferencial:
  `origin/main` = `932c835a…` (validada contra remoto).
- Ejecución en la copia aislada, comando exacto y tiempos en `COMMANDS.txt`;
  la ruta fija `build/coverage/lcov.info` se usó **solo** dentro de la copia y
  su hash se acreditó. No se sustituyó el LCOV de ningún worktree compartido.
- Intento 1 (registrado como **inválido, ambiental**): sin `$VENV/bin` en
  `PATH`, los subprocesos no hallaron `ruff`/`detect-secrets`/`semgrep` y el
  `which` real no vio `pytest` → 6 failed, 656 passed, 28 skipped, 51.4 s. No
  es fallo de producto. Intento 2 (válido) con `PATH` corregido.

### 3.2 Resultados

| Verificación | Resultado |
|---|---|
| Suite (alcance declarado) | **690 passed, 0 failed, 0 skipped, 1 deselected** (property), exit 0, 147.52 s (`coverage-pytest-attempt2.log`) |
| Cobertura total (coverage.py combinada, branch mode) | **87.99%** ≥ piso 74.5, exit 0 |
| Líneas (LCOV) | 3526/3940 = **89.49%** |
| Ramas (LCOV, BRF/BRH) | 1074/1288 = **83.39%** (padre informativo; no sustituye el total combinado ni el gate de diff) |
| Cobertura diferencial (diff-cover canónico) | **91%** (1169 líneas, 96 missing) ≥ 90, exit 0 (`diff-cover.log`) |
| Ratchet total (`wct ratchet check --require coverage-total,docstring-coverage`) | **2 de 2 exigibles**, exit 0 (`ratchet-coverage.log`) |

Artefactos (copia): `build/coverage/lcov.info` sha256
`d14dd3ae99ba8f6c0bb0dd3625ba5989d22803db13ee7eafb2edd365b66d6ddd`;
`.coverage` sha256 `b06aa273a9c07df3e7fab9682771cb12ebbeb1546d072ef89aaf02562f5f46fe`;
logs y manifiesto en
`build/tmp/calificacion-ac1-covcrapdry-20260916/` (24 entradas,
`manifest-evidencia.sha256`, sin auto-hash).

Archivos trasladados de la partición: frente a `origin/main` aparecen como
**archivos nuevos** y el cálculo diferencial mide todas sus líneas
(`checks_debt/checks_quality/checks_scanners`, `registry_*`, `runner_*`,
`fixtures_*` presentes en la salida de diff-cover; su cobertura arrastra el
total al 91%, aún sobre el umbral). Las fachadas (`checks.py`, `runner.py`,
`fixtures_tools.py`) salen al 100%.

### 3.3 Verificación independiente

El verifier independiente **APROBÓ** la cobertura: recomputó de forma
independiente `87.99%` total (`4600/5228`), `89.49%` líneas y `83.39%` ramas
desde el LCOV; confirmó los hashes, re-ejecutó diff-cover (salida idéntica,
exit 0) y el ratchet; confirmó que el intento 1 es ambiental (6 fallos
recuperados con `PATH`; 656+6+28=690). Sin omisiones silenciosas: 1 deselected
= property; 0 skips en la corrida válida; `__main__.py` fuera de cobertura por
configuración y sin cambios.

## 4. CRAP (Q-CRAP)

### 4.1 Receta, alcance y advertencia de cobertura de receta

- Canónica (G-CRAP): `tools/wct/gate/checks_debt.py:88-104` —
  `crap4py src --lcov build/coverage/lcov.info --max-crap <crap.changed_max>`;
  umbral vigente **6** (`governance/thresholds.yaml:22`; perfil `strict` = 6).
  La receta canónica **no cubre `tools/wct`** (scope registrado `("src",)`),
  igual que el hueco de alcance ya documentado para G-MUT-SITES en el plan §4.
  Como la PR no toca `src/`, el PASS canónico es **trivial y no evidencia
  limpieza del código nuevo**: se reporta separado de la medición
  suplementaria no invasiva con la **misma LCOV fresca**.
- Consumo: exclusivamente la LCOV recién producida para `b212f30`; sin
  excepciones nuevas ni cambios de baseline.

### 4.2 Resultados

| Medición | Comando | Resultado |
|---|---|---|
| Canónica | `crap4py src --lcov … --max-crap 6` | exit 0; 9 funciones; máx. 3.0 (`crap-canonical-src.log`) |
| Suplementaria (alcance real de la PR) | `crap4py tools/wct --lcov … --max-crap 6` | **exit 1**; 397 funciones; **69 con CRAP>6** (`crap-supplementary-tools.log`, `crap-violations.txt`) |

Clasificación de las 69 por fingerprint AST contra `origin/main` (script de
lectura; `crap-classification.txt`): **3 nuevas en alcance**, 9 trasladadas
(cuerpo idéntico en `checks.py`/`runner.py` base), 56 preexistentes (53 en
archivos no tocados + 3 en archivo tocado con cuerpo idéntico: `gate_meta_rules`,
`run_tier`, `gate_mutation_sites`), 1 anidada preexistente (`_cycles.walk`).
**0 modificadas.** Inventario: 397 funciones evaluadas; 6 de los 34 archivos
`tools/` cambiados no figuran en el log por tener 0 `def` (fachadas y datos de
módulo: `pipeline.py`, `checks.py`, `registry_process.py`, `registry_static.py`,
`tier_map.py`, `fixtures_tools.py`); `tools/wct/__main__.py` excluido por
`[tool.coverage.run] omit` y fuera del diff.

### 4.3 Incumplimiento en alcance nuevo (hallazgo)

| Archivo | Función | CC | Cobertura | CRAP | Causa dominante |
|---|---|---|---|---|---|
| `tools/wct/gate/semgrep_scope.py` | `_python_files` | 7 | 90.0% | **7.0** | **Complejidad**: con CC=7 el CRAP mínimo es 7.0 aun con cobertura 100%; la cobertura (90%) solo agrava |
| `tools/wct/gate/semgrep_scope.py` | `_build_dirs` | 7 | 100.0% | **7.0** | **Complejidad**: CRAP mínimo = CC = 7 > 6; los tests no pueden bajarlo |
| `tools/wct/accept/process.py` | `_execute` | 6 | 87.5% | **6.1** | **Cobertura**: con CC=6 y 100% daría 6.0; falta rama (`BRDA` línea 72, retorno al bucle en `finally`, `taken=0`) |

Los tres cuerpos **no existen en `origin/main`** (archivos nuevos de la PR;
verificado con `git cat-file` y fingerprint global). Detalle de cobertura y
ramas en `crap-detail-in-scope.txt` y `crap-branches-in-scope.txt`.

**Conclusión CRAP: INCUMPLE en el alcance nuevo de la PR.** No se parten
funciones ni se añaden tests en este encargo. El verifier independiente
**APROBÓ el hallazgo** y confirmó que 0 violaciones fuera de alcance están en
cuerpo modificado. Propuesta mínima de reparación para un encargo propio (no
implementada): reducir CC de `_python_files` y `_build_dirs` (extraer el filtro
de exclusión de `builds`/`_IGNORED_PARTS` a ayudantes pequeños) y cubrir la
rama no tomada de `_execute` (o extraer el cierre de streams), manteniendo
comportamiento e imports, con TDD (TEST-001) y la verificación de STYLE-003.

## 5. DRY (Q-DRY)

**NO EJECUTADO.** Con CRAP incumplido en alcance nuevo, el orden vigente
(PROC-004; plan §2/§9) prohíbe continuar: 0 s de los 600 s. `jscpd` 5.0.16
estaba disponible y no se invocó; no se ejecutó `wct dry`, `wct dry
--normalized` ni `jscpd`. No hay hallazgos DRY que reportar ni receta
alternativa que presentar como canónica.

## 6. Presupuestos

| Fase | Consumo | Tope |
|---|---|---|
| Reconciliación de la puerta | comprobaciones ejecutables no mutantes propias ≈30 s + verifier de puerta ≈15 s | 120 s |
| Cobertura | 51.4 s (intento inválido) + 1.3 s (colección) + 147.5 s (válido) + ≈5 s herramientas + verifier de mediciones (recálculo y re-ejecuciones acotadas) ≈40 s | 600 s |
| CRAP | 0.04 s + 1.6 s (herramientas) + ≈5 s clasificación + verifier (re-ejecuciones) ≈15 s | 600 s |
| DRY | **0 s** (no iniciado por parada expresa) | 600 s |

Sin transferencias entre fases ni ampliaciones automáticas. Sin fallos
instrumentales en las mediciones acreditadas.

## 7. Verificación documental del incremento y CI

- `git diff --check`: limpio.
- Fast (`UV_NO_SYNC=1 uv run wct gate --tier fast`): resultado en §7.1.
- Integridad (`wct integrity check`): exit 1, drift **recalculado 37 = 7
  modificadas + 30 nuevas** (no se asume el número: medido; idéntico al acta,
  sin rutas nuevas por este incremento documental). G-META-1 sigue siendo el
  rojo pre-bless conocido; no se ejecutó bless. Log: `integrity-final.txt`.
- CI remoto al corte: `commit-gates` FAILURE (run `35130458372`) por el mismo
  drift pre-bless; `doctor` y pasos posteriores no corren. El push de este
  registro dispara una corrida nueva con el mismo rojo esperado.
- No se ejecutó tier `full`, G-MUT, bless/update-manifest, merge, bump/lock,
  tag, release ni declaración de cierre integral AC1/beta.3.

### 7.1 Resultado de las comprobaciones

| Verificación | Resultado |
|---|---|
| `git diff --check` | Limpio |
| Fast (corrida final, tras la publicación documental) | **7/7 PASS** (G-META-2, G-RULES-DRIFT, G-SUPPRESS, G-DEBT, G-LINT, G-FMT, G-TYPE), exit 0 |
| Integridad | exit 1; drift medido **37 = 7 + 30**, sin rutas nuevas de este incremento |
| Colección | No re-ejecutada pesada: el incremento no toca tests ni producto (la suite medida es la del candidato) |

## 8. Publicación, límites y próxima acción mínima

- Cambio versionado de este encargo: este registro y las filas afectadas de
  `MATRIZ-DECISIONES-AC1-PENDIENTES-2026-09-13.md` (E8/E9). Nada más. El
  resultado FAIL de CRAP se publica **como evidencia revisada**, no como
  implementación ni como puerta aprobada.
- No ratifica equivalencias ni excepciones nuevas; no ejecuta campañas de
  fuentes, mutmut, Q-ACCMUT (evidencia histórica válida mientras no cambien
  sus inputs), ni los 928 IDs; no modifica gobernanza, baselines, manifests,
  lock ni versión; no bendice, no hace merge, bump, tag ni release.
- **Próxima acción mínima**: decisión humana sobre el hallazgo CRAP — (a)
  autorizar un encargo de reparación acotada de las 3 funciones (reducir CC de
  `_python_files`/`_build_dirs` y cubrir la rama de `_execute`) con TDD y
  repetir CRAP, o (b) disponer explícitamente el límite mediante el mecanismo
  humano que corresponda (con precedente H-01), sin editar umbrales ni
  baselines. Después: DRY → tier full PRE-BLESS → revisión protegida → bless.
  Nada de esto se autoriza aquí.
