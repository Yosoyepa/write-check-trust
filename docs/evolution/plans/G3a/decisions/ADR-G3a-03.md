# ADR-G3a-03 — Estrategia CI acotada: promoción por control, no `full` indiscriminado

Estado: propuesto (requiere aprobación humana; el workflow está protegido —
SEC-005 — y su diff se autoriza aparte). Trazabilidad: encargo humano
("no pondría todo full en CI indiscriminadamente"); ANALYSIS §1 §5.

## Decisión

Dos fases separadas por tipo de autorización:

**G3a-1 — sin tocar el workflow** (autorizada 2026-09-05 con ajustes
obligatorios; entrega sin commit en este encargo):

- Promover **G-INTROVERT a `_COMMIT_GATES`** y **RETIRAR su entrada
  literal de la lista full** (evitar duplicación: full ya es
  `[*_COMMIT_GATES, …]`). Efecto verificado sobre **pr**, que hereda
  `_COMMIT_GATES`: el control entra también al tier pr — documentado y
  probado en tests de membresía. Lógica del analizador INTACTA (limitación
  subprocess solo se documenta: ADR-G3a-04).
- El test repo-pinned de ADR-G3a-01 refuerza la misma frontera dentro de
  la suite.
- Restaurar ambas clases de aserción en el test del CLI (ADR-G3a-04).

**G3a-2 — con autorización humana del diff exacto del workflow**:

- Un paso nuevo tras la cobertura existente:
  `uv run wct ratchet check --require coverage-total,docstring-coverage`
  (o la lista que apruebes). La procedencia del LCOV la da el orden de
  pasos (el paso de cobertura ya existe antes); interrogate ya viene con
  `--group quality`.
- No se añade `full` ni `pr` al workflow en G3a: cada control adicional
  (G-MUT, G-COV-TOTAL, G-ACCEPT-MUT, G-PROP…) requiere su propio análisis
  de dependencias/costo y autorización — backlog con medición, no paquete.

## Addenda 2026-09-05 — G3a-2 con separación property (post-G3a-1)

G3a-1 se fusionó (PR #39, `f449cd6`). Para G3a-2, el paso único descrito
arriba se AMPLÍA a tres cambios en `quality.yml`, reconciliados con el
hallazgo R03 de RELEASE-BETA2/READINESS.md:

1. El paso de cobertura existente añade `-m "not property"`: alinea el
   workflow con la receta productiva (`_COVERAGE_TOTAL_COMMAND`, ya
   fijada por G3a-1) y con TEST-008. Hoy el workflow es la única receta
   que INCLUYE property en coverage — segunda definición, patrón F05.
2. Paso nuevo `Require measured ratchets` inmediatamente después del
   productor (frescura por orden de pasos, sin `continue-on-error`).
3. Paso nuevo `Run property tests separately`: necesario por (1) — G-TEST
   de commit corre `tests/unit tests/integration -m "not property"`
   (`gate/runner.py:369-372`), así que excluir property del productor sin
   este paso dejaría a los property SIN ejecución en CI. El paso preserva
   la ejecución que hoy vive dentro de cobertura; no añade una batería
   nueva.

La separación property es una ampliación explícita respecto del paso
único original de este ADR: requirió aprobación humana del diff completo
— **otorgada como Puerta 1 el 2026-09-05 (yosoyepa)**, aplicada
byte a byte — y medición del costo del paso añadido (sin promesa de
coste cero). El diff exacto, evidencia de viabilidad (exigible 2/2 sobre
LCOV sin property, exit 0), tests de contrato con rojo honesto y su
ejecución viven en
[specs/SPEC-G3a-2](../specs/SPEC-G3a-2.md).

## Inventario de controles faltantes (para decisiones futuras, NO parte de G3a)

| Control | Tier actual | Dependencia | Costo preliminar |
|---|---|---|---|
| G-INTROVERT | full | AST solo | barato → G3a-1 lo promueve |
| ratchet check (exigible) | ninguno | estáticas + interrogate + LCOV previo | barato → G3a-2 |
| G-COV-TOTAL | full | suite con cobertura | ya corre en CI como paso de cobertura, PERO el piso del ratchet no se aplica (F05) — candidato posterior |
| G-MUT | full | mutmut + alcance src/example | segundos hoy; escala con H0/H1 |
| G-ACCEPT-MUT / G-PROP | pr | fixtures de aceptación | sin medir |
| G-SAST-SEMGREP, G-SBOM, G-CRAP… | full | herramientas varias | sin medir |

## Alternativas rechazadas

- **`--tier full` en CI**: mezcla controles caros con baratos, encarece
  cada PR sin medición y acopla CI a dependencias opcionales (SKIPs masivos
  = ruido). El encargo lo veta y este ADR concuerda.
- **Duplicar los comandos en YAML en vez de promocionar por membresía**:
  deriva de contratos (el YAML se vuelve una segunda definición de qué se
  verifica — F05 de nuevo).

## Consecuencias

- G3a-1 requiere bless (toca `tools/wct/**`); G3a-2 además requiere tu
  autorización explícita del diff del workflow ANTES de escribirlo.
- La membresía de tiers queda como única fuente de verdad de qué corre
  localmente; CI referencia tiers/comandos, no los redefine.
