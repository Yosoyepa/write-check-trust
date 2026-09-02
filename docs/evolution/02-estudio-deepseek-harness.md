# Estudio de DeepSeek Harness

## Veredicto

DeepSeek Harness puede aportar patrones valiosos para ejecutar y reproducir
experimentos con agentes, pero no es en sí mismo el benchmark que WCT necesita.
Su aporte está en el **sustrato experimental**: sesiones durables, ejecución
programática, medición de tokens, replay, servidores mock a nivel de protocolo y
tests de ruta ensamblada.

La recomendación es aprender de esos patrones y, si una prueba de concepto
posterior lo justifica, integrarlo detrás de un adaptador opcional del plano de
evaluación. No debe convertirse en dependencia del core de WCT ni en el único
runtime admitido.

## Alcance investigado

La revisión se ancló al commit
`4e84901e6471b79ec0338099867ebb4606d12bb5`. El proyecto se presenta como
developer preview/alpha, con arquitectura extensible por plugins. Su archivo de
benchmark explica cómo lanzar sesiones aisladas mediante el SDK, pero no aporta
un corpus curado, oráculos independientes, protocolo estadístico ni scorer de
uplift. Por ello hay que distinguir:

- **runner/harness:** ejecuta un agente y conserva su trayectoria;
- **benchmark:** define tareas, controles, oráculos, splits y métricas;
- **evaluación causal:** atribuye diferencias a WCT y cuantifica incertidumbre.

DeepSeek contribuye sobre todo al primer punto. WCT debe diseñar los otros dos.

## Capacidades reutilizables como ideas

### 1. SDK programático y aislamiento explícito

El [Python SDK](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/python/sdk/README.md)
permite fijar provider, modelo, reasoning, tokens máximos, workspace, home del
harness, perfiles y patches. El resultado expone respuesta final, razón de
terminación, eventos y notificaciones.

**Aplicación a WCT:** cada ejecución experimental debe recibir un workspace,
home y session id propios. El tratamiento WCT debe expresarse como configuración
versionada, no como estado residual de una corrida anterior.

**Valor:** reduce contaminación cruzada, hace posible comparar brazos y captura
terminaciones que no son simplemente “el agente dijo que acabó”.

### 2. Event log append-only

Las sesiones conservan eventos de turnos, pasos, requests, herramientas,
fragmentos y uso. Un log append-only permite reconstruir cuándo falló un gate,
qué diagnóstico vio el agente y cuántas reparaciones necesitó.

**Aplicación a WCT:** modelar el uplift como trayectoria, no solo como snapshot
final. Dos brazos pueden terminar verdes, pero uno haber usado cuatro veces más
tokens, omitido un error o intentado alterar la gobernanza.

### 3. Medidor de tokens con semántica explícita

El [Token Meter](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/packages/llm/token-meter/README.md)
distingue input no cacheado, output, cache read/write, reasoning y presión de
contexto cuando el provider ofrece esos datos; también documenta cuándo estima.

**Aplicación a WCT:** almacenar valores facturados y estimados por separado. El
costo de gates —CPU y tiempo— también debe entrar al costo total. Comparar solo
tokens visibles puede favorecer de manera artificial a un provider con caché o
reasoning no reportado.

### 4. Session snapshots cerrados y normalizados

[Session Snapshot](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/packages/test-support/session-snapshot/README.md)
congela manifiesto, sesión normalizada y árbol esperado del workspace, con modos
de record, replay y refresh. Normaliza identificadores y paths inestables.

**Aplicación a WCT:** una ejecución de referencia puede convertirse en fixture
reproducible sin claves. Debe cerrarse sobre todos los artefactos relevantes y
fallar si aparecen archivos inesperados, no solo si falta un archivo esperado.

### 5. Replay de LLM sin claves

[LLM Replay](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/packages/test-support/llm-replay/README.md)
reproduce respuestas grabadas, exige consumo completo y puede guionar throw,
hang o retry.

**Aplicación a WCT:** separar dos preguntas:

- ¿la integración responde de forma determinista ante la misma trayectoria?
- ¿un modelo nuevo produce mejores trayectorias?

La primera puede verificarse con replay; la segunda exige API real y repeticiones.
No debe reportarse replay como evaluación de inteligencia del modelo.

### 6. Mock en la frontera real del protocolo

El [LLM Mock Server](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/packages/test-support/llm-mock-server/README.md)
simula HTTP/SSE, chunks malformados, stalls, rate limits, errores de servidor,
tool calls y stress determinista por seed.

**Aplicación a WCT:** probar que una interrupción del modelo o del stream no
produce evidencia truncada marcada como válida, que los retries se contabilizan
y que los presupuestos no se reinician accidentalmente.

### 7. Política: falsear el mundo, no el producto

La [política de testing](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/docs/testing.md)
recomienda mockear la frontera no determinista y mantener real el código aguas
abajo, además de incluir smokes por la ruta de entrada real.

**Aplicación a WCT:** sustituir los reconocedores paralelos del red team por
repositorios fixture que ejecuten `wct gate` real. El fixture es el mundo falso;
el runner, parser, configuración y gate son producto real.

### 8. Postmortems convertidos en guardrails

El [postmortem 0001](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/docs/postmortem/0001-acp-default-export-drops-inject.md)
documenta que 178 tests verdes y 100 % de cobertura de línea no cubrieron la ruta
ensamblada real. El remedio fue un smoke sin claves por el entrypoint productivo.

El [postmortem 0002](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/docs/postmortem/0002-js-expression-disabled-filesystem-tools.md)
muestra el riesgo inverso: refrescar un snapshot hizo determinista una regresión
`UNKNOWN_TOOL`, pero no la hizo correcta. La corrección necesitó invariantes
semánticos independientes del golden.

**Aplicación a WCT:** cada escape real debe producir:

1. postmortem breve y causal;
2. fixture que recorra la ruta real;
3. invariante semántico que no se reescriba al refrescar el snapshot;
4. clasificación del safeguard que falló;
5. entrada en el corpus de regresión y en la medición de escapes.

### 9. Verificaciones de ownership e invariantes del paquete

El repositorio incluye checks dedicados a ownership de configuración,
invariantes de paquetes y licencias. El valor no está en copiar nombres o stack,
sino en la idea de verificar que cada fuente generada tenga un dueño y que los
catálogos no diverjan.

**Aplicación a WCT:** meta-gate de configuración que detecte claves sin
consumidor, umbrales hardcoded que sombrean configuración y aliases contabilizados
como capacidades independientes. Para licencias, separar SBOM de decisión de
compatibilidad.

### 10. Perfiles y patches como tratamientos experimentales

La composición por perfiles y patches permite expresar variantes sin duplicar
todo el runtime.

**Aplicación a WCT:** representar los brazos “sin WCT”, “solo reglas”, “solo
gates” y “WCT completo” como tratamientos declarativos con digest. Esto evita
editar el repo de la tarea entre brazos y reduce diferencias accidentales.

## Mapa de adopción conceptual

| Patrón DeepSeek | Problema WCT | Adaptación propuesta | Prioridad |
|---|---|---|---|
| SDK programático | ejecución manual y difícil de comparar | interfaz de runner neutral y un adaptador | P1 |
| workspaces/homes aislados | contaminación entre corridas | sandbox por run y teardown verificable | P1 |
| event log durable | solo snapshot final | ledger de trayectoria append-only | P1 |
| token meter | costo incompleto | tokens facturados/estimados y costo total | P1 |
| session snapshot | irreproducibilidad | fixture cerrado y normalizado | P1 |
| LLM replay | tests dependientes de API | replay keyless para integración | P1 |
| mock HTTP/SSE | fallos de protocolo no cubiertos | fault injection determinista | P2 |
| testing por ruta real | red team paralelo | gate qualification end-to-end | P0 |
| invariantes sobre snapshots | goldens que legitiman regresiones | scorer semántico independiente | P0 |
| package/license checks | config drift y SBOM parcial | meta-gate de wiring/licencias | P0/P1 |
| postmortems | escapes sin memoria institucional | bucle escape → fixture → métrica | P2 |

## Qué no conviene adoptar

### No copiar toda la arquitectura de plugins

WCT es un harness de calidad con un core relativamente acotado. Reproducir la
arquitectura completa, el contenedor de plugins o el stack TypeScript aumentaría
dependencias y superficie de fallo antes de demostrar necesidad. Contradiría la
escalera minimalista del propio proyecto.

### No usar snapshots como oráculo de calidad

Un snapshot responde “¿cambió?”; un oráculo semántico responde “¿sigue siendo
correcto?”. Refrescar un expected output no puede ser la única vía para resolver
un fallo. Toda snapshot relevante necesita invariantes que sobrevivan al refresh.

### No presentar DeepSeek Harness como sandbox de seguridad suficiente

El propio proyecto declara límites y estado no auditado en
[SAFETY.md](https://github.com/deepseek-ai/deepseek-harness/blob/4e84901e6471b79ec0338099867ebb4606d12bb5/SAFETY.md).
Una evaluación adversarial de WCT debe ejecutar en una frontera de aislamiento
definida por la infraestructura del laboratorio, no confiar solo en el runtime
del agente.

### No acoplar el benchmark a un único proveedor o modelo

La pregunta de WCT es provider-neutral. Los contratos de tarea, ejecución,
scoring y evidencia deben sobrevivir a un cambio de runner. DeepSeek sería un
adaptador, no el dominio del laboratorio.

### No asumir estabilidad de una dependencia alpha

Si una fase posterior aprueba una prueba de concepto, debe fijar versión y commit,
aislar su actualización y medir breaking changes. Este dossier no recomienda
añadir la dependencia ahora.

## Alternativas comparadas

| Alternativa | Ventaja | Limitación | Uso recomendado |
|---|---|---|---|
| runner propio mínimo | control y cero acoplamiento | recrea sesiones, streaming y telemetría | contrato inicial o fallback |
| DeepSeek Harness | SDK, replay, snapshots y token meter integrados | alpha, superficie amplia, no es benchmark | adaptador experimental opcional |
| Inspect AI | composición madura de dataset/agent/tools/scorer/logs | otra dependencia y modelo conceptual | referencia o adaptador futuro |
| Harbor/Terminal-Bench | task contract y ejecución repetible | orientado a terminal; no modela WCT directamente | corpus externo y lecciones de calificación |
| integración directa por provider | rápido para un piloto | telemetría y semántica distintas por vendor | smoke inicial, no arquitectura final |

## Prueba de concepto recomendada — si se aprueba después

La PoC debería responder una sola pregunta: “¿puede un adaptador DeepSeek
producir el contrato neutral de ejecución y replay sin filtrar tipos del runtime
al dominio del laboratorio?”.

Alcance máximo propuesto:

- una tarea pequeña y un modelo;
- dos tratamientos: control y WCT completo;
- workspace y home aislados;
- captura de eventos y tokens;
- un replay sin API;
- un oráculo oculto externo al snapshot;
- comparación contra un runner mínimo de referencia;
- sin incorporar plugins propios ni modificar el core de gates.

La PoC se rechaza si exige tipos DeepSeek en contratos de dominio, no puede
producir costos comparables, no puede cerrar el árbol de artefactos o vuelve
imposible reproducir la tarea sin el servicio externo.

La decisión formal se documenta en
[ADR-007](decisions/ADR-007-deepseek-adaptador-opcional.md).
