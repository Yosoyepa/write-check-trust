# SH-P07–P09 — Moldes ejecutables, consumidores y adopción

Fecha: 2026-09-07. Base inspeccionada: `46669278ece7e3b7cc8059a5eff9ae27c2735284`.
Estado: auditoría estática y propuesta de contratos, **no implementación ni
aprobación de Gherkin**. Autor: subagente de arquitectura, revisión de moldes.
Único archivo editado por esta subtarea: este documento. No se consultaron otros
repositorios, modelo, cuentas ni proveedores.

Precedencia: [PIEZAS](../SELF-HOSTING/PIEZAS.md),
[ENTREGA-v2](../SELF-HOSTING/ENTREGA-v2.md),
[MOLDE-WCT-v2](../SELF-HOSTING/MOLDE-WCT-v2.md),
[SPEC-B3-01](../specs/SPEC-B3-01-moldes.md),
[SPEC-B3-02](../specs/SPEC-B3-02-evidencia-contexto.md) y
[TRAZABILIDAD-D0](../TRAZABILIDAD-D0.md). P07 productiva comienza después de P06
calificado; preparar sus contratos no sustituye esa dependencia. Terminar P01–P06
no satisface el alcance de producto comprometido para beta.3.

## 1. Hallazgos con causa y consecuencia

Las rutas y líneas siguientes corresponden a la base inspeccionada; un cambio
posterior exige volver a comprobarlas. «Existente» significa lectura de código,
no ejecución de las matrices futuras.

| ID | Evidencia concreta | Consecuencia para el siguiente contrato |
|---|---|---|
| MA-01 | `tools/wct/archmetrics/analyzer.py:123` toma `source[0]` y concatena el paquete punteado como directorio; `:160` clasifica por segundo segmento | Cambiar solo policy no soporta otro layout. P07 debe descubrir módulos por identidad y P08 consumir la clasificación, no repetir heurísticas |
| MA-02 | `tools/wct/wire/engine.py:35` reconoce nombres físicos; `:159` solo domain/application; `:177` omite SyntaxError | Un layout B puede perder controles sin rojo. Inventario/errores de parseo deben dominar el cierre nuevo; conservar la vía histórica hasta probar compatibilidad |
| MA-03 | `tools/wct/rules/engine.py:16` renderiza textos YAML; `:35` enumera destinos de proveedores. `.importlinter:2` fija `example`; `tools/wct/gate/runner.py:374` ejecuta `lint-imports` sin config del plan | `rules build` no compila hoy policy a Import Linter. Hace falta productor y consumidor de configuración efectiva, con prueba semántica; texto sincronizado no basta |
| MA-04 | `tools/wct/gate/runner.py:368` usa mypy sobre tools/src; `:375` fija first-party example/tools; `pyproject.toml:80` fija paquetes mypy; `:89` fija mutmut src/example | Declarar scope no cambia ejecución. El nuevo perfil debe fijar argumentos/config reales para tipos/dependencias y declarar mutación limitada, no ampliar source_paths por conveniencia |
| MA-05 | `tools/wct/config.py:26` exige un mapa YAML y `:40` schema 1; no valida todas las claves/tipos ni duplicados antes de safe_load | Reutilizar lectura de bytes y formato, no asumir schema estricto. Pack/instancia necesitan contrato propio que rechace claves desconocidas, IDs duplicados y referencias inválidas |
| MA-06 | `tools/wct/gate/capabilities.py:19` almacena tools/scope declarados; `tools/wct/gate/checks.py:215` compara **cantidad** de zonas con baseline | Metadata no es medición; igual número de hallazgos no implica igual deuda. P09 necesita IDs de deuda y cambios observados sin reescribir los ratchets legacy |
| MA-07 | `tools/wct/adopt/__init__.py:12` cuenta extensiones y propone src/app/lib; `tools/wct/adopt/lifecycle.py:23` escribe lock; `:240` produce patch | Hay inventario/lifecycle reutilizable, no clasificación de roles, debt ledger ni apply. `adopt plan` nuevo no debe invocar lock/sync para fingir lectura pura |
| MA-08 | `tools/wct/adopt/lifecycle.py:255` usa destino `out` y escribe; `tools/wct/cli.py:171` lo ofrece como patch destination | Esa libertad de destino pertenece al contrato histórico y no se declara aquí un defecto confirmado. No es una frontera de escritura reutilizable para packs no confiables: el plan nuevo requiere cero escrituras y materialización con propiedad explícita |
| MA-09 | `src/example/application/reserve_stock.py:8` co-localiza Protocol y caso de uso; `:22` reserva y persiste. `src/example/adapters/memory_inventory.py:6` solo implementa memoria | El contrato beta.2 no es idéntico al grafo de seis roles. No reclasificar todo el módulo mixto como ports, ni autorizar adapters.out→application por ocultar un símbolo de puerto |
| MA-10 | `tests/unit/test_reserve_stock.py:6` prueba una reserva persistida en memoria; `tests/integration/test_cli.py:6` invoca main real. No hay segundo adapter en src/example | Reusar estos consumidores y ampliar calificación observable; una segunda implementación de fixture prueba sustitución, no soporte productivo de SQLite |
| MA-11 | `tools/wct/accept/pipeline.py:188` genera un test por escenario; `tests/acceptance/steps.py:14` itera filas, y `:23` solo entiende stock del ejemplo | Añadir features de molde no acredita ejecución de filas. Cada pieza debe conectar sus contract tests/terminales a P03, conservar binding completo anunciado y rechazar handler faltante |
| MA-12 | `tools/wct/cli.py:195` reconoce solo lock/check/sync al normalizar `adopt <ruta>` | Añadir parser de `adopt plan` sin actualizar esta ruta lo convertiría en inventario de una carpeta llamada plan. La compatibilidad debe probar ambas invocaciones |

No se propone un segundo motor general de imports, un framework de plugins ni
un generador de negocio. Se conservan Import Linter, lectores AST existentes,
rules engine, lifecycle, GateResult, P01 y las piezas P02–P06 calificadas.

## 2. Contrato de entrada/salida que debe cerrar el arquitecto

### 2.1 Unidad mínima y límites

Producto inicial: un pack **hexagonal-python/1**, Python y un paquete regular
por instancia; dos layouts calificados. Perfil de compatibilidad beta.2 separado,
sin presentarlo como segunda arquitectura. Sin composición libre, código en
packs, descarga de plugins, namespace packages ni selección silenciosa de la
primera raíz de un monorepo. Una capacidad requerida no soportada impide cierre.

La primera instancia de autohardening selecciona explícitamente los módulos de
`tools.wct.evidence` que existan tras P06, más sus contenedores/imports necesarios.
Su lista se congela entonces; no se aprueba hoy «todo tools». El perfil local de
desarrollo conserva su nombre y límites: no recibe certificado hexagonal por
estar escrito en Markdown. Roles puros, IO y ensamblaje se mapean desde los bytes
finales; no requieren renombrar carpetas ni reclasificar módulos mixtos.

Entrada del compilador: bytes del pack fijado, instancia revisada, inventario
de snapshot P02, capacidades disponibles y versiones efectivas. Salida: un plan
inmutable/determinista con disposiciones exhaustivas y hallazgos. Compilar no
ejecuta código del proyecto ni escribe source/tests/governance. El plan no es
todavía una acreditación: los consumidores producen sus resultados después.

### 2.2 Campos, responsable y consumidor obligatorio

Nombres exactos/API/exits se fijarán en SPEC-P07 antes del coder. Esta tabla
define qué debe significar cada campo y quién debe consumirlo, no un schema
actual. Para cada fila activa habrá cambio bueno/malo y efecto observable.

| Campo del contrato | Responsable que lo fija | Consumidor productivo requerido / comprobación |
|---|---|---|
| schema, pack id/version/digest y compatibilidad | arquitecto + mantenedor del pack | cargador estricto: identidad/versión exactas; bytes distintos o motor incompatible no continúan |
| licencia/procedencia | mantenedor | validador de metadata y reporte de procedencia; no afirmación de seguridad por tener licencia |
| source_root, package y snapshot digest | instancia aprobada | inventario sin imports y todos los productores del perfil; conjunto vacío, raíz extra o cambio invalidan |
| rol por prefijo + particiones explícitas | arquitecto/adoptador | clasificador total, generador Import Linter, métricas/wire/contexto; ambigüedad no se resuelve por orden YAML |
| contenedores, __init__, exclusiones por capacidad | adoptador con motivo aprobado | inventario conserva esos módulos/reexports; exclusión de una medición no exime imports/otras obligaciones |
| aristas internas permitidas/prohibidas | pack fijado | configuración efectiva Import Linter y análisis por roles; cambiar arista cambia el resultado del motor |
| externos permitidos/prohibidos/review por rol | pack + dependencias declaradas | análisis de imports/wire y comprobación de dependencias; desconocido no dispara instalación |
| ciclos y agrupación de métricas | pack/instancia; sin alterar umbral legacy | analizador sobre módulos del plan; deuda por ID, no certificar por cantidad de zonas |
| capacidades requeridas, motor/versión, unidades y límites | perfil revisado | ensamblaje P06/P05: consumidor ausente/unidades faltantes no permite accredited; aliases no duplican claims |
| puertos/símbolos y contrato observable | specifier | extracción AST/mypy y suite de contrato por adapter; solo firma no satisface semántica |
| outputs propuestos/ownership y hashes | arquitecto + usuario del repo | materialización separada: revisar diff, preservar archivos mixtos y rehusar inputs obsoletos |
| deuda aceptada: regla, módulo/arista/símbolo, owner, issue real y revisión | humano adoptador | comparador de identidades en shadow/check; sustitución a igual N sigue siendo deuda nueva |
| tarea, allowlist, símbolos/versiones, ejemplos públicos, límite de contexto | arquitecto | generador de paquete de tarea desde plan/snapshot: referencias comprobables, sin holdout ni truncación silenciosa |
| plan/candidate/context/artifact digests y actor | productores + reviewer | envelope P06 y recibo sh-delivery/2, con inventario independiente y atribución de corridas |

No aceptar campos ejecutivos sin consumidor ni reinterpretar metadata como
capacidad. Una clave desconocida se rechaza; una capacidad soportada parcialmente
publica su límite y no satisface una obligación más fuerte.

## 3. PRs candidatas pequeñas y dependencias

Son etiquetas de planificación, no PRs remotas ni autorización de modificación.
Las rutas son fronteras **previstas**, listas que se cierran antes de cada encargo;
no comodines de escritura. Cada PR agrega su SPEC/GHERKIN/DoD al expediente de
la pieza y registra hash del paquete aprobado. Los escenarios de §4 deben
convertirse a Gherkin literal aprobado, no simplemente copiar estos títulos.

| PR candidata | Depende de | Frontera de producto/tests prevista | Salida verificable |
|---|---|---|---|
| P07a schema y pack fijado | P06 calificado + aprobación SPEC-P07a | nuevos `tools/wct/mold/__init__.py`, `schema.py`, `packs/hexagonal-python-v1.json`; `tests/unit/test_mold_schema.py`; `features/wct-mold-schema-001.feature` | schema estricto, sin ejecución/descargas; compatibilidad/digests, límites de recursos y duplicados; pack incluido en wheel/smoke |
| P07b inventario y plan puro | P07a | nuevos `tools/wct/mold/inventory.py`, `plan.py`; `tools/wct/cli.py`; `tests/unit/test_mold_plan.py`, `tests/integration/test_mold_cli.py`; `features/wct-mold-plan-001.feature` | CLI opt-in de plan, totalidad A/B, disposiciones y serialización; cero escritura de proyecto y mismas salidas semánticas en otro cwd |
| P08a imports del plan | P07b | nuevos `tools/wct/mold/imports.py`; `tests/unit/test_mold_imports.py`, `tests/integration/test_mold_importlinter.py`; `features/wct-mold-imports-001.feature` | configuración poseída por run, argv real al motor existente, cada arista aprobada/prohibida efectivamente medida |
| P08b analizadores por roles | P08a | `tools/wct/archmetrics/analyzer.py`, `tools/wct/wire/engine.py`; nuevos `tools/wct/mold/analysis.py`, `tests/unit/test_mold_analysis.py`, `tests/integration/test_mold_analysis_profile.py`; `features/wct-mold-analysis-001.feature` | reutilización de AST/algoritmos sin hardcodes físicos; legacy preservado; parseo incompleto y dinámicos no soportados visibles |
| P08c ensamblaje/instrucciones/scopes | P08a/b | nuevos `tools/wct/mold/run.py`, `render.py`; `tools/wct/rules/engine.py`, `tools/wct/cli.py`; `tests/unit/test_mold_consumers.py`, `tests/integration/test_mold_profile.py`; `features/wct-mold-consumers-001.feature` | mismo plan llega a imports, tipos/deps seleccionados, reporte P06 y contexto de reglas; no reemplazar GateResult/tier legacy |
| P09a contrato de piezas | P08c | nuevos `tests/contracts/test_inventory_adapters.py`, `tests/fixtures/mold_contracts/__init__.py`, `tests/fixtures/mold_contracts/sqlite_inventory.py`, `tests/integration/test_mold_reservation.py`; `features/wct-mold-pieces-001.feature` | misma suite para memoria real y SQLite de prueba; errores/efectos y CLI actual; no agregar producto DB ni cambiar negocio por defecto |
| P09b adopción/shadow/deuda | P08c; P09a antes de calificación final | nuevos `tools/wct/adopt/plan.py`, `debt.py`; `tools/wct/cli.py`; `tests/unit/test_adopt_plan.py`, `test_adopt_debt.py`, `tests/integration/test_adopt_brownfield.py`; `features/wct-mold-adoption-001.feature` | plan no mutante y deuda por identidad; upstream lock distinto de instancia; CLI histórica compatible; preview/revalidación sin apply implícito |
| P09c contexto verificable | P09a/b | nuevos `tools/wct/mold/context.py`; `tools/wct/cli.py`; `tests/unit/test_mold_context.py`, `tests/integration/test_mold_context_cli.py`; `features/wct-mold-context-001.feature` | símbolos/firmas vigentes, límites y comandos reales; cambio en inputs invalida contexto; contrato ambiguo no inventa API |

Si P08b excede tamaño/CRAP/sitios, primero proponer una partición por
responsabilidad en su propio contrato; no incorporar archivos nuevos implícitos.
Los fixtures A/B necesitan un manifiesto de archivos literales cerrado en
SPEC-P07b; pueden materializarse por fixtures de pytest en espacio temporal.
Esa lista aún no existe: es condición de entrada, no libertad del coder para
elegir un caso fácil. No editar baselines, policy, .importlinter, pyproject,
locks o workflows para que estas PRs pasen; si una integración lo requiere,
presentar diff protegido separado y nueva autorización.

La materialización productiva de una instancia no es `adopt sync --force`.
Beta.3 puede entregar plan/diff y revisión humana sin un apply automático,
conforme ADR-B3-04. Debe aclararse en Gherkin qué significa «aplicar plan»:
si se decide entregar apply, necesita PR/contrato propio, ownership, no-op,
drift, conflictos y reversión antes de prometerlo.

## 4. Escenarios discriminantes para calificar el ensamble

### A. Dos layouts equivalentes: esperado por roles independiente

Usar A (`src/shop`) y B (`python/commerce`), con prefijos de SPEC-B3-01; cada
inventario incluye el paquete raíz y contenedores. Tabla esperada escrita por
specifier antes del compilador: aristas/roles, módulos incluidos/excluidos,
contratos y hallazgos esperados. No obtener expected del plan que se evalúa.

| Grupo | Positivo obligatorio | Negativo/control que debe cambiar el resultado |
|---|---|---|
| M01/M04 | application→ports y ports→domain pasan en A/B; layout renombrado conserva veredicto | domain→adapters.out falla en ambos; cambiar solo mapping debe mover consumidor y hallazgo, no seguir midiendo example |
| M02/M03 | roles permitidos vacíos pero inventario total no vacío y único | paquete inexistente/vacío, nuevo módulo sin rol, solapamiento y contenedor perdido impiden cierre; omitir/inserir a N constante se detecta |
| M05/M15 | import relativo/alias/reexport válido calificado | arista prohibida directa e indirecta; dinámico opaco, sintaxis rota, segunda raíz y paquete namespace no calificado no desaparecen como limpio |
| M09/M12 | pack de datos válido con límites, ruta local y lista cerrada | unknown key/ID repetido, digest falso, ciclo/referencia ausente, payload ejecutable, traversal, symlink externo y expansión excesiva rechazan sin escribir |
| M10/M16 | mismo contenido desde otro cwd produce mismo plan semántico | compilador defectuoso omite módulo/regla, reporta scope distinto o reusa plan tras cambio: calificador independiente falla |
| Campos→consumidores | variar una opción permitida altera argv/config/scope efectivo donde corresponde | consumidor ignora el campo aunque JSON/snapshot cambie: test semántico falla; cambiar solo metadata nunca satisface caso |

Para reexports/relativos/TYPE_CHECKING/dinámicos, fijar primero si el claim mide
imports estáticos o dependencias runtime. El analizador histórico omite
TYPE_CHECKING (`analyzer.py:38`); no usar esa decisión como garantía universal de
arquitectura. Import Linter y análisis AST pueden tener scopes diferentes:
declarar el desacuerdo y probar el claim seleccionado, no escoger el motor verde.

### B. Piezas de negocio: encaje y comportamiento

- Caso válido literal: book=10, pen=20, reserva book=3 → retorno book=7,
  lectura posterior book=7 y pen=20; ejecutar la misma suite en memoria y SQLite
  local de prueba. Reabrir SQLite mantiene 7 y 20.
- Fronteras: Q=S deja cero; Q=0 y Q<0 producen ValueError y no cambian stock;
  Q>S produce InsufficientStockError y no cambia ningún producto. Estos tipos
  proceden de `src/example/domain/inventory.py:19`, no de una regla inventada.
- Variantes plausibles: doble descuento (4), retorna 7 sin guardar (10), guarda
  otro producto, pierde datos al reabrir, captura error y persiste parcial. Todas
  tienen forma compatible pero deben fallar por una aserción del contrato.
- Control de tipo: adapter alternativo compatible pasa mypy y suite; una firma
  errónea falla por tipo/contrato, no por import accidental. No asumir que
  conformidad estructural de Protocol valida efectos.
- Ruta real: CLI del ejemplo book 3 --stock 10 imprime 7 y retorna 0. Una
  composición defectuosa que conecta otro caso de uso falla; no puntúa un JSON
  escrito por el candidato sin invocar `src/example/entrypoints/cli.py:10`.
- Producto desconocido, límites de stock inicial, idempotencia y concurrencia
  no se inventan: aprobar contrato o informar fuera de alcance. SQLite es una
  segunda implementación de calificación, no soporte de DB para adoptores.

### C. Brownfield, deuda y contexto

- Snapshot del repo existente incluye tracked/unstaged/new en scope, config,
  scripts y documentos poseídos por el usuario. Plan antes/después deja esos
  bytes e índice Git idénticos; repetir no renueva aprobaciones ni escribe lock.
- Perfil beta.2 mide el mismo contrato de cuatro capas; el perfil hexagonal
  informa diferencias de roles sin renombrar código. Protocol co-localizado no
  excusa una arista prohibida; shadow enumera la decisión pendiente.
- Debt fixture: B={regla R, módulo A→B}; corregir ese hallazgo e introducir
  R,C→D mantiene N=1 pero detecta deuda nueva. Identidad no depende solo de línea
  móvil; incluye regla, módulo, destino/símbolo y contexto estable aprobado.
  Excepción sin owner/issue real o revisión aplicable no se acepta como deuda.
- Contexto extrae Inventory.reserve real del snapshot; eliminarlo, cambiar
  firma/mapping o cambiar contrato invalida el paquete. Un símbolo inventado no
  se publica como existente. Comandos compuestos conservan argv al escaparse.
- Tamaño excesivo, referencia no resoluble y ambigüedad funcional producen
  contexto incompleto con causa; no se truncan obligaciones ni se filtra holdout.
- El repositorio externo personalAssistant quedó como piloto posterior en
  ADR-SH-01: **no se inspeccionó ni calificó en esta subtarea**. WCT como brownfield
  local sirve para autoadopción, pero no sustituye la generalización externa que
  D0 mantiene. Antes de declarar esa condición de beta.3 completa: acceso/scope
  autorizado y SHA externo calificado, o recorte explícito humano de la promesa.

## 5. DoD y decisiones pendientes, sin cierre nominal

Cada PR necesita el recibo sh-delivery/2 antes del código: API/errores/exits,
Gherkin literal aprobado, fronteras cerradas, matriz campo→consumidor y positivos
más negativos. Reviewer diferente del coder verifica sensibilidad sobre bytes
congelados. Los tests de desarrollo no redefinen el calificador del lote.

DoD conjunto P07–P09:

- P06 calificado consumiendo ejecución real; plan e inventario anteceden los
  productores; mismos IDs/config/digests llegan al cierre. Nunca basta leer un
  plan JSON, generar carpetas o hacer que el parser acepte una feature.
- M01–M16 aplicables, E08/E12 de contexto y positivos anteriores ejecutados por
  CLI/consumidores reales; expectativas y denominadores independientes.
- Claim por capacidad: required/observed/excluded/unsupported, versiones y
  límites. Cero métricas requeridas no es éxito; mutación G1b no acreditada se
  conserva limitada, no se gana por terminar el compilador.
- CRAP/cobertura/sitios/DRY medidos explícitamente sobre cada archivo nuevo de
  tools/wct; suite/colección/focal/property separados, sin umbrales relajados.
- Cinco pares alternados de plan, escaneo/contexto y E2E con input/host/locks
  fijados: mediana/rango/N, sin p95 ficticio; techo técnico aprobado antes de
  ejecución. No atribuir mejoras a modelo barato sin lote comparativo.
- Preservación de source/tests/config y compatibilidad legacy; migración/
  reversión ensayadas sobre copias. Pack en wheel y smoke de adopción del SHA
  final; custodia y archivo de evidencias aprobados, no solo hashes en Markdown.
- Diff exacto, revisión/bless humano donde corresponda, CI y post-merge sobre
  SHA integrado. No ampliar listas de archivos ni atribuir aprobación al coder.

Decisiones que debe cerrar el arquitecto con el humano: APIs y Gherkin por PR;
semántica estática/runtime; límites de parser/recursos y latencia; qué capacidades
obligatorias consumen plan; mapping del subconjunto del harness tras P06;
contrato de materialización (solo diff o apply); perfil/alcance brownfield
externo; custodio y retención de evidencia. No son detalles que deba improvisar
el coder. PR #33, issue #35, G1b y el canal beta.2 permanecen en sus carriles:
este análisis no verificó su estado remoto ni los declara resueltos.

## 6. Evidencia ejecutada durante esta subtarea

Se leyeron código, contratos, AGENTS y skills architecture/review/adopt. No se
crearon fixtures ejecutables, no hubo inferencias externas ni pruebas nuevas.
Los motores comunes se coordinaron con el arquitecto para no duplicar procesos
sobre el worktree compartido. Resultados recibidos del arquitecto, no atribuidos
como ejecución propia:

- `lint-imports`: exit 0, 9 archivos / 8 dependencias, 4 contratos kept / 0 broken.
- `wct archmetrics --json`: exit 0, paquetes example.*, sin cycles ni violations;
  adapters/domain pain tolerado por baseline histórico.
- `wct dry --json`: exit 0, candidates=[] / errors=[] / units=3.
- `wct gate --tier commit`: exit 1, 20 PASS / 0 SKIP / G-META-1 FAIL por los
  dos nuevos archivos protegidos P01 heredados de PR #45; G-TEST PASS en
  102671 ms. No hubo código nuevo de P07–P09 en esa corrida.

Estas salidas describen el ejemplo/alcance histórico, **no califican el molde
futuro ni los archivos del harness**. Fast y cierre del worktree quedan en el
acta central del arquitecto. El árbol conserva ese rojo de integridad declarado;
esta subtarea no lo bendijo ni lo corrigió. El aporte es el mapa de
fallos/campos/PRs y sus entradas de aprobación, no un GO de beta.3.
