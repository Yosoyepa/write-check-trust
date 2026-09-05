# wct-capability-profile-001
Feature: El perfil de capacidades dice lo que un verde significa

# Un auditor externo puede derivar del report qué gate necesita qué
# herramienta, si está presente y qué scope escanea.

  Scenario Outline: Capacidad por gate derivada del constructor
    Given el gate <gate> que resuelve la herramienta <herramienta>
    When se genera el perfil de capacidades
    Then declara la herramienta y su presencia efectiva
    And declara el scope <scope> y los tiers donde corre

    Examples:
      | gate           | herramienta | scope           |
      | G-DEAD         | vulture     | src y tools/wct |
      | G-SAST-SEMGREP | semgrep     | reglas semgrep  |
      | G-DEPS         | deptry      | src y tools     |

  Scenario: Herramienta ausente queda listada como no verificada
    Given un entorno donde la herramienta de un gate está ausente
    When se genera el perfil en ese entorno sin la herramienta
    Then el gate aparece con presencia falsa y no desaparece del report

  Scenario: El resumen del tier con SKIPs declara capacidades no verificadas
    Given una corrida con al menos un resultado SKIP
    When se renderiza el resumen
    Then una línea adicional nombra las capacidades no verificadas
    And una corrida sin SKIPs produce exactamente el resumen de antes
