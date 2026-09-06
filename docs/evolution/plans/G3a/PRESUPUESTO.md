# G3a — Plan de presupuesto emparejado (POR MEDIR en implementación)

Ninguna cifra aquí es medición: es el protocolo. Regla (REVIEW-G1 §9): nada
de "costo cero"; muestra declarada; el presupuesto definitivo lo aprueba el
humano.

## Mediciones exigidas por G3a-1 (al implementar)

| Qué | Cómo | Reporte |
|---|---|---|
| Costo de G-INTROVERT en tier commit | `wct gate --tier commit` antes/después de la promoción, ≥3 reps mismo entorno | mediana + rango por gate y total |
| Costo del ratchet exigible vs tolerante | ambos modos, ≥3 reps (con LCOV presente y ausente) | mediana + rango |
| Suite | `pytest -q` antes/después (los tests nuevos suman; el repo-pinned es barato, el control negativo planta un fixture chico) | mediana + rango |

## Estimación de impacto CI (a confirmar con la medición)

- G3a-1: CI ya corre `--tier commit` → suma el tiempo de G-INTROVERT
  (análisis AST de tests/**; preliminarmente del orden de otros gates
  estáticos — ANALYSIS §5) + tests nuevos de suite. Sin pasos nuevos.
- G3a-2: un paso `ratchet check --require` (~estáticas + interrogate +
  LCOV ya producido): segundos; se mide antes del merge de esa unidad.

## Reglas del protocolo

1. Mismo entorno, scope, tests y versiones para antes/después; frío y
   caliente declarados por separado.
2. ≥3 repeticiones exploratorias; mediana y rango; NINGÚN p95 con muestra
   chica (H0 de POST-PR36, misma regla).
3. Cada cifra publicada cita el comando exacto y el entorno.
4. Si una medición emparejada no es posible (dependencia faltante), se
   declara no medida — no se estima.
