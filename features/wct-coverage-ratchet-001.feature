# wct-coverage-ratchet-001
Feature: coverage-total es una métrica de ratchet auditable

  Scenario: El ratchet mide desde el artefacto que produce el gate
    Given un build/coverage/lcov.info producido por G-COV-TOTAL
    When se ejecuta la medición de coverage-total
    Then el porcentaje coincide con el TOTAL oficial de coverage.py

  Scenario: Sin artefacto la medición se abstiene en vez de mentir
    Given un árbol sin build/coverage/lcov.info
    When se ejecuta la medición de ratchet
    Then coverage-total no se reporta y la ausencia queda declarada

  Scenario: El registro humano es por métrica y deja rastro
    Given un humano autorizado con --approved-by y --reason que cita un PR
    When corre ratchet record --metric coverage-total
    Then solo el baseline de coverage-total se reescribe
    And queda registrado commit, owner y razón
