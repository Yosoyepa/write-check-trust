# wct-config-wiring-001
Feature: Los gates consumen los umbrales declarados

  # thresholds.yaml declara que todos los números del harness viven ahí:
  # cambiar el YAML debe cambiar el gate, y el valor actual del repo no
  # debe alterar los comandos vigentes.

  Scenario Outline: El comando del gate nace del valor declarado
    Given un thresholds.yaml con <clave> en <valor>
    When el gate <gate> construye su invocación
    Then el flag <flag> recibe exactamente <valor>

    Examples:
      | clave                              | valor | gate       | flag               |
      | crap.changed_max                   | 9     | G-CRAP     | --max-crap         |
      | coverage.diff_min                  | 85    | G-COV-DIFF | --fail-under       |
      | dead_code.vulture_min_confidence   | 60    | G-DEAD     | --min-confidence   |
      | complexity.xenon_max_absolute      | C     | G-CC       | --max-absolute     |

  Scenario: Con el YAML vigente los comandos no cambian
    Given el thresholds.yaml del repositorio sin modificar
    When los gates cableados construyen sus invocaciones
    Then cada comando es identico al que producia el literal de antes

  Scenario: Una clave ausente es un gate rojo que la nombra
    Given un thresholds.yaml sin la clave <clave>
    When el gate que la consume construye su invocacion
    Then el gate falla declarando la clave esperada
    And nunca corre con un valor por defecto silencioso

    Examples:
      | clave                            |
      | crap.changed_max                 |
      | coverage.diff_min                |
      | dry.min_nodes                    |
