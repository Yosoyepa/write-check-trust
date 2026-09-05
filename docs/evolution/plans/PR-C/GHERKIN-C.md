# GHERKIN-C — Escenarios para aprobación humana (PROC-003)

**Requieren tu aprobación explícita antes de implementar.**

## wct-redteam-productive-001

```gherkin
# wct-redteam-productive-001
Feature: El red team califica con los motores productivos

  Un adversario rechazado lo rechaza el gate real, no una imitación.

  Scenario Outline: Defecto plantado cazado por el motor productivo
    Given un fixture aislado con <defecto> plantado
    When corre el caso <caso> por su arnés
    Then el motor productivo que usa su gate reporta el defecto
    And el caso cuenta como rechazado por ese motor

    Examples:
      | caso  | defecto                                  |
      | F1-a  | dos funciones estructuralmente idénticas |
      | F3-a  | test que no aserta sobre el SUT          |
      | F7-a  | ciclo de imports de dos módulos          |
      | F12-a | credencial AWS en el código              |
      | F10-a | dependencia usada y no declarada         |

  Scenario: Herramienta externa ausente es SKIP visible
    Given un caso gate-tool cuya herramienta no está instalada
    When corre el red team
    Then el caso se lista como SKIP con la herramienta nombrada
    And ni los rechazados ni los fallos crecen

  Scenario: El resumen cuenta por arnés
    Given la corrida completa del red team
    When se imprime el resumen
    Then separa gate-engine, gate-tool, hook y heuristic (declarados)
    And ningún caso heurístico se presenta como productivo

  Scenario: Un motor que no caza es un hallazgo, no un fixture ajustado
    Given un caso cuyo motor productivo no reporta el defecto plantado
    When corre el red team
    Then el caso falla en rojo con la salida del motor
    And el fixture no se modifica para volverlo verde
```

## wct-redteam-residual-001

```gherkin
# wct-redteam-residual-001
Feature: Los residuos del red team están declarados

  Scenario Outline: Residuo etiquetado con razón y redención
    Given el caso <caso> que hoy no puede ejecutar código productivo
    When se lee su entrada en cases.yaml
    Then declara harness heuristic
    And su comentario lleva la razón y la ruta de redención

    Examples:
      | caso | razón                                            |
      | F2-a | exige corrida real de mutmut                     |
      | F2-b | un test hardcoded pasa la suite por diseño       |
      | F4-b | diff-cover exige fixture git con rama base       |
      | F5-b | survived es el output de una corrida inexistente |

  Scenario: La unión de archivos conserva el invariario de modos
    Given los archivos de casos presentes
    When el runner valida los quince modos de fallo
    Then exige al menos dos casos por modo sobre la unión
    And la ausencia de un archivo no rompe la validación
```
