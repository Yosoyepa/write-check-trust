# Oleada técnica de cierre AC1 (2026-09-15)

Registro consolidado de la oleada autorizada por el encargo «ejecutar la
siguiente oleada técnica de cierre AC1 de la PR #53». Cubre los frentes A
(comprobaciones r3), B (despacho REGISTRY), C (aceptación: dos Outlines y
selectores numéricos) y D (diseño de partición TEST-007, solo lectura). Este
documento **no** acredita AC1, no cierra beta.3, no bendice, no actualiza
manifiestos, no hace merge, bump, tag ni release. No ratifica equivalencias:
las decisiones humanas históricas conservan exclusivamente su ámbito.

Convención de salida incremental elegida por el encargo: `1.0.0b3.dev1`
(objetivo futuro). **No se modificó ninguna versión, lock ni tag.**

Corte de lectura y publicación base:
`88f6bca8a56edce91a759b70ecf82967dc628805`, rama
`codex/beta3-ac1-r2-integration`, PR #53 OPEN. El remoto no había avanzado
respecto al corte indicado en el preflight.

## 1. Preflight e identidades

Comprobado en el worktree `build/tmp/beta3-ac1-r2-integration`:

- HEAD `88f6bca8a56edce91a759b70ecf82967dc628805`; rama
  `codex/beta3-ac1-r2-integration`; remoto `origin` =
  `https://github.com/Yosoyepa/write-check-trust.git`; rama remota idéntica
  al corte; PR #53 OPEN y `MERGEABLE` con `headRefOid` = corte.
- Índice vacío al iniciar; único untracked el documento ajeno
  `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md`, conservado fuera
  del incremento (ni leído para integrar, ni copiado, ni stageado).
- Runtime del worktree: Python 3.13.14; pytest 9.1.1; pytest-bdd 8.1.0;
  pytest-cov 7.1.0; mutmut 3.7.0; semgrep 1.174.0; ruff 0.16.4; mypy 2.3.1;
  coverage 7.15.4. No se instaló ni sincronizó el runtime compartido.
  El expediente histórico `build/tmp/ac1-r2-qualification/` se usó en modo
  lectura; `evidence/mutation-code-lot-r3-survivor-diffs.log` verifica
  sha256 `51d99c9bdb45679dbed1300f2959bfb96ee27f0178cb5d48a669bf634c204b21`.
- Hashes vigentes de las fuentes r3: `process.py` `84b9340f…`, `campaign.py`
  `686070cd…`, `pytest_receipt.py` `d4f136ae…` (coinciden con el anclaje del
  plan §3).
- Copias de trabajo: matrices y controles en `git worktree` temporales bajo
  `build/tmp/oleada-ac1-cierre-20260915/` (raíces Git propias, retiradas al
  terminar); logs y summary en el mismo expediente. Los `probe_*.py` son
  temporales y **no** forman parte del incremento publicado.

## 2. Frente A — comprobaciones r3

Allowlist permanente respetada: solo `tests/unit/test_accept_campaign.py`.
Los cuatro casos, los siete límites y los hooks se comprobaron en copias
aisladas con activación acreditada. La activación se acreditó con un canario
ejecutado en **el mismo proceso** que las pruebas: resuelve el módulo
`tools.wct.accept.process` desde la raíz de la copia, comprueba su sha256 y
un marcador textual de la mutación. Resultado `rc`, fase y causa por ID:

### 2.1 Cuatro casos de equivalencia cuestionados

| ID | Entrada de la comprobación | Resultado (variante) | Clasificación |
|---|---|---|---|
| `process.x__execute__mutmut_30` (A3) | Hijo propio vivo, salida parcial, selector real que falla en la 2.ª consulta | **rc=1**: el guard invertido del `finally` deja al hijo sin recolectar (la aserción `ChildProcessError` falla) | Defecto del mutante bajo contrato aprobado (recolección/captura); regresión permanente añadida |
| `process.x__read__mutmut_12` (A12) | Hijo real de 1 MiB + 1 con dos streams; causa, límite combinado y plazo propagados a `run_process` | rc=0: sin divergencia observable (logs exactos de 1 MiB, `output limit exceeded`, SIGKILL). La petición de 65537 no puede servirse por un pipe (máximo 65536) | Sin contraejemplo en esta entrada; **no** se ratifica equivalencia |
| `process.x__read__mutmut_14` (A13) | `_read` directo con buffers controlados en remaining 0, 1 y 65534 y excedente disponible | rc=0: sin divergencia observable; ambos capan en 1 MiB y marcan exceso | Sin contraejemplo; **no** se ratifica |
| `process.x__read__mutmut_17` (A14) | EOF de un stream antes de otro legible en la misma selección, reloj en el plazo, orden inverso como control | **rc=1**: el `break` pierde la captura parcial del segundo stream (`late-data` ausente); el control en orden inverso la conserva en ambos | Defecto del mutante de re-selección; artefacto temporal, pendiente de dictamen |

### 2.2 Siete limitaciones instrumentales

| ID | Entrada | Resultado (variante) | Clasificación |
|---|---|---|---|
| `process.x__execute__mutmut_28` | Doble de proceso con reloj controlado; espera tras hijo ya recolectado por `_terminate` | rc=0: sin divergencia en el flujo alcanzable | `None` no observable aquí; decisión de contrato pendiente |
| `process.x__execute__mutmut_29` | Ídem con `wait(2)` | rc=0 | `2` acotado; decisión pendiente |
| `process.x__terminate__mutmut_6` | Doble con recolección modelada a 1,5 s y reloj controlado | **rc=1**: `wait(None)` consume 3600 s simulados (sin cota, viola terminación acotada) | Defecto de la variante `None`; sonda temporal |
| `process.x__terminate__mutmut_7` | Ídem con `wait(2)` | rc=0: 1,5 s simulados, cota mantenida | Sin contraejemplo; decisión pendiente del límite exacto |
| `process.x__observe__mutmut_33` | Reloj exactamente en el deadline y salida lista | **rc=1**: original `>=` devuelve `timeout` antes de otra lectura (frontera inclusiva propuesta); el mutante `>` lee y devuelve `""` | Divergencia en la frontera; aclaración contractual pendiente |
| `process.x__execute__mutmut_31` | Fallo de observación con hijo vivo y streams abiertos | **rc=1**: `_terminate(None)` rompe la limpieza (`AttributeError`) | Defecto del mutante; regresión permanente añadida |
| `process.x__execute__mutmut_32` | Ídem | **rc=1**: streams nunca cerrados (`if stream is None`) | Defecto del mutante; regresión permanente añadida |

Regresión permanente incorporada (contratos aprobados de limpieza y captura
parcial del CONTRATO-AC1):
`tests/unit/test_accept_campaign.py::test_failed_observation_reports_reaps_and_closes_live_child`.
Observa reaping real con `os.waitpid` sobre un hijo propio, captura parcial
en pipes reales, cierre de ambos streams y causa reportada; no hay aserción
de mock. Original verde; mata m30, m31 y m32 en copias aisladas.

### 2.3 Hooks no instrumentados por mutmut

Receta corregida del plan §3-D, en
`build/tmp/ac1-r2-qualification/r3-hook-alternative/` (control, HOOK-MR-01,
HOOK-SF-01). El canario de plugin (raíz + sha256 del módulo cargado) pasa en
las tres corridas. No se inventó ningún `killed` de mutmut: es una
comprobación alternativa por comportamiento contractual.

| Corrida | pytest | recibo | caso | evento call | `validate_receipt` |
|---|---|---|---|---|---|
| Control | exit 1 | exit 1 | mismatch | mismatch | `("mismatch", "semantic mismatch")` — control correcto de rechazo |
| HOOK-MR-01 (call mismatch→pass) | exit 1 | exit 1 | pass | pass | `invalid` por contradicción status/exit (no `status:error`) |
| HOOK-SF-01 (`document["exit"]=0`) | exit 1 | exit 0 | mismatch | mismatch | `invalid` por exit discordante |

### 2.4 Presupuestos A consumidos

Matriz completa (12 variantes + original): 9,8 s la primera pasada y 9,5 s
la reejecución del verifier; sondas originales directas 0,3 s. Hooks: tres
corridas ~1,9 s (autor) y 2,1 s (verifier). Muy por debajo de los topes de
300 s (cuatro casos), 300 s (siete límites) y 120 s (hooks), sin ampliarlos.
Las cifras incluyen los intentos documentados en los logs.

## 3. Frente B — despacho real REGISTRY (PX-REG)

Allowlist respetada: solo `tests/unit/test_sast_targets.py`.

Prueba añadida:
`test_dispatch_registry_observa_fuente_completa_y_omision_total`. Invoca la
entrada real `REGISTRY["G-SAST-SEMGREP"]` (sin sustituir REGISTRY) sobre una
raíz Git propia con política `paths.source: [src]` que exige `src/a.py` y
reutiliza `_raiz_git_con_politica`, `_instrumento_controlado` y `_payload`:

- `scanned=["src/a.py"]`, exit 0, sin hallazgos → PASS, `gate_id` exacto,
  resumen `1 fuentes analizadas, 0 hallazgos`, comando literal.
- `scanned=[]`, exit 0, sin hallazgos → ERROR, `gate_id` exacto, resumen
  `0 de 1 fuentes` y detalle `omitida: src/a.py`.

Controles de sensibilidad en copias aisladas (worktrees temporales):

| Control | Resultado | Fase del fallo |
|---|---|---|
| Reposición del despacho antiguo `external(...)` | rc=1 | aserción de estado en el **caso de omisión** (`Status.ERROR` esperado, recibido PASS) |
| Entrada que retorna PASS constante | rc=1 | aserción de estado en el **caso de omisión** |

El orden de la prueba se dispuso con la omisión primero para que ambos
controles fallen exactamente en el caso de omisión, como exige el encargo;
el original es verde y conserva ambas aserciones. No es una prueba CLI
end-to-end ni sustituye a las puertas finales. Presupuesto focal: 8,2 s
(autor) + 10,0 s (verifier) + 1,9 s (controles) ≪ 120 s.

## 4. Frente C — aceptación: diseño exacto preparado y BLOQUEADO

### 4.1 Trabajo realizado y revertido

Se implementó en el árbol de integración el diseño exacto aprobado
(primer Outline de cinco filas de baseline sana y segundo Outline de aborto
con siete campos, selectores numéricos, `_modes`/`_verdict` por códigos,
paso «no se crea ningun intento mutante», prueba parametrizada de
independencia del aborto para los cinco modos válidos, controles de
inventario, canario 48→47). Fase TDD documentada: 12 fallos conductuales
(ninguno por import) y 49 pruebas verdes tras implementar.

El diseño literal aprobado hace fallar **G-ACCEPT** con exactamente 3
hallazgos `placeholder-variant` en las líneas 17, 18 y 19 de
`features/wct-acceptance-evidence-001.feature`: los pasos `When/Then/And`
del Outline de aborto son idénticos (normalizados) a los del Outline
primario y `ir_dry` los marca como repetición estructural. El resto de
features del repositorio da 0 hallazgos y el árbol sin el cambio da PASS:
el fallo es **nuevo** y reproducible. El `commit` tier quedaría rojo por un
gate no autorizado a quedar rojo en esta oleada (solo G-META-1 podía).

Conforme al encargo («documenta el contraejemplo y detén esa parte: no
cambies silenciosamente… para conseguir un PASS»), el frente C **no se
publica**. El candidato exacto quedó preservado como parche y evidencia:

- `build/tmp/oleada-ac1-cierre-20260915/c-candidate/frente-c-exacto.patch`
  (sha256 `497cd9cf328711d7c0cf69cd99db7c2f83a0533455dfa5f48a5157636be9c4c3`)
- `…/c-green.log` (49 passed) y `…/g-accept-counterexample.log` (3 findings)
- Los tres archivos del frente volvieron a su versión de HEAD.

### 4.2 Trazabilidad 48→47 ya preparada (para la decisión pendiente)

El inventario histórico 48 = 6 filas × 8 campos permanece intacto y trazado
al nuevo: la primera Outline recibe las filas 1 y 3–6 (40 celdas);
la segunda recibe 7 campos de la fila 2; la celda fila 2/mutación pasa a la
configuración fija `mismatch` con la prueba de independencia de los cinco
modos válidos. Total 40+7 = 47 celdas, sin eliminar ningún ID histórico ni
trasladar resultados. No se declara 47/47 killed por construcción.

### 4.3 Decisión humana mínima solicitada

Para desbloquear C se requiere aprobar **una** de estas alternativas
(ninguna se aplicó):

1. **Recomendada — reformular los tres pasos compartidos del Outline de
   aborto** conservando escenario, siete campos, selectores y semántica:
   - `When ejecuto la campana abortada con "<planned>" mutacion`
   - `Then el veredicto del aborto es "<verdict>" con "<killed>" killed y "<errors>" errores`
   - `And tras el aborto quedan "<survived>" supervivientes y "<not_run>" sin ejecutar`
   El parche exacto se recompone sobre `frente-c-exacto.patch` con estos
   literales y `campaign_steps.py` reconoce las tres formas nuevas.
2. Mantener el literal aprobado y aceptar G-ACCEPT en rojo: incompatible con
   el tier commit y con «ningún fallo nuevo».
3. Reunificar el aborto en el Outline primario con una columna explícita:
   se aleja del diseño aprobado («sin parámetro mutation inoperante»).

## 5. Frente D — diseño de partición TEST-007 (solo lectura)

No se particionó ni se tocó ningún archivo. Los 928 IDs no seleccionados
siguen **sin ejecución y sin veredicto**: no se ejecutan, excluyen ni
declaran equivalentes en esta oleada.

### 5.1 Métrica productiva actual (medida con `wct split-plan --json`)

| Archivo | Sitios totales | A nivel de módulo | Funciones |
|---|---|---|---|
| `tools/wct/gate/checks.py` | 258 | 8 | 250 (partes de 98 + 100 + 52) |
| `tools/wct/gate/runner.py` | 442 | **264** | 178 (partes de 71 + 93 + 14) |
| `tools/wct/selftest/fixtures_tools.py` | 191 | 40 | 151 (partes de 99 + 52) |

Desglose del bucket de módulo de `runner.py`: `REGISTRY` literal (L353) 176;
`REGISTRY.update` (L446) 23; `TIERS` (L486) 30; `_COMMIT_GATES` (L459) 21;
`SECRET_PATHS` (L252) 9; `MANIFEST_DIAGNOSTICS` (L162) 4; docstring 1.
Mover solo funciones **no** basta (264 sitios de datos en la fachada).

### 5.2 Submódulos propuestos y responsabilidad

| Submódulo propuesto | Contenido | Sitios |
|---|---|---|
| `gate/registry_static.py` | Entradas G-META-1…G-LCOM del `REGISTRY` (config y analizadores estáticos) | 98 |
| `gate/registry_process.py` | Entradas G-WIRE…G-REDTEAM (procesos externos y artefactos) | 78 |
| `gate/registry_derived.py` | Función `derived(registry)` con las 8 entradas del `update` (alias/compuestos) | 23 (bucket de función) |
| `gate/tier_map.py` | `_COMMIT_GATES` + `TIERS` + `run_tier` | 65 |
| `gate/runner_support.py` | `dynamic`, `external`, `alias` (trampolines de construcción) | 22 |
| `gate/runner_external.py` | `gate_coverage_diff`, `gate_audit`, `_audited_secrets` | 66 |
| `gate/runner_secrets.py` | `gate_secrets`, `gate_docstrings` + `SECRET_PATHS` | 46 + 9 |
| `gate/runner_static.py` | `gate_meta_rules`, `gate_mutation_sites` + `MANIFEST_DIAGNOSTICS` | 30 + 4 |
| `gate/checks_debt.py` | `_result`, `gate_meta_integrity`, `gate_rules_drift`, `gate_suppressions`, `gate_debt`, comandos de cobertura/complejidad | 98 |
| `gate/checks_scanners.py` | `gate_archmetrics`, `gate_dry`, `gate_introvert`, `gate_accept`, `gate_size`, `gate_cognitive` | 100 |
| `gate/checks_quality.py` | `gate_wire`, `gate_lcom`, `gate_dry_tpl` | 52 |
| `selftest/fixtures_governance.py` | `mutmut_pyproject`, `_plant`, `_vulture_governance`, `_arch_tree`, secretos, `_git_track`, `_git_base`, `f1_b`, `f11_a/b` | 99 |
| `selftest/fixtures_adversarial.py` | `f6_a`, `f9_a`, `f10_a/b`, `f12_a/b`, `f2_a`, `_mutation_adversary(.plant)`, `f4_b` | 52 |

`runner.py` queda como fachada que re-exporta: `REGISTRY`, `TIERS`,
`run_tier`, `Gate`, `dynamic`, `external`, `alias`, `gate_meta_rules`,
`gate_coverage_diff`, `gate_mutation_sites`, `gate_audit`, `gate_secrets`,
`gate_docstrings` y `gate_*` importados de `checks_*`. `checks.py` y
`fixtures_tools.py` quedan como fachadas que re-exportan sus grupos.

### 5.3 Dependencias, ciclos y dato REGISTRY

- `registry_static` y `registry_process` importan solo `capabilities`
  (`declares`/`stamped`), `model` y los gates ya extraídos; no importan la
  fachada. `registry_derived.derived(registry)` recibe el mapa base como
  argumento, de modo que los alias no necesitan importar la fachada ni crear
  ciclos. `tier_map` no importa `REGISTRY`. La fachada importa datos y
  funciones; nadie importa la fachada desde dentro del paquete salvo
  `runner`→`tier_map` para `run_tier`.
- El dato `REGISTRY` no se duplica: `runner.py` compone
  `REGISTRY = {**registry_static.REGISTRY, **registry_process.REGISTRY,
  **registry_derived.derived(base)}` (sin claves literales nuevas, ~0
  sitios). `TIERS` se importa de `tier_map`. `REGISTRY` y `TIERS` siguen
  accesibles desde `tools.wct.gate.runner` para CLI, gates y tests.

### 5.4 Obstáculo real detectado: parches por ruta de módulo

Diez archivos de test parchean atributos por ruta
`tools.wct.gate.runner.shutil.which` y/o
`tools.wct.gate.runner.subprocess.run` (`test_gate_commands.py`,
`test_gate_tiers.py`, `test_gate_secrets.py`, `test_gate_drytok.py`,
`test_gate_docstrings.py`, `test_gate_coverage_total.py`,
`test_gate_config_wiring.py`, `test_gate_mutation.py` y los que dependen de
`REGISTRY`). Mover las funciones que usan `shutil`/`subprocess` cambia su
espacio de nombres global y **rompe esos parches**: los tests dejarían de
`tools.wct.gate.runner.shutil.which` para interceptar la nueva ubicación.
Consecuencias y variantes:

- **Variante A (objetivo ≤100 por archivo, fiel al plan):** mover también
  esas funciones; exige ampliar la allowlist a los tests que migran sus
  rutas de parche. Rompe la promesa «tests intactos».
- **Variante B (fachada conserva las funciones parcheadas):** la fachada
  quedaría con ~178 sitios de función (>100) aunque sin funciones cambiadas;
  G-MUT-SITES no bloquearía (el límite solo aplica con funciones cambiadas
  vs manifest), pero incumple el objetivo declarado de ≤100 por archivo.
  No se concede excepción: es decisión humana.

### 5.5 Allowlist exacta del eventual incremento (propuesta, no ejecutada)

- Fase 1 (datos, sin tocar tests):
  `tools/wct/gate/runner.py`, `tools/wct/gate/registry_static.py`,
  `tools/wct/gate/registry_process.py`, `tools/wct/gate/registry_derived.py`,
  `tools/wct/gate/tier_map.py`.
- Fase 2 (funciones): las rutas nuevas de 5.2 y, si se elige la variante A,
  los tests con parches por ruta más `tests/unit/test_sast_targets.py` (import
  público vía fachada, sin cambio) — allowlist a ratificar antes de editar.
- Fase 3 (checks/fixtures): `tools/wct/gate/checks.py`,
  `tools/wct/selftest/fixtures_tools.py` y sus nuevos submódulos.

### 5.6 Verificaciones necesarias e impacto en evidencia anterior

- Identidad del traslado: fingerprints sin cambio para funciones no movidas;
  G-MUT-SITES por archivo; imports públicos idénticos (`REGISTRY`, `TIERS`,
  `run_tier`, gates importados); PX-REG reejecutado sobre el árbol nuevo;
  suite normativa, property, fast y commit.
- Impacto: el manifiesto de mutación indexa `archivo::qualname`; al mover
  funciones cambian sus claves y la evidencia histórica de `_declared`
  (11 IDs) y `f9_a` (20 IDs) **no se transfiere automáticamente**. La prueba
  PX-REG (frente B de esta oleada) queda anclada a `runner.py`; si el dato
  `REGISTRY` migra, debe repetirse y conservarse su nueva medición. Las
  ratificaciones GS-1/2/3 de `semgrep*` no dependen de estos archivos, pero
  cualquier cambio de `runner` reabre la verificación de su wiring.
- TEST-007 sigue abierto: este diseño no lo cumple ni lo dispensa.

## 6. Integración y verificación de la composición final

| Verificación | Resultado real |
|---|---|
| Colección completa | **667 tests** (`collect-full.txt`); focales 85 |
| Focales (A+B) | **85 passed** en 11,2 s (autor) y 85 passed en 10,0 s (verifier) |
| Suite normativa (`tests/unit tests/integration -m "not property"`) | **665 passed** en 123,4 s |
| Property separada (`tests/property`) | **1 passed** |
| Ratchets (`wct ratchet check`) | «Todos los ratchets se mantienen.» exit 0 |
| Introvertidos (`wct introvert`) | 407 extroverted / 8 cloistered / 4 questionable / 4 conditional; 0 introvertidos; G-INTROVERT PASS |
| Fast gate (`UV_NO_SYNC=1 uv run wct gate --tier fast`) | **7 PASS**, exit 0 |
| Tier commit sobre el candidato integrado | **20 PASS + G-META-1 FAIL** (2m07s). G-ACCEPT PASS (C revertido) |
| Integridad (`wct integrity check`) | exit 1; drift medido: **23 rutas = 7 modificadas + 16 nuevas** (ninguna nueva por esta oleada: solo tests cambiados) |

G-META-1 sigue rojo por el drift pre-bless acumulado (23 rutas), esperado y
no nuevo; el encargo permite ese rojo pre-bless. No se etiquetó ningún otro
fallo como preexistente: G-FMT se corrigió con `ruff format` sobre el archivo
tocado y el fast quedó verde.

## 7. Dictamen del verifier independiente

Agente distinto del autor, sin escritura sobre producto/tests/evidencia;
logs propios en `build/tmp/oleada-ac1-cierre-20260915/verifier/`.
**Dictamen: APROBAR CON RESERVAS** (verificación independiente con
reejecución total de A —matriz completa—, B, hooks y el contraejemplo de C;
reejecución parcial de gates: fast, integridad, ratchet, G-ACCEPT; tier
commit solo por revisión documental). Confirmó:

- diff acotado a los dos archivos de test (160 inserciones, 0 borrados);
- original verde y cada variante `rc=1` fallando por aserción conductual,
  con canario de activación correcto en todas las corridas;
- ambos controles de B fallando en el caso de omisión;
- hooks idénticos al plan; C: feature byte-idéntica a HEAD y parche aplicado
  en copia temporal produce exactamente 3 hallazgos;
- ninguna excepción instrumental contabilizada como éxito; ninguna
  regresión permanente con original rojo; evidencia del autor intacta.

Reservas aceptadas y registradas: (1) G-META-1 rojo por drift preexistente;
(2) m31 se detecta por la excepción del propio SUT, no por aserción de
valor; (3) m12/m14/m28/m29/m7 no divergen y m17/m6/m33 dependen de sondas
temporales fuera del PR (la sensibilidad permanente descansa en m30–m32);
(4) el artefacto verificado era local y quedó publicado después.

## 8. Evidencia y capas

- Históricos de campaña: `build/tmp/ac1-r2-qualification/` (r3, GS-1/2/3),
  intactos; bruto r3 497 = 450 + 47 sin cambios.
- Sondas de esta oleada: `build/tmp/oleada-ac1-cierre-20260915/r3/`
  (`summary.json` + logs), `…/b-controls/`, `…/probes/` (temporales),
  `build/tmp/ac1-r2-qualification/r3-hook-alternative/`.
- Regresiones permanentes: `tests/unit/test_accept_campaign.py` (A) y
  `tests/unit/test_sast_targets.py` (B), únicas rutas publicadas.
- Equivalencias ratificadas: ninguna nueva en esta oleada.
- Propuestas y pendientes: §4.3 (C) y §5 (D).

## 9. Pendientes humanos reducidos y próximo incremento

Pendientes que esta oleada deja servidos para decisión:

1. **C / Q-DESIGN-ACC**: aprobar la reformulación de los tres pasos del
   Outline de aborto (§4.3, alternativa 1) para desbloquear el diseño ya
   implementado y verificado en copia. Sin ello, el frente queda bloqueado.
2. **A / dictamen de sondas**: decidir por ID A12/A13 (sin contraejemplo en
   las entradas probadas), A14 y C1/C2 (§2) y si alguna merece regresión
   permanente; no ratificar por ausencia de contraejemplo.
3. **D / TEST-007**: elegir variante A o B de §5.4 y ratificar la allowlist
   de §5.5 antes de editar.
4. **Q-ACCMUT**: no ejecutada (requiere autorización y presupuesto propios);
   la campaña de los 928 sigue sin ejecución y sin veredicto.
5. **E9/bless**: G-META-1 rojo pre-bless por 23 rutas protegidas.
6. **E10/versión**: convención `1.0.0b3.dev1` elegida; bump/lock/tag
   pendientes de autorización propia.

Próximo incremento mínimo propuesto: reintroducir el frente C con los
literales de §4.3-1 sobre el parche preservado, verificar focales/colección/
G-ACCEPT/PX-REG y publicar como incremento propio. Allowlist anticipada:
`features/wct-acceptance-evidence-001.feature`,
`tests/acceptance/campaign_steps.py`, `tests/unit/test_accept_campaign.py`.
Criterio de cierre: 49+ pruebas focales verdes, G-ACCEPT 0 hallazgos,
trazabilidad 48→47 explícita, controles negativos de selector desconocido y
Then incorrecto, y sin Q-ACCMUT.

## 10. Límites de esta oleada

No acredita AC1 (mutación de fuentes y cadena E8 pendientes), no cierra
beta.3, no bendice, no actualiza el manifiesto, no hace merge, bump, lock,
tag ni release. No ratifica equivalencias ni dispensa TEST-007. No incorpora
P03a. No ejecuta la campaña de los 928 ni Q-ACCMUT. Los resultados de sonda
no son veredictos de campaña. La PR #53 sigue en borrador.
