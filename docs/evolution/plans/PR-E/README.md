# Plan PR-E — La mutación se vuelve real y verificable

Estado: **autorizado por delegación de arquitecto** (2026-09-05, "mantenemos
ritmo hasta mi bless continúa" — continuidad de la delegación de PR-D).
Corte de código: `9feac78` (main, post PR-D/#32).

## Objetivo de la fase

Quedan 4 residuos declarados en el red team; 3 de ellos (F2-a, F2-b, F5-b)
comparten una redención: corridas REALES de mutación. Hoy `G-MUT` corre
`mutmut run` solo sobre `src/example` (43 mutantes, todos cazados, 1.9s) y
no pertenece a ningún tier — el perfil de capacidades de PR-D lo destapó.
PR-E entrega:

1. **Las 3 redenciones con corridas reales**: cada caso planta su defecto
   (src sin tests; test hardcodeado sobre camino no ejercido; test débil)
   en un fixture con su propio `[tool.mutmut]` y la función de gate
   productiva corre `mutmut run` AHÍ — los sobrevivientes se miden de
   verdad. El red team queda **13 engine · 12 tool · 4 hook ·
   1 heuristic** — solo F4-b (diff-cover con fixture git) queda declarado.
   F2-b es EL caso demostración de por qué la mutación existe (ADR-C-02).
2. **G-MUT cableado al tier full** con presupuesto medido (1.9s sobre el
   scope actual) — resuelve con evidencia la decisión que quedó en mesa.
3. **Contrato exit-code de mutmut mapeado** (paso 0 obligatorio): la
   evidencia preliminar dice todo-cazado→0, sobreviviente→2, tests-rotos→
   DESCONOCIDO (arte de la corrida del pipe). Si mutmut traga un runner
   roto, G-MUT tiene un hueco de honestidad que esta PR documenta o cierra.
4. **Root-cause del ruff desnudo a nivel árbol** (622 S101 pese al
   `extend` de ADR-D-03): fix si es quirúrgico, hallazgo documentado si no.

## Qué NO es esta PR (con números)

Extender la mutación al harness completo: `tools/wct` tiene **4.235
sitios en 57 archivos, 16 sobre el presupuesto de 100** de G-MUT-SITES, y
a ~18s por corrida de suite serían ~21 horas. Wholesale queda rechazado
con evidencia (ADR-E-01); la ruta futura (mutación diferencial por
función cambiada) es diseño propio para cuando el costo lo justifique.

## Documentos

| Documento | Contenido |
|---|---|
| [ANALYSIS.md](ANALYSIS.md) | Evidencia archivo:línea, números medidos, matriz exit-code, riesgos, rollback |
| [DoD.md](DoD.md) | DoD por feature, workstream, commit, revisión y merge |
| [decisions/ADR-E-01](decisions/ADR-E-01-alcance-mutacion.md) | Fixtures reales + tier; wholesale rechazado con números |
| [decisions/ADR-E-02](decisions/ADR-E-02-gmut-full-tier.md) | G-MUT a full + contrato exit-code load-bearing |
| [specs/SPEC-E-01](specs/SPEC-E-01-redencion-mutacion-real.md) | Coder-E1: las 3 conversiones |
| [specs/SPEC-E-02](specs/SPEC-E-02-tier-y-ruff.md) | Coder-E2: tier wiring + ruff root-cause |
| [GHERKIN-E.md](GHERKIN-E.md) | Escenarios (delegación vigente; el bless los sella) |
| [VERIFICATION.md](VERIFICATION.md) | DoD de merge, matriz, secuencia humana |

## Dentro / fuera

**Dentro**: 3 conversiones gate-tool con mutmut real sobre fixtures;
G-MUT en TIERS["full"]; mapeo del contrato exit-code; root-cause ruff
desnudo (fix condicional); docs/features/addendums.

**Fuera**: mutación wholesale del harness (números arriba); convertir
F4-b; tocar la selección de tests del repo; nuevo diseño de mutación
diferencial; la deduplicación de plantillas (deuda registrada, PR propio).
