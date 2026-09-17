# Equivalencias sucesoras GS-3 y revisión protegida E9 — expediente para decisión humana (2026-09-17)

Registro documental del encargo «cierre documental de las equivalencias
sucesoras de GS-3 y de la revisión protegida E9 de la PR #53». Este documento
**no ratifica equivalencias, no aprueba el drift, no autoriza bless** y no
cambia producto, tests, features, gobernanza, configuración ni dependencias.
Sirve las cuatro decisiones humanas: ratificación por ID (§2), disposición de
la desviación de secuencia (§3), aprobación E9 por rutas (§4) y autorización
posterior de bless sobre un candidato exacto (§5). Resultado global:
**EXPEDIENTE CON PENDIENTES** (§8).

## 0. Identidades, preflight y congelamiento

| Elemento | Valor verificado |
|---|---|
| HEAD auditado = documental publicado = PR head | `2246148e351ffbff504418bf132a4be693ca9d46` (worktree `build/tmp/beta3-ac1-r2-integration`, rama `codex/beta3-ac1-r2-integration`, = `origin`, = `headRefOid` PR #53 vía `gh`; OPEN, borrador, MERGEABLE — que no es aprobación) |
| Candidato técnico medido | `421725367e3df6fae1b20af7f7ed910b2a4d50a7` (= d1896210 + 1 commit `fix(sast)`) |
| Base de la PR | `932c835ac0eeb75010ec7a1071315b1c51f78eb6` (merge-base confirmado) |
| Manifiesto protegido vigente | `governance/integrity.lock` @ base `46669278ece7e3b7cc8059a5eff9ae27c2735284`, 201 entradas |
| Fuente afectada | `tools/wct/gate/semgrep.py` — sha256 `33ff050950551e17ef04142b56a39f3fa5d76c6be8be0f3f1a71c8dc66c731d4` (blob `15ed6dff…`), **idéntica** en 4217253 y 2246148 |
| Árbol instrumentado | `camp/mutants/tools/wct/gate/semgrep.py` sha256 `23520ea69938ff40e9fb7e27119b7c09cd6a8ece7474b1a6c181fe8fbc53be94`; `semgrep.py.meta` sha256 `884740d91c13187c3b7fca009529caee689fb36536b3c40a1b6934a77a8124dc` |
| Expediente de reparación | `build/tmp/repara-sast-targets-20260916/` — `camp/` @ 4217253 (pyproject experimental `only_mutate`, `ids-campana.txt`, `resultados-campana.txt`, `instrumento.py`; sin `activacion.log` preservado: el intento de plugin fue descartado, la activación se acreditó vía canario en proceso) y `candidate/` @ 2246148 |
| Copia congelada de esta auditoría | `build/tmp/cierre-doc-equivalencias-e9-20260917/audit/` — clon con raíz Git propia, HEAD 2246148, árbol limpio; toda derivación pesada de este registro se ejecutó allí |
| Runtime de verificación | host `jandradeu`, Python 3.14.7; tooling WCT vía `.venv` del worktree (Python 3.13) |
| Índice del worktree | al iniciar: limpio, único sin seguimiento `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md` (ajeno, preservado). Al publicar este registro: staging exclusivo de este documento y de las filas E5/E8/E9 de la matriz (verificación previa al commit); ninguna ruta protegida involucrada |
| CI real (2246148) | run `35186904916` **FAILURE** en «Verify generated policy and control-plane integrity» (`wct integrity check`, drift 37) — rojo preexistente identificado, causa conocida G-META-1 pre-bless; fuera del alcance de este encargo, no se elude |

HEAD no avanzó respecto de los cortes comunicados: el delta entre candidato
técnico y cabeza documental es exactamente el commit `docs(sast)` 2246148,
que solo tocó `REPARACION-SAST-SEMGREP-TARGETS-2026-09-17.md` y filas E8/E9
de la matriz. Ninguna ruta protegida cambió después de 4217253 → la evidencia
medida sobre 4217253 conserva vigencia por identidad sobre 2246148.

## 1. Frente A — cinco equivalencias sucesoras (decisión humana D-A')

Derivación desde el bruto, no desde sufijos. Campaña del expediente: primera
pasada focal 63 killed + 11 survived (`resultados-campana.txt`, preservado);
re-test de los 11 bajo el fichero completo (59 tests) mata 6 — mutmut_24
(`cwd=None`), 26 (`capture_output=None`), 29 (`cwd` omitido), 31
(`capture_output` omitido), 34 (`capture_output=False`), 35 (`check=True`) —
y deja el **bruto final 74 ejecutados = 69 killed + 5 survived** (0 timeout,
0 suspicious, 0 errores instrumentales). El bruto se conserva; **no** se
presenta «74 killed», PASS de G-MUT ni equivalencias ya ratificadas.

Los cinco supervivientes son kwargs de la única llamada
`subprocess.run(argv, cwd=root, text=True, capture_output=True, check=False)`
de `x_gate_sast_semgrep`. Correspondencia histórica **por diff exacto**, no
por número: la fuente cambió (`0126c4e1…` → `33ff0509…`) y la renumeración
desplazó los IDs (el mutmut_26 y 31 nuevos son mutaciones de
`capture_output`, no de `check`).

| # | ID completo (4217253) | Diff exacto | Histórico ratificado | Acta histórica |
|---|---|---|---|---|
| S1 | `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_25` | `text=True` → `text=None` | `…__mutmut_24` (`text→None`) | `GS3-DOMINIO-BYTES-STRING…` §4; ratificación D1 en `ACTA-CIERRE-ACOTADO-GS3…` §1 |
| S2 | `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_30` | `text=True` omitido | `…__mutmut_29` (`text` omitido) | ídem |
| S3 | `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_33` | `text=True` → `text=False` | `…__mutmut_33` (`text=False`) | ídem |
| S4 | `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_27` | `check=False` → `check=None` | `…__mutmut_26` (`check=None`) | `GS3-CONTRATOS-REGRESIONES-Y-EQUIVALENCIAS…` §3; referencia en `ACTA-CIERRE…` §2 |
| S5 | `tools.wct.gate.semgrep.x_gate_sast_semgrep__mutmut_32` | `check=False` omitido | `…__mutmut_31` (`check` omitido) | ídem (y `x__topology__mutmut_6/11` para la misma familia) |

### S1–S3 (familia `text`, dominio bytes/string)

- **Fundamento**: dentro del dominio D — salida JSON UTF-8 **sin BOM** del
  productor fijado, capturada por un consumidor cuya decodificación efectiva
  resuelve a UTF-8 —, la ruta `bytes` (`json.loads` con `detect_encoding`)
  aplica exactamente la misma decodificación UTF-8 que `text=True`; mismo
  árbol, mismos diagnósticos; el JSON malformo produce el mismo
  `JSONDecodeError` → «salida ilegible»; el UTF-8 inválido produce la misma
  `UnicodeDecodeError` en ambos caminos. La mutación no altera ningún otro
  campo de `GateResult`. Fundamento estructural + evidencia empírica del
  expediente GS-3 (serializador del productor y observación).
- **Cambio de premisa que obligó a esta revisión**: la fuente (`33ff0509…` en
  lugar de `0126c4e1…`) **y** el comando (argv con targets explícitos de E en
  lugar de `COMMAND` solo). La propiedad dominante es independiente del argv
  (el serializador JSON del productor no emite BOM); las precondiciones fueron
  re-verificadas al nuevo SHA por el registro de reparación §5–§6: stdout
  inicia `{"vers…` sin BOM, decodificación UTF-8 estricta sin error,
  `json.loads(str) == json.loads(bytes)` en el dominio.
- **Precondiciones (las cinco de D1, re-ancladas al nuevo COMMAND)**:
  (1) Semgrep 1.174.0 y productor identificado; (2) COMMAND del gate — ahora
  `semgrep --quiet --error --severity ERROR --config governance/semgrep
  --json` **+ targets explícitos de E en el orden determinista de
  `required_sources`**; (3) stdout directo del productor, sin wrapper ni
  proxy en PATH que altere los bytes; (4) salida JSON UTF-8 sin BOM;
  (5) decodificación efectiva UTF-8 del consumidor (sin `PYTHONUTF8=0` ni
  locale no UTF-8).
- **Contraejemplos fuera del dominio** (conservados): BOM UTF-8 (original
  «salida ilegible» vs mutante PASS) y BOM UTF-16 (original
  `UnicodeDecodeError` vs mutante PASS), alcanzables solo con un productor
  ajeno al binario fijado; locale no UTF-8 (latin-1: mojibake medido).
- **Invalidantes**: cambio de versión o serializador del productor, emisión
  de BOM, wrapper en PATH, `PYTHONUTF8=0`/locale no UTF-8, cambio del
  consumo de stdout. Una observación empírica no agota el espacio de
  salidas: corrobora, no demuestra.
- **Estado**: **PROPUESTA CONFIRMADA** (evidencia y precondiciones
  verificadas sobre `33ff0509…`); ratificación PENDIENTE de decisión humana.

### S4–S5 (familia `check` falsy)

- **Fundamento**: semántica de runtime de `subprocess.run` en CPython —
  `check=None` y `check` omitido son equivalentes a `check=False` (la rama
  `if check and retcode` no se toma) — independiente del argv y del comando.
  El cambio de fuente no toca esa semántica; la única llamada del gate sigue
  siendo la instrumentada.
- **Precondiciones**: runtime CPython 3.13.x (venv del worktree); la semilla
  de fuente cambió y la revisión se ejecutó (re-derivación del diff y de la
  única llamada); **no** se extiende a `check=True` ni a otras mutaciones por
  semejanza (el `check=True` nuevo, mutmut_35, murió en el re-test y no es
  objeto de equivalencia).
- **Contraejemplos/límites**: con `check=True` el comportamiento difiere
  (excepción ante retcode ≠ 0) — fuera de lo propuesto; la equivalencia
  histórica no cubre otros call-sites.
- **Estado**: **PROPUESTA CONFIRMADA**; ratificación PENDIENTE.

`x__topology`/`x__policy` (34 sitios): fuente byte-idéntica a GS-3;
veredictos históricos conservados sin re-ejecución (el canario del expediente
re-validó la activación del mecanismo en proceso). Nada de lo anterior
convierte los 5 `survived` en `killed`: el bruto 69+5 es inmutable.

## 2. Frente B — desviación de secuencia (decisión humana D-B')

- **Instrucción aplicable**: el encargo de la reparación SAST exigía
  detenerse ante supervivientes sin disposición (regla de cadena que el
  propio registro §9 reconoce como próxima puerta: «decisión humana sobre las
  5 propuestas … y, con ella, la revisión humana protegida del drift (E9) →
  bless → POST-BLESS. Nada de eso se ejecuta ni se autoriza aquí»).
  Precedentes de parada en la misma rama: `e88d66e` (parada del DRY
  anticipado), `35ce654` (parada en la cláusula de rama), `192c869` (puerta
  no satisfecha → Q-ACCMUT no ejecutado), y `CIERRE-CLEANUP…` §5 («con
  supervivientes o errores sin disposición, detén la cadena» → full no
  ejecutado). Norma de fondo: PROC-004 y TEST-002 de AGENTS.md.
- **Punto donde correspondía detenerse**: al cierre de la campaña de
  mutación del cambio (bruto 69+5, cinco supervivientes sin disposición),
  ~00:15 del 2026-09-17.
- **Acciones que continuaron** (todas posteriores a conocer los 5
  supervivientes): G-ACCEPT (PASS, tras colisión placeholder-variant
  resuelta), cobertura fresca (colección 696; suite canónica 695 passed;
  total 88,09 %; G-COV-DIFF PASS; cláusula de rama 314/348 = 90,23 %), CRAP
  (`gate_sast_semgrep` CC 3 / CRAP 3,0), DRY (estructural 0; plantillas 17 =
  baseline; jscpd 0) y **full PRE-BLESS 34 gates = 33 PASS + 1 FAIL
  (G-META-1)**. Q-ACCMUT: NO ejecutado (declarado no aplica por auditoría de
  alcance — anclajes sin cambio).
- **Evidencia y tiempos** (mtimes del expediente + commits): 00:05:52 commit
  4217253 · 00:06:50 `logs-integrity.txt` (drift 37) · 00:08:29 copia `camp/`
  e `instrumento.py` · 00:11:42 `ids-campana.txt` · 00:12:05
  `resultados-campana.txt` (pasada focal) · re-test de los 11 (~169 s) ·
  cadena posterior hasta 00:39:57 (`candidate/`, full 361 s) · 00:43 commit
  documental 2246148.
- **Validez técnica ≠ cumplimiento**: las mediciones posteriores son
  técnicamente válidas **por identidad** (ejecutadas sobre 4217253/2246148;
  ninguna fuente protegida cambió después; números re-derivables), pero su
  admisión como cadena de calificación conforme PROC-004 requiere aceptación
  humana expresa de la desviación. Nada se borra, la secuencia no se presenta
  como conforme, ningún resultado se invalida automáticamente y **no** se
  concede excepción retroactiva.
- **Propuesta de conservación**: si el humano acepta la desviación y ratifica
  los cinco IDs, cobertura/CRAP/DRY/G-ACCEPT/full se conservan como evidencia
  del árbol 2246148 (sus valores no dependen de los kwargs `text`/`check`);
  si **rechaza** alguna propuesta, la puerta TEST-002 reabre: reparación
  (regresión) → nueva campaña → **repetir** cobertura, CRAP, DRY y full sobre
  el árbol reparado. La aceptación de esta desviación es puntual: no es
  permiso general para futuras rondas.

## 3. Frente C — auditoría E9 del drift (decisión humana D-E9')

Recalculo con el mecanismo vigente, ejecutado y documentado: en la copia
congelada, `python -m tools.wct integrity check` → **exit 1, 37 = 7
modificadas + 30 nuevas**, lista **byte-idéntica** a `logs-integrity.txt` del
expediente (diff ordenado: sin diferencias). Se distinguen: diff de la PR
frente a base 932c835 (toda la rama), drift frente al manifiesto protegido
(base 4666927) y cambios posteriores al candidato técnico medido (ninguno en
rutas protegidas: 2246148 es solo documental).

Tabla por ruta (hash aprobado = entrada en lock@4666927; «—» = nueva sin
entrada; intro/último = commits que tocaron la ruta desde la base del lock):

| Ruta | Clase | Aprobado | Actual | Intro→último | Finalidad · Autorización (fuente) · Evidencia · Vigencia | Dictamen |
|---|---|---|---|---|---|---|
| `tools/wct/accept/campaign.py` | N | — | `686070cd…` | 88de60e | Motor de aceptación AC1. `CONTRATO-AC1.md` (transcripción «si autorizo»/«vale continua»; frontera de archivos literal). Suite 639 passed; FAIL-survivors-stop 30 declarado. Sin cambios posteriores → vigente por identidad | CONFORME |
| `tools/wct/accept/generation.py` | N | — | `14249343…` | 88de60e | ídem | CONFORME |
| `tools/wct/accept/ir_checks.py` | N | — | `d40dd194…` | 88de60e | ídem | CONFORME |
| `tools/wct/accept/mutation_cases.py` | N | — | `a4528b8e…` | 88de60e | ídem | CONFORME |
| `tools/wct/accept/parsing.py` | N | — | `672c41f5…` | 88de60e | ídem | CONFORME |
| `tools/wct/accept/pytest_receipt.py` | N | — | `d4f136ae…` | 88de60e | ídem | CONFORME |
| `tools/wct/accept/receipt.py` | N | — | `52e929658…` | 88de60e | ídem (ruta extra autorizada por medición 105 sitios, «Arquitectura autoriza») | CONFORME |
| `tools/wct/accept/receipt_validation.py` | N | — | `ab6cca0b…` | 88de60e | ídem (ajuste de frontera autorizado en el contrato) | CONFORME |
| `tools/wct/accept/semantic.py` | N | — | `7e324c02…` | 88de60e | ídem | CONFORME |
| `tools/wct/accept/verdict.py` | N | — | `3990babd…` | 88de60e | ídem (ruta extra autorizada, 151 sitios) | CONFORME |
| `tools/wct/accept/verdict_validation.py` | N | — | `3c131a99…` | 88de60e | ídem | CONFORME |
| `tools/wct/accept/pipeline.py` | M | `925c8919…` | `af67b206…` | 88de60e | Fachada del motor. `CONTRATO-AC1.md` (archivo explícito de la frontera). Sin cambios posteriores | CONFORME |
| `tools/wct/accept/process.py` | N | — | `1a25984b…` | 88de60e→b4403c5→aed2acf→ee53166 | Transporte. `CONTRATO-AC1.md`; descomillado de casts (`REPARACION-INTEGRACION…` §0); reparación CRAP (`REPARACION-CRAP…`, encargo de alcance nominal); retiro de guard (`CIERRE-CLEANUP…`, encargo citado literal). Evidencia por capa: focales, mutación bounded, casts ratificados sobre `1a25984b…` (`CALIFICACION-FINAL…` §2). Sin cambios tras ee53166 → vigente | CONFORME |
| `tools/wct/gate/semgrep.py` | N | — | `33ff0509…` | 88de60e→4217253 | Gate SAST. Introducción: addenda de 9 rutas + partición 3+1 — **procedencia: transcripción en `HANDOFF-BASELINE-FIX-R2-2026-09-12.md`; la addenda original es fuente local ajena no versionada**. Cambio 4217253: encargo citado literal en `REPARACION-SAST…` («reparar la omisión… targets explícitos…»). Evidencia: TDD 59/59, gate PASS 169 fuentes/0 hallazgos, mutación 69+5. Vigente. **Su disposición E9 está acoplada por el propio registro §9 a la decisión sobre los 5 IDs (§1)** | **PENDIENTE** (subordinada a D-A') |
| `tools/wct/gate/semgrep_schema.py` | N | — | `512bb31b…` | 88de60e | Partición fachada semgrep. Misma procedencia transcrita (handoff). Evidencia GS-1 sucesiva (280+2, cierre O1–O5). Sin cambios posteriores | CONFORME |
| `tools/wct/gate/semgrep_verdict.py` | N | — | `3c109780…` | 88de60e | ídem | CONFORME |
| `tools/wct/gate/semgrep_scope.py` | N | — | `a7a41d35…` | 88de60e→aed2acf | Ídem + reparación CRAP (`_python_files` 7→3, `_build_dirs` 7→2; encargo de alcance nominal en `REPARACION-CRAP…`). 87/87 killed luego recalificado honesto en `FIDELIDAD…` (85/87 transferibles). Sin cambios tras aed2acf | CONFORME |
| `tools/wct/gate/checks.py` | M | `8caef617…` | `234adc15…` | 88de60e→3cc1c5a | `_declared` del gate (88de60e, addenda transcrita) + fachada de la partición TEST-007 fase checks (encargo citado en `PARTICION-TEST007…`). Evidencia por fase; REGISTRY intacto | CONFORME |
| `tools/wct/gate/runner.py` | M | `6927c945…` | `69a56d3e…` | 88de60e→da2725d | Registro del gate + fachada partición fase runner (misma autorización). PX-REG verde; suite 689 | CONFORME |
| `tools/wct/selftest/fixtures_tools.py` | M | `247fefbf…` | `213e80ac…` | 88de60e→ff3b7c5 | `f9_a` + fachada partición fase fixtures (misma autorización). Recalificación post-partición 31/31 | CONFORME |
| `tools/wct/gate/checks_debt.py` | N | — | `09209e38…` | 3cc1c5a | Partición TEST-007. Encargo citado literalmente en `PARTICION-TEST007…` (tras PX-T007 no aprobado → decisión humana). 17 archivos ≤100 sitios; tests byte a byte | CONFORME |
| `tools/wct/gate/checks_quality.py` | N | — | `818be620…` | 3cc1c5a | ídem | CONFORME |
| `tools/wct/gate/checks_scanners.py` | N | — | `a11932a0…` | 3cc1c5a | ídem | CONFORME |
| `tools/wct/gate/registry_derived.py` | N | — | `70268758…` | da2725d | ídem (fase runner) | CONFORME |
| `tools/wct/gate/registry_process.py` | N | — | `82e70f50…` | da2725d | ídem | CONFORME |
| `tools/wct/gate/registry_static.py` | N | — | `6625e18e…` | da2725d | ídem | CONFORME |
| `tools/wct/gate/runner_audit.py` | N | — | `0d285f42…` | da2725d | ídem | CONFORME |
| `tools/wct/gate/runner_docstrings.py` | N | — | `4d1443ec…` | da2725d | ídem | CONFORME |
| `tools/wct/gate/runner_secrets.py` | N | — | `0dc1544d…` | da2725d | ídem | CONFORME |
| `tools/wct/gate/runner_support.py` | N | — | `bb868315…` | da2725d | ídem | CONFORME |
| `tools/wct/gate/tier_map.py` | N | — | `8676221c…` | da2725d | ídem | CONFORME |
| `tools/wct/selftest/fixtures_adversarial.py` | N | — | `85fe5fca…` | ff3b7c5 | ídem (fase fixtures) | CONFORME |
| `tools/wct/selftest/fixtures_git.py` | N | — | `4f6f8fe8…` | ff3b7c5 | ídem | CONFORME |
| `tools/wct/selftest/fixtures_governance.py` | N | — | `372f01ea…` | ff3b7c5 | ídem | CONFORME |
| `governance/lint/vulture_whitelist.py` | M | `33b7fb00…` | `90e52d7f…` | b4403c5 | Reparación G-DEPS/G-DEAD. `REPARACION-INTEGRACION…` §0 (transcripción resumida del encargo; 6 entradas ancladas en ADR-D-02). G-DEPS/G-DEAD exit 0; verifier APROBAR CON RESERVAS | CONFORME |
| `pyproject.toml` | M | `b10f99b8…` | `c3a1b3e7…` | b4403c5 | ídem | CONFORME |
| `uv.lock` | M | `c484f92b…` | `072b223b…` | b4403c5 | ídem (`uv lock` sin upgrades) | CONFORME |

Notas de procedencia: (1) la autorización de las 9 rutas semgrep/runner/
checks/f9_a integradas en 88de60e **solo consta transcrita** en
`HANDOFF-BASELINE-FIX-R2-2026-09-12.md` (la addenda original es fuente local
ajena no versionada); se declara y no se sustituye por este resumen.
(2) `REPARACION-CRAP…` registra el alcance nominal del encargo sin cita
literal entre comillas. (3) Ninguna fila se apoya en «ya estaba en el drift»,
«hooks verdes» ni «verifier aprobó publicación»: cada dictamen cita
autorización y evidencia con su hash. **La aprobación E9 (incorporar estas 37
rutas al manifiesto) es la decisión humana global que este expediente sirve;
los dictámenes CONFORME no la sustituyen.**

## 4. Preparación del bless — SOLO DISEÑO, NO EJECUTADO

- **Comando exacto** (tras autorización humana; canónico del runbook
  `docs/runbook.md:18`), a ejecutar **por el humano** en el worktree de
  integración con el árbol en el estado aprobado:

  ```bash
  git add .secrets.baseline governance/ && uv run wct integrity bless \
    --approved-by "<humano>" \
    --reason "aprobado en PR #53: revision E9 del drift 37=7+30 tras decidir las 5 equivalencias sucesoras (D-A'/D-B'/D-E9')"
  ```

  El `--reason` debe citar URL o `#N` (regex `engine.py:20`) — «PR #53»
  cumple; `--approved-by` ≥ 2 chars y `--reason` ≥ 12 (`engine.py:15-16`).
- **Quién puede ejecutarlo**: el guard PreToolUse (`tools/wct/hooks/guard.py:28-41`)
  **bloquea al agente** ejecutar `wct integrity lock|bless` y
  `wct mutate update-manifest --approved-by`; bendice solo un humano fuera
  del agente. Este encargo no lo ejecuta ni lo prueba.
- **Archivos que modifica** (`bless()` en `tools/wct/integrity/engine.py:134-146`):
  `governance/integrity.log` no existe — escribe append en
  `governance/integrity-log.md` (cabecera ISO-8601 UTC, `Approved by`,
  `Reason`, `Commit` = HEAD al momento de correr) y **reemplaza**
  `governance/integrity.lock` (snapshot completo: `schema_version` 1,
  `hash` `sha256:eol-normalized`, `commit`, `files` ordenado). Nada más.
- **Candidato previo**: lock actual base `4666927…`, 201 entradas.
- **Delta esperado, medido sobre 2246148** (replicación de solo lectura de
  `snapshot()`): `files` 201 → **231**; **exactamente +30 claves** (las 30
  nuevas del drift), **7 hashes cambiados** (las modificadas: `uv.lock`,
  `vulture_whitelist.py`, `pyproject.toml`, `checks.py`, `fixtures_tools.py`,
  `pipeline.py`, `runner.py`), **0 claves eliminadas** (0 huérfanas: el lock
  no contiene rutas que la política vigente haya dejado de cubrir);
  `commit` → HEAD vigente al ejecutar (patrón histórico: la entrada del
  2026-09-08 registra `4666927`, el commit previo al que contiene el lock).
  **Alarma**: cualquier otra clave nueva, cualquier hash cambiado en ruta no
  tocada, o cualquier eliminación ⇒ ampliación inesperada del manifiesto:
  detener y auditar contra esta tabla antes de commitear.
- **Controles posteriores**: `uv run wct integrity check` → exit 0;
  `uv run wct gate --tier commit` (G-META-1 verde; `checks_debt.py:35-42`);
  Stop hook re-corrige tier commit; CI `quality.yml` paso «Verify generated
  policy and control-plane integrity» (hoy rojo por este drift, run
  `35186904916`) y tiers commit/full; `full-hardarding.yml` semanal. Sin
  cambios en `tools/wct/integrity/**` no se requieren los tests del
  mecanismo (`tests/unit/test_integrity.py`,
  `tests/integration/test_integrity_cli.py`) más allá de la suite normal.
- **Identidades separadas** (no transferir evidencia entre ellas sin delta):
  candidato técnico **4217253** ≠ HEAD documental **2246148** ≠ futuro
  **commit de bless** (nuevo SHA que contendrá el lock nuevo) ≠ futuro
  **SHA de merge** a main ≠ futuro **tag** (convención E10: `1.0.0b3.dev1`,
  no autorizado). El lock bendecido snapshot-ea el árbol en el momento del
  bless: si entre la aprobación E9 y el bless toca cualquier ruta protegida,
  el delta esperado deja de valer y la aprobación debe recalificarse.
  MERGEABLE ≠ aprobado, CI verde ni listo para release; E11 (revisión del
  diff completo y salida de borrador) permanece pendiente.

## 5. Coordinación, verifier y modalidad de revisión

Frentes paralelizados en copias independientes de solo lectura: A
(equivalencias), B/C (rutas protegidas y cronología) y D (bless). El
mecanismo de bless y la cadena de autorizaciones fueron auditados por
subagentes de solo lectura; una discrepancia del subagente de bless (alegó
134 violaciones y 70 rutas protegidas por lectura truncada de
`governance/policy.yaml` — 8 de 14 patrones, omitió `tools/wct/**` y otros)
fue **refutada por ejecución directa** del mecanismo real: 37 violaciones,
231 rutas protegidas en disco, 0 huérfanas. El verifier independiente de
solo lectura (§7) re-ejecutó las comprobaciones decisivas dentro del
presupuesto.

## 6. Presupuestos y limitaciones

- **Sondas de mutación/equivalencia**: coordinador 0 s (solo derivación
  estática de diffs y lectura de evidencia existente); el verifier re-ejecutó
  las comprobaciones decisivas dentro del tope conjunto de **180 s** (ver
  §7). No se repitieron campañas, Q-ACCMUT ni full.
- **Limitaciones**: la equivalencia S1–S3 descansa en implementación del
  productor + observación (no en cláusula normativa localizada — RFC 8259 es
  apoyo parcial); una salida concreta no agota el espacio de salidas. La
  addenda de las 9 rutas de 88de60e no está versionada (procedencia
  declarada). El guard crash del decode error se mantiene por decisión D2
  del acta (no es garantía universal). Este expediente no acredita AC1 ni
  beta.3.

## 7. Dictamen del verifier independiente (solo lectura, reejecución)

Verifier con clon aislado propio (HEAD 2246148 verificado) y cero escrituras
sobre worktree, rama o expedientes. Cuatro casillas separadas:

1. **Expediente apto para decisión humana: SÍ, con reservas menores** —
   ninguna bloqueante; la única discrepancia (fila de índice de §0,
   estado pre-escritura) queda corregida arriba al publicar.
2. **Equivalencias propuestas: FIELES 5/5** — diffs re-derivados por parseo
   estático (25/30/33 `text`; 27/32 `check`), correspondencia histórica
   re-derivada también contra el árbol instrumentado antiguo
   (`gs3.PDSK9G/checkout/mutants/`, fuente `0126c4e1…`): viejo 24≡nuevo 25,
   29≡30, 33≡33, 26≡27, 31≡32; advertencia confirmada (los nuevos 26/31 son
   de `capture_output`). Bruto verificado: primera pasada 63+11 (64 líneas
   killed con canario), re-test mata exactamente 24/26/29/31/34/35 →
   69+5=74; sha256 de la fuente idéntico en worktree, blob 4217253, blob
   2246148 y camp/.
3. **Aprobación E9: CONFORME, 0 rutas divergentes** — drift recalculado
   exit 1 con 37 = 7+30 idéntico ruta a ruta; autorizaciones contrastadas
   con citas verificadas (CONTRATO-AC1 líneas 4 y 169-183;
   REPARACION-INTEGRACION §0; PARTICION-TEST007 línea 3; CIERRE-CLEANUP
   líneas 3 y 177; REPARACION-SAST líneas 3-4; HANDOFF-R2 líneas 53-56 como
   única procedencia versionada de la addenda); git log 37/37 con último
   commit tocante = el declarado; `4217253..HEAD` solo documental. Cronología
   de la desviación confirmada con mtimes.
4. **Autorización de bless: PENDIENTE** — diseño NO ejecutado: lock del
   árbol 2246148 sigue en base `4666927…` con 201 entradas; última entrada
   de `integrity-log.md` sigue siendo la del 2026-09-08; sin cambios desde
   `0228acc` (2026-09-07). El verifier no concede autoridad humana.

**Reejecución decisiva (presupuesto consumido ≈ 6,5 s de 180)**: semgrep
`1.174.0` (2,35 s); COMMAND del gate `--json` sobre sonda con credencial
ficticia y no-ASCII (3,13 s): exit 1 con 1 hallazgo esperado por `--error`,
primeros 8 bytes `7b 22 76 65 72 73 69 6f` — **sin BOM** —, UTF-8 estricto
sin error, `json.loads(str) == json.loads(bytes)` = **True**;
`subprocess._text_encoding()` → `utf-8` (0,02 s); conteo del bruto (~1 s).
Un intento instrumental (xxd ausente) resuelto sin costo y sin valor
discriminante. Evidencia en
`build/tmp/cierre-doc-equivalencias-e9-20260917/verifier/`. No verificado
por el verifier: estado PR/CI vía `gh` (declaración del coordinador: run
35186904916 FAILURE por el drift; PR OPEN, borrador, MERGEABLE).

## 8. Bloque de decisiones humanas (forma corta)

1. **D-A' — Ratificación por ID** (cada uno por separado, bajo precondiciones
   de §1 y con revisión obligatoria si cambia fuente/productor/comando/
   runtime): S1 `mutmut_25` (`text→None`) · S2 `mutmut_30` (`text` omitido) ·
   S3 `mutmut_33` (`text→False`) · S4 `mutmut_27` (`check→None`) · S5
   `mutmut_32` (`check` omitido). Ratificar NO convierte los 5 `survived` en
   `killed`; el bruto 69+5 se conserva.
2. **D-B' — Disposición de la desviación de secuencia** (§2): aceptar como
   desviación puntual documentada (conservando las mediciones por identidad)
   o rechazar (implica repetir la cadena posterior cuando cambie la premisa).
3. **D-E9' — Aprobación E9 por rutas** (§3): 36 rutas dictaminadas CONFORME
   (autorización y evidencia vigentes); `tools/wct/gate/semgrep.py`
   PENDIENTE, subordinada a D-A' por la puerta declarada en el registro de
   reparación §9.
4. **D-BLESS' — Autorización posterior de bless** (§4): sobre un SHA exacto
   que el humano fije tras 1–3, con el comando preparado, delta esperado
   +30/7/0 (201→231) y controles posteriores. Ejecutable solo por el humano.

Estado del expediente: **CON PENDIENTES** (las cuatro decisiones anteriores).
No es «listo para bless».
