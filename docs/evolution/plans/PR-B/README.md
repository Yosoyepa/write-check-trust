# Plan PR-B — Conformidad configuración → runtime (O-005)

Estado: **plan completo pendiente de aprobación humana de escenarios** (PROC-003).
Corte de código: `ee17288` (main, post PR-A2/#29).

## Objetivo de la fase

`governance/thresholds.yaml` declara "TODOS los números del harness viven aquí"
— y hoy es una aspiración parcial: 8 umbrales viven como literales en
`gate/runner.py`, `dry/tpl.py`, `dry/analyzer.py` y `lcom/engine.py`, y al menos
5 claves declaradas con equivalente exacto no tienen lector. Cambiar el YAML no
cambia el gate: la configuración miente sobre su poder.

PR-B hace verdadera la declaración en ambas direcciones:

1. **Declarado → runtime**: los gates construyen sus comandos desde
   `thresholds.yaml` (crap, diff-cover 90, vulture 80, xenon B/A/A, dry
   min_lines/min_nodes).
2. **Runtime → declarado**: las 4 constantes huérfanas (lcom.min_methods,
   lcom.threshold, dry.template_threshold, dry.review_threshold) se declaran en
   thresholds.yaml — **edición de governance que requiere tu autorización
   explícita** (ADR-B-02 con el diff exacto; tu aprobación del plan la cubre y
   el bless la blinda).
3. **Visibilidad**: `wct doctor` lista cada clave cableada con su gate y valor
   efectivo — la conformidad se puede auditar con un comando.

## Documentos

| Documento | Contenido |
|---|---|
| [DoD.md](DoD.md) | **Definitions of done por unidad de aceptación**: feature, workstream de coder, commit, revisión y merge |
| [ANALYSIS.md](ANALYSIS.md) | Los 8 sitios verificados, inventario de claves huérfanas (insumo Horizonte 0), riesgos |
| [decisions/ADR-B-01](decisions/ADR-B-01-umbrales-declarados-a-runtime.md) | Cómo se cablea: gates dinámicos leyendo config; qué NO se inventa (perfiles crap) |
| [decisions/ADR-B-02](decisions/ADR-B-02-nuevas-claves-y-doctor.md) | Las 4 claves nuevas (con diff exacto y autorización) + superficie de doctor |
| [specs/SPEC-B-01](specs/SPEC-B-01-cableado.md) | Spec archivo-por-archivo con tests TDD nombrados |
| [GHERKIN-B.md](GHERKIN-B.md) | **Escenarios para aprobación humana** |
| [VERIFICATION.md](VERIFICATION.md) | DoD, matriz, predicciones falsables, secuencia humana |

## Dentro / fuera

**Dentro**: cableado de 5 claves existentes, declaración + cableado de 4
constantes, sección de conformidad en doctor, tests, docs factuales.

**Fuera**: `crap.profiles` (umbral full-repo por perfil — no existe gate
full-repo que lo consuma; inventarlo es alcance nuevo, va al backlog);
`mutation.*` operativos (max_workers, timeout, differential — pertenecen al PR
de mutación del harness); borrar/deprecar claves huérfanas de policy.yaml
(decisión Horizonte 0 con el inventario del ANALYSIS); `budgets_seconds`.
