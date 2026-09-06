# SPEC-G3a-2 — El ratchet exigible corre en CI sobre el LCOV que ella produce

Estado: **AUTORIZADA (Puerta 1, yosoyepa 2026-09-05: diff exacto + Gherkin
definitivo con comentarios) y EJECUTADA en este turno — sin commit; staging
propuesto para evaluar bless**. El workflow es ruta protegida (SEC-005):
G-META-1 queda rojo POR DISEÑO hasta el bless.

Trazabilidad: READINESS.md Etapa A (RELEASE-BETA2, hallazgos R02/R03),
ADR-G3a-02 §§1-9 (contrato exigible, entregado en G3a-1), ADR-G3a-03
(addenda de este turno: separación property). Padre del contrato:
`f449cd6` (G3a-1 fusionado, PR #39).

## Frontera

DENTRO: `.github/workflows/quality.yml` (un paso modificado, dos pasos
nuevos), `features/wct-ci-ratchet-exigible-001.feature` (texto definitivo
en [GHERKIN-G3a-2](../GHERKIN-G3a-2.md), validado parse+ir-dry; SIN steps
de ejecución — G-ACCEPT valida parse+ir-dry sobre todas las features y la
evidencia ejecutable vive en la suite unit, precedente de las features
`wct-*`), y tests de contrato del workflow en `tests/unit/`.

FUERA: `tools/wct/**` (el comando exigible ya existe y está probado desde
G3a-1 — cero cambios de código productivo), tiers/baselines/manifiestos,
`full-hardening.yml` y `adoption-smoke.yml`, G1b, PR #33, #12/#35.

## Diff exacto propuesto (objeto de la aprobación)

```diff
--- a/.github/workflows/quality.yml
+++ b/.github/workflows/quality.yml
@@ jobs.commit-gates.steps, tras "Run commit tier" y el audit de pip-audit
       - name: Generate branch coverage
-        run: uv run pytest --cov --cov-branch --cov-report=lcov:build/coverage/lcov.info -q
+        run: uv run pytest --cov --cov-branch --cov-report=lcov:build/coverage/lcov.info -q -m "not property"
+      - name: Require measured ratchets
+        run: uv run wct ratchet check --require coverage-total,docstring-coverage
+      - name: Run property tests separately
+        run: uv run pytest -q tests/property
```

Orden resultante del job `commit-gates` (los pasos no tocados quedan
idénticos): … → Run commit tier → pip-audit → **Generate branch coverage
(sin property)** → **Require measured ratchets** → **Run property tests
separately** → Require 90 percent coverage on the pull-request diff
(diff-cover, intacto) → accept mutate → redteam.

Justificación de cada línea:

1. **`-m "not property"` en el productor** alinea el workflow con la
   receta productiva `_COVERAGE_TOTAL_COMMAND` (`ratchet/measure.py`,
   fijada por los tests 0c/0f de G3a-1) y con TEST-008: los property no
   participan de coverage. Hoy el workflow es el ÚNICO lugar que los
   incluye — una segunda definición de la receta, exactamente el patrón
   F05 que G3a viene cerrando.
2. **`Require measured ratchets`** consume el artefacto que el paso
   anterior acaba de escribir en el mismo job, sin restauración
   intermedia: la frescura la acredita el orden productor→consumidor con
   checkout limpio (ADR-G3a-02 §2). Lista explícita
   `coverage-total,docstring-coverage` — las dos mediciones dependientes
   de artefacto/herramienta — conservando todas las comparaciones
   estáticas por la aditividad de G3a-1. `all` amplía la obligación si el
   inventario cambia; no es necesario para esta frontera. Sin
   `continue-on-error` ni `if: always()`: un productor fallido detiene el
   job ANTES del consumo — nunca se consume un residuo.
3. **`Run property tests separately`** preserva la ejecución que hoy
   sucede DENTRO del paso de cobertura: G-TEST de commit corre solo
   `tests/unit tests/integration -m "not property"`
   (`gate/runner.py:369-372`), así que excluir property del productor sin
   este paso dejaría a los property sin ejecución alguna en CI. Un
   property defectuoso pone roja la CI en su paso propio sin contaminar
   el LCOV exigible.

## Evidencia de viabilidad (medida este turno, main `f449cd6`)

| Medición | Resultado |
|---|---|
| Productor con `-m "not property"` (LCOV borrado antes) | 333 passed, 1 deselected, exit 0, 117.4 s |
| Consumidor `wct ratchet check --require coverage-total,docstring-coverage` sobre ese LCOV | `medidas 2 de 2 exigibles`, exit 0, 1.12 s (ambas ≥ baseline: 74.5 / 34.0) |
| `pytest -q tests/property` aislado | 1 passed, 0.2 s |
| Costo agregado local de los pasos nuevos | ≈ 1.3 s (el tiempo total del job se reporta del run real de CI — criterio 5) |

Conclusión: el diff no pone main en rojo con los baselines vigentes. No
se manipuló ningún baseline para obtener este verde.

## Tests (TDD — escritos primero; evidencia en la sección anterior)

En `tests/unit/test_workflow_contract.py`. Fueron escritos ANTES del diff
del workflow y corridos contra el workflow actual: el rojo observado y sus
causas están registrados arriba.

- **T1** `test_coverage_step_matches_productive_recipe` (escenario 1):
  leer `.github/workflows/quality.yml`, localizar el paso "Generate
  branch coverage", y comparar LANZADOR y ARGUMENTOS por separado: el
  comando del workflow empieza con `uv run` (lanzador), y los tokens
  restantes — a partir de `pytest` — deben igualar token a token el
  `shlex.split` de `_COVERAGE_TOTAL_COMMAND` (que empieza en `pytest`,
  sin lanzador). La comparación ingenua de las dos cadenas completas
  fallaría incluso con el workflow correcto por ese prefijo. El marcador
  queda preservado por shlex: `-m "not property"` separa como
  `['-m', 'not property']` — la cadena citada es UN token en ambas
  recetas, y un `.split()` ingenuo que la aplanara en tres no puede
  pasar la igualdad (lección de la corrección del comando productor en
  G3a-1). Cierra el
  triángulo de la receta: G3a-1 fijó builder↔comando productivo; este
  fija workflow↔comando productivo. Si alguien edita el YAML, la suite
  lo detecta sin esperar al bless.
- **T2** `test_required_ratchets_step_follows_producer` (escenario 2): el
  paso "Require measured ratchets" existe, su índice es POSTERIOR al del
  productor, su comando se pina COMPLETO por igualdad shlex —
  `["uv","run","wct","ratchet","check","--require",
  "coverage-total,docstring-coverage"]` — (hallazgo humano 1: un eco que
  repita los nombres sin ejecutar WCT no puede pasar), la lista exigida
  es exactamente el par aprobado Y subconjunto del inventario productivo,
  el paso es un bare run step (allowlist `{name, run}`) y el consumidor es
  ADYACENTE al productor (ronda 4: la aserción de orden era más débil que
  el claim «sin restauración intermedia» del docstring — un paso forjador
  insertado entre ambos pasaba).
- **T3** `test_property_tests_run_separately` (escenario 4): existe un
  paso posterior "Run property tests separately" que ejecuta
  `pytest -q tests/property`, y el paso de cobertura excluye property
  (coherente con T1; la aserción existe para que el mensaje de fallo
  nombre la pérdida de ejecución, no solo la divergencia de receta).
- **T4** `test_contracted_steps_execute_normally` (escenario 3): los
  tres pasos del contrato —productor, consumidor y property— son
  exactamente `{name, run}` (allowlist terminal `_is_bare_run_step`,
  fix del MAYOR de la ronda 3: un `shell` neutralizador a nivel paso
  hacía triunfar el comando pineado sin ejecutarlo). Cualquier clave
  extra —`if` (desactiva o condiciona: `failure()` ejecuta SOLO tras
  fallos), `continue-on-error`, `shell`, `env`, `working-directory`,
  `timeout-minutes`…— rompe el contrato, sin intérprete de expresiones
  de Actions. Junto con T2 (posición + comando completo), este es el
  mecanismo estructural que garantiza la consecuencia del escenario: un
  productor fallido detiene el job ANTES del consumidor (semántica por
  defecto de GitHub Actions). La identidad del productor es productiva
  (`LCOV_ARTIFACT`).
- **T5** cadena productor→consumidor sobre artefactos reales (escenario 5):
  en un workspace fixture, T5a verifica el cableado de rutas — el destino
  `--cov-report=lcov:` del paso productor del workflow es la ruta del
  artefacto que el ratchet lee por defecto (constante productiva de
  `ratchet/measure.py`) — y T5b/T5c ejercitan la función productiva
  `check_ratchets(required=...)` contra artefactos que el productor pudo
  dejar: LCOV válido por DEBAJO del baseline de coverage-total del
  fixture → falla nombrando la métrica (control negativo); LCOV válido
  por ENCIMA → pasa. El artefacto inválido NO se re-testea aquí: ya es
  matriz de G3a-1 (tests 0b/0e — MIN-008: no duplicar tablas de casos).
- **T6** `test_commit_gates_job_executes_normally` (MAYOR-1 del verifier
  ronda 2, misma clase que los hallazgos humanos un nivel arriba): el
  JOB commit-gates corre incondicional — sin `if` (desactivaría el job
  entero, consumidor incluido), sin `continue-on-error` (perdonaría el
  fallo de todo el job), sin `defaults.run.shell` custom (un shell
  neutralizador hace triunfar cada `run` sin ejecutar nada) — y sus
  triggers incluyen `pull_request` y `push`.
- **Controles defectuosos** `test_defective_step_mutations_are_detected` /
  `test_defective_job_mutations_are_detected`: mutaciones derivadas de
  pasos y job REALES — eco con nombres válidos (hallazgo 1), `if:
  false`/`failure()` (hallazgo 2), productor perdonado, job
  desactivado/perdonado/shell neutralizado (MAYOR-1). Ningún dict
  sintético sin anclaje al workflow real.

Nota de alcance: NO se añade un test end-to-end que ejecute el productor
real (≈2 min) — duplicaría el costo de la suite por evidencia que la
propia CI produce en cada push. El end-to-end queda como paso de CI y
como evidencia de la matriz de release (PLAN.md, RELEASE-BETA2).

## Evidencia de implementación (2026-09-05, main `f449cd6` + working tree)

TDD con rojo honesto — `tests/unit/test_workflow_contract.py`, 9 tests:

- **Pre-diff (workflow actual): 4 FAILED · 5 PASSED.**
  - T1 rojo por la razón correcta: desigualdad de tokens en exactamente
    `-m`/`not property` (`['pytest', …, '-q'] == […, '-m', 'not property']`).
  - T2/T3/T4 rojos porque los pasos "Require measured ratchets" y "Run
    property tests separately" no existen (KeyError/StopIteration).
  - **Defecto propio encontrado y corregido ANTES del diff**: la primera
    versión de `_positions` hacía `step["name"]` sobre pasos sin `name`
    (checkout/setup-python) y T2/T3 fallaban por KeyError ajeno al
    contrato. Corregido a filtrar pasos sin nombre; el rojo quedó
    atribuido al paso ausente, no al helper.
  - Los 5 verdes pre-diff son los que el encargo exigía con control
    defectuoso: cableado de rutas (T5a) + su control (productor que
    escribe otra ruta → detectado), perdones (T4-estructural quedaba
    cubierto por el rojo de consumidor ausente) + su control
    (`continue-on-error`/`always()` mutados → `_pardons` se enciende),
    y la cadena bajo/sobre baseline (T5b/T5c — sensibilidad inherente:
    si `check` dejara de fallar ante 50% < 74.5, el test enrojece).
- **Post-diff: 9 passed.** El diff aplicado es byte a byte el aprobado
  (verificado con `git diff`).
- **La doble red de G3a-1 cazó a los tests propios (episodio honesto):**
  la primera versión de T2/T3/T4 y del control de perdones quedó
  clasificada INTROVERTED por el analizador (4.0 en la métrica repo;
  `test_repo_introverted_ratchet_holds_baseline` en rojo) — aserciones
  estructurales sin trazado a ningún valor del SUT. Corregido con
  identidad productiva REAL, no decorativa: T2 valida la lista exigida
  contra `REQUIRED_INVENTORY` (CI solo puede exigir exigibles que
  existen), T3 deriva la marca de exclusión de la receta productiva (la
  causa del paso separado), T4/control anclan la identidad del productor
  a `LCOV_ARTIFACT` (es el paso que escribe el artefacto del ratchet) y
  mutan el paso REAL. Resultado: 9/9 extroverted, métrica repo 0.0, sin
  tocar el analizador ni sus umbrales. Es el incidente #37/#38
  reproduciéndose y siendo bloqueado por la regresión — exactamente lo
  que G3a-1 prometía.
- Feature creada en `features/wct-ci-ratchet-exigible-001.feature`
  (texto definitivo CON comentarios): `accept parse` exit 0,
  `accept ir-dry` count 0 en la ruta real.
- **Verifier independiente (PROC-005): APROBADO CON HALLAZGOS** —
  MAYOR-1 (T2 verificaba subconjunto, no la lista exacta: una
  debilitación del `--require` pasaba), MINOR-2 (checkbox de DoD
  prematuro), MINOR-3 (control de ruta sintético). Los tres corregidos
  en el turno (T2 ahora pina `["coverage-total", "docstring-coverage"]`
  además de validar contra `REQUIRED_INVENTORY`; el control de ruta
  muta el `run` real). Post-fixes: 9/9 passed · 9/9 extroverted ·
  repo 0.0 · fast 7/7.

## Ronda de corrección pre-bless (hallazgos humanos + verifier ronda 2)

Revisión humana con sondas EN MEMORIA (el YAML no se tocó) encontró dos
evasiones; el verifier de la ronda 2 reprodujo ambas cerradas y halló
una tercera de la misma clase un nivel arriba:

1. **Hallazgo humano 1 — consumidor sustituido por eco**
   (`uv run echo --require …` pasaba T2: verificaba nombres, no el
   comando). Fix: T2 pina el comando COMPLETO por igualdad shlex.
2. **Hallazgo humano 2 — consumidor desactivado/condicionado**
   (`if: ${{ false }}` / `if: ${{ failure() }}` pasaban: `_pardons` solo
   buscaba `always()`/`continue-on-error`). Fix evolucionado a allowlist
   terminal (ver ítem 5): los pasos del contrato son exactamente
   `{name, run}` — sin intérprete de expresiones de Actions.
3. **MAYOR-1 (verifier ronda 2) — nivel job**: `jobs.commit-gates.if:
   false`, `continue-on-error` de job, `defaults.run.shell`
   neutralizador y `on:` reducido pasaban la suite entera. Fix: T6
   `test_commit_gates_job_executes_normally` (predicado de job + triggers
   pull_request/push).
4. **MINOR-3 (verifier ronda 2) — residual**: `working-directory` y
   `env` a nivel paso no estaban pineados. CERRADO estructuralmente por
   el allowlist del ítem 5 (ninguna clave extra cabe en un paso
   contratado).
5. **MAYOR (verifier ronda 3) — `shell` a nivel PASO**: un
   `shell: "/bin/true {0}"` en el paso del consumidor neutralizaba el
   comando pineado sin romper ningún test (el efecto más grave: solo el
   exigible muere, el resto de la CI sigue verde). **Fix terminal**:
   allowlist de claves por paso — `_is_bare_run_step`,
   `set(step) == {"name", "run"}` para productor, consumidor y property.
   Cierra `shell`, `env`, `working-directory`, `timeout-minutes` y todo
   lo por venir: termina el juego de enumerar neutralizadores. Mismo
   Instancia verificada de esa misma frontera (ronda 5): claves de job
   no contratadas (p.ej. `env` con `PYTEST_ADDOPTS`) pasan la suite.
   Seguimiento OPCIONAL registrado por el verifier (no aplicado):
   allowlist de claves del job — el job real tiene exactamente
   `{runs-on, steps, timeout-minutes}`, así que
   `set(job) == {"runs-on", "steps", "timeout-minutes"}` cerraría la
   clase entera con la misma filosofía de `_is_bare_run_step`.
   allowlist razonado alrededor: `defaults` prohibido a nivel documento
   (heredaría a todos los jobs) y `strategy` prohibido en el job (un
   matrix vacío salta el job completo).
6. **Residual documentado (verifier rondas 3-5)**: los FILTROS de triggers
   (`push.branches`/`pull_request.branches` que nunca casen) no están
   pineados — se verifica presencia de `pull_request` y `push`, no su
   semántica de filtros. Compensación: ruta protegida (todo cambio exige
   bless de un diff visiblemente desviado) e integrity lock
   (G-META-1). Pinear la semántica de filtros equivaldría a re-pinear
   el archivo completo — fuera de esta corrección de tests.

Controles defectuosos de paso y job derivados del workflow REAL cubren
las cinco mutaciones (eco, if-false, failure(), perdón de productor, y
las tres de job). El workflow y la feature NO cambiaron: siguen byte a
byte los aprobados (verificado por el verifier en ambas rondas).
Limitación residual honesta del T1 de la ronda 1 («si alguien edita el
YAML, la suite lo detecta»): vale para el CONTRATO pineado (recetas,
comando completo, condiciones de paso/job, triggers) — no para campos no
contratados; la cobertura total del archivo la da el integrity lock
(G-META-1), no la suite.

## Aceptación (criterios de READINESS Etapa A, vinculantes)

1. LCOV ausente o inválido exigido bloquea; válido bajo baseline bloquea;
   válido sobre baseline pasa (sin manipular baselines para el verde).
2. Interrogate ausente/no medible bloquea; una métrica estática roja
   sigue roja.
3. En workspace aislado sin LCOV previo, la receta produce el artefacto
   consumido por el paso exigible (verificado este turno sobre main; se
   repite sobre el candidato en la matriz de release). Productor fallido
   no habilita publicación.
4. Property queda excluido de cobertura y conserva ejecución separada:
   commit lo excluye y no lo sustituye. Un property defectuoso pone roja
   la CI en su paso propio, sin contaminar LCOV.
5. Registrar costo del paso añadido y tiempo total del job del run real
   de CI. No atribuir a G3a-2 la investigación emparejada RG12 de
   mutación (pertenece a G1b).
6. Verifier independiente (PROC-005) sobre el diff final; bless del
   workflow (G-META-1 rojo por diseño hasta el bless); CI verde en PR y
   post-merge; el resto del árbol preservado.

## Riesgos residuales

- **diff-cover sobre LCOV sin property**: el umbral de 90 % del diff pasa
  a medirse sin el aporte de los property. Hoy hay un único test property
  (`tests/property/test_inventory_properties.py`, ejercita
  `example.domain.Inventory.reserve`, también cubierto por unit). Riesgo:
  un PR futuro cuya única cobertura viva en property. Mitigación: la
  regla es "property acompaña con su unit equivalente" (TEST-008 separa
  la verificación, no la sustituye); documentado en CHANGELOG de release.
- **`pytest -q tests/property` ejecuta todo el directorio**, no solo lo
  marcado: por diseño — el directorio ES la batería property. Si algún
  día convive con no-property ahí, el paso lo ejecutará también (fallar
  por exceso de ejecución es el fallo correcto).
- **YAML como segunda definición**: T1-T3 lo pinean, pero el pin vive en
  la suite, no en un gate propio. Un `wct` futuro podría exigir el
  workflow directamente; fuera de esta frontera.

## Presupuesto

- Implementación: tests T1-T3 + steps de aceptación + feature + diff YAML
  (≈ media jornada coder + verifier).
- CI: ≈ +1.3 s por job medido local; tiempo real reportado del run
  (criterio 5). Sin promesa de coste cero.
