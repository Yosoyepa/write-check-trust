# wct-split-plan-001
Feature: Split plan for mutation-heavy files

  Scenario Outline: Proponer partición fachada bajo el presupuesto
    Given un archivo fuente con funciones de <sites> sitios y límite <limit>
    When pido el split-plan del archivo "<file>"
    Then la propuesta tiene <parts> partes, cada una dentro del límite
    And el archivo original queda como fachada que re-exporta todo nombre público
    And ningún import de callers cambia

    Examples:
      | file      | sites       | limit | parts |
      | worker.py | 40,35,30    | 100   | 2     |
      | tiny.py   | 50          | 100   | 1     |
      | huge.py   | 60,60,60,60 | 100   | 3     |

  Scenario: Una función que sola excede el límite no se arregla partiendo el archivo
    Given un archivo con una función de 140 sitios y límite 100
    When pido el split-plan del archivo
    Then el comando termina con exit no-cero pidiendo partir la función, no el archivo
