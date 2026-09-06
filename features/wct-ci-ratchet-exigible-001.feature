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
