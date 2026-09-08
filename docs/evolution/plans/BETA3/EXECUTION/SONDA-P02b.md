# Sonda de preparación P02b — mecanismos, no implementación

Registro del specifier `p02b_contract`, B3-MA-D. Cierre documental observado
UTC `2026-09-08T02:35:27Z`; no se capturaron timestamps individuales de inicio/
fin: esos campos están unavailable, no se reconstruyen del mtime. Referencia:
[propuesta revisada](PROPUESTA-P02b.md), SHA-256 al preparar este registro
`7cccea9caec818f8b896005835700ebdc020b96ec8083e8cdc6f0f1178b45b09`.
Sin API/producto P02b, sin importar ni ejecutar P02a en implementación mutable,
sin commit/push/bless ni cambios de gobernanza.

## Reconciliación del challenge del arquitecto

1. JSON terminal tiene codec propio: floats finitos y enteros int64, preserva
   1.0/-0.0, no NaN/Infinity/overflow, objetos sin duplicate keys a cualquier
   profundidad, profundidad máxima 64. P02a sigue sin floats; no fingir reuso
   de un helper público que no prometió. Las validaciones del producto faltan.
2. Owner+inputs ≤2 MiB es límite adicional del ensamblaje: manifest P02a de
   exactamente 2 MiB sigue siendo válido allí y puede bloquear P02b con
   limit_exceeded. No estrechar silenciosamente el inventario para encajarlo.
   Segundo challenge del arquitecto: el owner incluye inode que solo existe
   después de mkdir. Corregido el contrato para calcular combinado exacto tras
   reservar y conservar parcial si excede; límite individual inputs sí previo.
   La versión anterior decía antes de reservar: era una contradicción, no una
   capacidad demostrada. WB22 ahora exige ambos momentos observables.
3. Lease queda sellado tras link exitoso aun si fsync falla; también al quedar
   pending o encontrarse terminal/pending previos. Nunca reintentar publicando
   encima de un primer intento. El consumidor no infiere éxito de su presencia.
4. check no es inventario autorizado de todos los outputs. Permite entradas
   regulares/directorios bajo artifacts/logs con límites; nivel raíz cerrado.
   P03/P04/P06 deberán clasificar extras pertinentes, no acreditarlos por existir.
5. Binding de snapshot es validación pura local de fields/schema/SHA, sin IO
   ni API privada inventada. La cadena final debe recapturar inputs por P02a.
6. Partición prevista en cinco fuentes cohesivas: tipos, snapshot puro,
   paths/recorrido, publicación y lifecycle. Aún no hay sitios/LOC medidos.
7. check valida bytes de owner/inputs y tipo/ubicación del terminal, no hash ni
   negocio del payload terminal. Consumidores P04/P06 deben compararlo con
   TerminalRef retenido; cambio posterior de payload no lo detecta este check.

## Entorno y frontera

- cwd: `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-execution.uW30FJ`.
- Python `3.13.14`, Linux `7.1.13-200.fc44.x86_64`, glibc `2.43`.
- `stat -f -c '%T' build/tmp/p02b-preflight-zHtS06` → `btrfs`.
- Runtime reutilizado explícitamente mediante UV_PROJECT_ENVIRONMENT de
  `build/tmp/sh-p01-CND-80B8/.venv`, PYTHONPATH del worktree documental y
  `uv run --no-sync`. No instalar ni modificar dependencias.
- Fixtures exclusivamente bajo `build/tmp/p02b-preflight-LQDdmh` (intento 1)
  y `build/tmp/p02b-preflight-zHtS06` (intento 2 y ampliación).
- Primer mktemp falló porque build/tmp no existía en este worktree: exit 1,
  `No such file or directory`. Se creó el padre de **sondas**, autorizado por
  el encargo; no es comportamiento de create_workspace ni de P02a.
- Evidencia **local-only**. Se preservaron parciales, enlaces, FIFO, archivos
  y scripts. No usar estos árboles de fixtures como inputs del producto ni
  publicarlos sin revisión. No borrarlos como parte de esta entrega.

## Comandos y resultados, incluidos rojos

Los scripts de sonda se escribieron con apply_patch; ejercitan syscalls sobre
fixtures propios. No son implementation ni tests de conformidad de un lease.
Los comandos de Python se capturaron con `set -o pipefail` y `tee`, stdout y
stderr combinados. Variables efectivas operativas enumeradas arriba; no dump
de entorno ni lectura de configuraciones de modelos/cuentas.

1. `uv run --no-sync python build/tmp/p02b-preflight-LQDdmh/probe.py`:
   **exit 1**. Pasó mkdir, no-follow, reemplazo, fork y link no-clobber; la
   inyección `os.fsync(-1)` produjo **ValueError**, no OSError/EBADF como había
   supuesto el script. No se llegó a kill/parse ni se presentó como corrida
   completa. Script inicial conservado como `probe-r1.py` y output intacto.
2. Se corrigió exclusivamente el instrumento: descriptor real duplicado y
   cerrado, en vez de entero negativo; fixtures nuevas y raíz por argumento.
   `uv run --no-sync python build/tmp/p02b-preflight-LQDdmh/probe.py
   build/tmp/p02b-preflight-zHtS06`: **exit 0**, todas las observaciones abajo.
3. `uv run --no-sync python build/tmp/p02b-preflight-zHtS06/followup.py`:
   **exit 0**, ampliación real de exec, tipos, prelink y codec finito.

| Mecanismo ensayado | Observación real | Límite |
|---|---|---|
| mkdir simultáneo, dos procesos y barrier | `created`, `exists`; ambos hijos exit 0 | Un par local, no stress/exclusión global |
| ID distinto | `run`, `run-b` coexistentes | No ejecutó pytest ni probó ausencia de outputs compartidos de P03 |
| no-follow hoja externa/rota | `ELOOP` | Destino quedó `UNCHANGED`; no test de API |
| no-follow directorio symlink | `ENOTDIR` con O_DIRECTORY | El adaptador futuro debe mapear causa por lstat, no solo errno |
| rename de directorio y sustituto | dev/inode distintos; apertura por fd permaneció en original; sustituto vacío | No snapshot atómico ni atacante del UID |
| fork | Descriptor heredado y válido en hijo | PID guard de lease aún no existe |
| exec real con close_fds=False | Descriptor 100 marcado no-heredable: hijo observó EBADF | No todas las variantes de launcher |
| link pending→terminal, fsync | Bytes completos, ambos nombres mismo inode/nlink2 | Filesystem local; no corte eléctrico |
| segundo link al mismo nombre | EEXIST; terminal original conservado | No probó máquina de estados de finish |
| fsync postlink sobre fd cerrado | EBADF, terminal completo permaneció | Fallo inducido de descriptor; no simula disco lleno ni confirma durabilidad |
| unlink postlink sobre fd cerrado | EBADF, par conservado | No borrado realizado; estado de lease sigue por implementar |
| link hacia padre inexistente | ENOENT, pending preservado, terminal ausente | Fallo antes de publicar, sin rollback |
| productor parcial SIGKILL | exit -9, log `partial\n` preservado, terminal ausente | No protocolo P03 todavía |
| FIFO por metadatos | Tipo detectado sin open | No producto de lectura/recorrido |
| hardlink de regular | nlink 2 visible | Rechazo del adaptador futuro no ejecutado |
| codec terminal stdlib | Literal `{"duration":1.0,"result":"rejected","zero":-0.0}\n` | No valida todavía todos los negativos JSON del contrato |
| parse_feature + ir_dry productivos | 1 Outline, 24 filas únicas, 0 findings | Sintaxis/IR; no binding completo ni ejecución por fila |

El ensayo de publicación conservó el par pending/terminal intencionalmente;
no necesitó eliminar ni reciclar outputs. Las carreras se coordinaron con
barrier/event, sin sleeps. Timeouts de espera de hijos: 10 s; no medición del
presupuesto del producto, ni garantía del tiempo de bloqueo de cualquier IO.

## Custodia por bytes

Rutas siguientes relativas al cwd documental, SHA-256 de bytes crudos:

| Archivo | SHA-256 |
|---|---|
| `build/tmp/p02b-preflight-LQDdmh/probe-r1.py` | `cc88c4b95c4ede9f91a040f0cd06dacbca431bdd0c81d8a2acd4d7c92665e2a0` |
| `build/tmp/p02b-preflight-LQDdmh/probe.py` | `35732ef8bd3fa81bf4b1c914afb265fa4601733222f0f19d0c2e3744225585e2` |
| `build/tmp/p02b-preflight-LQDdmh/output.txt` | `d48facb8f4786f013ddaf1e3fdb416a9b9d31b8d7225273cc69504e987b026bd` |
| `build/tmp/p02b-preflight-zHtS06/output.txt` | `e40392879ef125768d5a6f4f3ba28f2eb47f9586f8d3f01e38ed935ee485d30d` |
| `build/tmp/p02b-preflight-zHtS06/followup.py` | `ce07a401ebb5d087332151d474757f4f21a7abcaf5cc5018d866dfa5d547bee6` |
| `build/tmp/p02b-preflight-zHtS06/followup-output.txt` | `97a18a5ec2f21a0a8ef8941475e5d784ac7e457511b0b9b0467fd3696d03f444` |
| `build/tmp/p02b-preflight-zHtS06/proposal.feature` | `855d344108b262af1da16627dfa27ae83e817674c7eaea30f99820ef5c37ad96` |

No se creó hash agregado que oculte los dos intentos. Estos hashes identifican
scripts/salidas, no el inventario completo de los árboles ni una custodia
durable. El primer script tenía raíz junto a sí mismo; conservar ese cwd/path
para entender su output, no volver a ejecutarlo sobre fixtures existentes.

## Pendientes antes de autorización

- Challenge separado sobre propuesta revisada, prioridades de errores y las
  variantes de cada familia. La sonda no prueba comportamiento de producto.
- Confirmar slots P03: un events.jsonl y un pytest.log combinado son propuesta,
  no compromiso de stdout/stderr separados ni protocolo de eventos congelado.
- El codec de payload P06 debe conservar esta gramática o pedir una revisión;
  no aprobar campos de negocio nuevos por admitir un objeto JSON.
- Los tests futuros deben cubrir límites, JSON anidado, integridad completa de
  snapshot, races/errores de lifecycle y cierre. No existe una prueba pública
  P02a mutable importada para rellenar esta evidencia.
- Aprobar cinco módulos/nueve archivos Python más feature (10 archivos),
  contrato/hash y recibo de coder. Ningún bless se infiere del resultado.

Fast de la primera entrega documental: 7/7, ejecutado por este specifier;
no representa CI ni suite de P02b. No mutación/full/presupuesto ni inferencias
económicas. La revisión propuesta queda esperando al arquitecto.

## Addenda — reconciliación final del challenge separado

Por decisión de diseño del arquitecto, la propuesta ahora **siempre conserva**
el par `.terminal.pending`/`terminal.json` del mismo inode/nlink2 después de
link y fsync de directorio. P02b no elimina ninguna entrada. La opcionalidad de
unlink era superficie destructiva innecesaria; limpieza/custodia futura requiere
otro contrato. El fallo de unlink sobre fd cerrado ensayado arriba es histórico:
no se borra su resultado ni se presenta como parte del API final. La sonda ya
conservaba el par, pero no es una prueba de la futura máquina de estados.

Se aclaró que check limita terminal por st_size, sin leer sus bytes; finish
limita payload y envoltura antes de escribir. Se añadió §7.1 con IDs literales
de variantes→nodeids propuestos, controles válidos por familia y bordes exacto/
+1 por dimensión; es obligación de colección futura, no resultado ejecutado.
Para el límite total los dos nombres del par cuentan por ruta (dos tamaños),
sin prometer medición de bloques de disco. Los cuatro slots de outputs siguen
propuestos, esperando confirmación P03; no se añadieron más rutas productivas.

El digest `7cccea9c...` del encabezado identifica una versión histórica al
iniciar esta sonda. Revisión final de propuesta tras esta reconciliación:
`04749059f4483f22c0056f4ebdcd80414e7936612bf68d1ee37089c06d344c59`.
Las capturas de syscalls conservan los mismos bytes/hashes de la tabla; no
se atribuyen tests, aprobación de producto ni ejecución nueva de P02b al
agregar el mapa documental. Sigue pendiente autorización arquitectónica final.
