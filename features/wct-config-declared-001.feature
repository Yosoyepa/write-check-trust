# wct-config-declared-001
Feature: Las constantes del harness viven en thresholds.yaml

  Scenario Outline: Constantes antes huerfanas ahora declaradas y consumidas
    Given thresholds.yaml declara <clave> con el valor que hoy es un literal
    When el motor correspondiente evalua un fixture sensible a ese valor
    Then el comportamiento observa el valor declarado

    Examples:
      | clave                  | literal | motor      |
      | dry.template_threshold | 0.90    | dry/tpl    |
      | dry.review_threshold   | 0.95    | dry/token  |
      | lcom.min_methods       | 3       | lcom       |
      | lcom.threshold         | 2       | lcom       |

  Scenario: Ningun numero del harness queda huerfano en los modulos cableados
    Given los modulos dry y lcom del repositorio
    When se buscan umbrales numericos definidos como literales de modulo
    Then no queda ninguno de los inventariados en el ANALYSIS
