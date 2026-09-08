# SPEC-B3-02 — Evidencia de capacidades y contexto verificable de tarea

> Contrato del primer incremento: [SPEC-B3-P1](SPEC-B3-P1-evidencia.md).
> Fija subset tests/cobertura, interfaz opt-in, precedencia/exits, denominadores
> y presupuesto propuesto. Lo descrito aquí sobre arquitectura/contexto es el
> destino de beta.3 y no entra entero en P1. No se ha implementado.

Estado: **contrato conceptual propuesto**. No hay formato ejecutable/flags
nuevos implementados. Reutiliza [SPEC-001](../../../specs/SPEC-001-contratos-experimentales.md)
y [SPEC-003](../../../specs/SPEC-003-ledger-y-replay.md) sin alterar GateResult histórico.

## 1. Registro mínimo y productor de confianza

| Sección | Información obligatoria | Validación |
|---|---|---|
| Identidad | schema, run id, parent/task refs, inicio/fin/terminación | IDs únicos, estados terminales explícitos |
| Árbol | base commit, inventario/digest de inputs y patch; snapshot final | incluye cambios staged/unstaged y archivos nuevos en scope; HEAD no basta |
| Contrato | WCT/pack/mapping/config/umbrales/lock/runner versions y digests | inputs efectivos, no etiquetas obtenidas de comentarios |
| Alcance | raíces, módulos, tests, escenarios y exclusiones por capacidad | esperado independiente y mapeo total |
| Ejecución | argv real, cwd normalizado, motor/versión, exit, duración, logs | no reconstruir a partir del mensaje «ejecuté X» |
| Artefactos | productor/run id, digest, tipo, scope y relación de consumo | output correcto del productor esperado sobre los inputs de este run |
| Resultados | GateResult original y claim específico, unidades esperadas/medidas | conserva error/skip; sin aliases como instrumentos nuevos |
| Cierre | resultados, completitud, validez y límites de calificación | obligaciones exigidas se verifican antes del cierre |
| Coste | exacto/estimado/no disponible por recurso | ausencia no equivale a cero |

El inventario se fija antes de medir desde el scope/contrato aprobado y sus
inputs. No tomar como «esperado» únicamente lo que la herramienta logró devolver.
Para tests registrar nodeids requeridos/recolectados/ejecutados; para mutantes
comparar identidades generadas/reportadas bajo las precondiciones de G1b.
Tener N elementos no prueba que sean los N correctos.

Los registros de evidencia quedan fuera del set que se hashea como entrada
para evitar una dependencia circular. Ignorados como `.venv/build` no pueden
ocultar fuente ejecutada: cualquier input externo relevante queda fijado como
dependencia/imagen/fixture. No guardar valores secretos del entorno; usar una
allowlist de parámetros no sensibles y marcar la existencia de requisitos.

## 2. Frescura y cambio durante ejecución

La secuencia mínima es: fijar snapshot/contrato → ejecutar productor en espacio
propio → comprobar terminación/inventario → registrar artefacto → consumirlo
contra la misma identidad → cerrar. No reutilizar un LCOV antiguo si el
productor falla aunque aquel archivo parezca válido.

El timestamp es diagnóstico, no prueba. Si cambia fuente/tests/config después
de producir evidencia, esa evidencia no acredita el nuevo estado. Preferir
ejecución sobre snapshot inmutable; si se usa árbol vivo, comprobar inputs
antes/después y marcar invalidación. Esta comprobación local no es defensa
suficiente contra un escritor malicioso concurrente: se necesita aislamiento.

Un killed de motor no prueba causa. Crash/timeout/error de entorno son estados
distintos del fracaso de una aserción que detecta comportamiento. G1a conserva
su semántica hasta que la investigación permita observar esas diferencias.

## 3. Semántica de cierre

| Estado conceptual | Condición |
|---|---|
| acreditado en el alcance | todas las obligaciones seleccionadas pasan, con evidencia válida/completa y límites publicados |
| rechazado | existe incumplimiento de requisito observado |
| incompleto | faltan unidades, herramienta, colección o una capacidad requerida |
| inválido | mezcla de runs, inputs distintos, corrupción o verificador no confiable |

Un registro puede conservar simultáneamente fallos e invalidez: el resumen no
borra el fallo porque también hubo un error. La especificación del CLI futuro
deberá fijar precedencia y exits en un incremento propio; no reusar exits nuevos
sin revisar consumidores de beta.2.

El cierre no será un «confidence score» de 0 a 100. Publicará garantías por
capacidad: conformidad arquitectónica, contratos observables y aspectos sin
verificar. No acumular estilo para compensar un fallo de seguridad o de negocio.

## 4. Paquete de contexto: reducir incertidumbre antes de generar

Un documento pequeño de tarea, derivado de datos revisados, contiene:

- objetivo y criterios observables aprobados; ambigüedades que requieren decisión;
- scope de edición, módulos/roles y vecinos relevantes;
- símbolos/puertos reutilizables encontrados en el snapshot, con ruta y revisión;
- dependencias disponibles y restricciones; no sugerir APIs como existentes sin
  encontrarlas en código, tipos o documentación de la versión declarada;
- un ejemplo válido y uno inválido del patrón, sin incluir soluciones del holdout;
- plan mínimo de pruebas por riesgo, productores y comandos conocidos;
- límites de tiempo/calls/reparaciones y condiciones de escalación;
- digest de árbol/mapping/contrato sobre el que se produjo el contexto.

No es resumir todo el repo ni pegar cientos de reglas. El límite de tamaño se
acuerda y mide por bytes/tokens disponibles en el runtime. Si truncar oculta una
obligación, mostrar incompletitud y solicitar acotar la tarea. Un cambio en la
instancia o código invalida las referencias afectadas; no mantener API obsoleta
como consejo autoritativo.

Esto no prueba que desaparezcan las alucinaciones. Se medirán, por separado,
dependencias inventadas, símbolos inexistentes, firma equivocada, ubicación
incorrecta y lógica errónea con APIs válidas.

## 5. Feedback y reparación acotada

Diagnóstico estructurado: claim/regla, fichero y ubicación, esperado/observado,
causa, evidencia, acción orientativa y comando productor. Conservar argv como
lista; la representación copiable usa escaping correcto y no interpola entrada
no confiable en shell. Las sugerencias no son órdenes autoejecutables.

La reparación sigue pruebas y no rebaja governance. Repetición de la misma
causa, ambigüedad funcional, cambio protegido necesario o presupuesto agotado
termina en escalación, con historial intacto. No introducir reintentos ilimitados
ni un modelo premium fuera del presupuesto. La versión beta.3 puede entregar
este paquete al runtime existente sin implementar su propio bucle de agente.

La selección de checks por riesgo utiliza el impacto efectivo, no el precio del
modelo: cambiar auth, dependencias, serialización o transacciones puede exigir
pruebas adicionales aunque el diff sea corto. Selección incremental solo con
prueba de sensibilidad; si el impacto no puede determinarse, no omitir checks
requeridos para fingir menor latencia.

## 6. Escenarios y oráculo

Para las features del molde, mantener IDs estables de requisitos → escenarios
→ tests recolectados → resultados; declarar las features históricas que siguen
siendo solo parseadas. Cero escenarios/tests requeridos no es éxito.

La aceptación visible se ejecuta por el entrypoint real. El oráculo de evals se
custodia fuera del task workspace y se evalúa después de congelar el patch.
No entregar al agente logs del holdout para repararlo ni permitirle redefinir
scorer, entorno o tests que puntúan el resultado final.

## 7. Calificación del registro y del contexto

| ID | Negativo/control requerido |
|---|---|
| E01 | mismo HEAD, cambio unstaged o archivo nuevo: digest diferente, evidencia anterior no aplicable |
| E02 | LCOV viejo + productor fallido: inválido/incompleto, nunca aprobado |
| E03 | artefacto correcto de otro run/config/scope: rechazo atribuido |
| E04 | inventarios de igual tamaño con distinta identidad: incompleto/inválido |
| E05 | tool ausente, salida truncada, crash, timeout y SKIP requerido: no cierre |
| E06 | se omite un escenario requerido pero la suite restante pasa: detectado |
| E07 | cambio de verificador/config desde el agente: runner independiente rehúsa la evidencia |
| E08 | contexto señala símbolo eliminado o contrato actualizado: invalidación observable |
| E09 | reparación cambia baseline o duplica intentos para esconder fallo: prohibición/historial verificable |
| E10 | logs sugieren éxito sin patch o con error de estado: no puntúan como solución |
| E11 | intento de leer oracle, secretos o root externo: frontera de aislamiento comprobada |
| E12 | comando con argumento compuesto: argv y texto escapado preservan límites reales |
| E13 | alias de un gate: conserva vínculo con detector y no duplica cobertura de claims |
| E14 | orden aleatorio o cancelación: no pierde ni mezcla IDs/artefactos de otro run |

Además de estos negativos, cada capacidad exige un control válido y casos de
frontera. No confundir esta matriz de diseño con tests ya implementados.
