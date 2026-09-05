# wct-mutation-real-001
Feature: La mutación corre de verdad sobre los adversarios

# Los tres residuos de mutación redimidos: el defecto se mide con una
# corrida real de mutmut sobre el fixture, no con una imitación.

  Scenario Outline: El adversario de mutación cae con una corrida real
    Given un fixture con <adversario> y su propio config de mutmut
    When corre el caso <caso> por su arnés gate-tool
    Then mutmut mide <sobrevivientes> y el gate G-MUT productivo lo rechaza

    Examples:
      | caso | adversario                                     | sobrevivientes       |
      | F2-a | src real sin tests                             | todos los mutantes   |
      | F2-b | test hardcodeado sobre un camino no ejercido   | el mutante no cazado |
      | F5-b | test débil que no cubre la semántica          | al menos uno         |

  Scenario: El caso demostración expone lo que la suite calla
    Given un test que pasa y no protege el comportamiento mutado
    When corre la mutación real sobre su fixture
    Then el sobreviviente aparece aunque la suite esté en verde
    And el caso cuenta como rechazado por la corrida real

  Scenario: mutmut ausente es SKIP visible
    Given un entorno sin mutmut instalado
    When corre el red team
    Then los casos gate-tool de mutmut se listan como SKIP con la herramienta nombrada
    And ni los rechazados ni los fallos crecen
