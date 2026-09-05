# ADR-D-02 — F11-b redimido: vulture a confianza 60 con whitelist de 1 entrada

Estado: aceptado (arquitecto con autoría delegada sobre la decisión
pendiente de umbral, 2026-09-05). Redime el residuo F11-b declarado en
ADR-C-02 (addendum).
Contexto: [ANALYSIS.md](../ANALYSIS.md) §1 "sonda vulture@60".

## Decisión

`dead_code.vulture_min_confidence` baja de 80 a 60 con una whitelist de
exactamente una entrada (`abstract_symbols`, el falso positivo del
dataclass consumido vía `asdict()`). La clave nueva
`dead_code.whitelist` en thresholds.yaml nombra el archivo; el comando
del gate añade `--whitelist` solo cuando la clave existe (patrón PR-B:
config declarada, ausencia nombrada). F11-b se convierte a gate-tool con
fixture que declara confianza 60 y planta una constante muerta.

## Evidencia que decide

- Sonda sobre main (2026-09-05): vulture@60 reporta **1 hallazgo en todo
  el repo**, y es un falso positivo por reflexión. Muerte real a 60:
  cero. El costo del umbral es una línea de whitelist.
- Beneficio: la clase función/constante/atributo muerto (confianza 60) —
  el adversario que F11-b declaraba como escape desde PR-C — pasa a ser
  cazada por el gate productivo.
- Baseline del ratchet dead-code SIN fricción: hallazgos netos quedan en
  0 → no se necesita `ratchet record` ni `raise`.

## Alternativas consideradas

- **(a) Mantener 80 y dejar F11-b residuo**: rechazada con la sonda en la
  mano — mantener el hueco cuesta más (un adversario real sin caza) que
  la whitelist de 1 entrada.
- **(b) Bajar a 60 SIN whitelist y re-registrar la baseline con el FP**:
  rechazada — graba un falso positivo en la baseline del ratchet y
  requiere `ratchet record` humano para ruido conocido.
- **(c) Whitelist grande preventiva**: rechazada — la sonda dice que no
  hace falta; entries speculative son deuda.

## Consecuencias

- `wct gate --tier commit` (G-DEAD) pasa a escanear a 60: si aparece
  muerte nueva de confianza 60 en la selección del gate, ES muerte real y
  se arregla o se declara — no se whitelistea por defecto.
- F11-b deja el arnés heuristic; quedan 4 residuos (F2-a, F2-b, F4-b,
  F5-b) cuya redención es el PR de mutación del harness (PR-E).
- El caso YAML de cases.yaml pierde a F11-b; cases-tool.yaml lo gana con
  `tool: vulture`; el feature de residuos pierde su fila.
