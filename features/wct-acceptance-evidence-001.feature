Feature: Evidencia causal de mutacion de aceptacion
  Scenario Outline: Distinguir comportamiento de fallos del ejecutor
    Given un ejecutor con baseline "<baseline>" y mutante "<mutation>"
    When ejecuto una campana con "<planned>" mutacion
    Then el veredicto es "<verdict>" con "<killed>" killed y "<errors>" errores
    And quedan "<survived>" supervivientes y "<not_run>" sin ejecutar
    Examples:
      | baseline | mutation | planned | verdict | killed | errors | survived | not_run |
      | pass | mismatch | 1 | pass | 1 | 0 | 0 | 0 |
      | mismatch | mismatch | 1 | fail | 0 | 0 | 0 | 1 |
      | pass | pass | 1 | fail | 0 | 0 | 1 | 0 |
      | pass | missing_receipt | 1 | fail | 0 | 1 | 0 | 0 |
      | pass | wrong_identity | 1 | fail | 0 | 1 | 0 | 0 |
      | pass | mixed_error | 1 | fail | 0 | 1 | 0 | 0 |
