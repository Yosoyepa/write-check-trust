# wct-accept-nonvacuous-001
Feature: La aceptación por mutación no aprueba sin trabajo aplicable

  # Un veredicto verde exige mutaciones ejecutadas; cero mutaciones es
  # sin-datos, no éxito.

  Scenario Outline: Veredicto según mutaciones ejecutadas
    Given un escenario de aceptación con <examples> filas de Examples
    When corre la mutación de aceptación sobre el escenario
    Then el veredicto es <veredicto> porque ejecutó <ejecutadas> mutaciones

    Examples:
      | examples | ejecutadas | veredicto                     |
      | 0        | 0          | falla citando TEST-010        |
      | 2        | 2          | según sobrevivientes          |

  Scenario: Los escenarios sin Examples quedan visibles sin bloquear solos
    Given un feature con un escenario parametrizado y otro sin Examples
    When corre la mutación de aceptación del feature
    Then el reporte advierte la vacuidad del escenario sin Examples
    And el veredicto se decide por las mutaciones ejecutadas en total
