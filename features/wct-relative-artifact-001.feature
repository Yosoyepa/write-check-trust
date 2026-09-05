# wct-relative-artifact-001
Feature: El artefacto de aceptación es reproducible entre checkouts

# El mismo feature genera el mismo artefacto sin importar la ruta
# absoluta del checkout (bug observado en PR-C con worktrees).

  Scenario: Dos checkouts del mismo feature generan artefactos idénticos
    Given el mismo feature en dos roots distintos
    When se genera el artefacto de aceptación en cada uno
    Then los dos artefactos son byte-idénticos
    And el source del IR es la ruta relativa al root
