# ADR-D-04 — El artefacto de aceptación es reproducible entre checkouts

Estado: aceptado (arquitecto, 2026-09-05).
Contexto: [ANALYSIS.md](../ANALYSIS.md) §1 "artefacto con ruta absoluta".

## Decisión

El IR de un feature registra su `source` como ruta RELATIVA al root del
repo cuando el feature vive debajo de él (fallback: la ruta tal cual si
no es derivable). `wct accept generate` produce entonces el mismo
artefacto desde cualquier checkout/worktree. El artefacto existente se
regenera SOLO con la herramienta (`wct accept generate`, TEST-009: los
manifiestos y artefactos generados no se editan a mano).

## Evidencia que decide

El bug mordió durante PR-C: correr el pipeline desde el worktree
regeneró `tests/acceptance/generated/test_acceptance.py` con
`"source": ".../build/tmp/wt-c-merge/features/example.feature"` y ensució
el árbol (diff observado: únicamente el campo `source`). Un artefacto
versionado que depende de la ruta absoluta del checkout es una mentira de
reproducibilidad — el mismo input produce outputs distintos según dónde
vivas.

## Alternativas consideradas

- **(a) Excluir el artefacto del repo (generarlo en cada corrida)**:
  rechazada — el artefacto versionado es el registro auditable de qué IR
  ejecuta la suite de aceptación (O-001: resultados ligados a artefacto).
- **(b) Gitignore del artefacto**: mismo rechazo con menos matices.

## Consecuencias

- Test de estabilidad: `generate` desde dos roots distintos produce
  bytes idénticos.
- El diff de regeneración del artefacto existente debe mostrar ÚNICAMENTE
  la ruta relativa — cualquier otra diferencia es un hallazgo y se
  reporta, no se commitea.
