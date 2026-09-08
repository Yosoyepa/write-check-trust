# SH-P02b — Posesión operativa de un workspace de evidencia

Estado: **propuesta del specifier, no aprobada para implementar**. Cohorte
B3-MA-D; `sh-delivery/2`, `wct-harness-local/2`. La delegación registrada en
[D1](DECISION-D1.md) permite al arquitecto aprobar esta pieza después del
challenge; no autoriza a este specifier ni al coder a autoaprobarla. Bless y
publicación continúan reservados al humano.

## 1. Afirmación y frontera

P02b reserva un directorio nuevo para un run, vincula su dueño operativo con
el snapshot P02a y proporciona una publicación terminal sin sobrescritura.
No copia fuentes, ejecuta tests, decide `accredited`, acredita frescura ni
recupera runs abandonados. Un directorio privado evita colisiones cooperativas;
**no es un sandbox contra otros procesos del mismo UID**, ni autentica al
productor, ni hace atómicas todas las lecturas del proyecto.

Consumidores: P03 escribe los eventos/logs de su ejecución; P04 identifica y
valida el LCOV; P06 conserva el handle durante toda la cadena y vuelve a
capturar inputs. Esta pieza no cambia el contrato aprobado de
[P02a](PROPUESTA-P02a.md), [P1](../specs/SPEC-B3-P1-evidencia.md) ni la
[secuencia](CADENA-P03-P06.md).

## 2. Reutilización antes de construcción

Lectura del árbol documental sobre `0228acc6` y búsqueda de `workspace`,
`flock`, `O_EXCL`, `mkdtemp`, `TemporaryDirectory` y `rmtree` en `tools/wct`:

| Componente | Decisión y motivo |
|---|---|
| `evidence.input_types.InputSnapshot`, `RootBinding` propuestos/aprobados en P02a | Consumir sin duplicar tipos; esperar API implementada y revisada antes de coder P02b |
| `evidence.input_manifest` de P02a | No hay helper público de codec prometido. No inventarlo ni importar privados: P02b tiene validación pura de binding; terminal usa stdlib con contrato propio |
| `selftest/redteam.py`, `accept/pipeline.py`, `gate/runner.py`: `TemporaryDirectory` | No reutilizar como lifecycle: borra al salir y no conserva run/propietario; no modificar estos consumidores |
| `util.git` | No aporta propiedad de outputs; P02b no necesita nuevos comandos Git |
| stdlib `os`, `stat`, `hashlib`, `json`, `threading` | Basta inicialmente; descriptor relativo, creación exclusiva y publicación no-clobber. Sin dependencia, registry ni Protocol ornamental |

El coder registra nombres/firmas finalmente reutilizados. Si la implementación
de P02a requiere un adaptador público adicional, se propone un diff separado;
no se ensancha su allowlist retroactivamente. Este documento define conducta
y operaciones observables, no prescribe una jerarquía de clases de IO.

## 3. API cerrada propuesta

Importación desde `tools.wct.evidence.workspace`:

```text
create_workspace(parent: pathlib.Path, *, snapshot: InputSnapshot,
                 run_id: str) -> WorkspaceLease

WorkspaceLease.ref -> WorkspaceRef
WorkspaceLease.check() -> WorkspaceRef
WorkspaceLease.finish(*, termination: str, record: bytes) -> TerminalRef
WorkspaceLease.close() -> None
```

`WorkspaceLease` es un recurso operativo, no dataclass serializable ni token
criptográfico. Solo lo fabrica `create_workspace`; no hay `open`, `resume`,
`takeover`, `force`, constructor público de un lease válido ni búsqueda del
último run. Su instancia conserva descriptores y serializa sus operaciones:
dos llamadas concurrentes a finish no publican dos terminales. Un handle
heredado por fork se rechaza por PID observado distinto; descriptores no se
heredan a exec. No imprimir secretos, contenido del record o entorno.

Tipos de salida: dataclasses frozen, colecciones tuplas, campos en este orden:

| Tipo | Campos y significado |
|---|---|
| `WorkspaceRef` | `schema_version=1`, `run_id`, `path` absoluto local, `root: RootBinding`, `input_sha256`, `owner_sha256`, `device`, `inode`, `artifacts` |
| `ArtifactLocation` | `kind`, `path` relativo al workspace; ubicación reservada, **no artefacto producido** |
| `TerminalRef` | `run_id`, `path="terminal.json"`, `sha256`, `size`, `termination` |
| `WorkspaceError` | excepción con `code`, `path` relativo opcional y `errno` opcional; mensaje humano no normativo |

`run_id` es exactamente 32 caracteres hex minúsculos. El caller lo genera
antes de crear; ningún fallback a timestamp/PID ni autoincremento ante choque.
`parent` debe ser exactamente `Path(snapshot.root.path)/"build/tmp"`, absoluto
y sin symlinks en sus componentes. Debe existir como directorio: P02b **no crea
los padres**, no cambia permisos ajenos ni resuelve traversal. P06 preparará
esa precondición mediante un contrato explícito; no atribuirla a P02a read-only.

Estructura inicial exacta, creada sin heredar permisos amplios:

```text
build/tmp/wct-run-<run_id>/        modo 0700
  owner.json                     regular, modo 0600
  inputs.json                    manifest P02a byte-exacto, modo 0600
  artifacts/                     modo 0700, inicialmente vacío
  logs/                          modo 0700, inicialmente vacío
```

`artifacts` de WorkspaceRef enumera estas cuatro ubicaciones, no existencias:
`coverage-db → artifacts/.coverage`, `lcov → artifacts/lcov.info`,
`execution-events → artifacts/events.jsonl`, `execution-log → logs/pytest.log`.
No se crea archivo vacío para aparentar que un productor terminó. No se
aceptan paths arbitrarios de artefacto en esta API. Colección/eventos múltiples
y logs separados requerirán la revisión P03 antes de ampliar estas ubicaciones.

La API valida tipos antes de IO (`bool` no int, tupla no lista, Path no str).
Error estructural → TypeError; valores fuera del contrato → invalid_request.
Antes de crear, verifica que SHA256(snapshot.manifest) coincide con sha256 y
que su JSON canónico coincide con los campos semánticos del snapshot según
P02a. La función interna pura de `workspace_snapshot` recibe InputSnapshot,
comprueba tipos, esquema exacto, fields y SHA; no hace IO ni llama
capture_inputs. Compara spec/context/files/git y exclusion_rules_version
conforme §6 de P02a, excluyendo root/exclusions del manifest. No supone una API
pública adicional de P02a. No acepta un dataclass con fields contradictorios.
No recaptura inputs ni convierte ese cotejo en autenticación del caller.
La identidad física de la raíz debe coincidir con RootBinding al crear y en
cada check/finish; un snapshot antiguo con raíz reemplazada falla.

## 4. Posesión, colisión y límites de rutas

Creación mediante una operación exclusiva del directorio final relativo a un
descriptor del padre comprobado; nunca `exists` seguido de reutilización.
Cualquier entrada final existente (directorio, archivo o symlink, incluido
roto) → `workspace_exists`; no leerla, repararla ni borrarla. Esta precedencia
permite conservar exactamente toda entrada ajena.

Componentes anteriores symlink → `symlink_workspace`; FIFO/socket/dispositivo
→ `unsupported_entry`. Validar con no-follow y descriptores de directorios,
no `resolve().is_relative_to(...)` seguido de aperturas por path. Mantener y
recomprobar identidad dev/inode de raíz, padres, workspace y directorios propios.
Una sustitución/desaparición observable → `ownership_lost`. No reconectar al
nuevo path ni reintentar con otro ID. Montajes o escritores hostiles no están
calificados: Linux local inicialmente, no garantía NFS/Windows.

Tras reservar el directorio, cualquier error conserva lo ya creado como
parcial; no se retorna un lease válido. Directorio parcial sin owner completo
no se vuelve a reclamar. Pérdida del proceso/kill conserva el directorio y sus
bytes. Cerrar el handle solo libera descriptores; **no limpia archivos**.

La exclusividad es por `(parent físico, run_id)`. Dos procesos simultáneos con
el mismo par: exactamente un lease, el otro workspace_exists. IDs distintos
pueden coexistir, incluso sobre el mismo root estable; P03/P06 deben demostrar
que sus productores no escriben rutas históricas compartidas. Dos roots con
iguales inputs y nodeids tienen RootBinding y workspaces distintos. Digest
portable igual nunca permite consumir outputs del otro root/run.

`check` verifica vínculo físico y bytes exactos de owner/inputs. Recorre solo
el workspace propio sin seguir enlaces; rechaza symlinks internos, externos y
rotos, nodos especiales y archivos regulares con enlaces duros ajenos
(`st_nlink != 1`, salvo el par terminal propio descrito en §5). No sigue otros
workspaces. Paths internos tienen gramática P02a. Esto detecta estado observado,
no evita que un productor hostil cambie luego un path. P04 vuelve a verificar
la identidad al abrir/consumir el artefacto; un check previo no basta.

check permite regulares y subdirectorios adicionales dentro de artifacts/logs
sujetos a esa gramática, tipo y límites; **no certifica el esquema ni inventario
completo de outputs**. Las cuatro ubicaciones son el acuerdo inicial de los
consumidores, no una allowlist de todos los archivos producidos. El registro y
rechazo de artefactos extras relevantes pertenece a P03/P04/P06. Fuera de esos
dos directorios solo admite owner.json, inputs.json y los dos nombres terminal.
Otra entrada en ese nivel → unsupported_entry. Esta distinción permite caches
internas del productor sin fabricar acreditación a partir de su presencia.

Límites de check: 10 000 entradas incluyendo directorios y 250 MiB sumando
tamaños de regulares; exacto admitido, uno más `limit_exceeded`. No lee datos
de logs/LCOV para sumar tamaños, ni afirma imponer cuota durante producción:
P03 debe supervisarla. Owner/inputs tienen lectura acotada a 2 MiB cada uno.
check no lee el terminal: limita su `st_size` a 2 MiB. finish limita los bytes
recibidos y serializados antes de escribir. Antes de mkdir se valida el límite individual de inputs. La suma
exacta owner+inputs se calcula **después** de mkdir y fstat: dev/inode propios
todavía no existen antes de reservar. Exceso combinado → limit_exceeded,
directorio parcial conservado, sin lease retornado ni reuso del ID. No estimar
inode con placeholder/upper bound que rechace casos exactos válidos. Bytes
mayores no se truncan ni se aceptan como registros completos.

Este tope combinado es presupuesto **adicional P02b**, no promesa heredada:
un manifest P02a válido de exactamente 2 MiB no cabe con su owner y recibe
limit_exceeded tras reservar el run. P06 debe tratarlo como límite visible
de ensamblaje, nunca acortar inputs ni cambiar el tope P02a para obtener verde.

## 5. Recibos, terminal y limpieza segura

owner.json es JSON UTF-8 canónico con codec P02a, LF final, campos exactos:
`schema_version:1`, `record_type:"wct-workspace-owner"`, `run_id`,
`input_sha256`, `root:{path,device,inode}`, `workspace:{device,inode}`.
La ruta absoluta es procedencia local explícita, **fuera** del manifest portable
de inputs. No tiene PID/reloj, secreto, hostname ni el propio digest.
owner_sha256 identifica sus bytes. No contiene claim de éxito ni snapshot final.

finish admite termination literal `finished` o `interrupted`; ambos significan
solo que el caller está publicando un terminal, no que tests pasaron. `record`
son bytes de JSON UTF-8 canónico, objeto, máximo 2 MiB, sin duplicados de clave
en ningún nivel, NaN, Infinity ni trailing content. Se admiten null, bool,
strings UTF-8 representables, arrays, objetos, enteros entre -(2**63) y
2**63-1 y floats finitos; 1e999 que desborda a infinito se rechaza. Máxima
profundidad 64 contenedores, sin pares surrogate sueltos. Codec terminal:
json.dumps con sort_keys=True, ensure_ascii=False, allow_nan=False,
separators=(',', ':') y LF final; reserializar debe coincidir byte a byte.
El número 1.0 conserva representación float, no se reduce a 1; -0.0 se conserva.
Esto es un contrato de terminal distinto del manifest P02a sin floats:
no reutilizar un validador P02a para este payload. Validación completa antes
de efectos. Su schema de
negocio pertenece a P06, no se inventa ahora una segunda envoltura de cierre.
La envoltura de almacenamiento exacta es:

```text
schema_version: 1
record_type: "wct-workspace-terminal"
run_id: ID del lease
owner_sha256: digest del owner
input_sha256: digest inicial P02a
termination: "finished" | "interrupted"
record: objeto recibido, sin reinterpretación
```

El límite de 2 MiB aplica también a la envoltura serializada, no solo al payload.
Antes de crear pending, finish serializa la envoltura y comprueba margen sobre
el inventario actual de check: `entradas_actuales + 2 <= 10000` y
`bytes_actuales + 2 * len(envoltura) <= 250 MiB`. Las entradas contadas son
descendientes del workspace; la raíz misma no suma una entrada. Los dos
nombres terminales suman dos entradas y dos tamaños, aunque compartan inode.
Igualdad exacta pasa; exceso de uno produce limit_exceeded sin crear pending
ni terminal, sin sellar el lease por ese error de presupuesto previo a efectos.
No truncar ni borrar logs para obtener margen. Esto evita que las propias
escrituras de finish dejen un workspace que inmediatamente incumpla check;
no garantiza exclusión de escrituras ajenas concurrentes del mismo UID.
El orden operativo es check y reserva lógica del margen → escritura exclusiva de `.terminal.pending`
0600 → fsync de archivo → publicación atómica **sin reemplazo** como
`terminal.json` mediante link relativo en el mismo directorio → fsync del
directorio. Solo entonces retorna TerminalRef. **Siempre conserva ambos
nombres**: `.terminal.pending` y `terminal.json`, regulares del mismo inode
con nlink exactamente 2. check permite ese par tanto después de éxito como
tras interrupción postlink; otro hardlink se rechaza. No ejecuta unlink, rmdir
ni eliminación alguna. Una limpieza futura requiere otro corte y custodia
previa; conservar el par elimina una operación destructiva innecesaria.
Nunca sobrescribir terminal
o pending preexistente, incluso si sus bytes parecen iguales.

Si fsync falla después de publicar, reportar io_error y conservar los
bytes; no afirmar que el terminal no existe ni emitir otro con el mismo run.
El lease pasa a estado interno terminal inmediatamente después de link exitoso,
antes del fsync; todo nuevo finish devuelve already_terminal incluso si la
llamada previa levantó io_error. Si falla antes del link y queda pending, el
lease queda igualmente sellado para finish: no hay reintento ni reescritura.
Un pending/terminal preexistente al primer finish devuelve already_terminal y
sella el lease, sin inferir autenticidad de esos bytes. check sigue disponible
para inspección conforme su contrato, sin reparar; close libera descriptores.
Consumidor futuro exige formato íntegro, identidad y cierre P06: terminal
presente por sí solo no acredita nada. check comprueba tipos/ubicaciones/nlink
del terminal, **no rehashea ni valida semánticamente su payload**; su vínculo
de bytes está limitado a owner/inputs. Cambiar bytes de terminal con igual
tipo/tamaño puede pasar check. P04/P06 deben abrir el mismo artefacto con
no-follow, calcular SHA y compararlo con TerminalRef conservado fuera del
archivo, además de validar formato/refs/cierre. Ni check ni un digest que el
propio terminal declare son prueba de autenticidad/frescura del terminal.
No garantizar supervivencia a corte de
energía en todos los filesystems. Antes del coder se debe ensayar el mecanismo
local y sus fallos (§9); si no soporta link/fsync, error, no fallback a replace.

finish exitoso deja el lease terminal: check sigue permitido; segundo finish
→ `already_terminal`. close es idempotente; check/finish posteriores →
`lease_closed`. close antes de finish deja run pendiente, nunca éxito. Excepción
o KeyboardInterrupt se propaga conservando parciales; no fabricar finished.
No hay borrado de runs antiguos, TTL ni recuperación automática: custodia
durable y eliminación humana son acciones separadas con inventario y hashes.

Catálogo cerrado adicional a TypeError: `invalid_request`, `invalid_parent`,
`snapshot_mismatch`, `workspace_exists`, `symlink_workspace`,
`unsupported_entry`, `ownership_lost`, `already_terminal`, `lease_closed`,
`foreign_process`, `io_error`, `limit_exceeded`, `unsupported_platform`.
Validación estructural → valores/snapshot → raíz/padre → mkdir → recibos.
En check: handle/proceso → identidad → recibos → recorrido. Primera causa
observada, sin afirmar inventario exhaustivo de defectos simultáneos.

## 6. Matriz observable mínima

Cada familia incluye control válido equivalente y aserciones literales sobre
resultados/bytes ajenos, no solo que se llamó un mock. Barreras reales de
proceso/descriptor para carreras; no sleeps ni hooks públicos de test.

| Caso | Preparación y resultado exigido |
|---|---|
| WB01 | Nuevo ID, snapshot real P02a: lease, owner correcto, inputs byte-exactos, artifacts/logs vacíos |
| WB02 | Directorio/archivo/symlink final existente: workspace_exists, bytes y destino intactos |
| WB03 | ID mayúsculo/corto/traversal; parent fuera de root/build/tmp; snapshot contradictorio: error antes de mkdir |
| WB04 | Symlink interno/externo/roto en componente de padre: symlink_workspace, destino intacto |
| WB05 | Padre ausente: invalid_parent; no creación de build/tmp implícita |
| WB06 | Dos procesos mismo ID: exactamente un éxito, un workspace_exists, owner del ganador intacto |
| WB07 | Dos IDs mismo root: dos leases; terminar A no altera un byte de B |
| WB08 | Dos roots/inputs portables iguales/tests homónimos: root/workspace distintos; intercambiar owner produce ownership_lost |
| WB09 | Sustituir raíz/padre/workspace tras crear: ownership_lost, nada escrito en sustituto |
| WB10 | Symlink hoja/directorio interno/externo/roto en artifacts: symlink_workspace, destino no leído |
| WB11 | FIFO/socket/hardlink ajeno: unsupported_entry, sin bloquear ni tocar el destino |
| WB12 | Permiso/IO fallido tras mkdir: io_error, parcial preservado y mismo ID no reutilizable |
| WB13 | Kill antes de terminal: bytes parciales permanecen, sin terminal completo ni éxito inferido |
| WB14 | finish finished con record literal {"result":"rejected"}: terminal conserva rejected, no traduce a éxito |
| WB15 | finish interrupted con record literal {"reason":"cancelled"}: terminal interrupted, causa conservada |
| WB16 | Segundo finish o terminal preexistente: already_terminal, primer terminal intacto |
| WB17 | Dos finish concurrentes en un lease: uno retorna, otro already_terminal, un terminal íntegro |
| WB18 | Fallo antes/link/después de publicación: pending parcial o par íntegro, nunca overwrite ni borrado de ninguna entrada |
| WB19 | close dos veces válido; check/finish después lease_closed; no terminal creado ni borrado de outputs |
| WB20 | Handle en hijo fork: foreign_process; padre aún puede terminar |
| WB21 | Cambiar owner/inputs con longitud conservada: ownership_lost; no reconstruir recibos |
| WB22 | Límites exactos de entradas/bytes/metadata: válidos; +1: limit_exceeded, sin truncamiento; inputs sobre límite falla antes de mkdir, combinado exacto sobre límite falla después y conserva parcial |
| WB23 | Payload malformado/duplicado/NaN/no objeto: invalid_request antes de pending |
| WB24 | Pending ajeno preexistente: already_terminal, conservado; éxito conserva siempre par propio terminal/pending nlink2 válido para check; tercer enlace rechaza |

## 7. Gherkin propuesto

```gherkin
Feature: Propiedad operativa del workspace de evidencia
  # SH-P02b/1 propuesto: no acredita ejecucion ni aislamiento de seguridad.
  Scenario Outline: Conservar identidad y exclusividad de un run
    Given el workspace temporal del caso "<case>"
    When ejecuto la operacion contratada para ese caso
    Then el resultado observable es "<result>"
    And la propiedad comprobada es "<property>"

    Examples:
      | case | result | property |
      | WB01 | lease | inputs_byte_exact |
      | WB02 | workspace_exists | foreign_unchanged |
      | WB03 | error | no_mkdir |
      | WB04 | symlink_workspace | target_unchanged |
      | WB05 | invalid_parent | no_parent_creation |
      | WB06 | one_winner | one_owner |
      | WB07 | two_leases | independent_outputs |
      | WB08 | ownership_lost | roots_not_interchangeable |
      | WB09 | ownership_lost | replacement_unchanged |
      | WB10 | symlink_workspace | target_not_read |
      | WB11 | unsupported_entry | no_blocking_read |
      | WB12 | io_error | partial_preserved |
      | WB13 | pending | no_success_claim |
      | WB14 | finished | rejected_preserved |
      | WB15 | interrupted | cancelled_preserved |
      | WB16 | already_terminal | terminal_unchanged |
      | WB17 | one_terminal | complete_bytes |
      | WB18 | io_error | no_overwrite |
      | WB19 | lease_closed | outputs_preserved |
      | WB20 | foreign_process | parent_still_owns |
      | WB21 | ownership_lost | no_receipt_repair |
      | WB22 | boundary_pair | no_truncation |
      | WB23 | invalid_request | no_pending_creation |
      | WB24 | already_terminal | pending_unchanged |
```

Binding: feature, Outline/nombre, secuencia keyword/texto, columnas, número de
filas, IDs únicos y celdas. Positivo PASS; alteración de cada campo FAIL. Cada
familia se expande a nodeids explícitos con todas las variantes de §6. Contract
tests llaman API real; parse/IR no son ejecución ni proof de terminal por fila.

### 7.1 Mapa literal de variantes y colección futura

Los siguientes son **nodeids propuestos, no colección ejecutada**. Para cada
ID literal de la tabla, el nodeid exacto se forma como
`tests/unit/test_evidence_workspace.py::test_workspace_case[ID]`. No se deducen
variantes de outputs del SUT: el coder parametriza estos IDs y el verifier
compara la colección real con esta lista. Los demás tests de módulos pueden
añadirse, sin reemplazar ni renombrar estos casos sin revisión del contrato.

| Familia | IDs literales de variantes obligatorias |
|---|---|
| WB01 | `WB01-new`, `WB01-owner-bytes`, `WB01-inputs-bytes`, `WB01-empty-output-dirs` |
| WB02 | `WB02-directory`, `WB02-file`, `WB02-symlink-internal`, `WB02-symlink-external`, `WB02-symlink-broken` |
| WB03 | `WB03-id-uppercase`, `WB03-id-short`, `WB03-id-long`, `WB03-id-nonhex`, `WB03-id-traversal`, `WB03-id-wrong-type`, `WB03-parent-outside`, `WB03-parent-relative`, `WB03-parent-wrong-type`, `WB03-snapshot-sha-mismatch`, `WB03-snapshot-fields-mismatch`, `WB03-snapshot-wrong-type` |
| WB04 | `WB04-parent-link-internal`, `WB04-parent-link-external`, `WB04-parent-link-broken`, `WB04-ancestor-link` |
| WB05 | `WB05-parent-absent`, `WB05-parent-regular` |
| WB06 | `WB06-two-processes-same-id` |
| WB07 | `WB07-two-ids-same-root` |
| WB08 | `WB08-equal-inputs-distinct-roots`, `WB08-swapped-owner` |
| WB09 | `WB09-root-replaced`, `WB09-parent-replaced`, `WB09-workspace-replaced`, `WB09-own-directory-replaced`, `WB09-workspace-disappeared` |
| WB10 | `WB10-leaf-internal`, `WB10-leaf-external`, `WB10-leaf-broken`, `WB10-dir-internal`, `WB10-dir-external`, `WB10-dir-broken` |
| WB11 | `WB11-fifo`, `WB11-socket`, `WB11-foreign-hardlink`, `WB11-unknown-root-entry`, `WB11-extra-regular-under-artifacts`, `WB11-extra-directory-under-logs` |
| WB12 | `WB12-owner-write-denied`, `WB12-inputs-write-io`, `WB12-partial-id-reused` |
| WB13 | `WB13-kill-before-terminal`, `WB13-interrupt-before-terminal` |
| WB14 | `WB14-finished-rejected`, `WB14-finished-empty-object` |
| WB15 | `WB15-interrupted-cancelled` |
| WB16 | `WB16-second-finish`, `WB16-preexisting-terminal` |
| WB17 | `WB17-two-threads-finish` |
| WB18 | `WB18-pending-write-failure`, `WB18-file-fsync-failure`, `WB18-link-failure`, `WB18-directory-fsync-failure`, `WB18-no-deletions` |
| WB19 | `WB19-close-twice`, `WB19-check-after-close`, `WB19-finish-after-close`, `WB19-close-pending-preserves` |
| WB20 | `WB20-fork-handle-rejected`, `WB20-parent-after-fork`, `WB20-exec-no-inherited-fds` |
| WB21 | `WB21-owner-same-size-change`, `WB21-inputs-same-size-change`, `WB21-terminal-change-outside-check-claim` |
| WB22 | `WB22-entries-exact`, `WB22-entries-plus-one`, `WB22-total-bytes-exact`, `WB22-total-bytes-plus-one`, `WB22-input-bytes-exact`, `WB22-input-bytes-plus-one`, `WB22-owner-bytes-exact`, `WB22-owner-bytes-plus-one`, `WB22-combined-bytes-exact`, `WB22-combined-bytes-plus-one`, `WB22-record-bytes-exact`, `WB22-record-bytes-plus-one`, `WB22-envelope-bytes-exact`, `WB22-envelope-bytes-plus-one`, `WB22-check-terminal-size-exact`, `WB22-check-terminal-size-plus-one` |
| WB23 | `WB23-invalid-utf8`, `WB23-invalid-json`, `WB23-duplicate-root-key`, `WB23-duplicate-nested-key`, `WB23-nan`, `WB23-positive-infinity`, `WB23-negative-infinity`, `WB23-float-overflow`, `WB23-not-object`, `WB23-trailing-content`, `WB23-noncanonical`, `WB23-surrogate`, `WB23-depth-64`, `WB23-depth-65`, `WB23-int-min`, `WB23-int-below-min`, `WB23-int-max`, `WB23-int-above-max`, `WB23-finite-float`, `WB23-negative-zero`, `WB23-record-wrong-type`, `WB23-termination-invalid` |
| WB24 | `WB24-foreign-pending`, `WB24-owned-pair-after-success`, `WB24-owned-pair-after-fsync-error`, `WB24-third-hardlink`, `WB24-different-inodes` |

WB22 añade obligatoriamente `WB22-finish-entries-exact`,
`WB22-finish-entries-plus-one`, `WB22-finish-bytes-exact` y
`WB22-finish-bytes-plus-one`, con el mismo prefijo de nodeid. Los positivos
terminan y su check inmediato pasa; los negativos conservan los outputs
originales y no crean ninguno de los dos nombres terminales. Se mantiene el
tope de la envoltura para distinguirlo del margen agregado.

Cada familia añade el control literal correspondiente:
`WB01-valid-control`, `WB02-valid-control`, `WB03-valid-control`,
`WB04-valid-control`, `WB05-valid-control`, `WB06-valid-control`,
`WB07-valid-control`, `WB08-valid-control`, `WB09-valid-control`,
`WB10-valid-control`, `WB11-valid-control`, `WB12-valid-control`,
`WB13-valid-control`, `WB14-valid-control`, `WB15-valid-control`,
`WB16-valid-control`, `WB17-valid-control`, `WB18-valid-control`,
`WB19-valid-control`, `WB20-valid-control`, `WB21-valid-control`,
`WB22-valid-control`, `WB23-valid-control`, `WB24-valid-control`.
El control equivalente regular debe pasar; no usar una
única fixture que rechace todo para satisfacer los negativos. Este conjunto
de 24 controles es parte adicional explícita del mapa. WB11 extras admitidos,
WB14, WB21-terminal y WB23 fronteras/float válidos son positivos, no errores.

En WB22 las dimensiones son independientes: el borde exacto individual de
inputs puede requerir elevar **solo en fixture** el tope combinado para no
activar otro límite primero; luego se prueba el combinado por separado. Se
pueden reducir constantes internas de límites para fixtures pequeñas, con
valores efectivos registrados; ninguna opción pública de bypass. Owner real
se calcula después de mkdir/fstat; no inventar inode ni bytes esperados desde
el SUT para aprobar el borde. Los casos owner-size ejercitan el lector acotado;
no pretenden producir naturalmente un owner de 2 MiB. El límite total suma
tamaños por ruta, incluido dos veces el par terminal de dos nombres: contabilidad
de outputs conservadora, no medición de bloques físicos ocupados.

El mapa requiere cotejo de conjunto, cardinalidad y ausencia de duplicados
antes de convertir a set/dict. El manifest P02a completo y su compatibilidad
se prueban con fixtures conforme al contrato, no importando producto mutable
de otro worktree ni redefiniendo sus tipos para simular que está integrado.

## 8. Allowlist mínima propuesta y calificación

```text
tools/wct/evidence/workspace.py
tools/wct/evidence/workspace_types.py
tools/wct/evidence/workspace_snapshot.py
tools/wct/evidence/workspace_paths.py
tools/wct/evidence/workspace_publish.py
tests/unit/test_evidence_workspace.py
tests/unit/test_evidence_workspace_snapshot.py
tests/unit/test_evidence_workspace_paths.py
tests/unit/test_evidence_workspace_publish.py
features/wct-evidence-workspace-001.feature
```

workspace es lifecycle/composición; workspace_paths frontera de descriptores y
recorrido; workspace_publish escritura/no-clobber; workspace_snapshot validación
pura de binding; tipos puros no importan adaptadores. Cinco fuentes y cuatro
tests separan responsabilidades antes de superar sitios/LOC; no hay medición
de tamaño de implementación inexistente ni permiso de partir arbitrariamente.
No editar __init__, P01,
P02a, CLI, runner, governance, workflows, dependencias ni contratos. Si tamaño,
sitios o cohesión exigen partición distinta, pedir nuevo allowlist previamente.
Handoff y evidencia se asignan por root al autorizar; no quedan rutas abiertas.

Verifier distinto, digest final, TDD y colección real. Cubertura/CRAP/mutación/
DRY sobre los cinco archivos reales, no inferidos de src/example. CRAP≤6,
CC≤10, sitios≤100/archivo, sin nuevos suppressions. Tests focales no sustituyen
suite/gates; G-META pre-bless se declara, nunca se bendice por esta propuesta.
Conservar intentos fallidos, coste unavailable y asistencia. No presentar esta
campaña multiagente como repetición ciega del experimento económico P01.

## 9. Puertas del arquitecto antes del coder

1. Challenge de API y disponibilidad real de helpers P02a; aprobar codec sin
   duplicación y límites de snapshot. Decidir si P03 necesita más ubicaciones
   antes de congelar las cuatro propuestas, sin introducir slots genéricos.
2. Ensayar Linux/filesystem reales: mkdir concurrente; open relativo no-follow;
   link no-clobber; fsync; reemplazo observable de ancestros; fork/exec; fallo
   después de publicación y par pending/terminal. Registrar versión, argv,
   positivos y rojos; la descripción del mecanismo no demuestra su soporte.
3. Confirmar precondición padre existente y futuro caller P06; no dar a coder
   permiso implícito de crear/borrar directorios ajenos para hacer el fixture.
4. Parse/IR del bloque, mapa familia→variantes/nodeids y revisión de contrato
   separado. Este specifier no ha ejecutado sondas filesystem ni contract tests
   de producto inexistente. No afirmar que el bloque ya pasó el parser.
5. Registrar decisión/hash de propuesta revisada, Gherkin y allowlist. Solo
   después, recibo del coder. Esta entrega no cambia el estado a authorized.

Decisiones deliberadas: sin recuperación ni GC reduce superficie destructiva;
sin lock global evita serializar runs que poseen outputs distintos; el vínculo
físico evita confundir igualdad portable con propiedad; terminal separado evita
que un crash o mero exit 0 fabrique acreditación. La contrapartida es custodia
local creciente, soporte de plataforma acotado y obligación posterior de
calificar productores/consumidores, no una garantía universal de confianza.
