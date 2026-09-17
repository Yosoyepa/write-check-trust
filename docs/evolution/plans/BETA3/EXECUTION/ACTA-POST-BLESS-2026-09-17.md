# Acta POST-BLESS — publicación de los productos del bless humano (2026-09-17)

Registro sucesor de `EQUIVALENCIAS-SUCESORAS-Y-REVISION-E9-2026-09-17.md`.
Verifica, documenta y publica los productos del **bless ejecutado
personalmente por el humano** sobre el SHA aprobado. Este acta no ejecuta
bless ni `update-manifest`, no edita a mano los productos del bless, no hace
merge, bump, lock de dependencias, tag ni release, y no declara cierre
integral de AC1 ni beta.3. La PR #53 permanece en borrador.

## 1. Identidades

| Elemento | Valor |
|---|---|
| Candidato técnico medido | `421725367e3df6fae1b20af7f7ed910b2a4d50a7` (fix sast; fuente `33ff0509…`) |
| SHA previo al bless (= expediente E9 publicado = aprobado por D-BLESS') | `903f96162ad349d8f4e9c4aacc721cd0397eadbd` (= origen = headRefOid PR #53, verificado antes y después) |
| Productos del bless | `governance/integrity.lock` (sha256 `308e5296facd0e36e3977cdaad02249727cbebc3242d0f6374b18c2ecc52b5b1`) y `governance/integrity-log.md` (sha256 `9c2a6a9dc544755acafd1c31d874b67bdbcdc033efc04ca5a92dfbde85e001b3`), publicados byte a byte sin modificación manual |
| `lock.commit` | `903f96162ad349d8f4e9c4aacc721cd0397eadbd` — **se conserva**: su semántica es referir el candidato aprobado en el momento de la ejecución, no el commit que publica el lock (patrón histórico: la entrada 2026-09-08 registra `4666927`) |
| Entrada nueva del log | `## 2026-09-17T19:34:27.726122+00:00` · Approved by: yosoyepa · Reason: «aprobado en PR #53: D-A'/D-B'/D-E9'/D-BLESS' sobre 903f961 — 5 equivalencias sucesoras ratificadas (25/30/33 text; 27/32 check), desviacion aceptada puntualmente, 37 rutas E9 aprobadas (7 modificadas + 30 nuevas)» · Commit: `903f96162ad349d8f4e9c4aacc721cd0397eadbd` |
| Commits de publicación | 1.º exclusivamente los dos productos del bless: `1fc79157be0656fa18fbe410024d37121791236b`. 2.º este acta y los hunks de la matriz (su SHA se informa en la entrega; el acta no puede contener su propio commit) |

## 2. Delta verificado del lock (201 → 231)

Contra `git show 903f961:governance/integrity.lock` (201 entradas, base
`4666927…`):

- **Exactamente 30 claves nuevas**: las 30 rutas nuevas del drift aprobado
  por D-E9' (12 módulos `accept/*`, `semgrep{,_schema,_scope,_verdict}.py`,
  14 de la partición TEST-007, `semgrep.py` re-tocado por la reparación
  SAST) — lista íntegra en el expediente E9 §3.
- **0 eliminaciones** (ninguna huérfana).
- **Exactamente 7 hashes de producto/configuración actualizados**:
  `governance/lint/vulture_whitelist.py`, `pyproject.toml`,
  `tools/wct/accept/pipeline.py`, `tools/wct/gate/checks.py`,
  `tools/wct/gate/runner.py`, `tools/wct/selftest/fixtures_tools.py`,
  `uv.lock`.
- **Un octavo hash: `governance/integrity-log.md`**. **Corrección explícita
  del expediente E9 §4**: lo esperado «7 hashes cambiados» era incompleto;
  lo correcto es «**7 hashes aprobados + el hash del log de auditoría**».
  El mecanismo escribe primero el append del log y después el lock
  (`tools/wct/integrity/engine.py:138-146`), y el walk excluye el propio
  lock pero no el log (`engine.py:38-39`): **el lock registra el hash del
  log; el lock no se incluye a sí mismo**. El delta autorizado en el
  encargo POST-BLESS acepta expresamente este octavo hash. Precedente
  medido: el bless del 2026-09-08 (`0228acc`) también actualizó el hash del
  log (entonces junto a `mutation-manifest.json`, que hoy **no cambia**).
- `governance/generated/mutation-manifest.json`: sin cambio (árbol y
  entrada del lock idénticos).

## 3. Decisiones humanas transcritas (textual, de los mensajes recibidos)

**D-A'** — «Ratifico individualmente las propuestas de equivalencia de
x_gate_sast_semgrep__mutmut_25, _30, _33, _27 y _32, exclusivamente para los
bytes, runtime, comando y precondiciones documentados. Se conservan los
contraejemplos e invalidantes. El bruto permanece 69 killed + 5 survived, no
74 killed.»

**D-B'** — «Acepto puntualmente la reutilización de las mediciones
posteriores por identidad del candidato. La desviación de secuencia
permanece registrada; esta decisión no convierte su ejecución original en
conforme ni autoriza futuras omisiones de las paradas. No solicito
repetición sin un invalidante concreto.»

**D-E9'** — «Apruebo las 37 rutas enumeradas y sus hashes exactos en el
expediente, incluida semgrep.py tras D-A'. No autorizo rutas o hashes
adicionales.»

**D-BLESS'** — «Autorizo preparar el bless sobre
903f96162ad349d8f4e9c4aacc721cd0397eadbd. Lo ejecutaré personalmente conforme
al guard humano.» Ejecutado por el humano fuera del agente el 2026-09-17
(entrada del log en §1); verificado por este incremento. El encargo
POST-BLESS añadió la precisión de delta del §2 y la corrección terminológica
del octavo hash.

Procedencia: transcripción directa de los mensajes humanos recibidos en la
conversación del incremento; ningún prompt sugerido ni handoff se trata como
autorización.

## 4. Estado que se conserva (sin agregaciones indebidas)

- **Bruto de la campaña de la reparación SAST: 74 ejecutados = 69 killed +
  5 survived.** Las cinco equivalencias sucesoras (25/30/33 `text`;
  27/32 `check`) quedan **ratificadas en alcance acotado** — bytes
  (`33ff0509…`), runtime, comando (argv con targets explícitos de E) y
  precondiciones documentadas — con sus contraejemplos (BOM UTF-8/UTF-16,
  locale no UTF-8) e invalidantes (versión/productor, wrapper en PATH,
  `PYTHONUTF8=0`, serializador con BOM, cambio de consumo de stdout).
  Ratificar no convierte los 5 `survived` en `killed`.
- **Desviación de secuencia**: permanece registrada como desviación (la
  cadena siguió tras conocer los 5 supervivientes); D-B' acepta puntualmente
  reutilizar las mediciones por identidad y **no** convierte la ejecución
  original en conforme ni autoriza futuras omisiones de las paradas.
- **Límites de la calificación**: sin PASS de G-MUT sobre la campaña AC1, sin
  acreditación AC1, sin cierre de beta.3. Los 928 IDs históricos siguen sin
  ejecutar (delimitación aprobada); Q-ACCMUT conserva su 47/47 ligado a sus
  hashes; el full pre-bless 34 = 33 PASS + G-META-1 queda hoy resuelto en su
  único rojo por el bless (ver §5).
- **Pendientes antes de merge**: E11 (revisión humana del diff completo de
  la PR y salida de borrador); CI `commit-gates` verde sobre el SHA
  publicado (observación en curso, §6); cualquier pendiente que esa revisión
  abra.
- **Pendientes antes del cierre de beta.3**: E10 (bump/lock/tag no
  autorizados; convención `1.0.0b3.dev1` elegida sin ejecutar), custodia,
  SBOM y smokes de release; sin declaración de cierre integral.

## 5. Verificación ejecutada (pre-publicación)

- `uv run wct integrity check` → **exit 0** (antes del bless: exit 1, 37
  violaciones). Un integrity check verde acredita **consistencia del
  snapshot**, no autorización (la autorización es D-E9'/D-BLESS').
- `uv run wct gate --tier commit` → **21/21 PASS**, incluido **G-META-1
  PASS** («configuración protegida coincide con integrity.lock»); primer
  tier commit totalmente verde de la rama (antes: 20 PASS + 1 FAIL).
- Preflight: HEAD = origen = headRefOid = `903f961`; únicos cambios
  protegidos sin commitear los dos productos del bless; documento ajeno
  `PREPARACION-SALIDA-INCREMENTAL-BETA3.1-2026-09-13.md` preservado sin
  seguimiento; `git diff --name-only 4217253..903f961` = solo docs.
- **Dictamen del verifier independiente**: ver §7.

## 6. Publicación y verificación post-publicación

Publicación en dos commits deliberados, con `git diff --check` limpio, fast
gate 7/7, remoto revalidado sin avance e inspección de TODO el staging antes
de cada commit (hooks activos, sin bypass, push normal):

1. `1fc79157be0656fa18fbe410024d37121791236b` — exclusivamente los dos
   productos del bless, bytes sin modificación manual.
2. Este acta y los hunks E5/E8/E9/E11 de la matriz.

Verificación post-publicación sobre el SHA final (ejecutada tras el push y
reportada en la entrega del incremento, no en este acta): igualdad
local/remoto/headRefOid; `wct integrity check` y `gate --tier commit`
re-ejecutados; observación acotada de la CI `commit-gates` del workflow real
sobre ese SHA, distinguiendo PASS/FAIL/SKIPPED/CANCELLED/NO EJECUTADO. La CI
verde del SHA publicado — no el tier local ni un run de otro SHA — es la que
cuenta. `lock.commit` no se actualiza al commit posterior: conserva su
semántica de referencia al candidato aprobado (`903f961`).

## 7. Dictamen del verifier independiente (solo lectura, previo al commit)

**FAVORABLE, con reservas menores no bloqueantes**, a publicar los productos
del bless byte a byte. Detalle de sus comprobaciones (artefactos propios en
`build/tmp/postbless-verifier/`; ~3 min de ejecuciones; cero escrituras):

1. **Recálculo del lock**: 201→231; `commit` = `903f961…` (= HEAD exacto);
   30 nuevas, 0 eliminadas, 8 hashes cambiados (los 7 aprobados +
   `governance/integrity-log.md`, `dfff5b15…` → `9c2a6a9d…`); **38/38 hashes
   recalculados en disco** (replicando `_digest_eol_normalized`,
   `engine.py:45-52`) coinciden con el lock.
2. **Contraste E9**: igualdad de conjuntos por tres vías (lock nuevo, tabla
   §3 del expediente, drift recalculado) — 0 rutas divergentes; el log **no**
   figura en la tabla aprobada (correcto: consecuencia mecánica, no ruta).
3. **Append puro del log**: un único hunk al final (6 líneas, 10095 → 10433
   bytes); `cmp` confirma que el log viejo (43 entradas) es prefijo
   byte-exacto del nuevo (44).
4. **Orden de escritura confirmado** (`engine.py`): append del log en
   138-145, lock después en 146; el walk excluye solo el lock (38-39); el
   log cae bajo `governance/**`. El lock registra el hash del log ya con la
   entrada nueva; el lock jamás se incluye a sí mismo.
5. **`mutation-manifest.json` sin cambio** (hash idéntico en ambos locks y
   árbol limpio para esa ruta).
6. **Ejecuciones**: `integrity check` exit 0 (6,3 s); `gate --tier commit`
   exit 0 (2m10s), 21/21 PASS con G-META-1 PASS.
7. **Sin cambios de producto tras la calificación** (`4217253..903f961` =
   solo docs/; `semgrep.py` = `33ff0509…`).

Reservas: (a) la razón registrada difiere del texto plantilla del expediente
§4 aunque cumple el regex del motor y cita #53 y el SHA — sin valor
discriminatorio; (b) los docs concurrentes de este incremento exigen commits
deliberados (así se hace: §6); (c) PR/CI post-bless no verificados por el
verifier (se cubren en §6.1). Salvedad central del propio dictamen: un
integrity check verde acredita consistencia del snapshot, no autorización;
la autoridad es la decisión humana E9/D-BLESS'.

## 8. Límites de este acta

No autoriza ni declara: nuevo bless, `update-manifest`, merge, bump, lock de
dependencias, tag, release, cierre integral AC1/beta.3, ni ratificaciones
por analogía. El lock publicado registra la aprobación humana del árbol
`903f961`; cualquier cambio futuro en rutas protegidas vuelve a abrir el
drift y exige revisión E9 y bless propios.
