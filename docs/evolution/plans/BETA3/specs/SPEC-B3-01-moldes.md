# SPEC-B3-01 — Contrato mínimo de moldes arquitectónicos

> Precisión D0: [MVP y puerto](../D0.md) concretan contenedores, roles vacíos
> permitidos y Protocol co-localizado sin reclasificar módulos mixtos.
> [Trazabilidad](../TRAZABILIDAD-D0.md) identifica los consumidores existentes.
> No comenzar P2 hasta aprobar y calificar [P1](SPEC-B3-P1-evidencia.md).

Estado: **diseño propuesto**. No existe todavía una CLI `wct mold` ni el schema
que se describe aquí. Todo nombre de entidad/capacidad de esta SPEC es conceptual.
ADRs: [01](../decisions/ADR-B3-01-moldes.md), [04](../decisions/ADR-B3-04-adopcion.md).

## 1. Unidades y versionado

| Unidad | Datos obligatorios | Propósito |
|---|---|---|
| Pack | id, versión, digest, licencia/procedencia, schema y compatibilidad WCT/Python/motores | objeto inmutable que se puede revisar y fijar |
| Roles | identificadores, intención, dependencias permitidas, prohibiciones externas | contrato del patrón, independiente de carpetas |
| Capacidades | claim, motor/versión, parámetros, unidad/scope, límites, obligatoriedad | qué es ejecutable y qué requiere persona |
| Contratos | puertos/símbolos, invariantes aprobadas y tipo de prueba | compatibilidad real, no solo forma |
| Calificación | fixtures buenos/malos/frontera, expected independiente y plataforma | evidencia sobre el molde y sus instrumentos |
| Instancia | pack fijado, package/root, mapeos, símbolos, decisiones/excepciones | adaptación a un repo concreto |
| Plan efectivo | entradas fijadas, inventario de módulos y contratos, salidas y hashes | única referencia común para generación, medición y reporte |

Versión del pack, versión del motor y versión WCT son distintas. El contenido
del pack no se modifica bajo el mismo digest. No aceptar `latest` en un plan
aprobado. Una versión semántica ayuda a migrar pero no sustituye el digest.

## 2. Scope beta.3 y clasificación total

MVP: Python, una raíz de fuente y un paquete de negocio por instancia. El
prefijo del paquete puede estar anidado; los roles se asignan a módulos por
prefijos explícitos, no por `split('.')[1]`. Tests/harness/generados se clasifican
separadamente y se declaran como dentro o fuera de cada capacidad.

1. Descubrir módulos reales de la raíz aprobada, sin ejecutar código del repo.
2. Validar existencia de raíz/paquete y que el inventario no esté vacío.
3. Resolver cada módulo exactamente a un rol o exclusión aprobada.
4. Un solapamiento necesita partición explícita (por ejemplo, aplicación salvo
   su subpaquete de puertos); nunca una prioridad implícita por orden de YAML.
5. Publicar inventario total, clasificado, excluido, ambiguo y sin clasificar.
6. Cambio posterior de archivos/mapeo invalida el plan revisado.

Nuevos módulos no heredan una exclusión amplia por conveniencia. Múltiples
raíces/paquetes o sintaxis fuera de las capacidades del pack producen
`unsupported/incomplete` en el contrato nuevo; no se reduce el scope a la primera
raíz silenciosamente. El inventario es un denominador, no un detector de negocio.

## 3. Grafo de referencia `hexagonal-python`

Las flechas significan **puede importar código de**, no «llama en tiempo de
ejecución». Imports internos del mismo rol están sujetos a ciclos y al resto
de reglas; no quedan libres de controles.

| Rol fuente | Roles internos permitidos | Restricción/razón |
|---|---|---|
| domain | domain | sin dependencia de aplicación, adaptadores o composición |
| ports | ports, domain | contratos propiedad del lado que los necesita; sin concreciones de infraestructura |
| application | application, ports, domain | depende de abstracciones; no crea clientes HTTP/DB concretos |
| adapters.in | adapters.in, application, ports, domain | traduce entrada externa; no accede directamente a adapters.out |
| adapters.out | adapters.out, ports, domain | implementa conversación requerida por el núcleo; no importa casos de uso |
| composition | todos los anteriores y composition | ensambla implementaciones; el núcleo no importa esta raíz |

Todas las aristas entre roles no enumeradas están prohibidas para este pack.
El patrón general no exige esta única descomposición: es una variante concreta,
documentada y verificable del catálogo mínimo WCT, no una definición universal.

Para cada rol, políticas de dependencias externas distinguen standard library,
paquetes permitidos/prohibidos y casos de review. Lista de permitidos fijada por
el proyecto y sus dependencias declaradas. Un import desconocido no se resuelve
instalando automáticamente un paquete sugerido por el modelo.

### Misma arquitectura, distintos layouts

| Rol | Layout A | Layout B |
|---|---|---|
| domain | `shop.domain` | `commerce.core.entities` |
| ports | `shop.application.ports` | `commerce.core.contracts` |
| application | `shop.application` excepto ports | `commerce.core.usecases` |
| adapters.in | `shop.adapters.inbound` | `commerce.api` |
| adapters.out | `shop.adapters.outbound` | `commerce.infrastructure` |
| composition | `shop.entrypoints` | `commerce.bootstrap` |

Ambos deben aceptar/refutar las mismas aristas por rol. Renombrar directorios
no debe cambiar el veredicto si el mapeo conserva relaciones.

## 4. Encaje y semántica de los puertos

Cada puerto registrado define las operaciones/símbolos y su contrato de
comportamiento aprobado. Comprobar por separado:

- forma: firma, tipos de entradas/salidas y conformidad estática;
- errores: excepciones/resultados públicos y traducción en la frontera;
- efectos: estado observable, orden si importa y atomicidad/idempotencia si el
  requisito las promete;
- sustitución: misma suite contra adaptadores aplicables, incluyendo al menos
  una implementación alternativa cuando el puerto declara intercambiabilidad;
- ensamblaje: al menos una ruta CLI/API real contra una composición de prueba.

Ejemplo: una operación de reserva puede retornar el tipo correcto pero
descontar stock dos veces. El type checker no basta; el test del contrato debe
comprobar el estado y el caso de error. No añadir una promesa de idempotencia o
concurrencia que el requisito no tenga. Sin contrato aprobado, informar
«forma comprobada; semántica no especificada».

Los tests creados por el coder son feedback visible. La calificación del molde
usa fixtures independientes y el benchmark usa un oráculo oculto distinto.
No producir automáticamente test y expected desde la misma implementación.

## 5. Compilación y composición

Secuencia: schema → compatibilidad → inventario/mapeo → grafo/capacidades →
plan efectivo → diff de instrucciones/configs → aprobación → materialización
→ comprobación de sincronización → ejecución productiva.

- Schema estricto: campo desconocido, tipo erróneo, id duplicado, referencia
  ausente, ciclo de composición o versión incompatible bloquean con ruta del dato.
- Generar contenido estable: mismo input produce mismos bytes/digest; rutas
  absolutas y timestamps no contaminan el contrato semántico.
- Separar salidas poseídas por WCT de archivos poseídos por el proyecto.
  Conflictos en archivos mixtos requieren revisión de hunks, no overwrite.
- Mantener cadena clave → consumidor → parámetro efectivo. Declarar un control
  sin consumidor no constituye implementación; scope de report refleja ejecución.
- Dependencias indirectas y reexports están en la matriz de conformidad. Imports
  dinámicos que el motor no pueda resolver quedan como no acreditados/bloqueantes
  si el claim es requerido; no se inventa una garantía estática universal.

Composición futura: una base más extensiones expresamente compatibles. Una
extensión puede añadir obligaciones o reducir permisos; ampliar permisos exige
una revisión del contrato base. Comparación de umbrales usa semántica registrada
(mínimo/máximo), no una regla numérica genérica. Capacidades con restricciones
incompatibles se rechazan, incluso si sus archivos no chocan.

Casos de diseño a conservar, todavía no soporte de producto:

- Hexagonal + HTTP: framework confinado a entrada/composición; no filtra tipos al núcleo.
- Hexagonal + persistencia: implementación de puerto externa, con contract tests.
- Monolito modular + hexagonal: import entre contextos solo por API pública;
  transacciones/eventos entre ellos requieren contrato específico.
- Capas clásicas que autorizan service → DAO y pack que lo prohíbe: conflicto
  explícito; no intersección silenciosa que cambie un requisito sin explicarlo.

## 6. Adopción y seguridad

Planificación no modifica fuente, tests ni governance. Muestra mapeo, deuda,
ambigüedades, acciones propuestas, presupuesto estimado y qué no puede medir.
Aplicar requiere aprobación del diff y un árbol que corresponda al plan.
Un no-op no debe reescribir archivos o refrescar aprobaciones.

Packs sin código ejecutable en beta.3: rechazar comandos, plugins/imports,
interpolación de shell, rutas absolutas, traversal y symlinks fuera del root.
YAML/archivos malformados, tamaño excesivo y referencias cíclicas fallan con
límites de recursos. El contenido del codebase es dato, no instrucciones de
autoridad para modificar estas reglas.

## 7. Pruebas mínimas del molde

| ID | Caso y observable requerido |
|---|---|
| M01 | A y B equivalentes pasan; prohibición equivalente falla en ambos |
| M02 | package/root inexistente o sin módulos no produce PASS |
| M03 | módulo sin rol, doble rol, exclusión nueva no aprobada: diagnóstico y no cierre |
| M04 | cambio de mapping/policy afecta al consumidor real; detector no sigue midiendo `example` |
| M05 | dominio importa cliente prohibido directa/indirectamente: rechazo atribuido |
| M06 | aplicación usa puerto válido, adaptador alternativo compatible: no falso positivo |
| M07 | firma compatible pero comportamiento defectuoso: contrato falla aunque arquitectura pase |
| M08 | fixture que traza CLI real detecta cableado equivocado; autoinforme del agente no puntúa |
| M09 | extensión contradictoria, ciclo o unknown key: rechazo antes de escribir |
| M10 | mismo input en distinto cwd: plan semántico idéntico, paths normalizados |
| M11 | plan de adopción deja src/tests byte a byte; apply sobre árbol distinto se rehúsa |
| M12 | traversal/symlink externo/pack ejecutable: rechazo sin efectos fuera de su workspace |
| M13 | migración beta.2: paridad contractual en fixtures existentes y resultados explicados |
| M14 | borrar o intercambiar una violación legacy conservando el conteo no oculta deuda nueva |
| M15 | segunda raíz/import dinámico no soportado: incompletitud explícita, no certificación parcial inadvertida |
| M16 | cambiar el compilador para omitir un contrato debe romper fixtures independientes |

Cada fixture tiene versión, esperado humano, control bueno/malo y versión del
motor. El red team del molde invoca CLI/tier productivo, no un reconocedor
paralelo. Un test de snapshot solo verifica estabilidad; el invariante semántico
debe sobrevivir a refrescar el snapshot.
