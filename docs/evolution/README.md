# Dossier de evolución de WCT

Estado: **propuesta de producto y evaluación; no constituye implementación ni
decisión de gobernanza aceptada**.

Fecha de corte: 2026-09-01. Revisión local: `82d686d491baeac5ea03227c7283aeaf7d84628c`.

Este dossier responde a dos preguntas distintas que no deben confundirse:

1. ¿Qué tan fielmente los gates de WCT cumplen hoy las promesas documentadas?
2. ¿Cuánto mejora realmente un modelo económico cuando trabaja con reglas,
   gates y ciclos de reparación de WCT?

La primera pregunta es un prerrequisito de la segunda. Un gate verde no es una
medición independiente de que el cambio sea correcto cuando el propio gate es
parte del tratamiento experimental.

## Ruta de lectura

| Documento | Decisión que habilita |
|---|---|
| [Evaluación ejecutiva](00-evaluacion-ejecutiva.md) | Entender el diagnóstico, la tesis y las prioridades |
| [Auditoría de gates](01-auditoria-de-gates.md) | Distinguir control existente, control parcial y promesa aún no medida |
| [Estudio de DeepSeek Harness](02-estudio-deepseek-harness.md) | Identificar ideas reutilizables y límites de adopción |
| [Programa de evaluación](03-programa-de-evaluacion.md) | Medir causalmente el valor de WCT sobre modelos económicos |
| [Portafolio de oportunidades](04-portafolio-de-oportunidades.md) | Priorizar problemas, features y criterios de salida |
| [Roadmap](05-roadmap.md) | Ordenar la evolución desde beta hasta evidencia externa |
| [Trazabilidad](TRACEABILITY.md) | Conectar hallazgos, decisiones, requisitos y métricas |
| [Fuentes](SOURCES.md) | Auditar la procedencia de afirmaciones externas |

## Decisiones propuestas

- [ADR-004: separar plano de control y plano de evaluación](decisions/ADR-004-plano-de-evaluacion-separado.md)
- [ADR-005: calificar los gates antes de afirmar mejora de modelos](decisions/ADR-005-calificar-gates-antes-de-modelos.md)
- [ADR-006: usar oráculos independientes y holdout privado](decisions/ADR-006-oraculos-independientes.md)
- [ADR-007: integrar DeepSeek Harness solo como adaptador opcional](decisions/ADR-007-deepseek-adaptador-opcional.md)

## Requisitos de producto propuestos

- [PRD-001: Evidence Lab](prd/PRD-001-evidence-lab.md)
- [PRD-002: calificación end-to-end de gates](prd/PRD-002-calificacion-de-gates.md)
- [PRD-003: benchmark de uplift para modelos económicos](prd/PRD-003-benchmark-modelo-economico.md)
- [PRD-004: observatorio de adopción](prd/PRD-004-observatorio-adopcion.md)

## Especificaciones de análisis

- [SPEC-001: contratos de tarea, experimento y ejecución](specs/SPEC-001-contratos-experimentales.md)
- [SPEC-002: métricas, estadística y criterios de decisión](specs/SPEC-002-metricas-y-estadistica.md)
- [SPEC-003: ledger de evidencia, replay y reproducibilidad](specs/SPEC-003-ledger-y-replay.md)
- [SPEC-004: gobierno del corpus](specs/SPEC-004-gobierno-del-corpus.md)

## Planes de ejecución por PR

Cada PR del roadmap se planifica como fase completa (análisis, investigación,
ADRs, specs archivo-por-archivo, escenarios Gherkin para aprobación humana y
plan de verificación) antes de implementar nada.

- [PR-A1 — Honestidad del reporte del instrumento](plans/PR-A1/README.md)
  (O-003, O-004 y mitad de O-006; prerrequisito de PR-A2). Estado: **merge
  #28** — property aislado contractualmente, aceptación no vacua, resumen
  PASS/SKIP separados.
- [PR-A2 — El harness se mide a sí mismo](plans/PR-A2/README.md)
  (scope de cobertura + baseline aplicado). Estado: **merge #29** — coverage
  mide `src`+`tools/wct`, G-COV-TOTAL aplica `--cov-fail-under` del baseline,
  ratchet `coverage-total` con registro por métrica; piso registrado en 74.5
  (preciso, truncado hacia abajo; el redondeo entero del term habría fijado
  un piso inalcanzable — corrección fechada en ADR-A2-01).
- [PR-B — Conformidad configuración → runtime](plans/PR-B/README.md)
  (O-005). Estado: **merge #30** — 4 gates construidos desde thresholds.yaml
  (clave ausente = gate rojo que la nombra), 4 constantes declaradas con
  procedencia, y `wct doctor` con la sección de conformidad en vivo (12
  pares). Primer DoD por unidad de aceptación (feature/workstream/commit/
  revisión) — estándar desde ahora.
- [PR-C — Red team productivo](plans/PR-C/README.md) (O-002). Estado:
  **merge #31** — 30 casos = 13 gate-engine · 8 gate-tool · 4 hook ·
  5 heuristic (F9-b redimido en la misma PR). La ejecución destapó 2
  escapes reales y 2 atribuciones erróneas del reconocedor paralelo;
  G-ACCEPT le corrigió el escenario al arquitecto.
- [PR-D — Perfiles y completitud](plans/PR-D/README.md) (O-006). Estado:
  autorizado por delegación de arquitecto (2026-09-05), en ejecución.
  Perfil de capacidades derivado del constructor (herramienta, presencia,
  scope, tiers), resumen honesto con SKIPs, y tres redenciones: F11-b
  (vulture 60 + whitelist, sonda = 1 FP), ruff sin --config, artefacto de
  aceptación con ruta relativa.

## Límites

El dossier no introduce código, dependencias, gates, cambios de umbral ni
modificaciones bajo `governance/`. Los ADR aquí contenidos son propuestas para
discusión humana. Cualquier implementación posterior deberá pasar por sus
propios escenarios Gherkin, aprobación y TDD según el contrato vigente del
repositorio.
