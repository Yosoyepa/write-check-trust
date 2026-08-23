# wct-hook-deadlock-escape-001
Feature: Stop hook deadlock escape

  Scenario Outline: La tercera bloqueada consecutiva pasa con advertencia
    Given un árbol cuyo tier commit está en rojo con "<failure>"
    And un agente cuyo stop ya fue bloqueado <blocks> veces seguidas
    When el agente intenta terminar su turno
    Then el hook deja pasar el turno con advertencia DEADLOCK GUARD
    And la advertencia declara que el árbol sigue rojo
    And la racha de bloqueos se reinicia

    Examples:
      | failure                  | blocks |
      | G-TEST FAIL: 11 errors   | 2      |
      | G-LINT FAIL: 34 issues   | 2      |

  Scenario: Un stop verde reinicia la racha de bloqueos
    Given un agente con una bloqueada previa
    And un árbol cuyo tier commit pasa
    When el agente cierra el turno con el tier en verde
    Then el hook deja pasar el turno sin advertencia
    And una nueva bloqueada vuelve a contar desde uno

  Scenario: Un rol observador nunca se bloquea
    Given un árbol cuyo tier commit está en rojo
    And un agente con WCT_HOOK_ROLE=observer
    When el agente observador cierra su turno
    Then el hook deja pasar el turno con advertencia de observer
    And no consume intentos del cortacircuitos
