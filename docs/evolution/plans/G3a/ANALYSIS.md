# G3a — ANALYSIS: qué ejecuta CI, qué se salta, y la anatomía del escape

Corte: `f3c69b3`. Todo con atribución: [E] observación directa, [L] lectura
de fuente con líneas, [U] hallazgo del humano verificado aquí.

## 1. Matriz CI ↔ local (medida)

`.github/workflows/quality.yml` (job `commit-gates`) ejecuta [E]:

| Paso de CI | Contrato local equivalente |
|---|---|
| `wct rules check` + `wct integrity check` + `wct doctor` | integridad |
| `wct gate --tier commit` (20 gates) | tier commit |
| `pip-audit` (requirements exportados) | G-AUDIT |
| `pytest --cov --cov-branch --cov-report=lcov:…` + `diff-cover --fail-under=90` (solo PRs) | suite + G-COV-DIFF (con 90 HARDCODEADO, no thresholds — F05) |
| `wct accept mutate` (default = `features/example.feature`) | aceptación del EJEMPLO nada más |
| `wct selftest redteam` | red team |

**No ejecuta CI** [E]: `wct ratchet check` (en ningún tier ni paso), el tier
`full` completo (donde viven G-INTROVERT, G-COV-TOTAL, G-MUT, G-CRAP, G-CC,
G-DRY*, G-LCOM, G-SAST-SEMGREP, G-SBOM…), el tier `pr` (G-ACCEPT-MUT,
G-PROP, G-COV-DIFF como gate, …) — y `full` no es superconjunto de `pr`
(F05 de POST-PR36). "CI verde" acredita exactamente la tabla de arriba.

## 2. Anatomía del escape #37/#38 [E]

Un test introvertido llegó a main por tres vías simultáneas:

1. G-INTROVERT está solo en `full` (`gate/runner.py:506`) → invisible para
   el tier commit que CI corre.
2. `wct ratchet check` no existe en CI ni estaba en la matriz pre-merge de
   la PR #37 (sí en la de #36) — fallo de proceso del arquitecto.
3. NINGÚN test de la suite pineaba el invariario "el repo tiene cero tests
   introverted" — la suite que CI SÍ corre no podía verlo.

Consecuencia de diseño: la única capa que CI ejecuta garantizadamente es la
SUITE. Un contrato que no vive ni en tier-commit ni en un test es invisible
para CI por definición.

## 3. Semántica de salto de `ratchet check` [L + E + U verificado]

`ratchet/measure.py:118-140` (`measurements`): 8 métricas siempre medibles
por análisis estático (suppressions, debt-markers, introverted-tests,
archmetrics-zones, per-file-ignores, file-size, lcom-classes,
dry-template-clusters) y **2 condicionales que se omiten EN SILENCIO**:

- `docstring-coverage`: `None` si `interrogate` no está (`:44-51`).
- `coverage-total`: `None` si falta `build/coverage/lcov.info` (`:70-75`) —
  y si existe, se consume **sin comprobar procedencia ni antigüedad**.

`check()` (`:143-149`) itera lo que `measurements()` produjo: una métrica
omitida no es fallo. **"Todos los ratchets se mantienen" ≠ "todos los
ratchets se midieron"** [U, demostrado en vivo]: el `lcov.info` del árbol
local durante el cierre de G1a era del **2026-09-02 10:29** — tres días
viejo, anterior a los 19 tests y `verdict.py` — y el verde lo consumió sin
aviso [E, mtime].

## 4. Limitación de G-INTROVERT con subprocess [L]

`introvert/analyzer.py:71-79, 97-112`: una aserción es "grounded" solo si
referencia nombres importados del SUT (in-process) o derivados de ellos.
Un test que ejercita el entrypoint por subprocess y asevera sobre su salida
— comportamiento observable legítimo del SUT — es invisible para el
detector: puede salir "introverted" siendo un buen test (exactamente el
caso #37/#38). Es una limitación del detector, no un veredicto de calidad
del test [U]. Ensancharlo (reconocer salida de un entrypoint del SUT como
traza) es trabajo futuro con sensibilidad propia; G3a solo lo documenta y
establece la política de doble clase de aserciones (ADR-G3a-04).

## 5. Costos conocidos de los candidatos a promoción [E preliminar]

- `G-INTROVERT` (gate_introvert): análisis AST de `tests/**` — sin suite,
  sin subprocess pesado; coste del orden de los gates estáticos del tier
  commit (a medir emparejado en implementación, PRESUPUESTO.md).
- `ratchet check` exigible: 8 métricas estáticas + interrogate (si presente)
  + LCOV ya producido por la corrida — en CI el paso de cobertura corre
  ANTES, así que el artefacto es fresco POR ORDEN DE PASOS; localmente la
  ausencia del LCOV debe BLOQUEAR (fail-closed), no saltar.
- No se promueve `full` completo: G-MUT/G-COV-TOTAL/G-SBOM tienen costos y
  dependencias propias (mutmut, suite completa, ciclos de pip-audit) que
  exigen medición separada — fuera de G3a.
