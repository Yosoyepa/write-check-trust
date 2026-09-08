# Propuesta de adjudicación focal — requiere autorización humana

Estado: **no autorizada, no aplicada**. Alcance solicitado: calificación focal
P02a de beta.3. TEST-002, thresholds y la skill wct-hardening conservan hoy su
exigencia de cero supervivientes. D1 delega contratos, no permite elevar un
umbral ni convertir unilateralmente una excepción en PASS.

## Problema comprobado

La campaña inicial tuvo1552 mutantes y257 supervivientes; R1 tuvo1564 y96.
No son una comparación causal ni denominadores idénticos. Hay huecos reales
de tests, en reparación, y al menos un cambio equivalente con evidencia
independiente: `json.dumps(ensure_ascii=False)` frente a `None` en el runtime
calificado. Ambos seleccionan el mismo encoder; las muestras, incluido el
golden completo, producen bytes idénticos. Véase
[REVISION-P02a-MUTACION-1](REVISION-P02a-MUTACION-1.md).

Obligar a distinguir ese cambio mediante un mock de kwargs mediría el
andamiaje, no una diferencia del producto. Ocultarlo del inventario haría
incomparable la campaña. Ninguna de esas acciones está autorizada.

## Criterio propuesto, sin aplicar

| Clase | Requisito y consecuencia |
|---|---|
| R: diferencia observable contractual | Debe detectarse con tests discriminantes; si sobrevive, bloqueo |
| E: equivalencia demostrada en el perfil | Candidato a excepción individual, únicamente con revisión independiente y permiso humano para este criterio |
| D: diferencia observable en aspecto no especificado | Bloquea conformidad hasta aclaración contractual y reverificación. No llamarla equivalencia ni eximirla automáticamente |
| U: desconocido | Bloqueo; no asimilar falta de contraejemplo a prueba de equivalencia |
| I: instrumento inválido, import incorrecto, timeout o no ejecutado | No es killed ni E. Corregir/repetir o declarar calificación incompleta |

Para E se exige identificar la función y el delta del operador, dominio de
inputs y salidas/errores relevantes, razonamiento de equivalencia y controles
positivos/negativos pertinentes. Una muestra que coincide no basta sola.
Declarar límites: versión de Python/Git/biblioteca, perfil y dependencia de
que no se sustituya deliberadamente una primitiva por un mock introspectivo.
No confundir cambios de args/cause de excepción con identidad de comportamiento
si ese diagnóstico cambia; van inicialmente a D, no a E.

## Registro y control de la excepción propuesta

- Manifiesto completo del candidato, revisión base, herramienta/versión,
  inventario generado, resultados brutos y conjunto exacto de IDs adjudicados.
- Dos voces separadas: coder propone, verifier independiente desafía y
  arquitecto decide dentro de la autorización humana, si se concede.
- Ninguna exclusión por patrón, archivo completo, porcentaje tolerado o por
  declarar un helper privado. No suprimir cobertura, generar tests de detalles
  internos sin valor contractual ni mover literales fuera del alcance medido.
- Fuente, operador, runtime o perfil cambiados invalidan la adjudicación
  aplicable: no copiar veredictos de IDs nominalmente iguales a nuevos bytes.
- Informe conserva siempre **killed, survived bruto, E adjudicados, R/D/U/I**.
  No publicar «cero supervivientes brutos» cuando no es verdad.
- La posible conformidad sería «calificación focal con equivalentes
  adjudicados bajo autorización», no un G-MUT productivo verde inventado.
  Los otros gates, controles, umbrales y la revisión final siguen obligatorios.

Esta propuesta no implementa un clasificador ni modifica governance, flags,
locks o manifests. Bless, integración del producto y publicación mantienen
sus puertas. Si no se autoriza, se conserva el bloqueo por la regla vigente;
los refuerzos reales y su evidencia siguen siendo trabajo aprovechable.
