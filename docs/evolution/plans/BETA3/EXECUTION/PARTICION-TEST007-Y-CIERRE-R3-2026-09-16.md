# Partición TEST-007 implementada y cierre R3 de A12/A13/C2 (2026-09-16)

Registro sucesor del encargo «implementar la partición TEST-007 por fases,
preservar comportamiento y cerrar las comprobaciones pendientes de A12/A13 y la
regresión C2». Ejecuta la autorización exacta §2: implementación por fases del
diseño §6 de `DISPOSICION-R3-Y-DISENO-PARTICION-2026-09-15.md` dentro de su
allowlist, comprobación de observabilidad final de A12, precisión de A13 y
regresión permanente de C2 con su aclaración contractual. **No** ratifica
equivalencias, no impone `wait=1 s`, no toca gobernanza ni manifests, no ejecuta
Q-ACCMUT ni campañas (los 928 IDs siguen sin ejecución y sin veredicto), no
bendice, no hace merge, bump, lock, tag ni release, no declara cierre integral
AC1/beta.3.

## 1. Identidades y preflight

- HEAD de partida `b27f01e7ee006934d4f246474b06c4afb659ec01` = remoto =
  `headRefOid` de la PR #53 (OPEN). Índice limpio; único untracked el documento
  ajeno `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md`, intacto y fuera
  de todos los incrementos. Runtime `.venv` del worktree (Python 3.13.14),
  invocado con `UV_NO_SYNC=1 uv run`; nada instalado.
- Herramientas acreditadas en el venv: semgrep 1.174.0, detect-secrets,
  diff-cover, interrogate, mypy, ruff, pytest.
- **Baseline de aceptación con entorno completo** (`uv run` pone el bin del
  venv en PATH): normativa 686 passed, **0 fallos, 0 skips**; colección 688 =
  676 unit + 10 integration + 1 property + 1 acceptance; property 1 passed.
  Esta baseline sustituye a la comparación anterior del sandbox, que compartía
  4 fallos ambientales y 28 skips.
- Trampa de procedencia detectada y corregida en preflight: `git show` desde
  un directorio sin `.git` descubre el repo principal (otra rama) y corta desde
  SU HEAD; la cirugía fija `-C <worktree de integración>` explícitamente. La
  primera generación con la fuente equivocada producía un `f9_a` antiguo (sin
  plantado de policy/thresholds ni raíz Git propia) y 3 fallos en
  `test_sast_targets`; corregido antes de tocar el worktree.

## 2. Partición efectuada (fases y commits)

| Fase | Commit | Archivos | Sitios (motor WCT, medidos) |
|---|---|---|---|
| 1 — familia runner | `da2725d` | `runner.py` (fachada) + nuevos `runner_support`, `runner_secrets`, `runner_audit`, `runner_docstrings`, `registry_static`, `registry_process`, `registry_derived`, `tier_map` | 95 / 23 / 47 / 37 / 19 / 96 / 77 / 25 / 52 |
| 2 — familia checks | `3cc1c5a` | `checks.py` (fachada) + nuevos `checks_debt`, `checks_quality`, `checks_scanners` | 23 / 92 / 79 / 89 |
| 3 — familia fixtures | `ff3b7c5` | `fixtures_tools.py` (fachada) + nuevos `fixtures_governance`, `fixtures_git`, `fixtures_adversarial` | 47 / 57 / 48 / 75 |

Los **17 archivos resultantes cumplen ≤100 sitios** (medidos con
`tools.wct.mutate.engine.mutation_sites`, datos y constantes de módulo
incluidos; el listado completo está en §3 del registro de diseño y se re-midió
sobre el árbol final). Verificación por fase en el worktree: fase 1 — 72 passed
en los 11 archivos consumidores de runner, colección 688, fast 7/7; fase 2 —
fachada importable por todos sus consumidores y 52 passed, fast 7/7; fase 3 —
105 passed (redteam + sast + secrets), fast 7/7. **Cero archivos de test en los
tres commits** (`git diff HEAD~3 --name-only -- tests/` vacío al cierre de la
fase 3).

Ajustes respecto del traslado puro, todos documentados y sin cambio de
semántica:
1. `Gate` vive en `runner_support` (los submódulos del registro lo anotan sin
   importar la fachada; cero ciclos) y la fachada lo re-exporta.
2. `Builder` vive en `fixtures_governance` por la misma razón
   (`_mutation_adversary` lo anota).
3. Las entradas `G-META-2`, `G-MUT-SITES` y `G-COV-DIFF` del literal
   `REGISTRY` se componen en la fachada (sus gates residen allí por los parches
   P2; extraerlas crearía un ciclo).
4. Las fachadas usan `__all__` para la reexportación (sin `# noqa`: el
   ratchet de supresiones no crece); los submódulos llevan solo los imports
   que usan (podados con ruff F401, 288 eliminaciones mecánicas).
5. `shutil` y `subprocess` se conservan como superficie de parche de la
   fachada (`runner.shutil.which`, `runner.subprocess.run`); `subprocess` ya
   sin uso local queda documentado en el docstring y `__all__`.

## 3. Mapa de trazabilidad de identidades

Inventario completo con fingerprints por símbolo:
`build/tmp/particion-r3/logs/13-trazabilidad.json` (copia efímera; el resumen
autoritativo es esta tabla). Clasificación:

| Tipo | Cantidad | Detalle |
|---|---|---|
| Traslado mecánico (fingerprint idéntico) | **72** | Todas las funciones y datos de las tres familias (lista por módulo en §3 del registro de diseño): p. ej. `_declared` → `checks_debt.py::_declared`, `f9_a` → `fixtures_adversarial.py::f9_a`, `gate_secrets` → `runner_secrets.py::gate_secrets`, `dynamic`/`external`/`alias` → `runner_support.py`, `TIERS`/`_COMMIT_GATES` → `tier_map.py` |
| División del literal reacomodada | 2 | `REGISTRY` → mitades `registry_static`/`registry_process` (22+14 entradas literales, mismas entradas y valores) + 3 entradas compuestas en la fachada (`G-META-2`, `G-MUT-SITES`, `G-COV-DIFF`) |
| Construcción derivada nueva | 1 | `registry_derived.derived(base)`: las 8 entradas del antiguo `REGISTRY.update` con `REGISTRY[...]`→`base[...]` |
| Reexportación en fachada | 1+ | `Builder` (definido en `fixtures_governance`, reexportado por `fixtures_tools`; `BUILDERS` se queda en la fachada) |

Tipos de cambio NO presentes: ningún cambio conductual, de firma, de comando,
de configuración ni de contrato; `REGISTRY`/`TIERS` no se duplican (47 entradas
= 22+14+8+3; literales idénticas por `is`; `TIERS` mismo objeto). Los qualnames
de mutación cambian de archivo: **la evidencia histórica de `_declared` (11 IDs
ejecutados en fase E) y `f9_a` (20 IDs) NO se transfiere automáticamente** y su
re-ancle exige recalificación sobre el candidato; los 928 permanecen sin
ejecución ni veredicto y no quedan excluidos por el traslado. Propuesta mínima
de recalificación (NO ejecutada): re-ancle de los 31 IDs de fase E sobre los
qualnames nuevos con preflight y presupuesto propio (estimación ≤300 s de
ejecución + revisión), además de re-medir PX-REG (hecho: §5).

## 4. Compatibilidad demostrada tras la partición

- Suite normativa del candidato: **689 passed** (686 de la baseline + 3 casos
  de la regresión C2), 0 fallos; property 1 passed; focales 109 (55
  accept_campaign + 54 sast); colección 691 = 679 unit + 10 integration +
  1 property + 1 acceptance.
- **Controles discriminantes de parches** (falsos que registran): P1 sobre
  `gate_secrets` movida → INTERCEPTA (`runner.shutil.which`/`runner.subprocess.run`
  alcanzan la función en `runner_secrets`); P2 `runner.remote_base` →
  INTERCEPTA el consumidor `gate_coverage_diff` en la fachada; P2′
  `runner.scan_mutations` → INTERCEPTA `gate_mutation_sites` en la fachada;
  P2″ `runner.REGISTRY` → INTERCEPTA `run_tier` (test_gate_preflight verde).
- Despacho REGISTRY (PX-REG, `test_dispatch_registry_observa_fuente_completa_
  y_omision_total`): verde sobre el árbol particionado (21 passed en el lote
  preflight/config_wiring/mutation_gate/PX-REG).
- Ciclos: 0 en `tools/` (grafo de imports verificado tras cada fase).
- mypy estricto: «Success: no issues found in 92 source files» (sandbox
  equivalente y worktree). Ruff check + format con la config del gate: limpios.
- API pública: todos los imports que consumers reales hacen de las tres
  fachadas resuelven (runner: REGISTRY, TIERS, run_tier, gate_coverage_diff,
  gate_mutation, gate_mutation_sites, gate_secrets; checks: 20 nombres;
  fixtures_tools: 5 nombres). El namespace del antiguo monolito arrastraba
  asignaciones internas (p. ej. `json`, `tempfile` en runner) que la partición
  no replica: no son API consumida y se listan como cambio de tipo
  «resolución/imports» en el mapa.

## 5. Frente B — A12: observabilidad final (transporte completo)

Resuelto el ID completo `tools.wct.accept.process.x__read__mutmut_12` (diff
sellado: `min(65536→65537, remaining + 1)`; copia del transporte con sha256
`84b9340f…` y variante que difiere en EXACTAMENTE esa línea). Nueva sonda de
**transporte completo** (`build/tmp/particion-r3/a12-transporte/`, log
`salida.log`): `run_process` real sobre doble de `Popen` con pipes reales del
arnés — stdout con capacidad ampliada por-pipe (`F_SETPIPE_SZ` 131072 en el
extremo de lectura, sin privilegios ni configuración global) y alimentador
guionizado dentro de `select` que entrega hasta `OUTPUT_LIMIT+1` bytes
(1048577); `os.read` real (jamás devuelve más que min(pedido, disponible)).

Resultado (original vs variante, estado final completo):

| Magnitud | Original | Variante m12 |
|---|---|---|
| motivo | `output limit exceeded` | `output limit exceeded` |
| exit | 9 | 9 |
| stdout.log | 1048576 bytes, sha256 `8f990ba0…` | 1048576 bytes, **mismo sha256** |
| stderr.log | 0 bytes | 0 bytes |
| hijo recolectado | sí | sí |

**Lectura**: la divergencia intermedia de una ronda (la variante lee hasta
65537 cuando el original lee 65536) **no alcanza el resultado final**: el byte
de exceso queda en el pipe y el original lo lee en su ronda siguiente,
detectando el mismo excedente un ciclo después — exactamente el mecanismo que
el encargo pedía comprobar («el original leyendo primero 65536 y detectando
después el excedente»). Persistidos, motivo, exit y limpieza coinciden para
todo input con capacidad ampliada; sin capacidad ampliada son deductivamente
idénticos (invariante `disponible ≤ capacidad`, DICTAMEN del cierre C).

**Disposición propuesta (NO ratificada)**: equivalencia del estado persistido
con dominio completo — bytes, exit y limpieza idénticos en toda entrada;
residuo documentado: (i) la variante agota una ronda antes (granularidad de
syscalls, no observable en el reporte); (ii) si el deadline expirara entre la
ronda de señalización de la variante y la ronda siguiente del original —ventana
de un select (0,05 s), realizable solo como carrera temporal con hijos lentos—
el motivo sería `timeout` (original, conforme a la frontera inclusiva C2) frente
a `output limit exceeded` (variante), con bytes idénticos. La ausencia de
`F_SETPIPE_SZ` en el producto NO se invoca como garantía: la sonda usa
capacidad ampliada real y un hijo admisible podría ampliar su propia tubería.
El ID **sigue pendiente de decisión humana**: ratificar la equivalencia del
estado persistido con el residuo (i)-(ii) declarado, o tratar la divergencia de
motivo de la ventana como hueco contractual. No se ratifica aquí.

## 6. Frente B — A13: precisión y contabilidad (nota sucesora)

1. **El conjunto A12–A14/C1–C2 contiene OCHO IDs**, no siete: `x__read__12`
   (A12), `x__read__14` (A13), `x__read__17` (A14), `x__execute__28`,
   `x__execute__29`, `x__terminate__6`, `x__terminate__7` (C1) y
   `x__observe__33` (C2). El registro anterior decía «siete IDs»: corrección.
2. **Precisión de A13** (`x__read__14`: `remaining+1`→`remaining+2`): la
   justificación NO debe afirmar identidad de todo el estado interno. Lo
   preciso: en rondas que NO señalan exceso ambas leen exactamente
   `min(pedido, disponible) = disponible ≤ remaining` y la contabilidad interna
   coincide; la petición mayor solo se materializa en rondas donde
   `disponible > remaining`, y en TODAS ellas ambas variantes retornan el mismo
   motivo (`output limit exceeded`), persisten el mismo `chunk[:remaining]` y
   **la variante consume un byte más de la cola**. Esa diferencia interna
   alcanza solo a bytes que quedan (o se dejan) en una tubería cuyo proceso se
   termina y cuyos streams se cierran en la misma ronda: no alcanza ningún
   resultado público durante terminación, captura o limpieza. Equivalencia
   propuesta con esa observabilidad exacta (estado persistido, motivo y
   limpieza idénticos; consumo interno distinto solo en rondas ya terminales);
   **no ratificada** — decisión humana. La conciliación de la colección se
   conserva: el test generado de aceptación queda fuera de las dos rutas
   normativas; conteos del candidato por identidades en §7.

## 7. Frente C — C2: aclaración contractual y regresión permanente

**Aclaración autorizada y aplicada**: «Cuando el reloj alcanza o supera el
deadline, no comienza otra lectura; prevalece el timeout, conservando los bytes
capturados anteriormente». Documentada aquí y en la matriz; no se editó
gobernanza ni se inventó un contrato más amplio. `wait=1 s` NO queda fijado;
`terminate__7` conserva disposición separada (C).

Regresión permanente en `tests/unit/test_accept_campaign.py` (commit
`aa2ffa9`): `test_deadline_boundary_prevents_a_new_read_and_keeps_captured_bytes`,
parametrizada en tres casos con reloj simulado por ronda y emisión del hijo
modelada dentro del `select` guionado (determinista, sin sleeps de
sincronización; dobles fieles sobre `process_transport.time/selectors/
subprocess`, hijo propio real para killpg y reap real único):

| Caso | Original | Variante real `observe__33` (`>=`→`>`) |
|---|---|---|
| `antes` (check a 0,15 < plazo 0,2) | VERDE: captura early+tarde+mas | VERDE (control: permite leer antes del plazo) |
| `exacto` (check exactamente en 0,2) | VERDE: early+tarde; «mas» no se lee | **ROJO**: `stdout.log == early+tarde+mas` — inicia otra lectura en la frontera (causa contractual prevista) |
| `despues` (check a 0,25 > plazo) | VERDE: early+tarde | VERDE (control: tras el plazo nadie lee, ni el mutante) |

Sensibilidad demostrada contra el mutante REAL (copia del árbol `ff3b7c5` +
un diff sellado; tests byte-idénticos). Sin errores de colección/setup.
Independencia: 3 passed contra `x__read__mutmut_17` y `x__terminate__mutmut_6`.
Se preservan T5, A14, terminate__6 y los bindings del frente C. Log:
`build/tmp/particion-r3/C2-MATRIZ-ROJO-VERDE.md`. Procedimiento de re-ejecución
(reserva R2 del verifier): invocar pytest DESDE el directorio de la copia con
los tests copiados en ella; pasar la ruta externa de tests hace que el conftest
anteponga la raíz del worktree a `sys.path` y produzca un falso verde
(reproducido y descartado por el verifier).

## 8. Verificación final del candidato compuesto

Candidato: `b27f01e` → `da2725d` → `3cc1c5a` → `ff3b7c5` → `aa2ffa9` (+ este
registro). Sobre el worktree:

| Verificación | Resultado |
|---|---|
| `git diff --check` | Limpio |
| Colección completa | **691** = 679 unit + 10 integration + 1 property + 1 acceptance (normativa-ámbito 689 = 679+10; conciliación exacta por identidades, 688 previos + 3 casos C2) |
| Focales (`test_accept_campaign.py` + `test_sast_targets.py`) | **109 passed** |
| Normativa sin property | **689 passed**, 0 fallos, 0 skips |
| Property | **1 passed** |
| G-ACCEPT | **PASS, 0 hallazgos** |
| Ratchets | «Todos los ratchets se mantienen» |
| Introvertidos | 416 extroverted / 5 conditional / 5 questionable / 8 cloistered; **0 introverted** |
| Fast | **7/7 PASS** |
| Tier commit | **20 PASS + G-META-1 FAIL** (único rojo, pre-bless) |
| Sitios de los 17 archivos | todos ≤100 (§2) |
| Ciclos | 0 |
| Parches P1/P2/P2′/P2″ y PX-REG | INTERCEPTAN / verde (§4) |
| Integridad | exit 1; drift medido **37 rutas = 7 modificadas + 30 nuevas**; las 14 nuevas de esta partición (8 gate + 3 checks + 3 fixtures) entran al listado; ningún nombre del incremento fuera de tests/docs figura fuera de ese conjunto |

## 9. Presupuestos

| Frente | Tope | Consumo real |
|---|---|---|
| Sondas A12/A13 y controles C2 (incl. reejecuciones) | 600 s | ~6 s (sonda de transporte 2 corridas ≈1 s; matriz C2: 5 corridas de un test ≈1 s; copias mutantes ≈1 s) |
| Verificación de partición e integración (incl. baseline, sandbox, 3 fases, batería final, intentos inválidos) | 1800 s | ~730 s (baseline 117; sandbox ≈190, incl. la generación invalidada por la fuente Git equivocada; fases ≈115; batería final ≈300) |

Revisión documental (diseño §6, contratos, expedientes) registrada aparte de la
ejecución. Ningún presupuesto ampliado.

## 10. Verifier independiente

Agente distinto del autor, sin escritura sobre producto/tests; informe y
evidencia propios en `build/tmp/particion-r3/verifier/VEREDICTO.md`.
**Dictamen: APROBAR CON RESERVAS** (R1–R4, no bloqueantes). Reejecutó (≈10 s):
cadena de commits (fases sin tests; `aa2ffa9` solo `test_accept_campaign.py`
+134/−0); sitios de 6 archivos (coinciden 1:1 con §2, todos ≤100); REGISTRY 47
= 22+14+8+3 con literales idénticas por `is`, TIERS mismo objeto, `__module__`
correctos; consumers 7/20/5 nombres resuelven; P1/P2/P2′ INTERCEPTAN; P2″ +
PX-REG 21 passed; C2 — copia mut33 con diff sellado exacto (`process.py:41
>=`→`>`), `[exacto]` FAILED por `stdout.log` y antes/despues PASSED,
independencia en mut17/mut6, T5/A14/terminate__6 verdes; sonda A12 m12
re-ejecutada (motivo, exit 9, sha256 `8f990ba0…`); colección 691 = 688+3;
matriz con exactamente 4 filas editadas. Reservas y su atención: R1 (§10
pre-redactada por el autor → reescrita citando el dictamen real); R2
(procedimiento de re-ejecución de mutantes: invocar pytest DESDE la copia con
los tests copiados — el conftest antepone la raíz del worktree si se pasa la
ruta externa y produce un falso verde; registrado en §7); R3 (self-loop
preexistente `tools.wct.adopt` desde `db03e74`, ajeno al candidato); R4
(alcance ya declarado: evidencia de fase E sin transferir, A12/A13 sin
ratificar con residuos, G-META-1 pre-bless con drift 37). Sin discrepancias
entre el registro y la evidencia re-ejecutada.

## 11. Próxima puerta mínima

Recalificación mínima propuesta (requiere autorización propia, no ejecutada):
re-ancle de la evidencia de fase E (11 IDs de `_declared` →
`checks_debt.py::_declared`; 20 IDs de `f9_a` →
`fixtures_adversarial.py::f9_a`) sobre los qualnames nuevos, con preflight y
tope propuesto ≤300 s de ejecución + revisión documental; y revisión humana de
las disposiciones propuestas de A12/A13/C2 (§5–§7). Después, la cadena
pendiente del plan sigue siendo: mutación de fuentes → Q-ACCMUT →
cobertura/CRAP → DRY → full, con G-META-1 pre-bless por el drift de 37 rutas.
