# Cómo revisar al coder y convertir hallazgos en mejoras de WCT

Estado: rúbrica propuesta antes de ver el primer patch. El arquitecto evalúa
sin identidad/precio del modelo; el coder no aprueba ni puntúa su propio código.

## 1. Paquete requerido para revisión

Contrato/versiones y aprobación de la pieza; base/candidate_id/hash; diff
completo incluyendo archivos nuevos; ruta/hash de outputs; comandos/exits;
matriz caso→nodeid; incidentes, omisiones y desviaciones; todos los intentos.
Ningún «todo verde» sustituye esos datos. Verificar el código, no solo el texto
del handoff. Consumo y modelo permanecen con el custodio hasta cerrar calidad.

Antes de ejecutar: scope del patch y entorno seguro. Después: reproducir las
pruebas desde el snapshot correcto. Si falta aislamiento, limitar la afirmación
a revisión cooperativa. No ejecutar código con acceso a secretos por comodidad.

## 2. Rúbrica no compensatoria

Cada dimensión obtiene `satisface`, `defecto` o `no-evaluable`, con evidencias
por ID. No asignar puntos por verbosidad del informe o cantidad bruta de tests.

| Dimensión | Pregunta concreta | Para P01 |
|---|---|---|
| Corrección semántica | ¿Cumple todos los casos y sus combinaciones? | iguales N/diferentes IDs, vacíos, precedencia y lista completa |
| Diseño y ensamblaje | ¿Respeta rol, dependencias y contrato público? | kernel puro stdlib; no cambios a CLI/GateResult ni efectos |
| Honestidad de tests | ¿Una implementación plausible incorrecta falla? | expected literal, SUT real, controles buenos y variantes del calificador |
| Compatibilidad | ¿Conserva contrato y bytes previos donde se prometió? | allowlist nueva, tests históricos pasan; no refactor incidental |
| Gobernanza/evidencia | ¿Candidato y criterios son identificables, sin drift ajeno? | manifest/allowlist, reporte real de G-META pre-bless, ningún lock alterado |
| Mantenibilidad | ¿Se entiende y es mínimo sin duplicación dañina? | pocos tipos/funciones útiles, nombres claros, sin framework hipotético |
| Operación y límites | ¿Se conoce lo que no se verificó? | match no acredita ejecución, alcance tools vs example explícito |

Severidades:

- **BLOQUEANTE:** aceptación falsa/omisión crítica, pérdida o escritura ajena,
  modificación del juez/baseline no autorizada, evidencia fabricada, contrato
  roto o ejecución insegura. No hay GO por una media alta de otras dimensiones.
- **HIGH/MEDIUM:** defecto reproducible de requisito/compatibilidad/arquitectura
  o prueba esencial faltante. Corregir antes de aceptar la pieza, o volver a
  decisión de alcance; no rebajarlo porque el modelo es barato.
- **LOW/INFO:** mejora no esencial o limitación ya aprobada, descrita con motivo.
  Puede acompañar un dictamen conforme, sin esconder incumplimientos reales.

Dictámenes: `CONFORME_AL_CONTRATO`, `REQUIERE_CORRECCION`, `INCONCLUSO`.
Conforme no equivale a bless, seguridad universal, coste conveniente o beta.3
lista. Un check esencial no ejecutado da no-evaluable, no conforme por defecto.

## 3. Secuencia del arquitecto/verifier

1. Cotejar allowlist/versión aprobada con diff completo. Inspeccionar callers,
   efectos y opciones no pedidas; no confiar en conteo de archivos.
2. Reproducir discrepancias concretas; separar defecto de producto, contrato,
   detector y entorno. Un rojo no prueba automáticamente una mala implementación.
3. Verificar la tabla pública y negativos del instrumento contra el SUT. No
   hacer una segunda copia del algoritmo como expected ni solo comparar CLI
   con el mismo bug in-process; combinar literal y consistencia cuando aplique.
4. Probar soluciones válidas. Si el calificador las rechaza, registrar falso
   positivo y reparar el instrumento con nueva versión/challenge.
5. Revisar cobertura real del perímetro, orden/imports/efectos y declaraciones
   humanas. La suite actual no acredita motores que no apuntan a tools.
6. Congelar dictamen con candidate hash. Devolver causas y contrato, no un fix
   completo salvo que se acuerde `architect-assisted` y se contabilice.

PROC-005: la ejecución de checks por el coder sirve como evidencia de su
trabajo, pero no lo convierte en verifier. El arquitecto que diseñó la SPEC
debe reconocer su sesgo de especificación: challenge por otra sesión/lector
o humano, sin permiso de escribir el candidato. Si no existe, declararlo.

## 4. Registro de cada hallazgo

Formato normativo de la ficha (plantilla en REGISTROS):

`finding_id`, task/run/candidate/contract/version, severidad, regla afectada,
comportamiento esperado/observado, reproducción/artefacto, causa probable y
grado de certeza, control válido, control defectuoso, primera fase que lo
detectó, señal que debió detectarlo, coste de diagnóstico, decisión y owner.

Clasificación causal:

| Clase | Ejemplo | Acción sobre WCT |
|---|---|---|
| SPEC-GAP | dos estados de salida ambiguos | aclarar contrato/versionar; no culpar al coder por criterio nuevo |
| IMPL-LOGIC | compara tamaños y acepta sustitución | arreglar pieza y conservar regresión; evaluar si contexto faltó |
| INVENTED-API | importa símbolo o firma no existente | reforzar resolución del paquete de contexto, sin inventar fallback |
| ARCH-DRIFT | núcleo importa proceso/CLI | mejorar consumidor del molde con negativo y positivo |
| TEST-ORACLE | expected sale del mismo SUT | calificar tests/detector; contar el trabajo del reviewer |
| HARNESS-ESCAPE | todos sus controles verdes, defecto reproducible | candidato de gate/red-team; no promoverlo sin precisión/coste |
| HARNESS-FP | implementación válida rechazada | calibración de regla; diagnóstico antes de suprimir o elevar ratchet |
| EVIDENCE-GAP | faltan IDs, fases, recibos o versión | mejorar captura/denominador, no rellenar valores por inferencia |
| ENVIRONMENT | herramienta ausente/flake/concurrencia | incidente separado; mismo fallo conservado y reintento trazado |

La causa inicialmente es hipótesis si solo conocemos el síntoma. No atribuir
«alucinación del modelo» a todo error ni asumir intención de engañar.

## 5. Bucle de aprendizaje sin filtrar el examen

Para desarrollo: feedback puede abrirse completo; la siguiente reparación
queda en SH-D. Para SH-E: oráculo privado se consulta al final, sin enseñar
resultados durante repair. Si se revela un caso, deja de ser holdout y se
convierte en regresión de desarrollo; no usarlo otra vez como examen secreto.

Propuesta de mejora del harness debe incluir:

1. clase de defecto más amplia que la instancia que la motivó;
2. reproducción causal y al menos un control válido;
3. negativos nuevos no usados para diseñar la regla, con revisión independiente;
4. consumidor y scope exactos, falsos positivos/negativos conocidos;
5. presupuesto técnico y coste humano de diagnóstico;
6. compatibilidad, autorización protegida si aplica y plan de reversión;
7. suite de regresión y nueva versión Wn/Qn para **otro lote**.

No promover una regla solo porque detecta el código de un modelo. La misma
regla debe tratar igual código humano, de referencia y de otros modelos.
No ocultar un error del harness reescribiendo el código correcto para complacerlo.

## 6. Feedback que se devuelve al usuario

Primero: dictamen y bloqueantes. Después: qué fue comprobado, qué sigue sin
evidencia, cuánto trabajo de reparación hubo y cuáles son propuestas de mejora
del instrumento. Tras descegamiento: coste por tarea/éxito con recibos y límites.

Cada afirmación de mejora especifica objeto: código de esta pieza, instrumento
WCT, workflow asistido o rendimiento del modelo. No intercambiar esos niveles.
