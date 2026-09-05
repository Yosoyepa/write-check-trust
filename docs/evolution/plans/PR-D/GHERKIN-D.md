# GHERKIN-D — Escenarios (autorizados por delegación 2026-09-05; el bless los sella)

El humano delegó la decisión de arquitecto con autoría ("toma la decisión
como arquitecto… sigue autónomamente hasta que necesites mi bless"):
los escenarios aterrizan sin pre-aprobación y el bless del PR es la
aprobación explícita (PROC-003 satisfecho por delegación documentada).

## wct-capability-profile-001

```gherkin
# wct-capability-profile-001
Feature: El perfil de capacidades dice lo que un verde significa

  Un auditor externo puede derivar del report qué gate necesita qué
  herramienta, si está presente y qué scope escanea.

  Scenario Outline: Capacidad por gate derivada del constructor
    Given el gate <gate> que resuelve la herramienta <herramienta>
    When se genera el perfil de capacidades
    Then declara la herramienta y su presencia efectiva
    And declara el scope <scope> y los tiers donde corre

    Examples:
      | gate          | herramienta     | scope            |
      | G-DEAD        | vulture         | src y tools/wct  |
      | G-SAST-SEMGREP | semgrep        | reglas semgrep   |
      | G-DEPS        | deptry          | src y tools      |

  Scenario: Herramienta ausente queda listada como no verificada
    Given un entorno donde la herramienta de un gate está ausente
    When se genera el perfil en ese entorno sin la herramienta
    Then el gate aparece con presencia falsa y no desaparece del report

  Scenario: El resumen del tier con SKIPs declara capacidades no verificadas
    Given una corrida con al menos un resultado SKIP
    When se renderiza el resumen
    Then una línea adicional nombra las capacidades no verificadas
    And una corrida sin SKIPs produce exactamente el resumen de antes
```

## wct-deadcode-redeemed-001

```gherkin
# wct-deadcode-redeemed-001
Feature: El código muerto de confianza 60 es cazado

  Redime el residuo F11-b de ADR-C-02 con la sonda como evidencia.

  Scenario Outline: El adversario de confianza 60 cae con el gate real
    Given un fixture que declara confianza <confianza> con <defecto>
    When corre el caso F11-b por su arnés gate-tool
    Then el gate G-DEAD productivo lo rechaza

    Examples:
      | confianza | defecto           |
      | 60        | constante muerta  |

  Scenario: El repo real a 60 con whitelist queda en cero hallazgos
    Given la whitelist con el único falso positivo conocido
    When corre vulture sobre src y tools/wct a confianza 60
    Then no hay hallazgos y la baseline del ratchet no cambia
```

## wct-relative-artifact-001

```gherkin
# wct-relative-artifact-001
Feature: El artefacto de aceptación es reproducible entre checkouts

  El mismo feature genera el mismo artefacto sin importar la ruta
  absoluta del checkout (bug observado en PR-C con worktrees).

  Scenario: Dos checkouts del mismo feature generan artefactos idénticos
    Given el mismo feature en dos roots distintos
    When se genera el artefacto de aceptación en cada uno
    Then los dos artefactos son byte-idénticos
    And el source del IR es la ruta relativa al root
```

## wct-bare-ruff-001

```gherkin
# wct-bare-ruff-001
Feature: ruff sin --config usa el perfil del repo

  Un agente que corra ruff desnudo no debe recibir el ruleset de nadie.

  Scenario: ruff desnudo extiende el perfil viviente
    Given un archivo fuente del repo que pasa el lint del perfil
    When se corre ruff check sin --config sobre él
    Then no reporta hallazgos
    And el comando con --config sigue pasando igual
```
