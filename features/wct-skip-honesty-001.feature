# wct-skip-honesty-001
Feature: El resumen de gates distingue PASS de SKIP

# SKIP codifica "no se evaluó": el agregado del resumen no puede
# presentarlo como verificación exitosa.

  Scenario Outline: Conteo separado por estado
    Given una corrida con <pass> resultados PASS, <skip> SKIP y <fail> bloqueantes
    When se renderiza el resumen de la corrida
    Then la línea de resumen muestra los tres contadores por separado

    Examples:
      | pass | skip | fail |
      | 28   | 5    | 0    |
      | 7    | 0    | 0    |
      | 1    | 1    | 1    |

  Scenario: SKIP sigue sin bloquear la corrida
    Given una corrida cuyo único resultado no-PASS es SKIP
    When se calcula el veredicto de bloqueo de la corrida
    Then la corrida no bloquea
