# wct-self-coverage-001
Feature: El harness se mide a sí misma

# La cobertura del repo incluye el código del ejemplo y el del propio
# harness: el que verifica también se verifica.

  Scenario Outline: La fuente medida incluye al harness
    Given la configuración de coverage en pyproject.toml
    When se lee la lista source de la medición
    Then <paquete> está incluido en el scope

    Examples:
      | paquete   |
      | src       |
      | tools/wct |
