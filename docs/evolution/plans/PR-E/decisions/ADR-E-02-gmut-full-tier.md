# ADR-E-02 — G-MUT entra al tier full; el contrato exit-code es parte del entregable

Estado: aceptado (arquitecto con delegación vigente, 2026-09-05; resuelve
la decisión que PR-D dejó en mesa).
Contexto: [ANALYSIS.md](../ANALYSIS.md) §1.

## Decisión

1. `G-MUT` se agrega a `TIERS["full"]` en `runner.py` (una línea). Medido
   sobre main: 1.9s sobre el scope actual — el tier full local pasa de
   ~45s a ~47s. **No** entra a `pr`: preserva el presupuesto de CI y
   evita ensuciar el workspace de CI con el cache de mutmut; subirlo a pr
   queda como decisión futura si el scope del ejemplo crece en costo.
2. El paso 0 de E1 mide la matriz exit-code de `mutmut run` (cazado /
   sobreviviente / runner-roto) SIN pipes (redirigir a archivo y leer
   `$?` — la trampa que ya nos cobró tres veces). Si la fila
   runner-roto resulta exit 0, G-MUT aprueba en falso sobre fixtures
   rotos: se documenta como hallazgo del instrumento y, si el cierre es
   barato (p. ej. verificar `mutmut results` además del exit code en la
   función de gate), se propone como parte del handoff para decisión del
   arquitecto en revisión.

## Alternativas consideradas

- **(a) Dejar G-MUT sin tier y documentarlo manual-by-design**: rechazada
  — el perfil de capacidades de PR-D lo destapó como gap; con 1.9s el
  costo de cablearlo es inexistente y el tier full pierde su excusa.
- **(b) Cablearlo también a pr**: diferida — CI budget + artefactos de
  cache; no bloquea nada.

## Consecuencias

- `wct gate --tier full` pasa a incluir mutación real: 34 gates.
- El perfil de capacidades lo refleja automáticamente (tiers derivados).
- STATUS.md actualiza el conteo del tier full (33 → 34).

## Corrección fechada — la matriz real (ejecución, 2026-09-05)

El paso 0 de E1 midió la matriz completa y la fila peligrosa no era la
prevista: runner-roto → exit 1 (FAIL, ese hueco NO existe); la fila rota
es **sobrevivientes → exit 0** (mutmut 3.7.0 imprime stats y sale 0;
lectura de fuente confirmada; el "exit 2" del probe del ANALYSIS era el
exit del hijo de pytest). Consecuencia: G-MUT cableado como
`external(["mutmut","run"])` daba PASS en falso ante sobrevivientes — no
verificaba TEST-002. Ruling del arquitecto: G-MUT se convierte en función
de gate que corre mutmut y FALLA si `survived >= 1` (alineado con la
regla que dice verificar); con el contrato cerrado, F2-b/F5-b se redimen
tal como el SPEC las definió.
