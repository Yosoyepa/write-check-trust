Feature: Reconciliacion pura de observaciones pytest
  # SH-P03a/1: datos aportados, no ejecucion ni procedencia acreditada.
  Scenario Outline: Distinguir observaciones y defectos del protocolo
    Given el journal literal del caso "<case>"
    When reconcilio sus observaciones con expectativas revisadas
    Then el campo "<field>" tiene el valor literal "<expected>"

    Examples:
      | case | field | expected |
      | PA01 | protocol_complete | true |
      | PA02 | decoder_prefix_preserved | true |
      | PA03 | framing_defect_visible | true |
      | PA04 | phase_defect_visible | true |
      | PA05 | failed_terminal_preserved | true |
      | PA06 | identity_substitution_detected | true |
      | PA07 | property_mismatch_detected | true |
      | PA08 | exit_not_replaced | true |
      | PA09 | exact_boundary_allowed | true |
      | PA10 | over_boundary_rejected | true |
      | PA11 | provenance | caller-supplied-unverified |
      | PA12 | invalid_argument_rejected | true |
