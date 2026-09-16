# Reparación mínima de integración — G-DEPS y G-DEAD (2026-09-15)

Registro del incremento autorizado que repara los dos rojos preexistentes del
tier `commit` de la PR #53 y publica el candidato para la siguiente decisión
(GS-3). **No ejecuta bless, merge, bump, tag ni release; no reabre GS-2; no
ejecuta GS-3 ni campañas completas de mutación (§10.1); no acredita AC1 ni
beta.3.** La PR #53 permanece en borrador.

Antecedentes de solo lectura: `GS2-REVALIDACION-Y-PREPARACION-CIERRE-2026-09-15.md`,
`ANEXO-GDEPS-GDEAD-DIAGNOSTICO-2026-09-15.md`,
`ANEXO-PREPARACION-GS3-2026-09-15.md`,
`MATRIZ-DECISIONES-AC1-PENDIENTES-2026-09-13.md` y `ADR-D-02`
(`docs/evolution/plans/PR-D/decisions/ADR-D-02-f11b-vulture-60-whitelist.md`).

## 0. Corte e identidad

- Worktree de integración: `build/tmp/beta3-ac1-r2-integration`, rama
  `codex/beta3-ac1-r2-integration`, corte congelado
  `f122f792274805da7970498d05b9d420b6a2658b` (local == `origin` al congelar).
  PR #53: OPEN, borrador, `mergeStateStatus: BLOCKED`.
- Copia de trabajo aislada (todas las modificaciones y corridas de este
  incremento): `build/tmp/gdeps-gdead-r1.b4TNlw/checkout`, clon
  `git clone --no-hardlinks file://…` + `checkout --detach f122f79`, árbol
  limpio al iniciar. La publicación se hará después sobre la rama destino a
  partir del diff revisado, sin cambiar de rama en el worktree compartido.
- Trabajo ajeno preservado: `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md`
  permaneció untracked en el worktree de integración y fuera de este diff.
- Runtime de gates (sin sync/install): `build/tmp/beta3-ac1-r2-integration/.venv`
  — Python 3.13.14, uv 0.11.31, deptry 0.25.1, vulture 2.16, ruff 0.16.4,
  mypy 2.3.1, pytest 9.1.1.
- Autorización humana del encargo: extra `accept`, `uv lock` sin upgrades,
  seis entradas de whitelist (ADR-D-02), descomillado de los `cast` de
  `BinaryIO`, documentación/pruebas acotadas, verifier independiente y
  commit/push a la rama de la PR #53. Quedaron expresamente fuera: bless,
  merge, bump, tag, release, GS-3, campañas completas de mutación y cualquier
  relajación de umbrales.

## 1. Fallos reproducidos (Fase 1)

Comandos productivos exactos (builder en `tools/wct/gate/runner.py:376-392`),
cwd = raíz de la copia aislada, herramientas del venv de integración:

| Gate | argv | Antes | Salida |
|---|---|---|---|
| G-DEPS | `deptry src tools --known-first-party example --known-first-party tools` | **exit 1** | `tools/wct/accept/pytest_receipt.py:11:8: DEP004 'pytest' imported but declared as a dev dependency` |
| G-DEAD | `vulture src tools/wct governance/lint/vulture_whitelist.py --min-confidence 60` | **exit 3** | 7 hallazgos: 6 hooks en `pytest_receipt.py:28/37/42/46/82/103` + `BinaryIO` en `process.py:10` |

Mecanismos confirmados (no atribuidos por analogía):

- G-DEPS: `pytest` solo vive en `[dependency-groups] dev`; `pytest_receipt.py`
  se empaqueta (`[tool.hatch.build.targets.wheel] packages = ["tools", …]`) y
  se carga por reflexión (`PYTEST_PLUGINS` en `tools/wct/accept/campaign.py:29-33`;
  `-p tools.wct.accept.pytest_receipt` en `tests/unit/test_accept_pytest.py:303`).
  El importador es el módulo empaquetado, no una herramienta de desarrollo.
- G-DEAD hooks: pluggy/pytest invoca los hooks por nombre; vulture solo exime
  `pytest_*` cuando el archivo matchea sus patrones de test
  (`vulture/core.py` → `_is_test_file` / `_ignore_method` / `_ignore_function`)
  y `tools/wct/accept/pytest_receipt.py` no matchea.
- G-DEAD `BinaryIO`: vulture no evalúa literales string; las dos ocurrencias
  reales estaban en `cast("BinaryIO", …)` (`process.py:38-39`).

Los fallos coinciden byte a byte con `ANEXO-GDEPS-GDEAD-DIAGNOSTICO-2026-09-15.md`;
no apareció ningún fallo nuevo atribuible a otra causa.

## 2. Decisiones y diff (Fases 2 y 3)

### 2.1 G-DEPS — extra opcional `accept`

Inspección previa a la decisión: ningún camino base importa
`tools.wct.accept.pytest_receipt` (solo `campaign.py` por string y los tests);
`tools.wct.cli` y `tools.wct.accept.pipeline` no importan `pytest`; la
operación de aceptación por defecto sí ejecuta pytest (`cli.py` usa
`sys.executable -m pytest`). Conclusión: la aceptación es **opcional**, y el
extra es la metadata mínima correcta.

```diff
 [project.scripts]
 wct = "tools.wct.cli:main"

+[project.optional-dependencies]
+accept = ["pytest>=8.3"]
+
 [dependency-groups]
```

`pytest>=8.3` permanece en el grupo `dev`; no se sustituyó ninguna sección ni
se eliminaron extras.

`uv lock --offline` (sin `--upgrade`, uv 0.11.31): exit 0, 165 paquetes
resueltos. Diff del lock (10 inserciones, 1 borrado), solo en la entrada de
`write-check-trust`: `[package.optional-dependencies] accept = [pytest]`,
`requires-dist` gana `pytest; extra == 'accept'` y `provides-extras = ["accept"]`.
**Cero cambios de versión o resolución ajenos**; `uv lock --check` → exit 0.

### 2.2 G-DEAD — seis entradas de whitelist (ADR-D-02)

Entradas canónicas de `vulture --make-whitelist` añadidas a
`governance/lint/vulture_whitelist.py`, con la justificación en el docstring y
`# noqa: B018, F821` por entrada (mismo formato que la entrada existente):

```
_.pytest_collection_finish
_.pytest_collectreport
_.pytest_internalerror
_.pytest_runtest_makereport
_.pytest_sessionfinish
pytest_configure
```

Sin patrones amplios, sin excluir módulos, sin bajar la confianza. La
justificación no es «queda fuera del escaneo de G-SUPPRESS» (esa es una
consecuencia): es el falso positivo demostrado con `--make-whitelist` y la
autorización humana, conforme a ADR-D-02.

### 2.3 G-DEAD — `BinaryIO` sin comillas

```diff
-        selector.register(cast("BinaryIO", process.stdout), selectors.EVENT_READ, "stdout")
-        selector.register(cast("BinaryIO", process.stderr), selectors.EVENT_READ, "stderr")
+        selector.register(cast(BinaryIO, process.stdout), selectors.EVENT_READ, "stdout")
+        selector.register(cast(BinaryIO, process.stderr), selectors.EVENT_READ, "stderr")
```

Sin cambios de control de flujo, imports, timeouts, señales ni buffers:
exactamente dos líneas.

### 2.4 Pruebas permanentes

No se añadieron archivos de test nuevos: no existe un archivo de pruebas de
empaquetado en el repo y la declaración del extra ya tiene guard productivo
en G-DEPS (si `pytest` desapareciera de metadata, G-DEPS vuelve a exit 1). La
verificación de empaquetado se ejecutó en entornos desechables (§3) y las
regresiones de transporte existentes se reejecutaron (§5). Si se quisiera un
test permanente de metadata, la ruta propuesta (no creada) sería un unit test
junto a `tests/unit/test_coverage_scope.py`/`test_mutation_selection.py`, que
ya leen `pyproject.toml`.

## 3. Empaquetado e instrucciones

Artefacto: `uv build --wheel --offline` desde el candidato congelado →
`write_check_trust-1.0.0b2-py3-none-any.whl` con sha256
`fbb5ea93c7c231bf1cbd49fa5102e17de813dd1b79e13673021a3d57ba69e0ca`
(custodia local en el expediente). El build es reproducible: la construcción
independiente del verifier produjo el mismo hash bit a bit. Un primer wheel
(`f8146f5e…`) se construyó antes del descomillado de `process.py` y de la
nota del README; quedó superado y no es el artefacto de referencia (reserva
M-1 del dictamen, resuelta). METADATA del wheel final:

```
Provides-Extra: accept
Requires-Dist: pytest>=8.3; extra == 'accept'
```

| Control | Entorno | Resultado |
|---|---|---|
| Metadata declara el extra | wheel METADATA | `Provides-Extra: accept` + `Requires-Dist … extra == 'accept'` |
| Instalación base | `venv-base` (uv venv + wheel; solo pyyaml) | `import tools.wct.cli` OK; `wct --version` → `wct 1.0.0b2`; `import pytest` → `ModuleNotFoundError`; `import tools.wct.accept.pytest_receipt` → `ModuleNotFoundError` (opcional, no se carga sin el extra); operación ajena a aceptación `wct archmetrics --json` → exit 0 |
| Instalación con `[accept]` | `venv-accept` (`write-check-trust[accept] @ file://…whl`) | pytest 9.1.1 disponible; `import tools.wct.accept.pytest_receipt` desde `site-packages` OK |
| Smoke productivo del plugin | `venv-accept` + pytest real con `WCT_ACCEPT_*` | receipt escrito (`cases: pass`), `receipt.events.json` presente, exit 0 |
| Smoke de campaña productiva (aceptación mutante; desviación de alcance, §10.1) | `venv-accept`, `wct accept mutate features/example.feature` desde directorio sin `tools/` | baseline `pass` (exit 0), **6/6 mutaciones killed**, veredicto exit 0 — el plugin se cargó por `PYTEST_PLUGINS` desde el wheel instalado |

Versión medida: **pytest 9.1.1** (coincide con el runtime). No se afirma
compatibilidad con todo `pytest>=8.3`: solo se probó 9.1.1.

Los cinco controles de la tabla se reejecutaron sobre el wheel final en
entornos desechables frescos (`venv-base-final` y `venv-accept-final`),
además de las corridas previas: mismo resultado. La primera sonda de import
del plugin (`evidence/pkg-accept-check.txt`) se ejecutó con `cwd` en el
checkout principal `/home/jandradeu/Documents/well_code_template` (rama
`codex/plan-beta3-moldes-evals`), cuyo `tools/wct/accept/` solo contiene
`__init__.py` y `pipeline.py` — sin `pytest_receipt.py` — y por eso falló con
`ModuleNotFoundError: No module named 'tools.wct.accept.pytest_receipt'`
(atribución reproducida de forma determinista en
`evidence/pkg-import-contamination-repro.txt`). Fue contaminación de `cwd`,
no del paquete; quedó sustituida por la sonda con `cwd` limpio
(`pkg-imports-clean.txt`, import OK desde `site-packages`). Se registra como
corrida superada (reserva M-2).

Documento de instalación/aceptación elegido tras inspección: **`README.md`**
(sección «Elige la verificación adecuada», donde ya se documenta la aceptación
mutada). Se añadió una nota: la campaña de aceptación ejecuta pytest y la
instalación del paquete sin los grupos de desarrollo debe pedir el extra
`write-check-trust[accept]`; el resto del arnés no requiere pytest
(afirmación corregida después de publicar: §10.2).

## 4. Excepciones justificadas (G-DEAD)

| Símbolo | Mecanismo de invocación | Evidencia que lo ejerce | Motivo por el que vulture no lo reconoce |
|---|---|---|---|
| `_Recorder.pytest_collection_finish` | hook pluggy: `Session` lo llama al terminar la colección | `test_active_configuration_dispatches_receipt_with_exact_catalog` (dispatch pluggy real) y campaña productiva (§3) | `_ignore_method` solo exime `pytest_*` en archivos con patrón de test; el módulo no matchea |
| `_Recorder.pytest_collectreport` | hook pluggy: un `CollectReport` por colector durante la colección | `test_hook_receipt_preserves_protocol_faults[collection]` y colección real de la campaña | ídem |
| `_Recorder.pytest_internalerror` | hook pluggy: error interno del runner | `test_hook_receipt_preserves_protocol_faults[internal]` | ídem |
| `_Recorder.pytest_runtest_makereport` | hook wrapper pluggy: setup/call/teardown de cada test | `test_active_configuration_dispatches_receipt_with_exact_catalog` y campaña productiva | ídem |
| `_Recorder.pytest_sessionfinish` | hook wrapper pluggy: cierre de sesión | `test_active_configuration_dispatches_receipt_with_exact_catalog`; receipt escrito en la campaña | ídem |
| `pytest_configure` | hook de módulo: pytest lo llama al cargar el plugin (`PYTEST_PLUGINS`/`-p`) | `test_pytest_plugin_is_inactive_without_protocol` (subproceso pytest real con `-p`) y tests de configuración activa | `_ignore_function` solo exime `pytest_*` en archivos con patrón de test; el módulo no matchea |

`BinaryIO` no se whitelisteó: se corrigió el literal en los dos `cast`.

## 5. Impacto sobre evidencia anterior (Fase 4)

`tools/wct/accept/process.py` cambió de bytes:

- Antes: `bdbb564604f2e893ed870e435db4f26751a4a725c1d4c5e5a70f4c4b3dc396d1`.
- Después: `84b9340fd16b424a2d778e512166c4419c048001588665a313dcdf9f5d263ef7`.
- Diff: exactamente las dos líneas de `cast` (§2.3).

Por qué no cambia el valor retornado: `typing.cast` es identidad en runtime
(devuelve `val` sin evaluarlo); la diferencia entre pasar el literal `"BinaryIO"`
y el objeto `BinaryIO` es solo de resolución estática, sin efecto en el `fileobj`
registrado en el selector ni en los bytes leídos.

Regresiones de transporte ejecutadas (copia aislada, path productivo):

- `tests/unit/test_accept_campaign.py tests/unit/test_accept_pytest.py
  tests/unit/test_accept_pipeline.py tests/unit/test_accept_receipt.py
  tests/unit/test_accept_verdict.py -m "not property"` → **213 passed**.
  Incluye el T5 vigente (`test_transport_reads_pending_output_after_leader_terminates`,
  doble de Popen + selector real), timeout con streams parciales y reaping,
  límite exacto y exceso de un byte, EOF, limpieza y `_terminate` idempotente.
- Smoke de campaña productiva (§3): baseline + 6 mutantes por el transporte
  real — aceptación mutante, desviación de alcance (§10.1).

Evidencia histórica que sigue siendo referencia y **no** se reejecutó: series
GS-1/GS-2 (incluida la revalidación de atribución y sus 35 sucesores), lote
r3 de `process.x__*`, actas de ratificación y los dictámenes de T5. Ninguno se
traslada automáticamente al nuevo hash de `process.py`: el T5 aceptado en
`fa3558d` es referencia de diseño, y la evidencia vigente de no-regresión es
la corrida de esta sección. No se regeneró la campaña r3 ni se ejecutó mutación
nueva fuera del smoke de aceptación de §3 (§10.1).

## 6. Resultados reales por control

Todos los comandos sobre la copia aislada, con `PATH` al `bin` del venv de
integración (equivalente al entorno de `uv run`); los artefactos crudos viven
en el expediente local `build/tmp/gdeps-gdead-r1.b4TNlw/evidence/`.

| Control | Resultado |
|---|---|
| `git diff --check` | exit 0 |
| `wct gate --tier fast` | **7/7 PASS** |
| `pytest --collect-only -q` | 661 tests colectados, exit 0 |
| Suite normativa `pytest -q tests/unit tests/integration -m "not property"` | **659 passed, 0 skipped**, exit 0 |
| Property `pytest -q tests/property` | 1 passed, exit 0 |
| Cobertura CI `pytest --cov --cov-branch --cov-report=lcov:build/coverage/lcov.info -q -m "not property"` | 660 passed, 1 deselected, exit 0 |
| `wct ratchet check --require coverage-total,docstring-coverage` | medidas 2 de 2, exit 0 |
| G-DEPS productivo | antes exit 1 (DEP004) → **después exit 0** |
| G-DEAD productivo | antes exit 3 (7 hallazgos) → **después exit 0** |
| Ruff + mypy focales sobre lo cambiado | `ruff check` ok, `ruff format --check` ok, `mypy tools/wct src` → `Success: no issues found in 87 source files` |
| Tier `commit` | **20 PASS · 0 SKIP · 1 FAIL** (G-META-1) |
| Focal transporte (`test_accept_*`) | 213 passed |
| Empaquetado base / con extra | §3, ambos OK |
| No ejecutado (fuera de autorización) | bless, merge, bump, tag, release, GS-3, mutación de fuentes completa, aceptación mutada como gate; el smoke `wct accept mutate` de §3 sí se ejecutó como desviación de alcance (§10.1) |

Nota de entorno verificada: la suite normativa exige el `bin` del venv en
`PATH` (el test `test_capabilities_presence_with_real_which` usa `which` real);
con el `PATH` productivo da 659 passed y 0 skipped. La corrida inicial sin ese
`PATH` (627 passed/4 failed/28 skipped) fue un defecto del entorno de la
copia, no del candidato; queda registrado aquí y no se usa como evidencia.

El único rojo del tier `commit` es **G-META-1** (drift de rutas protegidas,
§7). G-DEPS y G-DEAD quedaron verdes, y el resto de la batería preexistente
no cambió.

## 7. Estado del drift de integridad

- En el corte `f122f79`: 20 rutas protegidas en drift (4 `modificado` +
  16 `nuevo protegido`).
- En el candidato de este incremento: **23 rutas** (7 `modificado` + 16
  `nuevo protegido`). El incremento suma 3 rutas `modificado`:
  `pyproject.toml`, `uv.lock` y `governance/lint/vulture_whitelist.py`.
  `tools/wct/accept/process.py` cambió de bytes pero ya pertenecía a la clase
  `nuevo protegido`.
- La fórmula «20 rutas» del registro de GS-1 queda **superada** por esta
  medición: la frontera protegida real del candidato es 23 rutas.
- G-META-1 requiere revisión humana y bless (SEC-005 / E9); **no se ejecutó
  bless**. El drift no invalida la reparación, pero la PR #53 sigue con
  `commit-gates: FAILURE` hasta esa decisión, que no forma parte de este
  encargo.

## 8. Dictamen independiente (Fase 5)

**Verifier independiente** (PROC-005, agente distinto sin permiso de escritura;
no escribió el cambio ni el registro). Revisó el manifiesto congelado (7/7
sha256 verificados dos veces), y distinguió revisión documental de reejecución
propia. **Dictamen: APROBAR CON RESERVAS (M-1 y M-2 documentales, M-3 de
cobertura); ningún hallazgo bloqueante.**

- **Reejecución propia**: G-DEPS exit 0; G-DEAD exit 0; `ruff check` y
  `ruff format --check` 0 findings (444 archivos); `mypy tools/wct src` exit 0
  (87 archivos); `uv lock --check` exit 0; `vulture --make-whitelist` con
  exactamente las 6 entradas canónicas; focales de transporte 213/213
  (T5, timeout/reaping, límite, EOF, `_terminate`); integridad 23 (candidato)
  y 20 (worktree) sin bless; tier `fast` 7/7.
- **Empaquetado reproducido en entornos propios**: wheel final
  `fbb5ea93…` (idéntico bit a bit al construido aquí), METADATA con
  `Provides-Extra: accept`; base sin pytest con CLI y operaciones no-aceptación
  verdes; con `[accept]` (pytest 9.1.1) plugin importable; campaña real
  6 planned / 6 killed / 0 survived / 0 errors / 0 not_run.
- **Reservas**: **M-1** el wheel citado en el borrador inicial (`f8146f5e…`)
  precedía al descomillado y a la nota del README — resuelta reconstruyendo el
  wheel final y reejecutando los smokes (queda registrado en §3); **M-2** una
  sonda de import temprana falló por contaminación de `cwd` y no estaba
  anotada — documentada en §3 y superada por la sonda con `cwd` limpio;
  **M-3** el verifier no reejecutó los números del tier `commit` ni la suite
  normativa/cobertura/ratchet de §6 (fuera de su mandato): se declaran como
  corridas del coder, no del verifier.
- **Frontera de lo no verificado por el verifier**: no ejecutó mutación de
  fuentes (`wct mutate`) ni aceptación mutada como gate, tier `full`, bless,
  merge, bump ni release; sí reprodujo el smoke `wct accept mutate` del
  empaquetado (§10.1). Tampoco reejecutó GS-2 ni sus sondas, ni consultó
  checks remotos de CI en ese momento (resultado real de CI: §10.3).

La publicación en la rama destino se hará con este dictamen y el manifiesto
congelado; al cierre de este registro la rama y la PR #53 siguen en `f122f79`
sin commit del incremento (publicación posterior: §10.3).

## 9. GS-2 y pendientes para GS-3 / cierre AC1

GS-2 se conserva en su alcance de evidencia sucesiva: **atribución pendiente
resuelta y regresiones sustentadas mediante evidencia sucesiva; no se ejecutó
una nueva campaña conjunta ni se acredita AC1**. Este incremento no reabre
GS-2, no reejecuta sus sondas y no modifica sus expedientes.

Pendientes que este incremento deja anotados (sin ejecutarlos):

1. **GS-3**: la fila E5 de la matriz queda anotada. `tools/wct/gate/semgrep.py`
   conserva su hash del anexo (`0126c4e1…`); `pyproject.toml` y `uv.lock`
   cambian de hash respecto a la tabla de congelación del anexo GS-3, de modo
   que al autorizar GS-3 hay que re-verificar esa tabla contra el nuevo
   candidato y actualizar los dos hashes (la condición de BLOQUEO del anexo
   es que cambie `semgrep.py`; no ocurre).
2. **G-META-1/E9**: revisión humana del drift (23 rutas) y bless; sigue siendo
   el único rojo del tier `commit`.
3. **AC1**: decisiones E1/E2 (destino de los 928), D-A/D-C/D-D, E6/E7 y E8
   siguen pendientes según la matriz; nada de este incremento las resuelve.
4. **Publicación**: CI de la PR #53 se consulta tras el push; no se anticipa
   verde mientras G-META-1 carezca de bless humano (consultada: §10.3).

## 10. Corrección documental (post-publicación)

Publicado el incremento en `b4403c5ef7273c3c929b975ebdf866381db0b88e`, la
revisión humana detectó dos imprecisiones documentales. Esta sección las
corrige sin borrar la historia: los textos anteriores siguen visibles y se
leen con la referencia a esta sección.

### 10.1 Sí hubo mutación de aceptación (desviación de alcance)

Las frases «no ejecuta … campañas de mutación» (§0) y «no se ejecutó
mutación nueva» (§5) no describen bien una corrida real: **sí se ejecutó
`wct accept mutate features/example.feature` como smoke de empaquetado**
(§3, «Smoke de campaña productiva»): baseline `pass` y **6/6 mutaciones
killed**, veredicto exit 0, con el plugin cargado desde el wheel instalado.
Esa corrida **es mutación de aceptación** y no debe describirse como «sin
mutación».

El encargo pedía un smoke de empaquetado productivo, pero prohibía
expresamente la aceptación mutante. Se registra como **desviación de
alcance**, no como autorización implícita: no amplía el alcance autorizado
ni habilita a repetirla.

Hechos que no cambian:

- No se repitieron las campañas completas GS-1/GS-2 ni la campaña r3, no se
  reejecutaron sus sondas y sus expedientes sellados no se modificaron.
- No se ejecutó GS-3, ni mutación de fuentes (`wct mutate`), ni la
  aceptación mutada como gate: G-ACCEPT-MUT no se exigió.
- El smoke no acredita por sí solo G-ACCEPT-MUT, AC1 ni beta.3: es una
  corrida de empaquetado, no una calificación.

Atribución de las corridas de aceptación mutante, según los registros:

| Corrida | Actor | Registro |
|---|---|---|
| `wct accept mutate` sobre el wheel (`venv-accept`) | coder | §3 y expediente `build/tmp/gdeps-gdead-r1.b4TNlw/evidence/` |
| Reproducción del smoke (6 planned / 6 killed / 0 survived / 0 errors / 0 not_run) sobre el wheel final | verifier | §8, «Empaquetado reproducido en entornos propios» |

Ninguna de las dos es el gate G-ACCEPT-MUT ni una campaña de calificación.

### 10.2 README: alcance de la instalación base

La nota añadida al README (§3) afirmaba que «el resto del arnés no requiere
pytest; sin el extra solo queda fuera de alcance la aceptación». Esa
afirmación es demasiado amplia: el registro productivo también usa pytest
para G-TEST, la cobertura, los property tests y el orden aleatorio. El
párrafo se sustituyó por el texto vigente, que limita la instalación base al
CLI y a las operaciones sin herramientas adicionales, y conserva el comando
copiable `pip install 'write-check-trust[accept]'`.

### 10.3 Publicación y CI real

- Publicación: commit `b4403c5ef7273c3c929b975ebdf866381db0b88e`, push
  normal `f122f79..b4403c5` a `codex/beta3-ac1-r2-integration`; PR #53
  sigue OPEN y en borrador. Las frases de §0 y §8 que describían la
  publicación como futura y la rama en `f122f79` quedan supersedidas por
  este commit.
- CI consultada tras el push (run `35006521104`, job `commit-gates`):
  **FAILURE a los 11 s, detenido en `wct integrity check`** con las 23
  rutas protegidas en drift (G-META-1 sin bless). Los pasos posteriores
  —tier `commit`, tests, cobertura, ratchet y aceptación— **no se
  ejecutaron**; no hay resultado de CI para ellos. La limitación se
  conserva: la PR #53 sigue con `commit-gates: FAILURE` hasta el bless.
