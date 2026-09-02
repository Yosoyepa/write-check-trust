# GHERKIN-A2 — Escenarios para aprobación humana (PROC-003)

**Requieren tu aprobación explícita antes de implementar.** Al aprobarse,
aterrizan en `features/` en el estilo del repo (prosa como comentarios `#`
— restricción del parser constatada en A1).

## wct-self-coverage-001 (scope)

```gherkin
# wct-self-coverage-001
Feature: El harness se mide a sí misma

  La cobertura del repo incluye el código del ejemplo y el del propio
  harness: el que verifica también se verifica.

  Scenario Outline: La fuente medida incluye al harness
    Given la configuración de coverage en pyproject.toml
    When se lee la lista source de la medición
    Then <paquete> está incluido en el scope

    Examples:
      | paquete   |
      | src       |
      | tools/wct |
```

## wct-coverage-floor-001 (aplicación del baseline)

```gherkin
# wct-coverage-floor-001
Feature: El baseline de cobertura total es un piso, no decoración

  Scenario Outline: El gate aplica el baseline registrado
    Given un baseline de coverage-total con valor <baseline>
    When el gate G-COV-TOTAL construye su invocación
    Then incluye --cov-fail-under=<baseline> sobre medición fresca

    Examples:
      | baseline |
      | 73       |
      | 100      |

  Scenario: Un baseline ausente es un gate rojo, no un piso removido
    Given un árbol sin governance/baselines/coverage-total.json
    When corre el gate G-COV-TOTAL
    Then falla declarando el archivo de baseline esperado

  Scenario: La cobertura por debajo del piso bloquea
    Given un baseline de 85 y una corrida cuyo total es <total>
    When el gate evalúa el resultado
    Then el veredicto es <veredicto>

    Examples:
      | total | veredicto |
      | 84    | falla     |
      | 85    | pasa      |
```

## wct-coverage-ratchet-001 (medición y registro)

```gherkin
# wct-coverage-ratchet-001
Feature: coverage-total es una métrica de ratchet auditable

  Scenario: El ratchet mide desde el artefacto que produce el gate
    Given un build/coverage/lcov.info producido por G-COV-TOTAL
    When se ejecuta la medición de coverage-total
    Then el porcentaje coincide con el TOTAL oficial de coverage.py

  Scenario: Sin artefacto la medición se abstiene en vez de mentir
    Given un árbol sin build/coverage/lcov.info
    When se ejecuta la medición de ratchet
    Then coverage-total no se reporta y la ausencia queda declarada

  Scenario: El registro humano es por métrica y deja rastro
    Given un humano autorizado con --approved-by y --reason que cita un PR
    When corre ratchet record --metric coverage-total
    Then solo el baseline de coverage-total se reescribe
    And queda registrado commit, owner y razón
```
