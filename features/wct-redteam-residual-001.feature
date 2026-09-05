# wct-redteam-residual-001
Feature: Los residuos del red team están declarados

  Scenario Outline: Residuo etiquetado con razón y redención
    Given el caso <caso> que hoy no puede ejecutar código productivo
    When se lee su entrada en cases.yaml
    Then declara harness heuristic
    And su comentario lleva la razón y la ruta de redención

    Examples:
      | caso  | razón                                              |
      | F2-a  | exige corrida real de mutmut                       |
      | F2-b  | un test hardcoded pasa la suite por diseño         |
      | F4-b  | diff-cover exige fixture git con rama base         |
      | F5-b  | survived es el output de una corrida inexistente   |
      | F11-b | vulture a umbral 80 no ve constantes (confianza 60) |

  Scenario: La unión de archivos conserva el invariario de modos
    Given los archivos de casos presentes
    When el runner valida los quince modos de fallo
    Then exige al menos dos casos por modo sobre la unión
    And la ausencia de un archivo no rompe la validación
