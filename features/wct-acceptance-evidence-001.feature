Feature: Evidencia causal de mutacion de aceptacion
  Scenario Outline: Distinguir comportamiento de fallos del ejecutor
    Given un ejecutor con baseline "<baseline>" y mutante "<mutation>"
    When ejecuto una campana con "<planned>" mutacion
    Then el veredicto es "<verdict>" con "<killed>" killed y "<errors>" errores
    And quedan "<survived>" supervivientes y "<not_run>" sin ejecutar
    Examples:
      | baseline | mutation | planned | verdict | killed | errors | survived | not_run |
      | 1 | 0 | 1 | 1 | 1 | 0 | 0 | 0 |
      | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
      | 1 | 2 | 1 | 0 | 0 | 1 | 0 | 0 |
      | 1 | 3 | 1 | 0 | 0 | 1 | 0 | 0 |
      | 1 | 4 | 1 | 0 | 0 | 1 | 0 | 0 |

  Scenario Outline: Abortar antes de lanzar mutantes si falla baseline
    Given un ejecutor con baseline "<baseline>" y un mutante que no debe ejecutarse
    When ejecuto la campana abortada con "<planned>" mutacion
    Then el veredicto del aborto es "<verdict>" con "<killed>" killed y "<errors>" errores
    And tras el aborto quedan "<survived>" supervivientes y "<not_run>" sin ejecutar
    And no se crea ningun intento mutante
    Examples:
      | baseline | planned | verdict | killed | errors | survived | not_run |
      | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
