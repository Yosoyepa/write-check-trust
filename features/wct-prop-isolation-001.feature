# wct-prop-isolation-001
Feature: Aislamiento contractual de property tests (TEST-008)

# Los property tests ejecutan en su gate dedicado y no participan de
# coverage, de la verificación normal ni de la selección de mutación.

  Scenario Outline: Los gates de métrica excluyen los tests marcados property
    Given property tests marcados con @pytest.mark.property en <fuente>
    When el gate <gate> construye su invocación de pytest
    Then la invocación excluye los tests marcados property

    Examples:
      | fuente         | gate        |
      | tests/property | G-COV-TOTAL |
      | tests/property | G-TEST      |

  Scenario: El gate dedicado ejecuta los property tests sin filtro
    Given property tests marcados con @pytest.mark.property en tests/property
    When el gate G-PROP construye su invocación de pytest
    Then la invocación no filtra por marker y ejecuta tests/property

  Scenario: La selección de tests para mutación excluye property
    Given la configuración de mutación en pyproject.toml
    When se lee la selección de tests que corre cada mutante
    Then ninguna entrada está bajo tests/property
