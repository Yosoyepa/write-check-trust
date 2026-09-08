# P03 — ampliación de sonda: raises, fixtures y wrappers

Actor `p02b_contract`, specifier B3-MA-D. Esta sonda complementa
[PROTOCOLO-P03-PREFLIGHT](PROTOCOLO-P03-PREFLIGHT.md), no lo reescribe ni se
atribuye sus 23 procesos. Lee e informa conducta de pytest instalado; **no
implementa ni aprueba el producto P03**. Contrato propuesto:
[PROPUESTA-P03](PROPUESTA-P03.md).

## Entorno, fuente y ejecución

Python 3.13.14 de `build/tmp/sh-p01-CND-80B8/.venv`, pytest9.1.1/pluggy1.6.0;
Linux local del worktree documental. Cwd:
`/home/jandradeu/Documents/well_code_template/build/tmp/beta3-execution.uW30FJ`.
Fixtures propias exclusivas creadas con apply_patch bajo
`build/tmp/p03-contract-1qkR4A/`. No imports del producto P02a mutable, P02b
inexistente ni ejecución de tests del candidato. No instalar paquetes, leer
cuenta/modelo o cambiar entorno ajeno. Coste económico unavailable.

Fuentes primarias leídas en
`build/tmp/sh-p01-CND-80B8/.venv/lib/python3.13/site-packages/_pytest/`:

| Fuente | SHA-256 | Lectura pertinente |
|---|---|---|
| skipping.py | `cc2102f5f8d19478f91ce77117c109348b8766ae04ebc4b8c33e5f9923e50aee` | 220–325: raises.matches, stash, transformaciones por excepción/fase |
| runner.py | `c8d7fd553c0516f7884502ee0e7954eb5a5b1542f21fcb5c4357500ed2fe1570` | 115–157: setup, call condicionado, teardown, logfinish |
| hookspec.py | `12098571044671c24ed0011e2bb7d94976380265e5734c30f856479482e6f88d` | 600–735: callbacks y primera implementación del protocolo |

Se releyeron completos P02b aprobado `8561047c...`, DECISION-P02b,
PROTOCOLO-P03-PREFLIGHT `16a4d72b...` y normativos P1/PIEZAS/molde/entrega ya
inspeccionados para la tarea. No afirmar soporte para otras versiones.

Comando supervisor:

```bash
UV_PROJECT_ENVIRONMENT=/home/jandradeu/Documents/well_code_template/build/tmp/sh-p01-CND-80B8/.venv \
PYTHONPATH=/home/jandradeu/Documents/well_code_template/build/tmp/beta3-execution.uW30FJ \
uv run --no-sync python build/tmp/p03-contract-1qkR4A/drive.py
```

Capturado con pipefail y tee en output.txt. **Driver exit0**, ocho procesos
pytest secuenciales, timeout15s cada uno; sin reintentos. Los exits de pytest
son datos de los casos, no evidencia de que todos los tests pasaron. Inicio
primer proceso `2026-09-08T03:11:00.576696+00:00`; fin último
`2026-09-08T03:11:03.145457+00:00`. No usar duración de micro-fixtures como
presupuesto del producto; tiempos humanos/CPU de la tarea unavailable.

Cada recibo contiene argv lista, cwd, entorno efectivo cerrado no secreto,
UTC inicio/fin, exit crudo, SHA de eventos/log y eventos completos. Selección:
-m "not property", autoload desactivado, -p observe, -p no:cacheprovider,
config propio mínimo y basetemp nuevo por proceso. El wrapper observador
makereport usa wrapper=True/tryfirst=True; registra también logreport.
Este plugin de laboratorio escribe su propio archivo, no el pipe/supervisor
de producto; el multiplexado ya fue ensayado por el actor anterior.

## Resultados nativos

S/C/T significa setup/call/teardown. wasxfail se observa como presencia, no
como texto inglés. La excepción procede de CallInfo antes de transformar report.

| Fixture | Exit | Observación determinante |
|---|---:|---|
| xfail raises=ValueError, lanza ValueError | 0 | S/T passed; C skipped+wasxfail; raw ValueError; strict activo |
| xfail raises=ValueError, lanza TypeError | 1 | C failed sin wasxfail; raw TypeError; marker activo **no convierte todo fallo en XFAIL** |
| fixture setup ValueError con marker raises matching | 0 | S skipped+wasxfail; C ausente; T passed; test_finish existe |
| fixture teardown ValueError, marker no estricto matching | 0 | C passed+wasxfail (XPASS), T skipped+wasxfail (XFAIL); conserva ambas disposiciones |
| fixture setup pytest.xfail explícito sin marker | 0 | S skipped+wasxfail y raw XFailed; stash null; C ausente; T passed |
| fixture teardown pytest.xfail explícito sin marker | 0 | S/C passed; T skipped+wasxfail; stash null; test_finish existe |
| conftest wrapper no-op + tmp_path | 0 | S/C/T passed sin excepción; archivo temporal leído con mismos bytes; make/log coherentes |
| conftest wrapper cambia assert False a report passed | 0 | S/C/T passed en **ambos make y log**, pero C conserva raw AssertionError; un resumen verde oculta el fallo |

No hubo fallo inesperado del driver/instrumento en esta ampliación. Rojo de
pytest por TypeError es deliberado y permanece registrado. No es TDD de código
P03 inexistente ni revisión independiente: este actor escribió/ejecutó sondas.

## Hallazgo discriminante y decisiones propuestas

**F-P03-07:** makereport y logreport pueden concordar en un falso PASS producido
por un wrapper. La concordancia no sustituye capturar excepción raw ni calificar
qué plugins/hooks alteran el protocolo. La combinación passed+exception_present
se propone como report_inconsistent, conservando ambos reports y causa raw.
Un wrapper no-op válido debe seguir pasando. El caso no prueba que el mecanismo
detecte un plugin malicioso que también altere el observador o su canal; mismo
proceso/UID continúa fuera de la garantía de aislamiento de P1.

**F-P03-08:** XFAIL no se limita a call ni siempre tiene stash activo. Los casos
setup/teardown y pytest.xfail explícito exigen preservar wasxfail y fases sin
fabricar call. La regla de solo tres fases para PASS no debe impedir registrar
un terminal no-PASS completo con setup no-PASS y teardown presente.

**F-P03-09:** no reejecutar raises.matches ni evaluar markers para clasificar.
El runtime ya evaluó esa lógica; volver a llamarla puede tener efectos y cambiar
el resultado. Guardar excepción presente/tipo y xfail metadata limitada; el
report transformado distingue matching (skipped) y mismatch (failed).

Basetemp nuevo funcionó con tmp_path en la fixture positiva. No se ensayó
basetemp preexistente/symlink/carrera ni limpieza en el producto; P03c debe
bloquear preexistencia antes de lanzar porque pytest puede borrar esa ruta.
El callback conftest de prueba fue explícitamente conocido en el laboratorio,
no se aprueba todo conftest del repositorio por esta observación.

## Identidad y custodia

Rutas relativas a `build/tmp/p03-contract-1qkR4A/`:

| Archivo | SHA-256 |
|---|---|
| observe.py | `4d75599cb6b276ac4bf568e428b58d90972748932178bbd24bd0970b9ab44b88` |
| drive.py | `c818f701daec52da3805419fac7bed55e81e54a17f468ae9334e7377b6620fd5` |
| receipts.json | `0945401f7d94e5e55802160ca7c747d1e4c00ab3d05ae21afb74fc130d33004a` |
| output.txt | `8ecd7a1212122c02d1cf2de3bfbe0d9ff8776bde916b0bacaf81194fc78bfc1c` |

Receipts liga cada events/log por hash; no es manifiesto completo de fixtures.
Custodia local-only, sin backup externo garantizado. No borrar parciales ni
basetemps al terminar; los artefactos deliberadamente defectuosos quedan fuera
del producto y de una futura PR salvo decisión de custodia revisada.

## Comprobación documental y pendiente

`check_spec.py` extrajo el Gherkin propuesto y llamó parse_feature/ir_dry
productivos: **exit0, 1 Outline, 20 filas únicas, 0 findings**, captura
spec-output.txt. No generó tests ni ejecutó handlers y no comprueba todavía
todo el binding. El mapa futuro de variantes no es colección ya observada.

Pendientes de aprobación: schema/tipos P03a, alcance exacto de plugin profile
y callback ordering P03b, runtime+receta P04/P06 y presupuestos conjuntos P03c.
No se escribió producto ni hubo commit/push, bless o cambio de versiones.
No se adjudica ahorro/calidad del modelo a ocho microprocesos de laboratorio.

## Addenda — separación P03a y rechazo del framing verbose

El arquitecto pidió cerrar el kernel puro por separado, sin condicionar su
implementación a aprobar todos los plugins o P04. La propuesta inicial de
veinte familias nativas se conserva byte-exacta en
`build/tmp/p03-contract-1qkR4A/PROPUESTA-P03-r1.md`, SHA
`954af9ee7dc3fb95f318e147f2152c60b6e06e0f48366422783e284c781c0518`.
La revisión intermedia verbose P03a quedó preservada como
`PROPUESTA-P03-r2-verbose.md`, SHA
`0e5f8bf433d8f67a0e9d0e525ea5c0025c6a3bf3ae941609139ccb8ea963fbcb`.
No era un producto implementado ni un criterio aplicado retroactivamente.

La revisión intermedia produjo un golden verbose de28 eventos/8415 bytes.
Su cálculo independiente dio12 registros obligatorios por test y mínimo3048
bytes/test aun usando nodeid de un byte y seq/local_seq1: 10000 tests
requieren al menos30480000 bytes. Frente a2097152, incluso el límite optimista
sin cierres ni IDs reales era688 tests. El arquitecto **rechazó** considerar
ese diseño coder-ready: el límite P1 es metadataJSON **conjunta**, no journal
aislado, y el crecimiento de la suite ya amenaza el caso objetivo.

Se conservan golden.jsonl, check_p03a_contract.py y p03a-contract-output.txt
como evidencia del diseño retirado. No decir que el codec compacto tiene
ese mínimo ni atribuir esos cálculos a un producto que nunca existió.

## Colección real de main y proyección explícitamente simulada

Se realizó solo colección, **sin ejecutar cuerpos de tests**, sobre
HEAD `34bd572a6f54f6c49f1205fe2ece63acd9e818a3` del worktree documental.
Comando driver: `uv run --no-sync python build/tmp/p03-contract-1qkR4A/collect_main.py`,
exit0, UTC `2026-09-08T03:34:25.302161+00:00` a
`2026-09-08T03:34:26.770803+00:00`. Salida pytest:
**404/405 tests collected (1 deselected)**. La marca no-property mantiene404
nodeids reales, máximo196 bytes. No son identidades de un candidato P02a.

Entorno nuevo cerrado, no secreto: PATH /usr/bin:/bin, LANG/LC_ALL C,
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1, PYTHONDONTWRITEBYTECODE=1,
PYTHONPATH=carpeta de sonda + worktree, P03_COLLECT_OUTPUT privado. Plugins
explicitados tras inspeccionar entrypoints instalados: pytest_cov.plugin,
pytest_bdd.plugin, _hypothesis_pytestplugin y anyio.pytest_plugin, además
del recorder collect_probe. cacheprovider off, --collect-only -q -m not property.
Config real del repo conservado; ningún -o addopts vacío ni selección -k.
Colección importa tests/conftests, por lo que no es ejecución de cero código;
es **ausencia de ejecución de test bodies**, no aislamiento ni pureza.

El supervisor conserva argv/cwd/env/start/end/exit y hashes en
main-collect-receipt.json. El cambio de nombre de rama del worktree no cambió
el SHA; documentos no trackeados permanecieron fuera de testpaths. No se
leyeron/ejecutaron fuentes del P02a mutable. Root aportó después una cardinalidad
de candidato645 total (644 normal+1 property): **dato reportado por root**,
no colección adicional de este actor.

### Codec compacto y cabida

`measure_compact.py` serializó un layout **SIMULADO** con los404 IDs reales
y crecimiento sintético explícito de234 bytes/nodeid. No evalúa tests ni
produce veredictos observados: impone fases PASS solo para medir framing.
Los archivos llevan prefijo SIMULATED-layout. El codec propone:

- Cabecera única de run/version/refs de dos ejecuciones.
- Registros `[seq,execution_index,local_seq,event_code,payload_values]`.
- Tabla de nodeids explícita, declarados una sola vez y referidos por índice;
  duplicates y referencias inexistentes se rechazan, no desaparecen en un set.
- Phase/outcome como enums numéricos reversibles; campos make y log completos,
  excepción raw/wasxfail/xfail preservados. No suprimir información obligatoria.

| Normales simulados | Crecimiento | Bytes JSONL |
|---:|---:|---:|
| 404 | 0 | 198658 |
| 581 | +177 | 314053 |
| 644 | +240, cardinalidad normal reportada por root | 355192 |
| 650 | +246 | 359110 |
| 1000 | +596 | 590685 |
| 1500 | +1096 | 935185 |

El escenario644 **no** contiene el nodeid property ni su deselection: ese
registro y collectors/plugins/diagnósticos adicionales requieren margen y
medición de integración. No llamar al número355192 tamaño real de un journal
del candidato645. Es cabida simulada sobre nombres sintéticos, no garantía.

Planificador size-only del filesystem documental encontró589 regulares y
97840 bytes del array de metadata de archivos. No hasheó contenidos ni
construyó snapshot P02a; Git/spec/context/owner/terminal no están incluidos.
Las exclusiones de planificación no acreditan semántica productiva P02a.

El arquitecto decidió **presupuesto restante explícito**, no reparto fijo:
max_bytes obligatorio exactint1..2MiB en decoder; datos mayores bloquean.
P03c/P06 calcularán disponible con ledger real de metadataJSON conjunta2MiB
menos owner/inputs/otras metadata y reserva terminal revisada, contando ambos
nombres terminales conforme P02b. Caller-declared max_bytes no acredita ese
ledger. El kernel no hace IO ni cambia límites ya válidos P02a/P02b.

El ejemplo512KiB inputs/1024KiB journal/4KiB owner/2*192KiB terminal/124KiB
resto es solo aritmética de planificación, **no nueva política**. El terminal
podrá referir fases/journal por identidad resoluble en vez de duplicar todas
sus estructuras; esa integración aún debe especificarse/calificarse.

## Golden compacto y QA documental final

golden-compact.jsonl: **1938 bytes**, cabecera+29 registros, SHA
`52eed49e69f6d98da227347396eaa42a57d0c854e93cd662c75d9e76173a6730`.
Tiene un ID literal t, dos ejecuciones, tres fases PASS aportadas, sin plugins
declarados. No se presentan esos datos sintéticos como una ejecución real.
El futuro test incorpora esos bytes como literal, no dependencia a build/tmp.

`check_compact_contract.py` dio exit0: secuencia global1..29, local7/15,
declaración única [0,t], fases0/1/2; hash/tamaño literales iguales. Comprobó
Feature P03a **12 filas**, bytes iguales al bloque puro previamente extraído,
parse/IR0 findings. No implementa decoder/FSM ni equivale a sensibilidad del
SUT futuro. La feature nativa20filas quedó en historia, no en el alcance P03a.

Archivos adicionales de custodia bajo `build/tmp/p03-contract-1qkR4A/`:

| Archivo | SHA-256 |
|---|---|
| main-nodeids.json | `b369fdf81e433339038390e8b4c2255abacd91d0e63cebb23ef63f0885441d49` |
| main-collect-receipt.json | `87b8b18787b3b2b3f4f3a37fe9a51724f424f5ffdb5f1dfa67f523a1fe850fa0` |
| measure_compact.py | `aacdcb0cc3c94319a45e10d78a33a2dea74a997b0d9fdd5bf9aeb1bf98e95af1` |
| compact-layout-report.json | `1f7991a1fa24b0bf6867e1b7138456c5b6bf01ce4fb610723109794c1487effc` |
| check_compact_contract.py | `72bafad7861df6e1eeaf600e0b774cccf89477034973311778c803fed4bda4bf` |
| compact-qa-output.txt | `b6fba0d1dcf3bb090c5ccd81a11469450f03b9d56873678bd79b16fd1c582245` |

La propuesta pura revisada tiene SHA
`05b7c1b96a8e8547ea17a215c36b32b9e29e7f02248099dda6345d63ecfe32a1`
al cerrar esta addenda. Falta challenge separado y autorización del arquitecto,
no inventario de plugins ni P04 para **este kernel puro**. No afirmar ahorro,
producto conforme o beta terminada por estas mediciones de bytes.

## Addenda — NO-GO del challenge: offsets e instancias

El reviewer separado detectó dos bloqueantes documentales y el arquitecto los
confirmó antes de autorizar P03a. Ancestros preservados, sin reescribirlos:

- `PROPUESTA-P03-r3-reviewed.md`, SHA
  `05b7c1b96a8e8547ea17a215c36b32b9e29e7f02248099dda6345d63ecfe32a1`.
- `SONDA-P03-r3-reviewed.md`, SHA
  `4bb713e73ca2857a64b1eb76fc482537b5b753ef4677ba25e7e880b3fc2ceb60`.

Ambos bajo la carpeta de sonda propia, custodia local-only. No eran producto
aprobado; este cambio es corrección del contrato antes del coder.

**C-P03a-01:** ProtocolFinding exigía offset, pero JournalEvent no conservaba
posiciones. Se añadieron offset/end_offset al modelo lógico, observados por
decoder y ajenos al wire. Reconcile valida tipos/rangos/orden/contigüidad y
límites en observations manuales. Los findings referencian bytes del evento,
no posiciones aproximadas por caracteres. Mapa ampliado con offsets negativos,
bool, solapamiento, hueco, cabecera incorrecta, end/consumed/max incoherentes y
Unicode multibyte. El golden sigue byte-exacto, no necesita nuevo schema wire.

**C-P03a-02:** unicidad global (execution,nodeid,phase) contradecía conservar
dos ejecuciones completas de un nodeid para que P01 denunciara duplicado.
Ahora la pareja es (execution_id,test_start.seq,phase), y TestObservation
conserva start_seq. Dos instancias secuenciales completas pueden ambas ser
terminales; sus identidades repetidas llegan a P01. Make/log duplicado dentro
de una instancia sigue siendo duplicate_phase/report_pair_mismatch y no
terminal. Mapa incluye controles de ambas situaciones sin deduplicar eventos.

### Comprobación acotada realizada

`check_offsets_instances.py` trabaja solo sobre el golden literal y P01 ya
integrado. **No implementa ni ejecuta el decoder/FSM P03a**. Calcula fronteras
de líneas, crea dos variantes nuevas y consulta P01 como referencia existente.

Primer intento falló: la sonda llamó compare_identities con tres argumentos
posicionales, pero su firma exige keywords. Traceback TypeError preservado en
offsets-instances-output.txt; script conservado como check_offsets_instances-r1.py.
El shell compuesto terminó con sha256sum exit0 después del traceback: **ese
exit del shell no es éxito del script fallido**. No se atribuye como positivo.

Se releyó firma real (identities.py:213–218) y corrigió la llamada a
expected=/collected=/executed=. La segunda corrida verificó que las variantes
ya creadas tenían bytes idénticos en vez de sobrescribirlas; exit0 real del
pipeline con pipefail, captura offsets-instances-r2-output.txt. Resultados:

- Golden original sin cambio:1938 bytes, SHA52eed49e…,29 eventos; primer
  intervalo [573,657), último end1938, todos los intervalos contiguos.
- Variante Unicode t→é:1939 bytes; el incremento es1 byte de UTF-8. No se
  tomó longitud de str como posición del archivo.
- Variante con bloque de test completo duplicado: start_seq18 y26. La sonda
  conservó bloques/seq y consultó P01 con expected=(t,), collected=(t,),
  executed=(t,t): status invalid y exactamente duplicate_identity en executed.
  Esto no demuestra todavía que el FSM P03a produzca esos terminales: ese es
  el nuevo test contractual del futuro coder/verifier.

| Archivo bajo carpeta de sonda | SHA-256 |
|---|---|
| check_offsets_instances-r1.py | `3de93a88d4e46c1e1744691b5da84ed9596632ba13fa8ea8080f551d465303ff` |
| offsets-instances-output.txt | `03f0ea5c4e141fdd8d4b6211db398555ef5771f5b8c65ef97b75e21c4966cabc` |
| check_offsets_instances.py | `575ca92953dfb915af0f451a627ea9294fb1ff016e6335b3e7f8c266539d1004` |
| offsets-instances-r2-output.txt | `367e19dce05e4a45881fc5a3ab142330027b2ca1dce134920a87adb69c3a559b` |
| golden-unicode-variant.jsonl | `8144a1068e4ec8d6d42c9487118544122491ea24211762580bb6e08f2e4b4548` |
| golden-repeated-instance-variant.jsonl | `1c4431fbd92c1c32b2a8da05300ec4397efae5092890b591bcd513dad1eca57b` |

Propuesta corregida al cierre de esta addenda: SHA
`47429b8896a38bcd0ec2c835d17a385dd68a4585e5b4207ab86127486ae9f251`.
La revisión independiente anterior había cotejado codec compacto/límites/
payloads y QA1938B/29eventos/12filas sin otro bloqueante reportado; no se
atribuye aquí haber ejecutado tests nativos ni la nueva FSM. Producto continúa
sin autorización hasta dictamen separado del arquitecto sobre estos bytes.
