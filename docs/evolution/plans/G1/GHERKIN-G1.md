# G1 — Gherkin: G1a APROBADO + G1b BORRADOR

§G1a **aprobada por humano (yosoyepa, 2026-09-05)** y aterrizada en
`features/wct-mutation-verdict-001.feature` verbatim. La §G1b es BORRADOR
de diseño (no aprobado, no implementable — ver SPEC-G1b-1). Narrativa como
comentarios `#` (convención del parser, #35).

## §G1a — wct-mutation-verdict-001 (FINAL, para aprobación)

```gherkin
# wct-mutation-verdict-001
Feature: El gate clasifica todo el inventario del motor de mutación

  # G1a (REVIEW-G1 D1/D2, ADR-G1-01): recepción y clasificación del
  # reporte de mutmut 3.7.0 vía results --all true. Claim LIMITADO: lo
  # que el motor reportó — sin causa (exit 3 colapsa a killed) ni
  # frescura (G1b). Un estado fuera del contrato de certificación nunca
  # produce PASS; el ERROR precede al FAIL conservando los hallazgos.

  Scenario Outline: Cada estado reportado decide el resultado del gate
    Given un árbol cuyo inventario reporta todos sus mutantes en estado <estado>
    When el gate G-MUT evalúa el árbol con el inventario completo
    Then el resultado es <resultado> con <causa>

    Examples:
      | estado                        | resultado | causa                                  |
      | killed                        | PASS      | clasificación del motor                |
      | survived                      | FAIL      | identidades de mutantes sobrevivientes |
      | no tests                      | FAIL      | identidades sin test asociado          |
      | timeout                       | ERROR     | estado fuera del contrato de WCT       |
      | suspicious                    | ERROR     | estado fuera del contrato de WCT       |
      | not checked                   | ERROR     | estado fuera del contrato de WCT       |
      | check was interrupted by user | ERROR     | estado fuera del contrato de WCT       |
      | segfault                      | ERROR     | estado fuera del contrato de WCT       |
      | caught by type check          | ERROR     | estado fuera del contrato de WCT       |
      | skipped                       | ERROR     | estado fuera del contrato de WCT       |

  Scenario Outline: Evidencia inválida precede sin esconder hallazgos
    Given un árbol con <sobrevivientes> mutantes sobrevivientes y <colgados> mutantes timeout en el inventario
    When el gate G-MUT evalúa el árbol mixto con el inventario completo
    Then el resultado es ERROR por estados fuera del contrato de WCT
    And el detalle conserva las identidades de los mutantes sobrevivientes

    Examples:
      | sobrevivientes | colgados |
      | 2              | 2        |
      | 1              | 3        |

  Scenario: Results fallido tras un run sano es error de instrumento
    Given una corrida cuyo mutmut run termina bien y cuyo results --all true falla
    When el gate G-MUT evalúa tras un results fallido
    Then el resultado es ERROR con fase results y las últimas líneas de diagnóstico

  Scenario: Run interrumpido bloquea sin atribuir defecto de producto
    Given una corrida cuyo mutmut run no puede completarse
    When el gate G-MUT evalúa tras un run interrumpido
    Then el resultado es FAIL con causa ejecución no completada y las últimas líneas de salida

  Scenario: Inventario legible y vacío no acredita verde
    Given una corrida legible cuyo inventario lista cero mutantes
    When el gate G-MUT evalúa tras leer un inventario vacío
    Then el resultado es ERROR con fase inventario y el mensaje nombra el alcance vacío

  Scenario: Renglones inválidos no pasan en silencio
    Given un inventario con una identidad duplicada o un estado fuera de vocabulario
    When el gate G-MUT evalúa tras toparse con un renglón inválido
    Then el resultado es ERROR con diagnóstico del renglón sospechoso

  Scenario Outline: El CLI y el gate responden igual cuando miden
    Given un micro-repo sin manifiesto con <sobrevivientes> mutantes sobrevivientes en el inventario
    When el CLI wct mutate run mide por subprocess y el gate G-MUT evalúa el mismo árbol
    Then el CLI termina con exit <exit> imprimiendo fase, conteos e identidades
    And el gate responde <resultado> con las mismas identidades

    Examples:
      | sobrevivientes | exit | resultado |
      | 2              | 1    | FAIL      |
      | 0              | 0    | PASS      |

  Scenario: Delta cero informa ausencia de trabajo, no calidad
    Given un árbol sin funciones cambiadas respecto al manifiesto
    When el CLI wct mutate run evalúa el manifiesto diferencial
    Then informa que no hay trabajo diferencial sin presentar una medición nueva de calidad
```

## §G1b — wct-mutation-freshness-001 (BORRADOR — NO aprobado, NO implementar)

```gherkin
# wct-mutation-freshness-001
# BORRADOR G1b: requiere ADR-G1-02/04 aprobados, RG12/13 medidos y
# aprobación humana propia (SPEC-G1b-1). No crear este archivo aún.
Feature: La evaluación de mutación usa la evidencia de su propia corrida

  Scenario: La repetición del alcance derrota la herencia
    Given una corrida previa con todos los mutantes killed y tests debilitados que conservan las llamadas
    When el gate y el CLI repiten el alcance completo con argumento literal
    Then los mutantes se re-ejecutan bajo los tests actuales
    And el veredicto refleja la corrida actual, no la heredada

  Scenario: El kill por error interno de pytest es distinguible
    Given un inventario donde mutmut imprime killed con exit crudo 3
    When el lector versionado clasifica la causa del kill
    Then el resultado separa error interno del kill por aserción

  Scenario: La pérdida parcial del inventario es detectada
    Given un meta perdido entre la fase de run y la de results
    When el adaptador compara inventario esperado contra recibido
    Then el resultado es ERROR por divergencia con las identidades perdidas
```

## Trazabilidad G1a (scenario → evidencia EVIDENCE.md → test SPEC-G1a-1)

| Scenario | Evidencia | Test nombrado |
|---|---|---|
| Cada estado decide el resultado | [L] tabla §2.1 + [O] P1/P2/P8 + [I] P7/B | `test_classification_table` + fixtures reales |
| Evidencia inválida precede | [O] P8 (timeout real) + clasificación | `test_mixed_survived_and_timeout_error_preserves_findings` |
| Results fallido tras run sano | [I]+[O] P4a/b standalone (doble etiquetado en test) | `test_results_failure_after_healthy_run_is_error` |
| Run interrumpido | [O] P3 + redteam F2-a (continuo) | `test_run_failure_blocks_without_product_label` |
| Inventario vacío | [I] P4c | `test_empty_inventory_is_error` |
| Renglones inválidos | diseño (nadie lo produce hoy) | `test_duplicate_identity_and_unknown_line_error` |
| CLI/gate igual cuando miden | §5 [INF]→ fijo por subprocess | `test_cli_subprocess_delta_reports_ids` |
| Delta cero | [L] engine.py:173-175 (existente) | `test_cli_delta_zero_informs_without_quality_claim` |
