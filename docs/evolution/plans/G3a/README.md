# G3a — Paridad de verificación: ejecución y completitud de los ratchets

Fecha: 2026-09-05. Estado: **G3a-1 AUTORIZADA con ajustes obligatorios
(yosoyepa, 2026-09-05; entrega SIN commit/push/PR en ese encargo); G3a-2 y
G1b productivo NO autorizados**. Código analizado: `f3c69b3` (main).
Padres: POST-PR36 (F05/G3), REVIEW-G1, G1 (escape #37/#38 y su registro en
EVIDENCE.md). Encargo directo del humano tras el cierre de G1a.

## Recomendación (concreta)

1. **G3a-1 (sin tocar workflow):** convertir el escape #37/#38 en regresión
   DENTRO de la suite que CI ya ejecuta (test repo-pinned con control
   negativo emparejado) y promover **G-INTROVERT al tier commit** (gate
   AST-only, barato) — el escape queda bloqueado por construcción, sin
   cambios en `.github/workflows/**`.
2. **G3a-2 (con autorización del diff exacto):** un paso de CI
   `wct ratchet check --require …` con artefacto de cobertura generado por
   la MISMA corrida (el workflow ya produce `lcov.info` antes): ausencia de
   medición exigible = fallo, nunca salto.
3. **Restaurar ambas clases de aserción** en el test del CLI (ajuste #38,
   registrado en EVIDENCE.md §addenda): contrato independiente + concordancia
   con el adaptador.
4. **Documentar la limitación de G-INTROVERT con subprocess** (el detector
   solo traza imports in-process) sin ensancharlo ahora.

NO se propone correr `full` completo en CI (encargo explícito): primero
inventario de controles faltantes, dependencias y costo (ANALYSIS §1).

## Documentos

| Documento | Contenido |
|---|---|
| [ANALYSIS.md](ANALYSIS.md) | Matriz CI/local medida, anatomía del escape, semántica de salto con líneas, LCOV rancio en vivo |
| [decisions/ADR-G3a-01](decisions/ADR-G3a-01.md) | La regresión del escape vive en la suite (test repo-pinned + control negativo) |
| [decisions/ADR-G3a-02](decisions/ADR-G3a-02.md) | Ratchets exigibles: medición presente y fresca; ausencia bloquea |
| [decisions/ADR-G3a-03](decisions/ADR-G3a-03.md) | Estrategia CI acotada (G3a-1 sin workflow; G3a-2 con autorización del diff) |
| [decisions/ADR-G3a-04](decisions/ADR-G3a-04.md) | G-INTROVERT y subprocess: limitación documentada + doble clase de aserciones |
| [specs/SPEC-G3a-1](specs/SPEC-G3a-1.md) | Spec del coder (G3a-1) — bloqueada hasta aprobación |
| [GHERKIN-G3a.md](GHERKIN-G3a.md) | Feature parametrizada para aprobación |
| [DoD.md](DoD.md) | DoD por unidad |
| [PRESUPUESTO.md](PRESUPUESTO.md) | Plan de medición emparejada (a ejecutar en implementación) |

Fuera: G1b (investigación ya desbloqueada aparte — ver
`G1/INVESTIGACION-G1b.md`), G2, #35, dedup, H0/H1.
