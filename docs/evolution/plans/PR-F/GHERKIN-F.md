# PR-F — Gherkin

> **Corrección del arquitecto (2026-09-05):** el bloque original de este
> archivo traía la narrativa como texto libre bajo `Feature:` — Gherkin
> estándar válido, pero que `parse_feature` (pipeline.py:24-72) no soporta:
> G-ACCEPT lo reprobó en `feature:4`. La forma aterrizada convierte la
> narrativa a comentarios `#` (texto íntegro), el convenio del repo desde
> PR-D. La limitación del parser quedó registrada como deuda con trazabilidad
> (issue #35 + TODO en pipeline.py, MIN-004); soportar narrativa es trabajo
> separado con TDD propio.

`features/wct-redteam-residual-001.feature` se reemplaza ÍNTEGRO por:

```gherkin
# wct-redteam-residual-001
Feature: El red team no declara residuos

  # F4-b, el último residuo (ADR-C-02), fue redimido en la PR-F (ADR-F-01):
  # la cobertura-diff corre productiva. Este feature es el ratchet — un caso
  # futuro con arnés heuristic lo pone en rojo y obliga a declararlo
  # consciente, con su razón y su ruta de redención.

  Scenario Outline: El residuo redimido corre el motor productivo
    Given el caso <caso> con producción nueva y cero tests en el fixture git
    When el arnés gate-tool invoca <herramienta> sobre el repositorio sembrado
    Then la cobertura de las líneas cambiadas da cero y el gate reprobará
    And el caso queda cazado por un FAIL productivo

    Examples:
      | caso | herramienta |
      | F4-b | diff-cover  |

  Scenario: Ningún caso declara arnés heuristic
    Given la unión de archivos de casos del red team
    When el runner cuenta los arneses declarados
    Then ningún caso queda en el arnés heuristic
    And el resumen imprime el conteo de heurísticos en cero

  Scenario: La unión de archivos conserva el invariario de modos
    Given los archivos de casos presentes
    When el runner valida los quince modos de fallo
    Then exige al menos dos casos por modo sobre la unión
    And la ausencia de un archivo no rompe la validación
```

## Trazabilidad

| Escenario | Comportamiento observable | Prueba que lo fija |
|---|---|---|
| El residuo redimido corre el motor productivo | F4-b caza vía `REGISTRY["G-COV-DIFF"]` sobre el fixture git | `test_tool_case_catches_planted_defect[F4-b]` (parametrizado existente) |
| Ningún caso declara arnés heuristic | unión sin `harness: heuristic` + resumen "0 heuristic (declarados)" | `test_union_declares_zero_heuristics` (nueva) |
| La unión conserva el invariario de modos | `_mode_gaps` exige ≥2 por modo F1–F15 | `test_mode_gaps_*` existentes en `test_redteam_engine.py` |
