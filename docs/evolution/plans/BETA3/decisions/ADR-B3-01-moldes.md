# ADR-B3-01 — El molde es un contrato compilable, no una carpeta modelo

> Adenda D0: se recomienda **aceptar con recorte**, sin aprobación presumida.
> [D0 §3](../D0.md) fija una raíz/paquete, A/B, personalAssistant brownfield,
> contenedores y puertos co-localizados. Composición libre queda fuera; el
> caso real requiere revisión de sus diferencias de contrato. La cadena de
> consumidores que debe calificar el molde está en [trazabilidad](../TRAZABILIDAD-D0.md).

Estado: **propuesto**, 2026-09-07. No autoriza código ni configuración protegida.
Motivación: [F01–F03/F07](../RESEARCH.md). Detalle: [SPEC-B3-01](../specs/SPEC-B3-01-moldes.md).

## Decisión recomendada

Un molde contiene identidad/versionado, roles, relaciones permitidas, políticas
de dependencias, contratos de interfaces, capacidades requeridas, ejemplos y
fixtures de calificación. Una instancia añade el mapeo a módulos reales y las
decisiones del proyecto. Un compilador determinista produce un plan efectivo
del que derivan instrucciones, contratos ejecutables y reporte de alcance.

Separar cuatro dimensiones evita una explosión de plantillas:

| Dimensión | Ejemplo | No debe decidir |
|---|---|---|
| Base de calidad | tests, integridad, estilo | arquitectura del negocio |
| Patrón arquitectónico | puertos/adaptadores | framework HTTP o reglas de stock |
| Implementación tecnológica | Python y motores disponibles | requisitos funcionales |
| Instancia del proyecto | rutas, símbolos y excepciones aprobadas | rebajar silenciosamente el contrato |

Beta.3 publica **una combinación**: hexagonal + Python. Una traducción de
compatibilidad representa el perfil beta.2 sin declararlo otro patrón nuevo.
La posibilidad de describir futuras combinaciones no implica que estén
calificadas o disponibles.

## Reglas del molde

- El grafo describe dependencias de código, no dirección de llamadas en runtime.
  La aplicación puede invocar un puerto implementado por un adaptador sin
  importar el adaptador concreto.
- Los roles no exigen nombres de carpetas. `core/usecases` puede mapearse a
  aplicación; `infrastructure` puede mapearse a adaptadores de salida.
- Todo módulo del scope debe tener una disposición única: rol o exclusión
  aprobada con motivo. Un mapeo ambiguo o vacío impide acreditar conformidad.
- La composición es explícita. Una extensión no puede abrir una dependencia
  que el patrón base prohíbe. Conflictos se muestran con las dos procedencias;
  no hay «último YAML gana».
- Las obligaciones se acumulan; permisos efectivos se restringen. Un cambio que
  amplía permisos requiere nueva decisión/versionado, nunca un override oculto.
- Los packs contienen datos y ejemplos; no hooks de shell, imports de plugins,
  descarga de código o autoedición de governance durante validación.

## Alternativas descartadas o diferidas

| Alternativa | Motivo |
|---|---|
| Solo más instrucciones al LLM | No detecta incumplimientos ni drift; útil como brazo experimental, no como contrato |
| Scaffold que copia una arquitectura completa | Sirve para arranque, pero se desactualiza y obliga a deformar repos existentes |
| Un molde por cada combinación framework/arquitectura | Mantenimiento y pruebas combinatorias antes de validar valor |
| DSL general de arquitectura y motor de imports propio | Import Linter y analizadores existentes ya cubren parte; recorrer MIN-001 primero |
| Deducir arquitectura por nombres y aplicarla automáticamente | Puede clasificar mal; inventario asistido necesita confirmación humana |

## Consecuencias

Beneficios esperados: menos decisiones arbitrarias para el modelo, invariantes
consistentes y migración revisable. Costes: schema, compilación, compatibilidad y
calificación del propio molde. No se atribuye corrección semántica al grafo.

La extensión modular-monolith + hexagonal por contexto queda como siguiente
candidato: exige reglas entre contextos y sus APIs, no repetir restricciones
internas N veces. DDD, CQRS y event-driven no son capas intercambiables que se
puedan apilar sin resolver contratos transaccionales y de consistencia.

## Evidencia exigida para aceptar esta decisión

Dos layouts equivalentes pasan el mismo contrato; import inválido, módulo
huérfano y combinación contradictoria fallan por su causa; una alternativa
válida no necesita copiar el ejemplo. El plan compilado y los consumidores
efectivos coinciden al variar cada campo activo del molde.
