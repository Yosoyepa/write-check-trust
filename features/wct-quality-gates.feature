# wct-quality-gates-001
Feature: Size and cognitive budgets

  Scenario Outline: El presupuesto de líneas por archivo
    Given un archivo "<file>" con <loc> líneas de código y límite <limit>
    When corre el gate de tamaño
    Then el gate <verdict>

    Examples:
      | file       | loc  | limit | verdict                 |
      | small.py   | 420  | 500   | pasa                    |
      | medium.py  | 499  | 500   | pasa                    |
      | large.py   | 560  | 500   | falla nombrando el archivo |

  Scenario: Un archivo nuevo sobre el límite no cabe en la baseline
    Given un archivo nuevo de 640 líneas con límite 500
    When corre el gate de tamaño sobre el archivo nuevo
    Then bloquea aunque la baseline tenga deuda legada

  Scenario: La deuda legada de tamaño solo puede bajar
    Given un archivo listado en la baseline con 593 líneas
    When corre el gate de tamaño sobre el legado
    Then pasa mientras el conteo legado no suba

  Scenario Outline: La anidación profunda cuesta más que la ramificación plana
    Given una función con <shape> y seis condiciones
    When corre el gate de complejidad cognitiva con límite 15
    Then la función <verdict>

    Examples:
      | shape              | verdict  |
      | seis ifs planos    | pasa     |
      | seis ifs anidados  | bloquea  |

  Scenario: Una función con complejidad cognitiva sobre el umbral bloquea
    Given una función con anidamiento que supera el umbral cognitivo
    When corre el gate de complejidad cognitiva sobre src
    Then el finding nombra archivo, línea y función
