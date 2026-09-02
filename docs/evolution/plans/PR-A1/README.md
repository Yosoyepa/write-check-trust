# Plan PR-A1 — Honestidad del reporte del instrumento

Estado: **plan completo pendiente de aprobación humana de escenarios** (PROC-003).
Nada de este plan está implementado. Rama previa `fix/instrument-honesty-p0a` fue
creada y descartada como trabajo prematuro; este documento la reemplaza.

Corte de código: `82d686d` (main, post PR #26). Fuente de diagnóstico:
[dossier de evolución](../../README.md) — verificado 7/7 contra el código
(ver [ANALYSIS.md](ANALYSIS.md)).

## Objetivo de la fase

Que lo que WCT **afirma sobre sí mismo** sea medible y verdadero en tres
superficies de reporte:

1. **Cobertura**: los property tests dejan de inflar la métrica (TEST-008).
2. **Aceptación**: un escenario sin parametrización no puede aprobar por
   mutación sin haber ejecutado mutación alguna (TEST-010).
3. **Resumen**: `PASS` y `SKIP` dejan de fusionarse en un mismo contador de
   "no bloqueantes" (prerrequisito de O-006, sin cambiar semántica de bloqueo).

Unificado: **el reporte de WCT no puede sobreafirmar**. Es el primer PR del
Horizonte 1 del [roadmap](../../05-roadmap.md) (O-003, O-004 y mitad de O-006),
y prerrequisito de PR-A2 (scope y baseline de cobertura: el baseline se debe
registrar bajo la semántica final de exclusión de este PR).

## Documentos

| Documento | Contenido |
|---|---|
| [ANALYSIS.md](ANALYSIS.md) | Evidencia verificada (archivo:línea), impacto cuantificado, riesgos, rollback, radio de explosión |
| [RESEARCH.md](RESEARCH.md) | Prior art que soporta cada decisión (markers/deselección, coverage del propio harness, mutación+property, pases vacíos, visibilidad de SKIP) |
| [decisions/ADR-A1-01](decisions/ADR-A1-01-aislamiento-property.md) | Cómo se aíslan los property tests (4 alternativas consideradas) |
| [decisions/ADR-A1-02](decisions/ADR-A1-02-aceptacion-no-vacua.md) | Semántica de veredicto no-vacuo (fail vs warn, dónde vive el check) |
| [decisions/ADR-A1-03](decisions/ADR-A1-03-honestidad-skip.md) | Conteo separado sin tocar semántica de bloqueo |
| [specs/SPEC-A1-01](specs/SPEC-A1-01-aislamiento-property.md) | Spec archivo-por-archivo con tests TDD nombrados |
| [specs/SPEC-A1-02](specs/SPEC-A1-02-aceptacion-no-vacua.md) | Spec del veredicto y del reporte de vacuidad |
| [specs/SPEC-A1-03](specs/SPEC-A1-03-resumen-skip.md) | Spec del render |
| [GHERKIN-A1.md](GHERKIN-A1.md) | **Escenarios para aprobación humana** — aterrizan en `features/` al implementar |
| [VERIFICATION.md](VERIFICATION.md) | Definition of done, matriz de verificación, contrato del coder, paso de bless |

## Flujo de aprobación (PROC-003)

1. Humano aprueba o corrige los escenarios de [GHERKIN-A1.md](GHERKIN-A1.md).
2. Coder implementa cada spec con TDD (TEST-001) en tres commits convencionales.
3. Verificación con salida real (PROC-012) según [VERIFICATION.md](VERIFICATION.md).
4. PR → bless humano único (`mutate update-manifest --approved-by`, razón citando
   el PR) → CI → squash merge.

## Dentro / fuera de alcance

**Dentro**: las tres superficies anteriores, sus tests, los escenarios Gherkin,
ajustes a documentación factualmente incorrecta tras el cambio.

**Fuera (explícito, con PR propio y análisis propio)**:

- `source_paths` de mutmut y `source` de coverage siguen en `src/example`;
  extenderlos a `tools/wct` es **PR-A2** (requiere re-baseline autorizado:
  medido 73 % con scope real vs 100 % declarado sobre 61 statements).
- Semántica de bloqueo de SKIP en tier full (perfil local vs completo): decisión
  de Horizonte 0; aquí solo se hace visible el conteo.
- Detección dura de vacuidad **por escenario** (aquí: fail agregado + warn por
  escenario); el endurecimiento pertenece a O-004 (corpus completo).
- Claves de thresholds.yaml sin consumidor (PR-B).
