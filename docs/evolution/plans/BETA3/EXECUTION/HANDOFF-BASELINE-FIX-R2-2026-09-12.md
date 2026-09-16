# Handoff — reparación de frontera (baseline AC1) — hijo R2

Fecha: 2026-09-12. Estado: **ambos incumplimientos de R1 reparados y verificados;
bloqueo de baseline resuelto sobre base Git real; AC1 sigue sin acreditar; binding
P03a no habilitado**. Sin commit, push, PR, bless ni campañas pesadas. Sin cambios
de gobernanza ni del runtime compartido.

## Origen: corrección de dos incumplimientos detectados por la revisión humana

1. **R1 no preservaba historia ni archivos rastreados** (contenido copiado +
   `git init` vacío: sin HEAD, `ls-files` 0). Corregido aquí construyendo el
   hijo desde la base Git REAL. El handoff de R1 fue corregido con una sección
   «CORRECCIÓN» explícita; sus resultados y manifiestos se conservan atribuidos
   a su entorno real, sin sobrescribir.
2. **`paths.build` no se excluía del inventario exigible** (el repro del
   revisor: `source=["tools"]`, `build="tools"` devolvía 79 fuentes), y no
   había filtrado de venvs/cachés anidados. Corregido en `semgrep_scope.py`
   con regresiones.

## Identidad del hijo R2 (base Git real)

- Expediente: `build/tmp/ac1-baseline-fix-r2/`; hijo en `candidate/`.
- Construcción: `git clone` de la raíz + `checkout --detach 932c835a…` —
  **HEAD `932c835ac0eeb75010ec7a1071315b1c51f78eb6`** (commit real «docs:
  authorize P02a adjudication…»), **`git ls-files` = 521**, historia completa
  (48 commits), reflog con solo `clone` + `checkout`: **ningún commit
  fabricado**; overlay AC1 y delta quedan como working-tree changes (51
  entradas en `git status`). `show-toplevel == hijo`.
- Overlay AC1: los 553 paths de
  `build/tmp/ac1-qualification-20260912-eaz8182e/evidence/candidate-base.sha256`
  copiados de `build/tmp/beta3-acceptance-engine` y verificados **553/553
  ANTES del delta** (registro de sesión y coherencia verificada: el origen
  sigue verificando 553/553 y en el hijo divergen exactamente los 5 archivos
  que el delta modifica — `evidence/child-identity.txt` y
  `evidence/divergence-553.txt`).
- Delta R2: los 12 archivos del incremento (11 aplicados desde R1 + el
  `semgrep_scope.py` corregido y sus regresiones). Comparación de árbol de
  producto R1↔R2 previa al arreglo: idéntica byte a byte.

## Delta exacto (12 archivos)

- Manifiesto **estándar compatible con `sha256sum -c`**:
  `child-delta.sha256` (12/12 OK, verificado desde el candidato; sha256 del
  manifiesto `496df51cba525373769c3118a8331294b020ec48ea058d0d1c5870376810a4c0`).
- Inventario **nuevo/modificado separado**: `child-delta-inventory.txt`
  (5 modificados — presentes en el manifiesto 553 con hash cambiado — y 7
  nuevos — ausentes del 553 y no rastreados en HEAD).
- El manifiesto histórico de R1 NO fue sobrescrito. Nota del verifier: R1
  rotulaba `tools/wct/gate/semgrep.py` como «modificado»; la rotulación
  correcta (R2) es «nuevo» (no está en el manifiesto de 553 ni rastreado en
  HEAD).

Contenido del delta: las nueve rutas de la addenda (fachada `gate/semgrep.py`
+ registro en `runner.py` + `_declared` en `checks.py` + `f9_a` +
conftest de aislamiento + 2 archivos de tests ampliados + feature verbatim)
más la partición fachada 3+1 autorizada (`semgrep_scope/schema/verdict.py`).

## Reparación 2 — exclusiones de alcance (`tools/wct/gate/semgrep_scope.py`)

- `paths.build` (string o lista) se resuelve bajo la raíz y se excluye
  **por límite de directorio** (`resolve()` + `is_relative_to`), nunca por
  prefijo textual: un `builder.py` o un `build2/` vecinos siguen contando
  (`test_build_anidado_respeta_el_limite_de_directorio`).
- Entornos virtuales y cachés anidados dentro de las rutas declaradas se
  excluyen por componente de ruta — mismo conjunto que `_protected` de
  integrity más `.git`: `.git/.venv/__pycache__/.pytest_cache/.mypy_cache/
  .ruff_cache` (`test_caches_y_entornos_anidados_quedan_fuera`).
- Se conserva la exigibilidad de archivos ignorados por Git (el walker no
  consulta Git) y de módulos `unsuitable_for_test` (no se lee esa clave).
- Repro del revisor a escala del hijo (policy real, en memoria): con
  `source=["tools"]`, `build="tools"` → **0 rutas bajo tools/** (antes: 79);
  con `build="build"` → las 79 de tools/ vuelven a ser exigibles
  (`evidence/environment-and-sites.txt`; reproducido independientemente por
  el verifier, incluida la forma de lista).
- Regresiones añadidas en la ruta autorizada `tests/unit/test_sast_targets.py`
  (TDD: 4 rojas antes del arreglo, luego verdes); sitios: semgrep.py 51,
  semgrep_scope.py 68, semgrep_schema.py 70, semgrep_verdict.py 56 — todos
  ≤100; LOC 85/114/80/93 — todos <500.

## Batería sobre R2 (logs en `evidence/`)

| Corrida | Resultado | Exit |
|---|---|---|
| Colección (`collect-r1.log`) | 640 tests | 0 |
| Focal normativa (`focal-r1.log`) | 268 passed | 0 |
| Cinco regresiones (`green-five-r1.log`) | 5 passed (texto e identidad intactos) | 0 |
| Suite global normativa (`global-r1.log`) | 639 passed, 1 deselected (property) | 0 |
| Auditoría de imports in-process | 93 módulos observados, `foreign={}` | — |
| Fast (`fast-r1.log`) | 7 gates: 7 PASS | 0 |

Runtime existente sin sync/instalación:
`build/tmp/sh-p01-CND-80B8/.venv` (Python 3.13.14, pytest 9.1.1, semgrep
1.174.0, ruff 0.16.4, mypy 2.3.1). Entorno: `PYTHONPATH=<hijo>:<hijo>/src`,
`PYTHONSAFEPATH=1`, `PYTHONDONTWRITEBYTECODE=1`, TMPDIR del expediente,
basetemp propio por corrida, `UV_NO_SYNC=1`/`UV_OFFLINE=1` para el fast.
El aislamiento Git in-process (techo al `tmp_path` de cada prueba) mantiene
verdes las cinco regresiones pese a que el hijo ahora SÍ tiene HEAD e
inventario rastreado.

## Verificación independiente

Dictamen del verifier de solo lectura con chequeo expreso de ambos puntos:
**«DICTAMEN R2: FAVORABLE»**. Punto 1 PASS (a–g): HEAD real, 521 rastreados,
48 commits, reflog sin commits fabricados, divergencia post-delta 548+5
exacta, overlay original 553/553, checkout principal sin cambios. Punto 2
PASS (a–d): exclusiones por límite de directorio verificadas por lectura,
repro del revisor reproducido en memoria (0 bajo tools/ solapado; 79
restauradas sin solape; también en forma de lista), 4 regresiones con
aserciones de comportamiento, sitios ≤100 y LOC <500 medidos. Contrato y
resultados PASS: manifiesto estándar 12/12, inventario coherente, manifiesto
histórico de R1 intacto, logs coherentes (640 = 639 + 1), colección
independiente 640/exit 0, feature verbatim, corrección de R1 presente.
Observaciones declaradas: incidencia menor del propio verifier (redirección a
/tmp fuera del repo, no borrada por el mandato), rotulación heredada de R1
para `semgrep.py`, y la atribución del 553/553 pre-delta al log de sesión.

## Declaraciones honestas

- **G-META-1 permanece rojo, pre-bless, sin excepción**: 20 hallazgos (13 del
  overlay AC1 + 7 de este incremento), todos atribuibles al delta declarado.
- El hijo R2 contiene residuo de ejecución (temporales de aceptación bajo
  `build/`, `.venv` creado por `uv run`, cachés), excluido del producto por
  las reservas de la addenda.
- La verificación «553/553 antes del delta» es atribuible al log de sesión de
  construcción (post-delta es irreproducible por diseño); su coherencia con
  el estado observado fue verificada por el verifier.
- Cobertura, mutación completa, CRAP/DRY: NO EJECUTADOS (no autorizados en
  este incremento). **Esto no acredita AC1** ni habilita el binding P03a.

## Próximos pasos (fuera de este incremento)

1. Lectura humana del delta R2 y decisión de bless de las rutas protegidas.
2. Reanudar la calificación AC1 por su propia puerta con baseline verde sobre
   base Git real; orden aleatorio (pytest-randomly no instalado; sin
   instalar) antes de cualquier campaña; luego mutación → aceptación →
   cobertura → CRAP/DRY según PROC-004, con campañas autorizadas expresamente.
