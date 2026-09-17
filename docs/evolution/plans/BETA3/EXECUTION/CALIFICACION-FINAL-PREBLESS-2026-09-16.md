# Calificación final pre-bless — ratificación de casts, Q-ACCMUT, cobertura/CRAP y parada (AC1 / PR #53, 2026-09-16)

Registro sucesor del encargo «ratificar los dos casts equivalentes del cleanup y
reanudar la calificación: Q-ACCMUT → cobertura/CRAP → DRY → full PRE-BLESS».
Candidato medido: `e88d66e942bf8ddb0be3a22b2a93df48b0ecec0e` (rama
`codex/beta3-ac1-r2-integration` = `origin` = `headRefOid` de la PR #53, OPEN),
con `tools/wct/accept/process.py`
`1a25984b0972c354e4e42c1d78d404475051e3705400476a500fb63b60acd5b8` (hash
exigido por la ratificación, verificado en worktree y copia de mutación).

**Estado global: cadena detenida en la cláusula de rama de TEST-004.** La
ratificación quedó registrada y verificada, Q-ACCMUT se repitió con resultado
bruto 47/47 y clasificación contractual, y la cobertura fresca pasó el
diferencial canónico de líneas (91 %) y los ratchets; pero la cláusula de rama
de TEST-004 mide **313/348 = 89,94 % < 90 %** sin disposición humana que cubra
los 35 arcos no tomados. Por la regla del encargo («si cobertura o CRAP
aplicables incumplen: detente antes de DRY»), **DRY no se ejecutó (0 s de 600)
y full PRE-BLESS no se ejecutó (0 s de 1800)**. No se declara PASS de G-MUT,
ni cierre de AC1, ni 8 killed en el lote del cleanup. No se ejecutan
bless/update-manifest, merge, bump/lock, tag ni release. El documento ajeno
`PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md` permanece intacto, sin
seguimiento y fuera del incremento (sha256 `dedda9f3f057e9a02bd40740404c2c25773ed21b502798360ec5146a0fd1d430`,
medido en el preflight). La evidencia bajo `build/tmp/` es temporal: no es
custodia durable.

## 1. Preflight e identidades

- Worktree `build/tmp/beta3-ac1-r2-integration`: HEAD
  `e88d66e942bf8ddb0be3a22b2a93df48b0ecec0e` = `origin/codex/beta3-ac1-r2-integration`
  = `headRefOid` de la PR #53 (OPEN), sin avances remotos (`git fetch` +
  `rev-parse`; `gh pr view 53`: base `main` @ `932c835ac0eeb75010ec7a1071315b1c51f78eb6`,
  confirmado con `git ls-remote origin main`).
- Índice vacío salvo el untracked ajeno citado; `git diff --check` limpio;
  `git stash list` vacío.
- SHA-256 de `process.py` = `1a25984b…` (worktree y copia de mutación
  `build/tmp/cierre-cleanup-20260916/mutation/`, idénticos); `campaign.py`
  `686070cd…` y `pytest_receipt.py` `d4f136ae…` intactos.
- Base genealógica medida, no supuesta: `git ls-remote` da `main` =
  `932c835`; el clon local del worktree traía `refs/remotes/origin/main`
  apuntando a la rama local `main` del checkout principal (`8de9107…`, que SÍ
  es ancestro de la rama de PR y de `932c835`). En la copia aislada se corrigió
  el ref (`git update-ref refs/remotes/origin/main 932c835…`) para que la base
  canónica de diff-cover sea la base real de la PR #53; `remote_base()` resuelve
  `origin/main` y el diff `932c835..HEAD` (58 commits) es el incremento puro.
- Copias Git aisladas bajo `build/tmp/calificacion-final-prebless-20260916/`:
  `candidate` (detached en `e88d66e`) y `base` (detached en `932c835`), cada una
  con raíz Git propia (`git clone --no-hardlinks --local`).
- Runtime acreditado: `.venv` del worktree — Python 3.13.14, pytest 9.1.1,
  mutmut 3.7.0, coverage 7.15.4, diff-cover 10.5.1, crap4py 0.1.1 — invocado
  por ruta absoluta con `PATH="/home/jandradeu/.local/bin:$W/.venv/bin:/usr/bin:/bin"`,
  `PYTHONPATH=$PWD:$PWD/src` (resuelto a la copia) y `UV_NO_SYNC=1`. Nada
  instalado ni sincronizado; runtime no modificado.

## 2. Ratificación de los dos casts del cleanup

Condiciones comprobadas contra los diffs y la fuente real antes de registrar:

1. **Diffs exactos** (fuente: `mutants/tools/wct/accept/process.py` de la
   campaña del cleanup, líneas 1193–1196 y 1217–1220, contra `_close_streams`
   de `process.py` `1a25984b…`):
   - `tools.wct.accept.process.x__close_streams__mutmut_1`:
     `cast(BinaryIO, process.stdout)` → `cast(None, process.stdout)` y nada más.
   - `tools.wct.accept.process.x__close_streams__mutmut_5`:
     `cast(BinaryIO, process.stderr)` → `cast(None, process.stderr)` y nada más.
2. **Fuente**: `process.py` con el SHA-256 exigido `1a25984b…` (medido).
3. **Runtime**: Python 3.13.14 (`inspect.getsource(typing.cast)` = `return val`),
   `cast(None, x) is x` → True; los mutantes importan `cast` de `typing`
   (ordinario, sin sustitución; el trampolín de mutmut es un import separado).
4. **Objeto retornado**: `typing.cast` retorna el segundo argumento sin
   evaluar el primero; el mismo objeto stream llega a `stream.close()`. Sin
   otros efectos alterados.
5. **Límites**: la equivalencia NO se extiende al análisis estático de tipos
   (el verifier reprodujo `mypy --strict` sobre `cast(None, x).close()` →
   `error: "None" has no attribute "close" [attr-defined]`, exit 1) ni a otros
   IDs.

**Verifier independiente (puerta previa): `CONFORME`**
(`build/tmp/verifier-puerta-previa-prebless/VEREDICTO.md`): identidad del
candidato, diffs exactos, condiciones runtime, vigencia de las demás
disposiciones (A4–A11: los casts de `_observe` sin cambio entre los anclajes;
`execute__28/29` re-anclados a `1a25984b…` como equivalencia deductiva C1 y
conservados como survived; A1/A2 con `campaign.py`/`pytest_receipt.py`
intactos), ausencia de residuos bloqueantes y de invalidantes.

**Disposición registrada**: los dos IDs quedan ratificados como **equivalencia
conductual en runtime**, acotada a esta fuente (`1a25984b…`), Python 3.13.14 y
`typing.cast` ordinario. **El bruto se conserva: 8 IDs = 6 killed + 2
supervivientes** (log de campaña `evidence/mutmut-close.log`:
`_1` y `_5` survived; `_2/_3/_4/_6/_7/_8` killed). La disposición sucesora es
**6 killed + 2 supervivientes ratificados como equivalentes**; nunca «8 killed»
ni PASS global de G-MUT a partir de este lote; no se reformuló el producto para
evitar mutaciones de `cast`. La campaña que produjo el resultado es la del
cierre del cleanup; la corrida posterior (esta) solo verificó candidato y
evidencia: no se re-ejecutó ni se atribuye como recampaña.

## 3. Q-ACCMUT fresco (repetición del alcance AC1)

Receta del acta (`ACTA-DECISIONES-FINALES-Y-QACCMUT-2026-09-16.md` §8) sobre el
candidato congelado, sin cambiar operador, feature, bindings ni denominador:

- **Interfaz real del CLI verificada** (`tools/wct/cli.py`; `wct accept mutate`
  → `parse_feature` → `generate(ir, --output)` → `run_mutations(ir, command)`).
- **`--output` privado**:
  `build/tmp/qaccmut-final/generated/test_acceptance.py` (fuera del generado
  histórico, que conserva sha256 `118295099f…` medido antes y después; 13/13
  hashes pre/post idénticos en `hashes-before.txt`/`hashes-after.txt`).
- **Inventario real reconciliado**: `parse_feature` + `mutations` = **47 celdas
  = 40 + 7** (5 filas × 8 campos + 1 fila × 7); 47 es el inventario, no un
  número forzado.
- **Baseline exterior**: pytest sobre el generado privado, 2 passed, exit 0.
  Arnés: 55 passed en `tests/unit/test_accept_campaign.py` (controles
  negativos incluidos).
- **Ejecución**: `wct accept --output build/tmp/qaccmut-final/generated/test_acceptance.py
  mutate features/wct-acceptance-evidence-001.feature` desde la raíz de la
  copia `candidate`. **exit 0, 44 s exteriores** (de 600 s de campaña; máx. por
  intento muy por debajo de 30 s).
- **Resultado bruto conservado**: `report.json` en
  `candidate/build/tmp/wct-accept-z55dcs_m/` — baseline `pass` (exit 0),
  **planned=47, killed=47, survived=0, errors=0, not_run=0**; stderr vacío.
  Intentos inválidos: ninguno.
- **Clasificación contractual estricta** (reconciliación propia por intento,
  47/47 sin problemas): `attempt.json` status `mismatch`, exit 1, recibo válido
  con `attempt_id`/`ir_sha256` iguales al SHA-256 real de los bytes del IR
  mutado, `errors` vacío en el recibo, 2 casos (mutado `mismatch`, hermano
  `pass`) y diff del IR contra el baseline en **exactamente la celda objetivo**
  (descenso por hojas incluidas listas `examples`). Sin selector desconocido ni
  fallo de arnés/setup/colección: cero errores instrumentales.
- **Verifier independiente de campaña: `APROBAR-QACCMUT-FINAL`**
  (`build/tmp/verifier-qaccmut-final/VEREDICTO.md`): manifiesto 296/296, muestreo
  causal profundo (mutation-0/23/46), activación real 47/47, sin
  instrumentales, inventario re-ejecutado, aislamiento del generado histórico y
  runtime sin instalaciones. Reservas no bloqueantes: el tiempo exterior de 44 s
  carece de campo firmado en el reporte (corroboración indirecta); no re-lanzó
  la campaña completa (fuera de encargo).
- Presupuesto: preflight ≈15 s + campaña 44 s; verifier aparte. Total del
  encargo muy por debajo de los 900 s exteriores.

## 4. Cobertura fresca sobre el candidato congelado

- **Intento inválido instrumental preservado**: la primera corrida con
  `PATH` sin `/home/jandradeu/.local/bin` dejó sin resolver `uv` a los tests
  que lanzan `uv run` por subprocess (`test_mutation_cli.py`, Popen 255): 2
  failed, exit 1. Descartado con causa registrada y log íntegro en
  `candidate/build/tmp/qaccmut-final/coverage-suite-INVALIDO-path-sin-uv.log`.
- **Suite canónica** (`pytest --cov --cov-branch
  --cov-report=lcov:build/coverage/lcov.info --cov-fail-under 74.5 -q -m "not
  property"`): **690 passed, 1 deselected** (property separado por marcador),
  exit 0, 138 s. Total combinado **88.05 %** ≥ 74.5.
- **LCOV fresco** sin herencia (`rm -rf build/coverage` previo): sha256
  `b45847a9e2d31c302611572cbed3031ca66a319be5e2bbb1fd10b32f10266818`.
- **Diferencial canónico de líneas** (`diff-cover build/coverage/lcov.info
  --compare-branch origin/main --fail-under 90 --include-untracked`, base
  exacta `932c835…`): **91 %**, 1179 líneas, 97 ausentes, **exit 0** → PASS.
- **Cláusula de rama de TEST-004** (método canónico del encargo anterior:
  `branch_metrics_final.py` sobre `git diff -U0 932c835...HEAD -- '*.py'` y los
  BRDA del LCOV fresco): **348 arcos / 313 tomados = 89,94 %** → **NO PASS**
  (89,9425 %, sin redondeo favorable). `process.py` queda **22/22 = 100 %** —
  la disposición (b) del guard defensivo (retirado en `ee53166`) está
  ejecutada y verificada; el 314/350 = 89,71 % anterior no se reutilizó.
  **Residuo: 35 arcos no tomados** — 31 en cuerpos trasladados AST-idénticos a
  la base (`checks_debt` 6, `checks_quality` 7, `checks_scanners` 10,
  `runner_audit` 6, `runner_secrets` 2) y 4 en módulos nuevos del incremento
  (`parsing.py` 1, `pytest_receipt.py` 1, `semgrep_scope.py` 2). Ninguna
  disposición humana aprobada cubre estos arcos para TEST-004.
- **Ratchets** (`wct ratchet check`): «Todos los ratchets se mantienen.»,
  exit 0 → PASS.
- **Verifier independiente: `CONFORME-CON-RESIDUO-BLOQUEANTE`**
  (`build/tmp/verifier-covcrap-final/VEREDICTO.md`): recalculó 348/313 con dos
  métodos independientes, clasificó los 35 arcos (31 + 4), reprodujo el CRAP
  66 = 9+3+54 y los ratchets, y dictaminó que la parada antes de DRY está
  correctamente fundada. Reservas no bloqueantes: no re-lanzó la suite
  completa; exit codes leídos de los logs.

## 5. CRAP en sus tres capas

| Capa | Comando | Resultado |
|---|---|---|
| Canónico | `crap4py src --lcov build/coverage/lcov.info --max-crap 6` | exit 0, máx. 3.0 → PASS |
| Incremental/focal | focal `process.py` y `semgrep_scope.py` | `_observe` 6.0, `_execute` 4.0, `_read` 4.0, `run_process` 3.0, `_close_streams` **2.0**, `_terminate` 1.0; `semgrep_scope` máx. 5.4 → todo ≤ 6, PASS |
| Suplementario global | `crap4py tools/wct --lcov … --max-crap 6` | exit 1, **66 violaciones** |

Clasificación contra la base `932c835…` por fingerprint AST
(`evidence/crap-classification-final.json`): **9 trasladada_mecanicamente +
3 preexistente_sin_cambios + 54 preexistente = 66; 0 nuevas, 0 modificadas**.
La frontera de las 12 (9 trasladadas + 3 cuerpos idénticos en `runner.py`)
**no cambia de premisa**: `_close_streams` (2.0) y los tres cuerpos reparados
no aparecen en la lista; no se reabre ni repara ninguna de las 66 por el rojo
suplementario.

## 6. DRY y full: no ejecutados por la parada

- **DRY posterior: NO EJECUTADO (0 s de 600).** La medición anticipada del
  encargo anterior permanece histórica; esta ejecución habría acreditado el
  orden sobre el candidato actual y queda bloqueada por la cláusula de rama.
- **Full PRE-BLESS: NO EJECUTADO (0 s de 1800).** Ni la campaña G-MUT sobre
  `src/example` ni ningún otro gate del tier; la receta vigente no llegó a
  inspeccionarse en ejecución porque la puerta previa no está conforme.
- No se ejecutaron supresiones, cambios de umbral, reparaciones de producto ni
  ampliaciones de alcance en ningún punto de la cadena.

## 7. Verificación, presupuestos y límites

| Puerta | Presupuesto | Consumido | Resultado |
|---|---|---|---|
| Preflight + controles de ratificación | 120 s | ≈15 s de ejecución (revisión documental aparte) | Ratificación CONFORME (verifier) |
| Q-ACCMUT | 900 s exteriores | ≈60 s propios + verifier | 47/47; APROBAR-QACCMUT-FINAL |
| Cobertura + CRAP | 900 s | ≈305 s (incluye intento inválido 139 s y verifier) | Líneas 91 % PASS; rama 89,94 % **NO PASS** → parada |
| DRY | 600 s | 0 s | NO EJECUTADO |
| Full y complementarios | 1800 s | 0 s (pendiente el fast documental) | NO EJECUTADO |

Los intentos inválidos y las reejecuciones del verifier están incluidos; no se
transfirieron saldos ni se ampliaron topes.

## 8. Próxima autorización mínima

Disposición humana de la cláusula de rama sobre los 35 arcos no tomados
(31 trasladados AST-idénticos + 4 de módulos nuevos del incremento): cubrirlos
con tests fieles, declarar su tratamiento por identidad como deuda, u otra vía
que el humano apruebe. Con esa disposición cerrada, reanudar: DRY
estructural/plantillas/tokens sobre el candidato final → full PRE-BLESS (con
G-MUT de `src/example` dentro de su presupuesto) → revisión protegida del
drift → bless. Nada de esto se autoriza aquí; no se bendice, no hay merge,
bump/lock, tag ni release, y no se declara cierre integral AC1/beta.3.
