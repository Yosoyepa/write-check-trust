# P03 — preflight del protocolo pytest y slots de P02b

Estado: **investigación y decisiones propuestas; no API/Gherkin autorizados ni
implementación de producto**. Actor: subagente `p02a_binding`, tarea separada
del binding P02a, cohorte B3-MA-D. Lectura de
[SPEC-P1](../specs/SPEC-B3-P1-evidencia.md),
[PIEZAS](../SELF-HOSTING/PIEZAS.md) y
[CADENA](CADENA-P03-P06.md) completas.
[P02b](PROPUESTA-P02b.md) inspeccionado con SHA-256
`13ae6e67e467fd1205574e053c1bf145b082928dab453b6b5e5251e0084f6ef7`,
junto con [su sonda](SONDA-P02b.md); no aprobado por este investigador.
Ningún import de P02a mutable ni de producto P02b inexistente.

## 1. Decisión inmediata para cerrar slots de P02b

**Los cuatro slots propuestos bastan para el corte P1 secuencial**, sin exigir
otro archivo de colección ni stdout/stderr separados:

| Slot P02b | Uso propuesto P03/P04 |
|---|---|
| `artifacts/events.jsonl` | Un journal del supervisor, multiplexado por execution ID, con colección y ejecución separadas y eventos nativos observados |
| `logs/pytest.log` | Bytes combinados stdout/stderr de ambos procesos, segmentos mediante offsets guardados por supervisor |
| `artifacts/.coverage` | Base privada del único proceso que realmente ejecuta tests con coverage |
| `artifacts/lcov.info` | LCOV de ese productor; pertenencia/validación P04, no la mera aparición del slot |

Motivo: la identidad de ejecución se expresa en cada evento, no en nombres
arbitrarios de archivo. Un único escritor supervisor evita append concurrente
de varios productores y puede registrar el exit aunque pytest muera sin hooks.
La separación de procesos se conserva en argv/execution ID/segmentos; combinar
logs no conserva qué descriptor original emitió cada byte ni un orden causal
entre escrituras con buffering. Ese límite es aceptable solo porque **el log
no es el canal de decisión ni el inventario autoritativo**.

Sonda real: dos procesos secuenciales (collect-only y ejecución no-property)
enviaron eventos por un pipe dedicado; el padre escribió **un events JSONL y un
log combinado**, 25 eventos, ambos exits 0. Offsets de log: colección [0,70),
ejecución [70,142). Solo execution-1 tuvo fases. El test imprimió un falso
`{"event":"session_finish","status":0}`: quedó en log, no en events.
No son eventos autenticados contra el propio test, que comparte UID/proceso
del plugin; la separación evita interpretar stdout accidental como evidencia.

No ampliar slots ahora por anticipación. P03 debe congelar esta disciplina
antes de implementar. Si luego exige productores concurrentes, reintentos,
stdout/stderr separados o colección persistida en archivos distintos, revisar
P02b primero. Los archivos de recibos de esta investigación no son slots
nuevos del producto: son evidencia de la sonda.

## 2. Fuentes primarias inspeccionadas y acoplamiento

Runtime reutilizado sin sync/install:

- Python 3.13.14, ejecutable
  `/home/jandradeu/Documents/well_code_template/build/tmp/sh-p01-CND-80B8/.venv/bin/python3`.
- pytest **9.1.1**, pluggy 1.6.0.
- Instalados, **no calificados por esta sonda**: pytest-cov 7.1.0,
  coverage 7.15.4, pytest-bdd 8.1.0, hypothesis 6.165.10.
- Fuentes bajo el mismo entorno, prefijo
  `lib/python3.13/site-packages/_pytest/`; se leyó código instalado,
  no se extrapoló documentación de otra versión.

| Fuente y líneas observadas | Hecho relevante |
|---|---|
| `hookspec.py:227–304` | itemcollected precede modifyitems; deselected puede llamarse varias veces; collection_finish ocurre después de modificación |
| `hookspec.py:620–696`, `runner.py:115–157` | logstart → setup → call solo si setup pasa → teardown → logfinish |
| `runner.py:236–268` | KeyboardInterrupt se relanza salvo modo depurador; no siempre hay report de call |
| `skipping.py:248–312` | xfail transforma report; XPASS estricto no tiene wasxfail |
| `main.py:317–389` | sessionfinish no reemplaza exit del proceso; colecciones vacías, errores e interrupciones tienen salidas diferentes |
| `mark/__init__.py:209–284` | -k y -m deselectan por pasos; marcar property no implica que una ausencia posterior se haya declarado correctamente |
| `config/__init__.py:1512–1594` | addopts desde entorno/config se mezcla antes de plugins; desactivar autoload no desactiva -p, PYTEST_PLUGINS ni conftest |

No hay garantía de este protocolo en todo el rango Python/pytest soportado por
metadata del paquete. Una futura implementación que lea
`_pytest.skipping.xfailed_key` **depende de API privada y versión calificada**;
debe aislar esa dependencia, fijar/calificar versión y bloquear una versión
desconocida, no continuar sin observar esa información.

## 3. Hallazgos que cambian la especificación P03

### F-P03-01 — exit 0 no equivale a test terminado

Reproducción: `os._exit(0)` dentro de test dejó únicamente setup PASS y salida
del proceso **0**, sin call, teardown, logfinish ni sessionfinish. Skip, xfail
y XPASS no estricto también dan exit 0 en pytest real.
Decisión: el supervisor conserva exit crudo; P01/P05 requieren además protocolo
completo por identidad y resultado permitido. Ningún fallback a resumen/stdout.

### F-P03-02 — ausencia de call tiene dos causas muy diferentes

Setup fallido/skip/xfail-notrun produce setup no-PASS, **teardown presente** y
logfinish: el call omitido es la conducta del runner, no pérdida del journal.
Crash/interrupción produjo setup PASS y fases restantes ausentes.
Decisión: conservar observación terminal del test por logfinish/fases
coherentes, con disposición `call not scheduled after nonpassing setup`.
Esto no satisface la obligación PASS. No fabricar un report call=skipped ni
exigir falsamente tres fases para reconocer un fallo completo. P05 conserva
FAIL de setup/teardown y decide sus ejes; P03 no inventa accredited/rejected.

### F-P03-03 — XPASS estricto requiere más que outcome y wasxfail

En pytest 9.1.1:
- XFAIL: outcome skipped + wasxfail.
- XPASS no estricto: outcome passed + wasxfail.
- **XPASS estricto: outcome failed, wasxfail ausente, call.excinfo ausente**.

La sonda usa wrapper `pytest_runtest_makereport` con `tryfirst=True`;
después de yield observa el report transformado, la presencia/tipo de excepción
cruda y el valor **ya evaluado** de xfail en stash. Strict activo + call sin
excepción + report failed distingue el caso en este runtime calificado.
No se reevalúa una expresión de xfail ni se interpreta el texto inglés
`[XPASS(strict)]` ni la salida del terminal.

Control positivo obligatorio ya ejecutado: `@pytest.mark.xfail(False,
strict=True)` pasó las tres fases, stash sin xfail activo y exit 0.
Otro control: marca strict añadida dinámicamente durante call sí produjo
XPASS estricto observable. Por tanto rechazar todo test decorado sería incorrecto.

Decisión propuesta: versión privada aislada/calificada para observar esta
distinción, con raw outcome + exception-presence + wasxfail-presence +
xfail-evaluated (run/strict) conservados, no solo una etiqueta calculada.
No aprobar todavía un esquema final de P03 con este párrafo: faltan challenge
y casos como xfail con raises, setup/teardown xfail y wrappers ajenos.
Plugins que alteren estas transformaciones necesitan calificación propia.

### F-P03-04 — collection_finish no significa colección exitosa

Error de import: collect_report failed, sin fases, exit 2, sessionfinish 2.
Error de plugin durante modifyitems: hubo **collection_finish con items**,
después internal_error y exit 3.
Decisión: colección acredita inventario solo con sus reportes, sesión terminal,
exit observado y consistencia con obligaciones; la existencia de un evento
collection_finish no basta.

### F-P03-05 — hay que observar antes y después de selección

Control property: dos item_collected, una deselection property y un seleccionado.
Plugin de prueba retiró un test normal notificando deselected: evento con
property=false y colección vacía. Variante silenciosa retiró el mismo test sin
notificar: item_collected mostró el original pero no apareció ni en selected
ni en deselected. Ambas fueron salidas 5 en micro-fixture, no éxito.

Decisión: comparar multiconjuntos preservando duplicados:
inventario observado previo = seleccionados finales + deselected declarados;
validar intersección/vacíos/duplicados antes de sets. Deselection autorizada
solo property y coherente con la selección revisada; lista explícita de IDs
property excluidos, no un número. Expected seleccionado aprobado se compara
independientemente con la colección y terminales; no se regenera desde ellos.
El journal conserva ambas colecciones si hay preflight y productor.

### F-P03-06 — sessionfinish puede cambiar el exit

Plugin control cambió session.exitstatus de 0 a 19. El wrapper observó argumento
original 0, estado final 19; el supervisor observó **exit 19**.
Decisión: conservar ambos valores si se observan, pero exit del proceso es
autoridad de esa ejecución. Un plugin posterior/cleanup puede fallar o cambiar
salida: sessionfinish 0 nunca sustituye wait/returncode. Crash/SIGKILL carecen
de ese hook y requieren terminal del supervisor. No admitir el plugin control
en el perfil de producto; fue un adversario de laboratorio.

## 4. Esqueleto de eventos propuesto, no schema congelado

Un journal UTF-8 JSONL, LF por registro; escritor único supervisor. Cada registro
con versión, run ID, execution ID, origen (supervisor/pytest), secuencia global
y payload tipado. El canal del plugin conserva su secuencia local aparte.
No generar IDs desde resultados ni permitir que el hijo elija otro run.

- Supervisor: inicio con argv lista exacta, cwd/root binding, contexto y receta;
  recepción EOF/truncamiento/errores; terminación con exit raw nullable, signal,
  timeout/cancelación observada, offsets/log digest y limitaciones.
- Pytest: inicio/versiones/plugins/opciones observadas; item_collected;
  collect_report; deselected; colección final; logstart; fase/report;
  logfinish; internalerror/interrupción; sessionfinish.
- `pytest_runtest_logreport` es el report que consume el runner; makereport
  aporta metadatos de excepción/xfail que logreport solo no contiene. El
  contrato final debe vincular/cotejar ambos sin contar dos ejecuciones.
  La sonda emitió fases desde makereport, **no calificó ese cotejo final**.
- Guardar nodeid literal UTF-8 con parámetros; no split por espacios, nombres
  cortos ni dict temprano. Estado de fase y terminal de test son dimensiones
  distintas. Secuencia repetida/identidad sustituida/missing LF/JSON inválido/
  referencia ajena produce defecto visible, no ignorar líneas desconocidas.
- No usar un evento enorme con todos los IDs sin límites: inventarios pueden
  emitirse por elemento más evento de cierre con conteo; el conteo nunca
  reemplaza las identidades. La sonda pequeña usa arrays y no prueba escala.
- Versión desconocida, tipo desconocido o campo no contratado bloquea consumo.
  Copia del journal/log no autentica productor; hashes y TerminalRef retenidos
  vinculan bytes observados bajo la confianza cooperativa de P1.

El canal dedicado puede ser pipe heredado explícitamente (`pass_fds`) con
framing acotado. No meter events en stdout ni dejar que child abra la ubicación
final del journal como autoridad. Tras EOF se conserva toda línea completa y
la cola incompleta como evidencia de truncamiento; se espera/recolecta el hijo.
La sonda demuestra multiplexado básico, **no** parser fail-closed, límites,
cancelación del supervisor ni resistencia a un hijo que herede/retenga el pipe.

## 5. Receta y entorno que P03 debe cerrar antes del coder

Propuesta: un proceso collect-only y después un único productor tests+coverage,
ambos ligados al mismo snapshot/contexto/expectations, sin G-TEST adicional.
Colección del productor debe corresponder a la revisada/preflight; si diverge,
se conserva el fallo y se impide acreditación. La colección extra tiene coste
y puede tener efectos al importar: no contar solo coste de hooks.

Receta conceptual del productor: intérprete absoluto revisado → `-m pytest`,
root/config explícitos, tests completos del perfil, `-m "not property"`,
plugin observador explícito y receta coverage productiva con destinos privados.
No usar `-k`, `--lf`, `--ff`, `--maxfail`, `--setup-only`, reruns, xdist,
`--runxfail`, depurador o selección incremental en este perfil inicial.
No quitar defaults de config para obtener verde sin decisión/registro.

Entorno nuevo cerrado, construido por campos, no volcado/heredado:
PATH mínimo, locale fijado, interpreter/plugin/import roots revisados,
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, `PYTHONDONTWRITEBYTECODE=1`,
ruta privada COVERAGE_FILE si se requiere, canal/ID operativos. Rechazar
configuración de selección no declarada del caller antes de sustituirla:
no silenciar PYTEST_ADDOPTS/PYTEST_PLUGINS/PYTHONPATH ajenos y luego afirmar
que se ejecutó su entorno. Nombres de variables a inspeccionar, valores
permitidos y receta final requieren contrato; no leer secretos para hacerlo.

Desactivar autoload **no bloquea plugins por -p ni conftest/pytest_plugins**.
Cargar explícitamente versiones revisadas necesarias del perfil (observador,
pytest-cov y las requeridas realmente por la suite), y observar inventario
efectivo. No afirmar aquí que pytest-bdd/hypothesis pueden simplemente omitirse
por excluir property: colección importa módulos y otros tests pueden usarlos.
Rechazo de plugins/opciones fuera del perfil antes de lanzar cuando sea
determinable; observación posterior no evita efectos ocurridos al cargar.
Conftest/config/tests son inputs revisados cooperativos, no código hostil seguro.

Cache y tmp de pytest deben ser privados:
`-p no:cacheprovider` o cache_dir privado es decisión por calificar;
`--basetemp` exclusivo dentro del workspace, creado/poseído sin riesgo de que
pytest borre un directorio ajeno. Las sondas desactivaron cacheprovider y no
usaron tmp_path; **no califican esta precondición de basetemp**.
HOME/TMPDIR adicionales si alguna dependencia los necesita: fijar rutas
privadas y probar, nunca heredar de forma abierta por conveniencia.

P03 supervisa bytes/logs/events/tiempo y outputs durante producción; P02b.check
solo observa límites al comprobar. Al exceder no truncar IDs y dar verde:
registrar límite, terminar/recolectar productor y conservar parcial. Cerrar
también descriptores/descendientes cooperativos que mantengan pipes abiertos.
Los techos globales P1 y 2 MiB metadata no se consideran medidos por estas
micro-fixtures; falta presupuesto emparejado y dimensionar el journal real.

## 6. Sondas ejecutadas y resultado nativo

Custodia `local-only`:
`build/tmp/p03-preflight-jCNZss/` del worktree documental. Fixtures y scripts
creados con apply_patch; eventos/logs/recibos son outputs de sus productores.
Todos los procesos bajo runtime indicado, sin instalaciones/red ni limpieza.
Los drivers tienen timeout de 15 s por pytest; multiplexado 10 s de drenaje
y 2 s de wait. No son límites de producto ni pruebas de rendimiento.

Comandos del supervisor, todos **exit 0** (los exits negativos de casos se
guardan, no se reinterpretan como fallos del driver):

```bash
uv run --no-sync python build/tmp/p03-preflight-jCNZss/drive.py
uv run --no-sync python build/tmp/p03-preflight-jCNZss/drive_extra.py
uv run --no-sync python build/tmp/p03-preflight-jCNZss/drive_pipe.py
```

Variables para los drivers:
UV_PROJECT_ENVIRONMENT=`/home/jandradeu/Documents/well_code_template/build/tmp/sh-p01-CND-80B8/.venv`;
PYTHONPATH=`/home/jandradeu/Documents/well_code_template/build/tmp/beta3-execution.uW30FJ`.
Cada recibo conserva argv como lista, cwd, entorno cerrado del hijo, UTC
inicio/fin, exit y hashes de log/events. En total **23 procesos pytest**:
12 iniciales, 9 controles adicionales, 2 de multiplexado. Sin reintentos.

| Caso real | Exit | Fases/terminales observados |
|---|---:|---|
| normal + property excluido | 0 | setup/call/teardown passed; logfinish y sessionfinish |
| assert falso | 1 | call failed, setup/teardown passed |
| setup RuntimeError | 1 | setup failed, sin call, teardown passed, logfinish |
| teardown RuntimeError | 1 | setup/call passed, teardown failed, logfinish |
| skip decorador / skip en call | 0 | setup skipped sin call / call skipped; teardown y logfinish |
| xfail / xfail run=False | 0 | call skipped+wasxfail / setup skipped+wasxfail, sin call |
| XPASS no estricto | 0 | call passed+wasxfail, no obligación PASS |
| XPASS estricto | 1 | call failed, sin excepción cruda ni wasxfail, xfail strict activo |
| xfail(False) estricto | 0 | tres fases passed, xfail evaluado ausente |
| xfail dinámico estricto | 1 | strict activo en call, failed sin excepción |
| import RuntimeError | 2 | collect_report failed; sin fases; sessionfinish |
| archivo sin tests | 5 | colección vacía, sin fases; sessionfinish |
| KeyboardInterrupt | 2 | setup passed, sin call/teardown/logfinish; keyboard_interrupt y sessionfinish |
| os._exit(17) | 17 | setup passed, sin fases restantes/sessionfinish |
| os._exit(0) | 0 | igual truncamiento, **no éxito terminal** |
| SIGKILL propio | -9 | truncamiento; exit negativo observado por padre |
| deselection normal explícita | 5 | evento deselected property=false; expected faltante |
| deselection normal silenciosa | 5 | item previo no está en selección ni exclusiones |
| plugin modifica exit | 19 | argumento sessionfinish 0, session.exitstatus 19, padre 19 |
| plugin falla en colección | 3 | collection_finish no basta: internal_error posterior |
| preflight collect-only | 0 | IDs y property separado; cero fases |
| multiplexado collect + ejecución | 0 / 0 | 25 registros, un journal/log; ID de proceso separa sus fases |

No hubo un rojo inesperado del instrumento que corregir en estas tres
corridas. Los rojos de pytest son fixtures deliberadas y quedan íntegros.
No afirmar TDD de producto inexistente ni verificación independiente: este
actor escribió y ejecutó las sondas; el challenge queda al arquitecto/reviewer.

## 7. Identidad de evidencia y límites del dictamen

Hashes de archivos relativos a la carpeta de sonda:

| Archivo | SHA-256 |
|---|---|
| probe_plugin.py | b58b435433103cbd2c806e90cdd5ee4fa7183adf6da8c1596efc3c80ff0c60b3 |
| pipe_plugin.py | f139735c60db5ebf93e826f4309ce349badd29393dcfff4a765222be44bca15e |
| drive.py | 603455af9410fbe6e56acfdcf0be56c48206994cceb4426d1ba1539cd1b5ffa9 |
| drive_extra.py | e4671f63c0c434db52130a62d3a62b54b73fe659d5b444b409eb0fa438dd0f8c |
| drive_pipe.py | 65bb1056dc2a479e20fa3de3bac193991a7f8653f3259b4c43bc7a67ea865956 |
| receipts.json | efbb1717c3e35268a3ae7394b6b6db91cc2b04bfe19c05fc7a9731017b34b3c9 |
| extra-receipts.json | 9acc5f744b5636230e195fbe2824fb765d828f36475be447e27c18e1605ff3eb |
| multiplex-receipt.json | 04b92176eea353fa14fe9651afbf7efea2ca85b7148ba15fbe2549fb52aa6e5c |
| multiplex.events.jsonl | 7b429c0b6748437cdef40a7aa1a22ac8d7ed3d4b847de1abf8372f8510882993 |
| multiplex.pytest.log | 1befb0ae3f6fe98a1dda096f9e761a35d5662a8f227b5e93cccc2d9cc9b2c168 |

Hashes de fuentes primarias instaladas, paths según §2:
hookspec.py `12098571044671c24ed0011e2bb7d94976380265e5734c30f856479482e6f88d`;
runner.py `c8d7fd553c0516f7884502ee0e7954eb5a5b1542f21fcb5c4357500ed2fe1570`;
skipping.py `cc2102f5f8d19478f91ce77117c109348b8766ae04ebc4b8c33e5f9923e50aee`;
main.py `8ee2725057ff1811e2ae9ebdf1befb7518195f8f333f9f8ca024d76a4b80780e`;
config/__init__.py `98b05c2c37d09e1d5c05975efc2d9af98d4aff6ea47de410a8e93956420873c1`.

Los recibos identifican logs/events, no constituyen un manifiesto completo de
todas las fixtures ni custodia externa durable. No borrar la única evidencia.
Fast documental posterior: `uv run --no-sync wct gate --tier fast`, exit 0,
7/7 PASS, 0 SKIP, sobre el worktree documental, no el candidato P02a mutable.
Ese verde no verifica un producto P03 ni las sondas deliberadamente defectuosas.
No suite WCT, commit/full, coverage/LCOV, hardening, P02b real, aislamiento,
telemetría económica ni calificación de todo pytest. Costes unavailable;
el tiempo de estos microprocesos no acredita presupuesto P1.

Salida para arquitecto: **conservar cuatro slots de P02b con las condiciones de
§1; cerrar un contrato P03 versionado y challenge con estos seis hallazgos
antes de coder**. Autorizar slots no autoriza el protocolo propuesto ni el uso
privado de stash en producto. La siguiente matriz debe añadir corrupción/
duplicados/truncamiento, timeout/cancelación del supervisor, efectos de
plugins/fixtures restantes y ensamble coverage real sobre snapshot/workspace.
