# Recalificación post-partición de `_declared`/`f9_a` y contraejemplo A12 (2026-09-16)

Registro sucesor del encargo «recalificar el alcance trasladado de fase E,
resolver la divergencia observable de A12 y revisar la cobertura del cambio
estructural de TEST-007». Ejecuta las autorizaciones A/B/C en copias aisladas
bajo `build/tmp/`, con verifier independiente antes y después. **No** ratifica
equivalencias, no cambia producto, tests, gobernanza, umbrales ni manifests, no
ejecuta Q-ACCMUT, campañas de fuentes ni los 928 IDs, no bendice, no hace
merge, bump, lock, tag ni release, y no declara cierre integral AC1/beta.3. El
documento ajeno `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md`
permanece intacto, sin seguimiento y fuera del incremento.

## 1. Identidades, fuentes y preflight

- Worktree `build/tmp/beta3-ac1-r2-integration`, rama
  `codex/beta3-ac1-r2-integration`. HEAD medido
  `91fa10b4bdf5c8c006552939aacd790586435feb` (corte comunicado `91fa10b`),
  idéntico a `origin/codex/beta3-ac1-r2-integration` tras `git fetch` y a
  `headRefOid` de la PR #53 (OPEN, base `main`, mergeable, sin avances
  posteriores). Sin reset, rebase, force push ni sobrescritura de trabajo
  concurrente; el checkout principal no se tocó.
- Índice al iniciar y al cerrar: solo el untracked ajeno citado. Runtime:
  `.venv` del worktree (Python 3.13.14, pytest 9.1.1, mutmut 3.7.0, semgrep
  1.174.0, git 2.55.0), invocado con `UV_NO_SYNC=1` o por ruta; nada
  instalado ni sincronizado. Herramientas, PATH, imports y raíz Git
  acreditados en cada frente (procedencia bajo la copia correcta, no bajo el
  worktree).
- Fuentes históricas resueltas por Git/rg (rutas absolutas):
  `docs/evolution/plans/BETA3/EXECUTION/RECETA-FASE-G-GATE-SELFTEST-2026-09-13.md`
  (principal), `ADJUDICACION-FASE-E-GATE-SELFTEST-2026-09-13.md`,
  `CIERRE-ADJUDICACION-FASE-E-2026-09-13.md` y
  `EJECUCION-INCREMENTO-F9A-LOADCONFIG-2026-09-13.md`; corrida sellada de fase
  E `build/tmp/lot-gate-selftest-fase-e.9TqhTG` (bruto 27 killed + 4 survived,
  intocado) con su runtime histórico `build/tmp/sh-p01-CND-80B8/.venv`;
  registro de partición `docs/.../PARTICION-TEST007-Y-CIERRE-R3-2026-09-16.md`
  publicado en `91fa10b`. Nada se reconstruyó por memoria.
- Drift de integridad re-medido sobre este candidato:
  `wct integrity check` → exit 1, **37 rutas = 7 modificadas + 30 nuevas**
  (no 23: fórmula superada por la medición de la partición); este incremento
  solo añade documentos y no introduce ninguna ruta protegida nueva.

## 2. Frente A — re-anclaje de `_declared` y `f9_a`

ID histórico sin presuponer rutas: mapa de traslado (PARTICION §3) y código
real. Rutas y qualnames vigentes: `tools/wct/gate/checks_debt.py::_declared`
(privada → `x__declared`) y
`tools/wct/selftest/fixtures_adversarial.py::f9_a` (pública → `x_f9_a`).
Cuerpos verificados **byte-idénticos** al corte `fb7f725` (normalizado por
AST: `4adfa15dc88f6479…` y `2e478e811ff4bf6f…`); el único cambio de resolución
es el módulo contenedor.

Copia nueva `build/tmp/recalificacion/frenteA/checkout` (clon `file://` del
worktree + `checkout --detach 91fa10b`), receta acreditada de fase G/E
adaptada a los qualnames nuevos (P3 privado con `only_mutate` de los dos
archivos, `also_copy`, selección `test_gate_config_wiring.py` +
`test_sast_targets.py`, `mutants/` pre-poblado, entorno limpio).

**Preflight (aprobado por verifier antes de la campaña):**

| Control | Resultado |
|---|---|
| Fuentes congeladas (10 rutas + pyproject privado) | sha256 registrados en `frenteA/evidence/fuentes-congeladas.sha256` |
| Baseline focal | **65 passed**, 0 fallos, **0 skips**, 0 xfail, exit 0 (6,69 s) |
| Colección explícita de nodeids | 65 nodeids, exit 0 |
| Generación (copia nueva) | exit 1 con la firma admisible: «2 files mutated, 91 ignored», stats corrida, sin «Running mutation testing» (8,27 s) |
| Inventario completo | **364 IDs** (250 `checks_debt` + 114 `fixtures_adversarial`); 0 IDs fuera de los dos módulos; 0 `x__f9_a` |
| Subconjunto objetivo | **31 IDs** = 11 `checks_debt.x__declared__mutmut_1..11` + 20 `fixtures_adversarial.x_f9_a__mutmut_1..20`, extraídos por identidad (no glob) |
| Inventario independiente de funciones | 31/31 con su lado `-` dentro del cuerpo AST de la función reclamada (`inventario-funciones.json`) |
| Asociaciones | 31/31 no vacías; 150 pares, 12 nodeids únicos, todos colectados |
| Procedencia | `__file__` de ambos módulos bajo `checkout/mutants/…` |
| Activación in-process (canario) | originales verdes; `x__declared__mutmut_2` rojo por `TypeError` en la guarda mutada (checks_debt.py:1194 instrumentado); `x_f9_a__mutmut_10` rojo por `ConfigError` (thresholds.yaml ausente por clave renombrada); sin errores de colección/setup |
| Launcher | bloquea si falta ID, asociación, fuente instrumentada o selección; `--max-children 1`, timeout; sin fallback a la suite completa; post-check 31/31 con veredicto y 333 not-checked (reserva R4 del verifier, atendida) |

El verifier independiente emitió **APROBAR CON RESERVAS (R1–R4, no
bloqueantes)** en `frenteA/verifier/PREFLIGHT-VEREDICTO.md`; re-verificó los
31 pares de correspondencia (33 s), baseline, generación, inventario,
asociaciones, canario y launcher. R1 (pyproject privado con ` M` esperado) y
R2 (manifiesto no `sha256sum -c`) quedaron registrados; R3 (sondas desde
`checkout/mutants`) se aplicó; R4 se atendió con el post-check del launcher.

**Correspondencia con la evidencia histórica** (sin transferir estados): los
31 diffs nuevos y los 31 históricos (`checks.x__declared` /
`fixtures_tools.x_f9_a`, extraídos con `mutmut show` del checkout sellado)
coinciden **31/31 por diff normalizado** (función, operador y ubicación);
0 nuevas, 0 desaparecidas, 0 ambiguas (`correspondencia-31.json`). El
inventario nuevo tiene 31 IDs por identidad comprobada, no por forzar el
conteo histórico.

**Campaña nueva** (serial, IDs explícitos, veredictos frescos; 25 s):
**31 killed + 0 survived + 0 instrumentales**. Reconciler: inventario
pre/post **conjunto-idéntico** (364 = 364); 333 IDs no objetivo permanecen
`not checked`. El bruto histórico E (27+4) y sus sellos permanecen intactos:
la nueva campaña **no** convierte `survived` histórico en `killed`; constata
que en el árbol particionado, con el binding `load_config` vigente, los
cuatro antiguos supervivientes (`x_f9_a__mutmut_10..13`) ahora caen.

**Clasificación causal** (`sondas-campana.tsv`, `probes/`): 31/31 con exit 1
por **fallos de test**, cero secciones `ERRORS`, cero errores instrumentales:

| Causa terminal | IDs |
|---|---|
| `AssertionError` de contrato (FAIL/PASS o literales de comando) | `x__declared_1,4,5,6,7,8,9,10,11`; `x_f9_a_6,7,9,14,15,16,17,18,19` |
| `TypeError` en la guarda mutada (FI1) | `x__declared_2,3` |
| Excepción del plantado retornado (`AttributeError`/`TypeError`) | `x_f9_a_1,2,3,4,5,20` |
| `yaml.scanner.ScannerError` (contenido deformado) | `x_f9_a_8,12` |
| `FileNotFoundError` (clave renombrada) | `x_f9_a_10,11` |
| `tools.wct.config.ConfigError` (`schema_version`) | `x_f9_a_13` |

Se conservan separados: bruto del nuevo lote (`results-campana.txt`,
`mutmut-campana.log`), sondas causales (`sondas-campana.tsv`, `probes/`),
correspondencia histórica (`correspondencia-31.json`) e intento inválido por
defecto propio del arnés (basetemp sin directorio padre; `probes-intento-invalido-1/`),
que no es detección del SUT. **Presupuesto A: ~227 s de 600** (medidos:
colección 0,33 + baseline 6,69 + generación 8,27 + campaña 25 + sondas
válidas 75 + reejecución del verifier 6; preparación, asociaciones y sondas
inválidas estimadas en el resto; verifier de preflight ~50 s).

## 3. Frente B — A12: la ventana del deadline, ejecutada

ID resuelto `tools.wct.accept.process.x__read__mutmut_12`; diff sellado
`min(65536 → 65537, remaining + 1)` en `_read` L23. Original vigente sha256
`84b9340fd16b424a2d778e512166c4419c048001588665a313dcdf9f5d263ef7` (idéntico al
ancla r3 del plan §3); variante con **exactamente una línea** sustituida,
sha256 `a6719695a3a4c7058d3caa782c985fb1d155b00c3d842b097301a7b62fbb80ac`.

La divergencia estaba **deducida** en `PARTICION…` §5 (residuo ii); aquí se
**ejecutó** con transporte completo y reloj controlado por ronda
(`frenteB/sonda_ventana.py`, 4 corridas ≈1 s; evidencia `salida.log`):

| Caso | Original | Variante m12 |
|---|---|---|
| normal (deadline no expira) | `output limit exceeded`, exit 9, stdout 1048576 B sha `8f990ba0…`, stderr 0, hijo recolectado | ídem (convergen; la variante señaliza una ronda antes) |
| **ventana** (deadline expira entre ambas señalizaciones) | **`timeout`**, exit 9, stdout 1048576 B sha `8f990ba0…`, stderr 0, hijo recolectado | **`output limit exceeded`**, mismos bytes/exit/stderr/reap |

Fidelidad del doble: `os.read` real sobre pipe real (lecturas cortas
`min(pedido, disponible)`), selector real, reloj guionizado por ronda sin
sleeps de sincronización, capacidad ampliada del arnés con `F_SETPIPE_SZ`
(sin privilegios ni configuración global), hijo propio real para
`killpg`/reap; el guion no depende de saber qué variante corre y el oráculo
es el estado público de `run_process`. El producto no usa `F_SETPIPE_SZ`
(`grep -rn F_SETPIPE_SZ tools/ src/` → 0), pero un hijo admisible puede
ampliar su propia tubería (demostrado por el arnés).

**Contrato:** `CONTRATO-AC1` («Timeout o exceso: terminar grupo y recolectar
hijo directo; guardar causa y captura parcial acotada») no fija precedencia;
la aclaración C2 aprobada fija la frontera del deadline para el original
(timeout) pero no dice nada de un exceso ya detectado en una ronda anterior.
**La precedencia entre timeout y exceso en esta ventana no está contratada**:
no se inventó literal esperado, no se añadió regresión, no se cambió
producto y la decisión queda pendiente. Alternativas servidas: (1) restringir
el dominio a tuberías no redimensionadas (equivalencia con invalidante);
(2) contratar que el exceso detectable antes del deadline prevalezca (cambio
de producto); (3) contratar que el timeout prevalezca en la frontera aunque
hubiera exceso detectable una ronda después (habilitaría regresión, previa
aprobación). Pregunta precisa para decisión humana: *¿qué causa debe
reportar el transporte cuando el reloj alcanza el deadline entre la ronda en
que una implementación detecta el exceso y la ronda en que otra lo
detectaría?*

**A13 (revisión de redacción, sin reabrir sondas):** la fila vigente ya
declara que la equivalencia es **observable** y no identidad de todo el
estado interno (la variante consume un byte más de una cola que muere con el
proceso terminado; mismo motivo, mismos bytes persistidos). Se confirma que
`remaining+1 → remaining+2` no hereda la ventana de A12: con
`remaining < 65536` y `disponible > remaining` ambas señalizan en la misma
ronda; con `remaining ≥ 65536` ambas leen 65536. Sin cambio de redacción.
**Presupuesto B: ~2 s de 300** (sonda; reejecución del verifier 56 ms).

## 4. Frente C — disposición del cambio estructural de la partición

Diff completo de partición auditado (`b27f01e → ff3b7c5`, 17 archivos) más
la regresión C2 (`aa2ffa9`). Clases y disposición:

| Clase | Evidencia ejecutada | Disposición |
|---|---|---|
| 1. Cuerpos trasladados mecánicamente | Fingerprints independientes AST: **72/72 idénticos**, 0 desaparecidos, 0 ambiguos; `REGISTRY` es el único símbolo cambiado previsto | Cubierto con evidencia (auditoría `fingerprints.log`) |
| 2. Resolución de nombres/imports | 0 ciclos en el grafo interno; ningún submódulo importa su propia fachada; `__all__` de las fachadas resuelve; imports de consumidores reales resuelven | Cubierto con evidencia (auditoría + suite) |
| 3. Composición de `REGISTRY` | 47 claves = 39 literales + 8 derivadas, conjunto idéntico al corte; expresión por clave normalizada idéntica; mitades disjuntas; centinelas de `derived`; **D2** (omitir `G-COV-TOTAL`) y **D4** (componer `G-MUT-SITES` con `gate_mutation`) detectados por tests | Cubierto con evidencia (auditoría + D2/D4 + `test_report_profile`) |
| 4. `derived(base)` | Centinelas que registran: `G-CVE→G-AUDIT`, `G-IMPORT-ORDER→G-LINT`, `G-SAST→G-SAST-BANDIT`, `G-TEST-FAST→G-TEST`; `G-HOOKS-WIRED` despacha `wct doctor` por los puntos de sustitución; `derived({})` falla cerrado; **D1** (alias `G-SAST→G-LINT`) detectado por `test_every_gate_with_external_tool_exposes_it` | Cubierto con evidencia (auditoría + D1) |
| 5. Identidad compartida, alias y `TIERS` | Entradas `is` mitades↔fachada; `TIERS`/`_COMMIT_GATES` mismo objeto y listas idénticas (fast 7 / commit 21 / full 34 / pr 27); todo gate de tier resuelve | Cubierto con evidencia; **limitación**: ningún consumidor actual observa la identidad `is` (solo la membresía/orden), de modo que una copia profunda no rompería consumidores: la identidad es invariante de fidelidad del traslado, no contrato observado |
| 6. Reexportaciones y puntos de patch | `Builder` compartido; `BUILDERS` callable; `SECRET_PATHS` compartido; P1/P2/P2′ INTERCEPTAN con falsos que registran; P2″ por PX-REG; **D3** (quitar `import shutil` de la fachada) detectado por `test_gate_commands` (ImportError del punto de patch) | Cubierto con evidencia (discriminantes + PX-REG + D3) |

Controles ejecutados sin duplicar la suite: lote sensible de 27 pruebas
(preflight, tiers, report_profile, commands, PX-REG) **27 passed** en 2,73 s;
auditoría estructural 23/23 OK; controles D1–D4 en copia aislada, con
reversión y estado limpio. Los 72 fingerprints idénticos **no** se usan como
acreditación del wiring: el wiring se acreditó por composición, centinelas y
discriminantes. No se detectó hueco que exija regresión nueva; tampoco se
afirma cobertura total de los 928 IDs ni de toda la partición. **Presupuesto
C: ~20 s de 180.**

## 5. Regresiones añadidas y controles realmente ejecutados

- Regresiones permanentes añadidas: **ninguna** (A12 sin discriminación
  contractual; C sin huecos; allowlists intactas).
- Controles ejecutados: campaña A completa con launcher y post-check;
  31 sondas causales; canario de activación; correspondencia 31/31;
  auditoría estructural y fingerprints; D1–D4; P1/P2/P2′; PX-REG; lote
  sensible; sonda B de ventana; verifier de preflight y verifier final.
- El verifier final (agente distinto del autor, solo escritura en
  `build/tmp/recalificacion/verifier/`) emitió **APROBAR CON RESERVAS**:
  A APROBAR CON RESERVAS (R-A1: el manifiesto de fuentes congeladas cambió
  tras el preflight), B APROBAR, C APROBAR; reejecutó los 4 IDs decisivos
  (6 s), la sonda B (56 ms), la auditoría y fingerprints (byte-idénticos) y
  D1. R-A1 quedó atendida: el contenido post-preflight se conservó como
  `fuentes-congeladas-post-preflight.sha256` y el hash del pyproject privado
  pasó a `mutation-config.sha256`, restaurando el original verificado
  (`e7f05e3e…`).

## 6. Verificación del incremento y CI

| Verificación | Resultado |
|---|---|
| `git diff --check` | Limpio |
| Colección completa | **691** = 679 unit + 10 integration + 1 property + 1 acceptance |
| Fast | **7/7 PASS**, exit 0 |
| G-ACCEPT | **PASS, 0 hallazgos** |
| Ratchets | «Todos los ratchets se mantienen», exit 0 |
| Integridad | exit 1; drift **37 = 7 modificadas + 30 nuevas**; sin ruta nueva de este incremento (solo documentos) |
| Normativa/property/focales | No re-ejecutadas como batería pesada: el incremento no toca tests ni producto (regla de comprobaciones exigibles); las focales afectadas del corte siguen siendo las de `PARTICION…` §7 |

CI de la PR #53: el run previo a este incremento terminó con `integrity
check` exit 1 (drift) y los pasos posteriores **NO EJECUTADOS**, sin
pronóstico. El run del commit de este registro se consulta tras el push y se
reporta en la entrega (no se escribe su propio SHA futuro en el documento).

## 7. Próxima puerta mínima y bloqueos concretos

1. **A12**: decisión humana de la precedencia timeout/exceso (pregunta de
   §3) o restricción de dominio; sin ella no hay regresión posible.
2. **A13/A14/C1c/C1d y C2**: ratificaciones humanas pendientes de las
   propuestas ya servidas; C2 ya tiene regresión permanente.
3. **Recalificación A cerrada en su alcance**: 31/31 killed con causa en el
   árbol vigente; los 928 siguen sin ejecución ni veredicto; el bruto E
   (27+4) y sus sellos permanecen intactos.
4. **TEST-007**: partición implementada y auditada; sin excepción concedida
   ni cambio de umbral.
5. **Bloqueos para publicar/merge**: G-META-1 sigue siendo el único rojo del
   tier commit (drift pre-bless de 37 rutas, pendiente de revisión humana);
   Q-ACCMUT, cobertura/CRAP, DRY y full no ejecutados; bless/merge/bump/tag/
   release no autorizados.

## 8. Límites

No ratifica equivalencias ni clasificaciones; no acredita AC1 ni beta.3; no
convierte `survived` histórico en `killed`; no ejecuta Q-ACCMUT, campañas de
fuentes, los 928 IDs, bless, merge, bump, lock, tag ni release; no modifica
producto, gobernanza, dependencias, umbrales ni manifests. La evidencia de
sondas y campañas vive bajo `build/tmp/` (temporal, no custodia durable ni
publicada como producto).
