# Cierre TEST-004, DRY y full PRE-BLESS — AC1 / PR #53 (2026-09-16)

Registro consolidado del encargo «cerrar el déficit de cobertura de ramas con
el mínimo test conductual útil y, si queda conforme, continuar hasta full
PRE-BLESS». Predecesor: `CALIFICACION-FINAL-PREBLESS-2026-09-16.md` (parada en
313/348 = 89,94 %). Candidato compuesto y medido:
`67e21b2a051cf837c2c74512335609d5bf716100` = `35ce654` (corte documental
anterior) + **un commit de test** (`tests/unit/test_sast_targets.py`, +8
líneas, 1 test). Sin cambios de producto, features, contratos, gobernanza,
umbrales, baselines, configuración de coverage, dependencias, lock ni versión.

**Estado global: cadena conformada hasta full; full ejecutado con dos rojos —
el esperado (G-META-1, drift) y un hallazgo real nuevo (G-SAST-SEMGREP) que
queda entregado para decisión humana.** TEST-004 queda CUMPLIDO (ramas
314/348 = 90,23 %), DRY conforme, y el tier full corrió sus 34 gates: 32 PASS,
G-META-1 FAIL (drift pre-bless conocido, 37 = 7+30) y **G-SAST-SEMGREP ERROR
«ruta distinta no compensa»**, primera vez que este gate se ejecuta sobre el
árbol real (solo vive en el tier full). No se declara full verde, ni PASS de
G-MUT global, ni cierre integral AC1/beta.3. No se ejecutan
bless/update-manifest, merge, bump/lock, tag ni release. El documento ajeno
`PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md` permanece intacto, sin
seguimiento y fuera del incremento (sha256 `dedda9f3…` medido en preflight).
La evidencia bajo `build/tmp/` es temporal: no es custodia durable.

## 1. Preflight e identidades

- Worktree `build/tmp/beta3-ac1-r2-integration`: HEAD de partida
  `35ce6543554fc535f1a6745e29f718c18edc081a` = `origin/codex/beta3-ac1-r2-integration`
  = `headRefOid` de la PR #53 (OPEN), sin avances remotos; índice vacío salvo
  el untracked ajeno citado; `git diff --check` limpio.
- Base exacta comprobada, no supuesta: `git ls-remote origin main` =
  `932c835ac0eeb75010ec7a1071315b1c51f78eb6` y `git merge-base origin/main HEAD`
  = `932c835…` (la base canónica coincide con el merge-base real).
- Copias aisladas bajo `build/tmp/cierre-test004-full-prebless/`:
  `candidate` (35ce654 → commit de test `67e21b2` para congelar el compuesto),
  `variant` (sensibilidad) y `scratch` (campaña mutmut fría de corroboración),
  cada una con raíz Git propia y `origin/main` corregido al valor remoto real.
- Runtime acreditado: `.venv` del worktree — Python 3.13.14, pytest 9.1.1,
  mutmut 3.7.0, coverage 7.15.4, diff-cover 10.5.1, crap4py 0.1.1, jscpd 5.0.16
  (caché npx, sin instalación), semgrep 1.174.0 — con `PATH` absoluto
  (incluye el bin de la caché npx y `/home/jandradeu/.local/bin`),
  `PYTHONPATH=$PWD:$PWD/src` y `UV_NO_SYNC=1`. Nada instalado; runtime no
  modificado.

## 2. Inspección de los cuatro arcos nuevos y selección

Arcos no tomados en módulos nuevos del incremento (inventario de
`CALIFICACION-FINAL-PREBLESS` §4, verificado sobre el LCOV fresco):

| Arc | Sitio | Contrato aplicable | Entrada y oráculo | ¿Alcanzable desde la allowlist? |
|---|---|---|---|---|
| `parsing.py:71→72` | `_Parser._row`: fila de Examples sin escenario activo → `raise ValueError(path:número)` | Rechazo de entrada malformada con localización | Feature con fila `|…|` fuera de un Outline; excepción con ubicación | Su hogar natural de test (`test_accept_pipeline.py`) está fuera de la allowlist; no seleccionado |
| `pytest_receipt.py:39→40` | `_Recorder.pytest_collectreport`: `report.passed` falso → append error | «Collection failures and skips invalidate the attempt» | Recibo con reporte de colección fallido; `errors` no vacío | Su hogar natural (`test_accept_pytest.py`) está fuera de la allowlist; no seleccionado |
| `semgrep_scope.py:36→37` | `relative_path`: no-`str` → `None` | Guarda de tipo documentada («None si el tipo o la forma no valen») | Llamada directa con no-string; retorno `None` | Cubrible, de menor valor conductual; no seleccionado |
| `semgrep_scope.py:98→99` | `_python_file`: candidato `*.py` que **no es fichero regular** → excluido | Docstring del módulo: «E = los *.py **regulares**» | Directorio llamado `decoy.py` bajo `src/`; `required_sources` lo omite | **SELECCIONADO** — productor real, filesystem real, esperado independiente, sin dobles, sin ramas nuevas en el test |

Ningún arco sin cubrir se trató como defecto del producto; no se usaron
streams `None` ni estados incompatibles con el productor real; sin
pragma/no-cover, supresiones ni exclusiones.

## 3. Test añadido y su verificación

`tests/unit/test_sast_targets.py::test_entrada_py_que_no_es_fichero_queda_fuera`
(8 líneas, familia de los tests de alcance existentes; sha256 del fichero
`d86971913425868c2403fafbd438ef2f71475f8cc79ffa5e537bd38e7b2cb252`, byte-idéntico
entre worktree y candidato medido):

- Ejecuta el SUT real (`required_sources` → `_python_files` → `_python_file`,
  reexportado por la fachada `semgrep.py`) sobre un árbol real en `tmp_path`;
  oráculo de lista esperada independiente (`["src/a.py"]`); determinista;
  recursos en `tmp_path`; sin `assert_called` ni mocks; sin ramas nuevas en el
  fichero (el denominador diferencial no cambia).
- **Nace verde como caracterización** (el original cumple su contrato); no se
  fabricó rojo. Sensibilidad demostrada en copia aislada (`variant`) contra
  dos variantes defectuosas plausibles, con mecanismo registrado de
  **control manual temporal exacto** (sin campaña ni IDs nuevos):
  1. Guarda `is_file` **retirada** (2 líneas borradas): el test cae ROJO con
     la causa contractual exacta — `src/decoy.py` incluido en el exigible.
  2. Flip exacto del diff del mutante histórico `x__python_file__mutmut_12`
     del lote FIDELIDAD (`if not candidate.is_file():` → `if
     candidate.is_file():`): el test **solo** cae ROJO.
- Focales: **110 passed** (109 + 1). Colección: **692 tests** (691 + el nuevo;
  1 property separado).
- Impacto en lotes de mutación: los 18 IDs `x__python_files__mutmut_1..18` del
  lote GS-2 sellado **no tocan** la rama `is_file` (verificado por diff de
  cuerpos contra `mutmut_orig`); el ID que la muta es `x__python_file__mutmut_12`
  (lote FIDELIDAD), históricamente **killed**; el test nuevo no cambia ningún
  veredicto (un test más solo puede matar más, nunca resucitar); los brutos
  GS-2 (102+16) y FIDELIDAD (85+2) quedan intactos. No se ratifican
  equivalencias nuevas ni se regeneran inventarios.

## 4. Verifier de fidelidad (antes de aceptar la sensibilidad)

`APROBAR-TEST-Y-CADENA-PARA-FULL`
(`build/tmp/verifier-test004-full/VEREDICTO.md`): commit de test aislado como
único delta; SUT real sin mocks; arco 98→99 tomado en el LCOV; métrica
recalculada por dos vías (348/314 = 90,23 %); ambas sensibilidades
re-ejecutadas con sus causas; monotonía de lotes; 8/8 hashes de vigencia
Q-ACCMUT; CRAP/DRY artefactos conformes. Reservas no bloqueantes: veredictos
de mutación por lectura (instruido), baseline tpl por valor corriente.

## 5. Vigencia de Q-ACCMUT

Solo cambió un test unitario fuera del alcance de la campaña de aceptación
(que ejecuta únicamente el generado privado). Los 8 anclajes del acta
(`process.py` `1a25984b…`, `campaign.py` `686070cd…`, `pytest_receipt.py`
`d4f136ae…`, feature `0b9aa268…`, `steps.py` `5b6863ed…`,
`campaign_steps.py` `f81b238d…`, `protocol_runner.py` `35ad31a1…`,
`pyproject.toml` `c3a1b3e7…`) midieron idénticos
(`hashes-vigencia-qaccmut.txt`). **El 47/47 de `CALIFICACION-FINAL-PREBLESS`
permanece vigente como ejecución histórica separada; no se declara ejecución
nueva ni se repitió la campaña.** Sin invalidantes.

## 6. Cobertura fresca y CRAP sobre el candidato compuesto

- Suite canónica (`pytest --cov --cov-branch --cov-report=lcov:… --cov-fail-under
  74.5 -q -m "not property"`): **691 passed, 1 deselected**, exit 0, 141 s;
  total **88,09 %**. LCOV fresco sin herencia: sha256
  `88ae9c640d832fd9196ea1886b5eba74fa2df98d3f223ebbb4696b263d9868ab`.
- Diferencial canónico de líneas (`diff-cover … --compare-branch origin/main
  --fail-under 90 --include-untracked`): **91 %** (1179 líneas, 96 ausentes),
  exit 0 → PASS.
- **Cláusula de rama de TEST-004** (método canónico de los encargos
  anteriores, `branch_metrics.py` sobre `git diff -U0 932c835...HEAD -- '*.py'`
  y el LCOV fresco): **348 arcos / 314 tomados = 90,23 % ≥ 90 → PASS**
  (90,2299 %, sin redondeo favorable). **El denominador sigue siendo 348
  porque el test no añade arcos** (sin `if/for/with`); el numerador sube
  313→314 exactamente por el arco 98→99 tomado. `semgrep_scope` queda 39/40
  (resta el arco 36 de `relative_path`, no seleccionado).
- Ratchets (`wct ratchet check`): «Todos los ratchets se mantienen.», exit 0.
- CRAP: canónico `src` exit 0; focal `process.py` máx. 6,0 y
  `semgrep_scope.py` máx. 5,4 (`_python_file` 5,0 al 100 %) → todo ≤ 6;
  suplementario `tools/wct` exit 1 con **66 violaciones clasificadas
  54 preexistente + 3 preexistente_sin_cambios + 9 trasladada_mecanicamente**
  (`crap-classification.json`, clasificador por fingerprint AST contra la base
  `932c835`): **0 nuevas, 0 modificadas; la frontera de las 12 no cambia de
  premisa**. El rojo suplementario se informa con su alcance real y no se
  transforma en verde.

## 7. DRY

| Receta | Resultado |
|---|---|
| Estructural `wct dry` (scope `src`) | 0 candidatos, exit 0 |
| Plantillas `wct dry --normalized` | 17 candidatos = baseline 17, exit 0 |
| Tokens `jscpd src tools --exit-code 1` (jscpd 5.0.16, caché npx, sin instalación) | **0 clones**, exit 0 |
| Suplementario `tools/wct` (`analyze` con rglob de 92 ficheros) | 354 unidades, **19 pares = 17 EXTRACT + 2 LEAVE_ALONE**, idéntico al histórico de `FIDELIDAD-TRANSPORTE-Y-FRONTERA-CRAP` — 0 hallazgos nuevos |

Sin deduplicación de matrices de casos, sin supresiones, sin baselines
elevadas. DRY CONFORME.

## 8. Full PRE-BLESS (tier canónico, copia aislada)

Receta inspeccionada antes de ejecutar: `TIERS["full"]` = 34 gates (los 21 de
commit + `G-COV-TOTAL`, `G-MUT`, `G-CRAP`, `G-CC`, `G-DRY`, `G-DRY-TOK`,
`G-DRY-TPL`, `G-LCOM`, `G-SAST-SEMGREP`, `G-AUDIT`, `G-SBOM`, `G-DOC`,
`G-REDTEAM`); `G-MUT` = `mutmut run` + `results --all true` con
`[tool.mutmut] source_paths=["src/example"]` y selección focal de 4 ficheros
de test; sin escritura de manifests protegidos ni cambios de scope/config.
`environment_required.full` = []. Ejecutado con PATH que incluye el bin de
jscpd. Resultado bruto: **34 gates = 32 PASS · 0 SKIP · 2 FAIL/ERROR; exit 1;
310 s** (`build/tmp/full-tier.log`).

### 8.1 G-MUT — campaña ejecutada de verdad

G-MUT: **PASS — «clasificación del motor: 43/43 killed»** en 3,8 s. El tiempo,
por sí solo, exigía corroboración: `mutants/` es gitignored y no trackeada
(`git ls-files mutants` vacío), creada por el propio gate en esa ventana.
Corroboración con **campaña fría cronometrada** en copia `scratch` (mismo
commit `67e21b2`, `src/` y `tests/` byte-idénticos): forced-fail test +
**43/43 killed (🎉 43, 0 🫥/⏰/🤔/🙁/🔇), 209,90 mutaciones/s con 22 CPUs**,
`mutmut results --all true` = 43 IDs únicos `example.*` killed, 0 survived,
0 timeout, 0 no-tests. **Fue campaña ejecutada real** (paralelismo de mutmut
3.7.0 sobre una selección focal muy rápida), no `changed_functions=0` ni vía
diferencial. No sustituye la adjudicación AC1 ni califica `tools/wct`; los
928 IDs históricos siguen sin ejecutar; no se tocaron manifests.

### 8.2 G-SAST-SEMGREP — ERROR real diagnosticado (hallazgo nuevo)

`G-SAST-SEMGREP ERROR «ruta distinta no compensa»` (4,4 s). Diagnóstico con
evidencia:

- El gate corre `semgrep --quiet --error --severity ERROR --config
  governance/semgrep --json` **sin targets explícitos** y contrasta
  `paths.scanned` con E = `required_sources` (src+tests+tools: **169
  ficheros** — 93 tools + 67 tests + 9 src).
- semgrep 1.174.0 omite por sus exclusiones por defecto **todo `tests/**`**:
  corridas manuales idénticas en candidate y worktree dan **103 scanned
  (9 src + 93 tools + 1 governance), 0 de tests/**
  (`semgrep-candidate.json`, `semgrep-worktree.json`).
- El veredicto del gate (`semgrep_verdict.py:75`) trata las omisiones como no
  compensables → ERROR con `omitida: …` (67) y `S_extra (diagnóstico, no
  compensa): governance/lint/vulture_whitelist.py`.
- **No es preexistente de otro gate ni un artefacto del candidato**: es la
  primera vez que este gate se ejecuta sobre el árbol real — no está en el
  tier `commit` (los 20 PASS + G-META-1 históricos no lo incluían; log
  `commit-gate-final.log`) y los tests unitarios que lo cubren usan árboles
  plantados con una única fuente. El comportamiento es idéntico en worktree y
  copia, y reproducción garantizada en cada corrida.
- **Requiere decisión humana y cambio de producto/config en un encargo propio**
  (p. ej. invocar semgrep con los targets de E explícitos, o ajustar la
  configuración de exclusiones): **fuera del alcance de este encargo**
  («no cambiar scope, reglas ni configuración»; «no reparación fuera de
  alcance»). Se entrega el hallazgo y se detiene la reparación.

### 8.3 G-META-1

FAIL por el drift protegido pre-bless — rojo conocido y esperado; no se
suprime ni se convierte en PASS (§10).

## 9. Verificación integrada sobre el candidato final

| Verificación | Resultado |
|---|---|
| `git diff --check` | Limpio |
| Colección | **692** tests, conciliada (+1 = el test nuevo) |
| Property separado | 1 passed, 691 deselected, exit 0 |
| Focales (allowlist) | **110 passed** |
| Fast (`wct gate --tier fast`) | **7/7 PASS**, exit 0 |
| Tier commit (dentro del full, 21 gates) | 20 PASS + G-META-1 FAIL (drift) |
| Ratchets / G-INTROVERT / G-ACCEPT | PASS / PASS / PASS (tabla full) |
| Integridad (`wct integrity check`) | exit 1, **drift 37 = 7 modificadas + 30 nuevas**, re-medido por rutas y hashes (no asumido) |
| Intento inválido preservado | `uv run --project` en la copia terminó en timeout por una sonda de dispositivo del host (no del repo): `build/tmp/integrity-candidato.txt`; sustituido por la invocación directa con el venv |

## 10. Verifier integrado final

`APROBAR-CADENA-COMPLETA-PREBLESS`
(`build/tmp/verifier-integrado-full/VEREDICTO.md`). Re-ejecutó: identidad y
diff del candidato; campaña G-MUT en scratch (43 IDs killed, 0 demás estados,
árbol byte-idéntico); `branch_metrics` 348/314; hashes de vigencia 8/8;
aritmética del ERROR de semgrep (E=169, omitted=67, S_extra={vulture_whitelist});
colección/property/fast/integridad; conteos CRAP 66=54+9+3 y DRY
354/19=17+2. Reservas no bloqueantes: la corroboración de G-MUT fue campaña
fría equivalente, no re-campaña in situ; semgrep no re-ejecutado (JSONs y
código del veredicto bastan); el árbol sigue rojo en full y esto no autoriza
bless/merge.

## 11. Presupuestos

| Frente | Tope | Consumido |
|---|---|---|
| Diagnóstico, focales y sensibilidad (§5) | 300 s | ≈25 s (incluye sonda inválida por indentación del parche, preservada y corregida) |
| Cobertura + CRAP (§7) | 900 s | ≈145 s propios + verifier ≈180 s |
| DRY (§8) | 600 s | ≈15 s |
| Full y complementarios (§9) | 1800 s | ≈340 s (full 310 + scratch 5 + diagnóstico semgrep/integridad) + verifier integrado ≈240 s |
| Q-ACCMUT (§6) | sin ejecución autorizada | 0 s (vigencia documental) |

Intentos inválidos incluidos y preservados con su causa; sin transferencias de
saldo.

## 12. Próxima autorización mínima

1. **Decisión humana sobre G-SAST-SEMGREP en el árbol real** (hallazgo nuevo,
   no cubierto por ninguna disposición anterior): elegir la vía — invocación
   con los targets de E explícitos, ajuste documentado de exclusiones, u otra
   — y autorizarla como cambio de producto/config en un encargo propio con su
   revisión. Mientras tanto, el tier full sigue con ese ERROR y **no hay full
   verde pre-bless**.
2. Con G-SAST-SEMGREP resuelto: revisión humana protegida del drift (E9:
   37 = 7+30), bless, y POST-BLESS. Nada de bless/update-manifest, merge,
   bump/lock, tag, release ni declaración de cierre integral AC1/beta.3 se
   ejecuta o autoriza aquí.
