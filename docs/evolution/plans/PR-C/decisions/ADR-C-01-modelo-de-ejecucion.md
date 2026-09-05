# ADR-C-01 — Modelo de ejecución: un arnés por caso, fixtures aislados, archivos por arnés

Estado: propuesto (se ejecuta al aprobarse GHERKIN-C.md).
Contexto: [ANALYSIS.md](../ANALYSIS.md).

## Decisión

1. **Arnés por caso** (campo `harness` en el YAML): `gate-engine`,
   `gate-tool`, `hook`, `heuristic`. El despachador (`redteam.py`) ejecuta
   según el arnés:
   - `gate-engine`: importa el **engine productivo** que su gate usa y lo
     corre sobre el fixture del caso. Misma API que el gate — si el engine
     cambia, el red team cambia con él.
   - `gate-tool`: invoca la **función de gate** (`REGISTRY[gate]` o la
     función interna que el REGISTRY referencia) sobre el fixture. Estado
     SKIP por herramienta ausente → **SKIP visible** en el resumen.
   - `hook`: camino actual (`pre_tool_use`) — sin cambios de fondo.
   - `heuristic`: reconocedor residual, etiquetado y justificado (ADR-C-02).
2. **Fixtures aislados**: cada caso declara su receta como builder Python
   (`selftest/fixtures_engine.py` / `selftest/fixtures_tools.py`: id →
   función que planta archivos y retorna el root del tmpdir). Un caso, un
   tmpdir; nada comparte estado.
3. **Partición de YAML por arnés** (para workstreams disjuntos):
   `cases.yaml` queda con hook + heuristic (edición exclusiva de R1 al
   recortar); `cases-engine.yaml` (R1) y `cases-tool.yaml` (R2) nuevos. El
   runner carga los tres y valida el invariario de modos (≥2 por F1–F15)
   **sobre la unión**; archivos ausentes se toleran para que cada worktree
   sea verde independiente.
4. **Resumen honesto** (hermano del render de A1): `selftest redteam` reporta
   conteos por arnés — p.ej. `30/30 rechazados · 10 gate-engine · 12
   gate-tool · 4 hook · 4 heuristic (declarados) · 0 SKIP` — y los SKIP
   lista con el caso y la herramienta ausente.
5. **Semántica de fallo de caso**: un caso convertido falla si el motor
   productivo NO reporta el defecto plantado. Ese rojo es un **hallazgo del
   instrumento** (falso negativo real del gate contra el adversario que
   declara cazar) y se reporta, no se maquilla ajustando el fixture hasta
   pasar.

## Alternativas consideradas

- **(a) Correr el tier completo sobre un repo-fixture monoliéxico**: rechazada
  — corre 26 gates para 30 casos (runtime ×26) y mezcla señales; el caso
  quiere SU gate, no el universo.
- **(b) Subprocess `wct gate` por caso (CLI completa)**: rechazada para
  engines (import directo es más rápido y tipa la dependencia); usada solo
  donde el gate YA es subprocess (gate-tool hereda su forma).
- **(c) Mantener heurísticas y añadir gates en paralelo ("doble verificación")**:
  rechazada — duplica el mantenimiento y el reporte vuelve a ambiguo; la
  conversión es sustitución, no adición.
- **(d) Un solo cases.yaml editado por ambos coders**: rechazada — frontera
  de archivos es la garantía de fusión limpia (lección de A1/A2/B); la
  partición por arnés la hace natural.

## Consecuencias

- El 30/30 pasa a significar "los motores productivos cazaron 26 adversarios
  y 4 residuos declarados fueron validados por sus heurísticas etiquetadas".
- Los falsos negativos que aflorarán (si los hay) son el primer output real
  de la calificación del instrumento (O-002) — insumo directo del gate de
  decisión del Horizonte 1 ("rediseñar o degradar gates antes de medir
  modelos").
- `selftest redteam` sube de runtime con el grupo quality ausente/presente
  — presupuesto medido en VERIFICATION.
