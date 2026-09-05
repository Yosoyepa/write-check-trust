# wct-gmut-full-001
Feature: G-MUT pertenece a un tier con presupuesto medido

# El perfil de capacidades de PR-D destapó que G-MUT no vivía en ningún
# tier; con 1.9s medidos se une al tier full.

  Scenario: El tier full incluye la mutación del ejemplo
    Given el tier full del repo
    When se consulta la membresía de G-MUT
    Then pertenece al tier full y a ningún otro
    And el perfil de capacidades lo refleja sin cambios manuales

  Scenario: El contrato del gate es real
    Given un fixture cuyos tests dejan sobrevivir un mutante
    When corre la función de gate G-MUT sobre el fixture
    Then el gate FALLA — el exit code de mutmut lo respalda
