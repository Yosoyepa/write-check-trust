# Preparación del piloto — corpus, oráculo y presupuesto sin inferencia

> Cambio de orden solicitado después de D0: comenzar por
> [WCT sobre WCT con modelo ciego](SELF-HOSTING/README.md). personalAssistant
> queda como validación externa posterior. El modelo/precio no se revelarán
> al arquitecto antes de puntuar; el custodio guarda recibos OpenRouter.
> Este piloto externo sigue siendo una propuesta distinta, no trabajo ya iniciado.

Estado: **selección propuesta; sin runs de modelos ni APIs de inferencia**.
Complementa EVALS.md, conserva A0/A3/B3/A4 y no fija margen de no inferioridad.

## 1. Repo brownfield elegido por el usuario

El usuario eligió su proyecto personalAssistant (o, si no encaja, otro repo
público de Yosoyepa) y **Codex para crear/revisar el oráculo**. Nombre remoto
verificado: [Yosoyepa/personalAssistant](https://github.com/Yosoyepa/personalAssistant).
Esta autorización permite preparar la selección; no autoriza gastar en modelos,
operar servicios ni modificar ese repositorio.

Snapshot candidato: `c1beefe5118ed5cb87a5f3545490aa2360831426` en main, consultado
2026-09-07. Lectura remota de árbol no truncado, pyproject, policy, ADR-003,
contratos de recordatorios y pruebas existentes. No se clonó/ejecutó el proyecto
ni sus integraciones. La lectura basta para candidatura, no para calificarlo.

| Criterio | Observación | Consecuencia para el freeze |
|---|---|---|
| Raíz/paquete | `src` / `personal_assistant`; setuptools incluye `personal_assistant*`; 201 `.py` bajo src, 88 bajo tests | Encaja físicamente; inventario de módulos/disposición todavía debe revisarse por completo |
| Dominio y puertos | `domain`, `application/ports`, `application/use_cases`; ReminderUnitOfWork tiene contrato de rollback explícito | Buenos candidatos de comportamiento sin necesitar LLM real |
| Layout | `infrastructure` contiene composición y HTTP; `contracts` contiene interoperabilidad; `evals` está dentro del paquete | No mapear por nombres. Clasificar módulos de infraestructura individualmente y separar evals por capacidad, sin ocultarlos |
| Contrato distinto | ADR-003 permite Pydantic en dominio; policy local lo refleja | Conflicto con la prohibición del template estricto. Empezar shadow/compatibilidad, publicar discrepancia y decidir perfil antes de enforcement; no cambiar requisitos para favorecer B3 |
| WCT adoptado | Usa harness con adaptación propia; pyproject dice 0.2.0-alpha.4 y commit integra WCT 0.3.0/0.4.0 | No llamar a su harness actual «A3 beta.2». Preparar overlay beta.2 fijado, adaptado y revisado antes de comparar |
| Dependencias/IO | LLM, WhatsApp/Telegram, PostgreSQL y otros adaptadores en el repo | Recortar tareas a operaciones deterministas en memoria y parser; cero credenciales/servicios reales. No basta omitir tests que fallen: declarar capacidad fuera de alcance |
| Licencia/procedencia | GitHub `licenseInfo=null`; no archivo LICENSE en árbol consultado | El propietario autorizó selección/uso del repo, pero falta decidir redistribución del corpus/fixtures de terceros. No asumir licencia abierta por ser público |

Mapeo **tentativo**, no resultado de conformidad: domain→domain;
application.ports→ports; resto de application→application; adapters.inbound→
adapters.in; adapters.outbound/persistence→adapters.out; composition se determina
por contenido de infrastructure. `contracts`, DTOs importados por adaptadores,
observability, evals y contenedores requieren clasificación explícita. No se
aprueba el paquete completo porque unas carpetas parezcan hexagonales.

La variante estricta de seis roles prohíbe ciertos imports que el ADR local
admite (p. ej. adaptador de salida→DTO de aplicación). Si se confirman, se
reportan como **incompatibilidad de contrato**, no como bug del repo. D2 debe
elegir: perfil de compatibilidad/shadow con claims limitados, o contrato nuevo
versionado y calificado en ambos brazos WCT. Recomendación: shadow para medir
adopción y scope de enforcement explícitamente compatible para tareas. No
relajar globalmente el molde ni reescribir personalAssistant en el piloto.

Si la clasificación demuestra que ese scope no puede sostener las obligaciones
de tareas, se detiene su entrada al piloto; elegir otro repo de la lista pública
ya autorizada es preferible a hacerlo pasar artificialmente. No hace falta
sustituto ahora: personalAssistant sigue siendo el candidato principal.

## 2. Corpus de 12 tareas preparado para revisión

Tres **codebases**, no tres repos reales independientes: fixtures A/B del molde
y personalAssistant. A/B se crean/califican en P2/P4, no en este turno. Sus
familias relacionadas se etiquetan; renombrar el mismo problema no crea dos
muestras independientes. Los snapshots y enunciados finales se congelan en D2.

| ID propuesto | Codebase | Clase / petición por especificar | Oráculo independiente requerido |
|---|---|---|---|
| T01 | A / shop | Feature: reserva parcial positiva y estado persistido | Resultado/lectura posterior y producto no modificado |
| T02 | A / shop | Feature: error por stock insuficiente preserva estado | Error público aprobado y snapshot antes/después |
| T03 | A / shop | Puerto: guardar/recuperar con adaptador local alternativo | Misma suite de contrato, persistencia tras reapertura |
| T04 | A / shop | Refactor: mover caso de uso preservando API pública | CLI y contratos de imports; alternativa válida sin estructura rígida |
| T05 | B / commerce | Feature: nueva operación determinista distinta de T01/T02 | Requisitos y casos de frontera propios, sin copiar familia de A |
| T06 | B / commerce | Integración: firma de puerto plausible pero incorrecta | Tipo + ejecución y efectos, no solo mypy |
| T07 | B / commerce | Integración: dependencia/símbolo inexistente en adaptador | Símbolos del snapshot y llamada local ensamblada |
| T08 | B / commerce | Refactor: sustituir composición manteniendo comportamiento | Entrada real usa implementación esperada; contrato válido alternativo |
| T09 | personalAssistant | Regresión curada: caso temporal de `extract_reminder` con reloj/zona fijados | Instante/ambigüedad/error aprobados; sin consulta LLM ni hora del sistema |
| T10 | personalAssistant | Regresión curada: salida sin commit conserva snapshot en InMemoryReminderTransaction | Estados observables iguales tras salida; prueba independiente de las llamadas mock |
| T11 | personalAssistant | Brownfield: refactor local de normalización de identidad sin cambiar claves | Equivalencia de claves/versiones y errores de inputs, varias implementaciones aceptables |
| T12 | personalAssistant | Brownfield: cambio local de cableado de ReminderUnitOfWork sin introducir deuda de imports | Ruta real en memoria y rollback explícito, comparación de aristas legacy por identidad |

No se afirma que T09–T12 sean bugs abiertos del proyecto. Son candidatos de
ejercicio; los tests actuales ya cubren varias propiedades. Antes de aprobar
una tarea se decide si usar un cambio nuevo solicitado o una regresión
deliberada en snapshot de evaluación etiquetado, sin alterar upstream. Sus
soluciones públicas no se usan como holdout desconocido. Auth, pagos, cambios
de permisos, servicios reales y transacciones PostgreSQL quedan fuera de este
piloto. Los fixtures semánticos de P4 no son muestras del modelo por sí solos.

Dos tareas **adicionales** de desarrollo sirven al preflight A3/B3 (4 runs).
No pueden ser T01–T12 ni entrar después al confirmatorio. Las 12×4×3=144
corridas del piloto son exploratorias, con dependencia por familia y repo.

## 3. Oráculo por Codex, con separación observable

Asignación aceptada del usuario: Codex lo crea y lo revisa. Propuesta operativa:

1. Sesión Codex de autor recibe requisitos aprobados y snapshot; produce rubric,
   tests y negativos fuera del workspace del agente que resolverá tareas.
2. Otra sesión Codex revisa a ciegas las soluciones válidas/defectuosas y busca
   especificación insuficiente/tests estrechos. No hereda la conversación de
   solución ni genera expected desde resultados del molde. Desacuerdos se elevan
   a `yosoyepa`, quien aprueba el contrato y su freeze.
3. El scoring primario es **ejecutable y determinista** después del patch
   congelado; no un «parece correcto» emitido por Codex. Codex revisa criterios
   humanos con patch anonimizado, sin modelo/brazo/precio.
4. Registro de autor/revisor/snapshot/hashes/accesos; cinco ejecuciones limpias
   de referencia + alternativa válida y negativos por requisito. No ejecutar
   esas calificaciones en el repo productivo ni exponer resultados ocultos al
   agente durante reparación.

Dos sesiones del mismo sistema no son independencia de proveedor ni eliminan
errores correlacionados de Codex. Se declara esa limitación, especialmente si
Codex también produce patches en un brazo. No sustituye revisión externa para
claims confirmatorios; el humano adjudica desacuerdos. No se crearon estas
sesiones ni se consumió una API para construir el oráculo en este turno.

Custodia: usuario/controlador del experimento conserva oracle y freeze fuera
de permisos del agente. Antes de inferencia comprobar mediante probes sin
claves que el agente no puede leer el oracle y que el código del patch tampoco
puede sustituir pytest/scorer, inventarios o runner al evaluar. No secretos,
socket Docker, datos reales ni red durante scoring. Error del oráculo es no
evaluable conservado, nunca éxito ni feedback para elegir el mejor patch.

## 4. Brazos y comparabilidad antes de correr

A0: modelo económico + requisitos y checks neutrales. A3: **el mismo** modelo
económico + beta.2 fijada y adaptada al repo. B3: mismo modelo + beta.3 limitada
con capacidades aprobadas. A4: modelo de referencia + baseline neutral A0.
Overlay versionado separado de snapshot de negocio. Todos reciben requisitos
arquitectónicos/funcionales idénticos; mismos servicios locales y oportunidades
de reparación. La adaptación de A3 a personalAssistant debe pasar su preflight;
no comparar con un A3 roto por `example`, tests/unit o ausencia de herramientas.

Fijar mutación reportada/limitaciones por brazo según D0; no nuevo claim G1b.
B3−A3 mide el paquete completo; B3−A4 no compara contra un modelo de referencia
optimizado con B3. Ablaciones y A5 quedan para otro diseño, no inferencias del
piloto. Cache/home/historial de soluciones no se comparten entre runs.

Aleatorización bloqueada por tarea y alternancia de ventanas; registrar semilla
de asignación. Tres repeticiones no son tres tareas independientes. Resultado
por tarea/familia/repo, intervalos descriptivos, sensibilidad con/sin cada
codebase. Bootstrap emparejado respeta familias relacionadas; con tan pocos
clusters no afirmar precisión poblacional. Las 12 tareas no prueban no inferioridad.

## 5. Presupuesto concreto para completar en D2

**No autorizado todavía.** Propuesta de límites iguales por run: 20 minutos de
agente, 20 llamadas de inferencia, 120000 tokens de entrada agregados y 16000
de salida facturable agregados (incluye razonamiento cuando corresponda), una
propuesta + hasta dos reparaciones visibles. Registrar tokens no comparables
entre tokenizadores, cache y accounting desconocido; no escoger el mejor patch
usando el holdout. Si el runtime no permite observar/enforzar un límite, no
iniciar hasta reemplazarlo por uno observable aprobado.

- 144 runs piloto + 4 preflight = 148 asignaciones. Preflight son 4 runs
  económicos; piloto: 108 económicos y 36 de referencia.
- Reintento de infraestructura: máximo uno por asignación y **8 adicionales
  globales**, solo incidente externo clasificado antes de ver calidad. Fallo
  de tests, mala solución y presupuesto agotado no reciben retry extra.
- Máximo contable: **156 intentos**; cada original/retry conserva costo, motivo
  y vínculo. Stop cuando no queda presupuesto para reservar el techo completo
  del siguiente intento. No reset de counters ni compras automáticas.
- Compute propuesto: hasta 2 vCPU/4 GiB por run, 5 minutos de oráculo adicional,
  concurrencia inicial 1 en preflight y hasta 2 en piloto. Máximo teórico de
  scoring+agente: 65 horas máquina / 130 vCPU-h, no estimación de uso real.
- Revisión humana presupuestada por separado, hasta 10 min/run (26 h máximo),
  más preparación/adopción y autoría/revisión Codex del oráculo, cuyos topes
  y costo deben figurar explícitos en la autorización.

Hoja de aprobación pendiente:

| Concepto | Valor a congelar antes de gastar |
|---|---|
| Económico / referencia / Codex autor-revisor | IDs exactos, snapshots, proveedor/runtime y parámetros; «Codex» solo designa rol/herramienta, no una tarifa/modelo aprobado |
| Tarifas | Moneda, fecha, URL oficial, entrada/salida/razonamiento/cache y herramientas. No cotizadas sin escoger modelo; no precio supuesto |
| Tope de cada clase | `C_e`, `C_r`, preparación/oráculo `C_o` y retries; costo máximo derivado de límites y tarifa |
| Techo total en caja | `112*C_e + 36*C_r + 8*max(C_e,C_r) + C_compute + C_o + C_herramientas`; valor monetario final **pendiente**, no infinito ni cero |
| Costo económico | Añadir tiempo humano a tarifa acordada y preparación/adopción; reportarlo separado de caja. Suscripción Codex sin cargo marginal identificable no se presenta como trabajo gratuito |
| Custodia y revisión | Usuario custodia/aprueba; sesiones Codex separadas; límites de autoría/revisión explícitos |
| Go preflight → piloto | Accounting, aislamiento, oracle y adaptación A3/B3 calificados, todavía dentro del total aprobado; fallo bloquea escalado |

Costo por éxito = costo de **todos** los intentos del brazo / éxitos
independientes; cero éxitos implica no finito. También reportar marginal,
preparación y amortización a 12/100/1000 tareas como escenarios, sin declarar
ahorro hasta medir. Costos unavailable no se rellenan con cero.

## 6. Puertas y claims

Piloto: exploratorio, delta **no aplica**, sin claim de no inferioridad. Después
se podrá estimar varianza/costo para tamaño confirmatorio; **delta y tolerancia
a escapes se eligen por criterio de producto/riesgo, nunca para acomodar los
resultados del piloto**. Se aprueban y congelan antes de las tareas confirmatorias.

D2 debe resolver snapshot final y disposición del brownfield, especificación
exacta T01–T12, calificación del oráculo y permisos de publicación, modelos,
tarifas, recursos y monto total. Nada de esto impide aprobar P1 ahora. Un
resultado negativo/inconcluso del piloto se publica como tal y no se sustituye
por el conteo de gates verdes.
