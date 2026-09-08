# Investigación — evidencia, oportunidades y límites

> Revalidación posterior en [D0 §1/§5](D0.md) y [trazabilidad](TRAZABILIDAD-D0.md):
> HEAD permanece en la base; #33 falla por integridad del lock antes de gates;
> #12 tiene runner 487 LOC y 30 exenciones totales; beta.2 también es Latest.
> Digest/bytes del SBOM comprobados, procedencia al SHA no acreditada.
> Corrección F03: mypy recibe `tools/wct src`; el package `example` está en
> pyproject. Los hallazgos iniciales siguientes se conservan como antecedente.

Consulta: 2026-09-07. Corte de código: `8de9107184288f1aa72c9578a14913686c47ad7c`.
Métodos: lectura de código/configuración/docs, sondas de introspección sin
escrituras, GitHub API mediante `gh` y fuentes primarias externas. No se hizo
una auditoría exhaustiva de seguridad ni una evaluación de modelos.

Etiquetas: **O** observado directamente; **L** documentado previamente, no
reproducido aquí; **I** inferencia de diseño; **P** propuesta sin medir.
La severidad expresa impacto en la promesa de beta.3, no una CVE.

## Hallazgos del proyecto

| ID / prioridad | Evidencia y hallazgo | Razón, impacto y decisión recomendada |
|---|---|---|
| B3-F01 / P0 | **O** [rules/engine.py](../../../../tools/wct/rules/engine.py), funciones `targets/build`: `rules build` escribe seis destinos de instrucciones, no `.importlinter`. El comentario de [policy.yaml](../../../../governance/policy.yaml) sí dice que genera ese contrato. | Antes de vender moldes hay que cerrar fuente → compilación → consumidor. Tener instrucciones y contratos divergentes hace que el modelo obedezca una arquitectura y el gate mida otra. Diseñar compilación determinista y prueba de cableado; no regenerar hoy archivos protegidos. |
| B3-F02 / P0 | **O** [archmetrics/analyzer.py](../../../../tools/wct/archmetrics/analyzer.py), `analyze`: usa `paths.source[0]`, un `root_package` y el segundo segmento del módulo como capa. [wire/engine.py](../../../../tools/wct/wire/engine.py) busca nombres de capa y fija `domain/application` como objetivos. | Configurar carpetas no equivale a soportar múltiples raíces, paquetes anidados o bounded contexts. El molde necesita mapeo exhaustivo de módulos a roles; un módulo no clasificado no puede desaparecer de la garantía. Es límite de implementación observado, no prueba de que toda adopción falle. |
| B3-F03 / P0 | **O** [runner.py](../../../../tools/wct/gate/runner.py) contiene scopes `src/example`, comando mypy con `example` y G-WIRE para domain/application del ejemplo. [.importlinter](../../../../.importlinter) fija `example`. Otros analizadores sí leen parte de policy. | La adaptación exige inventario de cada consumidor; sustituir un solo `root_package` sería insuficiente. Introducir un plan efectivo de capacidades para el scope seleccionado, sin prometer configurar los 34 gates de golpe. |
| B3-F04 / P0 | **O** [model.py](../../../../tools/wct/model.py): `GateResult` solo contiene gate, status, summary, duración, details y command. [overview.py](../../../../tools/wct/report/overview.py) muestra capacidades del entorno, no evidencia durable de un run. | Reportar un PASS no acredita qué árbol, configuración y artefactos lo produjeron. Reusar GateResult y añadir una envoltura versionada; no crear un segundo motor de veredictos. |
| B3-F05 / P0 | **O** [mutate/verdict.py](../../../../tools/wct/mutate/verdict.py) declara explícitamente `sin causa ni frescura (G1b)`. **L** [investigación local G1b](../G1/INVESTIGACION-G1b.md) conserva cuatro pendientes y resultados a escala pequeña. | No ampliar el claim de mutación por introducir un workspace o un hash. Identidades, frescura, exclusividad y causa deben acreditarse separadamente. No activar mutación de todo tools modificando solo `paths.source`. |
| B3-F06 / P0 | **O** [gate_accept](../../../../tools/wct/gate/checks.py) recorre features y valida parseo/IR. [steps.py](../../../../tests/acceptance/steps.py) ejecuta comportamiento del ejemplo. | Tener Gherkin no prueba automáticamente toda feature. El molde necesita manifiesto de escenarios requeridos → tests recolectados → ruta productiva → resultado, más negativos semánticos. La gramática del issue #35 es distinta de esta carencia de trazabilidad. |
| B3-F07 / P1 | **O** [adopt](../../../../tools/wct/adopt/__init__.py) inventaría extensiones/rutas; [lifecycle](../../../../tools/wct/adopt/lifecycle.py) ya tiene pin de upstream, drift y propuesta de diff. | Reusar el ciclo de vida y añadir mapeo revisable; no reemplazar el codebase por una plantilla. La detección automática es una sugerencia, no certificación de la arquitectura del usuario. |
| B3-F08 / P0 | **O** existen PRDs de evals, no una medición causal encontrada en el alcance revisado; el README declara ese límite. | 30 adversarios rechazados o una suite verde no prueban ahorro ni calidad equivalente a un modelo superior. Medir ambos modelos sobre las mismas tareas con oráculo separado, coste total y todos los fallos. |
| B3-F09 / P1 | **O** [doctor/checks.py](../../../../tools/wct/doctor/checks.py) tiene lista parcial de claves y exige hooks `.claude`; [config.py](../../../../tools/wct/config.py) valida mapa/schema_version, no un schema exhaustivo del futuro molde. | El contrato de molde debe rechazar claves desconocidas/conflictos y distinguir capacidad de control por proveedor. Instrucciones neutrales no acreditan idéntica contención en todos los runtimes. |
| B3-F10 / P1 | **O** [quality.yml](../../../../.github/workflows/quality.yml) ejecuta commit, coverage → ratchets exigibles y property por separado. [full-hardening](../../../../.github/workflows/full-hardening.yml) es manual/programado. | G3a sí cerró un escape concreto; no equivale a paridad absoluta entre todos los tiers. La promesa futura debe enumerar capacidades exigidas por riesgo, evitando equiparar nombre del tier con confianza. |
| B3-F11 / P1 | **O** PR #43 elimina una dependencia de orden y #44 aborda clones por tokens. **O** [baseline file-size](../../../../governance/baselines/file-size.json) vale 0, mientras #12 todavía describe runner con 593 LOC. | Las regresiones y el backlog deben reconciliarse contra el estado real. Mantener pruebas de orden y ruta ensamblada; no volver a planificar una reparación entregada ni cerrar toda #12 por un solo subproblema resuelto. |
| B3-F12 / P0 publicación | **O** GitHub devuelve `isPrerelease: false`, `isDraft: false` para beta.2, aunque su nombre es beta y el PLAN pedía prerelease. | El nombre del tag no configura el canal de GitHub. Solicitar corrección de metadata por separado y verificar el estado remoto en la próxima DoD. No se modificó la release ni se infiere por este dato si está marcada Latest. |

### Sondas reproducidas en este turno

- `git rev-parse 'v1.0.0-beta.2^{commit}'` → `8de9107184288f1aa72c9578a14913686c47ad7c`.
  Es un tag anotado: el objeto tag tiene otro SHA; no confundirlo con el commit.
- Introspección de `rules.targets(Path.cwd())` → CLAUDE.md, AGENTS.md,
  `.cursor/rules/wct.mdc`, `.github/copilot-instructions.md`, GEMINI.md y
  `.windsurf/rules/wct.md`; no incluye `.importlinter`.
- Introspección de TIERS → fast 7, commit 21, pr 27, full 34.
- Introspección de campos de GateResult → los seis listados en F04.
- `gh release view v1.0.0-beta.2 --json isPrerelease,isDraft,assets,url`
  → false/false, asset `sbom-8de9107.json` (189588 bytes). Se observó su
  existencia, no se validó en este turno su contenido ni digest.

## Fuentes externas y transferencia a WCT

Las conclusiones de diseño de este dossier son propuestas propias. Las fuentes
fundamentan mecanismos y límites; ninguna demuestra uplift de WCT beta.3.

| Fuente primaria consultada | Qué aporta / qué no extrapolar | Decisión de uso |
|---|---|---|
| [Cockburn: artículo original de arquitectura hexagonal](https://alistair.cockburn.us/hexagonal-architecture) | Separación interior/exterior, puertos según conversación y adaptadores sustituibles. No prescribe seis carpetas ni convierte estructura en corrección de negocio. | Modelar roles y contratos, no nombres de directorio ni un ranking de arquitecturas. |
| [Import Linter, contratos 2.3](https://import-linter.readthedocs.io/en/v2.3/contract_types.html) | Contratos de dependencias, independencia y exhaustividad por contenedor. Las reglas dentro de un contenedor no bastan para prohibir cruces entre contenedores. | Reutilizar el motor ya instalado antes de crear otro. El lock WCT usa 2.13: la documentación versionada 2.3 orienta el diseño; compatibilidad exacta con 2.13 requiere fixtures. La consulta a la página stable falló, no se asume equivalencia total. |
| [Copier: actualización](https://copier.readthedocs.io/en/stable/updating/) y [configuración/unsafe](https://copier.readthedocs.io/en/latest/configuring/) | Versionar respuestas y detectar conflictos permite evolucionar plantillas. Tasks/migraciones/extensiones pueden ejecutar código. | Aprender del ciclo de vida; no añadir dependencia ni ejecución de plugins de molde por defecto. Preservar personalizaciones y revisión del diff. |
| [EvalPlus, artículo de investigación](https://arxiv.org/abs/2305.01210) | Tests más rigurosos encontraron código incorrecto que pasaba tests originales. Su corpus funcional no representa por sí solo repositorios WCT ni arquitecturas complejas. | Calificar el oráculo con negativos y alternativas válidas; no usar cobertura visible como outcome final. |
| [OpenAI: buenas prácticas de evals](https://developers.openai.com/api/docs/guides/evaluation-best-practices) | Evaluación específica de tarea, registro de ejecuciones y calibración humana de scoring. | Adoptar método, no dependencia del servicio. La página anuncia deprecación de su plataforma Evals: no elegir esa API como cimiento de beta.3. |
| [Inspect: scorers](https://inspect.aisi.org.uk/scoring.html) y [sandboxing](https://inspect.aisi.org.uk/sandboxing.html) | Separación entre ejecución y evaluación, entornos con herramientas aisladas. | Referencia para el plano experimental; escoger un runtime solo tras prueba de compatibilidad. Un directorio separado no es aislamiento de seguridad. |
| [SWE-bench: contrato de tareas/CLI](https://www.swebench.com/SWE-bench/reference/cli/) | Enunciado, test patch, solución y entorno son artefactos distintos de una tarea. | Corpus versionado; no clonar una colección pública y llamarla holdout desconocido. |

### DeepSeek Harness: revisión actualizada, sin dependencia nueva

Commit remoto consultado: `d347e703908d0406b7a7ef80e3a0e594d86b2215`.
El [estudio anterior](../../02-estudio-deepseek-harness.md) estaba anclado a
`4e84901e6471b79ec0338099867ebb4606d12bb5`; se conserva como historia.

- Su [política de testing](https://github.com/deepseek-ai/deepseek-harness/blob/d347e703908d0406b7a7ef80e3a0e594d86b2215/docs/testing.md)
  vuelve a ser útil para beta.3: ejecutar la composición real, comprobar archivos
  y efectos externos, y demostrar que la regresión pone rojo el test. No copiar
  su política de gasto de API: WCT necesita presupuesto autorizado.
- [LLM replay](https://github.com/deepseek-ai/deepseek-harness/blob/d347e703908d0406b7a7ef80e3a0e594d86b2215/packages/test-support/llm-replay/README.md)
  comprueba consumo de una trayectoria grabada y declara límites de asociación
  de sesiones concurrentes. Reusar la idea para integración sin claves; no
  contar replay como nueva muestra de capacidad o ahorro del modelo.
- [SAFETY](https://github.com/deepseek-ai/deepseek-harness/blob/d347e703908d0406b7a7ef80e3a0e594d86b2215/SAFETY.md)
  mantiene el estado experimental/no auditado y advierte que no es una frontera
  de seguridad suficiente. No incorporarlo al core ni usarlo como contención
  única de código generado.

## Qué sigue abierto, frente a qué ya se integró

Estado remoto consultado el 2026-09-07; sin escrituras externas.

| Elemento | Estado | Tratamiento beta.3 |
|---|---|---|
| PRs #37–#44 | En historial de main; G1a, reparación, G3a y beta.2 integrados | Punto de partida, no PRs inconclusas |
| [PR #33](https://github.com/Yosoyepa/write-check-trust/pull/33) | Única PR abierta consultada; modifica uv.lock; commit-gates FAILURE | Revisión propia de dependencias y causa de CI; no asumir que basta bless ni mezclar con moldes |
| [Issue #35](https://github.com/Yosoyepa/write-check-trust/issues/35) | Abierto, narrativa Gherkin | Decidir subconjunto/gramática; no confundir con ejecutar todos los escenarios |
| [Issue #12](https://github.com/Yosoyepa/write-check-trust/issues/12) | Abierto, descripción parcialmente desactualizada | Reconciliar tamaño/exenciones con medición actual; conservar deuda restante |
| G1b | Propuesta e investigación local, implementación no acreditada | Resolver identidades/frescura/concurrencia/symlinks/source_paths y presupuesto antes de ampliar claim |
| Report V2 / O-001, O-006 | Propuestos; capacidades y SKIP ya aportan parte | Rebanada mínima de evidencia para capacidades beta.3, no reconstrucción completa |
| O-007–O-011, PRD-003 | Diseño previo disponible, beneficio causal no acreditado | Reusar y ejecutar piloto cuando haya autorización y oráculos calificados |
| Dedup de plantillas | Baseline versionado 17; no se midió conteo actual aquí | No es el mismo concepto que moldes arquitectónicos. Priorizar por deuda/impacto, no por cuota |
| Polyglot / composición libre | Aspiración, no soporte demostrado | Dejar fuera de beta.3; contratos por lenguaje antes de anunciar equivalencia |

Los nuevos IDs B3 son identificadores de planificación, **no issues de GitHub**.
Owner propuesto del triage: `yosoyepa`, pendiente aceptación. Antes de diferir
trabajo en código deben asignarse owner y issue reales según PROC-009; este
turno no crea números ficticios ni abre tickets.
