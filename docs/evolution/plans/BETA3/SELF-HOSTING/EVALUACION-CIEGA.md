# Evaluación ciega: calidad primero, coste después

Decisión del usuario, 2026-09-07: modelo secreto para evitar sesgos, sin usar
presupuesto como filtro de esta fase; al final aportará datos de OpenRouter.
**No solicitar su identidad al coder ni buscarla en configuración/logs.**
Este documento no ejecuta inferencias ni fija precios imaginarios.

## 1. Dos preguntas que no deben mezclarse

| Carril | Pregunta | Qué puede concluir |
|---|---|---|
| Desarrollo SH-D | ¿El coder entrega esta pieza correctamente y qué feedback necesita? | calidad de primer candidato/final, defectos, reparaciones, costes de esa trayectoria |
| Experimento SH-E | ¿El mismo modelo mejora con una versión/tratamiento WCT frente a otra? | diferencia emparejada bajo ese protocolo, con incertidumbre |

P01 es **SH-D**, no una comparación causal. Dar más feedback y obtener mejor
código demuestra que esa trayectoria produjo una corrección, no cuánto la
causó WCT frente a un coder competente con otras herramientas.

Antes de P06 el tratamiento disponible es WCT beta.2 + contratos/revisión
manual de este dossier. No llamarlo «software beta.3 funcionando». Después de
P06 puede evaluarse `B3-evidence`, limitado a la cadena implementada. Solo tras
P07–P09 calificadas se ensaya `B3-moldes-contexto`. No cambiar etiquetas para
atribuir a features futuras resultados de un proceso humano.

## 2. Cegamiento y custodia

El usuario asigna `coder_blind_id`, `task_id`, `run_id` y candidate_id opacos.
Custodia fuera del repositorio del coder y del paquete del reviewer:

- modelo solicitado y realmente servido, proveedor/routing/fallbacks,
  versión o ventana temporal cuando no haya snapshot fijo;
- configuración de inferencia, runtime y sesiones, recibos completos;
- asignación de brazos y, si procede, equivalencia de configuración entre ellos.

El arquitecto recibe contrato, código, tests, salidas técnicas y IDs ciegos;
no precio, marca ni ranking. No usa estilometría para adivinar el modelo.
Dictamen de calidad y severidades se congelan antes de abrir costes/identidad.
Los costes pueden revelarse agregados por tarea sin revelar el modelo si el
usuario prefiere mantenerlo ciego.

La revisión puede reconocer un tratamiento por su código: **ciego al modelo
no significa doble ciego perfecto**. El custodio oculta también el brazo en
la revisión semántica cuando sea practicable y registra cualquier revelación.
La separación de sesiones del mismo arquitecto reduce memoria explícita,
no elimina correlación de criterio con quien escribió la especificación.

No guardar un hash simple del nombre del modelo como supuesto secreto:
el espacio de nombres es pequeño. Custodia privada basta para este inicio;
si se usa compromiso criptográfico, requiere sal secreta/protocolo propio,
no una promesa de anonimato por SHA sin más.

## 3. SH-D: cómo registrar cada automejora desde P01

1. Congelar contrato/allowlist/criterios; asignar IDs ciegos antes de editar.
2. Guardar todos los intentos de trabajo y llamadas a herramientas que el
   runtime pueda observar. No registrar razonamiento privado del modelo ni
   exigirlo: hacen falta acciones, outputs, patches, tiempos y consumo.
3. El coder entrega su **primer candidato completo** con hash. Tests focales
   y ciclos TDD previos no se borran; son coste de ese candidato.
4. Verifier/arquitecto evalúan sin precio/modelo. El dictamen no sustituye las
   pruebas y señala qué dependió de juicio humano.
5. Reparación visible autorizada → nuevo candidate_id y parent_id. Se preserva
   la calidad del primero; el éxito final no la reemplaza.
6. Guardar todos los hallazgos en el ledger. Una revisión que proporciona el
   arreglo exacto se clasifica `architect-assisted`, no coder autónomo.

Un intento de desarrollo no tiene aquí techo monetario. Las reparaciones
posteriores se delegan explícitamente; no seguir generando indefinidamente
hasta encontrar un candidato que permita ocultar los anteriores.

## 4. SH-E: comparación interna que realmente cabe en WCT

Las reglas obligatorias de este repo y sus hooks no se desactivan para fabricar
un «sin WCT». Por tanto, el primer contraste interno es **incremental**:

| Brazo | Condición congelada | Igual en ambos |
|---|---|---|
| A3-SH | mismo coder ciego + W0 beta.2 y herramientas normales | tarea, requisitos, snapshot del sujeto, política común, oportunidad de reparar |
| B3-SH | mismo coder ciego + Wn con capacidades nuevas calificadas | evaluación final Qn, recursos externos al tratamiento, entorno y custodia |

La diferencia estima **Wn frente a W0**, no todo WCT frente a ausencia de WCT,
ni mejora intrínseca del modelo. Dar más requisitos funcionales solo a B3
invalidaría la comparación. El paquete ejecutable/contexto específico sí puede
ser parte del tratamiento, declarado de antemano.

Para estudiar WCT frente a un baseline neutral o comparar modelos, retomar
A0/A4 de [EVALS](../EVALS.md) en un protocolo de laboratorio autorizado; no
ignorar AGENTS/hooks en este proyecto. No hay modelo de referencia designado
en este encargo y no se presume uno a partir del modelo del arquitecto.

### Preflight de instrumentos, todavía sin claims

Antes de corridas comparativas: replay sin claves con fixture válido,
defectuoso, cancelado y recibo ausente. Probar:

- referencia W0/Qn realmente cargada de su instalación fijada, no desde el
  cwd/import path del candidato; el sujeto evaluado sí es el patch correcto;
- una alteración del runner del candidato no modifica el árbitro ni el expected;
- alcance igual del sujeto entre brazos; tratamientos montados por separado;
- accounting asocia todas las solicitudes/reintentos sin duplicar registros;
- patch/oráculo/outputs no cruzan permisos ni mezclan árboles;
- si el aislamiento no existe, registrar revisión cooperativa, no holdout secreto.

No hace falta crear ahora un orquestador o integrar OpenRouter en WCT core.
El operador puede registrar/exportar y delegar sesiones manualmente. Automatizar
solo cuando haya una repetición costosa y un contrato de exportación calificado.

### Lote exploratorio pequeño propuesto

Después de P06 y del preflight, preparar **6 tareas nuevas × 2 brazos × 2
repeticiones = 24 runs** sobre snapshots emparejados de WCT. No es aprobación
de 24 llamadas: un run puede contener varias llamadas. El usuario decide
arrancarlo por separado; precio y presupuesto no son un criterio de calidad.

Las seis tareas deben ser cambios independientes y puntuables, repartidos
entre lógica/errores de evidencia, integración/IO y arquitectura/contexto.
Usar tareas no utilizadas para calibrar Wn/Qn. No incluir P01 ya vista y llamar
holdout a una copia renombrada. Si todas proceden del mismo módulo/familia,
declarar esa dependencia y ampliar antes de generalizar.

Por tarea: mismo estado inicial en cada brazo; dos sesiones nuevas por brazo,
orden sorteado por el custodio, caché/memoria e historiales separados. Modelo
idéntico entre brazos, atestiguado por el custodio sin revelar nombre; cambios
de routing/provider quedan registrados y estratificados si afectan comparación.

Propuesta de oportunidad comparable: una entrega inicial + hasta dos rondas
de reparación con feedback visible; mismo límite de tiempo de trabajo/calls
fijado por el operador antes del lote. No hace falta igualar dinero ni consultar
precios antes de puntuar. Límites técnicos evitan dar más intentos a un brazo;
no son razón para relajar checks. Si no se fija oportunidad comparable, el
resultado sigue siendo descriptivo de dos workflows, no comparación controlada.

Evaluar una vez el **candidato final elegido sin consultar holdout**. No elegir
el mejor de tres tras mirar resultados privados. Registrar primer intento por
separado solo si el protocolo protege ese scoring de la reparación. Los fallos
de infraestructura tienen criterio objetivo y vínculo de reintento; no se
borran del ledger/coste ni se reclasifican por conveniencia.

24 runs son exploratorios en **un solo repo y seis tareas**, no 24 problemas
independientes ni evidencia de no inferioridad. No hay umbral de ahorro elegido
después de ver resultados. Generalización requiere nuevas tareas/repos externos.

## 5. Métricas y denominadores

| Métrica | Definición |
|---|---|
| Conformidad independiente | tareas/runs que satisfacen todos los criterios críticos y el contrato completo; mostrar también no evaluables y total asignado |
| Primer candidato / final | dos tasas distintas; no sobrescribir la primera con la reparada |
| Escape | candidato con checks visibles verdes y defecto detectado después; denominador = candidatos verdes realmente evaluados |
| Falso positivo | solución válida rechazada por un control; reportar denominador de controles válidos y causa por regla |
| Errores de implementación | semántica, omisión, API/dependencia inventada, arquitectura, pruebas débiles, manipulación de evidencia; identidad por defecto |
| Carga de reparación | entregas, ciclos, minutos y tipo de ayuda, incluida corrección escrita por arquitecto |
| Coste por tarea asignada | todos los costes facturados del lote / todas las tareas-runs asignadas |
| Coste por éxito independiente | coste de TODOS los runs del brazo / éxitos independientes; sin éxitos = no finito |
| Coste total de ingeniería | inferencia + compute + revisión/diseño a tarifa declarada, separados caja/oportunidad |

Un scalar de calidad no compensa un defecto crítico con estilo bonito. Tasa
de escape con cero verdes es no estimable, no 0 %. Coste desconocido es
unavailable, no gratuito. Mostrar datos por tarea/familia además de agregados.

En SH-E estimar diferencias emparejadas por tarea, manteniendo juntas sus
repeticiones. Con N=6 mostrar pares/rangos y mucha cautela con intervalos;
no declarar significancia/equivalencia basándose en pocos ejemplos o en un
intervalo que contenga cero. La muestra confirmatoria y margen de riesgo se
deciden antes de nuevas tareas, no mirando el piloto.

## 6. Coste posterior con OpenRouter

El custodio conserva el objeto de uso de cada respuesta y su generation ID,
incluido el evento final si usa streaming. La documentación oficial describe
tokens, caché/razonamiento cuando existen y coste en la respuesta; esos datos
pueden mantenerse privados hasta cerrar calidad. No añadir flags antiguos
solo por ejemplos históricos. [Usage Accounting](https://openrouter.ai/docs/cookbook/administration/usage-accounting).

Si hay que completar un registro, la API de generación permite consultar por
ID metadatos/consumo/coste; esa respuesta también puede revelar modelo y
proveedor y la maneja el custodio. No pedimos su clave ni consultamos su cuenta.
[Metadatos de una generación](https://openrouter.ai/docs/api/api-reference/generations/get-request-&-usage-metadata-for-a-generation).

Reconciliación propuesta, no promesa de un SDK implementado:

1. Dedupe por ID de generación; distinguir reintento de extracción del recibo
   y nueva inferencia facturable. No sumar cada chunk SSE como llamada.
2. Conservar campos crudos y unidades; preferir importe facturado reconciliado.
   No sumar `usage.cost` y `total_cost` de la misma generación como dos gastos.
3. No volver a añadir upstream/reasoning/cached como coste/tokens independientes
   sin semántica explícita: pueden ser componentes de un total ya contabilizado.
4. Para ausencia de factura, estimación separada con consumo, tarifa, fecha,
   caché/routing y supuestos. Las specs/tarifas solas no reconstruyen consumo.
5. Mostrar completitud de recibos: esperados/recuperados/desconocidos y coste
   de solicitudes fallidas/canceladas cuando sea observable; no asumir cero.
6. Descegar costes solo después del dictamen; no cambiar la puntuación porque
   el modelo resulte barato/caro. El balance económico es otro resultado.

Registrar también coste del arquitecto/verifier/infra cuando sea disponible,
sin atribuirlo al coder. El coste histórico de diseñar este dossier no está
medido; no inventarlo ni omitir que hay inversión inicial para amortizar.

## 7. Fuentes metodológicas y límite

El protocolo adapta evaluación específica de la tarea, registro completo y
calibración humana recomendados por las
[buenas prácticas oficiales de evals](https://developers.openai.com/api/docs/guides/evaluation-best-practices).
Se usa el método, no se añade dependencia a una API de evals ni se presupone
que un proveedor tenga mejor criterio. La aleatorización/custodia/contratos de
este ensayo son decisiones del proyecto, no resultados demostrados por esa guía.
