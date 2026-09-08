# Evals beta.3 — ¿cuándo compensa el modelo económico?

> Para el encargo vigente aplicar [evaluación ciega de automejora](SELF-HOSTING/EVALUACION-CIEGA.md):
> primer repo WCT; modelo custodiado en secreto; calidad antes de coste, sin
> techo monetario como filtro de aprobación. Desarrollo SH-D ahora; comparación
> interna Wn/W0 propuesta después de calificar instrumentos. El piloto externo
> siguiente se conserva, pero no está ejecutado ni sustituido por una entrega
> exitosa de WCT sobre WCT.

> Selección concretada en [PILOTO-PREPARACION](PILOTO-PREPARACION.md): usuario
> elige personalAssistant y Codex para el oráculo; 12 tareas candidatas, 144
> runs + 4 preflight y hasta 8 retries de infraestructura propuestos. Ni modelos,
> tarifas, tope monetario ni inferencia están aprobados. D0 limita mutación.

Estado: **protocolo propuesto; cero corridas de modelo realizadas en este turno**.
Extensión acotada de [PRD-003](../../prd/PRD-003-benchmark-modelo-economico.md),
[SPEC-002](../../specs/SPEC-002-metricas-y-estadistica.md) y
[gobierno del corpus](../../specs/SPEC-004-gobierno-del-corpus.md).

## 1. Preguntas y orden de las pruebas

1. ¿El molde/gate acepta soluciones válidas y detecta los defectos que promete?
2. ¿Un usuario puede adoptarlo sin reescribir su arquitectura ni perder cambios?
3. ¿El sistema beta.3 mejora éxito o coste frente a WCT beta.2 con el mismo modelo?
4. ¿En qué tareas se acerca a un modelo de referencia y cuáles siguen necesitando escalación?

Primero calificar instrumentos y adopción; después inferencia. Pruebas sin
claves/replay sirven para el runner. No son evidencia de rendimiento del modelo.
Los resultados de adversarios artificiales y de tareas reales se reportan
separadamente.

## 2. Brazo nuevo sin cambiar A0–A5 históricos

| ID | Modelo y tratamiento | Qué estima |
|---|---|---|
| A0 | económico; requisitos y checks neutrales de la tarea, sin WCT | baseline económico competente |
| A3 | mismo económico; WCT beta.2 fijado, reglas/gates y reparación | baseline actual del producto |
| B3 | mismo económico; candidato beta.3 + molde + contexto + capacidades aprobadas | efecto del paquete nuevo |
| A4 | modelo de referencia; mismo baseline neutral de A0 | comparación de capacidad/coste |

El control conserva tests, type checker y herramientas normales que pertenezcan
a la tarea. No deshabilitar pruebas para hacer ganar a WCT. Los requisitos de
arquitectura son visibles en todos los brazos; hidden tests no puntúan requisitos
que solo recibió B3. A3 se configura correctamente para el repo por un mantenedor
antes del freeze: no comparar un B3 adaptado contra un beta.2 roto por medir `example`.

El snapshot de negocio es idéntico entre brazos. El overlay de instrucciones,
controles y herramientas del tratamiento se monta/se registra por separado;
sus diferencias son deliberadas y auditables. Presupuestos, red y herramientas
ajenas al tratamiento permanecen iguales. No compartir historial ni memoria de
soluciones entre runs.

**B3−A3 mide el paquete, no el molde aislado.** Si interesa atribuir mecanismo,
aprobar después una ablación sobre el mismo core beta.3: contexto apagado/activo
× enforcement del molde apagado/activo, con requisitos textuales constantes y
feedback definido. A1/A2 siguen disponibles para separar instrucciones de gates.
No añadir todos los brazos en el primer piloto.

A4 es un baseline de referencia, no el mejor sistema posible con ese modelo.
Antes de afirmar que el económico sustituye al sistema premium optimizado,
comparar también el modelo de referencia con el mismo paquete beta.3, o A5 para
la pregunta histórica sobre WCT. No adjudicar al precio del modelo una ventaja
que en realidad procede de darle controles solo a uno de los dos.

## 3. Corpus y volumen propuesto

### Etapa sin inferencia

- Matrices M01–M16 y E01–E14 de las SPEC; controles buenos, defectuosos y de frontera.
- Dos layouts Python equivalentes y un fixture brownfield con deuda identificada.
- Un mismo puerto con dos adaptadores reales de prueba y una variante rota.
- Ruta CLI/API ensamblada y colección de escenarios requeridos.
- El equipo revisa a ciegas los expected cuando sea posible; el generador del
  molde no produce el expected autoritativo de sus propios tests.

### Preflight instrumental, separado de la medición

Propuesta: 2 tareas de desarrollo × 2 brazos (A3/B3) × 1 repetición = **4 runs**.
Solo comprueba aislamiento, accounting y evaluación. Necesita autorización de
API aunque sea pequeño. No cuenta entre las 144 corridas del piloto ni en un claim.

### Piloto exploratorio

Propuesta inicial: **12 tareas × 4 brazos × 3 repeticiones = 144 runs**;
no 144 tareas independientes. Distribuir 4 tareas en cada uno de 3 codebases
Python autorizados: un fixture greenfield, uno de layout alternativo y un repo
existente representativo. Si solo hay sintéticos, declarar la limitación y no
afirmar generalización a usuarios reales.

Distribución sugerida de tareas (ajustable antes del freeze):

- 3 cambios funcionales pequeños con reglas de negocio y errores observables;
- 3 integraciones de puertos/adaptadores, incluyendo dependencia inexistente o
  firma plausible pero equivocada;
- 2 refactors que preservan comportamiento y cambian ubicación/nombre;
- 2 reparaciones de regresiones con tests visibles insuficientes;
- 2 cambios brownfield con riesgo de violación arquitectónica o deuda nueva.

Autorización de pagos, auth sensible, migraciones destructivas y seguridad de
producción quedan fuera del piloto inicial de aceptación de código. Sus casos
adversariales controlados pueden calificar rechazo/escalación, sin afirmar
capacidad de implantarlos en producción.

Las 12 tareas sirven para factibilidad y varianza, no para probar no inferioridad.
Una fase confirmatoria usa nuevas tareas de holdout, varios repos y tamaño
derivado de potencia/coste. Los rangos anteriores de 30–50 tareas son planificación,
no una garantía de potencia. Tampoco 3 repos bastan para inferencia poblacional.

## 4. Preparación y oráculo

- Especificación aprobada antes de solución; requisitos críticos separados.
- Una solución de referencia y al menos otra implementación válida cuando aplique.
- Negativos plausibles: retorna constante, ignora error, no persiste efecto,
  firma falsa, dependencia incorrecta, test que se valida a sí mismo.
- Referencia estable en cinco ejecuciones limpias como punto inicial heredado
  de SPEC-004; cualquier flake se registra y corrige fuera del holdout.
- Oráculo privado fuera del workspace del agente, con licencia/procedencia,
  versión y acceso registrado. Evaluación posterior al patch congelado; sin
  realimentar sus resultados durante reparación.
- Entorno de scoring aislado: el patch también puede intentar interferir con
  pytest, imports o procesos del verificador. Comprobar tests esperados y
  controles del scorer, sin conceder confianza a un simple exit 0.
- Revisión humana ciega a modelo/brazo en los criterios no automatizables.
  Si el mismo autor prepara tarea y oráculo, declarar conflicto y exigir challenge.
- Separación dev/validation/holdout por familias y repos cuando sea posible.
  Renombrar una tarea pública no elimina contaminación.

## 5. Ejecución y control de presupuesto

Bloquear por tarea; aleatorizar orden de brazos y alternar ventanas de ejecución.
Registrar seeds de asignación y de tests. Un seed de inferencia no es portable
entre proveedores; si no existe, registrar indisponibilidad, no reproducibilidad ficticia.
Cada run tiene sesión, workspace y cache aislados; efectos de cache se estudian
como condición separada y facturada.

El protocolo congela dos nociones distintas:

- **calidad a recursos comparables:** mismos límites de tiempo/calls/reparaciones
  y contexto útil; tokens se reportan porque los tokenizadores pueden diferir;
- **frontera coste/calidad:** varios presupuestos monetarios aprobados, sin
  presentar resultados de más presupuesto como una comparación isocoste.

Punto de partida de planificación: una propuesta más hasta dos rondas de
reparación visible por run. No es política productiva aprobada. Mantener la
misma oportunidad de revisión neutral en A0/A4; las oportunidades no utilizadas
se conservan como dato. No escoger el mejor de varios patches después de consultar
el holdout: puntúa la salida final elegida con señales visibles.

Antes de iniciar: model IDs/snapshots, parámetros, ventana temporal, tarifas,
tope por run, tope total, concurrencia, política de error/reintento y custodia.
Un presupuesto total no conocido bloquea las llamadas, no la preparación documental.
Un cambio de versión de modelo durante el estudio produce un lote separado o
invalida la comparación, según la regla preregistrada.

## 6. Métricas que responden al caso de uso

| Métrica | Definición y precaución |
|---|---|
| Éxito independiente | runs asignados que satisfacen criterios críticos y umbral restante preregistrado / runs asignados; budget exhausted es fallo |
| Uplift de producto | diferencia emparejada `p(B3) − p(A3)`; informar también A3−A0 |
| Brecha con referencia | `p(B3) − p(A4)`; no equivalencia por ausencia de significancia |
| Escape condicionado | runs con gates visibles verdes y defecto oculto / runs con esos gates verdes; cero verdes → no estimable |
| Defecto crítico | casos críticos fallidos por brazo, denominadores e identidades; no compensable con estilo |
| Coste por éxito | coste de TODOS los runs del brazo / éxitos; cero éxitos → no finito, no cero |
| Reparación | intentos, tiempo y coste hasta estado final; curva éxito frente a presupuesto |
| Alucinación observable | símbolos/dependencias/firma inventados, separados de errores de negocio y arquitectura |
| Falso positivo | fixture/solución válida rechazada; tasa por regla y tiempo humano para resolverla |
| Adopción | minutos hasta mapeo/plan aprobado y primer resultado completo; cambios necesarios al repo |

Coste económico: inferencia facturada + compute/herramientas + revisión humana
a tarifa declarada. Mantener separado coste en caja y oportunidad, recursos
exactos y estimaciones; no sumar duración y dinero sin una conversión explícita.
Reportar coste inicial de diseñar/calificar el molde y de incorporar cada repo.

Amortización conceptual: `coste_molde / número_de_tareas + coste_variable_por_tarea`.
Punto de equilibrio solo existe si el ahorro variable es positivo a calidad
aceptable. No fijar un porcentaje de ahorro antes de medir.

## 7. Estadística y datos faltantes

- Mostrar resultados por tarea/run y agregado, con intervalos y tamaños reales.
- Bootstrap emparejado por tarea conserva juntos brazos/repeticiones; con pocos
  repos presentar además resultados por repo y sensibilidad al retirar uno.
  Una fase confirmatoria necesita diseño que represente la variación entre repos.
- No tratar las tres repeticiones como tres problemas independientes.
- Para no inferioridad, aprobar antes del holdout margen `delta` y tolerancia a
  escapes críticos. El límite inferior del intervalo de B3−A4 debe superar
  `−delta`; el piloto no tiene autorización de sostener ese claim.
- Ejemplo de cautela: con 0 escapes en 30 observaciones independientes, el
  límite superior unilateral binomial de 95 % es aproximadamente 9.5 %
  (`1 − 0.05^(1/30)`). Los adversarios fijos de WCT no son tal muestra aleatoria:
  el cálculo ilustra el límite, no estima el riesgo del red team actual.
- Missing oracle produce resultado no evaluable, conserva asignación y se
  informa análisis pesimista; no desaparecerlo para mejorar pass rate.
- Error de infraestructura se reintenta solo según regla objetiva congelada;
  se conserva original, coste y vínculo. Nunca borrar un fallo por ser desfavorable.
- Reruns, exclusiones, stopping y múltiples comparaciones quedan preregistrados.

## 8. Tres decisiones distintas

| Decisión | Evidencia necesaria |
|---|---|
| ¿Publicar beta.3 experimental? | features/verificación/migración completas y piloto informado con sus límites; puede ser negativo |
| ¿Afirmar ahorro o uplift? | efecto útil con incertidumbre compatible, coste total y sin empeorar riesgo según criterios aprobados |
| ¿Usar automáticamente el modelo económico? | evidencia por estrato/riesgo, presupuesto, escalación y control humano aprobados; no parte del MVP |

Entregable del piloto: manifest/corpus/tarifas congelados, ledger íntegro,
tabla de resultados con denominadores, casos discordantes, coste humano,
desviaciones y decisión GO/INCONCLUSO/NO-GO para cada claim. No un único badge verde.
