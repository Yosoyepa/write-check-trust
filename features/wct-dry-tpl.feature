# wct-dry-tpl-001
Feature: Template DRY clone detection gate

  Scenario Outline: Clones de plantilla anonimizada
    Given dos funciones con <structure>
    When calculo la similitud de plantilla AST
    Then el detector <verdict> con score <score>

    Examples:
      | structure                                  | verdict            | score |
      | estructura idéntica pero nombres distintos | detecta un cluster | 1.0   |
      | flujo de control diferente                 | no detecta cluster | 0.0   |

  Scenario: Los archivos de test quedan excluidos de la búsqueda de plantilla
    Given dos funciones idénticas ubicadas bajo tests
    When calculo la similitud de plantilla sobre el árbol
    Then no se reportan clusters para la suite de tests

  Scenario: El conteo de clusters de plantilla solo puede bajar
    Given un repositorio con clusters de plantilla
    When corre el gate de clones de plantilla sobre el repositorio
    Then pasa mientras el conteo no supere la baseline
