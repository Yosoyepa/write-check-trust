> **Entrada vigente tras R1 de P01:** [integración y próximas puertas](SELF-HOSTING/INTEGRACION-P01.md).
> El proceso del siguiente encargo usa [entrega v2](SELF-HOSTING/ENTREGA-v2.md)
> y [molde local v2](SELF-HOSTING/MOLDE-WCT-v2.md). Los estados y prompts que
> siguen son antecedentes fechados, no autorización para repetir P01 ni ejecutar
> piezas futuras. Esta incorporación documental no publica beta.3.

# Beta.3 — Moldes verificables y economía de código correcto

> **Encargo vigente: [automejora ciega de WCT](SELF-HOSTING/README.md).**
> WCT es ahora el primer sujeto; el usuario custodiará el modelo secreto y
> aportará datos OpenRouter después de puntuar calidad. El siguiente encargo
> concreto es [SH-P01](SELF-HOSTING/P01-IDENTIDADES.md), con
> [prompt del coder](SELF-HOSTING/PROMPT-CODER.md). La dirección está solicitada;
> el contrato/diff de implementación aún requiere su aprobación. No se
> presupone gasto, implementación ni resultados positivos.

> Revisión D0 del 2026-09-07: [propuesta de decisiones](D0.md),
> [cadena campo→consumidor→test→evidencia](TRAZABILIDAD-D0.md),
> [contrato exacto B3-P1](specs/SPEC-B3-P1-evidencia.md),
> [Gherkin/matriz de P1](GHERKIN-P1.md),
> [piloto con personalAssistant y oráculo por Codex](PILOTO-PREPARACION.md),
> [verificación de este turno](VERIFICACION-D0.md).
> El texto original siguiente se conserva. Su verificación corresponde a la
> entrega documental anterior; no es evidencia de implementar P1. Las adendas
> de D0 precisan el recorte del primer incremento sin darlo por aprobado.

Fecha: 2026-09-07. Estado: **propuesta para decisión humana; no implementación aprobada**.
Base inspeccionada: `8de9107184288f1aa72c9578a14913686c47ad7c`, commit al que
resuelve el tag anotado `v1.0.0-beta.2`. No se ejecutaron inferencias de pago.

## Dirección recomendada

Evolucionar WCT desde una plantilla con gates hacia **contratos de proyecto
verificables, acompañados de evidencia y evaluaciones de coste/calidad**.
Empezar con un molde hexagonal Python; conservar el comportamiento de los
adoptadores beta.2 mediante una traducción de compatibilidad explícita.
No construir todavía un catálogo de diez arquitecturas ni un agente universal.

La hipótesis de producto es que reducir decisiones ambiguas, ofrecer contexto
comprobado y dar feedback ejecutable puede permitir usar modelos económicos
con menos errores y reparaciones. **La hipótesis aún no está demostrada en WCT.**

## Aterrizaje de la analogía de fábrica

| Fábrica | WCT propuesto | Qué sigue sin garantizar |
|---|---|---|
| Plano de la pieza | requisitos y criterios de aceptación aprobados | que el requisito represente bien la necesidad |
| Molde y tolerancias | roles, dependencias, interfaces, reglas y límites | corrección universal del programa |
| Materia prima/proceso | modelo, contexto, herramientas y reparaciones | que toda capacidad sirva para toda tarea |
| Medición de la pieza | tipos, imports, tests de contrato y comportamiento | ausencia de defectos no observados |
| Prueba de ensamblaje | ruta real CLI/API → aplicación → adaptador | funcionamiento de todo entorno externo |
| Lote y trazabilidad | árbol, configuración, herramientas y evidencia del run | autenticidad si todo lo controla el mismo agente |

Un zapato puede tener la forma correcta y romperse al caminar. Del mismo modo,
un adaptador puede satisfacer un `Protocol` y calcular mal el saldo. El molde
verifica **conformidad**, los contratos verifican **compatibilidad observable**,
y el oráculo independiente evalúa **comportamiento**. No son sinónimos.

## Alcance objetivo y recorte

1. Evidencia mínima válida de las capacidades que beta.3 afirmará verificar.
2. Un molde `hexagonal-python` de contratos, no un generador de negocio.
3. Mapeo de un codebase existente sin imponer nombres de carpetas ni mover código.
4. Paquete de contexto y diagnósticos acotados para el agente, sin cambiar sus permisos.
5. Piloto emparejado de modelos: éxito independiente, escapes y coste por éxito.

G1b se mantiene como dependencia de **claims de mutación fresca/completa**, no
se declara terminado por este dossier. Su investigación pendiente tiene un
carril propio. Si no se cierra, beta.3 no anunciará mutación acreditada ni
aceptación automática sustentada en ella. El piloto puede medir un tratamiento
limitado si sus capacidades y limitaciones se congelan antes de las corridas.

## Lectura y decisiones

| Documento | Para qué sirve |
|---|---|
| [Investigación y hallazgos](RESEARCH.md) | evidencia del repo, fuentes primarias, oportunidades y pendientes reales |
| [PRD](PRD.md) | problemas, features, prioridad, no objetivos y resultados esperados |
| [ADR-01](decisions/ADR-B3-01-moldes.md) | molde como contrato y composición controlada |
| [ADR-02](decisions/ADR-B3-02-confianza.md) | evidencia y frontera de confianza |
| [ADR-03](decisions/ADR-B3-03-evaluacion.md) | evaluación neutral y coste total |
| [ADR-04](decisions/ADR-B3-04-adopcion.md) | compatibilidad, migración y elección de herramientas |
| [Especificación de moldes](specs/SPEC-B3-01-moldes.md) | roles, mapeo, composición, invariantes y casos adversariales |
| [Especificación de evidencia/contexto](specs/SPEC-B3-02-evidencia-contexto.md) | contratos del run, rechazo de evidencia inválida y feedback |
| [Plan de evals](EVALS.md) | brazos, corpus, costes, estadística y criterios de claim |
| [Gherkin propuesto](GHERKIN.md) | escenarios para aprobación, todavía no features ejecutables |
| [Plan por incrementos](PLAN.md) | dependencias, presupuestos, puertas y salida beta.3 |
| [Prompt de continuación](PROMPT.md) | encargo acotado para iniciar decisiones sin implementar |

Recomendación de la primera puerta: aprobar **la dirección y el diseño del
molde mínimo**, no todos los cambios protegidos, el gasto experimental ni una
publicación. El primer incremento técnico se especificará con su diff y
Gherkin propios antes de autorizar código.

## Continuidad, no otro portafolio paralelo

Este plan recorta y extiende [el portafolio O-001–O-018](../../04-portafolio-de-oportunidades.md),
[PRD-002](../../prd/PRD-002-calificacion-de-gates.md),
[PRD-003](../../prd/PRD-003-benchmark-modelo-economico.md) y
[SPEC-001–004](../../specs/SPEC-001-contratos-experimentales.md).
No cambia retroactivamente esos contratos ni da por implementadas sus propuestas.
La novedad es el molde ejecutable y su ablación experimental, no renombrar todo
el backlog como beta.3.

## Límites de esta entrega

Solo documentación en este directorio. Sin cambios a código, configuración,
baselines, herramientas, workflows, tests ejecutables o releases. Los ADRs son
recomendaciones razonadas, no constancias de aprobación humana.
Las observaciones sobre documentos locales G1b/POST-PR36 incluyen trabajo
sin commitear del usuario: se citan como antecedentes locales, no como entrega
publicada en beta.2.

## Verificación documental de esta entrega

- 13 documentos y 55 enlaces locales comprobados; sin enlaces locales rotos.
- Fences/espacios y columnas/parámetros de las tablas Gherkin comprobados. No
  equivale a parsear las features con el pipeline ni a ejecutar aceptación.
- `uv run wct gate --tier fast`: 7 PASS, 0 SKIP, 0 FAIL/ERROR.
- `uv run wct integrity check`: exit 0; `git diff --check`: sin errores.
- Sin diff en código, tests, governance, workflows, pyproject, uv.lock o README
  raíz. Los diffs tracked previos del usuario se conservaron idénticos.
- No se corrieron suite completa, full-hardening, mutación ni benchmark de
  modelos; esos resultados no son parte de la evidencia de este dossier.
- Rama documental: `codex/plan-beta3-moldes-evals`, sin commits/push nuevos.
