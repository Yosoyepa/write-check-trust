# Plan PR-A2 — El harness se mide a sí mismo: scope y baseline de cobertura

Estado: **plan completo pendiente de aprobación humana de escenarios** (PROC-003).
Corte de código: `b7eda55` (main, post PR-A1/#28). Prerrequisito cumplido: PR-A1
(exclusión de property ya vigente; el 73 % fue medido bajo esa semántica).

## Objetivo de la fase

Cerrar la deuda más incómoda del dossier (O-003): **la cobertura de WCT no
mide a WCT**. Hoy `source = ["src/example"]` mide 61 statements del código
ejemplo y el baseline `coverage-total.json` (100.0) es huérfano — nadie lo
lee. Tres cambios honestos:

1. **Scope**: la cobertura mide `src` + `tools/wct` (2 509 statements reales).
2. **Aplicación**: G-COV-TOTAL lee el baseline y lo aplica como
   `--cov-fail-under`: el 100 % deja de ser decorativo; hay piso.
3. **Ratchet**: `coverage-total` entra a `measurements()` leyendo el artefacto
   lcov que el propio gate produce, y `ratchet record` gana registro por
   métrica para que el humano pueda re-baselinear sin tocar las demás.

## La decisión humana central (ADR-A2-02)

El baseline vigente (100.0) fue sembrado (`recorded_by: "seed"`, commit null)
sobre el scope del ejemplo. Con scope real el total medido es **73 %** (medido
dos veces: con y sin property — idéntico). Aplicar el baseline sin
re-baselinear dejaría el árbol permanentemente rojo. El plan exige tu
`ratchet record --metric coverage-total` sobre la rama del PR, con razón que
cite el PR: registrar el punto de partida verdadero desde donde el ratchet
solo puede subir. No es bajar un umbral para pasar: es corregir el scope de
una cifra que siempre prometió ser "del repo completo" (la nota del propio
archivo baseline lo dice) y nunca lo fue.

## Documentos

| Documento | Contenido |
|---|---|
| [ANALYSIS.md](ANALYSIS.md) | Evidencia, datos de diseño (G-DEBT en fast tier, 41× de tamaño, semántica de fail-under), riesgos, rollback |
| [decisions/ADR-A2-01](decisions/ADR-A2-01-mecanismo-de-aplicacion.md) | Cómo se aplica el baseline: fail-under en el gate + medición por artefacto (4 alternativas) |
| [decisions/ADR-A2-02](decisions/ADR-A2-02-rebaseline-humano.md) | Re-baseline 100→73: secuencia humana y por qué es legítimo |
| [specs/SPEC-A2-01](specs/SPEC-A2-01-scope-y-baseline.md) | Spec archivo-por-archivo con tests TDD nombrados |
| [GHERKIN-A2.md](GHERKIN-A2.md) | **Escenarios para aprobación humana** |
| [VERIFICATION.md](VERIFICATION.md) | DoD, matriz, predicciones falsables, secuencia humana completa |

## Dentro / fuera

**Dentro**: scope de coverage, aplicación del baseline en G-COV-TOTAL,
medición artifact-based en el ratchet, `ratchet record --metric`, ajustes de
docs factuales.

**Fuera**: extender `source_paths` de mutmut a `tools/wct` (41× statements;
exige rediseñar la selección de tests por mutante hacia la suite unit — PR
propio con estimación de runtime); SKIP en tier full (Horizonte 0); claves de
thresholds.yaml sin consumidor (PR-B).
