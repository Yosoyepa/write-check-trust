# SH-P02a — Inventario reproducible de inputs, propuesta 2

Estado: **PROPUESTA PARA REVISIÓN; no autoriza implementación ni bless**.
Fecha: 2026-09-07. Base inspeccionada: `46669278ece7e3b7cc8059a5eff9ae27c2735284`.
Autoría: specifier separado del coder; decisión y challenge del arquitecto,
aprobación de API/Gherkin por `yosoyepa`. No cambia el contrato histórico P01.
Entrega: `sh-delivery/2`; molde: `wct-harness-local/2`.

Revisión 2 del arquitecto, tras challenge y [sonda real](SONDA-GIT-P02a.md).
La propuesta 1 (`fce6603d...`) se conserva íntegra en custodia local; sus rojos
no se reescriben como éxitos. Esta revisión precisa framing, filtros y tipos
históricos; no cambia P01 ni introduce implementación o aprobación humana.

## 1. Resultado y corte de la pieza

P02a obtiene, sin modificar el árbol, un inventario de los archivos regulares
seleccionados por un perfil revisado. Cada identidad conserva ruta relativa,
tipo, bytes y modo; el inventario incluye archivos tracked, nuevos, ignorados y
recursos fuera de `src`. Git aporta contexto, **nunca el denominador**.

Se separan tres productos: manifest portable de inputs, metadatos Git y binding
local de raíz. Un snapshot completo no significa tests ejecutados, entorno
autenticado, workspace exclusivo, cobertura acreditada ni beta.3 terminada.

P02b será dueño de crear/poseer outputs nuevos, vincular run/productor y conservar
resultados parciales. P03/P06 serán dueños de observar el entorno realmente
lanzado y comparar inputs al final. P02a no crea directorios, no copia fuentes,
no adquiere locks de ejecución, no ejecuta pytest, no decide `accredited`, no
busca el último LCOV y no añade CLI. Dos snapshots estables no prueban ausencia
de cambios transitorios restaurados ni protección contra otro proceso del UID.

Fuentes normativas: [PIEZAS](../SELF-HOSTING/PIEZAS.md),
[GOBERNANZA](../SELF-HOSTING/GOBERNANZA.md),
[ENTREGA-v2](../SELF-HOSTING/ENTREGA-v2.md),
[MOLDE-WCT-v2](../SELF-HOSTING/MOLDE-WCT-v2.md) y
[SPEC-B3-P1](../specs/SPEC-B3-P1-evidencia.md). Este documento precisa el corte
P02a; no sustituye los consumidores pendientes de esa cadena.

## 2. Reutilización y motivo de lo nuevo

| Existente inspeccionado | Decisión | Motivo observable |
|---|---|---|
| `util.git.changed_files` / `tracked_files` | No usar como enumerador | Omiten ignorados; materializan solo parte del universo y separan nombres con `splitlines` |
| `util.git.run_git` | Referencia de argv sin shell, no reuso directo | Su retorno textual y ausencia de timeout/límite no satisfacen aquí el protocolo NUL/binario acotado |
| `util.git.head_sha` | Semántica reutilizable, no fallback silencioso | `None` no equivale a HEAD observado; la nueva API necesita error tipado y captura acotada |
| `integrity.engine.snapshot` | No reutilizar ni modificar | Solo archivos protegidos y SHA con normalización CRLF; P02a identifica bytes crudos de todos sus inputs |
| `config.find_root` | No llamar implícitamente | Puede seleccionar otra raíz por entorno; P02a recibe y comprueba la raíz explícita |
| `gate.exec._captured` | No llamar | Mezcla/resume salidas, usa texto y no tiene límites del inventario autoritativo |
| `evidence.identities.compare_identities` | Mantener sin cambios | Reconcilia tres inventarios de obligaciones; no es un lector de filesystem ni comparador de contenido |
| `accept.pipeline.parse_feature` / `ir_dry` | Reusar para contrato | Verifican sintaxis/IR, no ejecución del snapshot ni seguridad del recorrido |
| stdlib: `os`, `stat`, `hashlib`, `json`, `subprocess`, `dataclasses` | Suficientes, sujeto a verificación local del coder | No hace falta dependencia, pack compiler, servicio ni framework nuevos |

No introducir interfaces de un solo implementador sin frontera real. Tipos y
serialización no leen disco/procesos; los lectores de filesystem/Git son
adaptadores explícitos. La aplicación futura inyectará su lector de inputs;
P02a no construye ahora un engine ni un registro de plugins.

## 3. API propuesta y datos que cruzan la frontera

Una operación pública, importable directamente de `tools.wct.evidence.inputs`:

```text
capture_inputs(root: pathlib.Path, *, spec: InputSpec,
               context: ContextRef, git_executable: pathlib.Path) -> InputSnapshot
```

No tiene defaults que estrechen alcance, no lee `WCT_PROJECT_ROOT`, no retorna
un booleano y no escribe stdout. Los tipos siguientes serán dataclasses
inmutables; todas las colecciones son tuplas. Orden de campos como se enumera;
validación de tipos también en la frontera, no confiar solo en anotaciones.
`root` debe ser absoluto y léxicamente canónico (sin `.`/`..`); otra forma
produce `invalid_root`, no una resolución implícita contra cwd. Esto no permite
seguir symlinks en los componentes de una raíz absoluta.

`git_executable` es la ruta absoluta existente/no-symlink al ejecutable aprobado
por el caller; no se busca por PATH del usuario. Es parámetro operativo, fuera
del manifest portable, y se vinculará al contexto observado en P03/P06. En el
entorno inspeccionado resuelve a `/usr/bin/git`; no afirmar que ese path sea
portable a toda instalación Linux. No ejecutar un binario propuesto por el
candidato sin la revisión/calificación del caller.

| Tipo/campos | Contrato |
|---|---|
| `InputSpec(schema_version, profile_id, profile_version, base_commit, required_files, required_roots)` | `schema_version` entero 1, no bool; `profile_id` string `beta3-p1`; `profile_version` string `1`; base commit literal hex minúsculo de 40 o 64 caracteres; archivos/raíces relativos, únicos, no vacíos, revisados antes del productor |
| `ContextRef(schema_version, review_id, sha256, provenance)` | Versión 1; review ID no vacío; digest de 64 hex minúsculos; provenance literal `caller-declared`. Identifica un documento de contexto revisado, no verifica sus afirmaciones |
| `InputFile(path, kind, sha256, size, mode)` | Ruta POSIX; kind literal `regular`; SHA-256 crudo; tamaño entero no negativo; bits de modo `stat.S_IMODE`, sin UID/GID ni timestamps en la identidad portable |
| `ExcludedInput(path, rule, kind)` | Entrada encontrada que se poda; regla cerrada de §4; tipo observado `directory` o `regular`. No afirmar inventario/hash de sus hijos |
| `GitState(head, base, index_sha256, status_sha256, changes)` | HEAD/base completos; digest semántico del índice y estado canónico **proyectados al scope de inputs**; cambios por ruta, con códigos Git de índice/worktree separados, sin deducir bytes desde ellos |
| `GitChange(path, index_status, worktree_status)` | Ruta validada; dos caracteres del protocolo Git. Orden por bytes UTF-8 de ruta; no colapsar registros duplicados |
| `RootBinding(path, device, inode)` | Raíz absoluta observada, `st_dev`, `st_ino`; solo procedencia local, fuera del manifest portable. No certificado de propiedad ni ID global persistente |
| `InputSnapshot(spec, context, files, exclusions, git, root, manifest, sha256)` | Datos coherentes, manifest en bytes y su digest. `exclusions` son fronteras observadas fuera del digest portable. Solo existe retorno completo; nunca lista parcial marcada como válida |
| `InputCaptureError(code, path, errno)` | Excepción con código de §7, ruta relativa cuando existe, `errno` opcional. Mensaje humano no normativo; no incluir contenido ni entorno en el error |

IDs de versión/review son UTF-8 no vacíos, sin C0/DEL; no normalizar espacios,
mayúsculas ni Unicode. Los paths tienen además el contrato estricto de §4.
Tipos estructuralmente incorrectos → `TypeError`, identificando el argumento;
valores del contrato inválidos → `InputCaptureError(invalid_spec, ...)` antes de
leer archivos. No aceptar listas donde se contrataron tuplas ni bool por int.
No permitir valores desconocidos por cast silencioso.

`required_roots` identifica directorios fuente/test/config consumidos que
deben existir; al menos una raíz debe contener un archivo seleccionado.
`required_files` identifica entradas obligatorias exactas que deben existir.
Ambas listas tienen al menos un elemento; se ordenan para serializar después
de rechazar duplicados. Un archivo puede estar dentro de una required root;
eso no es duplicación. Raíces entre sí no pueden ser iguales ni anidadas.

El caller del perfil WCT debe fijar, como mínimo, `src`, `tools/wct`, `tests`
como raíces, y `pyproject.toml`, `uv.lock`, `governance/policy.yaml`,
`governance/thresholds.yaml`, `governance/baselines/coverage-total.json` como
archivos obligatorios. Todos los demás archivos regulares no excluidos también
se inventarían: reglas, baselines restantes, workflows, configuraciones,
features, recursos, datos de fixtures, documentación y runner en `tools/wct`.
Los micro-fixtures conservan esos nombres/disposición con contenido mínimo;
no se les atribuye cobertura del repositorio real.

## 4. Selección, rutas, exclusiones y Git

### 4.1 Enumeración autoritativa

Recorrer el filesystem desde la raíz; no empezar por `git ls-files`, `git diff`,
LCOV ni colección pytest. Incluir cada archivo regular materializado, aunque
Git lo ignore. Archivos eliminados no tienen bytes presentes: su desaparición
se ve comparando manifests; si eran obligatorios, falla esta captura.
Los directorios vacíos no son archivos, aunque las raíces obligatorias se
comprueban. Un archivo de cero bytes sí se incluye con tamaño 0 y digest vacío.

Cada path se valida antes de usarlo: relativo POSIX, UTF-8 estricto, componentes
no vacíos, sin `.`/`..`, `/` inicial/final, backslash, C0/DEL ni NUL. No usar
`resolve` para convertir traversal/symlink en una ruta aceptable. Espacios,
acentos y guiones iniciales en componentes **sí** son válidos; preservarlos.
No normalización Unicode/case-folding ni conversión temprana a set/dict que
elimine duplicados. Nombres no representables producen `invalid_path`.

### 4.2 Exclusiones cerradas de P02a/1

No hay glob aportado por el coder o por CLI. Estas reglas son contrato fijo,
no una modificación a `governance/policy.yaml`:

| Regla | Match exacto | Disposición |
|---|---|---|
| `git-metadata` | `.git` en la raíz | Archivo regular de worktree o directorio Git; Git se observa aparte, no seguir este árbol como fuente |
| `root-output` | Directorio `build` en la raíz | Podar y registrar, sin leer hijos |
| `root-environment` | Directorio `.venv` en la raíz | Podar y registrar; el entorno ejecutado requiere ancla separada |
| `cache-directory` | Directorio con basename `__pycache__`, `.pytest_cache`, `.mypy_cache` o `.ruff_cache`, en cualquier profundidad | Podar y registrar cada frontera encontrada |
| `coverage-output` | Archivo regular con basename que empieza `.coverage`, **solo en la raíz** | Podar y registrar; no ocultar `src/.coverage_model.py` |

Una regla para directorio no excluye un archivo regular con ese nombre;
`src/build.py`, `build.txt` y un archivo regular `build` se incluyen. `.coverage`
directorio no se excluye por la regla de archivo. No crear reglas implícitas
para `mutants`, `.nodeterm`, `node_modules`, `.env`, `.tox` o directorios ajenos;
si son inputs locales grandes/inadecuados, cambiar el perfil requiere revisión,
no ignorarlos para obtener verde. El manifest no publica contenido de `.env`,
pero nombres y hashes también pueden ser sensibles: custodia/publicación aparte.

Antes de podar, comprobar que ningún required file/root coincide con la entrada
o queda dentro de ella. Intersección → `excluded_required_input`. Una caché no
se convierte en fuente legítima por omisión del registro; el consumidor no
puede ejecutar entradas excluidas y después reclamar identidad de esas entradas.
El listado de exclusiones acredita fronteras declaradas, **no prueba que ningún
script lea sus hijos**. Si la revisión descubre tal dependencia, corregir el
perfil antes del productor. No relajar exclusiones durante una ejecución.

Symlinks, incluso en la frontera de una exclusión, se rechazan antes de podar;
no inspeccionar su destino. Dentro de una carpeta ya podada no se enumeran
hijos ni se reclama ausencia de symlinks. P02b verificará por separado todos
los componentes del destino privado que vaya a crear debajo de `build/tmp`.

### 4.3 Estado Git, no fuente del inventario

P02a/1 requiere Git y un HEAD/base existentes; repos sin commit, submódulos,
conflictos de índice, sparse checkout, skip-worktree y assume-unchanged están
fuera del perfil inicial y producen `unsupported_git_state`. No ejecutar
checkout, reset, fetch, add, update-index ni comandos de red.

Adaptador Git con argv como lista, `shell=False`, stdout binario y protocolo
NUL para rutas. Deshabilitar actualizaciones opcionales del índice, fsmonitor
y lazy fetch; rechazar filtros configurados antes de `status` según el preflight
inferior. No invocar hooks ni filtros de contenido configurados. Validar antes de pasar base como
argumento; nunca interpolarla en shell. Obtener HEAD/base, entradas staged
`mode/blob/stage/path` y estado índice/worktree por separado. Renames desactivados:
se representan como eliminación y adición; no inferir identidad por parecido.

El índice semántico es la lista canónica de entradas Git staged dentro del
scope seleccionado (no los bytes del archivo `.git/index`, que incluyen datos
de caché). Leer el índice completo antes de proyectarlo. Los estados Git se
normalizan únicamente por orden de registros, nunca por contenido de paths.
Los hashes se calculan sobre la misma serialización JSON de §6. Incluir en
`changes` modificaciones staged/unstaged, adiciones, eliminaciones, `??` y `!!`
de entradas seleccionadas. Paths excluidos por §4.2 no entran en ninguno de
estos dos digests ni en changes, aunque Git los reporte; un path eliminado
no excluido sí entra. No excluir `!!` por su estado: `src/ignored.py` entra.
Si Git devuelve un directorio ignorado agregado, expandir su clasificación
únicamente sobre los paths ya enumerados por filesystem, sin excluirlos.

Proyección tipada, también cuando la ruta ya no existe: cada componente no
final de una ruta de archivo Git es un directorio por su identidad estructural.
Aplicar a esos componentes las exclusiones de directorio de §4.2, sin exigir
`lstat` actual. El tipo final se toma del índice; para una eliminación staged
ausente del índice, del árbol de HEAD; para una entrada nueva, del inventario
filesystem ya validado. No inferirlo por substring, extensión o existencia.
Entradas Git sin fuente de tipo coherente → `unsupported_git_state`.

Así, `build/report` y `src/__pycache__/item.pyc` quedan fuera aun si sus padres
se borraron enteros, mientras un archivo regular final llamado `build` permanece
seleccionado, incluido su borrado. `.coverage*` solo se excluye si el componente
final es regular y está en la raíz; un directorio con ese nombre no se excluye.
Los modos Git `100644`/`100755` identifican regular; `120000` no se interpreta
como regular ni como directorio. Los symlinks presentes siguen rechazándose
por el lector filesystem; un registro Git de una ruta ausente no se sigue.
No añadir al digest el inventario completo de HEAD: sirve para tipar la
proyección, no como segundo denominador de inputs ni como lista ejecutada.

No clasificar un path tracked como limpio solo porque no está en `changes` sin
tener el índice completo. La identidad primaria sigue siendo el hash de bytes:
una modificación con mismo HEAD/tamaño entra en el manifest. Un nuevo archivo
ignorado puede estar presente en `files` y clasificado `!!` simultáneamente.
Un renombre cambia las identidades aunque conserve el contenido y el conteo.

Prefijo fijo de argv: `[str(git_executable), "--no-optional-locks", "--no-lazy-fetch", "-c",
"core.fsmonitor=false", "-c", "core.untrackedCache=false", "-c",
"core.hooksPath=/dev/null", "-c", "core.excludesFile=/dev/null"]`.
Entorno nuevo cerrado, **sin heredar ni volcar `os.environ`**:
`{"PATH":"/usr/bin:/bin","LANG":"C","LC_ALL":"C",
"GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":"/dev/null",
"GIT_TERMINAL_PROMPT":"0"}`. No pasan `GIT_DIR`, `GIT_WORK_TREE`,
`GIT_INDEX_FILE`, `GIT_COMMON_DIR`, alternate/object directories ni
`GIT_CONFIG_COUNT`. No escribir configuración global o local. Se observa la
clasificación del repo con esa receta explícita; no la preferencia global de
ignore del usuario. La lectura que Git haga de su configuración local no se
presenta como frontera de seguridad contra un repositorio hostil.

Consultas cerradas. Respuestas escalares de `rev-parse`: exigir exactamente
un LF terminal, retirarlo una vez y validar el payload sin `strip()`; rechazar
LF adicionales o CR/nombres fuera del contrato. `show-prefix` válido es
`b'\n'` en el protocolo y payload vacío; no exigir cero bytes a Git.

Antes de `status`, completar inventarios/tipos, rechazo de estados no soportados
y consulta de filtros. Ningún caso rechazado debe llegar a ese comando:

- `["rev-parse", "--is-inside-work-tree"]` → `true`; `["rev-parse",
  "--show-prefix"]` → vacío; el caller no puede pasar una subcarpeta como raíz.
- `["rev-parse", "--show-toplevel"]`: retirar solo el LF terminal del protocolo;
  preservar espacios. El path y su identidad física deben coincidir con la
  raíz validada; raíz diferente → `invalid_root`. `.git` regular de worktree
  es legítimo y no justifica vincular metadatos de otro árbol.
- `["rev-parse", "--verify", "HEAD^{commit}"]` y `["rev-parse", "--verify",
  "<base_commit>^{commit}"]`, con base validada antes.
- `["ls-files", "--stage", "-z"]`: modo/blob/stage y path NUL; stage distinto
  de 0 o modo gitlink 160000 → estado no soportado. Para index_sha256, array
  JSON de objetos `{mode: string_octal, blob: hex, stage: int, path: string}`
  proyectados, ordenados por path/stage, con el codec de §6.
- `["ls-tree", "-r", "-z", "--full-tree", "HEAD"]`: modo/tipo/objeto TAB path
  NUL para identificar eliminados staged. No usar `--name-only`, que perdería
  el tipo. Gitlink 160000 sigue no soportado. Objeto necesario ausente o fallo
  de lectura → `unsupported_git_state`; no efectuar una descarga para repararlo.
- `["ls-files", "-v", "-z"]`: tag y path; tags minúsculos o `S` indican flags
  fuera de perfil. `["config", "--bool", "--get", "core.sparseCheckout"]`:
  `true` se rechaza; exit 1 con salida vacía significa no configurado, no fallo
  de herramienta. Cualquier otra forma no válida se rechaza.
- `["config", "--includes", "--null", "--name-only", "--get-regexp",
  "^filter\\."]`: consulta de claves efectivas, **sin `--local`**, para incluir
  config del worktree e includes. Exit 1 con stdout/stderr vacíos significa
  ausencia. Exit 0 con cualquier clave implica `unsupported_git_state` antes
  de `status`, aunque parezca un filtro inactivo; no se imprimen sus valores.
  Otros exits, protocolo vacío incoherente o errores no se tratan como ausencia.
  Consulta binaria acotada, bajo el mismo entorno cerrado. La primera propuesta
  del arquitecto con `--local` se retiró antes de ensayarse: omitía worktree.
- `["status", "--porcelain=v1", "-z", "--untracked-files=all",
  "--ignored=matching", "--no-renames", "--ignore-submodules=none"]`: parsear
  XY y paths, no frases. Un agregado de directorio termina en `/`; quitar solo
  ese terminador de protocolo, comprobar directorio y proyectar a entradas
  enumeradas bajo él. `status_sha256` es SHA del array JSON canónico de changes.

`--no-lazy-fetch` es parte de todas las consultas, no solo de `ls-tree`:
una consulta de lectura no equivale por sí sola a ausencia de red. Falta de
capacidad del Git seleccionado o de objetos locales bloquea; no se quita la
bandera para obtener un resultado. El entorno cerrado no convierte configuración
Git local en confiable ni evita un escritor del mismo UID que la cambie entre
preflight y status. P02a no promete esa defensa; P02b/P06 tampoco pueden elevar
esta sonda cooperativa a aislamiento sin una calificación propia.

El coder contrastará estas listas con repos temporales reales y registrará
argv/salidas; no modificará el protocolo si una variante falla. No reconstruir
un parser a partir de un ejemplo de prosa. Cualquier incapacidad
del Git instalado para cumplir este protocolo se reporta, no se degrada a
`splitlines` ni a inventario parcial. La aceptación no depende de una frase
localizada de stderr ni expone paths absolutos de metadatos Git.

Vectores literales revisables del codec de índice/estado, cada línea con LF
final (datos sintéticos de prueba; no evidencia de un commit del candidato):

```json
[{"blob":"8baef1b4abc478178b004d62031cf7fe6db6f903","mode":"100644","path":"src/a.py","stage":0},{"blob":"e69de29bb2d1d6434b8b29ae775ad8c2e48c5391","mode":"100644","path":"src/z.py","stage":0}]
```

SHA-256 literal: `3c64cbd3e3ae3dcf16ee370767360ba3fe5b460eb1f9ec1da439ffc32b9a7e34`.

```json
[{"index_status":" ","path":"src/a.py","worktree_status":"M"},{"index_status":"?","path":"src/new.py","worktree_status":"?"}]
```

SHA-256 literal: `631c20109b0cb309f1d37e0360eb2bf6937cbe0fcf1f3b302e4defd7268df168`.
El test usa estos bytes/valores literales, no una llamada al serializador SUT
para generar expected. Entrada permutada tiene la misma salida; duplicado de
Git → `unsupported_git_state`, duplicado del recorrido → `unstable_inputs`.
Falta todavía revisión independiente de la receta completa en repos adversarios;
su definición no equivale a calificación del adaptador.

## 5. Contexto de configuración, runner y dependencias

El manifest de archivos ya identifica bytes de config, lock y código del
runner dentro del proyecto. Cambiar policy/tests/conftest/runner/lock, aunque
HEAD no cambie, debe cambiar el digest. No interpretar YAML/TOML como otro
motor de política ni importar el código a inventariar.

`ContextRef` es obligatorio para no olvidar la segunda mitad de la identidad.
Su documento, custodiado por el caller/reviewer, debe enumerar: perfil y versión,
expectations revisadas y su digest, intérprete y ejecutables resueltos,
versiones observadas de pytest/coverage/plugins/dependencias, lock, plataforma
y variables operativas no secretas efectivas. Su formato/observación se cerrarán
en P03/P06; **P02a solo vincula la referencia, marcada caller-declared**.
Cambiar su digest/review ID cambia el snapshot portable; P02a no inventa un
valor si falta ni afirma haber inspeccionado un intérprete al recibirlo.

No leer `os.environ` completo, red, configuración del modelo/cuenta, recibos,
claves ni paquetes del usuario. El caller futuro deberá detectar selección
no declarada (`PYTEST_ADDOPTS`, `PYTHONPATH`, `COVERAGE_FILE` y demás variables
del perfil) antes de lanzar; P02a no certifica que hoy estén controladas.
`ContextRef` sin observación/calificación posterior es insuficiente para
`accredited`. Esto es una condición de ensamblaje, no un bypass documentado.

## 6. Serialización y estabilidad, sin digest mágico

`manifest` será JSON UTF-8 sin BOM, claves ordenadas, `ensure_ascii=False`,
separadores `(',', ':')`, sin NaN/float y con un LF final. Objeto exacto:

```text
{
  "schema_version": 1,
  "record_type": "wct-input-snapshot",
  "spec": {todos los campos de InputSpec},
  "context": {todos los campos de ContextRef},
  "files": [{todos los campos de InputFile}, ...],
  "exclusion_rules_version": "sh-p02a-exclusions/1",
  "git": {todos los campos de GitState}
}
```

El bloque anterior describe campos, no es un fixture JSON literal. Arrays de
archivos y changes se ordenan por path UTF-8; listas de required
paths se ordenan igual; entradas staged por path y después stage. Antes de
ordenar, duplicado → error. Mismo path/datos no puede aparecer dos veces y
desaparecer por un dict. Las observaciones `exclusions` también se ordenan por
path, pero permanecen fuera del manifest: el nacimiento de una caché excluida
no debe invalidar por sí solo el contenido de inputs. No se serializan paths
absolutos, inode/dev, duración,
relojes, PID, run ID ni el propio digest dentro del manifest portable.
`sha256 = SHA256(manifest)` con 64 hex minúsculos. Archivos: bytes crudos;
`b'abc'` tiene digest literal
`ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`;
cero bytes tiene
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
CRLF y LF son inputs distintos. No reutilizar SHA eol-normalized de integridad.

Dos raíces con idénticos inputs/contexto/Git pueden tener el mismo digest
portable. Sus `RootBinding` son diferentes: el caller no puede vincular outputs
por ese digest solo; necesita run/productor/raíz de P02b. Un path absoluto no
se filtra al manifest para fabricar unicidad. Cambio de Git sin cambio de
contenido altera el manifest conservadoramente; el consumidor podrá mostrar
qué eje cambió, pero no borrar el cambio para acreditar la ejecución anterior.
Resumen preciso: bytes/path/modo de input, required paths, profile/base/HEAD,
índice/estado de inputs o ContextRef distintos → digest distinto; orden de
enumeración, ubicación/dev/inode, cachés/outputs excluidos y sus estados Git
distintos → no cambian el digest. La identidad operativa sigue separada.

### Captura estable y límites de afirmación

1. Validar spec/context y raíz antes de abrir inputs. Rechazar componentes
   symlink de la raíz sin normalizarlos; Linux inicial, error visible en otra
   plataforma no calificada.
2. Mantener referencia a la raíz/directorios abiertos y no seguir symlinks en
   cada componente. Abrir archivos como regulares con comprobación de tipo y
   no-follow; no basta `is_file()` ni `resolve().is_relative_to(root)` antes
   de un `read_bytes()` que vuelva a resolver el path.
3. Comprobar identidad/tipo/tamaño/modo/mtime_ns/ctime_ns antes y después de
   cada lectura y volver a comprobar las entradas y directorios recorridos al
   cerrar la captura. Si cambia la estructura, desaparece una entrada o cambia
   el archivo durante esa ventana: `unstable_inputs`, sin reintento automático.
4. Obtener contexto Git antes/después; diferencias durante la captura también
   son `unstable_inputs`. La API no refresca la base/expected para aceptarlas.
5. Antes del dictamen P03/P06 deben volver a capturar con el mismo contrato y
   comparar manifest **y root binding**, no la igualdad de todas las observaciones
   de cachés excluidas; cambio persistente de inputs invalida ese run.

Revisiones de metadatos detectan cambios cooperativos observables, no snapshots
atómicos de todo el árbol, modificaciones transitorias restauradas, montajes
maliciosos ni autenticidad del runner. P02a no publica ese lenguaje de garantía.
Los tests de carreras usan barreras deterministas en la frontera de IO, no
`sleep` ni un hook de producción para aprobar fixtures. Si una plataforma no
ofrece el no-follow/descriptor necesario, no degradar silenciosamente.

## 7. Errores y límites de recursos propuestos

Catálogo cerrado de `code`: `invalid_spec`, `invalid_root`, `invalid_path`,
`missing_required_input`, `excluded_required_input`, `symlink_input`,
`unsupported_input_type`, `unsupported_git_state`, `git_unavailable`,
`io_error`, `unstable_inputs`, `limit_exceeded`, `unsupported_platform`.
FIFO/socket/dispositivo → `unsupported_input_type`, sin abrir para lectura.
Permiso denegado → `io_error`, nunca omisión. Subdirectorio repo/submódulo o
archivo `.git` anidado no raíz → `unsupported_git_state` antes de seguirlo.

Validación de spec/context precede IO; raíz precede Git/recorrido. Recorrido
canónico por path; al primer fallo descubierto la API termina y conserva su
código/path. No afirma haber inspeccionado todos los fallos posibles. Causas
ya observadas por otros productores se conservan en P05; P02a no las recibe ni
las borra. `KeyboardInterrupt`/cancelación se propaga; P02b/P06 conserva el
registro parcial, no se transforma en snapshot válido.

Límites **de propuesta, no nuevos umbrales de governance**: 10.000 entradas
visitadas (incluye dirs/fronteras excluidas), 64 MiB por archivo, 256 MiB total
hasheado y 2 MiB de manifest final. Límite exacto permitido; uno más falla.
Leer por bloques acotados, nunca archivo arbitrario completo en RAM. Cada
comando Git: 5 s y 2 MiB de stdout/stderr combinado, límite durante lectura,
sin truncamiento autoritativo silencioso; cerrar/recolectar el hijo al exceder.
No ampliar límites automáticamente por tamaño del repo. El presupuesto global
y overhead de SPEC-P1 siguen por medir; estos límites no acreditan cumplirlo.

Estos límites evitan inventarios truncados verdes. Reducirlos en fixtures de
borde es válido si se hace por sustitución de constantes internas del adaptador,
sin agregar un flag público de bypass ni adjudicar rendimiento de 256 MiB con
una fixture de 20 bytes. Registrar los límites efectivos de cada sonda.

## 8. Matriz literal de casos y defectos discriminantes

Cada fixture es un repo temporal real con HEAD/base, requeridos mínimos de §3,
contexto ficticio revisado y outputs aparte. `ok` significa captura completa,
**no** `accredited`. Las afirmaciones se añaden al conjunto mínimo común; no
contar fixtures de soporte como fuentes adicionales sin declararlo.

| ID | Preparación / resultado literal | Defecto que debe detectar |
|---|---|---|
| IA01 | `src/a.py = b'abc'` tracked limpio: presente, regular, size=3 y digest literal de §6 | Seleccionar solo diff y omitir limpios |
| IA02 | Mismo path unstaged `b'abd'`: su digest cambia, HEAD idéntico, worktree status `M` | Hash de HEAD/índice en lugar de bytes |
| IA03 | Stage `b'abd'` y worktree `b'abe'`: inventario corresponde a `b'abe'`, índice y worktree `M` | Usar bytes staged como ejecutados |
| IA04 | Nuevo `src/new.py = b'abc'`: presente, Git `??` | Inventariar solo tracked |
| IA05 | `.gitignore` contiene `src/ignored.py`; ese nuevo archivo existe: presente y Git `!!` | Obedecer gitignore como exclusión de fuente |
| IA06 | `tests/data/item.bin = b'abc'`: presente | Restringir a `.py`/`src` e ignorar fixtures |
| IA07 | Borrar `src/a.py`, agregar `src/b.py` con mismos bytes: igual N, paths/manifests distintos | Comparar conteos o solo hashes sin ruta |
| IA08 | `src/__init__.py = b''`: presente con hash vacío, sin acreditarlo como cobertura | Eliminar archivos vacíos |
| IA09 | Crear los mismos dos archivos en orden inverso, mismo Git/contexto: manifest byte-idéntico | Depender del orden de scandir |
| IA10 | `src/con espacio-é.py = b'abc'`: path conservado | Split por espacios, case-fold o normalización Unicode |
| IA11 | `src/a.py` con CRLF frente a LF: digests distintos | Reusar hash eol-normalized |
| IA12 | Igual archivo, cambiar modo 0644→0755: manifest distinto | Ignorar modo ejecutable |
| IA13 | Sin mover HEAD, agregar/cambiar `build/report`, `.coverage`, `src/__pycache__/a.pyc`: files y manifest idénticos; nuevas fronteras excluidas registradas fuera del digest | Incluir artefactos que la propia ejecución produce, incluso por metadatos Git/exclusión |
| IA14 | `src/build.py` y `src/.coverage_model.py`: ambos presentes | Exclusión por substring/basename excesivo |
| IA15 | Required file `build/input.py`: error `excluded_required_input` | Excluir un input declarado para cuadrar límites |
| IA16 | Required `pyproject.toml` ausente: error `missing_required_input` | Omitir config necesaria sin causa |
| IA17 | Path requerido `../outside`, `/outside`, `src//a.py` o `src/./a.py`: `invalid_spec` | Normalizar traversal hasta que parezca seguro |
| IA18 | Archivo con LF/backslash o nombre no UTF-8: `invalid_path` | Manifiesto ambiguo o pérdida silenciosa de nombre |
| IA19 | Symlink hoja interno, externo o roto: `symlink_input`, destino sin leer | `is_file()` que sigue enlaces |
| IA20 | Symlink directorio seleccionado o raíz con componente symlink: `symlink_input` | Protección solo en hoja |
| IA21 | Frontera `build` symlink: `symlink_input`; no recorrer destino | Podar antes de comprobar tipo |
| IA22 | FIFO/socket bajo árbol: `unsupported_input_type`, no bloqueo por lectura | Tratar cualquier nodo como archivo regular |
| IA23 | Error de permisos al leer `src/a.py`: `io_error` | `except OSError: continue` |
| IA24 | Cambiar bytes durante lectura, mismo tamaño: `unstable_inputs` | Comparar solamente tamaño |
| IA25 | Reemplazar por symlink entre enumeración y apertura: `symlink_input`, destino no leído | Check-then-use de path sin descriptor/no-follow |
| IA26 | Crear/borrar un archivo o reemplazar directorio durante captura: `unstable_inputs` | Inventario tomado de una única lista inicial |
| IA27 | Modificar índice durante captura: `unstable_inputs` | Git capturado una sola vez y atribuido al final |
| IA28 | Cambiar bytes de runner, policy, baseline, conftest o lock manteniendo HEAD: manifest distinto | Medir solo fuente de ejemplo |
| IA29 | Cambiar únicamente ContextRef.sha256/review_id: manifest distinto, provenance sigue caller-declared | Ignorar contexto o elevarlo a observado |
| IA30 | Dos raíces reales, mismos bytes/Git/contexto: digest portable igual y root binding distinto | Usar cwd en el hash o digest como dueño del output |
| IA31 | Git no disponible / base no resoluble: `git_unavailable` / `unsupported_git_state`, sin snapshot parcial | Inventar estado limpio ante fallo de herramienta |
| IA32 | Índice en conflicto/submódulo/flags excluidos: `unsupported_git_state` | Acreditar formatos/estados no implementados |
| IA33 | Dos subcasos obligatorios: IA33a al límite exacto de entradas/bytes/manifest/salida Git → ok; IA33b uno más → `limit_exceeded`, en cada dimensión | Cortar silenciosamente listado o rechazar todo |
| IA34 | Git excede timeout/salida: `limit_exceeded`, hijo terminado/recolectado | Captura ilimitada o inventario truncado verde |
| IA35 | Dos snapshots completos separados por cambio persistente: manifest distinto | Presentar un snapshot inicial como frescura final |
| IA36 | Contexto ausente/tipo incorrecto/versión desconocida/duplicado required: error antes de IO | Cast/default permissivo o dedup prematuro |
| IA37 | Variables Git del proceso apuntan a otro repo/índice: snapshot sigue ligado al repo root con entorno cerrado | Mezclar Git de B con bytes de A por entorno heredado |
| IA38 | Pasar subdirectorio como root o toplevel observado distinto: `invalid_root`; worktree con `.git` regular válido sigue permitido | Aceptar una raíz Git diferente o rechazar todo worktree |
| IA39 | Filtro clean/process local, include o worktree: `unsupported_git_state` antes de status, helper sin ejecutar; sin claves, control válido | Confiar solo en fsmonitor/hooks o consultar exclusivamente config local |
| IA40 | Sin mover HEAD, borrar outputs tracked y sus padres, unstaged y staged: digest igual; borrar archivo regular `build` sí cambia digest | Depender de lstat presente o confundir tipo de un archivo final con sus ancestros |
| IA41 | Objeto requerido no disponible localmente: `unsupported_git_state`, sin lazy fetch; objeto local completo permite captura | Activar red implícita para completar evidencia supuestamente local |

Cada control de error se acompaña del árbol regular válido equivalente. Para
symlinks, el negativo observa el resultado y que el destino no fue leído; no
una aserción huérfana `mock.assert_called`. Una sonda que falla por import/sintaxis
no acredita sensibilidad. IA13 debe incluir tanto escritura bajo fronteras
existentes como creación inicial de las cachés excluidas. Crear esa frontera
cambia las observaciones `exclusions`, pero no la identidad portable; se prueba
también que el estado Git de los outputs no invalida el caso válido.

## 9. Gherkin propuesto, parametrizado y sin narrativa no soportada

El bloque siguiente será verbatim solo tras aprobación. Una fila representa
una familia cuyo desglose literal está en §8; el binding deberá enumerar todas
las variantes indicadas allí como nodeids, no inferirlas del único ID de familia.

```gherkin
Feature: Inventario de inputs independiente de Git
  # Propuesta 2 de SH-P02a/1: no acredita ejecucion ni propiedad del workspace.
  Scenario Outline: Capturar y distinguir identidades de entrada
    Given el repositorio temporal revisado del caso "<case>"
    When capturo los inputs con el perfil "<profile>"
    Then el resultado de captura es "<result>"
    And el campo observable "<field>" coincide con el valor literal "<expected>"

    Examples:
      | case | profile | result | field | expected |
      | IA01 | beta3-p1 | ok | src/a.py.sha256 | ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad |
      | IA02 | beta3-p1 | ok | content_changed | true |
      | IA03 | beta3-p1 | ok | bytes_source | worktree |
      | IA04 | beta3-p1 | ok | new_present | true |
      | IA05 | beta3-p1 | ok | ignored_present | true |
      | IA06 | beta3-p1 | ok | resource_present | true |
      | IA07 | beta3-p1 | ok | renamed_digest_equal | false |
      | IA08 | beta3-p1 | ok | empty_present | true |
      | IA09 | beta3-p1 | ok | canonical_equal | true |
      | IA10 | beta3-p1 | ok | path_preserved | true |
      | IA11 | beta3-p1 | ok | eol_digest_equal | false |
      | IA12 | beta3-p1 | ok | mode_digest_equal | false |
      | IA13 | beta3-p1 | ok | excluded_files_equal | true |
      | IA14 | beta3-p1 | ok | ordinary_names_present | true |
      | IA15 | beta3-p1 | error | code | excluded_required_input |
      | IA16 | beta3-p1 | error | code | missing_required_input |
      | IA17 | beta3-p1 | error | code | invalid_spec |
      | IA18 | beta3-p1 | error | code | invalid_path |
      | IA19 | beta3-p1 | error | code | symlink_input |
      | IA20 | beta3-p1 | error | code | symlink_input |
      | IA21 | beta3-p1 | error | code | symlink_input |
      | IA22 | beta3-p1 | error | code | unsupported_input_type |
      | IA23 | beta3-p1 | error | code | io_error |
      | IA24 | beta3-p1 | error | code | unstable_inputs |
      | IA25 | beta3-p1 | error | code | symlink_input |
      | IA26 | beta3-p1 | error | code | unstable_inputs |
      | IA27 | beta3-p1 | error | code | unstable_inputs |
      | IA28 | beta3-p1 | ok | config_digest_equal | false |
      | IA29 | beta3-p1 | ok | context_digest_equal | false |
      | IA30 | beta3-p1 | ok | root_binding_equal | false |
      | IA31 | beta3-p1 | error | partial_snapshot | false |
      | IA32 | beta3-p1 | error | code | unsupported_git_state |
      | IA33a | beta3-p1 | ok | exact_limit_allowed | true |
      | IA33b | beta3-p1 | error | code | limit_exceeded |
      | IA34 | beta3-p1 | error | code | limit_exceeded |
      | IA35 | beta3-p1 | ok | final_digest_equal | false |
      | IA36 | beta3-p1 | error | filesystem_read | false |
      | IA37 | beta3-p1 | ok | alternate_git_used | false |
      | IA38 | beta3-p1 | error | code | invalid_root |
      | IA39 | beta3-p1 | error | code | unsupported_git_state |
      | IA40 | beta3-p1 | ok | deleted_outputs_digest_equal | true |
      | IA41 | beta3-p1 | error | code | unsupported_git_state |
```

Binding prometido para esta pieza: nombre de feature; inventario, nombre y tipo
Outline; secuencia exacta de keyword/texto de pasos; encabezados, cardinalidad,
IDs únicos y celdas. El control positivo debe pasar; una alteración por cada
campo protegido debe fallar por la aserción pertinente. No convertir rows a
dict antes de contar duplicados.
Además, colección real de los casos debe corresponder al mapa revisado de
familia→nodeids, preservando variantes. No afirmar que el generador genérico
histórico ejecuta este vocabulario: los contract tests llaman la API real de
P02a y se parametrizan con IDs explícitos. Aceptación por CLI nueva es P06.

## 10. Allowlist prevista y ensamblaje

La siguiente lista es propuesta cerrada para el coder tras aprobación; no
autoriza crear archivos ahora. Las particiones responden a responsabilidades
distintas; no dividir mecánicamente una función para engañar a CRAP.

```text
tools/wct/evidence/inputs.py
tools/wct/evidence/input_types.py
tools/wct/evidence/input_manifest.py
tools/wct/evidence/input_files.py
tools/wct/evidence/input_git.py
tests/unit/test_evidence_inputs.py
tests/unit/test_evidence_input_manifest.py
tests/unit/test_evidence_input_files.py
tests/unit/test_evidence_input_git.py
features/wct-evidence-inputs-001.feature
```

`inputs.py` compone esta captura y expone la API; `input_types` solo tipos;
`input_manifest` valida/serializa valores; `input_files` enumera/hashea por
frontera segura; `input_git` observa contexto Git binario/acotado. Dirección:
composición → adaptadores/puro → tipos; ningún tipo importa adaptadores.
No crear módulos vacíos, reexports que nadie use ni Protocol sin consumidor.

Fuera: `__init__.py` e `identities.py` de P01, tests/feature P01, CLI/runner,
workspaces/LCOV, governance, workflows, pyproject/uv.lock, generated y dossier
histórico. El coder no edita este contrato; handoff y evidencia se asignan con
rutas exactas por el arquitecto antes del encargo, sin «todo lo relacionado».
Si los límites de tamaño/sitios exigen otra partición, se solicita el nuevo
allowlist antes de editarla, no se extiende al final de la entrega.

## 11. Qué debe comprobar el verifier y qué NO se hereda de un verde

- Congelar contrato/Gherkin, contexto, variantes y allowlist antes del coder;
  recibir su ficha de entendimiento con argv y semántica Git contrastados.
- TDD focal por regla y rojo real, colección posterior con nodeids. Cubrir
  todos los módulos de P02a, no solo el ejemplo `src`; CRAP ≤6, CC ≤10, cero
  supresiones nuevas, fuentes ≤500 LOC y sitios estimados ≤100 por archivo.
- Mutación/desafíos por identidad real y controles válidos. Distinguir campaña
  productiva de mutación de manuales; no ampliar `paths.source` por cuenta propia.
- Cobertura focal separada de global, receta global no-property seguida de
  ratchets contemporáneos; `--require all` local no se atribuye a CI si exige dos.
- Fast/commit y DRY sobre archivos reales; regex/import-linter del ejemplo no
  certifican ni pureza ni seguridad de estos adaptadores. Revisión de no-follow,
  errores/recursos, falso positivo y API sobre el mismo digest final.
- Medir overhead de captura separadamente; positivo de dos raíces y estabilidad
  serial no acredita concurrencia/propiedad de P02b ni presupuesto E2E P06.
- Preservar historial de intentos, asistencia, actor y custodia. El modelo y el
  precio continúan cegados. No inferir ahorro de pasar esta pieza.

## 12. Decisiones de aprobación y verificación de esta propuesta

El arquitecto debe revisar especialmente estas decisiones antes de pedir el
visto bueno humano del bloque completo:

1. Aprobar el corte P02a read-only y los datos/API de §3; P02b conserva propiedad.
2. Aprobar exclusiones cerradas y estados Git no soportados. No esconder outputs
   usados como inputs ni tratar un worktree como sandbox.
3. Aprobar `ContextRef` declarado como vínculo limitado: P03/P06 tendrán que
   observar/calificar su contenido antes de `accredited`. No es autorización
   para dejar el contexto autodeclarado en el ensamblaje final.
4. Aprobar límites de §7 como presupuesto inicial de esta pieza, sujeto a
   medición; exceso produce bloqueo, no una subida automática del límite.
5. Aprobar Gherkin/matriz y allowlist. Falta todavía el registro de esa decisión;
   el estado de este documento no debe cambiar a autorizado por inferencia.

**Preparación bloqueante antes del coder:** el specifier/reviewer debe ensayar
la receta Git completa, el entorno cerrado, las proyecciones y sus vectores
contra repos válidos/adversarios y registrar el resultado. Aquí se definieron
argv y bytes esperados, pero solo se hicieron los spot-checks enumerados abajo.
Ese ensayo y el challenge independiente no se delegan al coder como decisiones
de comportamiento pendientes. Hasta cerrarlos y obtener aprobación, este
archivo es propuesta concreta, no paquete de implementación autorizado.

Verificación realizada por el specifier en esta propuesta (sin implementación):

- Lectura de AGENTS, roles architect/specifier y skills architecture,
  acceptance y gate; contratos y reutilización citados arriba.
- `lint-imports`: 4 contratos conservados, 9 archivos del ejemplo analizados.
- `wct archmetrics --json`: sin ciclos ni violations; dos zonas pain históricas
  del ejemplo, no evidencia de conformidad del snapshot aún inexistente.
- Git 2.55.0: observados toplevel, prefijo vacío y salidas NUL de `ls-files -v`
  y `status` con sus flags del contrato; los vectores literales se hashearon
  sin usar implementación P02a. No se calificó todavía toda la receta nueva.
- Parser/IR productivos sobre bloque en memoria: versión inicial 1 Outline,
  36 filas y 0 findings; bloque final de propuesta 1: 1 Outline, **39 filas/38 familias y 0
  findings**, incluyendo positivo IA33a, negativo IA33b y ligadura IA37/38.
  No se generaron tests ni ejecutaron handlers con esa comprobación.
- `git diff --no-index --check /dev/null <propuesta>`: sin diagnóstico de
  whitespace; exit 1 porque el archivo es una adición. No es una suite.
- Batería central del arquitecto, no ejecutada por este specifier: fast 7/7 y
  commit 20/21, solo meta heredado declarado. No se repite para esta revisión
  documental ni se atribuye a código P02a inexistente.

No se ejecutaron implementación P02a, contract tests P02a, mutación, full,
presupuesto, campaña adicional de inferencias, red ni promociones del producto
P02a. El trabajo de los agentes tiene consumo/coste unavailable, no cero.
Una especificación parseable es
un requisito de entrada, no un resultado de producto.

### Reconciliación de propuesta 2: decisiones y límites

El arquitecto incorporó PG01–PG03 de la sonda, con challenge independiente de
`molds_audit`: framing literal; perfil sin claves de filtros; proyección por
tipo/path de índice/HEAD; y `--no-lazy-fetch` sugerido por el reviewer. La
consulta preventiva se ensayó con filtro local y ausencia, sin ejecutar el
helper observado. La propuesta 1 queda preservada en
`build/tmp/beta3-campaign-review.Sjppx9/PROPUESTA-P02a-r1.md`, SHA completo en
la sonda. La evidencia de esa versión no se atribuye a revisión 2.

Pendientes identificados al formular revisión 2: includes y config.worktree,
tipado de eliminados staged con `ls-tree`, ausencia de lazy fetch en objeto
faltante y todos los límites/races del adaptador futuro. La semántica ya tiene
una decisión propuesta; no se delega al coder inventarla. No se da un GO de
implementación hasta revisar estos controles y obtener aprobación humana del
paquete revisado. Los tests de producto siguen siendo trabajo del coder,
después de esa aprobación, y deben fallar ante las variantes defectuosas.

### Cierre de preparación de las consultas de revisión 2

[SONDA §11](SONDA-GIT-P02a.md) ya registra las ampliaciones: claves desde
include/worktree; tipo de eliminados staged, incluido el regular final `build`;
y partial clone exclusivamente local con árbol faltante (exit 128) frente al
clon completo del mismo HEAD (exit 0), ambos con `--no-lazy-fetch`.
El arquitecto y el reviewer separado `molds_audit` leyeron esa sección completa.
No se encontraron bloqueantes documentales nuevos en estas consultas.

**Dictamen de preparación: presentable para D1 humana.** No es GO de producto
ni permiso del coder. El parser/IR central sobre el bloque de revisión 2 dio
1 Outline, 42 filas únicas, 0 findings. Los tests de la implementación,
proyección, límites, carreras, sensibilidad, coste y ensamblaje siguen
pendientes; estas sondas no los sustituyen. API, matriz y allowlist requieren
aprobación expresa antes del encargo. El expediente distingue cada actor,
incluida la corrección `--local` que hizo el propio arquitecto.
