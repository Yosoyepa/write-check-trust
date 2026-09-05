# GHERKIN-E — Escenarios (delegación vigente; el bless los sella)

## wct-mutation-real-001

```gherkin
# wct-mutation-real-001
Feature: La mutación corre de verdad sobre los adversarios

# Los tres residuos de mutación redimidos: el defecto se mide con una
# corrida real de mutmut sobre el fixture, no con una imitación.

  Scenario Outline: El adversario de mutación cae con una corrida real
    Given un fixture con <adversario> y su propio config de mutmut
    When corre el caso <caso> por su arnés gate-tool
    Then mutmut mide <sobrevivientes> y el gate G-MUT productivo lo rechaza

    Examples:
      | caso | adversario                                          | sobrevivientes       |
      | F2-a | src real sin tests                                  | todos los mutantes   |
      | F2-b | test hardcodeado sobre un camino no ejercido        | el mutante no cazado |
      | F5-b | test débil que no cubre la semántica               | al menos uno         |

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
```

## wct-gmut-full-001

```gherkin
# wct-gmut-full-001
Feature: G-MUT pertenece a un tier con presupuesto medido

# El perfil de capacidades de PR-D destapó que G-MUT no vivía en ningún
# tier; con 1.9s medidos se une al tier full.

  Scenario: El tier full incluye la mutación del ejemplo
    Given el tier full del repo
    When se consulta la membresía de G-MUT
    Then pertenece al tier full y a ningún otro
    And el perfil de capacidades lo refleja sin cambios manuales

  Scenario: El contrato del gate es real
    Given un fixture cuyos tests dejan sobrevivir un mutante
    When corre la función de gate G-MUT sobre el fixture
    Then el gate FALLA — el exit code de mutmut lo respalda
```
