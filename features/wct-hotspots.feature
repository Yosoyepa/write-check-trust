# wct-hotspots-001
Feature: Hotspot report

  Scenario Outline: El reporte prioriza por churn y complejidad
    Given un archivo "<file>" con <churn> cambios y complejidad cognitiva <complexity>
    When pido el reporte de hotspots
    Then su hotspot es <product> y la lista ordena por él de mayor a menor

    Examples:
      | file       | churn | complexity | product |
      | worker.py  | 120   | 21         | 2520    |
      | policy.py  | 40    | 6          | 240     |

  Scenario: El reporte es asesor, no bloqueante
    Given un repositorio con hotspots evidentes
    When pido el reporte de hotspots sobre el repositorio completo
    Then el comando termina con exit cero aunque el top esté poblado
