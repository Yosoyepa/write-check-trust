# Escenario SH-P01 para aprobación

Estado: **propuesto**, versión `sh-p01/1`. Copiar únicamente el bloque a
`features/wct-evidence-identities-001.feature` después de su aprobación.
El alcance es una API interna; no una nueva CLI ni acreditación de ejecución.
La [tabla P01](P01-IDENTIDADES.md) define las entradas y findings exactas de Ixx.

```gherkin
Feature: Reconciliacion no vacua de identidades de evidencia
  # Un match acredita igualdad de identidades, no ejecucion ni exito de tests.
  Scenario Outline: Cada inventario conserva sus obligaciones y sus defectos
    Given los inventarios del caso "<caso>" fijados por el contrato "<contrato>"
    When comparo expected collected y executed con la API productiva
    Then el estado de identidad es "<estado>"
    And las findings completas corresponden a "<hallazgos>"
    Examples:
      | caso | contrato | estado | hallazgos |
      | I01 | sh-p01/1 | match | ninguna |
      | I02 | sh-p01/1 | match | ninguna |
      | I03 | sh-p01/1 | mismatch | C:m:B; C:u:C; X:m:B; X:u:C |
      | I04 | sh-p01/1 | mismatch | C:m:B |
      | I05 | sh-p01/1 | mismatch | X:m:B |
      | I06 | sh-p01/1 | empty | E:e:None |
      | I07 | sh-p01/1 | empty | E:e:None; C:u:A; X:u:A |
      | I08 | sh-p01/1 | invalid | E:d:A |
      | I09 | sh-p01/1 | invalid | C:d:A |
      | I10 | sh-p01/1 | invalid | X:d:A |
      | I11 | sh-p01/1 | mismatch | C:u:B |
      | I12 | sh-p01/1 | mismatch | X:u:B |
      | I13 | sh-p01/1 | invalid | C:z:"" |
      | I14 | sh-p01/1 | invalid | E:e:None; E:z:""; C:u:A; X:u:A |
      | I15 | sh-p01/1 | mismatch | C:u:a |
      | I16 | sh-p01/1 | mismatch | X:m:A; X:u:" A" |
      | I17 | sh-p01/1 | invalid | E:d:A; C:z:""; C:m:B; C:u:C; X:d:A; X:m:B; X:u:C |
      | I18 | sh-p01/1 | invalid | X:z:""; X:m:A |
```

I19–I22 son pruebas de tipos/determinismo/inmutabilidad/opacidad adicionales;
su cobertura exacta está en la SPEC. Cada variante y fila ejecutada necesita
nodeid estable. Registrar el binding real después de colección; no inventar
un nodeid antes de existir el test ni derivar las expectativas de la salida.

Los actuales `accept parse`/`ir-dry` validan sintaxis/forma. No equivalen a
ejecutar estos ejemplos. `tests/acceptance/steps.py` hoy solo ejecuta reserva
del ejemplo; no usar `accept run/mutate` con ese handler para certificar P01.
El coder implementará contract tests directos y parametrizados; la aceptación
ensamblada del comando opt-in tiene su puerta propia en P06.
