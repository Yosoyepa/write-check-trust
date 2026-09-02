# ADR-A1-02 — Veredicto no vacío para aceptación por mutación

Estado: propuesto (se ejecuta al aprobarse GHERKIN-A1.md).
Contexto: [ANALYSIS.md §1.2](../ANALYSIS.md) · [RESEARCH.md R3](../RESEARCH.md).

## Contexto

El veredicto de `wct accept mutate` es exclusivamente
`bool(report["survived"])` (`tools/wct/cli.py:311-313`). Las mutaciones se
derivan solo de `scenario.get("examples", [])` (`accept/pipeline.py:172-194`):
cero Examples → cero mutantes ejecutadas → `0 == 0` → PASS silencioso. Un
escenario sin parametrización —exactamente lo que TEST-010 prohíbe— es
recompensado con un verde sin verificación.

## Decisión

**Semántica en dos niveles:**

1. **FAIL agregado**: si en toda la corrida `killed + survived == 0`
   (equivalente: `not report["results"]` — el coder usa la estructura real de
   `run_mutations` y lo justifica en el test), el veredicto es fallo con
   mensaje accionable que cita TEST-010: «0 mutaciones ejecutadas: el
   escenario no parametriza campos variables; agrega Examples (TEST-010)».
2. **WARN por escenario**: el reporte lista los escenarios sin Examples como
   advertencia de vacuidad, sin bloquear por sí solos.

El check vive junto al cálculo del veredicto (CLI/pipeline, donde existen los
conteos), no en `accept parse` (el parser no puede saber si unos Examples
generan mutaciones *válidas*; solo el run lo sabe).

**Condición previa obligatoria del PR (paso 0 del spec)**: enumerar los
escenarios del manifiesto de aceptación actual y su conteo de Examples; los
vacíos se parametrizan en el mismo PR (features/ es ruta libre). El PR no
puede dejar escenarios del corpus en estado de fail agregado recién creado.

## Alternativas consideradas

- **(a) Solo WARN, sin fail**: rechazada. Un warning no es gate: reproduce el
  defecto actual con mejor tipografía. El roadmap (O-004) exige «aceptación
  no puede pasar con cero trabajo aplicable».
- **(b) FAIL por escenario individual (no solo agregado)**: diferida a O-004.
  Endurece cada escenario sin Examples; puede exigir re-parametrizar corpus
  completo (incluye el generado). Es análisis de corpus, no semántica de
  veredicto — no cabe en A1 sin inflarlo. El WARN por escenario prepara ese
  endurecimiento dejando el censo visible desde ya.
- **(c) Umbral mínimo configurable (`min_mutations: N` en thresholds.yaml)**:
  diferida. N=1 es el mínimo falsable y no necesita configuración; añadir la
  clave es edición de governance (SEC-005) que este PR evita. Si la práctica
  pide N mayor, se propone con su propio mini-ADR.
- **(d) Check en `accept parse` (tiempo de parseo)**: rechazada como sede
  única — parse no distingue "sin Examples" de "Examples que no generan
  mutantes válidas"; el veredicto sí. (Un aviso de parse es aceptable como
  complemento si ya existe infraestructura de warnings ahí; no se añade
  infraestructura nueva para eso.)

## Consecuencias

- Features futuros sin parametrización fallan en CI en vez de pasar vacíos:
  el falso verde desaparece.
- El censo de vacuidad del corpus actual queda documentado en el PR (paso 0)
  — evidencia para O-004.
- Superficie mínima: veredicto + reporte; el motor de mutación no se toca.
- G-ACCEPT-MUT sigue siendo `optional=True` (SKIP si falta binario): esa
  superficie es de O-006/perfiles, no de este ADR; se deja constancia de la
  interacción (SKIP sigue pudiendo ocultar el nuevo fail — otra razón para
  que ADR-A1-03 haga visible el conteo).
