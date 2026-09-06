# G3a — Paridad de verificación: ejecución y completitud de los ratchets

Fecha: 2026-09-05. Estado: **G3a-1 FUSIONADA (PR #39, `f449cd6`); G3a-2
AUTORIZADA (Puerta 1, yosoyepa 2026-09-05) y EJECUTADA (working tree: diff
del workflow + feature + tests T1–T5 con rojo honesto; SIN commit — staging
propuesto, G-META-1 rojo por diseño hasta bless); G1b productivo NO
autorizado**. Código analizado: `f449cd6` (main).
Padres: POST-PR36 (F05/G3), REVIEW-G1, G1 (escape #37/#38 y su registro en
EVIDENCE.md). Encargo directo del humano tras el cierre de G1a.

## Recomendación (concreta)

1. **G3a-1 (sin tocar workflow):** convertir el escape #37/#38 en regresión
   DENTRO de la suite que CI ya ejecuta (test repo-pinned con control
   negativo emparejado) y promover **G-INTROVERT al tier commit** (gate
   AST-only, barato) — el escape observado #37/#38 tiene regresión y
   control ejecutado en CI, sin cambios en `.github/workflows/**`. No es
   una garantía universal: el analizador conserva sus límites
   (ADR-G3a-04) y full sigue fuera de quality.
2. **G3a-2 (con autorización del diff exacto):** tres cambios en
   `quality.yml` — productor alineado sin property (TEST-008), paso
   `wct ratchet check --require coverage-total,docstring-coverage`
   inmediatamente después, y ejecución separada de property (sin ella,
   property perdería su única ejecución en CI). Ausencia de medición
   exigible = fallo, nunca salto. Ver [specs/SPEC-G3a-2](specs/SPEC-G3a-2.md).
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
| [specs/SPEC-G3a-1](specs/SPEC-G3a-1.md) | Spec del coder (G3a-1) — EJECUTADA en PR #39 |
| [specs/SPEC-G3a-2](specs/SPEC-G3a-2.md) | Spec del coder (G3a-2) — AUTORIZADA (Puerta 1) y EJECUTADA con evidencia honesta de rojo/verde |
| [GHERKIN-G3a.md](GHERKIN-G3a.md) | Feature parametrizada G3a-1 (aprobada; vive en `features/wct-premerge-verification-001.feature`) |
| [GHERKIN-G3a-2.md](GHERKIN-G3a-2.md) | Feature G3a-2 APROBADA (Puerta 1); vive en `features/wct-ci-ratchet-exigible-001.feature` |
| [DoD.md](DoD.md) | DoD por unidad |
| [PRESUPUESTO.md](PRESUPUESTO.md) | Plan de medición emparejada (a ejecutar en implementación) |

Fuera: G1b (investigación ya desbloqueada aparte — ver
`G1/INVESTIGACION-G1b.md`), G2, #35, dedup, H0/H1.
