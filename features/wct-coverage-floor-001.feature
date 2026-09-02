# wct-coverage-floor-001
Feature: El baseline de cobertura total es un piso, no decoración

  Scenario Outline: El gate aplica el baseline registrado
    Given un baseline de coverage-total con valor <baseline>
    When el gate G-COV-TOTAL construye su invocación
    Then incluye --cov-fail-under=<baseline> sobre medición fresca

    Examples:
      | baseline |
      | 73       |
      | 100      |

  Scenario: Un baseline ausente es un gate rojo, no un piso removido
    Given un árbol sin governance/baselines/coverage-total.json
    When corre el gate G-COV-TOTAL
    Then falla declarando el archivo de baseline esperado

  Scenario: La cobertura por debajo del piso bloquea
    Given un baseline de 85 y una corrida cuyo total es <total>
    When el gate evalúa el resultado
    Then el veredicto es <veredicto>

    Examples:
      | total | veredicto |
      | 84    | falla     |
      | 85    | pasa      |
