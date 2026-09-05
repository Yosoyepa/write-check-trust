# ADR-F-02 — Retiro del checker `testless` e inversión del feature residual a ratchet

Fecha: 2026-09-05 · Estado: aceptado · Autor: arquitecto (delegación permanente)

## Contexto

La tabla `_CHECKERS` (`redteam.py:155-159`) declara tres reconocedores
residuales: `testless`, `protected-write`, `forbidden-command`. Con F4-b
convertido a gate-tool, `testless` queda con cero usuarios reales — solo lo
ejercitan casos sintéticos de tests unitarios. El feature
`wct-redteam-residual-001` queda con un Examples de cero filas.

## Decisión

1. **Retirar** `_reject_testless` y su entrada en `_CHECKERS` (STYLE-006:
   el código muerto que introdujimos en PR-C se retira en la misma deuda, no
   se deja "por si acaso"). El arnés `heuristic` del despachador NO se toca:
   los casos hook comparten `_reject_verdict` (`redteam.py:240-241`) y el
   mecanismo queda disponible para una declaración futura consciente.
2. **Re-enfocar** los casos sintéticos R1/X5/X6 de `test_redteam_engine.py`
   hacia checkers reales (protected-write / forbidden-command): el despachador
   hook/heuristic sigue probado, sin resurrectos.
3. **Invertir** el feature `wct-redteam-residual-001`: de "los residuos
   están declarados" a "no hay residuos declarados". El escenario de conteo
   se convierte en ratchet — un caso futuro con `harness: heuristic` pone el
   feature en rojo y obliga a declararlo consciente (actualizar este feature
   y su ADR), exactamente el mecanismo del resto de ratchets del repo. El
   escenario del invariario de modos se conserva (sigue siendo cierto y vive
   ahí). Nueva prueba unitaria `test_union_declares_zero_heuristics` lo
   fija a nivel código.

## Alternativas rechazadas

- **Conservar el checker para casos sintéticos** — código productivo vivo
  solo para que tests lo ejerciten es la definición de deuda: si vuelve a
  haber un residuo, se restaura con su caso y su razón in situ (el git
  history conserva la forma).
- **Feature con Examples vacío** — un Scenario Outline sin filas no
  parametriza nada (TEST-010) y el pipeline de aceptación lo parsea como
  escenario sin ejemplos: ruido, no contrato.
- **Borrar el feature completo** — pierde el escenario del invariario de
  modos y pierde el ratchet: nada pondría en rojo una declaración heurística
  futura accidental.
