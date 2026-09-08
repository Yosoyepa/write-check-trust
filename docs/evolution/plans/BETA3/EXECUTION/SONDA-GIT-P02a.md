# Sonda Git de preparación P02a — resultado: requiere reconciliación

Fecha: 2026-09-07. Actor: specifier; ensayo independiente de cualquier coder
P02a, pero no independiente de los supuestos de la propuesta que redactó.
Contrato inspeccionado: [PROPUESTA-P02a](PROPUESTA-P02a.md), SHA-256
`fce6603d8177235023542e9bd4a6b49eb70d025feddc9cf21bd64b5eae62c978`.
Ese archivo se mantuvo congelado. No se implementó `capture_inputs`, su
proyección, manifest ni comparador. No hay dictamen de producto P02a.

## 1. Dictamen y decisiones necesarias

**La receta es ensayable, pero no debe pasar todavía al coder como contrato
cerrado.** Se observó el camino válido y se confirmaron estas tres necesidades:

| ID | Evidencia real | Consecuencia / recomendación para el specifier |
|---|---|---|
| PG01 — framing escalar | `rev-parse --show-prefix` en raíz válida retorna `b'\n'`, exit 0, no `b''` | Definir el framing de todas las respuestas escalares. Quitar solo el LF terminal del protocolo; no `strip()` de paths. El positivo no debe ser rechazado por una expectativa ambigua de «vacío» |
| PG02 — helper local | La receta exacta de `status`, con entorno cerrado y fsmonitor/hooks apagados, ejecutó un filtro clean local controlado: tres marcas en stderr, exit 0 | Contradice el requisito «no invocar helpers». Proponer perfil inicial sin filtros clean/process y detección previa segura, o cambiar/qualificar otra receta. No afirmar que deshabilitar fsmonitor/hooks deshabilita `filter.*` |
| PG03 — exclusión de eliminados | Tras borrar por completo carpetas de output con hijos tracked, `status` conserva sus paths ` D`, mientras filesystem ya no aporta las fronteras ni su tipo | Fijar proyección de entradas históricas/eliminadas y control positivo independiente. No decidir por ausencia actual del directorio; tampoco incluir todo `D` excluido y volver inválida una ejecución sana |

PG01 se puede resolver documentalmente con bytes explícitos y su prueba.
PG02 y PG03 necesitan nueva decisión de receta/semántica y ensayo de positivos
y negativos antes de autorización. Esta sonda **no aplica esos cambios** ni
autoriza al coder a inventarlos. El challenge independiente del arquitecto
originó PG02/PG03; el specifier los reprodujo con fixtures nuevas.

## 2. Frontera y reproducibilidad de las fixtures

Solo repositorios nuevos bajo:

```text
/home/jandradeu/Documents/well_code_template/build/tmp/beta3-campaign-review.Sjppx9/git-p02a.m1Pfut/
  repo-a/
  repo-b/
  worktree-valid/
  worktree-flags/
  worktree-conflict-ours/
  worktree-conflict-theirs/
```

Directorio creado con `mktemp -d` en la raíz autorizada. Archivos de fixture
creados/editados/borrados con `apply_patch`; Git init/add/commit/worktree y
preparación de flags/conflicto se limitaron a esos repos. Sin remotos ni red,
sin cambios a WCT/producto/gobernanza, sin leer configuración de modelo/cuenta.
No se leyó ni volcó `os.environ` global. Los repos comparten disco/UID y los
worktrees comparten metadatos Git: **no** se presume sandbox de seguridad.

Git observado: `/usr/bin/git`, `git version 2.55.0`. Driver de sonda en memoria:
Python 3.13.14 ya disponible; solo orquestación de comandos y expectativas
literales, sin módulo/algoritmo de P02a. Los tiempos de Git de las fixtures se
fijaron sintéticamente en 2000-01-01/02 para sus commits reproducibles; **no**
son timestamps de ejecución de esta sonda. No se midió presupuesto técnico.

Bases iniciales, con commit fixture `test: prepare deterministic Git fixture`:

- repo-a: `e2c7965bc891075b22688309507e620871338083`.
- repo-b: `6a8d0a28a233be3b5601490cd57cb27ddff4fc0b`.

Los cuatro worktrees nacieron de repo-a en ramas `codex/worktree-*` nuevas.
El positivo `.git` regular se observó **antes** de agregarle las fixtures del
filtro y borrado; esas etapas se distinguen para no mezclar estados.

Fixture inicial tracked de repo-a:

| Path | Bytes |
|---|---|
| `.gitignore` | `src/ignored.py\nsrc/ignored_dir/\nbuild/\n.coverage*\n**/__pycache__/\n` |
| `src/a.py` | `abc\n` |
| `src/z.py` | Vacío |
| `src/flag.py` | `flag\n` |
| `src/con espacio-é.py` | `unicode\n` |
| `tests/data/item.bin` | `resource\n` |

Repo-b solo contiene `other.txt = b'other tree\n'`. Estas son fixtures del
protocolo Git; no afirman cumplir los required files/roots de un snapshot P1.

## 3. Receta observada y alcance del ensayo

Prefijo utilizado en las consultas:

```json
["/usr/bin/git","--no-optional-locks","-c","core.fsmonitor=false","-c","core.untrackedCache=false","-c","core.hooksPath=/dev/null","-c","core.excludesFile=/dev/null"]
```

Entorno completo suministrado a cada consulta, sin herencia:

```json
{"PATH":"/usr/bin:/bin","LANG":"C","LC_ALL":"C","GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":"/dev/null","GIT_TERMINAL_PROMPT":"0"}
```

`subprocess` recibió argv como lista, cwd explícito, `shell=False` por default,
captura binaria, `timeout=5`. La sonda no implementó el lector acotado durante
streaming: las salidas pequeñas observadas **no califican el tope de 2 MiB** ni
la terminación del grupo de procesos/helper al agotar presupuesto.

Consultas completadas en la raíz limpia:

| Sufijo argv | Exit | Stdout exacto / disposición |
|---|---:|---|
| `rev-parse --is-inside-work-tree` | 0 | `true\n` |
| `rev-parse --show-prefix` | 0 | `\n` |
| `rev-parse --show-toplevel` | 0 | Path absoluto de repo-a + LF |
| `rev-parse --verify HEAD^{commit}` | 0 | SHA completo repo-a + LF |
| `rev-parse --verify e2c7965bc891075b22688309507e620871338083^{commit}` | 0 | Mismo SHA completo + LF |
| `ls-files --stage -z` | 0 | Seis entradas staged, formato modo/blob/stage TAB path NUL |
| `ls-files -v -z` | 0 | Seis tags `H`, paths UTF-8, NUL |
| `config --bool --get core.sparseCheckout` | 1 | Stdout/stderr vacíos: configuración ausente |
| `status --porcelain=v1 -z --untracked-files=all --ignored=matching --no-renames --ignore-submodules=none` | 0 | Stdout/stderr vacíos |

La primera corrida del driver se detuvo en un `AssertionError`: había puesto
literalmente `stdout == b''` para show-prefix. No se atribuye ese fallo a Git
ni se borra del historial. La segunda mantuvo la receta y corrigió **solo la
expectativa de la sonda** a `b'\n'`; completó las consultas. Por eso PG01 pide
reconciliar el framing en la propuesta, no cambiar Git para fabricar el positivo.

SHA-256 de stdout NUL del índice inicial completo:
`b0d2d6cc412cdf1a65dad87c9796a42f039d72b06103e01f03027c90c82f28e1`.
Dos entradas, tomadas de esa salida real, coinciden con los blobs del vector
literal de la propuesta:

```text
100644 8baef1b4abc478178b004d62031cf7fe6db6f903 0\tsrc/a.py\0
100644 e69de29bb2d1d6434b8b29ae775ad8c2e48c5391 0\tsrc/z.py\0
```

Esta notación muestra escapes, no agrega LF al protocolo NUL. Se observaron
los metadatos del vector; **no se ejecutó una proyección/serialización P02a**.
El SHA del blob Git no es el SHA-256 crudo del archivo.

## 4. Índice y worktree distintos; ignorados y outputs

Después del commit inicial, `src/a.py` se cambió a `abd\n` y se stageó;
después se cambió a `abe\n` sin staging. El HEAD siguió igual. También se
crearon `src/new.py`, un ignorado individual, dos hijos de directorio ignorado,
outputs/cachés, `src/.coverage_model.py` y se modificó el archivo Unicode.

Resultado real de status, escape `\0` representa NUL:

```text
MM src/a.py\0
 M src/con espacio-é.py\0
?? src/new.py\0
!! .coverage\0
!! build/\0
!! src/.coverage_model.py\0
!! src/__pycache__/\0
!! src/ignored.py\0
!! src/ignored_dir/\0
```

No hay LF entre los registros reales. Exit 0, stderr vacío; SHA-256 de stdout:
`95a653c415fd73822e44782d0c69de27211d804d0a6a029f18835a87a98cb7a8`.
El índice mostró para `src/a.py` el blob staged
`4d0dc3ad822fa9f6bccfb218295ba5fda986367f`; bytes leídos del worktree `abe\n`
tienen SHA-256
`614c0cc3d0b3c4d78bbde46fd89f527e603bfacc5cb663590d21c282fef1505a`.
Son observaciones separadas: Git no ofrece los bytes realmente ejecutados a
través de ese blob staged ni a través de `MM`.

Interpretación manual del contrato, **no un resultado de implementación**:

- `src/new.py`, `src/ignored.py` y ambos hijos de `src/ignored_dir/` deben
  inventariarse; no los elimina `??`/`!!`.
- El `!!` de directorio agrega sus hijos: se necesita el inventario filesystem
  independiente para expandirlos. No puede inferirse N ni sus nombres del tag.
- `src/.coverage_model.py` debe incluirse aunque Git lo ignore: la exclusión
  `.coverage*` de P02a es solo en la raíz, no en `src`.
- `.coverage`, build y caché se excluyen del digest de inputs por contrato,
  no porque Git diga `!!`. La proyección y estabilidad de su digest no se
  probaron aquí: aún no existe ese código.

Espacios/acentos se conservaron como UTF-8 real en ambos protocolos `-z`;
no aparecieron comillas ni escapes octales como en la prosa de `git commit`.

## 5. Toplevel, raíz y entorno; worktree válido

Control defectuoso deliberado: mismo cwd repo-a, pero se añadieron al entorno
de prueba estas tres variables conocidas, sin leer el entorno del usuario:

```text
GIT_DIR=<fixture>/repo-b/.git
GIT_WORK_TREE=<fixture>/repo-b
GIT_INDEX_FILE=<fixture>/repo-b/.git/index
```

Git devolvió toplevel repo-b y HEAD
`6a8d0a28a233be3b5601490cd57cb27ddff4fc0b`, **exit 0**. El mero exit no detecta
la atribución falsa. Con el entorno cerrado de §3, mismo cwd, devolvió repo-a
y HEAD `e2c7965bc891075b22688309507e620871338083`, exit 0.

Con cwd `repo-a/src`, Git retornó show-prefix `src/\n` y toplevel repo-a,
exit 0: la API debe rechazar la raíz subdirectorio, no aceptar solo porque Git
puede resolver un HEAD. Son comparaciones esperadas para la futura frontera;
no se ejecutó `InputCaptureError` inexistente.

Con cwd worktree-valid recién creado: show-prefix `\n`, toplevel su propio
path y HEAD inicial de repo-a. Observación `lstat`: `.git` es archivo regular
en el worktree y directorio en repo-a; inodes de ambas raíces distintos.
Ambos son positivos Git válidos. No se calculó todavía digest portable P02a
ni se afirmó propiedad/aislamiento por esos inodes.

## 6. Estados explícitamente no soportados

En worktree-flags se prepararon flags solo de fixture:

```text
git update-index --assume-unchanged -- src/flag.py
git update-index --skip-worktree -- src/z.py
```

La consulta contratada `ls-files -v -z` devolvió, entre otros registros:
`h src/flag.py\0` y `S src/z.py\0`, exit 0. Confirma que la receta puede
observar esos flags; **no** prueba que el adaptador futuro los rechace.

En dos ramas fixture separadas se commitearon `src/a.py = ours\n` y `theirs\n`.
Su merge deliberado devolvió exit 1 y conflicto de contenido. La consulta
`ls-files --stage -z` mostró para `src/a.py`:

```text
100644 8baef1b4abc478178b004d62031cf7fe6db6f903 1\tsrc/a.py\0
100644 b19a1e93bec1317dc6097229e12afaffbfa74dc2 2\tsrc/a.py\0
100644 950b81b7eee953d050aa05a641f8e056c85dd1bd 3\tsrc/a.py\0
```

Status devolvió exactamente `UU src/a.py\0`, exit 0. Rechazo esperado del
perfil, no fallo de la herramienta. El inventario no debe colapsar los tres
stages en un dict por path antes de identificar el estado no soportado.

Base inexistente `0000000000000000000000000000000000000000^{commit}`:
exit 128, stdout vacío, stderr `fatal: Needed a single revision\n`.
No se infiere un HEAD/base fallback. No se prepararon sparse checkout activo,
gitlink/submódulo, repos unborn ni Git ausente en esta sonda acotada.

## 7. PG02 reproducido: status ejecuta filtro clean local

Solo en la fixture se añadió `.gitattributes`:

```text
filter_input.txt filter=p02a-probe
```

Configuración local creada para el ensayo (compartida por sus worktrees):

```text
filter.p02a-probe.clean=/usr/bin/python3 tools/filter_probe.py
filter.p02a-probe.required=true
```

Helper controlado, contenido completo:

```python
import sys

sys.stderr.write("P02A_CONTROLLED_FILTER_EXECUTED\n")
sys.stdout.buffer.write(sys.stdin.buffer.read())
```

No lee otros archivos, no escribe archivos, no hace red. El archivo filtrado
se commiteó con `before\n`; luego se cambió a `after!\n`, mismo tamaño. Durante
la preparación Git add/commit ya emitió marcas del helper: se registran como
**preparación**, no como prueba de la receta read-only.

La evidencia decisiva es la consulta `status` posterior con **exactamente**
el prefijo/entorno de §3. Exit 0; incluyó ` M filter_input.txt\0` en stdout y
en stderr:

```text
P02A_CONTROLLED_FILTER_EXECUTED
P02A_CONTROLLED_FILTER_EXECUTED
P02A_CONTROLLED_FILTER_EXECUTED
```

Esto refuta «esta receta no invoca helpers» incluso con todas las restricciones
que sí contiene la propuesta. La lectura de un patch puede ejecutar código a
través de Git, antes de pytest. No se ensayaron filtros process/smudge; el
contraejemplo clean basta para refutar la afirmación universal.

Recomendación de diseño **aún no implementada ni calificada**: definir un
perfil inicial sin filtros y detectar/rechazar clean/process activos antes de
la primera consulta que pueda invocarlos, con control válido sin filtros y
negativos propios. No usar un glob de `-c filter.*` suponiendo que Git lo
expande; ni resolverlo solo con «el repo es cooperativo» mientras se mantiene
el claim de no helpers. El arquitecto decidirá la receta revisada.

## 8. PG03 reproducido: outputs tracked eliminados sin frontera actual

Solo en worktree-valid se crearon y añadieron explícitamente con `git add -f`
dos archivos de prueba que `.gitignore` excluiría. Se commitearon en
`cbeae64` (`test: prepare filter and tracked output probes`) y después se
borraron con `apply_patch`. Se retiraron sus directorios ya vacíos con `rmdir`
sobre los dos paths exactos de fixture. **Los bytes son recuperables en ese
commit local**; no se borró ningún archivo del usuario ni de WCT.

La consulta `ls-files --stage -z` aún devolvió:

```text
100644 2580bd6cfe1ae3cb198b82b89d193af6b83ef06e 0\tbuild/tracked-report.txt\0
100644 aa46d860bb6b37889f69bb947719a26a120814cf 0\tsrc/__pycache__/tracked-cache.pyc\0
```

Status completo en esa etapa (incluye el caso del filtro):

```text
 D build/tracked-report.txt\0
 M filter_input.txt\0
 D src/__pycache__/tracked-cache.pyc\0
```

Exit 0. SHA-256 de stdout:
`51be97358f5376727f369d1fb9195299a441a977ab4a9300d7ad3b46af18db8e`.
Las comprobaciones `.exists()` de `build` y `src/__pycache__` devolvieron false.
Git conserva paths y modo de **archivo**, no un `lstat` de sus padres borrados.

El contrato quiere ignorar cambios de outputs, pero la regla para excluir
directorios se formula sobre fronteras encontradas. Falta fijar cómo se aplica
al índice/status histórico cuando ya no existe la frontera. Resolverlo por
substring introduciría otro defecto: un archivo regular llamado `build`
debe seguir incluido, y `src/build.py` tampoco es output. La revisión debe
definir el caso eliminado por componentes/tipo/disposición explícita, con
positivos equivalentes y sin depender solo del filesystem presente. No se
escribió una proyección ad hoc para hacer pasar la sonda.

## 9. Cierre, comprobaciones y custodia

**Observado:** receta normal, framing NUL/escalares, staged ≠ worktree,
ignorado individual/directorio, outputs, Unicode/espacios, inyección de raíz
por entorno y control cerrado, subdirectorio, worktree legítimo, flags,
conflicto, base no resoluble, helper clean y eliminados tracked.

**No observado/calificado:** algoritmo de proyección/manifest/digests P02a,
frescuras antes/después de productor, límites streaming/timeout con helpers,
symlinks/TOCTOU del inventario, sparse activo/submódulos, semántica Git SHA-256,
otra plataforma/versiones, private workspace P02b y ensamblaje P03/P06.
No se ejecutaron tests de producto, mutación, inferencias ni medición de ahorro.
La batería central previa del arquitecto no califica estos mecanismos nuevos.

Se conserva la primera sonda fallida (PG01), la segunda con expectativa
corregida y los desafíos; sin reescribir la propuesta para convertirlos en
éxitos retrospectivos. Los stdout esenciales se incluyen aquí como escapes y
hashes; recibos completos de las llamadas permanecen en la conversación.
Fixtures/Git locales: custodia `local-only`, sin copia externa ni replay durable
garantizado. No se limpian esos repos al cerrar esta tarea.

Puerta siguiente: reconciliar PG01–PG03 con el arquitecto/specifier, challenge
de la versión revisada y aprobación humana del contrato/Gherkin. Solo después
puede entregarse implementación P02a con la nueva versión congelada.

## 10. Addenda: consulta preventiva propuesta por el arquitecto para revisión 2

Después de los resultados anteriores, el arquitecto propuso rechazar de forma
conservadora cualquier clave efectiva `filter.*` antes de consultar status.
Su primera formulación incluía `--local`; **la corrigió antes de ensayarla**
para no excluir `config.worktree` cuando `extensions.worktreeConfig=true`.
No se atribuye esa primera formulación a la propuesta 1 ni se registró una
ejecución preventiva con `--local` que no ocurrió.

Sufijo de argv ensayado con el mismo prefijo/entorno cerrado de §3:

```json
["config","--includes","--null","--name-only","--get-regexp","^filter\\."]
```

Resultados reales de las dos consultas adicionales:

| Fixture | Exit | Stdout exacto | Stderr |
|---|---:|---|---|
| worktree-valid, con filtro controlado de §7 | 0 | `filter.p02a-probe.clean\0filter.p02a-probe.required\0` | Vacío |
| repo-b, sin filtros | 1 | Vacío | Vacío |

SHA-256 del stdout con claves:
`d43e2f7e647b69a1b70cb98b3552a7483da4616b69c36ff8b8417f03fa5814fb`.
No se volcaron valores de configuración. No apareció la marca de ejecución
que el helper controlado emite incondicionalmente en stderr; a diferencia de
status, esta consulta no ejecutó ese filtro en la fixture observada.

Esto acredita **detección de claves del filtro local de esta fixture** y el
positivo de ausencia con exit 1/vacío. No se prepararon fixtures adicionales
para includes ni `config.worktree`; retirar `--local` evita estrechar la
consulta, pero aquí no se califica experimentalmente cada origen posible.
No se implementó el rechazo, sus límites ni el orden de preflight en P02a.
La condición propuesta es rechazar cualquier clave, incluso si un filtro
parece inactivo; esa limitación de adopción debe aprobarse, no deducirse del
éxito de esta consulta.

Persisten PG01/PG03 y la reconciliación del contrato para PG02. La comprobación
no protege frente a otro escritor del mismo UID que cambie configuración entre
preflight y status. Los rojos originales permanecen vigentes para propuesta 1;
esta addenda es evidencia de una alternativa para la futura revisión 2, no una
corrección retrospectiva ni autorización del coder.

## 11. Addenda final: consultas de revisión 2 contrastadas en fixtures nuevas

Encargo acotado adicional del arquitecto: contrastar includes/config.worktree,
tipado de eliminados staged y `--no-lazy-fetch`, sin crear lector/proyección.
Revisión 2 inspeccionada, no modificada por este specifier:
`1aac1287b73974338d9a9516491788493c6382db678e5b32c1ad810bc9d541c2`.
Esta sección amplía el alcance observado; no borra las limitaciones que tenían
las sondas anteriores en el momento de ejecutarse.

Fixtures nuevas, creadas con `mktemp -d`, bajo:

```text
/home/jandradeu/Documents/well_code_template/build/tmp/beta3-campaign-review.Sjppx9/git-p02a-final.oKQ12n/
  config-source/
  config-worktree/
  history-directory/
  history-regular/
  partial-source/
  partial-clone/
  full-clone/
```

Archivos por `apply_patch`; commits de fixture con fecha Git sintética
2000-01-03, sin atribuirla a la ejecución actual. No se tocó WCT ni repositorios
del usuario. Las únicas transferencias fueron clones `file://` desde un origen
de prueba propio dentro de este mismo directorio. No hubo remoto externo,
credenciales ni modificación/eliminación de objetos para forzar el caso parcial.

Todas las consultas de esta addenda usaron el mismo entorno cerrado de §3 y
el prefijo de revisión 2, que añade `--no-lazy-fetch`:

```json
["/usr/bin/git","--no-optional-locks","--no-lazy-fetch","-c","core.fsmonitor=false","-c","core.untrackedCache=false","-c","core.hooksPath=/dev/null","-c","core.excludesFile=/dev/null"]
```

### 11.1 Claves efectivas desde include y config.worktree

El nuevo repo config-source comenzó sin filtros. Después se añadió por
configuración local un `include.path` absoluto hacia una fixture propia,
`config-fixtures/local.inc`, cuyo contenido es:

```gitconfig
[filter "frominclude"]
    clean = /usr/bin/false
```

Se activó `extensions.worktreeConfig=true` en el repo fixture y, desde su
worktree separado, se configuró únicamente allí
`filter.fromworktree.process=/usr/bin/false` con `git config --worktree`.
Los valores son inertes y propios del ensayo; la consulta publica solo claves.

Consulta exacta de revisión 2:

```json
["config","--includes","--null","--name-only","--get-regexp","^filter\\."]
```

| Etapa / cwd | Exit | Stdout exacto | Stderr |
|---|---:|---|---|
| config-source antes de añadir include | 1 | Vacío | Vacío |
| config-source después del include | 0 | `filter.frominclude.clean\0` | Vacío |
| config-worktree después de su configuración propia | 0 | `filter.frominclude.clean\0filter.fromworktree.process\0` | Vacío |
| config-source después de configurar el otro worktree | 0 | `filter.frominclude.clean\0` | Vacío |

Digests de stdout: include solo
`ef2172d0f15caa341de2a93688b48b208075fda53e45a7227c657434c74d739d`;
include + worktree
`459bb83d1f2c42f647d9e1afd45ecd26795f949ce42ad97aa0becdcbe76874cd`.
Confirma detección de esas dos procedencias y que la configuración del worktree
no se atribuye automáticamente al árbol principal. No se ejecutó status después
de detectar claves, ni se implementó el rechazo automático de P02a. No califica
includes condicionales de todas las formas, ciclos, límites, errores de lectura
ni carreras de configuración; son dimensiones distintas de esta sonda.

### 11.2 `ls-tree` conserva el tipo de eliminados staged

Dos repos separados contienen, antes del borrado:

- history-directory, commit fixture `9643bb2`: `build/report.txt`,
  `src/__pycache__/cache.pyc`, `src/real.py`.
- history-regular, commit fixture `52b3500`: un **archivo regular** final
  `build`, y `src/real.py`.

Se borraron los dos outputs del primero y el archivo `build` del segundo con
`apply_patch`. Se retiraron los dos directorios ya vacíos de history-directory
con `rmdir` y se stagearon las eliminaciones mediante `git add -- <paths
exactos>`. Solo bytes de fixture; permanecen recuperables en esos commits.

En ambos repos, `ls-files --stage -z` ya muestra **solo** `src/real.py`.
Status de eliminaciones staged y árbol de HEAD conservaron:

| Repo | Status NUL, exit 0 | Entradas pertinentes de `ls-tree -r -z --full-tree HEAD`, exit 0 |
|---|---|---|
| history-directory | `D  build/report.txt\0D  src/__pycache__/cache.pyc\0` | `100644 blob 2580bd6cfe1ae3cb198b82b89d193af6b83ef06e\tbuild/report.txt\0` y `100644 blob aa46d860bb6b37889f69bb947719a26a120814cf\tsrc/__pycache__/cache.pyc\0` |
| history-regular | `D  build\0` | `100644 blob d9029698bbf3ad086d3bb0e6747e90df87846888\tbuild\0` |

Stderr vacío en todas esas consultas. SHA-256 de stdout completo de ls-tree:
history-directory
`dfc529304f4115abc5c3e2c61caeeed3f8e29dc7fba681972889b15eff765092`;
history-regular
`8f49e936f9e60b747e8cb10c0d7fe4062e354e62ef95e78ce917a43e50222cf1`.

Son datos suficientes para aplicar la distinción **especificada** por el
arquitecto en revisión 2: `build` como ancestro estructural de `build/report.txt`
no es el componente final regular `build`. Git aporta el modo final aun cuando
el índice ya lo eliminó. Aquí no se implementó esa proyección ni se afirmó que
un digest de inputs permanezca estable: su algoritmo y falsos positivos todavía
deben verificarse sobre el futuro código.

### 11.3 Partial clone local: falta de árbol sin descarga implícita

Se creó partial-source con dos archivos: `src/a.py = b'abc\n'` y
`src/nested/b.py = b'nested\n'`. HEAD completo:
`d1e66e00c5839f8c7593b78f6c8ee1516f9eb41b`.
Solo en ese origen propio se configuró `uploadpack.allowFilter=true`.

Preparación del negativo, por transporte de archivo local exclusivamente:

```text
/usr/bin/git clone --no-checkout --no-local --filter=tree:0 file://<fixture>/partial-source <fixture>/partial-clone
```

Preparación del positivo equivalente, mismo origen y HEAD:

```text
/usr/bin/git clone --no-checkout --no-local file://<fixture>/partial-source <fixture>/full-clone
```

Ambos clones devolvieron exit 0 y solo el mensaje de clonación; no hubo warning
de filtro ignorado. No se hizo checkout, fetch posterior, ni borrado manual de
objetos. Los comandos clone son preparación autorizada de fixtures, no forman
parte de la API P02a ni se presentan como consultas sin transferencias.

Resultados usando el prefijo **con `--no-lazy-fetch`**:

| Consulta | Partial clone `tree:0` | Clone completo |
|---|---|---|
| `rev-parse --verify HEAD^{commit}` | Exit 0, HEAD `d1e66e0…` | Exit 0, el mismo HEAD |
| `ls-tree -r -z --full-tree HEAD` | **Exit 128**, stdout vacío, stderr `fatal: not a tree object\n` | **Exit 0**, dos registros de archivos, stderr vacío |
| `count-objects -v`, antes/después | `in-pack: 1`, `packs: 1`, salida byte-idéntica | `in-pack: 6`, `packs: 1`, salida byte-idéntica |

Stdout del positivo:

```text
100644 blob 8baef1b4abc478178b004d62031cf7fe6db6f903\tsrc/a.py\0
100644 blob 79c53955ef856f16f2107446bc721c8879a1bd2e\tsrc/nested/b.py\0
```

SHA-256: `114475328b8e1923d52c8a40dc15af19dcae883929dc001d34589287f4c11f5a`.
El negativo confirma que conocer el commit no implica tener sus árboles, y la
consulta falla visiblemente con la bandera exigida. No se quitaron restricciones
para convertirla en verde. El positivo descarta que esa receta rechace todo.
El conteo estable acompaña la ausencia de reparación de objetos observada;
no se instrumentaron paquetes de red/syscalls ni se extrapola una garantía de
aislamiento a otra versión de Git o a un proceso hostil del mismo UID.

### 11.4 Cierre de esta ampliación

Las consultas concretas solicitadas tienen ahora salidas reales y controles
positivos/negativos. No surgió un nuevo bloqueo en estas tres preparaciones.
Los rojos de propuesta 1 permanecen registrados; el arquitecto debe evaluar
si la revisión 2 y esta evidencia satisfacen su puerta documental D1.

No se implementaron snapshot, proyección, límites de streaming, errores de
P02a ni comparación final. No se repitieron gates: la batería central pertenece
al arquitecto y al código ya existente. La aprobación humana de contrato y
Gherkin sigue siendo previa al coder; esta sonda no la sustituye.
Todas las nuevas fixtures quedan preservadas bajo `build/tmp` con custodia
`local-only`. No se reclamó replay externo durable ni medición económica.
