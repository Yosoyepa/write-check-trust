# GHERKIN-B — Escenarios para aprobación humana (PROC-003)

**Requieren tu aprobación explícita antes de implementar.** Al aprobarse,
aterrizan en `features/` (prosa como comentarios `#` — restricción del parser).

## wct-config-wiring-001 (declarado → runtime)

```gherkin
# wct-config-wiring-001
Feature: Los gates consumen los umbrales declarados

  thresholds.yaml declara que todos los números del harness viven ahí:
  cambiar el YAML debe cambiar el gate, y el valor actual del repo no
  debe alterar los comandos vigentes.

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
```

## wct-config-declared-001 (runtime → declarado)

```gherkin
# wct-config-declared-001
Feature: Las constantes del harness viven en thresholds.yaml

  Scenario Outline: Constantes antes huerfanas ahora declaradas y consumidas
    Given thresholds.yaml declara <clave> con el valor que hoy es un literal
    When el motor correspondiente evalua un fixture sensible a ese valor
    Then el comportamiento observa el valor declarado

    Examples:
      | clave                  | literal | motor      |
      | dry.template_threshold | 0.90    | dry/tpl    |
      | dry.review_threshold   | 0.95    | dry/token  |
      | lcom.min_methods       | 3       | lcom       |
      | lcom.threshold         | 2       | lcom       |

  Scenario: Ningun numero del harness queda huerfano en los modulos cableados
    Given los modulos dry y lcom del repositorio
    When se buscan umbrales numericos definidos como literales de modulo
    Then no queda ninguno de los inventariados en el ANALYSIS
```

## wct-doctor-conformance-001 (visibilidad)

```gherkin
# wct-doctor-conformance-001
Feature: doctor audita la conformidad declarado → runtime

  Scenario: doctor lista cada umbral cableado con su gate y valor vivo
    Given el repositorio con sus umbrales declarados
    When corre wct doctor
    Then la seccion de conformidad lista al menos 11 pares clave y gate
    And cada valor mostrado proviene del thresholds.yaml vigente

  Scenario: La seccion refleja el YAML del entorno, no una lista congelada
    Given un fixture cuyo thresholds.yaml difiere del repo
    When corre wct doctor sobre el fixture
    Then los valores mostrados son los del fixture
```
