# Gherkin beta.3 — escenarios propuestos para revisión

> Para aprobar el primer incremento usar [GHERKIN-P1](GHERKIN-P1.md), que
> concreta casos, ejes, salidas y matriz. Los escenarios generales siguientes
> se conservan para incrementos posteriores; no sustituyen el contrato P1.

Estado: **borrador, no aprobado ni conectado al pipeline**. Los bloques son
especificaciones, no nuevos archivos `.feature` ni pruebas ejecutadas. Cada
incremento debe seleccionar su bloque, resolver parámetros y obtener aprobación
humana antes de implementarlo. Se evita narrativa libre bajo `Feature:` mientras
se decide el issue #35; resolver gramática no resuelve trazabilidad de ejecución.

## Mapeo y conformidad — M01–M04/M15

```gherkin
Feature: Conformidad de un molde sobre modulos reales
  Scenario Outline: El resultado depende del contrato y no del nombre de carpeta
    Given un proyecto con layout "<layout>" y molde "<molde>"
    And el inventario tiene "<clasificacion>"
    When verifico la dependencia "<dependencia>" con el motor productivo
    Then el resultado es "<resultado>"
    And la causa identificada es "<causa>"
    Examples:
      | layout | molde | clasificacion | dependencia | resultado | causa |
      | A | hexagonal-python | completa | application a ports | aceptado | permitida |
      | B | hexagonal-python | completa | application a ports | aceptado | permitida |
      | A | hexagonal-python | completa | domain a adapters.out | rechazado | dependencia prohibida |
      | B | hexagonal-python | completa | domain a adapters.out | rechazado | dependencia prohibida |
      | A | hexagonal-python | modulo sin rol | application a ports | incompleto | modulo sin clasificar |
      | A | hexagonal-python | vacia | ninguna | incompleto | inventario vacio |
      | varias raices | hexagonal-python | fuera del MVP | application a ports | incompleto | alcance no soportado |
```

## Composición, adopción y ownership — M09/M11–M14

```gherkin
Feature: Planificacion segura de una instancia de molde
  Scenario Outline: Un plan no altera el codigo y no oculta conflictos
    Given una instancia revisada con condicion "<condicion>"
    When preparo la operacion "<operacion>"
    Then la decision es "<decision>"
    And los archivos del usuario permanecen "<preservacion>"
    Examples:
      | condicion | operacion | decision | preservacion |
      | mapeo valido | plan de adopcion | propuesta revisable | identicos |
      | roles contradictorios | compilar | rechazo con ambas causas | identicos |
      | ruta externa por symlink | plan de adopcion | rechazo de frontera | identicos |
      | arbol cambio tras revisar | aplicar plan | requiere nueva revision | identicos |
      | deuda sustituida por otra de igual conteo | verificar deuda | nueva violacion | identicos |
```

## Forma frente a comportamiento — M06–M08

```gherkin
Feature: Compatibilidad observable de un puerto
  Scenario Outline: La forma correcta no aprueba una implementacion defectuosa
    Given el puerto "<puerto>" con contrato aprobado "<contrato>"
    And el adaptador "<adaptador>" satisface su firma estatica
    When ejecuto el contrato por la composicion productiva
    Then el resultado semantico es "<resultado>"
    And el estado observable es "<estado>"
    Examples:
      | puerto | contrato | adaptador | resultado | estado |
      | inventario | reservar 3 de 10 | memoria valida | aceptado | quedan 7 |
      | inventario | reservar 3 de 10 | persistencia valida | aceptado | quedan 7 |
      | inventario | reservar 3 de 10 | doble descuento | rechazado | quedan 4 |
      | inventario | reservar 3 de 10 | devuelve sin persistir | rechazado | quedan 10 |
```

## Evidencia y feedback — E01–E08

```gherkin
Feature: Cierre por evidencia correspondiente al alcance
  Scenario Outline: Una evidencia incompleta o ajena no acredita un perfil
    Given el perfil exige la capacidad "<capacidad>"
    And la evidencia tiene condicion "<condicion>"
    When intento cerrar el perfil
    Then el cierre es "<cierre>"
    And se informa "<causa>"
    Examples:
      | capacidad | condicion | cierre | causa |
      | arquitectura | misma instancia y modulos medidos | acreditado en alcance | contrato comprobado |
      | cobertura | productor falla y LCOV viejo existe | invalido | artefacto sin productor valido |
      | tests | falta un escenario requerido | incompleto | identidad faltante |
      | arquitectura | mismo HEAD pero fuente unstaged distinta | invalido | inputs diferentes |
      | mutacion fresca | solo reporte limitado G1a | incompleto | frescura no acreditada |
      | arquitectura | motor requerido ausente | incompleto | herramienta ausente |
```

```gherkin
Feature: Contexto de tarea con referencias vigentes
  Scenario Outline: El contexto obsoleto no dirige una reparacion como si fuera vigente
    Given el contexto cita el simbolo "<simbolo>" del snapshot "<snapshot>"
    And el estado actual del simbolo es "<estado>"
    When preparo el feedback para el agente
    Then la accion es "<accion>"
    Examples:
      | simbolo | snapshot | estado | accion |
      | Inventory.reserve | S1 | vigente en S1 | entregar referencia verificable |
      | Inventory.reserve | S1 | eliminado en S2 | invalidar referencia y regenerar contexto |
      | Inventory.reserve | S1 | requisito ambiguo | solicitar decision sin inventar API |
```

## Evals y coste — E09–E14 / EVALS

```gherkin
Feature: Medicion honesta de modelos economicos
  Scenario Outline: Todos los intentos permanecen en el resultado
    Given un run del brazo "<brazo>" con terminacion "<terminacion>"
    When genero el informe del experimento
    Then su disposicion es "<disposicion>"
    And su coste se registra como "<coste>"
    Examples:
      | brazo | terminacion | disposicion | coste |
      | B3 | presupuesto agotado | fallo incluido | consumo acumulado |
      | A3 | exito del agente y oracle falla | defecto incluido | consumo acumulado |
      | A4 | oracle indisponible | no evaluable visible | consumo acumulado |
      | B3 | exito independiente | exito incluido | consumo acumulado |
```

Los IDs de snapshots, capacidades y operaciones son vocabulario contractual
pendiente de concretar. No tratar estas tablas como el oracle de un benchmark:
sirven para aprobar el comportamiento de WCT, no para medir inteligencia.
