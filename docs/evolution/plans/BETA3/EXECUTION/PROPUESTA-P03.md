# SH-P03a/1 — Protocolo pytest observado: contrato puro autocontenido

Estado: **propuesta revisada para aprobación del arquitecto; no implementación**.
Entrega sh-delivery/2, molde wct-harness-local/2, cohorte B3-MA-D. P03a necesita
P01 integrado; no depende de aprobar el inventario real de plugins, ejecutar
P02a/P02b mutable o completar P04. P03b (plugin) y P03c (supervisor) quedan
fuera de este encargo. Bless/publicación humanos permanecen separados.

La propuesta anterior completa (`954af9ee…`) se conserva en la custodia
identificada en [SONDA-P03](SONDA-P03.md). Este documento la sustituye para
**P03a únicamente**; no autoriza su Gherkin nativo de veinte familias ni sus
APIs pendientes P03b/c. Se incorpora el challenge de hacer un kernel verificable
sin fingir que un evento declarado autentica su productor.

## 1. Afirmación, reutilización y fronteras

Entrada: bytes de un journal y expectativas aportadas explícitamente. Salida:
prefijo decodificado, defectos de protocolo, inventarios y fases observadas.
Un protocolo completo **no** demuestra origen, runtime/plugins calificados,
inputs frescos, cobertura, seguridad contra otro proceso del UID ni accredited.

Se reutiliza `compare_identities` de P01 para tres inventarios; se preservan
sus findings sin modificarlo. No se usa `gate.exec._captured` (resume exit y
texto), el parser genérico de Gherkin como ejecución, ni un codec privado P02b.
P02b no ofrece codec público y su terminal admite floats; este schema pequeño
de eventos no los admite. Stdlib json/dataclasses/collections basta, sin pytest,
subprocess, filesystem, entorno, reloj ni nuevas dependencias en estas fuentes.

La semántica de fases procede de fuentes instaladas pytest9.1.1 y las sondas
citadas. Los futuros adaptadores deberán producir este schema y calificar sus
hooks; recibir `pytest_version="9.1.1"` no es verificar esa instalación.

## 2. API, tipos y límites de entrada

Importación pública desde `tools.wct.evidence.pytest_observation`:

```text
decode_pytest_journal(data: bytes, *, run_id: str,
                      executions: tuple[ExecutionExpectation, ...],
                      max_bytes: int) -> JournalObservation
reconcile_pytest(observation: JournalObservation, *,
                 expected: tuple[str, ...],
                 property_ids: tuple[str, ...]) -> PytestObservation
```

Sin defaults de seguridad. Los argumentos del API son tipos exactos según
tabla: bool no sustituye int, bytearray no bytes, lista no tupla. Error de
**tipo público** → TypeError con nombre de argumento; valor público inválido
→ ObservationError(code, field), excepción Python normal, nunca frozen.
El decoder no lanza excepciones por contenido de journal malformado dentro
del límite: devuelve prefijo y findings. No se tratan excepciones de memoria/
cancelación como un journal válido; se propagan.

`executions` contiene exactamente dos ExecutionExpectation, en orden,
execution_id `collection-1`/role `collection`, luego `producer-1`/role
`producer`. Cada uno lleva input_sha256, context_sha256 y recipe_sha256;
digest lowerhex64, run_id lowerhex32. No se construye expected desde eventos.
No exige que ambos tengan recipe_sha256 igual (las recetas son diferentes).

Todos los tipos de valores son dataclasses frozen. Tuplas en toda colección,
sin un dict/list mutable oculto bajo un frozen. Orden de campos normativo:

| Tipo | Campos |
|---|---|
| ExecutionExpectation | execution_id: str; role: str; input_sha256: str; context_sha256: str; recipe_sha256: str |
| JournalEvent | seq: int; execution_id: str; origin: str; local_seq: int o None; kind: str; payload: unión exacta de §3; offset: int; end_offset: int |
| ProtocolFinding | code: str; execution_id: str o None; nodeid: str o None; phase: str o None; offset: int o None |
| JournalObservation | run_id: str; executions: tupla de ExecutionExpectation; events: tupla de JournalEvent; findings: tupla de ProtocolFinding; consumed_bytes: int; tail_sha256: str o None; max_bytes: int |
| XfailObservation | run: bool; strict: bool; raises_present: bool |
| PhaseObservation | nodeid: str; phase: str; outcome: str; exception_present: bool; exception_type: str o None; wasxfail: bool; xfail: XfailObservation o None; disposition: str |
| TestObservation | nodeid: str; start_seq: int; phases: tupla de PhaseObservation; terminal: bool; pass_eligible: bool; call_disposition: str |
| ExecutionObservation | execution_id: str; role: str; items: tupla de str; selected: tupla de str; deselected_property: tupla de str; tests: tupla de TestObservation; exit_code: int o None; termination: str; protocol_complete: bool; findings: tupla de ProtocolFinding |
| PytestObservation | executions: tupla de ExecutionObservation; identities: IdentityComparison P01; preflight_identities: IdentityComparison P01; property_findings: tupla de ProtocolFinding; findings: tupla de ProtocolFinding; provenance: str |
| ObservationError | excepción con code: str y field: str, sin traceback/context congelados |

`provenance` es siempre literal `caller-supplied-unverified`. No tiene una
opción para elevarlo a observado/acreditado. pass_eligible quiere decir
**las fases aportadas satisfacen la regla PASS**, no que este kernel las haya
ejecutado ni autenticado.

offset/end_offset son posiciones de bytes observadas por el decoder, intervalo
semiabierto [offset,end_offset) que incluye el LF de esa línea. Son campos
**solo lógicos**, no viajan en el wire y no se aceptan desde un payload. Cada
ProtocolFinding con evento causante copia su offset observado, nunca calcula
la posición sumando caracteres Unicode ni busca el nodeid por substring.
start_seq es el seq de test_start que creó esa instancia; se deriva al
reconciliar y tampoco añade campo al wire.

Límites fijos:

- max_bytes obligatorio, int exacto1..2 097 152; fuera del rango →
  ObservationError(`invalid_reference`, `max_bytes`), bool/tipo no int →
  TypeError. data≤max_bytes; un byte más → ObservationError(`limit_exceeded`,
  `data`) antes de parsear, sin inventario parcial retornado. No default2MiB.
  max_bytes se conserva como límite caller-declared en JournalObservation;
  **no acredita** el ledger conjunto de metadata ni permisos del emisor.
- línea≤64 KiB incluido LF; strings representables en UTF-8 estricto, sin
  surrogate, C0/DEL. `nodeid` no vacío y≤4096 bytes; collect_report admite
  nodeid vacío para el collector raíz. No normalizar Unicode ni partir IDs.
- Máximo10 000 entradas por inventario/execution (items, selected, deselected,
  test_start, phase_make y phase_log **por fase**, test_end). Exacto permitido;
  +1 se observa como limit_exceeded y descarta el evento que lo excede.
- Expected y property_ids≤10 000 cada uno, strings válidos, sin duplicados
  ni intersección. Expected vacío se permite para devolver empty P01 con causa;
  property_ids vacío es válido.
- Números JSON solo enteros en rangos explícitos; floats/NaN/Infinity rechazados.
  Contenedor máximo8 niveles, contando objeto exterior como1; sin claves
  duplicadas en ningún nivel. No claves/descriptores de ejecución arbitrarios.

Códigos de ObservationError (solo valores del API): `invalid_reference`,
`invalid_expectations`, `invalid_observation`, `limit_exceeded`.
field nombra el argumento público o su campo (`executions[1].role`, etc.).
En reconcile, comprobar campos/frozen/tuplas/schema de observation antes de
usar datos construidos manualmente; no aceptar un evento imposible por venir
en dataclass. Esa entrada inconsistente → invalid_observation, no fingir que
provino del decoder. No exige leer bytes originales para validarla.
Reconcile valida offsets de observations construidas manualmente: int exactos
no bool, 0≤offset<end_offset≤consumed_bytes≤max_bytes, longitud de línea1..65536,
intervalos contiguos en orden de eventos, primer offset igual a longitud UTF-8
de la cabecera canónica reconstruible desde run_id/executions y último
end_offset=consumed_bytes. Sin eventos, consumed_bytes es0 o longitud de esa
cabecera, según el prefijo declarado; ninguna posición excede max_bytes.
En findings de decoder, offset debe coincidir con consumed_bytes (comienzo
de línea no aceptada), con offset0 para defecto de header. Rango/orden
incoherente → invalid_observation. Estos cotejos no autentican bytes no
aportados: provenance sigue sin verificar.

## 3. Schema y payloads frozen exactos

El wire compacto preserva los tipos lógicos de la tabla inferior, sin repetir
run ID, nombres de clave/schema ni nodeids largos doce veces por test. No
deduce identidades desde conteos: cada referencia debe resolverse a una única
declaración explícita anterior. JSON canónico UTF-8, sin BOM, claves ordenadas
en objetos, separators(',', ':'), ensure_ascii=False y LF por registro. Arrays
posicionales tienen longitud exacta. No floats/NaN/duplicados de clave/trailing
content. Enteros requieren int exacto, no bool.

Primera línea única: objeto de cabecera con claves exactas `schema_version:1`,
`record_type:"wct-pytest-journal"`, `run_id` y `executions`. executions es
array de dos arrays, cada uno en orden:
`[execution_id,role,input_sha256,context_sha256,recipe_sha256]`.
Debe coincidir con argumentos revisados; no hashes de origen elegidos del
journal. El header no contiene seq; su longitud consume max_bytes y64KiB.

Cada línea siguiente es exactamente:
`[seq, execution_index, local_seq, event_code, payload_values]`.
execution_index0/1 refiere a la cabecera, seq desde1 global contiguo,
local_seq desde1 por ejecución pytest y null para supervisor. event_code
determina kind/origin sin permitir alias; nunca interpretar un mensaje de
stdout como origen supervisor. P03a solo verifica esos datos aportados,
no autentica el pipe. payload_values es array con orden de campos de la tabla,
excepto transformaciones exhaustivas siguientes:

- nodeid de toda clase salvo NodeDeclaration viaja como índice entero a tabla
  global anterior, incluso collect_report vacío. NodeDeclaration viaja
  `[index,nodeid_literal]`; índices desde0 contiguos, cada string único,
  máximo20 000 declaraciones. Repetir índice/string no normaliza: invalid_field.
  Referencia desconocida → foreign_reference. Una declaración vacía solo puede
  usarse en CollectionReport; item vacío continúa inválido.
- phase viaja0=setup,1=call,2=teardown; outcome0=passed,1=failed,2=skipped.
  Cualquier otro valor o bool → invalid_field; el resultado lógico conserva
  strings del contrato. No se elimina el outcome de make ni el de log.
- xfail viaja null o array exacto `[run,strict,raises_present]`; resultado
  XfailObservation. No se invocan expresiones del marker.
- execution_start omite en wire role y tres digests porque se reconstruyen
  inequívocamente desde su única cabecera. Su payload_values exacto es
  `[argv,cwd,log_start,monotonic_ns,utc]`.
- Todas las demás clases conservan orden de la tabla y valores JSON de sus
  campos; las arrays de argv se convierten a tuplas. No otra compresión,
  default ni pérdida de campo aceptada.

| event_code | origin / kind |
|---|---|
| 0 | supervisor / node_declaration |
| 1 | supervisor / execution_start |
| 2 | supervisor / channel_end |
| 3 | supervisor / execution_end |
| 4 | pytest / session_start |
| 5 | pytest / plugin |
| 6 | pytest / plugins_end |
| 7 | pytest / options |
| 8 | pytest / item |
| 9 | pytest / collect_report |
| 10 | pytest / deselected |
| 11 | pytest / selected |
| 12 | pytest / collection_end |
| 13 | pytest / test_start |
| 14 | pytest / phase_make |
| 15 | pytest / phase_log |
| 16 | pytest / test_end |
| 17 | pytest / internal_error |
| 18 | pytest / interrupted |
| 19 | pytest / session_end |
| 20 | pytest / session_end_error |

NodeDeclaration es metadata del supervisor en la ejecución activa, antes de
la primera referencia. No consume local_seq ni representa item recolectado.
Se conserva como JournalEvent para no perder orden; no suma un test esperado.
Una tabla de nombres autorizada no implica que esos tests hayan ocurrido.

Notación de tipos: U=entero0..2**63-1 no bool; S=string UTF-8 con reglas
anteriores≤4096 bytes; H=digest lowerhex64; B=bool; N=None. Campos en orden
según cada fila. Payload classes tienen exactamente esos campos y nombres
de clase; no herencia con campos adicionales ni dict de extensión.

| origin/kind → clase | Campos y rangos |
|---|---|
| supervisor/node_declaration → NodeDeclaration | index:U; nodeid:S (vacío solo para collector raíz) |
| supervisor/execution_start → ExecutionStart | role: collection/producer; argv: tupla no vacía de S no vacíos; cwd: S absoluto POSIX sin componentes . o ..; input_sha256:H; context_sha256:H; recipe_sha256:H; log_start:U; monotonic_ns:U; utc:S |
| supervisor/channel_end → ChannelEnd | eof:B; tail_bytes:U; tail_sha256:H o N; defect: código de canal o N |
| supervisor/execution_end → ExecutionEnd | exit_code:int -255..255 o N; termination: enum §5; signal:int1..64 o N; log_end:U; log_sha256:H; monotonic_ns:U; utc:S; log_truncated:B |
| pytest/session_start → SessionStart | pytest_version:S no vacío; pluggy_version:S no vacío; observer_version:S no vacío; runtime_profile_sha256:H |
| pytest/plugin → PluginClaim | name:S no vacío; module:S no vacío; distribution:S no vacío o N; version:S no vacío o N; source_sha256:H o N; qualified:B |
| pytest/plugins_end → PluginsEnd | count:U |
| pytest/options → OptionsClaim | effective_sha256:H; profile_match:B |
| pytest/item → CollectedItem | nodeid:S no vacío; property:B |
| pytest/collect_report → CollectionReport | nodeid:S (vacío permitido); outcome: passed/failed/skipped |
| pytest/deselected → DeselectedItem | nodeid:S no vacío; property:B |
| pytest/selected → SelectedItem | nodeid:S no vacío |
| pytest/collection_end → CollectionEnd | selected_count:U; deselected_count:U |
| pytest/test_start → TestStart | nodeid:S no vacío |
| pytest/phase_make → PhaseMake | nodeid:S no vacío; phase:setup/call/teardown; outcome:passed/failed/skipped; exception_present:B; exception_type:S no vacío o N; wasxfail:B; xfail:XfailObservation o N |
| pytest/phase_log → PhaseLog | nodeid:S no vacío; phase:setup/call/teardown; outcome:passed/failed/skipped; wasxfail:B |
| pytest/test_end → TestEnd | nodeid:S no vacío |
| pytest/internal_error → InternalError | exception_type:S no vacío |
| pytest/interrupted → Interrupted | exception_type:S no vacío |
| pytest/session_end → SessionEnd | argument_exit:int0..255; observed_exit:int0..255 |
| pytest/session_end_error → SessionEndError | exception_type:S no vacío |

utc exige formato `YYYY-MM-DDTHH:MM:SS.ffffff+00:00`, fecha/hora válida; se
valida por stdlib sin consultar reloj. Diferencia UTC negativa es posible por
ajuste de reloj: no se usa para ordenar ni medir duración. monotonic_ns final
de cada proceso debe ser≥inicial. Entre procesos no se exige wallclock estable.

exception_present false exige exception_type None; true exige no vacío.
xfail usa run/strict/raises_present bool exactos. Nunca reevalúa marker o raises.
El schema conserva excepciones por tipo como diagnóstico, no clasifica por
nombre de clase ni por frases `[XPASS(strict)]`. No reason/longrepr arbitrario.

PluginClaim.qualified, OptionsClaim.profile_match, versiones y hashes de
runtime son **claims del emisor**: se guardan sin verificarlos contra un
inventario externo inexistente. No crean runtime_unqualified ni un certificado
positivo dentro de P03a. P03b/c/P05 evaluarán la calificación con su ancla.
Un booleano false también se conserva; el kernel no lo convierte en true.

## 4. Decoder: precedencia, prefijo y datos parciales

Validar primero header completo/canónico y refs. Si falla, events vacío,
consumed_bytes0, tail_sha256 de data entero y finding offset0. Header válido
se consume y guarda referencias lógicas; EOF inmediatamente posterior no
inventa una ejecución. Por cada línea de evento, precedencia del primer defecto:

1. Límite de línea, UTF-8, LF y JSON/duplicate keys/depth/float.
2. Aridad exacta del array exterior, event_code y clase payload.
3. Aridad/campos/rangos del payload, referencia nodeid y coherencia de campos.
4. execution_index y tabla de declaraciones; reconstrucción de refs desde header.
5. seq/local_seq, límites individuales de inventarios.

Al primer defecto, no incorporar esa línea ni ninguna posterior. Retorna todos
los eventos anteriores aceptados con offset/end_offset reales, un finding con byte offset del inicio de la
línea defectuosa, consumed_bytes hasta ese offset y tail_sha256 SHA256 de todo
el sufijo conservado en data. Si termina exactamente en LF y no hay defecto,
consumed_bytes=len(data), tail_sha256=None. data vacío retorna events/findings
vacíos, consumed_bytes0; reconcile añade ausencias, no inventa EOF verdadero.

Los findings de decoder son solo:
`limit_exceeded`, `invalid_encoding`, `truncated_line`, `invalid_json`,
`noncanonical_json`, `unknown_schema`, `unknown_field`, `invalid_field`,
`unknown_event`, `foreign_reference`, `sequence_error`.
JSON válido con claves duplicadas se clasifica invalid_json; campo requerido
ausente invalid_field; campo extra unknown_field; versión/record_type diferente
unknown_schema. Tipo/rango JSON errado invalid_field, distinto de TypeError
reservado a tipos públicos API. event_code no reconocido produce unknown_event.
Cabecera con campo extra es unknown_field; schema_version bool es
invalid_field antes de comparar versión, diferente versión int es unknown_schema.
Aridad mayor/menor de vector es invalid_field; event_code desconocido
unknown_event. Una clave textual fuera de un objeto de header no existe como
campo opcional del wire: vector con objeto en lugar de array es invalid_field.
Línea sin LF produce truncated_line aun si JSON del fragmento parece completo.
Nodo excediendo4096 produce invalid_field; inventario excediendo10000
limit_exceeded. Tail no se devuelve como texto ejecutable ni se descarta
silenciosamente. Un prefijo cortado nunca tiene protocol_complete=True.

Estos findings son de bytes aportados; no se afirma que el canal real fue
truncado por pytest. Un supervisor puede aportar un evento channel_end con
defecto incluso con JSON completo: ese hecho se procesa en la FSM.

## 5. FSM del reconciliador y terminación

El reconciliador conserva **todos** los findings semánticos sobre el prefijo
válido, sin abandonar ante el primer FAIL. No cambia el prefijo ni reordena
los eventos. Crea dos ExecutionObservation en orden de expectativas; si no
hay eventos de una ejecución, campos-tupla vacíos, exit_code=None,
termination=`unobserved`, protocol_complete=False y missing_execution.

Máquina global: collection-1 primero; producer-1 no comienza antes del
execution_end de collection-1. El cambio prematuro agrega execution_order;
no se trasplantan eventos a otra ejecución. Cada ejecución requiere exactamente
un execution_start; evento anterior a start o posterior a end → event_order,
sin descartarlo del journal. Duplicar eventos singleton → duplicate_event.

Ejecución ausente agrega solo missing_execution, no cada callback que nunca
empezó. Si hubo start pero faltan cierres, agrega ausencias aplicables al final
del prefijo, exit_code=None/termination=unobserved si no se vio execution_end.
Singleton duplicado no reemplaza el primero en campos resumidos. Declaraciones
nodeid pueden aparecer durante sesión activa, antes de cada referencia nueva;
no cambian la FSM de callbacks ni satisfacen un item/selected.

Máquina local normal:

```text
execution_start
session_start
options
colección: item*, collect_report*, deselected*, selected*, collection_end
tests del productor: (test_start, fases coherentes, test_end)*
plugins_end
session_end
channel_end
execution_end
```

`plugin` puede aparecer en cualquier punto entre session_start y plugins_end,
incluso durante tests: plugins tardíos se preservan. plugins_end.count coteja
cantidad de PluginClaim sin deduplicar; names repetidos → duplicate_plugin.
Items/collect_reports pueden intercalarse antes de collection_end; selected y
deselected no aparecen antes de sus item ni después de collection_end.
options exactamente una vez antes del primer item/collect_report.
collection_end exige conteos iguales a los eventos selected/deselected.
Un collect_report failed o skipped agrega collection_report_nonpass y conserva
la colección parcial. Su nodeid identifica collector, no una obligación test.

Plugins_end es cierre de inventario, justo antes de session_end en la ruta
normal, no promesa de que solo los plugins iniciales existan. Collection role
no admite test_start/phase/test_end; producer solo tests después de collection_end.
Un test no puede solaparse con otro en este perfil secuencial. Fases ajenas al
test activo o test_end de otro nodeid → test_order. Fase huérfana queda en
events/findings, no crea TestObservation. Cada test_start crea instancia; si
había otra activa, la anterior queda incompleta con missing_test_end. No se
fusionan por compartir nodeid. Tests con ID seleccionado
ausente → unexpected_test, además de findings de P01 posteriores.

internal_error/interrupted/session_end_error están permitidos como eventos
diagnósticos mientras sesión está activa. Marcan protocolo incompleto; no
equivalen a session_end normal. Tras diagnóstico todavía se permiten cierres
session_end/channel_end/execution_end y otro diagnóstico, sin fabricar fases.
session_end_error y session_end son alternativas: ambos → duplicate_event.
Un crash puede ir de cualquier estado a channel_end/execution_end: no es error
de parser, pero faltan sesión/fases/cierres y se conservan esos findings.

channel_end exactamente una vez precede execution_end. EOF normal:
eof=True, tail_bytes=0, tail_sha256=None, defect=None. Cola>0 exige H y
defect=`truncated_channel`; eof puede false. eof=False/cola0 exige defect
`io_error`, `timeout`, `cancelled` o `limit_exceeded`. Para estos cuatro
defectos, cola puede>0 con su hash; no imponer un hash vacío por defecto.
Otras combinaciones → channel_inconsistent. Cada defecto no-null agrega
channel_defect; sin channel_end agrega missing_channel_end.

Consistencia exit/termination/signal:

| termination | exit_code y signal permitidos |
|---|---|
| exited | exit_code0..255 no null, signal=None |
| signal | signal1..64, exit_code=-signal |
| launch_error | exit_code=None, signal=None; no session ni fases legítimas |
| timeout/cancelled/io_error/limit_exceeded | si hijo terminó naturalmente: exit_code0..255 y signal=None; si fue señalado: exit_code=-signal, signal1..64; si no se pudo observar: ambosNone |
| unobserved | salida sintetizada cuando falta execution_end, nunca admitido en wire |

Cualquier otra combinación → termination_inconsistent; no reinterpretar
números negativos como éxito. execution_end.log_end≥execution_start.log_start,
monotonic_ns final≥inicial; offsets contiguos entre procesos: primer log_start0,
segundo log_start=log_end previo. Error → execution_bounds. Log hash identifica
segmento declarado pero no se verifica sin bytes de log. log_truncated true
agrega log_truncated; no es terminal completo de evidencia.

session_end.argument_exit/observed_exit se preservan. Si termination=exited y
exit_code != observed_exit, finding exit_disagreement. **No sustituir**
exit_code por hook; esa divergencia puede venir de cleanup real, no se acusa
manipulación sin evidencia. argument_exit distinto de observed_exit es dato
válido de hook, no por sí solo defecto. Exit1 por test fallido con protocolo
íntegro puede ser completo; exit2/3/4/5 u otro no0/1 agrega abnormal_exit.
Una colección-only íntegra con exit0 es completa; productor con exit0/1
necesita fases/cierres íntegros. Esto no decide piso de cobertura ni rechazo P05.

protocol_complete=True solo si están todos los cierres/counts/eventos
estructurales requeridos, sin findings de decoder/FSM para la ejecución,
sin diagnósticos ni canal/log truncados y exit admisible. Un fallo nativo de
call con teardown y exit1 **no** es defecto de protocolo. Selección errónea
puede tener protocolo completo: se reporta separadamente por inventarios.

## 6. Fases y disposición nativa, sin confundir ejecución con éxito

Pareja make/log única por **(execution_id,test_start.seq,phase)**, make antes
de log. test_start.seq identifica una instancia, no la identidad del test.
Dos instancias secuenciales del mismo nodeid pueden tener ambas setup/call/
teardown y ser terminales; no se confunden con fases duplicadas dentro de una
instancia. TestObservation.start_seq conserva esa distinción. Para cada pareja,
nodeid/phase/outcome/wasxfail deben coincidir. Falta o diferencia →
report_pair_mismatch. Se conserva PhaseObservation desde make válido aunque
falta log; una fase únicamente log no fabrica metadata make: queda finding,
no PhaseObservation inventada. phases conserva una PhaseObservation por cada
phase_make estructuralmente válida de la instancia en orden observado,
incluyendo duplicados que invaliden su terminal; ningún dict por phase oculta
ese defecto. Los eventos originales permanecen disponibles.

Orden setup→call→teardown; inversión de ese orden agrega phase_order.
Setup passed exige call y teardown; setup failed/
skipped omite legítimamente call pero exige teardown. No call inventada.
Call presente después de setup no-PASS → unexpected_phase; cualquier fase
repetida → duplicate_phase; ausente requerida → missing_phase. El terminal
requiere test_start/test_end únicos, pares completos/coherentes, orden válido
y fases requeridas; un test fallido puede ser terminal=True.

Orden de reglas de disposition (primera aplicable):

1. outcome passed + exception_present=True → inconsistent.
2. skipped + wasxfail=True → xfail.
3. passed + wasxfail=True → xpass (si no es call, inconsistent).
4. failed + phase=call + exception_present=False + xfail.strict=True
   → xpass_strict.
5. failed → failed.
6. skipped → skipped.
7. passed + phase=call + xfail.strict=True → inconsistent.
8. restante passed → passed.

inconsistent agrega report_inconsistent. No clasificar por exception_type.
XFAIL explícito puede tener xfail=None; raises mismatch puede failed con
marker activo. Stash en setup/teardown no-PASS no se transforma por heurística.
Caller puede falsificar metadata: provenance sigue sin verificar.

call_disposition: observed si hubo make call; not_scheduled si setup no-PASS
coherente y call ausente; missing en otro caso. pass_eligible=True únicamente
terminal=True y exactamente tres PhaseObservation con disposition=passed,
sin finding de ese test. No exige éxito de otros tests ni convierte el
protocolo global en acreditación. Una prueba pasa pero teardown falla:
terminal=True, pass_eligible=False y el fallo queda visible.

## 7. Inventarios, findings y precedencia de salida

Se preservan orden y duplicados de item/selected/deselected/test_start/end en
eventos y tuplas. Items previos = selected + deselected por multiconjunto;
cada deselected debe property=True y corresponder a property_ids revisados.
Deselected con marca cambiada respecto a item agrega property_marker_changed.
Selected property agrega unauthorized_selection. Todo ID esperado property
debe aparecer en deselected, sin extras; no permitir una cantidad igual con
otra identidad. No se acepta un item retirado silenciosamente.

preflight_identities = P01(expected, selected collection, selected producer).
identities = P01(expected, selected producer, nodeids terminales del productor).
Estas son expresiones de negocio: la API vigente se invoca con keywords
`compare_identities(expected=..., collected=..., executed=...)`, no posicionales.
No usar pass_eligible como executed: FAIL terminado también fue ejecutado.
Cada repetición completa del mismo test produce un TestObservation adicional,
con otro start_seq, para que P01 detecte duplicado; no dict por nodeid previo
que la pierda. La unicidad de pareja de §6 es por instancia: estas repeticiones
no generan duplicate_phase solo por repetir nodeid y nombres de fase.
Repeticiones
incompletas también conservan eventos/findings, aunque no sumen terminal.

Catálogo cerrado de findings semánticos:
`missing_execution`, `execution_order`, `event_order`, `duplicate_event`,
`missing_session_start`, `missing_options`, `missing_collection_end`,
`collection_count_mismatch`, `collection_report_nonpass`, `duplicate_plugin`,
`plugin_count_mismatch`, `missing_plugins_end`, `missing_session_end`,
`missing_channel_end`, `missing_execution_end`, `channel_inconsistent`,
`channel_defect`, `termination_inconsistent`, `execution_bounds`,
`exit_disagreement`, `log_truncated`, `abnormal_exit`,
`internal_error`, `interrupted`, `session_end_error`, `test_order`,
`unexpected_test`, `report_pair_mismatch`, `phase_order`, `duplicate_phase`,
`missing_phase`, `unexpected_phase`, `missing_test_end`,
`report_inconsistent`, `selection_mismatch`, `unauthorized_deselection`,
`unauthorized_selection`, `property_marker_changed`,
`missing_property`, `unexpected_property`, `duplicate_property`.

property_findings contiene últimos seis códigos relativos a property
(unauthorized_deselection/selection/marker/missing/unexpected/duplicate).
No incluye selection_mismatch general. ProtocolFinding no tiene texto dinámico;
identifica execution/nodeid/phase/offset. Offset apunta al evento causante;
para ausencia al finalizar ejecución es None. Finding global de decoder sin
execution identificable tiene execution_id=None y afecta completitud de ambas.

Orden determinista: findings decoder primero (máximo uno), después por
execution expectation (collection,producer), luego por offset ascendente,
None después, code lexicográfico y nodeid/phase (None antes de strings).
Duplicados exactos del mismo finding se emiten una sola vez tras detectarlos;
duplicados de eventos/identidades **no se eliminan**. PytestObservation.findings
es unión ordenada de decoder, FSM y property/selection. IdentityComparison
conserva su propio orden/catálogo P01, no se inserta como otro ProtocolFinding.

No resumen invalid>incomplete>rejected>accredited en P03a: eso pertenece a P05.
No hacer que una causa dominante borre otra ni elevar una observación nativa
a PASS global. La tabla define hechos puros, no un segundo motor de gates.

## 8. Golden de protocolo y capacidad conjunta

Golden compacto literal: `golden-compact.jsonl`, 1938 bytes, cabecera más29
eventos, SHA-256
`52eed49e69f6d98da227347396eaa42a57d0c854e93cd662c75d9e76173a6730`,
en custodia de [SONDA-P03](SONDA-P03.md). Primeras dos líneas:

```json
{"executions":[["collection-1","collection","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"],["producer-1","producer","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]],"record_type":"wct-pytest-journal","run_id":"00000000000000000000000000000000","schema_version":1}
[1,0,null,1,[["python","-m","pytest"],"/r",0,1,"2026-09-08T00:00:00.000000+00:00"]]
```

Cada línea restante está congelada en el archivo literal, no regenerada con
el SUT. El coder incorpora esos bytes como literal en los tests autorizados;
la suite entregada no depende de que sobreviva una ruta build/tmp del specifier.
Dos ejecuciones completas, un test t, sin properties/plugins declarados,
log vacío por proceso; expected=(t,), property_ids=(), max_bytes=1938.
Resultado esperado: consumed_bytes1938, tail_sha256None, findings vacíos;
dos protocol_complete=True/exits0; productor un test terminal/pass_eligible
True, setup/call/teardown passed y call_disposition observed; ambos P01 match.
provenance permanece caller-supplied-unverified; plugins count0 no acredita
calificación. max_bytes1937 debe lanzar limit_exceeded antes de decodificar.

La versión verbose previa golden8415 bytes y su cálculo mínimo de30,48 MB
para10 000 tests son **históricos retirados**, no cabida del codec actual.
El codec compacto fue dimensionado con404 nodeids no-property coleccionados
realmente en main34bd572, sin ejecutar tests, y crecimiento sintético explícito:

| Escenario | IDs reales / sintéticos | JSONL simulado |
|---|---|---:|
| main actual | 404 / 0 | 198658 bytes |
| crecimiento inicial +177 | 404 / 177 | 314053 bytes |
| candidato P02a reportado:644 normales +1 property | 404 / 240 | 355192 bytes para normales |
| margen650 normales | 404 / 246 | 359110 bytes |
| margen1000 normales | 404 / 596 | 590685 bytes |
| escenario1500 normales | 404 / 1096 | 935185 bytes |

IDs sintéticos234 bytes, más largos que máximo real196. Son **simulaciones de
framing con fases PASS impuestas**, no ejecuciones, evidencia del candidato
ni predicción de todos los futuros errores/plugins/collector records.
Inventory filesystem de planificación del worktree:589 regulares,
array de metadata97840 bytes, sin hashing de contenido ni captura Git/P02a.
Contexto/spec/Git/owner/terminal/expectations faltan en ese tamaño parcial.

P1 mantiene **2 MiB de metadata JSON conjunta**, no2 MiB por archivo. P03a
acepta max_bytes obligatorio aportado; no impone una partición fija ni cambia
los límites válidos P02a/P02b. P03c/P06 deberán calcularlo de presupuesto2MiB
menos bytes reales de inputs/owner/otra metadata y reserva terminal justificada,
contando ambos nombres terminales conforme P02b. No duplicar todas las fases
en el terminal: referencias resolubles a journal/hashes preservan la información
sin otra copia. Ese ensamblaje y reserva deben aprobarse en P04/P06.

Ejemplo **estimado, no política** de cabida: input512KiB + journal1024KiB +
owner4KiB +2 terminales de192KiB +resto124KiB=2048KiB. El escenario1500 ocupa
935185 bytes, bajo ese ejemplo de journal, dejando113391 bytes para registros
no modelados; no acredita que el total real de la cadena quepa. El target
644+1 tiene margen sustancial bajo ese modelo; property/collectors/errores
reales deberán medirse al integrar. Nunca elevar presupuesto ni reducir IDs
para obtener verde; si ledger real no da margen, bloqueo explícito.

Los topes individuales10 000 no prometen cabida10 000 bajo el presupuesto
conjunto. max_bytes limita el journal, y provenance afirma únicamente datos
aportados; llamar al decoder con2MiB no certifica que no existan otros2MiB en
inputs. El ledger supervisado y su comprobación final son responsabilidad
posterior, no una dependencia que impida construir el kernel puro.

## 9. Feature P03a y mapa literal de tests puros

Esta es la **única feature del corte P03a**. No afirma ejecución nativa de
pytest: consume journals sintéticos/literales como SUT puro.

```gherkin
Feature: Reconciliacion pura de observaciones pytest
  # SH-P03a/1: datos aportados, no ejecucion ni procedencia acreditada.
  Scenario Outline: Distinguir observaciones y defectos del protocolo
    Given el journal literal del caso "<case>"
    When reconcilio sus observaciones con expectativas revisadas
    Then el campo "<field>" tiene el valor literal "<expected>"

    Examples:
      | case | field | expected |
      | PA01 | protocol_complete | true |
      | PA02 | decoder_prefix_preserved | true |
      | PA03 | framing_defect_visible | true |
      | PA04 | phase_defect_visible | true |
      | PA05 | failed_terminal_preserved | true |
      | PA06 | identity_substitution_detected | true |
      | PA07 | property_mismatch_detected | true |
      | PA08 | exit_not_replaced | true |
      | PA09 | exact_boundary_allowed | true |
      | PA10 | over_boundary_rejected | true |
      | PA11 | provenance | caller-supplied-unverified |
      | PA12 | invalid_argument_rejected | true |
```

Nodeid exacto por cada ID literal siguiente:
`tests/unit/test_pytest_observation.py::test_observation_case[ID]`.
No nombres de casos nativos PT del dossier anterior en este corte.

| Familia | IDs literales y obligación |
|---|---|
| PA01 | `PA01-golden`, `PA01-permuted-opaque-nodeids`: control completo válido; no ordenar bytes del journal para fingir seq |
| PA02 | `PA02-invalid-utf8`, `PA02-invalid-json`, `PA02-duplicate-root-key`, `PA02-duplicate-nested-key`, `PA02-noncanonical`, `PA02-no-final-lf`, `PA02-empty`: prefijo/offset/hash exactos; vacío missing_execution |
| PA03 | `PA03-schema`, `PA03-event-code`, `PA03-extra-field`, `PA03-missing-field`, `PA03-global-seq-gap`, `PA03-local-seq-gap`, `PA03-seq-repeat`, `PA03-foreign-run`, `PA03-foreign-execution`, `PA03-reference-digest`, `PA03-supervisor-local-seq`, `PA03-node-reference-missing`, `PA03-node-declaration-repeat-index`, `PA03-node-declaration-repeat-string`, `PA03-node-before-declaration`, `PA03-header-execution-order`, `PA03-float`, `PA03-bool-int`, `PA03-depth` |
| PA04 | `PA04-no-make`, `PA04-no-log`, `PA04-pair-outcome`, `PA04-pair-wasxfail`, `PA04-phase-order`, `PA04-duplicate-phase`, `PA04-no-teardown`, `PA04-no-test-end`, `PA04-call-after-nonpass-setup`, `PA04-overlap`, `PA04-collection-has-phases`, `PA04-passed-raw-exception` |
| PA05 | `PA05-call-failed`, `PA05-setup-failed`, `PA05-teardown-failed`, `PA05-setup-skipped`, `PA05-call-skipped`, `PA05-xfail`, `PA05-xfail-explicit-setup`, `PA05-xfail-teardown`, `PA05-xpass`, `PA05-xpass-strict`, `PA05-inactive-marker`, `PA05-raises-mismatch`: outputs literal según §6, no SUT generando expected |
| PA06 | `PA06-same-count-replacement`, `PA06-duplicate-item`, `PA06-duplicate-selected`, `PA06-duplicate-terminal`, `PA06-silent-drop`, `PA06-collection-producer-diverge`, `PA06-empty-expected` |
| PA07 | `PA07-valid-property`, `PA07-normal-deselected`, `PA07-property-selected`, `PA07-property-missing`, `PA07-property-extra`, `PA07-property-duplicate`, `PA07-property-marker-change` |
| PA08 | `PA08-exit-zero-no-session-end`, `PA08-exit-disagrees`, `PA08-hook-argument-changed`, `PA08-signal-valid`, `PA08-signal-mismatch`, `PA08-launch-error`, `PA08-timeout-null`, `PA08-timeout-signalled`, `PA08-bounds`, `PA08-log-truncated`, `PA08-internal-error`, `PA08-interrupted`, `PA08-session-end-error`, `PA08-channel-tail`, `PA08-channel-inconsistent`, `PA08-producer-before-collection-end`, `PA08-duplicate-start`, `PA08-after-execution-end` |
| PA09 | `PA09-line-exact`, `PA09-journal-exact`, `PA09-nodeid-exact`, `PA09-items-exact`, `PA09-selected-exact`, `PA09-deselected-exact`, `PA09-test-start-exact`, `PA09-phase-make-exact`, `PA09-phase-log-exact`, `PA09-test-end-exact`, `PA09-expected-exact`, `PA09-property-ids-exact` |
| PA10 | `PA10-line-plus-one`, `PA10-journal-plus-one`, `PA10-nodeid-plus-one`, `PA10-items-plus-one`, `PA10-selected-plus-one`, `PA10-deselected-plus-one`, `PA10-test-start-plus-one`, `PA10-phase-make-plus-one`, `PA10-phase-log-plus-one`, `PA10-test-end-plus-one`, `PA10-expected-plus-one`, `PA10-property-ids-plus-one` |
| PA11 | `PA11-plugin-claim-false`, `PA11-plugin-claim-true`, `PA11-unknown-version-claim`, `PA11-options-claim-false`, `PA11-opaque-context`: claims cambian datos, no provenance |
| PA12 | `PA12-data-type`, `PA12-max-bytes-type`, `PA12-max-bytes-zero`, `PA12-max-bytes-over-absolute`, `PA12-run-value`, `PA12-reference-order`, `PA12-reference-duplicate`, `PA12-observation-type`, `PA12-observation-incoherent`, `PA12-expected-list`, `PA12-expected-duplicate`, `PA12-expected-property-overlap`, `PA12-property-list`, `PA12-property-duplicate` |

Variantes literales adicionales del challenge, con el mismo prefijo de nodeid:

- `PA01-golden-offsets`: primer evento [573,657), último end_offset1938;
  offsets/end_offsets iguales a las fronteras reales de las29 líneas, sin
  añadir campos al wire. TestObservation.start_seq del único test es18.
- `PA01-unicode-byte-offsets`: sustituir nodeid t por é en su única declaración;
  todos los offsets posteriores a esa línea aumentan **un byte**, no un
  carácter contado como ASCII. El control literal t sigue pasando.
- `PA04-same-instance-duplicate-make` y `PA04-same-instance-duplicate-log`:
  duplicación dentro de una instancia produce duplicate_phase y terminal=False;
  fases/eventos repetidos siguen visibles, no dict previo por fase.
- `PA06-two-complete-instances-same-nodeid`: copiar el bloque íntegro
  test_start/fases/test_end antes del cierre de plugins, ajustando solo seq y
  local_seq. Start_seq18/26 identifican dos TestObservation terminal=True;
  ejecutados=(t,t) llegan intactos a P01 y devuelven invalid por
  duplicate_identity en executed. No duplicate_phase ni falso test_order por
  el mero hecho de compartir nodeid; pass_eligible local puede serTrue en ambas
  y nunca convierte el inventario duplicado en acreditado.
- `PA12-offset-negative`, `PA12-offset-bool`, `PA12-end-before-offset`,
  `PA12-offset-overlap`, `PA12-offset-gap`, `PA12-offset-wrong-header`,
  `PA12-end-over-consumed`, `PA12-consumed-over-max`, `PA12-last-end-mismatch`,
  `PA12-decoder-finding-offset-mismatch`: observation manual inconsistente,
  invalid_observation. El caso bueno usa intervalos derivados de bytes reales.

Para repetición dentro de una instancia, un segundo make o log del mismo
phase agrega duplicate_phase además de report_pair_mismatch por cardinalidad
no1-a-1. Este diagnóstico no aplica a la instancia posterior que posee otro
test_start.seq. Se conserva la regla de ordering de findings de §7.

Controles adicionales literales: `PA01-valid-control`, `PA02-valid-control`,
`PA03-valid-control`, `PA04-valid-control`, `PA05-valid-control`,
`PA06-valid-control`, `PA07-valid-control`, `PA08-valid-control`,
`PA09-valid-control`, `PA10-valid-control`, `PA11-valid-control`,
`PA12-valid-control`. Cada negativo tiene control equivalente bueno; no
rechazar todo. Los mapas son obligación de colección futura, no corridas hechas.

Bordes de inventarios se aíslan con constantes internas reducidas en fixtures
y bytes suficientes, reportando límites efectivos; no flag público de bypass.
La prueba literal data2MiB pasa max_bytes=2MiB y se puede rellenar con eventos plugin válidos antes
de plugins_end sin exceder64KiB/línea, ajustando count/seq. No relleno whitespace
no canónico que active otra causa primero. Nodeid4096 requiere línea mayor
pero bajo64KiB. +1 conserva la causa contractual, no cualquier error casual.

Binding exige Feature/Outline/nombre/keyword/texto/headers/cardinalidad/IDs/celdas
con positivo y alteración por campo. Generic handlers históricos no ejecutan
este vocabulario; contract tests invocan las dos APIs puras. El verifier coteja
expected literal, conjunto y multiplicidad de nodeids, sin dict prematuro.

## 10. Allowlist propuesta, calidad y puerta de coder

```text
tools/wct/evidence/pytest_observation.py
tools/wct/evidence/pytest_types.py
tools/wct/evidence/pytest_payloads.py
tools/wct/evidence/pytest_schema.py
tools/wct/evidence/pytest_phases.py
tools/wct/evidence/pytest_inventory.py
tests/unit/test_pytest_observation.py
tests/unit/test_pytest_schema.py
tests/unit/test_pytest_phases.py
features/wct-pytest-observation-001.feature
```

Diez rutas: seis fuentes, tres tests y feature. Composición pública→schema/
fases/inventarios→tipos/payloads; tipos/payloads no importan lógica ni pytest.
Payloads es contrato de wire, types es resultado de reconciliación: separación
cohesiva previa al código. No crear módulos vacíos ni API extra/export en
__init__. Archivo nuevo>100 sitios exige partición revisada, no claim anticipado
de medición. CRAP≤6, CC≤10, ≤500LOC, sin suppressions, cobertura/DRY/mutación
del scope tools real. No modificar P01/P02, governance, CLI, workflows o deps.

Antes de coder: challenge separado de este paquete y golden; decisión/hash
del arquitecto, base P01 integrada, allowlist/handoff exactos y recibo de
entendimiento. No hace falta completar plugin inventory o coverage recipe
para autorizar este **kernel puro**. Esos datos no serán acreditados aquí.
Coder no modifica este contrato ni el oráculo para pasar; verifier distinto
sobre digest final, tests sensibles y controles válidos. No bless automático.

P03b/c necesitarán contratos posteriores de callbacks/runtime/supervisión,
cuatro slots de P02b, límites conjuntos y recipe privada P04. La sonda nativa
documenta riesgos para ellos; no se implementan anticipadamente en P03a.
