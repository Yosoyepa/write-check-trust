# wct-redteam-residual-001
Feature: El red team no declara residuos

  # F4-b, el último residuo (ADR-C-02), fue redimido en la PR-F (ADR-F-01):
  # la cobertura-diff corre productiva. Este feature es el ratchet — un caso
  # futuro con arnés heuristic lo pone en rojo y obliga a declararlo
  # consciente, con su razón y su ruta de redención.

  Scenario Outline: El residuo redimido corre el motor productivo
    Given el caso <caso> con producción nueva y cero tests en el fixture git
    When el arnés gate-tool invoca <herramienta> sobre el repositorio sembrado
    Then la cobertura de las líneas cambiadas da cero y el gate reprobará
    And el caso queda cazado por un FAIL productivo

    Examples:
      | caso | herramienta |
      | F4-b | diff-cover  |

  Scenario: Ningún caso declara arnés heuristic
    Given la unión de archivos de casos del red team
    When el runner cuenta los arneses declarados
    Then ningún caso queda en el arnés heuristic
    And el resumen imprime el conteo de heurísticos en cero

  Scenario: La unión de archivos conserva el invariario de modos
    Given los archivos de casos presentes
    When el runner valida los quince modos de fallo
    Then exige al menos dos casos por modo sobre la unión
    And la ausencia de un archivo no rompe la validación
