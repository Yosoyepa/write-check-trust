# Cierre del cleanup de `_close_streams` y calificación pre-bless — AC1 / PR #53 (2026-09-16)

Registro sucesor del encargo «simplificar el cleanup conforme a su precondición
real, cerrar TEST-004 y la frontera de deuda preexistente, y avanzar hasta full
PRE-BLESS solo si las puertas anteriores quedan conformes». Candidato medido:
`1a25984b0972c354e4e42c1d78d404475051e3705400476a500fb63b60acd5b8` en
`tools/wct/accept/process.py`, integrado por el commit de código de este
encargo sobre `a813387e1b54dded55dc6803f6b22f7b6c977a3c`. Base de PR #53:
`origin/main` = `932c835ac0eeb75010ec7a1071315b1c51f78eb6`.

**Estado global: cadena detenida en la mutación acotada.** El cleanup focal es
conforme y se preserva con su estado declarado (§13 del encargo), pero la
función limpiada genera dos supervivientes de mutación runtime-equivalentes
(`x__close_streams__mutmut_1/5`) sin disposición humana. Por la regla «con
supervivientes o errores sin disposición, detén la cadena», **no se repitió
Q-ACCMUT, no se recomputó cobertura/CRAP sobre el candidato final, no se repitió
DRY y no se ejecutó full PRE-BLESS**. No se presenta cierre global ni PASS de
G-MUT. No se ejecutan bless/update-manifest, merge, bump/lock, tag, release ni
declaración de cierre integral AC1/beta.3. El documento ajeno
`PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md` permanece intacto, sin
seguimiento y fuera del incremento (sha256 `dedda9f3…`). La evidencia bajo
`build/tmp/` es temporal, no custodia durable.

## 1. Preflight e identidades

- Worktree `build/tmp/beta3-ac1-r2-integration`, rama
  `codex/beta3-ac1-r2-integration`; HEAD de partida
  `a813387e1b54dded55dc6803f6b22f7b6c977a3c` = `origin` = `headRefOid` de la PR
  #53 (OPEN, `MERGEABLE`), sin avances remotos posteriores (`git ls-remote`).
  Índice limpio salvo el untracked ajeno citado.
- Copias aisladas con raíz Git propia:
  `build/tmp/cierre-cleanup-20260916/{candidate,mutation}` (detached en
  `a813387`) y `build/tmp/fidelidad-transporte-20260916/base` (`origin/main`).
  Runtime acreditado: `.venv` del worktree — Python 3.13.14, pytest 9.1.1,
  mutmut 3.7.0, coverage 7.15.4, diff-cover 10.5.1, crap4py 0.1.1, jscpd
  5.0.16 — con PATH absoluto e imports resueltos a la copia
  (`PYTHONPATH=$PWD:$PWD/src`). Nada instalado ni sincronizado; runtime no
  modificado. Un intento previo del tier commit en el encargo anterior fue
  invalidado por PATH relativo (instrumental, ya diagnosticado).

## 2. Precondición acreditada y diff mínimo

El verifier independiente emitió **`PRECONDICION-CONFIRMADA`** con variante
recomendada A, tras revisar y re-ejecutar:

- `_close_streams` tiene un único consumidor: `_execute`, en su `finally`
  (process.py:78), con el `process` construido por el propio SUT con
  `stdin=DEVNULL`, `stdout=subprocess.PIPE`, `stderr=subprocess.PIPE`
  (process.py:62-69). Cero importaciones del helper en tests.
- CPython 3.13.14 POSIX: `self.stdout/stderr` inicializan en `None`
  (subprocess.py:872-874), los pipes PIPE se envuelven antes del lanzamiento
  (1021-1037) y cualquier fallo de `_execute_child` cierra y **re-lanza**
  (1048-1075); ningún retorno correcto con PIPE deja streams en `None`.
- Ninguna vía admitida (`_observe`, `_terminate`, señales, reasignaciones)
  sustituye los atributos por `None` antes del `finally`; único camino público
  `campaign._attempt → run_process`.

Diff mínimo aplicado (3 inserciones, 4 supresiones):

```diff
 def _close_streams(process: subprocess.Popen[bytes]) -> None:
-    """Close available child streams after observation finishes."""
-    for stream in (process.stdout, process.stderr):
-        if stream is not None:
-            stream.close()
+    """Close the child streams requested with PIPE after observation finishes."""
+    for stream in (cast(BinaryIO, process.stdout), cast(BinaryIO, process.stderr)):
+        stream.close()
```

Variante A frente a B (`assert`): B falla `ruff` con 2× S101 y exigiría dos
supresiones (prohibidas y con ratchet); A replica el patrón ya existente en
`_observe` (process.py:38-39) y no oculta un problema real de tipos: el
`| None` es del contrato general de `Popen`, no del valor en este punto, y el
cast localiza una precondición demostrada. `mypy --strict` pasa; `ruff
format`/`ruff check` pasan; sin supresiones nuevas.

Caracterización: **verde antes** (109 passed, 11.66 s) y **verde después** (109
passed, 11.44 s) de los focales `tests/unit/test_sast_targets.py` +
`tests/unit/test_accept_campaign.py`; no se fabricó ningún rojo TDD
(refactorización con caracterización verde declarada). Cobertura focal (LCOV
`690f60be…`, en
`build/tmp/cierre-cleanup-20260916/candidate/build/tmp/evidencia/focal-process.lcov`):
`_close_streams` queda en **2/2 arcos, 100% de rama con streams
reales** (antes 3/4 = 75%); `_execute` conserva 6/6. No se añadió ningún test de
streams `None`.

## 3. Control defectuoso discriminado (canario del oráculo)

Sonda en la copia de campaña: cuerpo de `_close_streams` reemplazado por
`return` (omite el cierre) y prueba discriminante
`test_failed_observation_reports_reaps_and_closes_live_child` → **ROJO por la
causa prevista**: `AssertionError: assert False is True` sobre
`double.stdout.closed` (`<_io.FileIO …>.closed`). Restaurado el cuerpo canónico
(sha256 `1a25984b…`). Evidencia: `evidence/canario-defective-control.log`. Esto
acredita que el oráculo discrimina la omisión del cierre sin estados
imposibles.

## 4. Frontera normativa de las 12 funciones (aprobada por el encargo)

Queda registrada la delimitación aprobada: las **9 trasladadas** y los **3
cuerpos idénticos de `runner.py`** se tratan como deuda preexistente, con
revisión por identidad confirmada (cuerpo conservado; resolución/imports
equivalentes o comprobados; comportamiento preservado; ausencia de lógica nueva
encubierta):

| # | Ruta::qualname actuales | Base | CRAP |
|---|---|---|---:|
| 1 | `tools/wct/gate/checks_scanners.py::gate_archmetrics` | `gate/checks.py::gate_archmetrics` | 30.0 |
| 2 | `tools/wct/gate/runner_audit.py::gate_audit` | `gate/runner.py::gate_audit` | 30.0 |
| 3 | `tools/wct/gate/checks_scanners.py::gate_accept` | `gate/checks.py::gate_accept` | 20.0 |
| 4 | `tools/wct/gate/checks_scanners.py::gate_introvert` | `gate/checks.py::gate_introvert` | 20.0 |
| 5 | `tools/wct/gate/runner_secrets.py::gate_secrets` | `gate/runner.py::gate_secrets` | 13.1 |
| 6 | `tools/wct/gate/checks_scanners.py::gate_dry` | `gate/checks.py::gate_dry` | 12.0 |
| 7 | `tools/wct/gate/checks_quality.py::gate_dry_tpl` | `gate/checks.py::gate_dry_tpl` | 12.0 |
| 8 | `tools/wct/gate/checks_quality.py::gate_lcom` | `gate/checks.py::gate_lcom` | 12.0 |
| 9 | `tools/wct/gate/checks_debt.py::gate_suppressions` | `gate/checks.py::gate_suppressions` | 12.0 |
| 10 | `tools/wct/gate/runner.py::gate_meta_rules` | misma ruta/qualname (cuerpo idéntico) | 30.0 |
| 11 | `tools/wct/gate/runner.py::run_tier` | misma ruta/qualname (cuerpo idéntico) | 7.2 |
| 12 | `tools/wct/gate/runner.py::gate_mutation_sites` | misma ruta/qualname (cuerpo idéntico) | 7.0 |

Evidencia: `build/tmp/fidelidad-transporte-20260916/evidence/crap-classification-66.json`
(fingerprints AST) y `resolution-check.txt`; el verifier reprodujo la identidad
de cuerpo **incluidos args, decoradores y retorno** de las 12, y confirmó que
los únicos cambios de proveedor (`_result`, `_audited_secrets`) tienen cuerpo
AST-idéntico y que `REGISTRY` y la fachada `checks.py` re-exportan las
funciones. Comportamiento preservado: identidad de cuerpo + resolución
equivalente + wiring verificado + suite normativa (G-TEST/G-ACCEPT/G-INTROVERT
PASS en el tier commit). Límites declarados por el encargo: esta decisión
delimita el alcance incremental de STYLE-002 para estas 12; **no** es PASS global
de `crap4py tools/wct` ni exclusión de archivos completos; los 54 cuerpos fuera
del diff mantienen su clasificación documentada; no se reparan las 66 ni se
eleva el umbral. La pregunta de si un traslado mecánico activa STYLE-002 queda
resuelta en el sentido aprobado (deuda preexistente) para estas 12.

## 5. Mutación acotada: resultado real y residuo (bloqueo)

Receta revisada por el verifier y materializada en
`build/tmp/cierre-cleanup-20260916/mutation` (`source_paths=["tools/"]`,
`only_mutate=["tools/wct/accept/process.py"]`, selección focales con deselect de
`test_binding_el_preflight_tolera_git_no_cero_acotado`; pyproject sha256
`8495471f…`). Antes de mutar: focales verdes, cobertura focal de lo afectado,
inventario independiente, IDs explícitos, control original y canario (§3).
Activación acreditada por la sonda causal del canario y por los mutantes
generados en `mutants/tools/wct/accept/process.py`.

La función limpiada **sí genera inventario** (el verifier había anticipado 0
mutantes; la medición lo corrige): 8 IDs nuevos `x__close_streams__mutmut_1..8`.
Resultado con IDs explícitos y sin fallback a suite completa:

| ID | Mutación | Resultado |
|---|---|---|
| `x__close_streams__mutmut_1` | `cast(BinaryIO, process.stdout)` → `cast(None, …)` | **survived** |
| `x__close_streams__mutmut_2` | `cast(BinaryIO, None)` en stdout | killed |
| `x__close_streams__mutmut_3` | `cast(process.stdout)` (falta argumento) | killed |
| `x__close_streams__mutmut_4` | `cast(BinaryIO, )` en stdout | killed |
| `x__close_streams__mutmut_5` | `cast(BinaryIO, process.stderr)` → `cast(None, …)` | **survived** |
| `x__close_streams__mutmut_6` | `cast(BinaryIO, None)` en stderr | killed |
| `x__close_streams__mutmut_7` | `cast(process.stderr)` (falta argumento) | killed |
| `x__close_streams__mutmut_8` | `cast(BinaryIO, )` en stderr | killed |

`x__execute__mutmut_28/29` se re-anclaron con la misma receta: **survived**
(mutaciones `wait(timeout=None)` / `wait(timeout=2)`), conservando su bruto y su
adjudicación como equivalencia deductiva C1; no se convierten en killed.

Residuo: los dos supervivientes son runtime-equivalentes por construcción
(`typing.cast` ignora su primer argumento; el valor retornado es idéntico). Son
la misma clase que las equivalencias A4–A11 ratificadas para `_observe`, pero
son IDs nuevos y **no se ratifican automáticamente**. Por la regla del encargo,
la cadena se detiene aquí y el residuo se entrega por ID para disposición
humana: `tools.wct.accept.process.x__close_streams__mutmut_1` y
`…x__close_streams__mutmut_5`. No se ejecutó ninguna ampliación de campaña para
forzar su muerte ni se creó estado artificial alguno.

## 6. Q-ACCMUT: impacto analizado, vigencia NO declarada

`process.py` cambia de `0a218827…` a `1a25984b…` (retirada del guard). El
camino de aceptación (`wct accept mutate` → `campaign.run_mutations` →
`_attempt` → `run_process`) sigue pasando por `_close_streams` en cada intento,
pero el cambio no altera el comportamiento con streams reales (siempre
no-`None`) ni la clasificación semántica de recibos. Conforme a los
invalidantes de `ACTA…` §3.8, un hash distinto de `process.py` impide declarar
vigente el 47/47 histórico por mera conservación del informe; la repetición del
mismo alcance AC1 está autorizada por el encargo **si el verifier lo determina**
y no se ejecutó porque la cadena quedó detenida en el residuo de mutación (§5).
No se presenta el 47/47 como vigente para este candidato.

## 7. Cobertura/CRAP, DRY y full: no ejecutados por la parada

- **Cobertura fresca y CRAP sobre el candidato final: NO EJECUTADOS** (la
  secuencia §8 del encargo exige mutación cerrada; el residuo §5 la detiene).
  Evidencia disponible del cleanup: cobertura focal con `_close_streams` 2/2
  (100%) y `_execute` 6/6; frontier incremental de ramas del encargo anterior:
  TODO 314/350 = 89.71%, PREEXISTENTES 29/60 = 48.33%, EN ALCANCE 285/290 =
  98.28% (se recalcula cuando la cadena se reanude). No se redondea 89,xx a 90
  ni se altera el denominador.
- **Corrección del registro DRY (solicitada por el encargo):** DRY se ejecutó en
  el encargo anterior (`FIDELIDAD-TRANSPORTE-Y-FRONTERA-CRAP-2026-09-16.md` §7)
  **anticipadamente**, mientras TEST-004 seguía pendiente de disposición
  humana (cláusula de rama y frontera de las 12 abiertas en el encargo previo). La medición y sus resultados se conservan
  como evidencia histórica de ese momento; **no** se usan para afirmar
  cumplimiento retrospectivo de PROC-004. La repetición de DRY sobre el
  candidato final **no se ejecutó** por la parada en mutación.
- **Full PRE-BLESS: NO EJECUTADO.** Receta inspeccionada: tier `full` = 34 gates
  (21 de commit + `G-COV-TOTAL`, `G-MUT`, `G-CRAP`, `G-CC`, `G-DRY`,
  `G-DRY-TOK`, `G-DRY-TPL`, `G-LCOM`, `G-SAST-SEMGREP`, `G-AUDIT`, `G-SBOM`,
  `G-DOC`, `G-REDTEAM`); `G-MUT` dispara una campaña mutmut sobre
  `src/example` (config del repo) y `G-COV-TOTAL` escribe
  `build/coverage/lcov.info` (ruta ignorada, no protegida); no se detectó
  escritura de manifests protegidos. Aun así, la puerta previa no está conforme
  y no se ejecutó.

## 8. Verificación compuesta del incremento preservado

| Verificación | Resultado |
|---|---|
| `git diff --check` | Limpio |
| Colección | **690/691** (1 property deselected), exit 0 |
| Focales | 109 passed (caracterización pre 11.66 s; post 11.44 s) |
| Normativa (tier commit, G-TEST) | PASS |
| Property separado | 1 passed, 690 deselected |
| G-ACCEPT / G-INTROVERT | PASS / PASS |
| Fast | **7/7 PASS** |
| Commit | **20 PASS / 1 FAIL**; único rojo **G-META-1** por drift pre-bless |
| Drift protegido recalculado | **37 = 7 modificadas + 30 nuevas**, conjunto sin rutas nuevas (el contenido de `process.py` cambia; la ruta ya figuraba) |
| CI | Se comprueba tras el push (esperado: FAILURE en `wct integrity check`, pasos posteriores no corridos) |

## 9. Presupuestos

- Diagnóstico/focales: caracterización 12 s + post 12 s + focal coverage 12 s +
  ruff/mypy y sondas ≈ 45 s; verifier de precondición ≈ 150 s; total ≈ 195 s de
  300 s.
- Mutación acotada y sondas: canario ≈ 2 s + 2 IDs de `_execute` 29 s + 8 IDs de
  `_close_streams` 18 s ≈ 50 s de 600 s.
- Q-ACCMUT: 0 s de 900 (no ejecutado; parada declarada).
- Cobertura + CRAP: 0 s de 900 (no ejecutado).
- DRY: 0 s de 600 (no ejecutado).
- Full pre-bless y comandos canónicos complementarios: tier commit ≈ 173 s +
  fast ≈ 1,5 s + colección/property ≈ 2 s de 1800 s. Sin transferencias de saldo.

## 10. Próxima autorización mínima

Disposición humana de los dos supervivientes nuevos
(`x__close_streams__mutmut_1` y `_5`, equivalencia runtime de `typing.cast`,
clase A4–A11): ratificarlos como equivalencia acotada al candidato
`process.py 1a25984b…` o rechazarlos exigiendo otra implementación sin cast
(p. ej. un narrowing alternativo que no genere mutantes equivalentes). Con esa
disposición cerrada, reanudar la cadena en el orden del encargo: repetir
Q-ACCMUT (47 celdas, salida privada), cobertura fresca + TEST-004 + CRAP
(incremental y suplementario con la frontera ya registrada), DRY estructural/
plantillas/tokens sobre el candidato final y full PRE-BLESS. Nada de esto se
autoriza aquí; no se bendice, no hay merge, bump/lock, tag ni release.
