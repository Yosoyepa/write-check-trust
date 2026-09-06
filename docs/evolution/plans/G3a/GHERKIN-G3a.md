# G3a — Gherkin parametrizado (para aprobación humana; no entra al repo antes)

Narrativa como comentarios `#` (convención del parser, #35). Validado con
`wct accept parse` + `ir-dry` desde build/tmp en este dossier.

```gherkin
# wct-premerge-verification-001
Feature: La verificación pre-merge mide lo que exige y bloquea lo que falta

  # G3a (POST-PR36 F05, escape #37/#38): el incidente se convierte en
  # regresión — la suite que CI ejecuta pinea el invariario, el tier commit
  # gana G-INTROVERT, y el ratchet exigible falla ante métrica no medida
  # en lugar de saltarla en silencio. La procedencia del artefacto de
  # cobertura la da el orden de pasos de la corrida, no heurísticas.

  Scenario Outline: Una métrica exigible sin medición bloquea nombrándola
    Given una verificación que exige <métrica> y no puede medirla porque <causa>
    When el ratchet exigible evalúa
    Then falla nombrando la métrica y la causa
    And sugiere el comando que produce la medición

    Examples:
      | métrica            | causa                            |
      | coverage-total     | no existe build/coverage/lcov.info |
      | docstring-coverage | interrogate no está instalado    |
      | introverted-tests  | análisis de tests no disponible  |

  Scenario: El invariario de cero introvertidos vive dentro de la suite
    Given el repositorio con cero tests introverted
    When la suite de CI evalúa el invariario pineado
    Then pasa y un test introvertido nuevo lo rompería
    And un fixture con un introverted cuenta uno en el control negativo

  Scenario: El tier commit ejecuta el control de introvertidos
    Given el inventario de gates del tier commit
    When se listan sus miembros
    Then G-INTROVERT está presente junto a los veinte existentes

  Scenario: El modo tolerante del ratchet conserva su contrato
    Given una verificación sin requisitos explícitos
    When el ratchet tolerante evalúa
    Then su salida es idéntica a la actual sin nuevos claims

  Scenario Outline: El verde exigible declara qué midió
    Given una verificación con <total> métricas exigidas y todas medidas
    When el ratchet exigible evalúa con todo medido
    Then la salida declara medidas <total> de <total> exigibles

    Examples:
      | total |
      | 2     |
      | 10    |

  Scenario: El test del CLI de mutación conserva dos clases de aserción
    Given el test del CLI que ejecuta wct mutate run por subprocess
    When se revisan sus aserciones
    Then exige el contrato observable independiente con exit uno y fase literales
    And coteja las identidades impresas contra el veredicto del adaptador
```

## Trazabilidad (scenario → requisito → test futuro)

| Scenario | ADR | Test (SPEC-G3a-1) |
|---|---|---|
| Métrica exigible sin medición | ADR-G3a-02 §1/3 | `test_require_fails_naming_missing_metric` |
| Invariario en la suite | ADR-G3a-01 | `test_repo_introverted_ratchet_holds_baseline` + control defectuoso |
| G-INTROVERT en commit | ADR-G3a-03 G3a-1 | `test_commit_tier_includes_introvert` |
| Modo tolerante intacto | ADR-G3a-02 §1 | `test_without_require_behavior_unchanged` |
| Denominador honesto | ADR-G3a-02 §4 | `test_require_reports_denominator` |
| Doble clase de aserción | ADR-G3a-04 §1 | `test_cli_mutate_run_keeps_independent_contract` |
