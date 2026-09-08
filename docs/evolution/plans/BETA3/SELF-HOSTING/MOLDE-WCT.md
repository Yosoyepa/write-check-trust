# Molde local `wct-harness-local/1`

Estado: **contrato de diseño, no configuración ejecutable existente**. Aplica
a las piezas nuevas de evidencia; no reclasifica silenciosamente el legacy.
El pack público `hexagonal-python/1` conserva su especificación en
[SPEC-B3-01](../specs/SPEC-B3-01-moldes.md).

## 1. La pieza que queremos fabricar

Para WCT el negocio es decidir **qué afirmaciones soporta una evidencia**, con
qué alcance y qué causas impiden aceptarla. El negocio no es «obtener exit 0».
Una pieza tiene ID, contrato versionado, entradas/salidas, dependencias,
propietario, pruebas discriminadoras y límites de uso. Un molde define cómo
esas piezas se conectan; no escribe por sí mismo la lógica correcta.

## 2. Roles lógicos y límites de importación

| Rol | Puede depender de | No puede hacer |
|---|---|---|
| Contratos/datos puros | stdlib de tipos, dataclasses, colecciones y otros datos puros | leer disco/env/reloj/red; ejecutar procesos; cargar config global |
| Decisión pura | contratos/datos puros y otras decisiones puras acíclicas | conocer pytest, GateResult histórico, CLI, LCOV global o estado del repo |
| Aplicación de evidencia | decisiones, contratos y puertos de IO que consume | importar adaptadores concretos para crearlos implícitamente |
| Adaptadores de frontera | contratos/puertos, biblioteca necesaria para esa frontera | decidir a escondidas la aceptación global; filtrar objetos de framework al núcleo |
| Composición/CLI | todos los anteriores para ensamblar | duplicar reglas/expected, ejecutar shell desde texto o inventar defaults de seguridad |
| Legacy explícito | APIs existentes enumeradas y caracterizadas | ser una excepción abierta para que cualquier módulo nuevo importe cualquier cosa |

P01 no necesita puertos ni una carpeta por rol: un módulo puro con su API y
sus datos es suficiente. La validación estructural de los argumentos ocurre
en su frontera pública; las reglas de reconciliación son puras. No introducir
una interfaz de una sola implementación sin frontera de IO real (MIN-007).

`open`, lectura de entorno, reloj, random, importación dinámica, red, subprocess,
`eval`/`exec` y salida por stdout son efectos prohibidos en P01, aunque no
aparezcan como imports. Un linter de imports no demuestra pureza general.
Revisión de flujo y pruebas de efectos complementan la comprobación estática.

## 3. Mapa de módulos previsto, no árbol que haya que crear hoy

| Módulo candidato | Papel y dueño del comportamiento | Introducción |
|---|---|---|
| `tools/wct/evidence/identities.py` | contrato puro de tres inventarios; P01 fija la API | P01 |
| `tools/wct/evidence/inputs.py` | tipos/snapshot y adaptador explícito de enumeración; separar si cruza límites o crece | P02, especificación de API propia antes de código |
| `tools/wct/evidence/workspace.py` | propiedad/exclusión/symlinks de outputs | P02 |
| `tools/wct/evidence/pytest_capture.py` | adaptador de colección y fases reales, argv/exits; consume P01 | P03 |
| `tools/wct/evidence/artifacts.py` | pertenencia y completitud de artefactos; reutiliza validación LCOV | P04 |
| `tools/wct/evidence/closure.py` | reglas puras de cierre/capacidades y causas simultáneas | P05 |
| `tools/wct/evidence/engine.py` | caso de uso compuesto mediante dependencias explícitas | P06 |
| `tools/wct/cli.py` | wiring opt-in; bytes/exits previos intactos | P06, no P01 |

Son ubicaciones candidatas posteriores a P01, no permiso para crear esqueletos
vacíos. No crear ahora engine, registry, decorators ni jerarquía de plugins.
Cada siguiente pieza debe fijar su API y diff antes de delegarse.

## 4. Qué se reutiliza y qué debe adaptarse

| Fuente existente | Reuso | Límite que no se puede esconder |
|---|---|---|
| `model.GateResult`, `Status` | embebidos sin cambiar sus seis campos | no almacenan el protocolo completo de ejecución |
| `gate.checks.coverage_total_command` | receta y argumentos canónicos | salida privada de P1 requiere parámetro opt-in y tests de paridad |
| `ratchet.measure.check`, validadores LCOV | comparación aditiva, umbrales y defectos ya corregidos | LCOV está ligado a ruta histórica; no copiar un archivo privado allí como atajo |
| `util.git` | HEAD/estado cuando aporten contexto | no inventario completo de inputs nuevos/ignorados; P02 lo especifica |
| `mutate.verdict.classify_inventory` | referencia de conservar causas e identidades | consume reporte de mutmut; no sirve de reconciliador P01 ni de prueba fresca |
| `dry.parse_tree` y analizadores actuales | AST/diagnóstico si su contrato aplica | no añadir copia de helpers ni fingir que analizan roles nuevos |
| `accept.parse_feature`, `ir_dry` | gramática/duplicación de escenarios aprobados | no ejecutan negocio ni terminales por fila |
| `rules`, `adopt`, `archmetrics`, `wire` | lifecycle/consumidores futuros del plan efectivo | muchas rutas/nombres actuales corresponden a `example`; requieren adaptación P07/P08 |

## 5. Contrato del futuro molde de producto

El plan efectivo debe resolver, con versión/digest: instancia, roots/paquetes,
roles por módulo, aristas permitidas, dependencias prohibidas, puertos y
bindings, exclusiones con motivo/identidad, capacidades y consumidores.

Invariantes mínimos heredados de SPEC-B3-01:

- Cada módulo tiene disposición total, incluyendo contenedores/imports y
  archivos nuevos; sin «no clasificado pero verde».
- Un conflicto de roles/dependencias se rechaza con causas, no con último
  archivo gana o valores por defecto permisivos.
- La misma instancia normalizada alimenta instrucciones y motores. Cambiar
  una regla debe cambiar un resultado en una fixture discriminadora.
- Mapeo por arquitectura real, no por nombre de carpeta. Los dos layouts
  equivalentes producen la misma decisión de conformidad.
- Instrucciones y nombres de símbolos derivados de código vigente; cualquier
  referencia no resoluble se marca desconocida. El contexto no incluye el oráculo.
- Un puerto exige contrato conductual y ruta ensamblada; `Protocol` solo
  acredita compatibilidad estática parcial.
- Ningún pack ejecuta hooks arbitrarios. Versiones/digests/procedencia y
  migración revisable antes de distribuir moldes ajenos.

Para el harness, no fingir que `tools/wct` ya satisface el pack hexagonal
estricto del ejemplo. Empezar con el perímetro P01/P02 y registrar cualquier
legacy que se importe. La ampliación de scope o promoción a enforcement global
es otra decisión, no una reparación cosmética del código para obtener verde.

## 6. Verificación del molde local

Ahora: revisión arquitectónica sobre el diff y comprobaciones explícitas del
perímetro. P01 solo permite imports stdlib; un import a CLI, pytest o runner es
un negativo inequívoco. Medir efectos, tipos, complejidad y cobertura del módulo
real, sin inferirlos del análisis de `src/example`.

Después: P07/P08 materializan los checks y los calibran con soluciones válidas,
arista invertida, import transitivo/alias, contenedor con efecto y módulo sin
clasificar. Mientras no estén instalados no escribir «G-ARCH verifica este
molde». La limitación de imports dinámicos permanece publicada.
