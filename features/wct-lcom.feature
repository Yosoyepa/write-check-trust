# wct-lcom-001
Feature: LCOM4 class cohesion gate

  Scenario Outline: Cohesión de clases medida por componentes conexas
    Given una clase con <layout>
    When calculo la métrica LCOM4 de la clase
    Then el resultado es <components> componentes

    Examples:
      | layout                                       | components |
      | dos grupos disjuntos de métodos y atributos  | 2          |
      | métodos que comparten atributos encadenados  | 1          |
      | orquestador con métodos que solo se llaman   | 1          |

  Scenario: Las clases tipo dataclass quedan excluidas del análisis
    Given una clase decorada con dataclass
    When calculo la métrica LCOM4 para la dataclass
    Then la clase no participa en el reporte

  Scenario: El conteo de clases poco cohesivas solo puede bajar
    Given un repositorio con clases poco cohesivas
    When corre el gate de cohesión LCOM4 sobre el repositorio
    Then pasa mientras el conteo no supere la baseline
