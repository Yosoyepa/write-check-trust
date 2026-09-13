# Preparación de salida incremental beta.3.1

Fecha: 2026-09-13. Estado: **preparación documental; no es GO, bless, merge, tag ni publicación**.

Este documento consolida la base aceptada para preparar una entrega incremental.
No modifica ni reemplaza los expedientes históricos L1/r1b, r2b o r3; tampoco
incorpora archivos no seguidos del worktree. No autoriza campañas de mutación,
bump, bless, merge, tag, release ni cambios de producto, tests permanentes,
gobernanza o workflows.

## 1. Corte e identidad consultada

- Worktree consultado:
  `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration`.
- Rama: `codex/beta3-ac1-r2-integration`.
- Commit de referencia documental: `fb7f7254129bf47ebd20a50d6045ebed4982e667`.
- La identidad actual **no es candidata**: al corte, el worktree contiene
  cambios ajenos en `tests/unit/test_accept_campaign.py`, el archivo no seguido
  `descendant.py` y una addenda r3 no seguida. No se inspeccionan, mezclan,
  restauran, añaden ni atribuyen a este plan.

Toda calificación futura empieza desde un checkout aislado y limpio del SHA que
se pretenda fusionar. La preservación por commit/push sólo conserva un
candidato revisable; no acredita su comportamiento ni autoriza la salida.

## 2. Fronteras que deben permanecer separadas

1. **Preservación:** commit/push de código, documentación y referencias. No
   cambia el estado de calificación.
2. **Calificación pre-merge:** resuelve sobre un candidato limpio las puertas
   funcionales, de calidad, mutación, aceptación, cobertura, CRAP, DRY,
   integridad y revisión independiente aplicables. Un pendiente técnico no se
   difiere para resolverlo tras el merge.
3. **Bless humano:** se hace sólo sobre el diff final protegido, incluida la
   versión y lock si fueron autorizados. No prueba comportamiento ni autoriza
   automáticamente merge o publicación.
4. **Merge:** ocurre únicamente cuando la calificación pre-merge, la revisión
   humana, el bless final y la CI de PR están conformes.
5. **Verificación post-merge:** comprueba el SHA real de `main` que se
   etiquetaría. No sirve para reparar un bloqueo ni para cambiar el candidato.
6. **Publicación:** requiere decisión D3 separada, evidencia del SHA final,
   custodia verificable, SBOM, smoke y comprobación remota del canal.

Cualquier bloqueo post-merge —quality, integridad, full, smoke, SBOM, custodia,
versión, asset o metadata remota— **detiene la publicación**. No se etiqueta,
no se publica, no se mueve un tag y no se corrige directamente sobre `main`;
la reparación vuelve a un incremento revisable y repite las puertas afectadas.

## 3. Identidad de lotes AC1: referencias, no agregación

Los conteos no se mezclan ni se presentan como una campaña integral:

- **L1 / r1:** `498 = 468 killed + 30 survived`; alcance de cuatro módulos.
  Fuentes: `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration/docs/evolution/plans/BETA3/EXECUTION/ADJUDICACION-SUPERVIVIENTES-AC1-L1-2026-09-12.md`
  y `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration/docs/evolution/plans/BETA3/EXECUTION/RESULTADO-AC1-R2-REANUDACION-2026-09-13.md`.
- **r1b:** repetición del mismo alcance L1, con producto idéntico y pruebas de
  diagnóstico endurecidas: `498 = 493 killed + 5 survived`; esos cinco son las
  equivalencias ratificadas de ese lote. Fuente:
  `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration/docs/evolution/plans/BETA3/EXECUTION/RESULTADO-AC1-L1B-2026-09-13.md`.
- **r2b:** lote distinto del núcleo puro de `accept/`: `486 = 462 killed + 24
  survived`; los 24 se ratificaron bajo bytes, runtime y precondiciones
  documentadas. El r2 previo con `51 no-tests` es antecedente de receta, no
  evidencia intercambiable con r2b. Fuentes:
  `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration/docs/evolution/plans/BETA3/EXECUTION/RESULTADO-AC1-LOTE-R2-2026-09-13.md`
  y `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration/docs/evolution/plans/BETA3/EXECUTION/RATIFICACION-AC1-R2B-H01-H04-2026-09-13.md`.
- **r3:** lote distinto de transporte: `497 = 450 killed + 47 survived`; la
  adjudicación técnica no ratifica automáticamente ninguno. Sus decisiones,
  regresiones y propuesta de hooks permanecen en sus expedientes existentes y
  no se duplican aquí. Fuentes:
  `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration/docs/evolution/plans/BETA3/EXECUTION/RESULTADO-AC1-LOTE-R3-2026-09-13.md`,
  `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration/docs/evolution/plans/BETA3/EXECUTION/ADJUDICACION-SUPERVIVIENTES-AC1-R3-2026-09-13.md`
  y `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration/docs/evolution/plans/BETA3/EXECUTION/ADENDA-AC1-R3-CUSTODIA-Y-HASHES-2026-09-13.md`.

## 4. Candidato aislado: Git, runtime, imports y artefactos

Un árbol Git limpio es necesario, pero no basta. Para cualquier calificación
pre-merge o verificación post-merge se debe registrar y aislar lo siguiente:

- **Git e inputs:** checkout o worktree nuevo, detached al SHA objetivo;
  `git status --porcelain` vacío; `git rev-parse HEAD`, `sha256sum uv.lock` y
  manifiesto de fuentes/tests del alcance antes y después de la corrida.
- **Runtime y escrituras de preparación:** crear un entorno nuevo del checkout
  con `uv sync --frozen --group dev --group quality`; registrar ruta de
  `sys.executable`, Python, uv, pytest, mutmut y Commitizen. Esta preparación
  puede crear o actualizar `<checkout>/.venv/` y la caché de uv: son escrituras
  previstas, declaradas y distintas de los artefactos de ejecución. Se debe
  fijar `UV_CACHE_DIR` dentro de la raíz del run cuando sea viable; si la caché
  queda fuera, se registra su ruta absoluta y su política de limpieza. Con
  `--frozen` no se permite modificar `pyproject.toml` ni `uv.lock`. No
  reutilizar el venv histórico `sh-p01-CND-80B8` como runtime de release; sólo
  usarlo para interpretar evidencia histórica que lo cita.
- **Imports:** no heredar `PYTHONPATH`, `PYTHONHOME` ni user-site del host.
  Usar `PYTHONSAFEPATH=1`, `PYTHONNOUSERSITE=1` y
  `PYTHONDONTWRITEBYTECODE=1`; registrar `tools.wct.__file__`,
  `example.__file__` y el origen de cualquier plugin cargado. Los imports deben
  resolver al checkout aislado, no a la copia de la PR, a `build/tmp` previo ni
  a paquetes globales.
- **Ejecución y artefactos:** después de preparar el runtime, cada corrida
  recibe una raíz propia bajo
  `<checkout>/build/tmp/release-beta3.1/<run-id>/` para `TMPDIR`,
  `PYTEST_DEBUG_TEMPROOT`, logs, LCOV, SBOM, reports, capturas y, si se eligió,
  la caché de uv. Fuera de esa raíz sólo se permiten las escrituras de
  preparación explícitamente declaradas (`.venv/` y la caché de uv registrada).
  Ninguna salida de tests o herramientas puede sobrescribir rutas históricas ni
  tomarse como vigente por fecha/modificación.
- **Limpieza:** no se borra ningún directorio de evidencia hasta que la copia
  durable y su prueba de recuperación hayan pasado. La limpieza es una decisión
  posterior, no una fase automática de los tests.

El aislamiento no convierte el candidato en sandbox frente a código hostil; el
límite de confianza sigue siendo cooperativo, conforme a
`/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration/docs/evolution/plans/BETA3/decisions/ADR-B3-02-confianza.md`.

## 5. Custodia durable sin circularidad

### 5.1 Estado actual

Los documentos de `docs/evolution/plans/BETA3/EXECUTION/` están versionados;
la evidencia cruda no. Por `.gitignore`, `build/` queda ignorado, incluidos:

- `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration/build/tmp/ac1-r2-qualification/evidence/`
- `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration/build/tmp/ac1-r2-qualification/preflight-h04/`
- `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration/build/tmp/ac1-r2-qualification/r3-adjudication/`
- `/home/jandradeu/Documents/well_code_template/build/tmp/adjudicacion-ac1-l1/`

Los hashes en las actas identifican bytes, pero no constituyen por sí mismos
custodia durable, recuperación ni inmutabilidad. El estado actual es
`local-only` hasta una copia verificada en un destino aprobado.

### 5.2 Diseño propuesto

El manifiesto canónico futuro se llama de forma estable, no por su propio hash:

```text
<checkout>/docs/evolution/plans/BETA3/EXECUTION/CUSTODIA-BETA3.1.json
<checkout>/docs/evolution/plans/BETA3/EXECUTION/CUSTODIA-BETA3.1.json.sha256
```

`CUSTODIA-BETA3.1.json` **no contiene su propio SHA-256** ni los campos
`candidate_commit`, SHA candidato, tag o tag previsto. Identifica el origen de
la evidencia, no el commit que en el futuro pudiera contener el manifiesto o
recibir un tag: por cada artefacto registra `evidence_source_commit` y, si
corresponde, la referencia de origen. También registra `lote`,
`ruta_relativa`, `sha256`, `bytes`, `tipo`, `input_manifest_sha256`,
`productor`, `verifier`, `estado_de_ratificacion`, fecha, owner, runtime y la
referencia al documento histórico que lo describe. Su digest vive únicamente
en el compañero separado `CUSTODIA-BETA3.1.json.sha256`; el SHA de Git que
contenga estos ficheros no se escribe dentro de ellos.

La copia cruda futura se empaqueta sin venvs, secretos ni caches como un
conjunto de ficheros hermanos, todos fuera del archivo comprimido:

```text
beta3.1-expediente-<custody-run-id>.tar.zst
beta3.1-expediente-<custody-run-id>.tar.zst.sha256
CUSTODIA-BETA3.1.json
CUSTODIA-BETA3.1.json.sha256
SHA256SUMS
```

El `.tar.zst` contiene solamente los artefactos de evidencia. Su sidecar
`.tar.zst.sha256` verifica el archivo comprimido. `SHA256SUMS` inventaría los
miembros extraídos y el manifiesto, pero no se incluye a sí mismo, no incluye
los sidecars y no se inserta dentro del `.tar.zst`; así tampoco existe una
referencia indirecta del hash del bundle sobre un fichero que lo contiene.
Debe conservar planes, preflights, logs de corrida, results-all, diffs de
supervivientes, reconciliaciones, metadatos, sondas/veredictos y los
manifiestos de entradas de cada lote, sin mezclar sus identidades.

Antes de D3 debe existir una copia del conjunto en un destino durable aprobado,
con identificador de objeto y versión, retención/protección, responsable y
recuperación satisfactoria registrados. Esa copia durable recuperada es la
fuente de custodia; un asset de prerelease sólo puede añadirse después como
copia de conveniencia, nunca como el primer destino durable ni como base de la
prueba previa a la publicación. Un asset de release o un tag no se describe
como inmutable sin comprobar el mecanismo de protección y recuperación
realmente disponible en el servicio elegido.

### 5.3 Prueba de recuperación obligatoria antes de D3

La prueba no ejecuta mutmut ni reconstruye resultados. En un host limpio,
antes de autorizar D3:

1. Obtener el conjunto desde el destino durable aprobado mediante su
   identificador y versión, por una ruta distinta de la copia original y no
   desde un asset de release.
2. Verificar los digests separados del manifiesto y del `.tar.zst`; leer los
   `evidence_source_commit` para comprobar la procedencia de cada artefacto,
   sin exigir que coincidan con un tag o con el commit que pudiera versionar el
   manifiesto.
3. Verificar `SHA256SUMS`; rechazar rutas absolutas, `..`, symlinks inesperados
   o miembros no inventariados antes de extraer.
4. Extraer en una raíz nueva y volver a calcular cada hash listado.
5. Para cada lote por separado, comprobar que `results-all`, reconciliación y
   diffs representan el mismo conjunto de IDs y el conteo registrado; no sumar
   L1/r1b, r2b y r3.
6. Registrar el comando, host, runtime, identificador/versionado remoto,
   digest del manifiesto, digest del bundle y resultado de la recuperación en
   un acta externa de custodia, sin editar los expedientes históricos.

Hasta que esta prueba pase, el checklist conserva `custodia no verificada` y
D3, el tag y la publicación permanecen bloqueados.

### 5.4 Vínculo posterior con el SHA etiquetado

Una vez que un tag haya sido autorizado y creado sobre el SHA final, una
atestación externa posterior —fuera del commit etiquetado, del manifiesto y del
bundle— vincula explícitamente `tag`, `tagged_commit`, digest del manifiesto,
digest del bundle, identificador/versionado durable y el acta de recuperación
pre-D3. Esta atestación no modifica el candidato ni intenta hacer que el
manifiesto prediga el SHA que lo contiene. Si no puede emitirse o verificarse,
se detiene la publicación; adjuntar después el conjunto como asset no sustituye
ni la copia durable ni este vínculo externo.

## 6. Compatibilidad PEP 440 y Commitizen

La pareja autoritativa propuesta es:

```text
Paquete: 1.0.0b3.dev1
Tag:    v1.0.0b3.dev1
Orden:  1.0.0b2 < 1.0.0b3.dev1 < 1.0.0b3
```

Comprobaciones no mutantes ya realizadas:

- `packaging.version.Version("1.0.0b3.dev1")` es válido.
- `tools.wct` obtiene la versión desde `importlib.metadata`; su test canónico
  compara según PEP 440.
- La configuración actual de Commitizen acepta y extrae el tag histórico
  `v1.0.0-beta.2` como `1.0.0b2`.
- La configuración actual genera `v1.0.0b3.dev1` desde `v$version`, pero no lo
  filtra ni extrae completo; la configuración propuesta siguiente sí acepta y
  extrae ambos tags con correspondencias exactas.
- El filtro `tags: ["v*"]` de
  `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration/.github/workflows/adoption-smoke.yml`
  coincide con `v1.0.0b3.dev1`. `quality.yml` no se dispara por tag y
  `full-hardening.yml` sigue siendo manual/programado.

### 6.1 Diff protegido propuesto, no aplicado

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
@@ [project]
-version = "1.0.0-beta.2"
+version = "1.0.0b3.dev1"
@@ [tool.commitizen]
 name = "cz_conventional_commits"
-version = "1.0.0-beta.2"
+version = "1.0.0b3.dev1"
 tag_format = "v$version"
+version_scheme = "pep440"
+legacy_tag_formats = ["v$major.$minor.$patch$prerelease$devrelease"]
```

Después de autorización, `uv lock` sin `--upgrade` debe producir un diff
revisable donde el bloque del paquete pase de `1.0.0b2` a `1.0.0b3.dev1`.
El resultado real de `uv lock` manda; no se edita el lock a mano. Este cambio
requiere revisión humana y bless porque modifica `pyproject.toml`.

### 6.2 Receta reproducible de compatibilidad, sin escritura

Ejecutar en un checkout aislado con el entorno quality ya sincronizado. No crea
tags, no modifica `pyproject.toml`, no invoca `cz bump` y no ejecuta campañas:

```bash
UV_NO_SYNC=1 uv run --all-groups cz version --project --tag

PYTHONDONTWRITEBYTECODE=1 UV_NO_SYNC=1 uv run --all-groups python - <<'PY'
from commitizen.defaults import DEFAULT_SETTINGS
from commitizen.git import GitTag
from commitizen.tags import TagRules
from packaging.version import Version

settings = DEFAULT_SETTINGS.copy()
settings.update({
    "tag_format": "v$version",
    "version_scheme": "pep440",
    "legacy_tag_formats": ["v$major.$minor.$patch$prerelease$devrelease"],
    "ignored_tag_formats": [],
    "changelog_merge_prerelease": False,
})
rules = TagRules.from_settings(settings)
expected = {
    "v1.0.0-beta.2": "1.0.0b2",
    "v1.0.0b3.dev1": "1.0.0b3.dev1",
}
for tag, version in expected.items():
    assert rules.is_version_tag(tag)
    assert str(rules.extract_version(GitTag(tag, "digest", "date"))) == version
assert str(Version("1.0.0b3.dev1")) == "1.0.0b3.dev1"
assert rules.normalize_tag("1.0.0b3.dev1") == "v1.0.0b3.dev1"
print("PEP440/Commitizen tag compatibility: PASS")
PY

PYTHONDONTWRITEBYTECODE=1 UV_NO_SYNC=1 uv run --all-groups python - <<'PY'
from fnmatch import fnmatchcase
assert fnmatchcase("v1.0.0b3.dev1", "v*")
print("adoption-smoke tag filter: PASS")
PY
```

La salida esperada del primer comando antes del bump es `v1.0.0b2`; eso
confirma el estado actual, no realiza una promoción. La receta Python fija, no
sólo permite, que el tag histórico extraiga `1.0.0b2` y que el candidato
extraiga `1.0.0b3.dev1` bajo la configuración propuesta.

## 7. Borradores de notas y migración

### Notas de release propuestas

> **WCT 1.0.0b3.dev1 — incremento experimental de evidencia de aceptación**
>
> Añade una base experimental para campañas de aceptación con baseline
> explícito, recibos ligados al IR y separación entre desacuerdo semántico y
> fallo instrumental. Conserva expedientes reproducibles de los lotes AC1 bajo
> sus límites publicados.
>
> Los runners cooperativos de aceptación deben consumir las variables
> `WCT_ACCEPT_*` y producir un recibo válido; un exit sin recibo no acredita
> aceptación.
>
> Esta entrega no afirma acreditación integral de AC1, cierre de beta.3,
> mutación completa, autonomía, sustitución de revisión humana, ahorro de
> costes ni mejora causal de modelos. “Experimental” no reduce las puertas de
> calidad, integridad, custodia, SBOM, smoke ni revisión humana.

### Migración propuesta

1. Quien provea un runner de aceptación debe implementar el recibo y las
   variables del protocolo descritas en
   `/home/jandradeu/Documents/well_code_template/build/tmp/beta3-ac1-r2-integration/docs/evolution/plans/BETA3/EXECUTION/CONTRATO-AC1.md`.
2. Los adoptadores siguen acoplándose por SHA y deben revisar con
   `wct adopt check`/`wct adopt sync`; la versión no sustituye el diff-review.
3. No se promete paquete PyPI, wheel, sdist, marketplace ni matriz multiversión
   en esta entrega sin una autorización y smokes propios.

## 8. Pendientes concretos antes de cualquier salida

- Decisión D1 sobre el alcance incremental y los claims permitidos.
- Checkout aislado limpio del SHA candidato; resolución pre-merge de todas las
  puertas técnicas del alcance, sin reciclar evidencia de otro SHA/lote.
- El trabajo técnico de r3 y GS que conduce al bless sigue siendo requisito
  propio: esta preparación documental no lo califica, reemplaza ni adelanta.
- Revisión humana del diff protegido, diff de versión/lock y bless final único.
- CI de PR verde después del bless; merge sólo entonces.
- Verificación post-merge del SHA real que se etiquetaría; cualquier bloqueo
  detiene la publicación y vuelve a un incremento revisable.
- Antes de D3: manifiesto no circular, copia durable aprobada y prueba de
  recuperación verificada desde ese destino, antes de limpiar evidencia
  `local-only`. Un asset de prerelease no satisface esta condición.
- D3 explícita sólo después de la recuperación anterior. Tras el tag autorizado,
  la atestación externa debe ligar tag/SHA final con los digests custodiados
  antes de publicar o adjuntar assets.
- SBOM, full hardening, smoke pre/post-tag y comprobación remota de
  prerelease/asset/tag→SHA sobre el candidato final.
- El reporte previo del fast gate (5 PASS, 2 FAIL en `G-LINT` y `G-FMT`) se
  conserva como evidencia atribuida al revisor, incluida su atribución al
  estado preexistente; no es una comprobación repetida aquí ni permite declarar
  verde al candidato. Por sí solo tampoco invalida este Markdown.
