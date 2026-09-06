# GHERKIN-G3a-2 — Feature definitiva (validada parse + ir-dry)

Estado: **APROBADA (Puerta 1, yosoyepa 2026-09-05) y creada en
`features/wct-ci-ratchet-exigible-001.feature`** — verbatim, con
comentarios. Validación en la ruta real: `accept parse` exit 0 ·
`accept ir-dry` count 0. Acompaña al diff exacto de
[specs/SPEC-G3a-2](specs/SPEC-G3a-2.md), aplicado en el mismo turno.

## Texto definitivo

```gherkin
# wct-ci-ratchet-exigible-001
Feature: La CI exige ratchets medidos sobre el LCOV que ella misma produce

  # G3a-2: quality.yml alinea productor y consumidor. La cobertura se
  # genera sin property (TEST-008) y el paso exigible consume ese mismo
  # artefacto en el mismo job, sin restauración intermedia. Property
  # conserva ejecución propia: el tier commit no la ejecuta y el
  # productor la excluye, así que sin paso propio dejaría de correr en CI.

  Background:
    Given el workflow quality.yml del repositorio

  Scenario: El paso de cobertura sigue la receta productiva sin property
    When se lee el paso que genera la cobertura de rama
    Then su comando coincide token a token con la receta productiva del ratchet
    And excluye los tests marcados como property

  Scenario: El consumidor exigible sigue al productor sin perdonar fallos
    When se inspecciona la vecindad del paso que exige ratchets medidos
    Then existe un paso que exige coverage-total y docstring-coverage
    And su posición es posterior al paso que produce el LCOV
    And el consumidor no declara continue-on-error ni condición always

  Scenario: El productor de cobertura tampoco perdona su propio fallo
    When se examinan las condiciones de fallo del paso que genera la cobertura
    Then el productor no declara continue-on-error ni condición always
    And un productor fallido detiene el job antes de ejecutar al consumidor exigible

  Scenario: Los property tests conservan ejecución propia en CI
    When se listan los pasos que ejecutan baterías de tests
    Then existe un paso posterior que ejecuta tests/property
    And ese paso no genera cobertura ni toca el LCOV exigible

  Scenario Outline: El consumidor exigible decide según el artefacto producido
    Given un job cuyo productor terminó y dejó un LCOV <estado>
    When el paso exigible evalúa ese artefacto
    Then el job <resultado> con la causa nombrada

    Examples:
      | estado                 | resultado |
      | inválido               | falla     |
      | por debajo del baseline| falla     |
      | sobre el baseline      | pasa      |
```

## Validación ejecutada (2026-09-05, main `f449cd6`)

- **Rojo reproducido primero**: el texto de la ronda anterior (Given
  repetido en tres escenarios + When compartido) da `ir-dry count: 4` —
  cuatro `placeholder-variant`, los mismos que detectó la revisión
  humana.
- **Texto definitivo**: `wct accept parse` exit 0 (5 escenarios,
  background de 1 paso) · `wct accept ir-dry` **count: 0**, sin
  findings. Archivo de trabajo: `build/tmp/g3a2/` (efímero; la feature
  real se crea recién tras la aprobación).

## Decisiones de la reestructuración

1. **`Background` para el contexto común** — no una evasión del detector:
   el parser guarda el background UNA vez en el IR
   (`accept/pipeline.py:34-35`) y el ejecutor lo antepone a cada
   escenario (`tests/acceptance/steps.py:16`), así que es semánticamente
   el Given de todos los escenarios sin repetir su forma. `ir_dry`
   escanea `ir["scenarios"]`; el contexto común no colisiona consigo
   mismo.
2. **Productor y consumidor separados en escenarios propios**: la
   revisión corrigió que el Scenario Outline mezclaba "productor falló"
   con "productor terminó y dejó artefacto X". Ahora el outline SOLO
   cubre estados del artefacto con el productor terminado; el fallo del
   productor vive en su escenario, cuya consecuencia correcta es que el
   consumidor NO se ejecuta (semántica de GitHub Actions: un paso
   fallido detiene los siguientes salvo `continue-on-error`/`always()` —
   exactamente lo que los tests T2/T4 del SPEC niegan por estructura).
3. **Whens todos distintos**: cada escenario inspecciona una cosa
   distinta del workflow (paso leído, vecindad del consumidor,
   condiciones del productor, pasos que ejecutan baterías, evaluación
   del artefacto).
4. **Sin steps de ejecución**: precedente de las features `wct-*` — el
   contrato se valida con G-ACCEPT (parse + ir-dry sobre todas las
   features); la evidencia ejecutable vive en la suite unit (T1–T5 del
   SPEC). `accept mutate` de CI muta `features/example.feature`.
