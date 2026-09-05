# wct-deadcode-redeemed-001
Feature: El código muerto de confianza 60 es cazado

# Redime el residuo F11-b de ADR-C-02 con la sonda como evidencia:
# vulture a 60 reporta 1 falso positivo en todo el repo (campo de
# dataclass consumido por asdict), muerte real cero.

  Scenario Outline: El adversario de confianza 60 cae con el gate real
    Given un fixture que declara confianza <confianza> con <defecto>
    When corre el caso F11-b por su arnés gate-tool
    Then el gate G-DEAD productivo lo rechaza

    Examples:
      | confianza | defecto          |
      | 60        | constante muerta |

  Scenario: El repo real a 60 con whitelist queda en cero hallazgos
    Given la whitelist con el único falso positivo conocido
    When corre vulture sobre src y tools/wct a confianza 60
    Then no hay hallazgos y la baseline del ratchet no cambia
