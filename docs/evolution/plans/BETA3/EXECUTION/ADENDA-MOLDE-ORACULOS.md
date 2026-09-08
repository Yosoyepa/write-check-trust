# Adenda del molde — oráculos discriminantes

Decisión del arquitecto bajo D1 para los siguientes encargos P02–P10.
Complementa entrega sh-delivery/2 y molde wct-harness-local/2; no modifica
umbrales, aprobaciones humanas, alcance de mutación ni escenarios aprobados.
Se origina en la prerevisión y primera campaña focal de P02a, no en una
comparación causal entre modelos.

## Contrato mínimo para el coder

| Frontera | Regla ejecutable al escribir el test | Motivo observado |
|---|---|---|
| Errores tipados | Comprobar clase y `.code == literal`; comprobar path/errno cuando el contrato los fija. `raises(match=...)` puede acompañar, no sustituir igualdad de un código cerrado | Una regex sin anclas acepta `XXunsupported_git_stateXX` |
| Serialización | Incluir un documento completo literal independiente del serializer, Unicode y LF; distinguir igualdad exacta de sensibilidad de digest | Un serializer que omite campos puede cambiar su hash y aun pasar tests de sensibilidad |
| Límites de bytes | Expected desde los bytes conocidos de fixture o literal revisado; exacto pasa, +1 bloquea. Incluir más de un bloque de lectura | `size = len(chunk)` puede sobrevivir si todas las pruebas caben en un bloque |
| Tipos de entrada | Rechazar tipos inválidos antes de convertir/copiar/serializar. Probar un valor con protocolo ejecutable que no debe invocarse | `asdict` puede ejecutar `__deepcopy__` antes de la validación |
| Manejo de errores IO | Desafiar tanto la operación principal como la lectura usada para diagnosticar su fallo; preservar cierre de recursos | Un stat dentro de except también puede fallar y escapar sin diagnóstico contractual |
| Mutación | Conservar inventario y resultados brutos por identidad, controles positivos y errores del instrumento separados | Exit0 del comando no significa cero supervivientes ni imports correctos |

Estas reglas aplican donde exista la frontera: no añadir fixtures irrelevantes
a módulos que no serializan, no tienen IO o no leen por bloques. Antes de
codificar, el encargo identifica las filas pertinentes y reutiliza controles
existentes; no exige un framework nuevo ni tests de detalles internos para
matar mutantes semánticamente equivalentes.

## Responsabilidad separada

El coder propone expected explícito y documenta el rojo anterior al fix. El
arquitecto resuelve ambigüedades del contrato antes de ajustar esos expected;
el verifier independiente revisa la identidad final y la sensibilidad de
los tests. Si una prueba se ejecuta mientras cambian sus dependencias, no se
atribuye a una identidad congelada: conservarla como intento no acreditado.

No renombrar asistencia, reparaciones de borrador o controles añadidos por
otros actores como primera aceptación independiente del coder. No declarar
TDD retroactivo. Una posible equivalencia requiere evidencia propia y
adjudicación; esta adenda **no autoriza exclusiones ni eleva cero supervivientes**.

Referencia de la evidencia y limitaciones:
[REVISION-P02a-MUTACION-1](REVISION-P02a-MUTACION-1.md). Aplicar esta adenda
a los prompts siguientes y evaluar si reduce escapes y retrabajo; todavía no
hay medición que permita afirmar esa reducción.
