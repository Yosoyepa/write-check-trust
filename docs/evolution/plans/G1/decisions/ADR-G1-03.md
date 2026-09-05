# ADR-G1-03 — Un contrato de veredicto, dos consumidores observables (G1a)

Estado: **aceptado** (yosoyepa, 2026-09-05). Sustituye a la versión
anterior (que afirmaba por error que G-MUT usaba ERROR con herramienta
ausente — es SKIP, `mutation.py:43`). Trazabilidad: REVIEW-G1 §6, §10, D5.

## Decisión

1. **Una función adaptadora** (en `tools/wct/mutate/`, casa exacta a definir
   por el coder dentro de la frontera del SPEC-G1a) ejecuta la secuencia
   run → results-inventario → clasificación de ADR-G1-01 y retorna un
   **`GateResult` existente** — no se añade un tipo `Verdict` redundante:
   status/summary/details/command ya expresan fase, conteos e identidades.
   Es un puerto IO real (orquestación de subprocess), no una capa por gusto.
2. **Gate**: `gate_mutation` delega en el adaptador; mapeo PASS/FAIL/ERROR/
   SKIP según ADR-G1-01; conserva la fachada y su export público.
3. **CLI**: `wct mutate run` — delta cero → mensaje informativo exit 0
   (RG08); delta > 0 → adaptador con la MISMA política del gate → exit
   0/1/2 e **impresión legible: estado, fase, conteos, identidades y
   límites del claim**. `engine.run` hoy retorna int; se permite tocar
   `cli.py` para IMPRIMIR el diagnóstico (la frontera "solo help" del
   primer dossier era insuficiente — REVIEW-G1 §10).
4. **El CLI se prueba por subprocess del entrypoint real** (`uv run wct
   mutate run` sobre un micro-repo fixture), no llamando `engine.run` en
   Python (RG09). El fixture ejercita delta con manifiesto AUSENTE —
   `scan` marca toda función como cambiada (`engine.py:107-116`) — sin
   tocar el manifiesto/lock protegidos del repo. Si el fixture necesita un
   manifiesto, se genera con la herramienta permitida DENTRO del tempdir,
   nunca editando `governance/`.

## Alternativas rechazadas

- `fresh=False` como vía certificada del CLI: heredaría resultados de
  funciones cuyos tests se debilitaron (REVIEW-G1 §6); eliminado.
- Gate como wrapper del CLI por subproceso: pierde control del root del
  fixture (los casos gate-tool del red team invocan la función) y añade
  una capa de parsing humano.
- Tres módulos con lógica difusa: reproduce la divergencia F02.

## Consecuencias y riesgos

- Cambio observable del CLI (exit semántico + diagnóstico impreso): fijo
  por Gherkin y probado por subprocess; la ayuda se actualiza.
- `GateResult` reutilizado con details más largos: sin cambio de esquema
  ni de agregación de tiers; O-001 (evidencia por ejecución) sigue en G3.
- El diagnóstico impreso por el CLI es salida nueva: mantenerlo estable y
  parsable amodestamente (líneas `estado:`, `fase:`, `identidades:`) para
  no crear un contrato informal frágil.
