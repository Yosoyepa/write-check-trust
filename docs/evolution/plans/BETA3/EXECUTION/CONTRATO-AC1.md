# AC1 — aceptación con evidencia causal mínima

2026-09-08. Contrato aprobado por arquitectura bajo D1 y la autorización
humana posterior al piloto: «si autorizo» y «vale continua». Se autoriza
implementar este incremento; no bless, release, exclusiones ni bajar umbrales.
Base: `932c835ac0eeb75010ec7a1071315b1c51f78eb6`. P02a R3 queda intacto.

## Decisiones y alcance

Cerrar primero baseline, causas y transporte productivos. No desarrollar aquí
los 42 handlers P02a, un clasificador automático de equivalencias ni P03/P06.
Los operadores históricos se conservan salvo el cero numérico: se cambia a
`1`, no a `0__mutated`, para no romper el léxico numérico. Esto no acredita
validez semántica de toda mutación; sobreviven los valores equivalentes y
los rechazos no semánticos bloquean. No reutilizar IDs adjudicados de otro IR.

Reuso: parser, IR-dry, generación y enumeración existentes; pytest ya instalado.
La rutina histórica no tiene baseline, timeout ni diagnóstico causal. No hay
ejecutor acotado reusable en main. No depender de los módulos P02a sin integrar.
`pipeline.py` tiene 259 sitios estimados: se convierte en fachada preservando
imports públicos. Parser/IR-dry/generador se mueven sin cambio de comportamiento;
`parse_feature` tiene 95 sitios y su módulo debe permanecer dentro de 100.
La sonda radon mide CC25 en parse_feature y CC11 en ir_dry. Por ello se
autoriza partición interna en helpers cohesionados dentro de los módulos
asignados, precedida por caracterización, preservando comportamiento y API:
no basta trasladar deuda a archivos nuevos. Se mantienen rechazo de narrativa
actual (issue #35), diagnósticos/líneas, Background, tipos Outline, orden y
contenido del IR. Si la partición requiere más rutas, proponerlas antes.

## Protocolo por intento

`run_mutations(ir, command)` conserva su interfaz de dos argumentos. Cada
campaña crea directorio exclusivo persistente bajo `build/tmp/wct-accept-*`;
conserva IR original, mutados y logs. No borrar parciales ni usar /tmp. No
escribir manifests, política o tests generados desde esta función.
La API conserva el cwd del invocador, igual que antes: build/tmp se resuelve
desde ese cwd y tanto baseline como mutantes ejecutan allí. El expediente
registra el cwd efectivo y las rutas de protocolo son absolutas. La invocación
de calificación se hace desde la raíz del checkout. La diferencia histórica
del CLI (accept run pasa cwd=root, accept mutate no) no se corrige aquí;
no afirmar soporte nuevo de invocación CLI desde subdirectorios. Resolver
find_root obligatoriamente en esta API rompería runners que operan sobre
directorios temporales sin gobernanza y excedería esta frontera.

Primero ejecutar el comando una vez con el IR original explícito. Inyectar
`WCT_ACCEPT_IR`, `WCT_ACCEPT_RECEIPT`, `WCT_ACCEPT_ATTEMPT_ID` (nonce nuevo),
`WCT_ACCEPT_IR_SHA256` y `WCT_ACCEPT_PHASE` (`baseline`/`mutation`). No heredar
esos valores del host. Protocolo cooperativo, no autenticación frente al runner
malicioso del mismo UID. El recibo obliga a procedencia declarada/completitud;
no demuestra por sí solo ejecución de cada fila Gherkin ni ausencia de plugins.

Recibo JSON UTF-8, objeto de claves exactas:

```json
{"schema_version":1,"attempt_id":"nonce","ir_sha256":"64hex","exit":0,"cases":[{"scenario":0,"status":"pass"}],"errors":[]}
```

Tipos exactos, no bool como int; schema=1; nonce/hash coinciden con el intento
y los bytes del IR conservado. cases contiene exactamente una entrada por
índice de Scenario del IR, sin omisión, duplicación o extra. status pertenece
a pass/mismatch/error. errors es lista de strings no vacíos. No claves extra,
duplicadas ni NaN. Max 1 MiB de recibo; symlink/no regular/ausencia/JSON roto
o identidad incorrecta → instrumento inválido. No aceptar recibo previo.

Combinaciones válidas: todos pass + errors vacío + exit0 = pass; al menos
un mismatch, ningún error, errors vacío + exit1 = mismatch. Cualquier status
error, errors no vacío, exit2+, señal o contradicción = invalid. El exit del
recibo debe ser el observado. Un mismatch junto a error NO es killed.

Sin casos del IR, un recibo vacío no acredita trabajo: cero mutaciones
continúa bloqueado por TEST-010. No degradar fallos de baseline a «sin datos».

## Ejecución acotada y resultado de campaña

30 s máximos por intento, 600 s para campaña; 1 MiB combinado stdout/stderr.
Topes operativos iniciales del nuevo transporte, no cambio de thresholds.
Popen sin shell, grupo de proceso propio en POSIX. Timeout o exceso: terminar
grupo y recolectar hijo directo; guardar causa y captura parcial acotada.
No prometer contener procesos que escapen deliberadamente de la sesión.
TMPDIR y PYTEST_DEBUG_TEMPROOT apuntan al directorio privado de cada intento
para productores cooperativos de temporales; no es una jaula del filesystem.
Incluso si el presupuesto vence antes de lanzar un intento, conservar su
attempt.json con identidad, argv, cwd y razón, y logs vacíos. Un comando
vacío se reporta como error de lanzamiento, no traceback sin reporte.
Error de lanzamiento, señal, import, colección, setup/teardown, skip/xfail,
recibo incompleto o desconocimiento del lenguaje nunca cuentan como killed.

Baseline inválido/mismatch: cero mutantes lanzados, todos not_run, fallo con
causa. Baseline sano: recorrer inventario estable de `mutations(ir)`; cada
resultado incluye id consecutivo, scenario/row/field/from/to del operador,
status killed/survived/error/not_run, exit observado o null y razón.
mismatch válido → killed; pass válido → survived; invalid → error y parar;
restantes → not_run. Mantener baseline separado de todos los contadores.

Reporte versionado con baseline, results, planned, killed, survived, errors,
not_run y directorio de evidencia. Las cuatro cuentas suman planned, coinciden
con results y sus identidades/metadata con la enumeración independiente del IR.
`accept_verdict` valida esas invariantes, no solo confía en totales del caller.
Reportes históricos incompletos dejan de aprobar: cambio deliberado de
seguridad, sin modo legacy que perpetúe el falso verde. Mensajes nombran causa.
Solo baseline sano, trabajo >0, killed=planned y cero survived/errors/not_run
permite aprobar. Los escenarios sin Examples conservan advertencia vacuous.

## Adaptador pytest y compatibilidad del ejemplo

Para el runner pytest existente, cargar plugin propio mediante PYTEST_PLUGINS
en el entorno del hijo (conservar plugins declarados; no ocultar su error).
Plugin inactivo sin las variables del protocolo; no modificar corridas normales.
Verificar colección exacta de nombres que produce generate para los escenarios,
sin duplicados ni extras; conservar nodeids observados. No inferir cobertura
por nombre: es identidad contractual, no prueba contra suplantación del runner.
Registrar setup/call/teardown; skip, xfail, error de colección/interno o fase
no completada → errors. Un fallo de call cuenta como mismatch SOLO cuando su
excepción es `SemanticMismatch`, tipo público nuevo derivado de AssertionError.
Para cumplir N818 sin supresiones, el nombre concreto de la clase puede ser
`SemanticMismatchError`, exportado también como `SemanticMismatch` (alias del
mismo tipo, no wrapper). Imports, raise, except e isinstance por el nombre
contractual se conservan; los diagnósticos de tipo muestran el nombre concreto.
AssertionError genérico, error de import o missing handler → error. Emitir
recibo al cierre con el exit real; la campaña valida también el exit externo.

`tests/acceptance/steps.py`: Then compara unidades reales y lanza
SemanticMismatch al diferir. InsufficientStockError en la llamada productiva
significa que falló la reserva exitosa esperada: mismatch tipado. ValueError
solo se traduce en la rama quantity<=0 de esa llamada, nunca desde parsing o
setup; los demás errores se propagan como instrumentales. Un paso desconocido
no lanza SemanticMismatch. No editar dominio/aplicación para facilitar tests.

CLI actual sigue usando sus imports y comando pytest. Un --runner propio debe
emitir el recibo; exit1 sin él ya no pasa. Documentar migración, sin afirmar
compatibilidad de un protocolo que antes no existía. Generate sigue siendo
la única herramienta que escribe su archivo generado, si hiciera falta.

## Pruebas y Gherkin aprobados

Además de las unitarias negativas por cada campo/invariante y procesos reales,
crear este feature verbatim y un ejecutor semántico focal de tests. Sus fixtures
lanzan runners de proceso deliberados; el oráculo observa la campaña real,
no compara la tabla consigo misma. El binding no reemplaza estas ejecuciones.

```gherkin
Feature: Evidencia causal de mutacion de aceptacion
  Scenario Outline: Distinguir comportamiento de fallos del ejecutor
    Given un ejecutor con baseline "<baseline>" y mutante "<mutation>"
    When ejecuto una campana con "<planned>" mutacion
    Then el veredicto es "<verdict>" con "<killed>" killed y "<errors>" errores
    And quedan "<survived>" supervivientes y "<not_run>" sin ejecutar
    Examples:
      | baseline | mutation | planned | verdict | killed | errors | survived | not_run |
      | pass | mismatch | 1 | pass | 1 | 0 | 0 | 0 |
      | mismatch | mismatch | 1 | fail | 0 | 0 | 0 | 1 |
      | pass | pass | 1 | fail | 0 | 0 | 1 | 0 |
      | pass | missing_receipt | 1 | fail | 0 | 1 | 0 | 0 |
      | pass | wrong_identity | 1 | fail | 0 | 1 | 0 | 0 |
      | pass | mixed_error | 1 | fail | 0 | 1 | 0 | 0 |
```

Control sano y mutante real del ejemplo deben pasar la campaña; P02a unknown
handler original debe fallar baseline y lanzar cero mutantes. Probar errores
que ocurren SOLO después de baseline: import, crash, señal, salida excesiva,
timeout y pytest teardown con mismatch simultáneo. No llamar killed al doble
roto. Compleción/nombres/IR/nonce/contadores alterados deben bloquear.
Probar runner custom válido y uno que ignora IR; este último no logra matar
mutantes por ignorarlos. Golden de receipt literal independiente y controles
válidos alternativos. Preservar rojo anterior al fix y colección real.

## Frontera y entrega

Solo estos archivos de producto/test (se autorizan módulos separados por
cohesión y para respetar 100 sitios; no crear más sin revisión):

- tools/wct/accept/pipeline.py (fachada), parsing.py, ir_checks.py, generation.py;
- tools/wct/accept/mutation_cases.py, campaign.py, receipt.py, process.py;
- tools/wct/accept/pytest_receipt.py, semantic.py, verdict.py;
- tools/wct/accept/receipt_validation.py y verdict_validation.py: validación
  pura separada del transporte JSON y del inventario/dictamen respectivamente;
- tests/acceptance/steps.py, campaign_steps.py, protocol_runner.py;
- tests/unit/test_accept_pipeline.py, test_accept_verdict.py,
  test_accept_campaign.py, test_accept_receipt.py, test_accept_pytest.py;
- features/wct-acceptance-evidence-001.feature;
- tests/acceptance/generated/test_acceptance.py solo regenerado por herramienta.

Fuera: CLI, P01/P02, governance, workflows, dependencies, reglas, baselines y
bless. Fuentes nuevas/cambiadas <=100 sitios, CC/CRAP existentes sin relajar.
Temporales exclusivos bajo build/tmp; sin sync/instalación del runtime compartido.
Handoff propio nuevo SELF-HOSTING/runs/HANDOFF-B3-MA-AC1-R0.md. No commit/push del
coder; root integra tras revisión. Campaña asistida, coste unavailable.

Primero test rojo, luego implementación; independiente revisa. Gate default
src no califica estos módulos: medición focal y reporte de alcance obligatorios.
La calificación de mutación de fuentes conserva sus reglas; autorización P02a
no aplica a nuevas fuentes AC1. Ante contradicción, parar antes de improvisar.

### Ajuste de frontera durante implementación

Arquitectura autoriza las dos rutas de validación anteriores tras la medición
preliminar del coder (receipt 105 sitios, verdict 151). La separación sigue
responsabilidades distintas; no mueve código fuera del alcance de calificación.
Ambos módulos nuevos se incluyen en mutación, cobertura y revisión. El borrador
campaign con 101 sitios y las complejidades históricas del parser/IR-dry siguen
requiriendo corrección: esta autorización no concede excepciones a límites.
