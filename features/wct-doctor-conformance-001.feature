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
