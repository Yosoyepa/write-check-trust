# wct-mutation-verdict-001
Feature: El gate clasifica todo el inventario del motor de mutación

  # G1a (REVIEW-G1 D1/D2, ADR-G1-01): recepción y clasificación del
  # reporte de mutmut 3.7.0 vía results --all true. Claim LIMITADO: lo
  # que el motor reportó — sin causa (exit 3 colapsa a killed) ni
  # frescura (G1b). Un estado fuera del contrato de certificación nunca
  # produce PASS; el ERROR precede al FAIL conservando los hallazgos.

  Scenario Outline: Cada estado reportado decide el resultado del gate
    Given un árbol cuyo inventario reporta todos sus mutantes en estado <estado>
    When el gate G-MUT evalúa el árbol con el inventario completo
    Then el resultado es <resultado> con <causa>

    Examples:
      | estado                        | resultado | causa                                  |
      | killed                        | PASS      | clasificación del motor                |
      | survived                      | FAIL      | identidades de mutantes sobrevivientes |
      | no tests                      | FAIL      | identidades sin test asociado          |
      | timeout                       | ERROR     | estado fuera del contrato de WCT       |
      | suspicious                    | ERROR     | estado fuera del contrato de WCT       |
      | not checked                   | ERROR     | estado fuera del contrato de WCT       |
      | check was interrupted by user | ERROR     | estado fuera del contrato de WCT       |
      | segfault                      | ERROR     | estado fuera del contrato de WCT       |
      | caught by type check          | ERROR     | estado fuera del contrato de WCT       |
      | skipped                       | ERROR     | estado fuera del contrato de WCT       |

  Scenario Outline: Evidencia inválida precede sin esconder hallazgos
    Given un árbol con <sobrevivientes> mutantes sobrevivientes y <colgados> mutantes timeout en el inventario
    When el gate G-MUT evalúa el árbol mixto con el inventario completo
    Then el resultado es ERROR por estados fuera del contrato de WCT
    And el detalle conserva las identidades de los mutantes sobrevivientes

    Examples:
      | sobrevivientes | colgados |
      | 2              | 2        |
      | 1              | 3        |

  Scenario: Results fallido tras un run sano es error de instrumento
    Given una corrida cuyo mutmut run termina bien y cuyo results --all true falla
    When el gate G-MUT evalúa tras un results fallido
    Then el resultado es ERROR con fase results y las últimas líneas de diagnóstico

  Scenario: Run interrumpido bloquea sin atribuir defecto de producto
    Given una corrida cuyo mutmut run no puede completarse
    When el gate G-MUT evalúa tras un run interrumpido
    Then el resultado es FAIL con causa ejecución no completada y las últimas líneas de salida

  Scenario: Inventario legible y vacío no acredita verde
    Given una corrida legible cuyo inventario lista cero mutantes
    When el gate G-MUT evalúa tras leer un inventario vacío
    Then el resultado es ERROR con fase inventario y el mensaje nombra el alcance vacío

  Scenario: Renglones inválidos no pasan en silencio
    Given un inventario con una identidad duplicada o un estado fuera de vocabulario
    When el gate G-MUT evalúa tras toparse con un renglón inválido
    Then el resultado es ERROR con diagnóstico del renglón sospechoso

  Scenario Outline: El CLI y el gate responden igual cuando miden
    Given un micro-repo sin manifiesto con <sobrevivientes> mutantes sobrevivientes en el inventario
    When el CLI wct mutate run mide por subprocess y el gate G-MUT evalúa el mismo árbol
    Then el CLI termina con exit <exit> imprimiendo fase, conteos e identidades
    And el gate responde <resultado> con las mismas identidades

    Examples:
      | sobrevivientes | exit | resultado |
      | 2              | 1    | FAIL      |
      | 0              | 0    | PASS      |

  Scenario: Delta cero informa ausencia de trabajo, no calidad
    Given un árbol sin funciones cambiadas respecto al manifiesto
    When el CLI wct mutate run evalúa el manifiesto diferencial
    Then informa que no hay trabajo diferencial sin presentar una medición nueva de calidad
