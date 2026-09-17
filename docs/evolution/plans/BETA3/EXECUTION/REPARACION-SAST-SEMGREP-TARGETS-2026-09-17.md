# Reparación G-SAST-SEMGREP con targets explícitos de E — AC1 / PR #53 (2026-09-17)

Registro del encargo «reparar la omisión de fuentes causada por las
exclusiones predeterminadas de Semgrep usando como targets explícitos los
archivos del conjunto E que el gate ya calcula». Base de partida:
`d1896210eec258d219b3e3f9edf8f28eaedb5ab4` (worktree de integración =
remoto = headRefOid de la PR #53, OPEN en borrador; verificado en preflight,
sin avance). Candidato medido: **`421725367e3df6fae1b20af7f7ed910b2a4d50a7`
= d1896210 + UN commit de producto** (`fix(sast)`, 4 archivos de la allowlist:
`tools/wct/gate/semgrep.py`, `tests/unit/test_sast_targets.py`,
`features/wct-sast-targets-001.feature`, `docs/gates.md`; 145 inserciones /
11 borraciones). Sin cambios en `semgrep_scope.py`, `semgrep_schema.py`,
`semgrep_verdict.py`, policy, reglas, workflows ni dependencias. Sin bless,
update-manifest, merge, bump, tag ni release. E no se reduce; ninguna omisión
se silencia.

## 1. Causa reproducida y evidencia (derivada, no asumida)

Reproducción mínima sobre el corte elegido (copia aislada con raíz Git real
y `origin/main` corregido a `932c835`): `required_sources` con la política
vigente → **E = 169** (9 src + 67 tests + 93 tools); el gate histórico
(invocación sin targets) → **ERROR «ruta distinta no compensa»** con 67
`omitida:` (todas bajo tests/) y 1 `S_extra` (governance/lint/
vulture_whitelist.py). La causa —la lista de ignorados por defecto del motor,
que omite directorios de pruebas cuando no recibe targets— fue discriminada
por el piloto del 2026-09-16 (expediente `build/tmp/typesafe-pilot-sast-
20260916/`, EVIDENCIA-VERIFICADA: no es Git, no son `paths:` de regla; un
`.semgrepignore` de repo la sustituye) y re-validada aquí por la fidelidad
del rojo (§3). Los números son históricos del corte; los actuales se derivan
en cada corrida.

## 2. Diff exacto

`tools/wct/gate/semgrep.py` — `gate_sast_semgrep`:

- `argv = [*COMMAND, *required]`; `subprocess.run(argv, cwd=root,
  text=True, capture_output=True, check=False)`; `command` =
  `" ".join(argv)`. Sin shell; orden determinista (el de `required_sources`,
  que ya ordena). Docstring del módulo actualizado.
- **E vacío conserva la invocación histórica exacta** (argv = COMMAND sin
  targets; nunca `.`).
- `tests/unit/test_sast_targets.py` — 4 tests nuevos + helper
  `_raiz_git_con_gobernanza`; `COMANDO` actualizado a
  «…--json src/a.py» (el exigible de la raíz plantada; expectativa
  justificada del command); `APPROVED_SCENARIOS` + escenario nuevo.
- `features/wct-sast-targets-001.feature` — escenario «Las exclusiones por
  defecto del motor no ocultan fuentes exigibles» (paso formulado «sobre la
  raiz plantada» para resolver la colisión placeholder-variant que G-ACCEPT
  detectó en el primer intento) y celda `comando` del outline final con
  « src/a.py».
- `docs/gates.md` — D6 «Targets explícitos del exigible (reparación
  2026-09-17)», D4 redactado para argv real, fila de tabla y procedencia
  D1–D5 (GS-3) vs D6 explícita.

## 3. TDD y prueba real de recuperación del alcance

1. Test rojo primero: `test_un_defecto_dentro_de_tests_es_observado_por_el_gate`
   (Semgrep real; defecto de credencial en tests/; espera FAIL con
   `wct-hardcoded-credential-shape` y la ruta). Bajo d1896210 cayó ROJO por
   la causa contractual exacta: `ERROR 'falta tests/test_cred.py'` con
   `omitida: tests/test_cred.py` — la omisión escondía el hallazgo. (Un
   primer intento de plantación usó la clave de policy `src` en vez de
   `source` y produjo un rojo espurio «ruta distinta no compensa» con
   S_extra=src/a.py; corregido y documentado — intento inválido preservado.)
2. Tras el fix: 59/59 del fichero (55 previos + 4 nuevos). La regresión de
   exclusiones ejecuta Semgrep real en 3 de los 4 nuevos (defecto en tests/,
   tres directorios, espacios); E vacío usa instrumento controlado con argv
   literal histórico independiente del productivo.
3. Recuperación del alcance sobre el árbol real (copia): gate → **PASS
   «169 fuentes analizadas, 0 hallazgos»**, detalles vacíos.

## 4. E/scanned/faltantes/extras derivados por conjuntos

| Medida | Valor (derivable en cada corrida) |
|---|---|
| E (required_sources, policy vigente) | 169 = 9 src + 67 tests + 93 tools |
| scanned con targets explícitos | 169; faltantes = ∅; extras = ∅ |
| scanned con invocación histórica (corte) | 103; faltantes 67 (todo tests/); extra 1 (vulture_whitelist) |
| Frontera argv (contrato G) | 5 182 bytes de targets para E=169 frente a ARG_MAX 2 097 152 (margen ~400×); un exceso fallaría como OSError → rama ERROR acotada. Sin batching ni abstracciones anticipadas. |

## 5. Impacto en command y contratos GS-3 (tabla)

| Evidencia previa | Cambio de premisa | Comprobación requerida / hecha |
|---|---|---|
| D1 SKIP exacto (herramienta ausente) | Ninguno (rama intacta) | test preexistente pasa (59/59) |
| D2 Git no-cero acotado | Ninguno | ídem |
| D3 duration_ms (error y retorno) | Ninguno | ídem (1250/2500 ms) |
| D4 command = join(COMMAND) | **Cambia**: ahora join(argv) con targets | binding compara command contra argv invocados (independiente del formateador); gate real corrobora; docs D4 redactado |
| D5 policy ilegible | Ninguno | ídem |
| Equivalencias GS-3 `text=True` (24/29/33) | **Cambia la semilla**: fuente y comando cambian → revisión obligatoria | Precondiciones re-verificadas al nuevo SHA: stdout `{"vers…` sin BOM, UTF-8 estricto OK, `json.loads(str)==json.loads(bytes)` en el dominio; sucesores propuestos §6, SIN ratificar |
| Equivalencias check falsy (6/11/26/31) | **Cambia la semilla** | Semántica subprocess (check=None/omitido ≡ False) independiente del comando; sucesores propuestos §6, SIN ratificar |
| Literal command aprobado en Examples | **Actualizado** con « src/a.py» | Sondas de alteración del Examples (vacío/retirada/duplicación/alteración): 4/4 detectadas por el binding |
| Q-ACCMUT 47/47 (ancla feature wct-acceptance-evidence-001 y maquinaria) | Ninguno (anclajes sin cambio; el feature SAST no es consumido por la campaña de aceptación) | No aplica a este delta; G-ACCEPT (todos los features) PASS |

## 6. Mutación: bruto, atribución y residuos

Campaña en copia fresca (`camp/`, raíz Git propia, pyproject experimental:
`only_mutate=["tools/wct/gate/semgrep.py"]`, `source_paths=["tools"]`,
`also_copy=["src","features","governance"]`), gen-only con la firma admisible
(`__main__.py:1247`, 21,6 s). Inventario nuevo: **108 = 26 x__topology + 8
x__policy + 74 x_gate_sast_semgrep** (recuento idéntico al histórico; los
diffs de la función cambiada son nuevos — mapeo por diff, no por ID).
Baseline focal 8 tests en 0,24 s; fichero completo 59 en 19,6 s.
**Canario** `x__topology__mutmut_1` (completed=None): killed por mutmut
(2,24 s) y **activación acreditada en proceso** (con
`MUTANT_UNDER_TEST=tools.wct.gate.semgrep.x__topology__mutmut_1` y PYTHONPATH
sobre `mutants/`, `_topology` produce el `AttributeError: 'NoneType' object
has no attribute 'returncode'` documentado; sin variable, original OK).

- Pasada focal (8 tests controlados): 63 killed + 11 survived (8,4 s).
- Re-test de los 11 bajo el fichero completo (59 tests, 168,7 s): mueren 6
  (24/26/29/31/34/35) → **bruto final: 69 killed + 5 survived** (0 timeout,
  0 suspicious, 0 errores instrumentales; el txt de la primera pasada se
  conserva y ambas se reportan).
- Los 5 supervivientes (25/27/30/32/33) son solo kwargs de la única llamada
  `subprocess.run`: **25/30/33** (`text=True → None/omitido/False`),
  sucesores de la familia 24/29/33; **27/32** (`check=False → None/omitido`),
  sucesores de la familia falsy 6/11/26/31. Se registran como **propuesta de
  equivalencia sucesora PENDIENTE DE DECISIÓN HUMANA** bajo las precondiciones
  re-verificadas (Semgrep 1.174.0, stdout directo UTF-8 sin BOM, consumidor
  con decodificación UTF-8); este encargo NO ratifica equivalencias ni
  traslada dictámenes al nuevo hash. `x__topology`/`x__policy` (34): fuente
  byte-idéntica a GS-3; veredictos históricos conservados, no re-ejecutados
  (el canario re-valida la activación del mecanismo).

## 7. Aceptación, cobertura, CRAP, DRY y full realmente ejecutados

- Colección **696** (695 + 1 property); property separado 1 passed; suite
  canónica **695 passed, 1 deselected**, exit 0, 159 s; total **88,09 %**
  ≥ 74,5; LCOV fresco.
- G-COV-DIFF (productivo, base fiel): **PASS**; cláusula de rama del
  diferencial: **314/348 = 90,2299 %** ≥ 90 (script reconstruido —el
  histórico era efímero— que reproduce el número canónico exacto del corte
  previo; el delta no añade arcos).
- CRAP: canónico src exit 0 (máx 3,0); archivo cambiado: `gate_sast_semgrep`
  CC 3, 100 %, CRAP 3,0 ≤ 6. TEST-007: semgrep.py 101 líneas, sin déficit.
- DRY: estructural 0 candidatos; plantillas 17 = baseline 17; jscpd 0 clones.
- G-ACCEPT: **PASS** tras resolver la colisión placeholder-variant (intento
  rojo preservado); sondas del Examples 4/4.
- **Full PRE-BLESS: 34 gates = 33 PASS + 1 FAIL** (361 s) — el único rojo es
  **G-META-1** (drift protegido pre-bless conocido: 37 = 7+30, conjunto
  idéntico al previo; `tools/wct/gate/semgrep.py` ya figuraba entre las 30
  nuevas). **G-SAST-SEMGREP: PASS «169 fuentes analizadas, 0 hallazgos»**.
  G-MUT: 43/43 killed (su campaña de src/example). Q-ACCMUT: no ejecutado
  (auditoría de alcance: anclajes sin cambio; el 47/47 histórico no cubría el
  feature SAST y no se alega lo contrario).

## 8. Presupuestos, incidentes y dictamen independiente

| Frente | Tope | Consumido |
|---|---|---|
| Reproducción + TDD + focales | 600 s | ≈75 s (incluye intento inválido de plantación con clave `src`) |
| Mutación de fuentes afectadas | 1200 s | ≈222 s (gen 21,6 + baselines 21 + canario 2,2 + campaña 8,4 + re-test 168,7; incluyó 1 intento inválido de plugin `-p instrumento` 1,5 s) |
| Atribución/sondas de mutantes | 600 s | ≈8 s (diffs + precondiciones bytes/BOM) |
| Q-ACCMUT | 900 s | 0 (no aplica; declarado) |
| Cobertura + CRAP | 900 s | ≈180 s |
| DRY | 600 s | ≈35 s |
| Full PRE-BLESS | 1800 s | 361 s |

Verifier independiente (solo lectura, 0 escrituras en el candidato, 0
consultas externas): **APROBAR-PUBLICACION**. Re-ejecutó: 59/59; el gate
real con derivación por conjuntos propia (169/169/∅/∅); la fidelidad del
rojo con plantación propia (invocación histórica omite tests/; gate del
candidato observa el hallazgo; classify bajo stdout viejo → ERROR falta);
la no-reducción de alcance (diff exclusivo de 4 archivos, E recalculado);
causalidad de mutación en vivo (killed 1 y 8; survived 27; los 6 discrepantes
del txt re-ejecutados killed); métricas (88,09 %, 314/348, drift 37, jscpd
0); staging exclusivo y worktree intacto. Reservas no bloqueantes: el txt de
primera pasada focal no reproduce el estado final (se reportan ambas); el
LCOV del candidato es regeneración post-commit con números idénticos; diff
contra 932c835 abarca la rama (el delta del incremento es contra d1896210).

## 9. Drift protegido recalculado y próxima puerta

Drift re-medido (`wct integrity check`, exit 1): **37 = 7 modificadas + 30
nuevas, conjunto sin cambios**. Próxima puerta mínima: decisión humana sobre
las 5 propuestas de equivalencia sucesora (§6) y, con ella, la revisión
humana protegida del drift (E9) → bless → POST-BLESS. Nada de eso se ejecuta
ni se autoriza aquí. **El piloto Jev no fue consultado ni usado como
evidencia en este encargo** (0 llamadas TypeSafe).
