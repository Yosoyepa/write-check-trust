Feature: Operador tipado de mutacion de aceptacion
  Scenario Outline: Transformar exclusivamente una celda declarada
    Given una fila con tipo "<type>" y valor "<value>"
    When enumero con activacion "<activation>"
    Then obtengo "<changed>" con "<planned>" celdas elegibles
    Examples:
      | type | value      | activation | changed                  | planned |
      | bool | true       | explicit   | false                    | 1       |
      | bool | false      | explicit   | true                     | 1       |
      | str  | x          | explicit   | x__typed                 | 1       |
      | str  |            | explicit   | __typed                  | 1       |
      | str  | ñ__typed  | explicit   | ñ__typed__typed          | 1       |
      | bool | true       | absent     | true__mutated            | 1       |
      | str  | 0          | absent     | 1                        | 1       |
      | str  | 2          | absent     | 0                        | 1       |

  Scenario Outline: Rechazar configuracion invalida
    Given una politica con defecto "<defect>"
    When intento activar y enumerar
    Then obtengo error "<error>" sin aprobar inventario
    Examples:
      | defect               | error               |
      | present-null         | MutationPolicyError |
      | present-empty        | MutationPolicyError |
      | schema-bool          | MutationPolicyError |
      | schema-unknown       | MutationPolicyError |
      | extra-key            | MutationPolicyError |
      | duplicate-json-key   | MutationPolicyError |
      | nan                  | MutationPolicyError |
      | unknown-type         | MutationPolicyError |
      | invalid-bool         | MutationPolicyError |
      | unknown-column       | MutationPolicyError |
      | unknown-row          | MutationPolicyError |
      | unknown-scenario     | MutationPolicyError |
      | duplicate-cell       | MutationPolicyError |
      | empty-cells          | MutationPolicyError |
      | wrong-source         | MutationPolicyError |
      | wrong-hash           | MutationPolicyError |
      | missing-policy-file  | MutationPolicyError |
      | invalid-utf8         | MutationPolicyError |

  Scenario Outline: Cotejar inventario independientemente del resultado
    Given un inventario original de "<rows>" filas y "<columns>" columnas
    When selecciono "<eligible>" columnas con activacion "<activation>"
    Then hay "<planned>" identidades unicas y solo cambia su celda
    Examples:
      | rows | columns | eligible | activation | planned |
      | 12   | 3       | 1        | explicit   | 12      |
      | 12   | 3       | 1        | absent     | 36      |
